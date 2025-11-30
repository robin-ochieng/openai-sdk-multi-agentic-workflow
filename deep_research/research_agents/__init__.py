"""
Research Agents for Deep Research System

Six specialized agents working together in a pipeline:
1. QueryAnalyzerAgent - Classifies and understands research queries
2. SourceValidatorAgent - Validates and scores source credibility
3. PlannerAgent - Creates strategic search plans
4. SearchAgent - Performs web searches and summarizes results
5. WriterAgent - Synthesizes results into comprehensive reports
6. EmailAgent - Converts to HTML and sends via Gmail SMTP
"""

from .query_analyzer_agent import (
    create_query_analyzer_agent,
    EnhancedQueryAnalyzer,
    estimate_search_count,
    get_recommended_report_length,
)
from .source_validator_agent import (
    create_source_validator_agent,
    SourceValidator,
    EnhancedSourceValidator,
    DomainClassifier,
    validate_search_results,
    get_domain_classifier,
    get_source_validator,
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
    # Source Validation
    'create_source_validator_agent',
    'SourceValidator',
    'EnhancedSourceValidator',
    'DomainClassifier',
    'validate_search_results',
    'get_domain_classifier',
    'get_source_validator',
    # Core Pipeline
    'create_planner_agent',
    'create_search_agent',
    'create_writer_agent',
    'create_email_agent',
]
