"""
Structured Output Models for Deep Research Agent
Using Pydantic for type safety and validation
"""

from .research_models import (
    WebSearchItem,
    WebSearchPlan,
    ResearchSummary,
    ReportData,
    EmailResponse
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

__all__ = [
    # Research Models
    'WebSearchItem',
    'WebSearchPlan',
    'ResearchSummary',
    'ReportData',
    'EmailResponse',
    # Query Analysis Models
    'QueryAnalysis',
    'QueryAnalysisRequest',
    'QueryType',
    'ComplexityLevel',
    'TimeSensitivity',
    'AudienceLevel',
    'ResearchDepth',
    'QUERY_TYPE_DESCRIPTIONS',
]
