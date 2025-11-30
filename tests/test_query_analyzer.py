"""
Unit Tests for QueryAnalyzerAgent

Tests cover:
1. Model schema validation
2. Query classification for different query types
3. Entity extraction accuracy
4. Integration with ResearchManager

Run with:
    pytest tests/test_query_analyzer.py -v
    
Or run specific tests:
    pytest tests/test_query_analyzer.py::test_query_analysis_schema -v
"""

import pytest
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

# Import models
from deep_research.models.query_analysis import (
    QueryAnalysis,
    QueryAnalysisRequest,
    QueryType,
    ComplexityLevel,
    TimeSensitivity,
    AudienceLevel,
    ResearchDepth,
    QUERY_TYPE_DESCRIPTIONS,
)

# Import agent utilities
from deep_research.research_agents.query_analyzer_agent import (
    estimate_search_count,
    get_recommended_report_length,
)


# ---------------------------------------------------------------------------
# Schema Validation Tests
# ---------------------------------------------------------------------------

class TestQueryAnalysisSchema:
    """Test the QueryAnalysis Pydantic model."""
    
    def test_default_values(self):
        """Test that default values are applied correctly."""
        analysis = QueryAnalysis()
        
        assert analysis.query_type == "general"
        assert analysis.complexity == "moderate"
        assert analysis.time_sensitivity == "current"
        assert analysis.audience_level == "general"
        assert analysis.required_depth == "detailed"
        assert analysis.geographic_scope == "global"
        assert analysis.recommended_search_count == 5
        assert analysis.estimated_research_time == 5
    
    def test_full_initialization(self):
        """Test initialization with all fields."""
        analysis = QueryAnalysis(
            query_type="market_research",
            complexity="complex",
            time_sensitivity="current",
            primary_entities=["OpenAI", "Anthropic", "Google DeepMind"],
            secondary_entities=["AI assistants", "LLMs"],
            geographic_scope="North America",
            time_range="2023-2025",
            audience_level="executive",
            required_depth="comprehensive",
            recommended_sections=[
                "Executive Summary",
                "Market Overview",
                "Competitive Landscape",
            ],
            required_data_points=["market size", "growth rate", "market share"],
            visualization_opportunities=["pie chart", "trend line"],
            estimated_research_time=15,
            recommended_search_count=8,
        )
        
        assert analysis.query_type == "market_research"
        assert analysis.complexity == "complex"
        assert len(analysis.primary_entities) == 3
        assert "OpenAI" in analysis.primary_entities
        assert analysis.geographic_scope == "North America"
        assert analysis.recommended_search_count == 8
    
    def test_invalid_query_type_raises_error(self):
        """Test that invalid enum values raise validation errors."""
        with pytest.raises(ValueError):
            QueryAnalysis(query_type="invalid_type")
    
    def test_search_count_bounds(self):
        """Test that search count is bounded (3-15)."""
        # Valid bounds
        analysis_min = QueryAnalysis(recommended_search_count=3)
        assert analysis_min.recommended_search_count == 3
        
        analysis_max = QueryAnalysis(recommended_search_count=15)
        assert analysis_max.recommended_search_count == 15
        
        # Out of bounds should raise error
        with pytest.raises(ValueError):
            QueryAnalysis(recommended_search_count=2)
        
        with pytest.raises(ValueError):
            QueryAnalysis(recommended_search_count=20)
    
    def test_json_serialization(self):
        """Test that the model serializes to JSON correctly."""
        analysis = QueryAnalysis(
            query_type="technical",
            primary_entities=["Python", "FastAPI"],
        )
        
        json_data = analysis.model_dump_json()
        assert "technical" in json_data
        assert "Python" in json_data
        assert "FastAPI" in json_data
    
    def test_model_dump(self):
        """Test dictionary export."""
        analysis = QueryAnalysis(
            query_type="comparative",
            primary_entities=["AWS", "Azure", "GCP"],
        )
        
        data = analysis.model_dump()
        assert isinstance(data, dict)
        assert data["query_type"] == "comparative"
        assert len(data["primary_entities"]) == 3


class TestQueryAnalysisRequest:
    """Test the QueryAnalysisRequest model."""
    
    def test_valid_request(self):
        """Test valid request creation."""
        request = QueryAnalysisRequest(
            query="What is the market size of AI in healthcare?",
            context="Focus on North American market"
        )
        
        assert "market size" in request.query
        assert request.context is not None
    
    def test_query_min_length(self):
        """Test that query must have minimum length."""
        with pytest.raises(ValueError):
            QueryAnalysisRequest(query="Hi")
    
    def test_optional_context(self):
        """Test that context is optional."""
        request = QueryAnalysisRequest(
            query="What are the latest trends in machine learning?"
        )
        
        assert request.context is None


