"""
Regression tests for Enhanced Writer Wiring (Phase 1 Prompt 3).

Tests ensure:
- ReportData new fields serialize correctly
- SourceMetrics calculates derived properties
- Report formatter adds methodology section
- Source credibility badges render in reports
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from deep_research.models.research_models import (
    ReportData,
    SourceMetrics,
    WebSearchItem,
    WebSearchPlan,
)
from deep_research.report_formatter import (
    format_research_report,
    add_methodology_section,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_source_metrics() -> SourceMetrics:
    """Create sample source metrics for testing."""
    return SourceMetrics(
        total_sources=20,
        included_count=12,
        caveat_count=5,
        excluded_count=3,
        average_score=68.5,
        high_credibility_count=8,
        category_distribution={
            "high": 8,
            "medium": 7,
            "low": 5,
        }
    )


@pytest.fixture
def sample_query_analysis_summary() -> Dict[str, Any]:
    """Create sample query analysis summary."""
    return {
        "query_type": "market_research",
        "complexity": "complex",
        "audience_level": "professional",
        "required_depth": "comprehensive",
        "time_sensitivity": "current",
        "primary_entities": ["AI agents", "enterprise adoption", "ROI metrics"],
        "recommended_search_count": 8,
        "estimated_research_time": 25,
    }


@pytest.fixture
def sample_sources_with_credibility() -> List[Dict[str, Any]]:
    """Create sample sources with credibility badges."""
    return [
        {
            "url": "https://arxiv.org/abs/2024.12345",
            "title": "AI Agent Architecture Survey",
            "credibility_score": 85,
            "credibility_badge": "⭐ High Credibility (85)",
            "credibility_level": "high",
        },
        {
            "url": "https://techcrunch.com/ai-enterprise",
            "title": "Enterprise AI Adoption Trends",
            "credibility_score": 65,
            "credibility_badge": "✓ Medium Credibility (65)",
            "credibility_level": "medium",
        },
        {
            "url": "https://medium.com/@user/ai-thoughts",
            "title": "My Thoughts on AI Agents",
            "credibility_score": 42,
            "credibility_badge": "⚠️ Low Credibility (42)",
            "credibility_level": "low",
            "caveats": ["User-generated content", "Requires corroboration"],
        },
    ]


@pytest.fixture
def sample_markdown_report() -> str:
    """Create sample markdown report."""
    return """# Research Report: AI Agents in Enterprise

## Executive Summary

AI agents are transforming enterprise operations...

## Introduction

This report examines the adoption of AI agents...

## Key Findings

1. Market growth of 45% annually
2. Enterprise adoption increasing

## Recommendations

- Start with pilot programs
- Focus on measurable ROI

## Conclusion

AI agents represent a significant opportunity...

## References

1. Source A
2. Source B

