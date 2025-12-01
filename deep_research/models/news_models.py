"""
News Intelligence Models for Deep Research Agent.

Provides Pydantic schemas for news aggregation and fact-checking including:
- NewsEvent: Individual news event with sentiment and source scoring
- NewsTimeline: Chronological collection of news events
- FactualClaim: Extracted claim from text with context
- VerificationResult: Fact-check result with confidence level
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Sentiment Enums
# =============================================================================

class Sentiment(str, Enum):
    """Sentiment classification for news content."""
    
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class SentimentIntensity(str, Enum):
    """Intensity level of sentiment."""
    
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


# =============================================================================
# Verification Enums
# =============================================================================

class VerificationStatus(str, Enum):
    """Verification status for factual claims."""
    
    VERIFIED = "verified"         # Claim confirmed by multiple reliable sources
    UNCERTAIN = "uncertain"       # Insufficient evidence or conflicting sources
    DISPUTED = "disputed"         # Contradicted by reliable sources
    UNVERIFIABLE = "unverifiable" # Cannot be fact-checked (opinion, prediction, etc.)


class ClaimCategory(str, Enum):
    """Categories of factual claims."""
    
    STATISTIC = "statistic"       # Numbers, percentages, measurements
    EVENT = "event"               # Historical or current events
    QUOTE = "quote"               # Attributed statements
    SCIENTIFIC = "scientific"     # Scientific facts or findings
    LEGAL = "legal"               # Laws, regulations, court decisions
    BIOGRAPHICAL = "biographical" # Facts about people
    GEOGRAPHIC = "geographic"     # Location-based facts
    TEMPORAL = "temporal"         # Dates, timelines, durations
    COMPARATIVE = "comparative"   # Comparisons between entities
    CAUSAL = "causal"             # Cause-and-effect claims
    OTHER = "other"


class NewsCategory(str, Enum):
    """Categories for news content."""
    
    BREAKING = "breaking"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    POLITICS = "politics"
    HEALTH = "health"
    FINANCE = "finance"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    WORLD = "world"
    ENVIRONMENT = "environment"
    OPINION = "opinion"
    OTHER = "other"


# =============================================================================
# News Models
# =============================================================================

class NewsSource(BaseModel):
    """Source information for a news article."""
    
    name: str = Field(
        ...,
        description="Name of the news source/publication"
    )
    url: str = Field(
        default="",
        description="URL of the source article"
    )
    credibility_score: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Credibility score from 0-100"
    )
    bias_label: Optional[str] = Field(
        default=None,
        description="Known bias label if any (e.g., left-leaning, right-leaning)"
    )
    is_primary_source: bool = Field(
        default=False,
        description="Whether this is a primary source for the news"
    )
    
    @property
    def credibility_level(self) -> str:
        """Get credibility level label."""
        if self.credibility_score >= 80:
            return "high"
        elif self.credibility_score >= 60:
            return "medium"
        elif self.credibility_score >= 40:
            return "low"
        else:
            return "very_low"


class SentimentAnalysis(BaseModel):
    """Sentiment analysis for news content."""
    
    sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL,
        description="Overall sentiment classification"
    )
    intensity: SentimentIntensity = Field(
        default=SentimentIntensity.MODERATE,
        description="Intensity of the sentiment"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in sentiment classification"
    )
    key_phrases: List[str] = Field(
        default_factory=list,
        description="Key phrases indicating sentiment"
    )
    
    @property
    def sentiment_label(self) -> str:
        """Get human-readable sentiment label."""
        intensity_prefix = "" if self.intensity == SentimentIntensity.MODERATE else f"{self.intensity.value} "
        return f"{intensity_prefix}{self.sentiment.value}"


class NewsEvent(BaseModel):
    """
    Represents a single news event with timeline context.
    
    Captures the event details, timing, sentiment, and source credibility
    for chronological ordering and analysis.
    """
    
    # Core event information
    headline: str = Field(
        ...,
        description="Headline or title of the news event"
    )
    summary: str = Field(
        default="",
        description="Brief summary of the event"
    )
    event_date: Optional[datetime] = Field(
        default=None,
        description="Date/time when the event occurred"
    )
    published_date: Optional[datetime] = Field(
        default=None,
        description="Date/time when the news was published"
    )
    
    # Classification
    category: NewsCategory = Field(
        default=NewsCategory.OTHER,
        description="Category of the news event"
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Key entities mentioned (people, orgs, places)"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords/tags for the event"
    )
    
    # Source information
    sources: List[NewsSource] = Field(
        default_factory=list,
        description="Sources reporting this event"
    )
    
    # Sentiment analysis
    sentiment: SentimentAnalysis = Field(
        default_factory=SentimentAnalysis,
        description="Sentiment analysis of the news"
    )
    
    # Reliability metrics
    source_count: int = Field(
        default=1,
        ge=1,
        description="Number of sources reporting this event"
    )
    average_source_score: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Average credibility score of sources"
    )
    
    # Verification status
    is_breaking: bool = Field(
        default=False,
        description="Whether this is breaking/developing news"
    )
    is_verified: bool = Field(
        default=False,
        description="Whether event has been verified by multiple sources"
    )
    
    def __lt__(self, other: "NewsEvent") -> bool:
        """Enable sorting by event date (most recent first)."""
        if self.event_date and other.event_date:
            return self.event_date > other.event_date
        if self.published_date and other.published_date:
            return self.published_date > other.published_date
        return False
    
    @property
    def reliability_tier(self) -> str:
        """Get reliability tier based on sources."""
        if self.source_count >= 3 and self.average_source_score >= 70:
            return "high"
        elif self.source_count >= 2 and self.average_source_score >= 50:
            return "medium"
        else:
            return "low"
    
    def to_timeline_entry(self) -> str:
        """Format as timeline entry for reports."""
        date_str = ""
        if self.event_date:
            date_str = self.event_date.strftime("%Y-%m-%d")
        elif self.published_date:
            date_str = self.published_date.strftime("%Y-%m-%d")
        else:
            date_str = "Unknown date"
        
        sentiment_emoji = {
            Sentiment.POSITIVE: "🟢",
            Sentiment.NEGATIVE: "🔴",
            Sentiment.NEUTRAL: "⚪",
            Sentiment.MIXED: "🟡",
        }.get(self.sentiment.sentiment, "⚪")
        
        reliability_emoji = {
            "high": "✅",
            "medium": "⚠️",
            "low": "❓",
        }.get(self.reliability_tier, "❓")
        
        return f"**{date_str}** {sentiment_emoji}{reliability_emoji} {self.headline}"


class NewsTimeline(BaseModel):
    """
    Chronological collection of news events.
    
    Aggregates events with timeline analysis and trend detection.
    """
    
    topic: str = Field(
        ...,
        description="Main topic or query for the timeline"
    )
    events: List[NewsEvent] = Field(
        default_factory=list,
        description="List of news events in chronological order"
    )
    
    # Timeline metadata
    date_range_start: Optional[datetime] = Field(
        default=None,
        description="Start of the timeline date range"
    )
    date_range_end: Optional[datetime] = Field(
        default=None,
        description="End of the timeline date range"
    )
    
    # Aggregate analysis
    overall_sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL,
        description="Overall sentiment trend across events"
    )
    sentiment_trend: str = Field(
        default="stable",
        description="Trend direction: improving, declining, stable, volatile"
    )
    
    # Statistics
    total_sources: int = Field(
        default=0,
        ge=0,
        description="Total unique sources across all events"
    )
    average_credibility: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Average credibility across all sources"
    )
    
    # Key insights
    key_developments: List[str] = Field(
        default_factory=list,
        description="Key developments or turning points"
    )
    
    def sort_chronologically(self) -> None:
        """Sort events by date (most recent first)."""
        self.events.sort()
    
    def get_events_by_sentiment(self, sentiment: Sentiment) -> List[NewsEvent]:
        """Filter events by sentiment."""
        return [e for e in self.events if e.sentiment.sentiment == sentiment]
    
    def get_high_reliability_events(self) -> List[NewsEvent]:
        """Get only high-reliability events."""
        return [e for e in self.events if e.reliability_tier == "high"]
    
    def to_markdown_timeline(self) -> str:
        """Generate markdown-formatted timeline."""
        lines = [
            f"## News Timeline: {self.topic}",
            "",
            f"*{len(self.events)} events from {len(set(s.name for e in self.events for s in e.sources))} sources*",
            f"*Overall sentiment: {self.overall_sentiment.value} ({self.sentiment_trend})*",
            "",
            "### Timeline",
            "",
        ]
        
        for event in self.events:
            lines.append(f"- {event.to_timeline_entry()}")
            if event.summary:
                lines.append(f"  - {event.summary[:200]}...")
        
        if self.key_developments:
            lines.extend([
                "",
                "### Key Developments",
                "",
            ])
            for dev in self.key_developments:
                lines.append(f"- {dev}")
        
        return "\n".join(lines)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary."""
        return {
            "topic": self.topic,
            "event_count": len(self.events),
            "date_range": {
                "start": self.date_range_start.isoformat() if self.date_range_start else None,
                "end": self.date_range_end.isoformat() if self.date_range_end else None,
            },
            "overall_sentiment": self.overall_sentiment.value,
            "sentiment_trend": self.sentiment_trend,
            "total_sources": self.total_sources,
            "average_credibility": self.average_credibility,
            "key_developments": self.key_developments,
            "sentiment_breakdown": {
                "positive": len(self.get_events_by_sentiment(Sentiment.POSITIVE)),
                "negative": len(self.get_events_by_sentiment(Sentiment.NEGATIVE)),
                "neutral": len(self.get_events_by_sentiment(Sentiment.NEUTRAL)),
                "mixed": len(self.get_events_by_sentiment(Sentiment.MIXED)),
            },
        }