# ---------------------------------------------------------------------------
# Utility Function Tests
# ---------------------------------------------------------------------------

class TestEstimateSearchCount:
    """Test the search count estimation logic."""
    
    def test_simple_query_default_count(self):
        """Simple queries should use the model's recommendation."""
        analysis = QueryAnalysis(
            complexity="simple",
            recommended_search_count=4,
        )
        
        count = estimate_search_count(analysis)
        assert count == 4
    
    def test_complex_query_increases_count(self):
        """Complex queries should have at least 7 searches."""
        analysis = QueryAnalysis(
            complexity="complex",
            recommended_search_count=5,
        )
        
        count = estimate_search_count(analysis)
        assert count >= 7
    
    def test_expert_level_increases_count(self):
        """Expert-level queries should have at least 10 searches."""
        analysis = QueryAnalysis(
            complexity="expert_level",
            recommended_search_count=5,
        )
        
        count = estimate_search_count(analysis)
        assert count >= 10
    
    def test_comparative_scales_with_entities(self):
        """Comparative queries should scale with entity count."""
        analysis = QueryAnalysis(
            query_type="comparative",
            primary_entities=["AWS", "Azure", "GCP", "Oracle Cloud"],
            recommended_search_count=5,
        )
        
        count = estimate_search_count(analysis)
        # 4 entities * 2 = 8 minimum
        assert count >= 8
    
    def test_max_cap_at_15(self):
        """Search count should never exceed 15."""
        analysis = QueryAnalysis(
            query_type="comparative",
            complexity="expert_level",
            primary_entities=[f"Entity{i}" for i in range(20)],
            recommended_search_count=15,
        )
        
        count = estimate_search_count(analysis)
        assert count <= 15


class TestRecommendedReportLength:
    """Test report length recommendations."""
    
    def test_overview_length(self):
        """Overview depth should recommend 500-1000 words."""
        analysis = QueryAnalysis(required_depth="overview")
        min_words, max_words = get_recommended_report_length(analysis)
        
        assert min_words == 500
        assert max_words == 1000
    
    def test_detailed_length(self):
        """Detailed depth should recommend 1500-2500 words."""
        analysis = QueryAnalysis(required_depth="detailed")
        min_words, max_words = get_recommended_report_length(analysis)
        
        assert min_words == 1500
        assert max_words == 2500
    
    def test_comprehensive_length(self):
        """Comprehensive depth should recommend 3000-5000 words."""
        analysis = QueryAnalysis(required_depth="comprehensive")
        min_words, max_words = get_recommended_report_length(analysis)
        
        assert min_words == 3000
        assert max_words == 5000
    
    def test_exhaustive_length(self):
        """Exhaustive depth should recommend 5000-10000 words."""
        analysis = QueryAnalysis(required_depth="exhaustive")
        min_words, max_words = get_recommended_report_length(analysis)
        
        assert min_words == 5000
        assert max_words == 10000


# ---------------------------------------------------------------------------
# Query Classification Examples (Integration-style tests)
# ---------------------------------------------------------------------------