---
*Word count: 150*
"""


# ============================================================================
# SourceMetrics Tests
# ============================================================================

class TestSourceMetrics:
    """Tests for SourceMetrics model."""
    
    def test_default_values(self):
        """Default SourceMetrics should have zero values."""
        metrics = SourceMetrics()
        assert metrics.total_sources == 0
        assert metrics.included_count == 0
        assert metrics.average_score == 0.0
    
    def test_inclusion_rate_calculation(self, sample_source_metrics):
        """Inclusion rate should be calculated correctly."""
        # (12 + 5) / 20 * 100 = 85%
        assert sample_source_metrics.inclusion_rate == 85.0
    
    def test_inclusion_rate_zero_sources(self):
        """Inclusion rate should handle zero sources."""
        metrics = SourceMetrics(total_sources=0)
        assert metrics.inclusion_rate == 0.0
    
    def test_quality_tier_high(self):
        """High average score should return 'high' tier."""
        metrics = SourceMetrics(average_score=75.0)
        assert metrics.quality_tier == "high"
    
    def test_quality_tier_medium(self):
        """Medium average score should return 'medium' tier."""
        metrics = SourceMetrics(average_score=55.0)
        assert metrics.quality_tier == "medium"
    
    def test_quality_tier_low(self):
        """Low average score should return 'low' tier."""
        metrics = SourceMetrics(average_score=35.0)
        assert metrics.quality_tier == "low"
    
    def test_quality_tier_poor(self):
        """Very low average score should return 'poor' tier."""
        metrics = SourceMetrics(average_score=20.0)
        assert metrics.quality_tier == "poor"
    
    def test_serialization(self, sample_source_metrics):
        """SourceMetrics should serialize to dict correctly."""
        data = sample_source_metrics.model_dump()
        
        assert data["total_sources"] == 20
        assert data["included_count"] == 12
        assert data["average_score"] == 68.5
        assert "high" in data["category_distribution"]
    
    def test_json_serialization(self, sample_source_metrics):
        """SourceMetrics should serialize to JSON correctly."""
        json_str = sample_source_metrics.model_dump_json()
        
        assert "total_sources" in json_str
        assert "68.5" in json_str


# ============================================================================
# ReportData Tests
# ============================================================================

class TestReportData:
    """Tests for enhanced ReportData model."""
    
    def test_basic_fields(self):
        """Basic ReportData fields should work as before."""
        report = ReportData(
            short_summary="Test summary",
            markdown_report="# Test Report",
            follow_up_questions=["Question 1"],
        )
        
        assert report.short_summary == "Test summary"
        assert report.markdown_report == "# Test Report"
        assert len(report.follow_up_questions) == 1
    
    def test_new_optional_fields_default_none(self):
        """New fields should default to None/empty."""
        report = ReportData(
            short_summary="Test",
            markdown_report="# Report",
        )
        
        assert report.query_analysis_summary is None
        assert report.source_metrics is None
        assert report.planning_notes is None
        assert report.sources_with_credibility == []
    
    def test_with_source_metrics(self, sample_source_metrics):
        """ReportData should accept SourceMetrics."""
        report = ReportData(
            short_summary="Test",
            markdown_report="# Report",
            source_metrics=sample_source_metrics,
        )
        
        assert report.source_metrics is not None
        assert report.source_metrics.total_sources == 20
        assert report.source_metrics.average_score == 68.5
    
    def test_with_query_analysis_summary(self, sample_query_analysis_summary):
        """ReportData should accept query analysis summary."""
        report = ReportData(
            short_summary="Test",
            markdown_report="# Report",
            query_analysis_summary=sample_query_analysis_summary,
        )
        
        assert report.query_analysis_summary is not None
        assert report.query_analysis_summary["query_type"] == "market_research"
    
    def test_with_planning_notes(self):
        """ReportData should accept planning notes."""
        report = ReportData(
            short_summary="Test",
            markdown_report="# Report",
            planning_notes="Query classified as market_research with complex complexity.",
        )
        
        assert report.planning_notes is not None
        assert "market_research" in report.planning_notes
    
    def test_with_sources_with_credibility(self, sample_sources_with_credibility):
        """ReportData should accept sources with credibility."""
        report = ReportData(
            short_summary="Test",
            markdown_report="# Report",
            sources_with_credibility=sample_sources_with_credibility,
        )
        
        assert len(report.sources_with_credibility) == 3
        assert report.sources_with_credibility[0]["credibility_score"] == 85
    
    def test_full_serialization(
        self,
        sample_source_metrics,
        sample_query_analysis_summary,
        sample_sources_with_credibility
    ):
        """Full ReportData should serialize correctly."""
        report = ReportData(
            short_summary="AI agents are transforming enterprise.",
            markdown_report="# Full Report\n\nContent here...",
            follow_up_questions=["How to measure ROI?"],
            query_analysis_summary=sample_query_analysis_summary,
            source_metrics=sample_source_metrics,
            planning_notes="Query classified as market_research.",
            sources_with_credibility=sample_sources_with_credibility,
        )
        
        data = report.model_dump()
        
        # Check all fields present
        assert "short_summary" in data
        assert "markdown_report" in data
        assert "query_analysis_summary" in data
        assert "source_metrics" in data
        assert "planning_notes" in data
        assert "sources_with_credibility" in data
        
        # Check nested structure
        assert data["source_metrics"]["total_sources"] == 20
        assert data["query_analysis_summary"]["query_type"] == "market_research"
        assert len(data["sources_with_credibility"]) == 3


# ============================================================================
# Report Formatter Tests
# ============================================================================

class TestAddMethodologySection:
    """Tests for add_methodology_section function."""
    
    def test_no_metrics_returns_unchanged(self, sample_markdown_report):
        """Report should be unchanged if no metrics provided."""
        result = add_methodology_section(sample_markdown_report)
        assert result == sample_markdown_report
    
    def test_adds_methodology_heading(
        self,
        sample_markdown_report,
        sample_source_metrics
    ):
        """Should add Methodology & Source Quality heading."""
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=sample_source_metrics,
        )
        
        assert "## Methodology & Source Quality" in result
    
    def test_adds_source_quality_table(
        self,
        sample_markdown_report,
        sample_source_metrics
    ):
        """Should add source quality statistics table."""
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=sample_source_metrics,
        )
        
        assert "Total Sources Analyzed" in result
        assert "Average Credibility Score" in result
        assert "68.5" in result  # Average score
    
    def test_adds_research_approach(
        self,
        sample_markdown_report,
        sample_query_analysis_summary
    ):
        """Should add research approach section."""
        result = add_methodology_section(
            sample_markdown_report,
            query_analysis_summary=sample_query_analysis_summary,
        )
        
        assert "### Research Approach" in result
        assert "market_research" in result
        assert "complex" in result
    
    def test_adds_credibility_legend(
        self,
        sample_markdown_report,
        sample_source_metrics
    ):
        """Should add credibility legend."""
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=sample_source_metrics,
        )
        
        assert "### Credibility Legend" in result
        assert "⭐ High" in result
        assert "⚠️ Low" in result
    
    def test_adds_key_sources(
        self,
        sample_markdown_report,
        sample_source_metrics,
        sample_sources_with_credibility
    ):
        """Should add key sources with credibility badges."""
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=sample_source_metrics,
            sources_with_credibility=sample_sources_with_credibility,
        )
        
        assert "### Key Sources Used" in result
        assert "arxiv.org" in result
        assert "⭐ High Credibility" in result
    
    def test_inserts_before_references(
        self,
        sample_markdown_report,
        sample_source_metrics
    ):
        """Should insert methodology section before References."""
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=sample_source_metrics,
        )
        
        # Methodology should appear before References
        methodology_pos = result.find("## Methodology & Source Quality")
        references_pos = result.find("## References")
        
        assert methodology_pos < references_pos
    
    def test_quality_badge_high(self, sample_markdown_report):
        """High average score should show high quality badge."""
        metrics = SourceMetrics(
            total_sources=10,
            average_score=75.0,
        )
        
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=metrics,
        )
        
        assert "⭐ **High Quality**" in result
    
    def test_quality_badge_medium(self, sample_markdown_report):
        """Medium average score should show medium quality badge."""
        metrics = SourceMetrics(
            total_sources=10,
            average_score=55.0,
        )
        
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=metrics,
        )
        
        assert "✓ **Medium Quality**" in result
    
    def test_quality_badge_low(self, sample_markdown_report):
        """Low average score should show warning badge."""
        metrics = SourceMetrics(
            total_sources=10,
            average_score=35.0,
        )
        
        result = add_methodology_section(
            sample_markdown_report,
            source_metrics=metrics,
        )
        
        assert "⚠️ **Mixed Quality**" in result


class TestFormatResearchReport:
    """Tests for format_research_report function."""
    
    def test_removes_table_of_contents(self):
        """Should remove Table of Contents section."""
        report = """# Report

