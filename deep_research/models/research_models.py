"""
Pydantic Models for Structured Outputs in Deep Research Agent
All agent responses use these models for type safety and validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional


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
    Final comprehensive research report
    
    Attributes:
        short_summary: Brief 2-3 sentence overview of findings
        markdown_report: Full report in markdown format (5-10 pages, 1000+ words)
        follow_up_questions: Suggested topics for further research
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
