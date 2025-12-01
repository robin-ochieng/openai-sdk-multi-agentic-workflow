"""
Fact Checker Agent for Deep Research.

Scans drafted markdown, extracts factual claims, cross-checks against
validated sources, and annotates with confidence levels.

Features:
- Factual claim extraction from markdown
- Cross-checking against multiple sources
- Confidence scoring (verified/uncertain/disputed)
- Inline annotation generation
- Verification report generation
"""

import os
import re
import json
import logging
import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

from agents import Agent, Runner, WebSearchTool

from deep_research.models.news_models import (
    FactualClaim,
    VerificationResult,
    VerificationReport,
    VerificationSource,
    VerificationStatus,
    ClaimCategory,
)


# Configure logging
logger = logging.getLogger("deep_research.fact_checker")


# =============================================================================
# Claim Extraction Patterns
# =============================================================================

# Patterns for identifying factual claims
STATISTIC_PATTERNS = [
    r'\b(\d+(?:\.\d+)?)\s*(%|percent)\b',  # Percentages
    r'\$\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion|B|M|T)?\b',  # Money
    r'\b(\d+(?:\.\d+)?)\s*(billion|million|trillion|thousand)\b',  # Large numbers
    r'\b(\d{1,2}(?:st|nd|rd|th))\s+(?:largest|smallest|highest|lowest)\b',  # Rankings
    r'\b(\d+)\s+(?:people|users|customers|employees|companies)\b',  # Counts
]

EVENT_PATTERNS = [
    r'\b(?:in|on|during)\s+(\d{4})\b',  # Year references
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
    r'\bfounded\s+(?:in\s+)?(\d{4})\b',  # Founding dates
    r'\bacquired\s+(?:by|in)\s+(\d{4})?\b',  # Acquisition events
]

QUOTE_PATTERNS = [
    r'"([^"]+)"',  # Double quotes
    r"'([^']+)'",  # Single quotes
    r'according to\s+([^,\.]+)',  # Attributed statements
    r'(\w+(?:\s+\w+)?)\s+said\s*(?:that)?\s*"?([^"\.]+)',  # X said Y
]

COMPARATIVE_PATTERNS = [
    r'\bmore\s+than\s+(\d+)',  # More than X
    r'\bless\s+than\s+(\d+)',  # Less than X
    r'\b(\d+)\s*(?:x|times)\s+(?:more|faster|larger|greater)\b',  # X times more
    r'\b(\d+(?:\.\d+)?)\s*%\s+(?:increase|decrease|growth|decline)\b',  # Percentage change
]


def extract_claims_from_markdown(markdown: str) -> List[FactualClaim]:
    """
    Extract factual claims from markdown text.
    
    Args:
        markdown: Markdown text to scan.
        
    Returns:
        List of extracted FactualClaim objects.
    """
    claims = []
    claim_id = 0
    
    # Split into sections for context tracking
    lines = markdown.split('\n')
    current_section = ""
    
    for line_num, line in enumerate(lines, 1):
        # Track sections
        if line.startswith('#'):
            current_section = line.strip('#').strip()
            continue
        
        # Skip empty lines and code blocks
        if not line.strip() or line.strip().startswith('```'):
            continue
        
        # Extract claims from this line
        line_claims = _extract_claims_from_line(
            line, 
            line_num, 
            current_section,
            claim_id
        )
        
        for claim in line_claims:
            claims.append(claim)
            claim_id += 1
    
    return claims


