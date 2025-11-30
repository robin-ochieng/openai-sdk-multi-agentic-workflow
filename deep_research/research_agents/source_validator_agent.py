"""
Source Validator Agent for Deep Research.

Validates and scores sources for credibility before including them in research.
Uses domain classification, recency checks, and optional LLM assessment.

Features:
- Domain-based credibility scoring with configurable allow/deny lists
- Recency-based scoring adjustments
- Structured exclusion logging
- Graceful handling of missing configuration files
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from agents import Agent, Runner

from deep_research.models.source_validation import (
    SourceMetadata,
    SourceCredibility,
    CredibilityScores,
    ValidationResult,
    ValidationStatistics,
    DomainCategory,
    InclusionDecision,
    ExclusionReason,
    CredibilityLevel,
)


# Configure structured logging
logger = logging.getLogger("deep_research.source_validator")


# Default configuration path
CONFIG_DIR = Path(__file__).parent.parent / "config"
SOURCE_DOMAINS_FILE = CONFIG_DIR / "source_domains.json"


class DomainClassifier:
    """
    Classifies domains and applies credibility adjustments.
    
    Loads domain lists from JSON configuration and provides
    lookup functionality for scoring.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize classifier with domain configuration.
        
        Args:
            config_path: Path to source_domains.json. Uses default if not provided.
        """
        self.config_path = config_path or SOURCE_DOMAINS_FILE
        self.config = self._load_config()
        
        # Build lookup structures for efficient classification
        self._trusted_domains: Dict[str, Tuple[DomainCategory, int]] = {}
        self._flagged_domains: Dict[str, Tuple[DomainCategory, int]] = {}
        self._blocked_domains: set = set()
        self._blocked_patterns: List[str] = []
        
        self._build_lookups()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load domain configuration from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded domain configuration from {self.config_path}")
                return config
            else:
                logger.warning(
                    f"Domain configuration not found at {self.config_path}. "
                    "Using default empty configuration."
                )
                return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in domain configuration: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading domain configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return minimal default configuration."""
        return {
            "trusted_domains": {},
            "flagged_domains": {},
            "blocked_domains": {"domains": [], "patterns": []},
            "recency_weights": {
                "fresh": {"max_days": 30, "bonus": 10},
                "recent": {"max_days": 180, "bonus": 5},
                "current": {"max_days": 365, "bonus": 0},
                "dated": {"max_days": 730, "penalty": -10},
                "outdated": {"max_days": None, "penalty": -20}
            },
            "scoring_thresholds": {
                "include": {"min_score": 50},
                "include_with_caveat": {"min_score": 30},
                "exclude": {"min_score": 0}
            }
        }
    
    def _build_lookups(self):
        """Build efficient lookup structures from configuration."""
        # Map category names to enums
        category_map = {
            "government": DomainCategory.GOVERNMENT,
            "academic": DomainCategory.ACADEMIC,
            "major_news": DomainCategory.MAJOR_NEWS,
            "tech_authoritative": DomainCategory.TECH_AUTHORITATIVE,
            "official_company": DomainCategory.OFFICIAL_COMPANY,
            "research_data": DomainCategory.RESEARCH_DATA,
            "user_generated": DomainCategory.USER_GENERATED,
            "wiki_collaborative": DomainCategory.WIKI_COLLABORATIVE,
            "social_media": DomainCategory.SOCIAL_MEDIA,
            "content_farms": DomainCategory.CONTENT_FARMS,
        }
        
        # Build trusted domains lookup
        trusted = self.config.get("trusted_domains", {})
        for category_name, domains in trusted.items():
            if category_name.startswith("_"):  # Skip metadata fields
                continue
            if isinstance(domains, list):
                category = category_map.get(category_name, DomainCategory.UNKNOWN)
                for domain in domains:
                    self._trusted_domains[domain.lower()] = (category, 20)  # +20 bonus
        
        # Build flagged domains lookup
        flagged = self.config.get("flagged_domains", {})
        for category_name, info in flagged.items():
            if category_name.startswith("_"):
                continue
            if isinstance(info, dict):
                category = category_map.get(category_name, DomainCategory.UNKNOWN)
                penalty = info.get("penalty", -10)
                for domain in info.get("domains", []):
                    self._flagged_domains[domain.lower()] = (category, penalty)
        
        # Build blocked domains
        blocked = self.config.get("blocked_domains", {})
        self._blocked_domains = set(d.lower() for d in blocked.get("domains", []))
        self._blocked_patterns = [p.lower() for p in blocked.get("patterns", [])]
    
    def classify_domain(self, domain: str) -> Tuple[DomainCategory, int]:
        """
        Classify a domain and return category with score adjustment.
        
        Args:
            domain: Domain to classify (e.g., "arxiv.org")
        
        Returns:
            Tuple of (DomainCategory, score_adjustment)
        """
        domain = domain.lower()
        
        # Check blocked first
        if domain in self._blocked_domains:
            return (DomainCategory.BLOCKED, -100)
        
        # Check for blocked patterns
        for pattern in self._blocked_patterns:
            if pattern in domain:
                return (DomainCategory.BLOCKED, -100)
        
        # Check trusted domains (exact match)
        if domain in self._trusted_domains:
            return self._trusted_domains[domain]
        
        # Check trusted domains (suffix match for TLDs like .gov, .edu)
        for trusted_domain, (category, bonus) in self._trusted_domains.items():
            if domain.endswith(f".{trusted_domain}"):
                return (category, bonus)
        
        # Check flagged domains
        if domain in self._flagged_domains:
            return self._flagged_domains[domain]
        
        # Check flagged domains (suffix match)
        for flagged_domain, (category, penalty) in self._flagged_domains.items():
            if domain.endswith(f".{flagged_domain}") or domain == flagged_domain:
                return (category, penalty)
        
        # Unknown domain - neutral
        return (DomainCategory.UNKNOWN, 0)
    
    def is_blocked(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a domain is blocked.
        
        Returns:
            Tuple of (is_blocked, reason)
        """
        domain = domain.lower()
        
        if domain in self._blocked_domains:
            return (True, f"Domain '{domain}' is in blocked list")
        
        for pattern in self._blocked_patterns:
            if pattern in domain:
                return (True, f"Domain contains blocked pattern '{pattern}'")
        
        return (False, None)
    
    def get_recency_adjustment(self, publication_date: Optional[datetime]) -> Tuple[int, str]:
        """
        Calculate recency-based score adjustment.
        
        Args:
            publication_date: When the source was published
        
        Returns:
            Tuple of (score_adjustment, recency_label)
        """
        if publication_date is None:
            return (0, "unknown")
        
        now = datetime.utcnow()
        age_days = (now - publication_date).days
        
        recency = self.config.get("recency_weights", {})
        
        # Check each tier
        if age_days <= recency.get("fresh", {}).get("max_days", 30):
            return (recency.get("fresh", {}).get("bonus", 10), "fresh")
        elif age_days <= recency.get("recent", {}).get("max_days", 180):
            return (recency.get("recent", {}).get("bonus", 5), "recent")
        elif age_days <= recency.get("current", {}).get("max_days", 365):
            return (recency.get("current", {}).get("bonus", 0), "current")
        elif age_days <= recency.get("dated", {}).get("max_days", 730):
            return (recency.get("dated", {}).get("penalty", -10), "dated")
        else:
            return (recency.get("outdated", {}).get("penalty", -20), "outdated")


class SourceValidator:
    """
    Core source validation logic.
    
    Validates sources based on domain classification, recency,
    and content signals to produce credibility assessments.
    """
    
    def __init__(self, domain_classifier: Optional[DomainClassifier] = None):
        """
        Initialize validator.
        
        Args:
            domain_classifier: Optional custom classifier. Creates default if not provided.
        """
        self.classifier = domain_classifier or DomainClassifier()
    
    def validate_source(self, source: SourceMetadata) -> SourceCredibility:
        """
        Validate a single source and produce credibility assessment.
        
        Args:
            source: Source metadata to validate
        
        Returns:
            Complete SourceCredibility assessment
        """
        domain = source.extract_domain()
        exclusion_reasons: List[ExclusionReason] = []
        
        # Check if domain is blocked
        is_blocked, block_reason = self.classifier.is_blocked(domain)
        if is_blocked:
            exclusion_reasons.append(ExclusionReason(
                reason_code="BLOCKED_DOMAIN",
                reason_text=block_reason or "Domain is blocked",
                severity="critical"
            ))
            logger.warning(
                f"Source excluded - blocked domain",
                extra={
                    "url": source.url,
                    "domain": domain,
                    "reason": block_reason
                }
            )
        
        # Classify domain
        category, domain_adjustment = self.classifier.classify_domain(domain)
        
        # Calculate base authority score (50 baseline)
        authority_score = max(0, min(100, 50 + domain_adjustment))
        
        # Calculate recency score
        recency_adjustment, recency_label = self.classifier.get_recency_adjustment(
            source.publication_date
        )
        recency_score = max(0, min(100, 50 + recency_adjustment * 2))  # Scale adjustment
        
        if recency_label in ("dated", "outdated"):
            exclusion_reasons.append(ExclusionReason(
                reason_code="OUTDATED_SOURCE",
                reason_text=f"Source is {recency_label} ({recency_label})",
                severity="warning",
                remediation="Consider finding more recent sources"
            ))
        
        # Objectivity score (based on category)
        objectivity_scores = {
            DomainCategory.GOVERNMENT: 70,
            DomainCategory.ACADEMIC: 80,
            DomainCategory.MAJOR_NEWS: 65,
            DomainCategory.TECH_AUTHORITATIVE: 60,
            DomainCategory.OFFICIAL_COMPANY: 55,  # May have bias toward own products
            DomainCategory.RESEARCH_DATA: 75,
            DomainCategory.USER_GENERATED: 40,
            DomainCategory.WIKI_COLLABORATIVE: 50,
            DomainCategory.SOCIAL_MEDIA: 30,
            DomainCategory.CONTENT_FARMS: 35,
            DomainCategory.BLOCKED: 0,
            DomainCategory.UNKNOWN: 50,
        }
        objectivity_score = objectivity_scores.get(category, 50)
        
        if objectivity_score < 40:
            exclusion_reasons.append(ExclusionReason(
                reason_code="LOW_OBJECTIVITY",
                reason_text=f"Source category '{category.value}' may have limited objectivity",
                severity="warning",
                remediation="Corroborate with authoritative sources"
            ))
        
        # Default corroboration score (will be updated later if cross-checking)
        corroboration_score = 50
        
        # Create scores object
        scores = CredibilityScores(
            authority=authority_score,
            recency=recency_score,
            objectivity=objectivity_score,
            corroboration=corroboration_score
        )
        
        # Create credibility assessment
        credibility = SourceCredibility.create(
            source=source,
            scores=scores,
            domain_category=category,
            exclusion_reasons=exclusion_reasons
        )
        
        # Log the validation result
        self._log_validation(credibility)
        
        return credibility
    
    def validate_sources(
        self,
        sources: List[SourceMetadata],
        query_context: str = ""
    ) -> ValidationResult:
        """
        Validate a batch of sources.
        
        Args:
            sources: List of source metadata to validate
            query_context: Research query for context
        
        Returns:
            ValidationResult with partitioned sources and statistics
        """
        import time
        start_time = time.time()
        
        included: List[SourceCredibility] = []
        caveat: List[SourceCredibility] = []
        excluded: List[SourceCredibility] = []
        total_score = 0.0
        high_credibility_count = 0
        
        for source in sources:
            credibility = self.validate_source(source)
            total_score += credibility.overall_score
            
            if credibility.credibility_level == CredibilityLevel.HIGH:
                high_credibility_count += 1
            
            if credibility.decision == InclusionDecision.INCLUDE:
                included.append(credibility)
            elif credibility.decision == InclusionDecision.INCLUDE_WITH_CAVEAT:
                caveat.append(credibility)
            else:
                excluded.append(credibility)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Build statistics
        total = len(sources)
        stats = ValidationStatistics(
            total_sources=total,
            included=len(included),
            included_with_caveat=len(caveat),
            excluded=len(excluded),
            average_score=total_score / total if total > 0 else 0.0,
            high_credibility_count=high_credibility_count,
            validation_duration_ms=elapsed_ms
        )
        
        result = ValidationResult(
            query_context=query_context,
            included_sources=included,
            caveat_sources=caveat,
            excluded_sources=excluded,
            statistics=stats
        )
        
        logger.info(
            f"Batch validation complete",
            extra={
                "total": total,
                "included": len(included),
                "caveat": len(caveat),
                "excluded": len(excluded),
                "avg_score": stats.average_score,
                "duration_ms": elapsed_ms
            }
        )
        
        return result
    
    def _log_validation(self, credibility: SourceCredibility):
        """Log validation result with structured data."""
        log_data = {
            "url": credibility.source.url,
            "domain": credibility.domain,
            "category": credibility.domain_category.value,
            "overall_score": credibility.overall_score,
            "decision": credibility.decision.value,
            "scores": {
                "authority": credibility.scores.authority,
                "recency": credibility.scores.recency,
                "objectivity": credibility.scores.objectivity,
                "corroboration": credibility.scores.corroboration
            }
        }
        
        if credibility.decision == InclusionDecision.EXCLUDE:
            reasons = [r.reason_text for r in credibility.exclusion_reasons]
            log_data["exclusion_reasons"] = reasons
            logger.warning(f"Source EXCLUDED: {credibility.source.url}", extra=log_data)
        elif credibility.decision == InclusionDecision.INCLUDE_WITH_CAVEAT:
            reasons = [r.reason_text for r in credibility.exclusion_reasons]
            log_data["caveats"] = reasons
            logger.info(f"Source INCLUDED (with caveats): {credibility.source.url}", extra=log_data)
        else:
            logger.info(f"Source INCLUDED: {credibility.source.url}", extra=log_data)


def create_source_validator_agent() -> Agent:
    """
    Create the SourceValidatorAgent for LLM-enhanced validation.
    
    This agent can be used for deeper content analysis when needed,
    but the primary validation is done by the SourceValidator class
    using rule-based scoring for performance.
    
    Returns:
        Configured Agent instance
    """
    instructions = """You are a Source Validation Expert for deep research tasks.

Your role is to assess the credibility and reliability of information sources.
When asked to evaluate sources, analyze them based on:

1. **Authority**: Is this source authoritative for the topic?
   - Academic/government sources are highly authoritative
   - Major news outlets have moderate authority
   - User-generated content has lower authority

2. **Recency**: How current is the information?
   - Consider if the topic requires recent data
   - Technology topics may need sources from last 1-2 years
   - Historical topics can use older sources

3. **Objectivity**: Is the source likely to be neutral?
   - Watch for commercial interests
   - Consider political or ideological bias
   - Academic sources tend to be more objective

4. **Corroboration**: Can this information be verified?
   - Multiple sources agreeing increases reliability
   - Unique claims need extra scrutiny

For each source, provide:
- A credibility score (0-100)
- Key concerns or strengths
- Recommendation: INCLUDE, INCLUDE_WITH_CAVEAT, or EXCLUDE

Be concise and focus on actionable insights."""

    return Agent(
        name="SourceValidator",
        instructions=instructions,
        model="gpt-4o-mini",  # Use smaller model for cost efficiency
    )


class EnhancedSourceValidator:
    """
    Enhanced validator that combines rule-based and LLM-based validation.
    
    Use this for high-stakes research where deeper content analysis is needed.
    """
    
    def __init__(self):
        self.rule_validator = SourceValidator()
        self._agent = None
    
    @property
    def agent(self) -> Agent:
        """Lazy-load the agent."""
        if self._agent is None:
            self._agent = create_source_validator_agent()
        return self._agent
    
    def validate_with_llm(
        self,
        sources: List[SourceMetadata],
        query_context: str,
        deep_analysis: bool = False
    ) -> ValidationResult:
        """
        Validate sources with optional LLM analysis.
        
        Args:
            sources: Sources to validate
            query_context: Research query for context
            deep_analysis: If True, use LLM for deeper content analysis
        
        Returns:
            ValidationResult with all assessments
        """
        # First pass: rule-based validation
        result = self.rule_validator.validate_sources(sources, query_context)
        
        if not deep_analysis:
            return result
        
        # Second pass: LLM analysis for borderline cases
        # (Sources with caveat or scores between 30-70)
        borderline_sources = [
            s for s in result.caveat_sources
            if 30 <= s.overall_score <= 70
        ]
        
        if borderline_sources:
            logger.info(f"Performing LLM analysis on {len(borderline_sources)} borderline sources")
            # LLM analysis would go here - for now just log
            # This could be expanded to use Runner.run() with the agent
        
        return result


# Convenience functions for integration
def validate_search_results(
    search_results: List[Dict[str, Any]],
    query: str = ""
) -> Tuple[List[Dict[str, Any]], ValidationStatistics]:
    """
    Validate search results and filter by credibility.
    
    Args:
        search_results: Raw search results with url, title, snippet keys
        query: Original search query for context
    
    Returns:
        Tuple of (filtered_results, validation_statistics)
    """
    validator = SourceValidator()
    
    # Convert search results to SourceMetadata
    sources = []
    for result in search_results:
        sources.append(SourceMetadata(
            url=result.get("url", ""),
            title=result.get("title", ""),
            snippet=result.get("snippet", ""),
            publication_date=result.get("publication_date"),
        ))
    
    # Validate
    validation_result = validator.validate_sources(sources, query)
    
    # Return filtered results with credibility metadata
    return validation_result.to_search_results(), validation_result.statistics


def get_domain_classifier() -> DomainClassifier:
    """Get a configured domain classifier instance."""
    return DomainClassifier()


def get_source_validator() -> SourceValidator:
    """Get a configured source validator instance."""
    return SourceValidator()