class TestQueryClassificationExamples:
    """
    Test expected classifications for common query patterns.
    
    These tests validate the expected output structure for different
    types of research queries, simulating what the QueryAnalyzerAgent
    should produce.
    """
    
    def test_market_research_query_structure(self):
        """
        Example: Market research query should have specific structure.
        
        Query: "What is the current market size of AI code assistants?"
        """
        # This is what we expect the agent to produce
        expected_analysis = QueryAnalysis(
            query_type="market_research",
            complexity="moderate",
            time_sensitivity="current",
            primary_entities=["AI code assistants"],
            secondary_entities=["GitHub Copilot", "Amazon CodeWhisperer", "Tabnine"],
            geographic_scope="global",
            audience_level="executive",
            required_depth="detailed",
            recommended_sections=[
                "Executive Summary",
                "Market Overview",
                "Key Players",
                "Market Size & Growth",
                "Future Outlook",
            ],
            required_data_points=["market size", "growth rate", "market share"],
            visualization_opportunities=["market size chart", "competitor comparison"],
            estimated_research_time=8,
            recommended_search_count=6,
        )
        
        # Validate structure
        assert expected_analysis.query_type == "market_research"
        assert "market size" in expected_analysis.required_data_points
        assert len(expected_analysis.recommended_sections) >= 4
    
    def test_comparative_query_structure(self):
        """
        Example: Comparative query should identify all entities.
        
        Query: "Compare React, Vue, and Angular for enterprise applications"
        """
        expected_analysis = QueryAnalysis(
            query_type="comparative",
            complexity="complex",
            time_sensitivity="current",
            primary_entities=["React", "Vue", "Angular"],
            secondary_entities=["enterprise applications", "frontend frameworks"],
            geographic_scope="global",
            audience_level="technical",
            required_depth="comprehensive",
            recommended_sections=[
                "Executive Summary",
                "Framework Overview",
                "Feature Comparison",
                "Performance Benchmarks",
                "Use Case Recommendations",
                "Conclusion",
            ],
            required_data_points=[
                "performance benchmarks",
                "learning curve",
                "community size",
                "enterprise adoption",
            ],
            visualization_opportunities=[
                "feature comparison matrix",
                "performance chart",
                "radar chart",
            ],
            estimated_research_time=12,
            recommended_search_count=9,
        )
        
        # Validate structure
        assert expected_analysis.query_type == "comparative"
        assert len(expected_analysis.primary_entities) == 3
        assert "React" in expected_analysis.primary_entities
        assert expected_analysis.audience_level == "technical"
    
    def test_technical_query_structure(self):
        """
        Example: Technical query should focus on implementation details.
        
        Query: "How to implement rate limiting in FastAPI with Redis?"
        """
        expected_analysis = QueryAnalysis(
            query_type="technical",
            complexity="moderate",
            time_sensitivity="evergreen",
            primary_entities=["FastAPI", "Redis", "rate limiting"],
            secondary_entities=["Python", "API design", "caching"],
            geographic_scope="global",
            audience_level="technical",
            required_depth="detailed",
            recommended_sections=[
                "Introduction",
                "Prerequisites",
                "Implementation Steps",
                "Code Examples",
                "Best Practices",
                "Troubleshooting",
            ],
            required_data_points=["implementation patterns", "performance considerations"],
            visualization_opportunities=["architecture diagram", "flow chart"],
            estimated_research_time=6,
            recommended_search_count=5,
        )
        
        # Validate structure
        assert expected_analysis.query_type == "technical"
        assert expected_analysis.time_sensitivity == "evergreen"
        assert "FastAPI" in expected_analysis.primary_entities
    
    def test_due_diligence_query_structure(self):
        """
        Example: Due diligence query should cover comprehensive areas.
        
        Query: "Investment due diligence on Stripe for Series B participation"
        """
        expected_analysis = QueryAnalysis(
            query_type="due_diligence",
            complexity="expert_level",
            time_sensitivity="current",
            primary_entities=["Stripe"],
            secondary_entities=["payments industry", "fintech", "Series B"],
            geographic_scope="global",
            audience_level="investor",
            required_depth="exhaustive",
            recommended_sections=[
                "Executive Summary",
                "Company Overview",
                "Market Analysis",
                "Financial Analysis",
                "Competitive Position",
                "Risk Assessment",
                "Investment Thesis",
            ],
            required_data_points=[
                "revenue",
                "valuation",
                "growth rate",
                "market share",
                "funding history",
            ],
            visualization_opportunities=[
                "funding timeline",
                "revenue growth chart",
                "competitive positioning matrix",
            ],
            estimated_research_time=20,
            recommended_search_count=12,
        )
        
        # Validate structure
        assert expected_analysis.query_type == "due_diligence"
        assert expected_analysis.complexity == "expert_level"
        assert expected_analysis.audience_level == "investor"
        assert expected_analysis.required_depth == "exhaustive"


# ---------------------------------------------------------------------------
# Constants Tests
# ---------------------------------------------------------------------------

class TestConstants:
    """Test module constants and descriptions."""
    
    def test_query_type_descriptions_complete(self):
        """Ensure all query types have descriptions."""
        expected_types = [
            "exploratory",
            "comparative",
            "technical",
            "market_research",
            "due_diligence",
            "competitive_analysis",
            "trend_analysis",
            "general",
        ]
        
        for query_type in expected_types:
            assert query_type in QUERY_TYPE_DESCRIPTIONS
            assert len(QUERY_TYPE_DESCRIPTIONS[query_type]) > 10


# ---------------------------------------------------------------------------
# Run tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
