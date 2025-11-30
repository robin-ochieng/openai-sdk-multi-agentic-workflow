"""
Source validation models for the Deep Research Agent.

Provides Pydantic schemas for assessing source credibility including:
- SourceMetadata: Input data about a source (url, title, snippet, date)
- SourceCredibility: Detailed credibility assessment with scores
- ValidationResult: Collection of validated sources with statistics
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, HttpUrl


class CredibilityLevel(str, Enum):
    """Categorical credibility rating for sources."""
    
    HIGH = "high"  # Score >= 70: Authoritative, reliable
    MEDIUM = "medium"  # Score 50-69: Generally reliable, some caveats
    LOW = "low"  # Score 30-49: Use with caution, needs corroboration
    UNRELIABLE = "unreliable"  # Score < 30: Should not be used


class InclusionDecision(str, Enum):
    """Decision on whether to include source in research."""
    
    INCLUDE = "include"  # Use source without reservations
    INCLUDE_WITH_CAVEAT = "include_with_caveat"  # Use but note limitations
    EXCLUDE = "exclude"  # Do not use this source


class DomainCategory(str, Enum):
    """Category of the source domain."""
    
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    MAJOR_NEWS = "major_news"
    TECH_AUTHORITATIVE = "tech_authoritative"
    OFFICIAL_COMPANY = "official_company"
    RESEARCH_DATA = "research_data"
    USER_GENERATED = "user_generated"
    WIKI_COLLABORATIVE = "wiki_collaborative"
    SOCIAL_MEDIA = "social_media"
    CONTENT_FARMS = "content_farms"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class SourceMetadata(BaseModel):
    """Input metadata about a source for credibility assessment."""
    
    url: str = Field(
        ...,
        description="Full URL of the source"
    )
    title: str = Field(
        default="",
        description="Title of the source document/page"
    )
    snippet: str = Field(
        default="",
        description="Brief excerpt or summary from the source"
    )
    publication_date: Optional[datetime] = Field(
        default=None,
        description="Publication or last updated date"
    )
    author: Optional[str] = Field(
        default=None,
        description="Author or publishing organization"
    )
    source_type: Optional[str] = Field(
        default=None,
        description="Type of source (article, paper, blog, etc.)"
    )
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is properly formatted."""
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith(('http://', 'https://')):
            v = f"https://{v}"
        return v
    
    def extract_domain(self) -> str:
        """Extract domain from URL for categorization."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(self.url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""


class CredibilityScores(BaseModel):
    """Individual credibility dimension scores (0-100 scale)."""
    
    authority: int = Field(
        ...,
        ge=0,
        le=100,
        description="Domain/source authority and expertise (0-100)"
    )
    recency: int = Field(
        ...,
        ge=0,
        le=100,
        description="How current the information is (0-100)"
    )
    objectivity: int = Field(
        ...,
        ge=0,
        le=100,
        description="Perceived neutrality and balance (0-100)"
    )
    corroboration: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Alignment with other sources (0-100, default 50 if unchecked)"
    )
    
    def calculate_overall(self, weights: Optional[Dict[str, float]] = None) -> int:
        """
        Calculate weighted overall score.
        
        Args:
            weights: Custom weights for each dimension. 
                     Defaults to authority:0.35, recency:0.25, objectivity:0.25, corroboration:0.15
        
        Returns:
            Overall credibility score (0-100)
        """
        default_weights = {
            "authority": 0.35,
            "recency": 0.25,
            "objectivity": 0.25,
            "corroboration": 0.15
        }
        w = weights or default_weights
        
        overall = (
            self.authority * w["authority"] +
            self.recency * w["recency"] +
            self.objectivity * w["objectivity"] +
            self.corroboration * w["corroboration"]
        )
        return round(overall)


class ExclusionReason(BaseModel):
    """Detailed reason for source exclusion."""
    
    reason_code: str = Field(
        ...,
        description="Machine-readable reason code"
    )
    reason_text: str = Field(
        ...,
        description="Human-readable explanation"
    )
    severity: str = Field(
        default="warning",
        description="Severity: 'critical', 'warning', or 'info'"
    )
    remediation: Optional[str] = Field(
        default=None,
        description="Suggested action to address the issue"
    )


class SourceCredibility(BaseModel):
    """
    Complete credibility assessment for a single source.
    
    This is the primary output from the SourceValidatorAgent,
    containing all scoring dimensions plus the final decision.
    """
    
    source: SourceMetadata = Field(
        ...,
        description="Original source metadata"
    )
    domain: str = Field(
        ...,
        description="Extracted domain from URL"
    )
    domain_category: DomainCategory = Field(
        default=DomainCategory.UNKNOWN,
        description="Categorization of the domain"
    )
    scores: CredibilityScores = Field(
        ...,
        description="Individual dimension scores"
    )
    overall_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall credibility score (0-100)"
    )
    credibility_level: CredibilityLevel = Field(
        ...,
        description="Categorical credibility rating"
    )
    decision: InclusionDecision = Field(
        ...,
        description="Whether to include this source"
    )
    exclusion_reasons: List[ExclusionReason] = Field(
        default_factory=list,
        description="Reasons for exclusion or caveats (if any)"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in this assessment (0-1)"
    )
    score_badge: str = Field(
        default="",
        description="Display badge for UI (e.g., '⭐ High Credibility')"
    )
    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this validation was performed"
    )
    
    @classmethod
    def create(
        cls,
        source: SourceMetadata,
        scores: CredibilityScores,
        domain_category: DomainCategory = DomainCategory.UNKNOWN,
        exclusion_reasons: Optional[List[ExclusionReason]] = None
    ) -> "SourceCredibility":
        """
        Factory method to create a SourceCredibility with calculated fields.
        
        Args:
            source: Source metadata
            scores: Credibility scores
            domain_category: Category of the domain
            exclusion_reasons: Any reasons for concern
        
        Returns:
            Fully populated SourceCredibility instance
        """
        overall = scores.calculate_overall()
        
        # Determine credibility level
        if overall >= 70:
            level = CredibilityLevel.HIGH
        elif overall >= 50:
            level = CredibilityLevel.MEDIUM
        elif overall >= 30:
            level = CredibilityLevel.LOW
        else:
            level = CredibilityLevel.UNRELIABLE
        
        # Determine inclusion decision
        reasons = exclusion_reasons or []
        has_critical = any(r.severity == "critical" for r in reasons)
        
        if has_critical or overall < 30:
            decision = InclusionDecision.EXCLUDE
        elif overall < 50 or len(reasons) > 0:
            decision = InclusionDecision.INCLUDE_WITH_CAVEAT
        else:
            decision = InclusionDecision.INCLUDE
        
        # Generate score badge
        badge = cls._generate_badge(level, overall)
        
        return cls(
            source=source,
            domain=source.extract_domain(),
            domain_category=domain_category,
            scores=scores,
            overall_score=overall,
            credibility_level=level,
            decision=decision,
            exclusion_reasons=reasons,
            score_badge=badge
        )
    
    @staticmethod
    def _generate_badge(level: CredibilityLevel, score: int) -> str:
        """Generate a display badge based on credibility level."""
        badges = {
            CredibilityLevel.HIGH: f"⭐ High Credibility ({score})",
            CredibilityLevel.MEDIUM: f"✓ Medium Credibility ({score})",
            CredibilityLevel.LOW: f"⚠️ Low Credibility ({score})",
            CredibilityLevel.UNRELIABLE: f"❌ Unreliable ({score})"
        }
        return badges.get(level, f"? Unknown ({score})")


class ValidationStatistics(BaseModel):
    """Statistics from a batch validation run."""
    
    total_sources: int = Field(
        default=0,
        description="Total sources validated"
    )
    included: int = Field(
        default=0,
        description="Sources included without caveat"
    )
    included_with_caveat: int = Field(
        default=0,
        description="Sources included with caveats"
    )
    excluded: int = Field(
        default=0,
        description="Sources excluded"
    )
    average_score: float = Field(
        default=0.0,
        description="Average overall score of all sources"
    )
    high_credibility_count: int = Field(
        default=0,
        description="Count of high credibility sources"
    )
    validation_duration_ms: int = Field(
        default=0,
        description="Time taken to validate in milliseconds"
    )
    
    @property
    def inclusion_rate(self) -> float:
        """Percentage of sources included."""
        if self.total_sources == 0:
            return 0.0
        return (self.included + self.included_with_caveat) / self.total_sources * 100


class ValidationResult(BaseModel):
    """
    Result of validating a batch of sources.
    
    Contains validated sources partitioned by decision,
    along with aggregate statistics.
    """
    
    query_context: str = Field(
        default="",
        description="The research query these sources relate to"
    )
    included_sources: List[SourceCredibility] = Field(
        default_factory=list,
        description="Sources approved for use"
    )
    caveat_sources: List[SourceCredibility] = Field(
        default_factory=list,
        description="Sources approved with caveats"
    )
    excluded_sources: List[SourceCredibility] = Field(
        default_factory=list,
        description="Sources excluded from research"
    )
    statistics: ValidationStatistics = Field(
        default_factory=ValidationStatistics,
        description="Aggregate statistics"
    )
    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When validation was performed"
    )
    
    def get_usable_sources(self) -> List[SourceCredibility]:
        """Get all sources that can be used (include + caveat)."""
        return self.included_sources + self.caveat_sources
    
    def get_top_sources(self, n: int = 5) -> List[SourceCredibility]:
        """Get the top N sources by overall score."""
        all_usable = self.get_usable_sources()
        return sorted(all_usable, key=lambda x: x.overall_score, reverse=True)[:n]
    
    def to_search_results(self) -> List[Dict[str, Any]]:
        """
        Convert validated sources back to search result format.
        
        Returns list compatible with the existing search result structure,
        with credibility metadata added.
        """
        results = []
        for source in self.get_usable_sources():
            results.append({
                "url": source.source.url,
                "title": source.source.title,
                "snippet": source.source.snippet,
                "credibility_score": source.overall_score,
                "credibility_badge": source.score_badge,
                "credibility_level": source.credibility_level.value,
                "has_caveats": source.decision == InclusionDecision.INCLUDE_WITH_CAVEAT,
                "caveats": [r.reason_text for r in source.exclusion_reasons]
            })
        return results