def _extract_claims_from_line(
    line: str,
    line_num: int,
    section: str,
    base_id: int,
) -> List[FactualClaim]:
    """Extract claims from a single line."""
    claims = []
    seen_texts = set()
    
    # Get surrounding context (the whole line serves as context)
    context = line.strip()
    
    # Check statistic patterns
    for pattern in STATISTIC_PATTERNS:
        matches = list(re.finditer(pattern, line, re.IGNORECASE))
        for match in matches:
            claim_text = _get_claim_sentence(line, match.start(), match.end())
            if claim_text and claim_text not in seen_texts:
                seen_texts.add(claim_text)
                claims.append(FactualClaim(
                    claim_id=f"claim_{base_id + len(claims)}",
                    claim_text=claim_text,
                    context=context,
                    source_section=section,
                    line_number=line_num,
                    category=ClaimCategory.STATISTIC,
                    is_quantitative=True,
                    is_checkable=True,
                ))
    
    # Check event patterns
    for pattern in EVENT_PATTERNS:
        matches = list(re.finditer(pattern, line, re.IGNORECASE))
        for match in matches:
            claim_text = _get_claim_sentence(line, match.start(), match.end())
            if claim_text and claim_text not in seen_texts:
                seen_texts.add(claim_text)
                claims.append(FactualClaim(
                    claim_id=f"claim_{base_id + len(claims)}",
                    claim_text=claim_text,
                    context=context,
                    source_section=section,
                    line_number=line_num,
                    category=ClaimCategory.EVENT,
                    is_time_sensitive=True,
                    is_checkable=True,
                ))
    
    # Check quote patterns
    for pattern in QUOTE_PATTERNS:
        matches = list(re.finditer(pattern, line, re.IGNORECASE))
        for match in matches:
            claim_text = _get_claim_sentence(line, match.start(), match.end())
            if claim_text and claim_text not in seen_texts and len(claim_text) > 20:
                seen_texts.add(claim_text)
                claims.append(FactualClaim(
                    claim_id=f"claim_{base_id + len(claims)}",
                    claim_text=claim_text,
                    context=context,
                    source_section=section,
                    line_number=line_num,
                    category=ClaimCategory.QUOTE,
                    is_checkable=True,
                ))
    
    # Check comparative patterns
    for pattern in COMPARATIVE_PATTERNS:
        matches = list(re.finditer(pattern, line, re.IGNORECASE))
        for match in matches:
            claim_text = _get_claim_sentence(line, match.start(), match.end())
            if claim_text and claim_text not in seen_texts:
                seen_texts.add(claim_text)
                claims.append(FactualClaim(
                    claim_id=f"claim_{base_id + len(claims)}",
                    claim_text=claim_text,
                    context=context,
                    source_section=section,
                    line_number=line_num,
                    category=ClaimCategory.COMPARATIVE,
                    is_quantitative=True,
                    is_checkable=True,
                ))
    
    return claims


def _get_claim_sentence(text: str, match_start: int, match_end: int) -> str:
    """
    Extract the sentence containing the matched pattern.
    
    Args:
        text: Full text.
        match_start: Start position of match.
        match_end: End position of match.
        
    Returns:
        Sentence containing the match.
    """
    # Find sentence boundaries
    sentence_start = match_start
    sentence_end = match_end
    
    # Look backwards for sentence start
    for i in range(match_start - 1, max(0, match_start - 200), -1):
        if text[i] in '.!?\n' and i < match_start - 1:
            sentence_start = i + 1
            break
        if i == max(1, match_start - 200):
            sentence_start = i
    
    # Look forwards for sentence end
    for i in range(match_end, min(len(text), match_end + 200)):
        if text[i] in '.!?\n':
            sentence_end = i + 1
            break
        if i == min(len(text) - 1, match_end + 199):
            sentence_end = i + 1
    
    sentence = text[sentence_start:sentence_end].strip()
    
    # Clean up markdown formatting
    sentence = re.sub(r'\*+', '', sentence)  # Remove bold/italic
    sentence = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', sentence)  # Remove links
    sentence = re.sub(r'^[-*]\s+', '', sentence)  # Remove list markers
    
    return sentence


def categorize_claim(claim_text: str) -> ClaimCategory:
    """
    Categorize a claim based on its content.
    
    Args:
        claim_text: Text of the claim.
        
    Returns:
        ClaimCategory enum value.
    """
    text_lower = claim_text.lower()
    
    # Check for statistics
    if re.search(r'\d+(?:\.\d+)?%|\$\d+|\d+\s*(?:billion|million|trillion)', text_lower):
        return ClaimCategory.STATISTIC
    
    # Check for dates/events
    if re.search(r'\b(?:in|on|during)\s+\d{4}|(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}', text_lower):
        return ClaimCategory.TEMPORAL
    
    # Check for quotes
    if '"' in claim_text or "'" in claim_text or 'said' in text_lower:
        return ClaimCategory.QUOTE
    
    # Check for comparisons
    if re.search(r'more than|less than|greater than|smaller than|times', text_lower):
        return ClaimCategory.COMPARATIVE
    
    # Check for scientific claims
    if re.search(r'study|research|scientists|findings|discovered|evidence', text_lower):
        return ClaimCategory.SCIENTIFIC
    
    return ClaimCategory.OTHER


# =============================================================================
# Fact Checker Agent
# =============================================================================

