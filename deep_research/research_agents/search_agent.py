"""
Search Agent
Performs web searches and summarizes results with enhanced capabilities
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from openai import OpenAI
from agents import Agent, WebSearchTool, ModelSettings

# Configure logging
logger = logging.getLogger(__name__)

# Enhanced instructions with more specific guidance
INSTRUCTIONS = """
You are an expert research assistant specializing in web search and information synthesis.

Your task is to:
1. Search the web for the given query using the most relevant search terms
2. Analyze and extract key information from multiple sources
3. Identify credible and authoritative sources
4. Cross-reference facts when possible
5. Note any contradictions or varying perspectives

Output Requirements:
- Produce a concise summary (3-5 paragraphs, max 300 words)
- Focus on factual, objective information
- Prioritize recent and authoritative sources
- Include key statistics, dates, or figures when relevant
- Organize information logically (most important first)
- Use bullet points for lists when appropriate
- Note source credibility when questionable

Format: Write succinctly without unnecessary commentary. This summary will be used for further analysis.
"""

# Specialized instructions for different search types
SEARCH_TEMPLATES = {
    "technical": "Focus on technical specifications, implementation details, and expert opinions.",
    "news": "Prioritize recent developments, official statements, and verified facts.",
    "academic": "Emphasize peer-reviewed sources, research findings, and scholarly consensus.",
    "market": "Include market data, trends, competitive analysis, and financial metrics.",
}


def create_search_agent(
    api_key: str,
    model: str = "gpt-4o",
    search_type: Optional[str] = None,
    max_results: int = 10,
    temperature: float = 0.3,
    enable_caching: bool = True
) -> Agent:
    """
    Create an enhanced Search Agent with configurable parameters
    
    This agent performs intelligent web searches using OpenAI's WebSearchTool and produces
    structured, concise summaries optimized for downstream processing.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o)
        search_type: Type of search focus ('technical', 'news', 'academic', 'market')
        max_results: Maximum number of search results to process
        temperature: Model temperature for response generation (0.0-1.0)
        enable_caching: Whether to enable response caching
        
    Returns:
        Configured Agent instance with enhanced WebSearchTool
        
    Example:
        >>> search_agent = create_search_agent(
        ...     api_key, 
        ...     search_type="technical",
        ...     temperature=0.2
        ... )
        >>> result = Runner.run(search_agent, {"query": "LLM optimization techniques"})
        >>> print(result.final_output)
    """
    client = OpenAI(api_key=api_key)
    
    # Customize instructions based on search type
    instructions = INSTRUCTIONS
    if search_type and search_type in SEARCH_TEMPLATES:
        instructions = f"{INSTRUCTIONS}\n\nAdditional Focus: {SEARCH_TEMPLATES[search_type]}"
        logger.info(f"Using specialized instructions for {search_type} search")
    
    # Configure search tool (WebSearchTool only accepts search_context_size)
    # Use "high" for more comprehensive searches, "low" for faster results
    context_size = "high" if max_results > 5 else "low"
    search_tool = WebSearchTool(search_context_size=context_size)
    
    # Create agent with enhanced settings
    search_agent = Agent(
        name="EnhancedSearchAgent",
        instructions=instructions,
        tools=[search_tool],
        model=model,
        model_settings=ModelSettings(
            tool_choice="required",
            temperature=temperature,
            max_tokens=500,  # Ensure concise responses
            response_format={"type": "text"}
        )
    )
    
    logger.info(f"Created enhanced search agent with model: {model}")
    return search_agent


def create_multi_search_agent(
    api_key: str,
    model: str = "gpt-4o",
    parallel_searches: int = 3
) -> Agent:
    """
    Create a multi-search agent that performs parallel searches with different strategies
    
    Args:
        api_key: OpenAI API key
        model: Model to use
        parallel_searches: Number of parallel search strategies to use
        
    Returns:
        Agent configured for comprehensive multi-angle searching
    """
    client = OpenAI(api_key=api_key)
    
    multi_instructions = f"""
    {INSTRUCTIONS}
    
    Additional Guidelines:
    - Perform {parallel_searches} searches with varied search terms
    - Use synonyms and related concepts to broaden search coverage
    - Combine results from multiple searches into a unified summary
    - Highlight consensus findings and note discrepancies
    """
    
    search_agent = Agent(
        name="MultiSearchAgent",
        instructions=multi_instructions,
        tools=[WebSearchTool(search_context_size="high")],
        model=model,
        model_settings=ModelSettings(
            tool_choice="required",
            temperature=0.4,
            max_tokens=600
        )
    )
    
    return search_agent


def validate_search_results(results: Dict[str, Any]) -> bool:
    """
    Validate search results for quality and completeness
    
    Args:
        results: Search results dictionary
        
    Returns:
        Boolean indicating if results meet quality standards
    """
    if not results or "final_output" not in results:
        return False
    
    output = results.get("final_output", "")
    word_count = len(output.split())
    
    # Check word count constraints
    if word_count < 50 or word_count > 350:
        logger.warning(f"Output word count ({word_count}) outside optimal range")
        return False
        
    return True
