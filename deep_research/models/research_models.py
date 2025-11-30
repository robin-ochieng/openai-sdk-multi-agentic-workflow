"""
Pydantic Models for Structured Outputs in Deep Research Agent
All agent responses use these models for type safety and validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SourceMetrics(BaseModel):
    """
    Aggregated metrics from source validation.
    
    Provides summary statistics about the quality and distribution
    of sources used in the research report.
    """
    total_sources: int = Field(
        default=0,
        description="Total number of sources collected"
    )
    included_count: int = Field(
        default=0,
        description="Number of sources included without caveats"
    )
    caveat_count: int = Field(
        default=0,
        description="Number of sources included with caveats"
    )
    excluded_count: int = Field(
        default=0,
        description="Number of sources excluded for low credibility"
    )
    average_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Average credibility score across all sources (0-100)"
    )
    high_credibility_count: int = Field(
        default=0,
        description="Number of high-credibility sources (score >= 70)"
    )
    category_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of sources by domain category"
    )
    
    @property
    def inclusion_rate(self) -> float:
        """Percentage of sources included (with or without caveats)."""
        if self.total_sources == 0:
            return 0.0
        return (self.included_count + self.caveat_count) / self.total_sources * 100
    
    @property
    def quality_tier(self) -> str:
        """Overall quality tier based on average score."""
        if self.average_score >= 70:
            return "high"
        elif self.average_score >= 50:
            return "medium"
        elif self.average_score >= 30:
            return "low"
        else:
            return "poor"


class WebSearchItem(BaseModel):
    """
    Single web search to perform
    
    Attributes:
        reason: Why this search is important to the query (helps focus results)
        query: The specific search term to use for the web search
    """
    reason: str = Field(
        description="Your reasoning for why this search is important to the query."
    )
    query: str = Field(
        description="The search term to use for the web search."
    )


class WebSearchPlan(BaseModel):
    """
    Plan containing multiple web searches to perform
    
    Attributes:
        searches: List of 3-5 targeted web searches to best answer the query
    """
    searches: List[WebSearchItem] = Field(
        description="A list of web searches to perform to best answer the query.",
        min_items=3,
        max_items=5
    )


class ResearchSummary(BaseModel):
    """
    Concise summary of a single search result
    
    Attributes:
        search_term: The original search term used
        key_findings: 2-3 paragraph summary (less than 300 words)
        sources: List of URLs referenced
    """
    search_term: str = Field(
        description="The search term that was used"
    )
    key_findings: str = Field(
        description="A concise 2-3 paragraph summary of the key findings (max 300 words). "
                    "Capture main points without fluff."
    )
    sources: List[str] = Field(
        description="List of source URLs referenced in this summary",
        default_factory=list
    )


class ReportData(BaseModel):
    """
    Final comprehensive research report with metadata.
    
    Extended to capture query analysis context, source quality metrics,
    and planning notes for transparency and reproducibility.
    
    Attributes:
        short_summary: Brief 2-3 sentence overview of findings
        markdown_report: Full report in markdown format (5-10 pages, 1000+ words)
        follow_up_questions: Suggested topics for further research
        query_analysis_summary: Optional summary of query classification
        source_metrics: Aggregated source quality metrics
        planning_notes: Notes about research strategy and methodology
        sources_with_credibility: Sources tagged with credibility badges
    """
    short_summary: str = Field(
        description="A short 2-3 sentence summary of the findings."
    )
    
    markdown_report: str = Field(
        description="The final comprehensive report in markdown format. "
                    "Should be 5-10 pages (1000+ words) with proper structure, "
                    "headings, and detailed analysis."
    )
    
    follow_up_questions: List[str] = Field(
        description="Suggested topics to research further based on the findings",
        default_factory=list
    )
    
    # New fields for enhanced metadata
    query_analysis_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of query analysis including type, complexity, and entities"
    )
    
    source_metrics: Optional[SourceMetrics] = Field(
        default=None,
        description="Aggregated metrics about source quality and distribution"
    )
    
    planning_notes: Optional[str] = Field(
        default=None,
        description="Notes about research methodology and strategy"
    )
    
    sources_with_credibility: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of sources with credibility scores and badges"
    )


class EmailResponse(BaseModel):
    """
    Response from email sending operation
    
    Attributes:
        status: Success or failure status
        message: Human-readable message about the operation
        recipient: Email address where report was sent
    """
    status: str = Field(
        description="Status of email operation: 'success' or 'error'"
    )
    message: str = Field(
        description="Human-readable message about what happened"
    )
    recipient: str = Field(
        description="Email address where the report was sent"
    )
