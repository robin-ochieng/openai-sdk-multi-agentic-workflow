"""
Search Agent
Performs web searches and summarizes results
"""

from openai import OpenAI
from agents import Agent, WebSearchTool, ModelSettings


# Instructions for the search agent
INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)


def create_search_agent(api_key: str, model: str = "gpt-4o") -> Agent:
    """
    Create the Search Agent
    
    This agent performs web searches using OpenAI's WebSearchTool and produces
    concise summaries of the results (2-3 paragraphs, <300 words).
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o)
        
    Returns:
        Configured Agent instance with WebSearchTool
        
    Example:
        >>> search_agent = create_search_agent(api_key)
        >>> result = Runner.run(search_agent, {"query": "OpenAI agents"})
        >>> print(result.final_output)
    """
    client = OpenAI(api_key=api_key)
    
    search_agent = Agent(
        name="SearchAgent",
        instructions=INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size="low")],
        model=model,
        model_settings=ModelSettings(tool_choice="required"),
    )
    
    return search_agent
