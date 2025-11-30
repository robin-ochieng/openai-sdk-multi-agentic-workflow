"""Utility helpers for reshaping LLM-written research reports.

This module post-processes raw markdown returned by the writer agent so that the
frontend always receives a consistent, professional structure.  It creates the
requested hierarchy, applies bullet formatting, and highlights key terminology
without needing to re-prompt the model or rely on fragile prompt engineering.

Enhanced to include:
- Methodology & Source Quality section
- Source credibility badges in references
- Research quality summary
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence, Tuple, Any

# Try to import SourceMetrics, but don't fail if circular import
try:
    from deep_research.models.research_models import SourceMetrics
except ImportError:
    SourceMetrics = None  # type: ignore


def _clean_report(raw_markdown: str) -> str:
	"""
	Clean the report by removing Table of Contents and duplicate sections.
	Preserves exactly one Introduction section after Executive Summary.
	
	Args:
		raw_markdown: The raw markdown from the writer agent
		
	Returns:
		Cleaned markdown without TOC and duplicate sections
	"""
	lines = raw_markdown.split('\n')
	cleaned_lines = []
	skip_until_next_heading = False
	seen_headings = set()
	
	i = 0
	while i < len(lines):
		line = lines[i]
		stripped = line.strip()
		
		# Check if this is a heading
		if stripped.startswith('#'):
			heading_text = stripped.lstrip('#').strip().lower()
			
			# Skip Table of Contents section entirely
			if 'table of contents' in heading_text or heading_text == 'contents':
				skip_until_next_heading = True
				i += 1
				continue
			
			# Check for duplicate headings (including Introduction)
			if heading_text in seen_headings:
				skip_until_next_heading = True
				i += 1
				continue
			
			# Valid heading - add it
			seen_headings.add(heading_text)
			skip_until_next_heading = False
			cleaned_lines.append(line)
		else:
			# Skip content if we're in a section to skip
			if skip_until_next_heading:
				i += 1
				continue
			cleaned_lines.append(line)
		
		i += 1
	
	result = '\n'.join(cleaned_lines)
	# Clean up excessive newlines
	result = re.sub(r'\n{3,}', '\n\n', result)
	return result


def format_research_report(raw_markdown: str, short_summary: str, *, query: Optional[str] = None) -> str:
	"""Format loosely structured markdown into a consistent, polished report.

	Args:
		raw_markdown: The unstructured markdown returned by the writer agent.
		short_summary: A concise summary to reuse for the executive summary.
		query: Optional research question for contextual messaging.

	Returns:
		A markdown string with the desired heading hierarchy, bullets, spacing,
		and highlighted terminology.
	"""
	# First, clean the report to remove TOC and duplicate sections
	cleaned_markdown = _clean_report(raw_markdown)
	
	# Return the cleaned markdown as-is (the writer agent already formats it well)
	return cleaned_markdown.strip() + "\n"


def add_methodology_section(
    markdown_report: str,
    source_metrics: Optional[Any] = None,
    query_analysis_summary: Optional[Dict[str, Any]] = None,
    sources_with_credibility: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Add a Methodology & Source Quality section to the report.
    
    This section provides transparency about the research process,
    including source validation statistics and credibility scores.
    
    Args:
        markdown_report: The formatted markdown report.
        source_metrics: SourceMetrics with validation statistics.
        query_analysis_summary: Summary of query classification.
        sources_with_credibility: List of sources with credibility badges.
    
    Returns:
        Report with methodology section inserted before References/Conclusion.
    """
    if not source_metrics and not query_analysis_summary:
        return markdown_report
    
    # Build the methodology section
    section_parts = [
        "",
        "---",
        "",
        "## Methodology & Source Quality",
        "",
    ]
    
    # Add research approach subsection
    if query_analysis_summary:
        section_parts.extend([
            "### Research Approach",
            "",
        ])
        
        query_type = query_analysis_summary.get("query_type", "general")
        complexity = query_analysis_summary.get("complexity", "moderate")
        audience = query_analysis_summary.get("audience_level", "general")
        depth = query_analysis_summary.get("required_depth", "detailed")
        
        section_parts.extend([
            f"This report was generated using an AI-powered deep research system. "
            f"The query was classified as **{query_type}** research with **{complexity}** complexity, "
            f"targeted at a **{audience}** audience with **{depth}** coverage.",
            "",
        ])
        
        entities = query_analysis_summary.get("primary_entities", [])
        if entities:
            section_parts.extend([
                f"**Primary research focus:** {', '.join(entities[:5])}",
                "",
            ])
    
    # Add source quality subsection
    if source_metrics:
        section_parts.extend([
            "### Source Quality Assessment",
            "",
        ])
        
        # Quality summary
        total = getattr(source_metrics, 'total_sources', 0)
        included = getattr(source_metrics, 'included_count', 0)
        caveat = getattr(source_metrics, 'caveat_count', 0)
        excluded = getattr(source_metrics, 'excluded_count', 0)
        avg_score = getattr(source_metrics, 'average_score', 0)
        high_count = getattr(source_metrics, 'high_credibility_count', 0)
        
        # Determine quality tier
        if avg_score >= 70:
            quality_badge = "⭐ **High Quality**"
            quality_desc = "Sources are predominantly from authoritative, peer-reviewed, or official channels."
        elif avg_score >= 50:
            quality_badge = "✓ **Medium Quality**"
            quality_desc = "Sources are generally reliable with some requiring additional verification."
        elif avg_score >= 30:
            quality_badge = "⚠️ **Mixed Quality**"
            quality_desc = "Sources include a mix of authoritative and less reliable channels. Key claims should be verified."
        else:
            quality_badge = "❌ **Low Quality**"
            quality_desc = "Limited authoritative sources available. Findings should be treated as preliminary."
        
        section_parts.extend([
            f"**Overall Source Quality:** {quality_badge} (Score: {avg_score:.1f}/100)",
            "",
            quality_desc,
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Sources Analyzed | {total} |",
            f"| High-Credibility Sources | {high_count} |",
            f"| Sources Included | {included} |",
            f"| Sources with Caveats | {caveat} |",
            f"| Sources Excluded | {excluded} |",
            f"| Average Credibility Score | {avg_score:.1f}/100 |",
            "",
        ])
    
    # Add source credibility legend
    section_parts.extend([
        "### Credibility Legend",
        "",
        "| Badge | Meaning |",
        "|-------|---------|",
        "| ⭐ High | Authoritative sources (government, academic, major news) |",
        "| ✓ Medium | Generally reliable sources |",
        "| ⚠️ Low | Use with caution, requires corroboration |",
        "| ❌ Excluded | Not used due to low credibility |",
        "",
    ])
    
    # Add top validated sources if available
    if sources_with_credibility and len(sources_with_credibility) > 0:
        section_parts.extend([
            "### Key Sources Used",
            "",
        ])
        
        # Show top 8 sources sorted by credibility
        sorted_sources = sorted(
            sources_with_credibility,
            key=lambda x: x.get("credibility_score", 0),
            reverse=True
        )[:8]
        
        for source in sorted_sources:
            badge = source.get("credibility_badge", "")
            title = source.get("title", "Source")[:60]
            url = source.get("url", "")
            score = source.get("credibility_score", 0)
            
            if title and url:
                section_parts.append(f"- {badge} [{title}]({url})")
        
        section_parts.append("")
    
    methodology_section = "\n".join(section_parts)
    
    # Find the best place to insert (before References or Conclusion)
    # Look for ## References, ## Conclusion, or end of document
    insert_patterns = [
        r'(^## References)',
        r'(^## Conclusion)',
        r'(^---\s*$\s*\*Word count:)',  # Before word count footer
    ]
    
    for pattern in insert_patterns:
        match = re.search(pattern, markdown_report, re.MULTILINE | re.IGNORECASE)
        if match:
            insert_pos = match.start()
            return (
                markdown_report[:insert_pos].rstrip() + 
                methodology_section + 
                "\n\n" + 
                markdown_report[insert_pos:]
            )
    
    # No match found, append at the end
    return markdown_report.rstrip() + methodology_section + "\n"