## Table of Contents
- Section 1
- Section 2

## Executive Summary
Content here...
"""
        result = format_research_report(report, "Summary")
        
        assert "Table of Contents" not in result
        assert "Executive Summary" in result
    
    def test_removes_duplicate_headings(self):
        """Should remove duplicate section headings."""
        report = """# Report

## Introduction
First intro...

## Key Findings
Findings...

## Introduction
Duplicate intro...
"""
        result = format_research_report(report, "Summary")
        
        # Count occurrences of "## Introduction"
        count = result.count("## Introduction")
        assert count == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the enhanced writer wiring."""
    
    def test_full_report_with_all_metadata(
        self,
        sample_source_metrics,
        sample_query_analysis_summary,
        sample_sources_with_credibility,
        sample_markdown_report
    ):
        """Test creating a full report with all metadata."""
        # Format and add methodology
        formatted = format_research_report(
            sample_markdown_report,
            "AI agents summary",
        )
        
        enhanced = add_methodology_section(
            formatted,
            source_metrics=sample_source_metrics,
            query_analysis_summary=sample_query_analysis_summary,
            sources_with_credibility=sample_sources_with_credibility,
        )
        
        # Create ReportData
        report = ReportData(
            short_summary="AI agents summary",
            markdown_report=enhanced,
            query_analysis_summary=sample_query_analysis_summary,
            source_metrics=sample_source_metrics,
            sources_with_credibility=sample_sources_with_credibility,
        )
        
        # Verify structure
        assert "## Methodology & Source Quality" in report.markdown_report
        assert report.source_metrics.total_sources == 20
        assert len(report.sources_with_credibility) == 3
        
        # Verify serialization
        data = report.model_dump()
        assert data["source_metrics"]["average_score"] == 68.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
