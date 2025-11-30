"""
Research Agents for Deep Research System

Five specialized agents working together in a pipeline:
1. QueryAnalyzerAgent - Classifies and understands research queries
2. PlannerAgent - Creates strategic search plans
3. SearchAgent - Performs web searches and summarizes results
4. WriterAgent - Synthesizes results into comprehensive reports
5. EmailAgent - Converts to HTML and sends via Gmail SMTP
"""

from .query_analyzer_agent import (
    create_query_analyzer_agent,
    EnhancedQueryAnalyzer,
    estimate_search_count,
    get_recommended_report_length,
)
from .planner_agent import create_planner_agent
from .search_agent import create_search_agent
from .writer_agent import create_writer_agent
from .email_agent import create_email_agent

__all__ = [
    # Query Analysis
    'create_query_analyzer_agent',
    'EnhancedQueryAnalyzer',
    'estimate_search_count',
    'get_recommended_report_length',
    # Core Pipeline
    'create_planner_agent',
    'create_search_agent',
    'create_writer_agent',
    'create_email_agent',
]
