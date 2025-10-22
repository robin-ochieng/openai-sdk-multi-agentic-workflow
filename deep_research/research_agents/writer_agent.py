"""
Writer Agent
Synthesizes search results into comprehensive report
"""

from typing import Optional, Dict, Any, List
from openai import OpenAI
from agents import Agent, ModelSettings
from deep_research.models import ReportData
import logging
import re

logger = logging.getLogger(__name__)

# Enhanced instructions for the writer agent
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive, professional report for a research query. "
    "You will be provided with the original query, and research data from multiple sources.\n\n"
    
    "IMPORTANT STRUCTURE GUIDELINES:\n"
    "1. Start with an 'Executive Summary' section (200-300 words) that provides key findings and recommendations\n"
    "2. Follow with a 'Table of Contents' that lists all major sections with subsections\n"
    "3. Include an 'Introduction' section that contextualizes the research question\n"
    "4. Create logical main body sections that thoroughly explore the topic:\n"
    "   - Current State Analysis\n"
    "   - Key Findings and Insights\n"
    "   - Comparative Analysis (if applicable)\n"
    "   - Challenges and Opportunities\n"
    "   - Future Outlook/Trends\n"
    "5. Add a 'Recommendations' section with actionable insights\n"
    "6. End with a 'Conclusion' section summarizing key takeaways\n"
    "7. Include a 'References' section with all cited sources\n\n"
    
    "FORMATTING RULES:\n"
    "- Use ## for main section headings\n"
    "- Use ### for subsections\n"
    "- Use #### for sub-subsections if needed\n"
    "- Include bullet points and numbered lists for clarity\n"
    "- Add tables for comparative data using markdown table syntax\n"
    "- Use **bold** for key terms and *italics* for emphasis\n"
    "- Include relevant quotes in blockquotes using >\n"
    "- Do NOT duplicate section headings\n\n"
    
    "CONTENT REQUIREMENTS:\n"
    "- Synthesize information from multiple sources\n"
    "- Cite sources inline using [Source: name] format\n"
    "- Identify and highlight conflicting information\n"
    "- Provide balanced analysis of different perspectives\n"
    "- Include specific examples and case studies\n"
    "- Add data points, statistics, and metrics where available\n\n"
    
    "The final output should be in markdown format, comprehensive and detailed. "
    "Target length: 2000-3000 words minimum, organized into clear sections."
)

# Template for specific report types
REPORT_TEMPLATES = {
    "technical": (
        "Focus on technical specifications, implementation details, architecture, "
        "performance metrics, and code examples where relevant."
    ),
    "business": (
        "Focus on market analysis, ROI, competitive landscape, business implications, "
        "and strategic recommendations."
    ),
    "academic": (
        "Focus on literature review, methodology, theoretical frameworks, "
        "empirical evidence, and scholarly citations."
    ),
    "general": (
        "Provide a balanced overview suitable for a general audience, "
        "avoiding excessive jargon while maintaining accuracy."
    )
}


def enhance_instructions(base_instructions: str, report_type: str = "general", 
                        custom_requirements: Optional[str] = None) -> str:
    """
    Enhance instructions based on report type and custom requirements
    
    Args:
        base_instructions: Base instruction template
        report_type: Type of report (technical, business, academic, general)
        custom_requirements: Additional custom requirements
        
    Returns:
        Enhanced instruction string
    """
    enhanced = base_instructions
    
    # Add report type specific instructions
    if report_type in REPORT_TEMPLATES:
        enhanced += f"\n\nREPORT TYPE FOCUS:\n{REPORT_TEMPLATES[report_type]}\n"
    
    # Add custom requirements if provided
    if custom_requirements:
        enhanced += f"\n\nCUSTOM REQUIREMENTS:\n{custom_requirements}\n"
    
    return enhanced


def validate_search_results(search_results: Any) -> bool:
    """
    Validate that search results contain sufficient data for report generation
    
    Args:
        search_results: Search results to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not search_results:
        logger.warning("No search results provided")
        return False
    
    # Check if results have minimum content
    if isinstance(search_results, list):
        if len(search_results) < 2:
            logger.warning("Insufficient search results for comprehensive report")
            return False
    elif isinstance(search_results, str):
        if len(search_results) < 100:
            logger.warning("Search results too brief for comprehensive report")
            return False
    
    return True


def create_writer_agent(
    api_key: str, 
    model: str = "gpt-4o",
    report_type: str = "general",
    custom_requirements: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = 4000
) -> Agent:
    """
    Create an enhanced Writer Agent
    
    This agent synthesizes all search results into a comprehensive report
    (2000+ words) in markdown format with improved structure and citations.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o)
        report_type: Type of report - technical, business, academic, or general
        custom_requirements: Additional custom requirements for the report
        temperature: Creativity level (0.0-1.0, default: 0.7)
        max_tokens: Maximum tokens for response (default: 4000)
        
    Returns:
        Configured Agent instance with ReportData output type
        
    Example:
        >>> writer = create_writer_agent(
        ...     api_key,
        ...     report_type="technical",
        ...     custom_requirements="Include code examples and benchmarks"
        ... )
        >>> input_data = {
        ...     "query": "Latest AI frameworks",
        ...     "search_results": [...]
        ... }
        >>> result = Runner.run(writer, input_data)
        >>> print(result.final_output.markdown_report)
    """
    client = OpenAI(api_key=api_key)
    
    # Enhance instructions based on report type
    enhanced_instructions = enhance_instructions(
        INSTRUCTIONS, 
        report_type, 
        custom_requirements
    )
    
    writer_agent = Agent(
        name="EnhancedWriterAgent",
        instructions=enhanced_instructions,
        model=model,
        output_type=ReportData,
        model_settings=ModelSettings(
            temperature=temperature,
            max_tokens=max_tokens
        )
    )
    
    logger.info(f"Created Enhanced Writer Agent with {report_type} report type")
    
    return writer_agent


def post_process_report(markdown_report: str) -> str:
    """
    Post-process the generated report to ensure quality
    
    Args:
        markdown_report: Raw markdown report
        
    Returns:
        Cleaned and formatted markdown report
    """
    # Remove duplicate headings
    lines = markdown_report.split('\n')
    seen_headings = set()
    cleaned_lines = []
    
    for line in lines:
        if line.startswith('#'):
            heading = line.strip()
            if heading not in seen_headings:
                seen_headings.add(heading)
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    # Ensure proper spacing between sections
    report = '\n'.join(cleaned_lines)
    report = re.sub(r'\n{3,}', '\n\n', report)
    
    # Add word count at the end
    word_count = len(report.split())
    report += f"\n\n---\n*Word count: {word_count}*"
    
    return report
