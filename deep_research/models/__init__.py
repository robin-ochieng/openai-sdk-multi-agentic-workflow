"""
Structured Output Models for Deep Research Agent
Using Pydantic for type safety and validation
"""

from .research_models import (
    WebSearchItem,
    WebSearchPlan,
    ResearchSummary,
    ReportData,
    EmailResponse,
    SourceMetrics,
)

from .query_analysis import (
    QueryAnalysis,
    QueryAnalysisRequest,
    QueryType,
    ComplexityLevel,
    TimeSensitivity,
    AudienceLevel,
    ResearchDepth,
    QUERY_TYPE_DESCRIPTIONS,
)

from .source_validation import (
    SourceMetadata,
    SourceCredibility,
    CredibilityScores,
    ValidationResult,
    ValidationStatistics,
    CredibilityLevel,
    InclusionDecision,
    DomainCategory,
    ExclusionReason,
)

from .academic_models import (
    AcademicSource,
    AcademicSearchFilters,
    AcademicSearchQuery,
    AcademicSearchResult,
    Author,
    FieldOfStudy,
    PublicationVenue,
)

from .market_models import (
    MarketSnapshot,
    MarketMetrics,
    CompetitorProfile,
    PricingBenchmark,
    RiskNote,
    SECFilingData,
    MarketIntelligenceQuery,
    MarketTrend,
    RiskLevel,
    DataConfidence,
)

__all__ = [
    # Research Models
    'WebSearchItem',
    'WebSearchPlan',
    'ResearchSummary',
    'ReportData',
    'EmailResponse',
    'SourceMetrics',
    # Query Analysis Models
    'QueryAnalysis',
    'QueryAnalysisRequest',
    'QueryType',
    'ComplexityLevel',
    'TimeSensitivity',
    'AudienceLevel',
    'ResearchDepth',
    'QUERY_TYPE_DESCRIPTIONS',
    # Source Validation Models
    'SourceMetadata',
    'SourceCredibility',
    'CredibilityScores',
    'ValidationResult',
    'ValidationStatistics',
    'CredibilityLevel',
    'InclusionDecision',
    'DomainCategory',
    'ExclusionReason',
    # Academic Models
    'AcademicSource',
    'AcademicSearchFilters',
    'AcademicSearchQuery',
    'AcademicSearchResult',
    'Author',
    'FieldOfStudy',
    'PublicationVenue',
    # Market Intelligence Models
    'MarketSnapshot',
    'MarketMetrics',
    'CompetitorProfile',
    'PricingBenchmark',
    'RiskNote',
    'SECFilingData',
    'MarketIntelligenceQuery',
    'MarketTrend',
    'RiskLevel',
    'DataConfidence',
]
