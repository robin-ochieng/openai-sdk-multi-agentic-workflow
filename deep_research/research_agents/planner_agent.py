"""
Planner Agent
Analyzes research query and creates strategic search plan with enhanced capabilities
"""

from typing import Optional, Dict, Any, List
from openai import OpenAI
from agents import Agent, ModelSettings
from deep_research.models import WebSearchPlan
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_SEARCH_COUNT = 5
MIN_SEARCHES = 3
MAX_SEARCHES = 10
DEFAULT_MODEL = "gpt-4o"

# Enhanced instructions for the planner agent
INSTRUCTIONS = """
You are an expert research strategist. Your task is to analyze a research query and create a comprehensive search strategy.

For each query, you must:
1. Identify key concepts and entities to research
2. Generate diverse search terms that cover different aspects:
    - Direct searches for the main topic
    - Related concepts and background information
    - Recent developments and updates
    - Comparative or alternative perspectives
    - Specific data, statistics, or case studies

Guidelines:
- Create {search_count} distinct search queries
- Ensure queries are specific and likely to yield high-quality results
- Include temporal qualifiers (e.g., "2024", "latest") when relevant
- Mix broad overview searches with specific deep-dive queries
- Avoid redundant or overlapping search terms
- Prioritize authoritative sources by including relevant keywords

Output exactly {search_count} search terms optimized for web search engines.
"""

# Tool functions for query enhancement
def enhance_query_context(query: str, context: Optional[Dict[str, Any]] = None) -> str:
     """
     Enhance the query with additional context if provided
     
     Args:
          query: Original research query
          context: Optional context dictionary with domain, time_range, etc.
     
     Returns:
          Enhanced query string
     """
     if not context:
          return query
     
     enhanced = query
     if "domain" in context:
          enhanced = f"{enhanced} [Domain: {context['domain']}]"
     if "time_range" in context:
          enhanced = f"{enhanced} [Time: {context['time_range']}]"
     if "depth" in context:
          enhanced = f"{enhanced} [Depth: {context['depth']}]"
     
     return enhanced

def validate_search_count(count: int) -> int:
     """
     Validate and adjust search count within acceptable bounds
     
     Args:
          count: Requested number of searches
     
     Returns:
          Validated search count
     """
     if count < MIN_SEARCHES:
          logger.warning(f"Search count {count} below minimum, using {MIN_SEARCHES}")
          return MIN_SEARCHES
     elif count > MAX_SEARCHES:
          logger.warning(f"Search count {count} above maximum, using {MAX_SEARCHES}")
          return MAX_SEARCHES
     return count


class EnhancedPlannerAgent:
     """Enhanced Planner Agent with additional capabilities"""
     
     def __init__(
          self, 
          api_key: str, 
          model: str = DEFAULT_MODEL,
          search_count: int = DEFAULT_SEARCH_COUNT,
          temperature: float = 0.7,
          max_tokens: int = 1000
     ):
          """
          Initialize the Enhanced Planner Agent
          
          Args:
                api_key: OpenAI API key
                model: Model to use
                search_count: Number of searches to plan
                temperature: Model temperature for creativity
                max_tokens: Maximum tokens for response
          """
          self.client = OpenAI(api_key=api_key)
          self.model = model
          self.search_count = validate_search_count(search_count)
          self.temperature = temperature
          self.max_tokens = max_tokens
          
          # Create the base agent
          self.agent = self._create_agent()
     
     def _create_agent(self) -> Agent:
          """Create the underlying Agent instance"""
          instructions = INSTRUCTIONS.format(search_count=self.search_count)
          
          return Agent(
                name="EnhancedPlannerAgent",
                instructions=instructions,
                model=self.model,
                output_type=WebSearchPlan,
                model_settings=ModelSettings(
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
          )
     
     def plan(
          self, 
          query: str, 
          context: Optional[Dict[str, Any]] = None,
          refine: bool = True
     ) -> WebSearchPlan:
          """
          Create a search plan for the given query
          
          Args:
                query: Research query
                context: Optional context for query enhancement
                refine: Whether to refine search terms
          
          Returns:
                WebSearchPlan with optimized search terms
          """
          # Enhance query with context if provided
          enhanced_query = enhance_query_context(query, context)
          
          # Log the planning request
          logger.info(f"Creating search plan for: {query[:100]}...")
          
          # Generate the plan
          result = self.agent.run({"query": enhanced_query})
          
          # Optionally refine the search terms
          if refine and hasattr(result, 'searches'):
                result.searches = self._refine_searches(result.searches, query)
          
          logger.info(f"Generated {len(result.searches)} search terms")
          return result
     
     def _refine_searches(self, searches: List[str], original_query: str) -> List[str]:
          """
          Refine search terms for better results
          
          Args:
                searches: Initial search terms
                original_query: Original user query
          
          Returns:
                Refined list of search terms
          """
          refined = []
          for search in searches:
                # Remove redundant terms
                if search.lower() != original_query.lower():
                     # Add quotes for exact phrases if needed
                     if len(search.split()) > 3 and '"' not in search:
                          search = f'"{search}"'
                     refined.append(search)
          
          return refined[:self.search_count]
     
     def update_configuration(
          self,
          search_count: Optional[int] = None,
          temperature: Optional[float] = None,
          model: Optional[str] = None
     ):
          """
          Update agent configuration
          
          Args:
                search_count: New search count
                temperature: New temperature
                model: New model name
          """
          if search_count is not None:
                self.search_count = validate_search_count(search_count)
          if temperature is not None:
                self.temperature = temperature
          if model is not None:
                self.model = model
          
          # Recreate agent with new configuration
          self.agent = self._create_agent()
          logger.info("Agent configuration updated")


def create_planner_agent(
     api_key: str,
     model: str = DEFAULT_MODEL,
     search_count: int = DEFAULT_SEARCH_COUNT,
     enhanced: bool = False,
     **kwargs
) -> Agent:
     """
     Create a Planner Agent (basic or enhanced)
     
     This agent analyzes the user's research query and creates a strategic plan
     with targeted search terms to perform.
     
     Args:
          api_key: OpenAI API key
          model: Model to use (default: gpt-4o)
          search_count: Number of searches to plan (3-10)
          enhanced: Whether to use enhanced planner with additional features
          **kwargs: Additional configuration options
          
     Returns:
          Configured Agent instance or EnhancedPlannerAgent
          
     Example:
          >>> # Basic usage
          >>> planner = create_planner_agent(api_key)
          >>> result = planner.run({"query": "Latest AI frameworks"})
          >>> print(result.searches)
          
          >>> # Enhanced usage with context
          >>> planner = create_planner_agent(api_key, enhanced=True)
          >>> result = planner.plan(
          ...     "AI frameworks",
          ...     context={"domain": "computer vision", "time_range": "2024"}
          ... )
     """
     if enhanced:
          return EnhancedPlannerAgent(
                api_key=api_key,
                model=model,
                search_count=search_count,
                **kwargs
          )
     
     # Basic agent for backward compatibility
     search_count = validate_search_count(search_count)
     instructions = INSTRUCTIONS.format(search_count=search_count)
     
     return Agent(
          name="PlannerAgent",
          instructions=instructions,
          model=model,
          output_type=WebSearchPlan,
     )
