"""Utility helpers for reshaping LLM-written research reports.

This module post-processes raw markdown returned by the writer agent so that the
frontend always receives a consistent, professional structure.  It creates the
requested hierarchy, applies bullet formatting, and highlights key terminology
without needing to re-prompt the model or rely on fragile prompt engineering.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple


# Order of sections expected in the final report output.
SECTION_ORDER: Sequence[str] = (
	"Introduction",
	"Technological Advancements",
	"Key Industry Developments",
	"Future Directions",
	"Applications Across Industries",
)

# Sections that should default to bullet formatting when entries are detected.
BULLET_SECTIONS = {
	"Key Industry Developments",
	"Future Directions",
	"Applications Across Industries",
}

# Terms to emphasize inline if the model does not already highlight them.
KEY_TERMS = (
	"Multi-agent systems",
	"Multi-agent Systems",
	"Real-time Adaptation",
	"Cybersecurity",
	"Enterprise Automation",
	"Finance & Trading",
	"Salesforce Agentforce 360",
	"Anthropic Claude Skills",
	"Microsoft's Copilot Actions",
)


def _clean_lines(raw_markdown: str) -> List[str]:
	"""Convert raw markdown into a list of stripped, non-empty lines."""

	return [line.strip() for line in raw_markdown.replace("\r", "").split("\n") if line.strip()]


def _normalize_section_lookup() -> Dict[str, str]:
	"""Return a case-insensitive lookup for known section headings."""

	return {title.lower(): title for title in SECTION_ORDER}


def _segment_sections(lines: List[str]) -> Tuple[Optional[str], Dict[str, List[str]]]:
	"""Split lines into the predefined section buckets.

	Returns the optional headline (first line before a known section) together
	with a mapping of section title to its collected content lines.
	"""

	lookup = _normalize_section_lookup()
	sections: Dict[str, List[str]] = {title: [] for title in SECTION_ORDER}
	headline: Optional[str] = None
	current_section: Optional[str] = None

	for raw_line in lines:
		section_title = lookup.get(raw_line.lower())
		if section_title:
			current_section = section_title
			continue

		if headline is None:
			# Treat the very first non-heading line as the report headline.
			headline = raw_line
			continue

		target_section = current_section or "Introduction"
		sections.setdefault(target_section, []).append(raw_line)

	return headline, sections


def _emphasize_terms(text: str) -> str:
	"""Ensure important terms appear in bold once."""

	for term in KEY_TERMS:
		bold_term = f"**{term}**"
		if term in text and bold_term not in text:
			text = text.replace(term, bold_term)
	return text


def _combine_paragraphs(lines: Sequence[str]) -> str:
	"""Create markdown paragraphs by joining non-empty lines."""

	if not lines:
		return ""

	paragraphs = [
		_emphasize_terms(sentence.strip())
		for sentence in lines
		if sentence.strip()
	]
	return "\n\n".join(paragraphs)


def _parse_bullet_entries(lines: Sequence[str]) -> List[Tuple[str, str]]:
	"""Convert colon-delimited lines into (title, description) pairs."""

	entries: List[Tuple[str, str]] = []
	current_title: Optional[str] = None
	buffer: List[str] = []

	for raw in lines:
		line = raw.strip()
		if not line:
			continue

		if ":" in line:
			if current_title is not None:
				entries.append((current_title, " ".join(buffer).strip()))
				buffer.clear()

			current_title, remainder = line.split(":", 1)
			current_title = current_title.strip()
			remainder = remainder.strip()
			if remainder:
				buffer.append(remainder)
		else:
			buffer.append(line)

	if current_title is not None:
		entries.append((current_title, " ".join(buffer).strip()))
	elif buffer:
		entries.append(("", " ".join(buffer).strip()))

	return entries


def _format_bullets(lines: Sequence[str]) -> str:
	"""Return a bullet list from the provided lines."""

	entries = _parse_bullet_entries(lines)
	if not entries:
		return _combine_paragraphs(lines)

	bullets: List[str] = []
	for title, description in entries:
		clean_description = _emphasize_terms(description)
		if title:
			emphasized_title = _emphasize_terms(title)
			# Ensure title itself stays bold even if emphasis already applied.
			if not emphasized_title.startswith("**"):
				emphasized_title = f"**{emphasized_title}**"
			bullet = f"- {emphasized_title} – {clean_description}"
		else:
			bullet = f"- {clean_description}"
		bullets.append(bullet)

	return "\n".join(bullets)


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

	lines = _clean_lines(raw_markdown)
	_, sections = _segment_sections(lines)

	executive_summary = _emphasize_terms(short_summary.strip())

	rendered_sections: List[str] = ["## Executive Summary", executive_summary]

	for section in SECTION_ORDER:
		content_lines = sections.get(section, [])
		if not content_lines:
			continue

		if section in BULLET_SECTIONS:
			body = _format_bullets(content_lines)
		else:
			body = _combine_paragraphs(content_lines)

		if not body:
			continue

		rendered_sections.append(f"## {section}")
		rendered_sections.append(body)

	conclusion_lines = [
		"Between 2023 and 2025, **agentic AI** progressed from targeted pilots to ",
		"enterprise-grade deployments that rely on resilient **multi-agent systems**.",
		" Organizations that invest in governance, integration, and talent are best positioned to harness",
		" sustained value from these advances."
	]
	conclusion_text = _emphasize_terms("".join(conclusion_lines).strip())

	rendered_sections.append("## Conclusion")
	rendered_sections.append(conclusion_text)

	return "\n\n".join(rendered_sections).strip() + "\n"

