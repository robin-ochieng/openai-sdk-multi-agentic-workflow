"""
Research Agents for Deep Research System

Seven specialized agents working together in a pipeline:
1. QueryAnalyzerAgent - Classifies and understands research queries
2. SourceValidatorAgent - Validates and scores source credibility
3. AcademicResearchAgent - Fetches peer-reviewed papers from Semantic Scholar
4. PlannerAgent - Creates strategic search plans
5. SearchAgent - Performs web searches and summarizes results
6. WriterAgent - Synthesizes results into comprehensive reports
7. EmailAgent - Converts to HTML and sends via Gmail SMTP
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
from .academic_agent import (
    AcademicResearchAgent,
    SemanticScholarClient,
    create_academic_research_agent,
    should_use_academic_search,
    get_academic_filters_from_query_analysis,
)
from .market_agent import (
    MarketIntelligenceAgent,
    SECFilingParser,
    SECAPIClient,
    create_market_intelligence_agent,
    should_use_market_intelligence,
    get_sec_filing_parser,
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
    # Academic Research
    'AcademicResearchAgent',
    'SemanticScholarClient',
    'create_academic_research_agent',
    'should_use_academic_search',
    'get_academic_filters_from_query_analysis',
    # Market Intelligence
    'MarketIntelligenceAgent',
    'SECFilingParser',
    'SECAPIClient',
    'create_market_intelligence_agent',
    'should_use_market_intelligence',
    'get_sec_filing_parser',
    # Core Pipeline
    'create_planner_agent',
    'create_search_agent',
    'create_writer_agent',
    'create_email_agent',
]