# =============================================================================
# Fact-Checking Models
# =============================================================================

class FactualClaim(BaseModel):
    """
    A factual claim extracted from text for verification.
    
    Captures the claim text, context, and categorization
    for systematic fact-checking.
    """
    
    # Claim identification
    claim_id: str = Field(
        default="",
        description="Unique identifier for the claim"
    )
    claim_text: str = Field(
        ...,
        description="The exact text of the factual claim"
    )
    context: str = Field(
        default="",
        description="Surrounding context from the source document"
    )
    
    # Location in source
    source_section: str = Field(
        default="",
        description="Section of the document where claim was found"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Line number in source document if available"
    )
    
    # Classification
    category: ClaimCategory = Field(
        default=ClaimCategory.OTHER,
        description="Category of the claim"
    )
    entities_mentioned: List[str] = Field(
        default_factory=list,
        description="Entities mentioned in the claim"
    )
    
    # Claim characteristics
    is_quantitative: bool = Field(
        default=False,
        description="Whether the claim contains numerical data"
    )
    is_time_sensitive: bool = Field(
        default=False,
        description="Whether the claim's accuracy depends on timing"
    )
    requires_expert_knowledge: bool = Field(
        default=False,
        description="Whether verification requires domain expertise"
    )
    
    # Checkability
    is_checkable: bool = Field(
        default=True,
        description="Whether the claim can be fact-checked"
    )
    checkability_reason: str = Field(
        default="",
        description="Reason if claim is not checkable"
    )


