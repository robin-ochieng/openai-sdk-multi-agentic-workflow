"""
Deep Research Agent Package
AI-powered research system with 4-agent pipeline
"""

from .research_manager import ResearchManager
from .models import (
    WebSearchItem,
    WebSearchPlan,
    ResearchSummary,
    ReportData,
    EmailResponse
)

__version__ = "1.0.0"
__all__ = [
    'ResearchManager',
    'WebSearchItem',
    'WebSearchPlan',
    'ResearchSummary',
    'ReportData',
    'EmailResponse'
]