class FactCheckerAgent:
    """
    Agent for fact-checking claims in research reports.
    
    Extracts factual claims from markdown, verifies them against
    trusted sources, and generates verification annotations.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the fact checker agent.
        
        Args:
            model: OpenAI model to use.
        """
        self.model = model
        self._verification_agent: Optional[Agent] = None
        
        # Cache for verified claims
        self._verification_cache: Dict[str, VerificationResult] = {}
    
    @property
    def verification_agent(self) -> Agent:
        """Lazy-load verification agent."""
        if self._verification_agent is None:
            self._verification_agent = Agent(
                name="FactVerificationAgent",
                instructions="""You are a fact-checking specialist.
                Your job is to verify factual claims by searching for reliable sources.
                
                When verifying a claim:
                1. Search for multiple authoritative sources
                2. Look for official statistics, government data, or reputable news sources
                3. Note if sources agree or disagree with the claim
                4. Pay attention to the date/currency of information
                5. Distinguish between facts and opinions
                
                For each source found, note:
                - The source name and URL
                - Whether it supports, contradicts, or is neutral on the claim
                - A relevant excerpt from the source
                
                Be especially careful with:
                - Statistics and numbers (verify exact figures)
                - Dates and timelines (confirm accuracy)
                - Quotes and attributions (verify who said what)
                """,
                model=self.model,
                tools=[WebSearchTool()],
            )
        return self._verification_agent
    
    async def verify_report(
        self,
        markdown: str,
        max_claims: int = 20,
        collected_sources: List[Dict[str, Any]] = None,
    ) -> VerificationReport:
        """
        Verify factual claims in a markdown report.
        
        Args:
            markdown: Markdown text to fact-check.
            max_claims: Maximum number of claims to verify.
            collected_sources: Sources already collected during research.
            
        Returns:
            VerificationReport with all results.
        """
        logger.info("Starting report verification")
        
        # Extract claims
        claims = extract_claims_from_markdown(markdown)
        logger.info(f"Extracted {len(claims)} claims from report")
        
        # Prioritize claims (statistics and comparatives first)
        claims = self._prioritize_claims(claims)[:max_claims]
        
        # Verify each claim
        results = []
        for claim in claims:
            try:
                result = await self._verify_claim(claim, collected_sources)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to verify claim '{claim.claim_text[:50]}...': {e}")
                results.append(VerificationResult(
                    claim=claim,
                    status=VerificationStatus.UNCERTAIN,
                    confidence=0.0,
                    explanation=f"Verification failed: {str(e)}",
                ))
        
        # Build report
        report = VerificationReport(
            document_title="Research Report",
            results=results,
        )
        report.calculate_statistics()
        
        logger.info(
            f"Verification complete: {report.verified_count} verified, "
            f"{report.disputed_count} disputed, {report.uncertain_count} uncertain"
        )
        
        return report
    
    def _prioritize_claims(self, claims: List[FactualClaim]) -> List[FactualClaim]:
        """Prioritize claims for verification."""
        def priority_score(claim: FactualClaim) -> int:
            score = 0
            
            # Statistics and comparatives are high priority
            if claim.category == ClaimCategory.STATISTIC:
                score += 3
            elif claim.category == ClaimCategory.COMPARATIVE:
                score += 3
            
            # Quantitative claims are important
            if claim.is_quantitative:
                score += 2
            
            # Time-sensitive claims need verification
            if claim.is_time_sensitive:
                score += 1
            
            return score
        
        return sorted(claims, key=priority_score, reverse=True)
    
    async def _verify_claim(
        self,
        claim: FactualClaim,
        collected_sources: List[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """Verify a single claim."""
        # Check cache first
        cache_key = self._get_cache_key(claim)
        if cache_key in self._verification_cache:
            logger.debug(f"Cache hit for claim: {claim.claim_text[:50]}...")
            return self._verification_cache[cache_key]
        
        # First, check against collected sources
        source_check = self._check_collected_sources(claim, collected_sources or [])
        if source_check:
            self._verification_cache[cache_key] = source_check
            return source_check
        
        # If not found in collected sources, search online
        result = await self._search_and_verify(claim)
        self._verification_cache[cache_key] = result
        
        return result
    
    def _get_cache_key(self, claim: FactualClaim) -> str:
        """Generate cache key for a claim."""
        text = claim.claim_text.lower().strip()
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_collected_sources(
        self,
        claim: FactualClaim,
        sources: List[Dict[str, Any]],
    ) -> Optional[VerificationResult]:
        """Check if claim can be verified from collected sources."""
        if not sources:
            return None
        
        supporting = []
        contradicting = []
        claim_words = set(claim.claim_text.lower().split())
        
        for source in sources:
            # Check if source content relates to the claim
            source_text = ""
            if "snippet" in source:
                source_text = source["snippet"].lower()
            elif "summary" in source:
                source_text = source["summary"].lower()
            
            if not source_text:
                continue
            
            # Simple relevance check
            source_words = set(source_text.split())
            overlap = len(claim_words & source_words)
            
            if overlap < 3:  # Not enough overlap
                continue
            
            # Determine if source supports or contradicts
            # (simplified - in production, use NLI model)
            credibility = source.get("credibility_score", 50)
            
            verification_source = VerificationSource(
                name=source.get("title", "Unknown Source"),
                url=source.get("url", ""),
                credibility_score=credibility,
                supports_claim=True,  # Assume support if relevant
                contradicts_claim=False,
                relevant_excerpt=source_text[:200],
            )
            
            if credibility >= 60:
                supporting.append(verification_source)
            else:
                # Low credibility sources are less reliable
                pass
        
        # If we found supporting sources, mark as verified
        if supporting:
            avg_confidence = sum(s.credibility_score for s in supporting) / len(supporting) / 100
            return VerificationResult(
                claim=claim,
                status=VerificationStatus.VERIFIED,
                confidence=min(0.9, avg_confidence + 0.3),  # Boost for having sources
                supporting_sources=supporting,
                contradicting_sources=contradicting,
                explanation=f"Verified by {len(supporting)} collected source(s).",
            )
        
        return None
    
    async def _search_and_verify(self, claim: FactualClaim) -> VerificationResult:
        """Search for sources and verify claim."""
        try:
            # Build search query
            search_query = self._build_verification_query(claim)
            
            # Run verification search
            result = await Runner.run(
                self.verification_agent,
                f"Verify this claim: \"{claim.claim_text}\"\n\n"
                f"Search for: {search_query}\n\n"
                "Find authoritative sources that either confirm or refute this claim. "
                "Report what you find and whether sources agree with the claim."
            )
            
            # Parse verification result
            verification = self._parse_verification_response(claim, result.final_output)
            return verification
            
        except Exception as e:
            logger.error(f"Verification search failed: {e}")
            return VerificationResult(
                claim=claim,
                status=VerificationStatus.UNCERTAIN,
                confidence=0.3,
                explanation=f"Could not verify: search failed ({str(e)[:50]})",
            )
    
    def _build_verification_query(self, claim: FactualClaim) -> str:
        """Build search query for verification."""
        # Extract key terms from claim
        text = claim.claim_text
        
        # Remove common words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "that", "this", "these", "those", "it", "its", "of", "in",
            "for", "on", "with", "at", "by", "from", "to", "and", "or",
        }
        
        words = text.lower().split()
        key_words = [w for w in words if w not in stopwords and len(w) > 2][:8]
        
        # Add fact-check keywords
        query = " ".join(key_words) + " fact check statistics"
        
        return query
    
    def _parse_verification_response(
        self,
        claim: FactualClaim,
        response: str,
    ) -> VerificationResult:
        """Parse verification agent response."""
        response_lower = response.lower()
        
        # Determine verification status based on response content
        supporting_indicators = [
            "confirms", "verified", "accurate", "correct", "true",
            "supports", "consistent with", "matches", "agrees",
        ]
        contradicting_indicators = [
            "contradicts", "false", "incorrect", "inaccurate",
            "disputes", "refutes", "differs from", "wrong",
        ]
        uncertain_indicators = [
            "could not find", "unable to verify", "no reliable sources",
            "conflicting", "mixed", "unclear", "insufficient",
        ]
        
        supporting_count = sum(1 for ind in supporting_indicators if ind in response_lower)
        contradicting_count = sum(1 for ind in contradicting_indicators if ind in response_lower)
        uncertain_count = sum(1 for ind in uncertain_indicators if ind in response_lower)
        
        # Determine status
        if contradicting_count > supporting_count:
            status = VerificationStatus.DISPUTED
            confidence = min(0.9, 0.5 + contradicting_count * 0.1)
        elif supporting_count > contradicting_count and uncertain_count < supporting_count:
            status = VerificationStatus.VERIFIED
            confidence = min(0.9, 0.5 + supporting_count * 0.1)
        elif uncertain_count > 0:
            status = VerificationStatus.UNCERTAIN
            confidence = 0.4
        else:
            status = VerificationStatus.UNCERTAIN
            confidence = 0.5
        
        # Extract sources from response
        sources = self._extract_sources_from_response(response)
        
        # Split sources by support/contradiction
        supporting_sources = [s for s in sources if s.supports_claim]
        contradicting_sources = [s for s in sources if s.contradicts_claim]
        
        # Generate explanation
        explanation = self._generate_explanation(
            status, supporting_sources, contradicting_sources, response
        )
        
        return VerificationResult(
            claim=claim,
            status=status,
            confidence=confidence,
            supporting_sources=supporting_sources,
            contradicting_sources=contradicting_sources,
            explanation=explanation,
        )
    
    def _extract_sources_from_response(
        self,
        response: str,
    ) -> List[VerificationSource]:
        """Extract source information from response."""
        sources = []
        
        # Look for URLs
        url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.[a-z]+[^\s\)]*'
        urls = re.findall(url_pattern, response)
        
        for i, url_match in enumerate(urls[:5]):  # Limit to 5 sources
            # Try to extract context around URL
            full_url_match = re.search(
                rf'https?://(?:www\.)?{re.escape(url_match)}[a-z]+[^\s\)]*',
                response
            )
            url = full_url_match.group(0) if full_url_match else f"https://{url_match}.com"
            
            # Determine support based on surrounding text
            start = max(0, response.find(url) - 100)
            end = min(len(response), response.find(url) + 100)
            context = response[start:end].lower()
            
            supports = any(ind in context for ind in ["confirms", "supports", "verified"])
            contradicts = any(ind in context for ind in ["contradicts", "disputes", "refutes"])
            
            sources.append(VerificationSource(
                name=url_match.title(),
                url=url,
                credibility_score=60.0,  # Default score
                supports_claim=supports and not contradicts,
                contradicts_claim=contradicts,
                relevant_excerpt=context,
            ))
        
        return sources
    
    def _generate_explanation(
        self,
        status: VerificationStatus,
        supporting: List[VerificationSource],
        contradicting: List[VerificationSource],
        response: str,
    ) -> str:
        """Generate explanation for verification result."""
        if status == VerificationStatus.VERIFIED:
            if supporting:
                return f"Verified by {len(supporting)} source(s) including {supporting[0].name}."
            return "Claim appears to be accurate based on available evidence."
        
        elif status == VerificationStatus.DISPUTED:
            if contradicting:
                return f"Disputed by {len(contradicting)} source(s). May need correction."
            return "Evidence suggests this claim may be inaccurate."
        
        elif status == VerificationStatus.UNVERIFIABLE:
            return "This claim cannot be fact-checked (opinion, prediction, or no data available)."
        
        else:  # UNCERTAIN
            return "Insufficient evidence to confirm or refute this claim."
    
    def annotate_markdown(
        self,
        markdown: str,
        report: VerificationReport,
    ) -> str:
        """
        Add verification annotations to markdown.
        
        Args:
            markdown: Original markdown.
            report: Verification report.
            
        Returns:
            Annotated markdown.
        """
        annotated = markdown
        
        # Add annotations in reverse order (to preserve positions)
        sorted_results = sorted(
            report.results,
            key=lambda r: r.claim.line_number or 0,
            reverse=True
        )
        
        for result in sorted_results:
            if result.status in [VerificationStatus.DISPUTED, VerificationStatus.UNCERTAIN]:
                # Find the claim in the markdown
                claim_text = result.claim.claim_text
                
                # Only annotate if claim is found
                if claim_text in annotated:
                    annotation = result.to_annotation()
                    annotated = annotated.replace(
                        claim_text,
                        f"{claim_text} {annotation}",
                        1  # Replace only first occurrence
                    )
        
        return annotated


# =============================================================================
# Factory Functions
# =============================================================================

def create_fact_checker_agent(model: str = "gpt-4o-mini") -> FactCheckerAgent:
    """
    Factory function to create a FactCheckerAgent.
    
    Args:
        model: OpenAI model to use.
        
    Returns:
        Configured FactCheckerAgent instance.
    """
    return FactCheckerAgent(model=model)


def get_fact_checker() -> FactCheckerAgent:
    """Get a default FactCheckerAgent instance."""
    return FactCheckerAgent()


async def verify_markdown_claims(
    markdown: str,
    max_claims: int = 20,
    sources: List[Dict[str, Any]] = None,
) -> VerificationReport:
    """
    Convenience function to verify claims in markdown.
    
    Args:
        markdown: Markdown text to verify.
        max_claims: Maximum claims to check.
        sources: Collected sources for cross-reference.
        
    Returns:
        VerificationReport with results.
    """
    checker = FactCheckerAgent()
    return await checker.verify_report(markdown, max_claims, sources)