class VerificationSource(BaseModel):
    """Source used to verify a claim."""
    
    name: str = Field(
        ...,
        description="Name of the verification source"
    )
    url: str = Field(
        default="",
        description="URL of the source"
    )
    credibility_score: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Credibility score of the source"
    )
    supports_claim: bool = Field(
        default=False,
        description="Whether source supports the claim"
    )
    contradicts_claim: bool = Field(
        default=False,
        description="Whether source contradicts the claim"
    )
    relevant_excerpt: str = Field(
        default="",
        description="Relevant excerpt from the source"
    )


class VerificationResult(BaseModel):
    """
    Result of fact-checking a claim.
    
    Contains the verification status, confidence level,
    and supporting evidence.
    """
    
    # Reference to original claim
    claim: FactualClaim = Field(
        ...,
        description="The original claim being verified"
    )
    
    # Verification outcome
    status: VerificationStatus = Field(
        default=VerificationStatus.UNCERTAIN,
        description="Verification status"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in the verification (0-1)"
    )
    
    # Evidence
    supporting_sources: List[VerificationSource] = Field(
        default_factory=list,
        description="Sources that support the claim"
    )
    contradicting_sources: List[VerificationSource] = Field(
        default_factory=list,
        description="Sources that contradict the claim"
    )
    
    # Analysis
    explanation: str = Field(
        default="",
        description="Explanation of the verification result"
    )
    corrected_claim: Optional[str] = Field(
        default=None,
        description="Corrected version of the claim if disputed"
    )
    
    # Metadata
    verification_date: datetime = Field(
        default_factory=datetime.now,
        description="When verification was performed"
    )
    
    @property
    def confidence_level(self) -> str:
        """Get confidence level label."""
        if self.confidence >= 0.8:
            return "high"
        elif self.confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    @property
    def status_emoji(self) -> str:
        """Get emoji for status."""
        return {
            VerificationStatus.VERIFIED: "✅",
            VerificationStatus.UNCERTAIN: "⚠️",
            VerificationStatus.DISPUTED: "❌",
            VerificationStatus.UNVERIFIABLE: "❓",
        }.get(self.status, "❓")
    
    def to_annotation(self) -> str:
        """Generate annotation text for the claim."""
        source_count = len(self.supporting_sources) + len(self.contradicting_sources)
        return (
            f"[{self.status_emoji} {self.status.value.upper()}] "
            f"(confidence: {self.confidence:.0%}, {source_count} sources checked)"
        )


