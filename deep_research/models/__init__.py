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

__all__ = [
    'WebSearchItem',
    'WebSearchPlan',
    'ResearchSummary',
    'ReportData',
    'EmailResponse'
]
