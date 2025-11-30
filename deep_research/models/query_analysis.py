"""
Query Analysis Models for Deep Research Agent

This module defines Pydantic models for structured query classification.
The QueryAnalyzerAgent uses these schemas to inspect every incoming research
query and produce actionable metadata that downstream agents (planner, search,
writer) can leverage for optimized results.

Extending Classifications:
    To add a new query_type or audience_level:
    1. Add the value to the corresponding Literal type.
    2. Update QUERY_TYPE_DESCRIPTIONS or similar docstrings as needed.
    3. Adjust any downstream logic in ResearchManager that keys on these values.

Example:
    >>> analysis = QueryAnalysis(
    ...     query_type="market_research",
    ...     complexity="moderate",
    ...     time_sensitivity="current",
    ...     primary_entities=["OpenAI", "Anthropic"],
    ...     audience_level="executive",
    ...     required_depth="detailed",
    ...     recommended_sections=["Market Overview", "Competitive Landscape"],
    ... )
    >>> print(analysis.recommended_search_count)
    5
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumeration Literals (using Literal for JSON-friendly structured outputs)
# ---------------------------------------------------------------------------

QueryType = Literal[
    "exploratory",          # Open-ended discovery
    "comparative",          # Comparing options, technologies, companies
    "technical",            # Deep technical specifications or how-to
    "market_research",      # Market sizing, trends, industry analysis
    "due_diligence",        # Investment or acquisition research
    "competitive_analysis", # Competitor landscape
    "trend_analysis",       # Emerging trends and future outlook
    "general",              # Catch-all for simple factual queries
]

ComplexityLevel = Literal[
    "simple",       # Single concept, direct answer
    "moderate",     # Multiple related concepts
    "complex",      # Requires synthesis across domains
    "expert_level", # Specialized knowledge, extensive research
]

TimeSensitivity = Literal[
    "historical",       # Past events, archival data
    "current",          # Recent developments, latest info
    "future_focused",   # Predictions, roadmaps
    "evergreen",        # Timeless content
]

AudienceLevel = Literal[
    "executive",   # C-suite, high-level summaries
    "technical",   # Engineers, developers, detailed specs
    "investor",    # Financial focus, ROI, risk
    "general",     # Non-specialist, accessible language
]

ResearchDepth = Literal[
    "overview",        # Quick summary, 500-1000 words
    "detailed",        # Standard report, 1500-2500 words
    "comprehensive",   # In-depth analysis, 3000-5000 words
    "exhaustive",      # Full research paper, 5000+ words
]


# ---------------------------------------------------------------------------
# Descriptions for prompt engineering and documentation
# ---------------------------------------------------------------------------

QUERY_TYPE_DESCRIPTIONS: dict[str, str] = {
    "exploratory": "Open-ended discovery of a topic without a specific hypothesis.",
    "comparative": "Side-by-side comparison of multiple options, products, or strategies.",
    "technical": "Detailed technical specifications, implementations, or how-to guides.",
    "market_research": "Industry sizing, market trends, TAM/SAM/SOM, growth rates.",
    "due_diligence": "Investment-grade research for M&A, funding, or partnerships.",
    "competitive_analysis": "Mapping competitor strengths, weaknesses, strategies.",
    "trend_analysis": "Emerging technologies, future outlook, and predictions.",
    "general": "Straightforward factual queries or definitions.",
}


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class QueryAnalysis(BaseModel):
    """
    Structured classification of a user's research query.

    Populated by the QueryAnalyzerAgent before the planning phase begins.
    Downstream agents reference these fields to tailor searches, report
    structure, and visualizations.

    Attributes:
        query_type: Primary classification of the research intent.
        complexity: Estimated difficulty/depth of research required.
        time_sensitivity: Whether the query needs fresh, historical, or timeless data.
        primary_entities: Key subjects (companies, technologies, people) to investigate.
        secondary_entities: Related/supporting entities to consider.
        geographic_scope: Regional focus (e.g., "global", "North America", "Kenya").
        time_range: Explicit time window if mentioned (e.g., "2020-2024", "last 6 months").
        audience_level: Who will consume the report—affects tone and detail.
        required_depth: How extensive the final report should be.
        recommended_sections: Suggested report headings based on query type.
        required_data_points: Specific metrics or facts needed (e.g., "revenue", "market share").
        visualization_opportunities: Charts or infographics that would add value.
        estimated_research_time: Approximate minutes needed for thorough research.
        recommended_search_count: Number of distinct web searches to plan.
    """

    # --- Core Classification ---
    query_type: QueryType = Field(
        default="general",
        description="Primary classification of the research intent.",
    )
    complexity: ComplexityLevel = Field(
        default="moderate",
        description="Estimated difficulty of the research task.",
    )
    time_sensitivity: TimeSensitivity = Field(
        default="current",
        description="Temporal focus of the query.",
    )

    # --- Entities ---
    primary_entities: List[str] = Field(
        default_factory=list,
        description="Key subjects to investigate (companies, technologies, people, concepts).",
    )
    secondary_entities: List[str] = Field(
        default_factory=list,
        description="Supporting or related entities.",
    )

    # --- Scope ---
    geographic_scope: str = Field(
        default="global",
        description="Geographic focus of the research.",
    )
    time_range: Optional[str] = Field(
        default=None,
        description="Explicit time window mentioned in the query (e.g., '2023-2024').",
    )

    # --- Audience & Depth ---
    audience_level: AudienceLevel = Field(
        default="general",
        description="Target audience for the final report.",
    )
    required_depth: ResearchDepth = Field(
        default="detailed",
        description="Expected depth and length of the final report.",
    )

    # --- Output Guidance ---
    recommended_sections: List[str] = Field(
        default_factory=list,
        description="Suggested section headings for the report.",
    )
    required_data_points: List[str] = Field(
        default_factory=list,
        description="Specific data or metrics the user expects.",
    )
    visualization_opportunities: List[str] = Field(
        default_factory=list,
        description="Chart or visual types that would enhance the report.",
    )

    # --- Resource Estimation ---
    estimated_research_time: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Estimated minutes to complete research.",
    )
    recommended_search_count: int = Field(
        default=5,
        ge=3,
        le=15,
        description="Optimal number of web searches to perform.",
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "query_type": "market_research",
                    "complexity": "complex",
                    "time_sensitivity": "current",
                    "primary_entities": ["AI code assistants", "GitHub Copilot"],
                    "secondary_entities": ["Amazon CodeWhisperer", "Tabnine"],
                    "geographic_scope": "global",
                    "time_range": "2023-2025",
                    "audience_level": "executive",
                    "required_depth": "comprehensive",
                    "recommended_sections": [
                        "Executive Summary",
                        "Market Overview",
                        "Competitive Landscape",
                        "Technology Trends",
                        "Future Outlook",
                    ],
                    "required_data_points": ["market size", "growth rate", "adoption rate"],
                    "visualization_opportunities": ["market share pie chart", "trend line"],
                    "estimated_research_time": 10,
                    "recommended_search_count": 7,
                }
            ]
        }


class QueryAnalysisRequest(BaseModel):
    """
    Input wrapper for the QueryAnalyzerAgent.

    Attributes:
        query: The raw user research question.
        context: Optional additional context (domain, prior research, etc.).
    """

    query: str = Field(
        ...,
        min_length=5,
        description="The user's research question or topic.",
    )
    context: Optional[str] = Field(
        default=None,
        description="Optional additional context to refine classification.",
    )
