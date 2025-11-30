"""
Query Analyzer Agent

Inspects incoming research queries and produces structured QueryAnalysis
objects that downstream agents (planner, search, writer) use for optimized
research strategies.

Usage:
    >>> from deep_research.research_agents import create_query_analyzer_agent
    >>> from agents import Runner
    >>> agent = create_query_analyzer_agent(api_key)
    >>> result = await Runner.run(agent, "What is the current state of AI in healthcare?")
    >>> print(result.final_output.query_type)  # e.g., "exploratory"

Extending Classifications:
    1. Add new query_type values in models/query_analysis.py
    2. Update INSTRUCTIONS below to describe the new category
    3. Add examples to help the model recognize the pattern
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from openai import OpenAI
from agents import Agent, ModelSettings

from deep_research.models.query_analysis import (
    QueryAnalysis,
    QueryAnalysisRequest,
    QUERY_TYPE_DESCRIPTIONS,
)

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "gpt-4o"

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
INSTRUCTIONS = """
You are an expert research query analyst. Your role is to deeply understand
user research queries and produce structured classification metadata.

For EVERY query, analyze and determine:

## 1. Query Type Classification
Classify into ONE of these categories:
- exploratory: Open-ended discovery, no specific hypothesis
- comparative: Comparing multiple options, products, or companies
- technical: Deep technical specs, implementations, how-to guides
- market_research: Industry analysis, market sizing, trends
- due_diligence: Investment or acquisition research
- competitive_analysis: Competitor landscape mapping
- trend_analysis: Emerging trends, future outlook
- general: Simple factual queries or definitions

## 2. Complexity Assessment
- simple: Single concept, direct answer
- moderate: Multiple related concepts
- complex: Cross-domain synthesis required
- expert_level: Specialized knowledge needed

## 3. Time Sensitivity
- historical: Past events, archival data
- current: Recent developments, latest information
- future_focused: Predictions, roadmaps, forecasts
- evergreen: Timeless content

## 4. Entity Extraction
- Identify PRIMARY entities: Main companies, technologies, people, or concepts
- Identify SECONDARY entities: Related or supporting subjects
- Determine GEOGRAPHIC scope: global, regional, or country-specific
- Extract TIME RANGE if mentioned: specific dates or periods

## 5. Audience Assessment
- executive: C-suite, high-level summaries
- technical: Engineers, detailed specifications
- investor: Financial focus, ROI, risk analysis
- general: Non-specialist, accessible language

## 6. Depth Determination
- overview: Quick summary (500-1000 words)
- detailed: Standard report (1500-2500 words)
- comprehensive: In-depth analysis (3000-5000 words)
- exhaustive: Full research paper (5000+ words)

## 7. Output Planning
- Recommend SECTIONS based on query type and audience
- Identify required DATA POINTS (metrics, statistics)
- Suggest VISUALIZATION opportunities (charts, infographics)
- Estimate RESEARCH TIME in minutes
- Recommend optimal SEARCH COUNT (3-15 searches)

### Guidelines:
- Be precise with entity extraction—include full company/technology names
- Match audience level to implicit cues (jargon suggests technical audience)
- Complex queries with multiple subjects need more searches (7-10)
- Market research queries should include market size, growth rate in data points
- Technical queries should include benchmarks, specifications in data points