class VerificationReport(BaseModel):
    """
    Complete verification report for a document.
    
    Summarizes all fact-checked claims with statistics.
    """
    
    # Document reference
    document_title: str = Field(
        default="",
        description="Title of the verified document"
    )
    
    # All verification results
    results: List[VerificationResult] = Field(
        default_factory=list,
        description="All verification results"
    )
    
    # Statistics
    total_claims: int = Field(
        default=0,
        ge=0,
        description="Total claims identified"
    )
    verified_count: int = Field(
        default=0,
        ge=0,
        description="Number of verified claims"
    )
    uncertain_count: int = Field(
        default=0,
        ge=0,
        description="Number of uncertain claims"
    )
    disputed_count: int = Field(
        default=0,
        ge=0,
        description="Number of disputed claims"
    )
    unverifiable_count: int = Field(
        default=0,
        ge=0,
        description="Number of unverifiable claims"
    )
    
    # Overall assessment
    overall_reliability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall reliability score (0-1)"
    )
    
    # Metadata
    verification_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When verification was completed"
    )
    
    def calculate_statistics(self) -> None:
        """Calculate statistics from results."""
        self.total_claims = len(self.results)
        self.verified_count = sum(
            1 for r in self.results if r.status == VerificationStatus.VERIFIED
        )
        self.uncertain_count = sum(
            1 for r in self.results if r.status == VerificationStatus.UNCERTAIN
        )
        self.disputed_count = sum(
            1 for r in self.results if r.status == VerificationStatus.DISPUTED
        )
        self.unverifiable_count = sum(
            1 for r in self.results if r.status == VerificationStatus.UNVERIFIABLE
        )
        
        # Calculate overall reliability
        if self.total_claims > 0:
            checkable = self.total_claims - self.unverifiable_count
            if checkable > 0:
                # Verified = 1.0, Uncertain = 0.5, Disputed = 0.0
                score = (
                    self.verified_count * 1.0 +
                    self.uncertain_count * 0.5 +
                    self.disputed_count * 0.0
                )
                self.overall_reliability = score / checkable
    
    def to_markdown_section(self) -> str:
        """Generate markdown verification status section."""
        self.calculate_statistics()
        
        # Reliability badge
        if self.overall_reliability >= 0.8:
            badge = "🟢 High Reliability"
        elif self.overall_reliability >= 0.5:
            badge = "🟡 Moderate Reliability"
        else:
            badge = "🔴 Low Reliability"
        
        lines = [
            "## Verification Status",
            "",
            f"**{badge}** ({self.overall_reliability:.0%} verified)",
            "",
            "### Claim Summary",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✅ Verified | {self.verified_count} |",
            f"| ⚠️ Uncertain | {self.uncertain_count} |",
            f"| ❌ Disputed | {self.disputed_count} |",
            f"| ❓ Unverifiable | {self.unverifiable_count} |",
            f"| **Total** | **{self.total_claims}** |",
            "",
        ]
        
        # Add disputed claims if any
        if self.disputed_count > 0:
            lines.extend([
                "### ⚠️ Disputed Claims",
                "",
            ])
            for result in self.results:
                if result.status == VerificationStatus.DISPUTED:
                    lines.append(f"- **Claim:** {result.claim.claim_text}")
                    if result.corrected_claim:
                        lines.append(f"  - **Correction:** {result.corrected_claim}")
                    lines.append(f"  - **Explanation:** {result.explanation}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary."""
        self.calculate_statistics()
        return {
            "document_title": self.document_title,
            "total_claims": self.total_claims,
            "verified": self.verified_count,
            "uncertain": self.uncertain_count,
            "disputed": self.disputed_count,
            "unverifiable": self.unverifiable_count,
            "overall_reliability": self.overall_reliability,
            "verification_timestamp": self.verification_timestamp.isoformat(),
        }
