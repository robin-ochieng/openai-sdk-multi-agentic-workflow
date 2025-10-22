"""
Writer Agent
Synthesizes search results into comprehensive report
"""

from openai import OpenAI
from agents import Agent
from deep_research.models import ReportData


# Instructions for the writer agent
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n\n"
    "IMPORTANT STRUCTURE GUIDELINES:\n"
    "1. Start with an 'Executive Summary' section that provides a brief overview\n"
    "2. Follow with a 'Table of Contents' that lists all major sections\n"
    "3. Then include an 'Introduction' section (ONLY ONCE - do not repeat this heading)\n"
    "4. Continue with the main body sections covering the research topic\n"
    "5. End with a 'Conclusion' section\n\n"
    "FORMATTING RULES:\n"
    "- Use ## for main section headings (Executive Summary, Introduction, Conclusion, etc.)\n"
    "- Use ### for subsections\n"
    "- Do NOT duplicate section headings\n"
    "- Ensure the Table of Contents accurately reflects the actual sections\n\n"
    "The final output should be in markdown format, lengthy and detailed. Aim for 5-10 pages "
    "of content, at least 1000 words."
)


def create_writer_agent(api_key: str, model: str = "gpt-4o") -> Agent:
    """
    Create the Writer Agent
    
    This agent synthesizes all search results into a comprehensive 10-15 page report
    (1500+ words) in markdown format.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o)
        
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