Output your analysis as a structured JSON matching the QueryAnalysis schema.
"""

# ---------------------------------------------------------------------------
# Example Classifications (for few-shot prompting)
# ---------------------------------------------------------------------------
EXAMPLE_CLASSIFICATIONS = [
    {
        "query": "What is the current state of AI in software development?",
        "analysis": {
            "query_type": "exploratory",
            "complexity": "moderate",
            "time_sensitivity": "current",
            "primary_entities": ["AI", "software development"],
            "secondary_entities": ["GitHub Copilot", "code generation", "DevOps"],
            "geographic_scope": "global",
            "time_range": None,
            "audience_level": "general",
            "required_depth": "detailed",
            "recommended_sections": [
                "Executive Summary",
                "Introduction",
                "Current State Analysis",
                "Key Technologies",
                "Industry Adoption",
                "Challenges",
                "Future Outlook",
                "Recommendations",
            ],
            "required_data_points": ["adoption rate", "productivity gains", "tool usage statistics"],
            "visualization_opportunities": ["adoption trend chart", "tool comparison table"],
            "estimated_research_time": 7,
            "recommended_search_count": 5,
        },
    },
    {
        "query": "Compare AWS, Azure, and Google Cloud for enterprise AI workloads in 2024",
        "analysis": {
            "query_type": "comparative",
            "complexity": "complex",
            "time_sensitivity": "current",
            "primary_entities": ["AWS", "Azure", "Google Cloud"],
            "secondary_entities": ["enterprise AI", "cloud computing", "machine learning platforms"],
            "geographic_scope": "global",
            "time_range": "2024",
            "audience_level": "technical",
            "required_depth": "comprehensive",
            "recommended_sections": [
                "Executive Summary",
                "Introduction",
                "Platform Overview",
                "Feature Comparison",
                "Pricing Analysis",
                "Performance Benchmarks",
                "Use Case Recommendations",
                "Conclusion",
            ],
            "required_data_points": ["pricing tiers", "GPU availability", "ML service offerings", "SLAs"],
            "visualization_opportunities": ["feature comparison matrix", "pricing chart", "benchmark radar"],
            "estimated_research_time": 12,
            "recommended_search_count": 8,
        },
    },
]


# ---------------------------------------------------------------------------
# Agent Factory
# ---------------------------------------------------------------------------
def create_query_analyzer_agent(
    api_key: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> Agent:
    """
    Create a Query Analyzer Agent that classifies research queries.

    The agent inspects user queries and returns structured QueryAnalysis
    objects with classification metadata, entity extraction, and research
    planning recommendations.

    Args:
        api_key: OpenAI API key for authentication.
        model: Model identifier (default: gpt-4o).
        temperature: Sampling temperature; lower = more deterministic (default: 0.3).
        max_tokens: Maximum tokens for the response (default: 1500).

    Returns:
        Configured Agent instance with QueryAnalysis output type.

    Example:
        >>> agent = create_query_analyzer_agent(api_key)
        >>> result = await Runner.run(agent, "Market size of electric vehicles in Europe")
        >>> print(result.final_output.query_type)
        'market_research'
        >>> print(result.final_output.primary_entities)
        ['electric vehicles', 'Europe EV market']
    """
    logger.info(f"Creating QueryAnalyzerAgent with model={model}, temperature={temperature}")

    # Build enhanced instructions with examples
    enhanced_instructions = INSTRUCTIONS + "\n\n## Example Classifications:\n"
    for example in EXAMPLE_CLASSIFICATIONS:
        enhanced_instructions += f"\nQuery: \"{example['query']}\"\n"
        enhanced_instructions += f"Analysis: {example['analysis']}\n"

    agent = Agent(
        name="QueryAnalyzerAgent",
        instructions=enhanced_instructions,
        model=model,
        output_type=QueryAnalysis,
        model_settings=ModelSettings(
            temperature=temperature,
            max_tokens=max_tokens,
        ),
    )

    logger.info("QueryAnalyzerAgent created successfully")
    return agent


# ---------------------------------------------------------------------------
# Enhanced Analyzer Class (Optional advanced usage)
# ---------------------------------------------------------------------------
class EnhancedQueryAnalyzer:
    """
    Advanced query analyzer with caching, validation, and customization.

    Use this class when you need:
    - Query history/caching
    - Custom classification rules
    - Pre/post-processing hooks
    - Batch analysis

    Example:
        >>> analyzer = EnhancedQueryAnalyzer(api_key)
        >>> analysis = await analyzer.analyze("AI trends in healthcare")
        >>> print(analysis.query_type)
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        cache_enabled: bool = True,
    ):
        """
        Initialize the Enhanced Query Analyzer.

        Args:
            api_key: OpenAI API key.
            model: Model to use for classification.
            cache_enabled: Whether to cache recent analyses.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, QueryAnalysis] = {}
        self._agent = create_query_analyzer_agent(api_key, model)

        logger.info(f"EnhancedQueryAnalyzer initialized (cache={cache_enabled})")

    async def analyze(
        self,
        query: str,
        context: Optional[str] = None,
        force_refresh: bool = False,
    ) -> QueryAnalysis:
        """
        Analyze a research query and return structured classification.

        Args:
            query: The user's research question.
            context: Optional additional context.
            force_refresh: Bypass cache if True.

        Returns:
            QueryAnalysis with full classification metadata.
        """
        from agents import Runner

        # Check cache
        cache_key = f"{query}:{context or ''}"
        if self.cache_enabled and not force_refresh and cache_key in self._cache:
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return self._cache[cache_key]

        # Build input
        input_text = f"Query: {query}"
        if context:
            input_text += f"\nAdditional Context: {context}"

        logger.info(f"Analyzing query: {query[:100]}...")

        # Run analysis
        result = await Runner.run(self._agent, input_text)
        analysis: QueryAnalysis = result.final_output

        # Cache result
        if self.cache_enabled:
            self._cache[cache_key] = analysis
            # Limit cache size
            if len(self._cache) > 100:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

        logger.info(
            f"Analysis complete: type={analysis.query_type}, "
            f"complexity={analysis.complexity}, "
            f"searches={analysis.recommended_search_count}"
        )

        return analysis

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
        logger.info("Query analysis cache cleared")

    def apply_overrides(
        self,
        analysis: QueryAnalysis,
        overrides: Dict[str, Any],
    ) -> QueryAnalysis:
        """
        Apply manual overrides to an analysis.

        Useful for user-specified preferences or domain-specific rules.

        Args:
            analysis: Original QueryAnalysis.
            overrides: Dictionary of field names to new values.

        Returns:
            New QueryAnalysis with overrides applied.
        """
        data = analysis.model_dump()
        data.update(overrides)
        updated = QueryAnalysis(**data)
        logger.debug(f"Applied overrides: {list(overrides.keys())}")
        return updated


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------
def estimate_search_count(analysis: QueryAnalysis) -> int:
    """
    Refine search count based on analysis attributes.

    This can be used to override the model's recommendation with
    domain-specific logic.

    Args:
        analysis: The query analysis.

    Returns:
        Refined search count.
    """
    base = analysis.recommended_search_count

    # Increase for complex queries
    if analysis.complexity == "complex":
        base = max(base, 7)
    elif analysis.complexity == "expert_level":
        base = max(base, 10)

    # Increase for comparative queries (need data on each entity)
    if analysis.query_type == "comparative":
        entity_count = len(analysis.primary_entities)
        base = max(base, entity_count * 2)

    # Cap at maximum
    return min(base, 15)


def get_recommended_report_length(analysis: QueryAnalysis) -> tuple[int, int]:
    """
    Get recommended word count range based on depth.

    Args:
        analysis: The query analysis.

    Returns:
        Tuple of (min_words, max_words).
    """
    depth_ranges = {
        "overview": (500, 1000),
        "detailed": (1500, 2500),
        "comprehensive": (3000, 5000),
        "exhaustive": (5000, 10000),
    }
    return depth_ranges.get(analysis.required_depth, (1500, 2500))
