"""
Planner Agent
Analyzes research query and creates strategic search plan
"""

from openai import OpenAI
from openai.lib._agents import Agent
from ..models import WebSearchPlan


# Number of searches to plan (3-5)
HOW_MANY_SEARCHES = 5

# Instructions for the planner agent
INSTRUCTIONS = (
    "You are a helpful research assistant. Given a query, come up with a set of web searches "
    "to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."
)


def create_planner_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent:
    """
    Create the Planner Agent
    
    This agent analyzes the user's research query and creates a strategic plan
    with 5 targeted search terms to perform.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini)
        
    Returns:
        Configured Agent instance
        
    Example:
        >>> planner = create_planner_agent(api_key)
        >>> result = Runner.run(planner, {"query": "Latest AI frameworks"})
        >>> print(result.final_output.searches)
    """
    client = OpenAI(api_key=api_key)
    
    planner_agent = Agent(
        name="PlannerAgent",
        instructions=INSTRUCTIONS,
        model=model,
        output_type=WebSearchPlan,
    )
    
    return planner_agent
