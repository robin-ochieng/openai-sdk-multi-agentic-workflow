"""
Writer Agent
Synthesizes search results into comprehensive report
"""

from openai import OpenAI
from openai.lib._agents import Agent
from ..models import ReportData


# Instructions for the writer agent
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


def create_writer_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent:
    """
    Create the Writer Agent
    
    This agent synthesizes all search results into a comprehensive 5-10 page report
    (1000+ words) in markdown format.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini)
        
    Returns:
        Configured Agent instance with ReportData output type
        
    Example:
        >>> writer = create_writer_agent(api_key)
        >>> input_data = {
        ...     "query": "Latest AI frameworks",
        ...     "search_results": [...]
        ... }
        >>> result = Runner.run(writer, input_data)
        >>> print(result.final_output.markdown_report)
    """
    client = OpenAI(api_key=api_key)
    
    writer_agent = Agent(
        name="WriterAgent",
        instructions=INSTRUCTIONS,
        model=model,
        output_type=ReportData,
    )
    
    return writer_agent
