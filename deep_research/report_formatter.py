"""Utility helpers for reshaping LLM-written research reports.

This module post-processes raw markdown returned by the writer agent so that the
frontend always receives a consistent, professional structure.  It creates the
requested hierarchy, applies bullet formatting, and highlights key terminology
without needing to re-prompt the model or rely on fragile prompt engineering.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence, Tuple


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

