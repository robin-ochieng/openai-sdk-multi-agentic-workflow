"""
Unit Tests for Fact Checker Agent

Tests for:
- Claim extraction from markdown
- Claim categorization
- Verification result models
- VerificationReport generation
- FactCheckerAgent functionality
"""

import pytest
from datetime import datetime
from typing import List

# Import models
from deep_research.models.news_models import (
    FactualClaim,
    VerificationResult,
    VerificationReport,
    VerificationSource,
    VerificationStatus,
    ClaimCategory,
)

# Import agent and utilities
from deep_research.research_agents.fact_checker_agent import (
    FactCheckerAgent,
    create_fact_checker_agent,
    get_fact_checker,
    extract_claims_from_markdown,
    categorize_claim,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown report for testing."""
    return """
# Research Report: AI Industry Growth

## Executive Summary

The artificial intelligence market grew by 37.5% in 2024, reaching a total value of $200 billion.
According to industry analysts, "AI adoption will continue to accelerate through 2025."

## Market Analysis

In 2024, OpenAI's revenue exceeded $5 billion, representing a 3x increase from the previous year.
Microsoft invested more than $13 billion in AI technologies. The global AI market is expected
to reach $500 billion by 2027.

## Key Players

- Google has deployed AI in over 80% of its products
- Amazon Web Services holds approximately 32% market share in cloud AI
- NVIDIA reported $47 billion in annual revenue

## Risks

Economic uncertainty may impact AI investment decisions.
"""


@pytest.fixture
def sample_claim() -> FactualClaim:
    """Create a sample factual claim."""
    return FactualClaim(
        claim_id="claim_1",
        claim_text="The AI market grew by 37.5% in 2024.",
        context="The artificial intelligence market grew by 37.5% in 2024, reaching $200 billion.",
        source_section="Executive Summary",
        line_number=5,
        category=ClaimCategory.STATISTIC,
        is_quantitative=True,
        is_checkable=True,
    )


@pytest.fixture
def sample_verification_source() -> VerificationSource:
    """Create a sample verification source."""
    return VerificationSource(
        name="Reuters",
        url="https://reuters.com/ai-market-report",
        credibility_score=90.0,
        supports_claim=True,
        contradicts_claim=False,
        relevant_excerpt="AI market growth reached 37.5% according to latest data.",
    )


@pytest.fixture
def sample_verification_result(sample_claim, sample_verification_source) -> VerificationResult:
    """Create a sample verification result."""
    return VerificationResult(
        claim=sample_claim,
        status=VerificationStatus.VERIFIED,
        confidence=0.85,
        supporting_sources=[sample_verification_source],
        contradicting_sources=[],
        explanation="Verified by 1 source including Reuters.",
    )


@pytest.fixture
def sample_verification_report(sample_verification_result) -> VerificationReport:
    """Create a sample verification report."""
    # Create additional results with different statuses
    uncertain_claim = FactualClaim(
        claim_id="claim_2",
        claim_text="OpenAI revenue exceeded $5 billion.",
        category=ClaimCategory.STATISTIC,
    )
    
    disputed_claim = FactualClaim(
        claim_id="claim_3",
        claim_text="Google uses AI in 80% of products.",
        category=ClaimCategory.STATISTIC,
    )
    
    results = [
        sample_verification_result,
        VerificationResult(
            claim=uncertain_claim,
            status=VerificationStatus.UNCERTAIN,
            confidence=0.4,
            explanation="Insufficient evidence.",
        ),
        VerificationResult(
            claim=disputed_claim,
            status=VerificationStatus.DISPUTED,
            confidence=0.7,
            explanation="Sources report different figures.",
            corrected_claim="Google uses AI in approximately 70% of products.",
        ),
    ]
    
    report = VerificationReport(
        document_title="AI Research Report",
        results=results,
    )
    report.calculate_statistics()
    
    return report


# =============================================================================
# Test Class: FactualClaim Model
# =============================================================================

class TestFactualClaim:
    """Tests for FactualClaim model."""
    
    def test_create_basic_claim(self):
        """Test creating a basic claim."""
        claim = FactualClaim(claim_text="Test claim")
        
        assert claim.claim_text == "Test claim"
        assert claim.claim_id == ""
        assert claim.category == ClaimCategory.OTHER
        assert claim.is_checkable is True
    
    def test_create_full_claim(self, sample_claim):
        """Test creating a full claim."""
        assert sample_claim.claim_id == "claim_1"
        assert "37.5%" in sample_claim.claim_text
        assert sample_claim.category == ClaimCategory.STATISTIC
        assert sample_claim.is_quantitative is True
    
    def test_claim_with_entities(self):
        """Test claim with entities."""
        claim = FactualClaim(
            claim_text="Microsoft invested $13 billion",
            entities_mentioned=["Microsoft"],
        )
        
        assert "Microsoft" in claim.entities_mentioned
    
    def test_uncheckable_claim(self):
        """Test uncheckable claim."""
        claim = FactualClaim(
            claim_text="AI will transform the world.",
            is_checkable=False,
            checkability_reason="Opinion/prediction, not verifiable fact.",
        )
        
        assert claim.is_checkable is False
        assert "Opinion" in claim.checkability_reason


# =============================================================================
# Test Class: VerificationSource Model
# =============================================================================

class TestVerificationSource:
    """Tests for VerificationSource model."""
    
    def test_create_basic_source(self):
        """Test creating a basic source."""
        source = VerificationSource(name="Test Source")
        
        assert source.name == "Test Source"
        assert source.url == ""
        assert source.credibility_score == 50.0
    
    def test_create_supporting_source(self, sample_verification_source):
        """Test creating a supporting source."""
        assert sample_verification_source.supports_claim is True
        assert sample_verification_source.contradicts_claim is False
    
    def test_contradicting_source(self):
        """Test contradicting source."""
        source = VerificationSource(
            name="Conflicting Source",
            supports_claim=False,
            contradicts_claim=True,
        )
        
        assert source.contradicts_claim is True


# =============================================================================
# Test Class: VerificationResult Model
# =============================================================================

class TestVerificationResult:
    """Tests for VerificationResult model."""
    
    def test_create_basic_result(self, sample_claim):
        """Test creating a basic result."""
        result = VerificationResult(claim=sample_claim)
        
        assert result.status == VerificationStatus.UNCERTAIN
        assert result.confidence == 0.5
    
    def test_verified_result(self, sample_verification_result):
        """Test verified result."""
        assert sample_verification_result.status == VerificationStatus.VERIFIED
        assert sample_verification_result.confidence == 0.85
        assert len(sample_verification_result.supporting_sources) == 1
    
    def test_confidence_level_high(self, sample_claim):
        """Test high confidence level."""
        result = VerificationResult(
            claim=sample_claim,
            confidence=0.9,
        )
        assert result.confidence_level == "high"
    
    def test_confidence_level_medium(self, sample_claim):
        """Test medium confidence level."""
        result = VerificationResult(
            claim=sample_claim,
            confidence=0.6,
        )
        assert result.confidence_level == "medium"
    
    def test_confidence_level_low(self, sample_claim):
        """Test low confidence level."""
        result = VerificationResult(
            claim=sample_claim,
            confidence=0.3,
        )
        assert result.confidence_level == "low"
    
    def test_status_emoji_verified(self, sample_verification_result):
        """Test verified emoji."""
        assert sample_verification_result.status_emoji == "✅"
    
    def test_status_emoji_disputed(self, sample_claim):
        """Test disputed emoji."""
        result = VerificationResult(
            claim=sample_claim,
            status=VerificationStatus.DISPUTED,
        )
        assert result.status_emoji == "❌"
    
    def test_status_emoji_uncertain(self, sample_claim):
        """Test uncertain emoji."""
        result = VerificationResult(
            claim=sample_claim,
            status=VerificationStatus.UNCERTAIN,
        )
        assert result.status_emoji == "⚠️"
    
    def test_to_annotation(self, sample_verification_result):
        """Test annotation generation."""
        annotation = sample_verification_result.to_annotation()
        
        assert "VERIFIED" in annotation
        assert "85%" in annotation


# =============================================================================
# Test Class: VerificationReport Model
# =============================================================================

class TestVerificationReport:
    """Tests for VerificationReport model."""
    
    def test_create_basic_report(self):
        """Test creating a basic report."""
        report = VerificationReport()
        
        assert report.document_title == ""
        assert len(report.results) == 0
    
    def test_calculate_statistics(self, sample_verification_report):
        """Test statistics calculation."""
        assert sample_verification_report.total_claims == 3
        assert sample_verification_report.verified_count == 1
        assert sample_verification_report.uncertain_count == 1
        assert sample_verification_report.disputed_count == 1
    
    def test_overall_reliability(self, sample_verification_report):
        """Test overall reliability calculation."""
        # 1 verified (1.0) + 1 uncertain (0.5) + 1 disputed (0.0) = 1.5 / 3 = 0.5
        assert 0.4 <= sample_verification_report.overall_reliability <= 0.6
    
    def test_to_markdown_section(self, sample_verification_report):
        """Test markdown section generation."""
        markdown = sample_verification_report.to_markdown_section()
        
        assert "## Verification Status" in markdown
        assert "### Claim Summary" in markdown
        assert "Verified" in markdown
        assert "Disputed" in markdown
    
    def test_to_markdown_includes_disputed(self, sample_verification_report):
        """Test markdown includes disputed claims section."""
        markdown = sample_verification_report.to_markdown_section()
        
        assert "### ⚠️ Disputed Claims" in markdown
        assert "Correction" in markdown
    
    def test_to_summary_dict(self, sample_verification_report):
        """Test summary dict generation."""
        summary = sample_verification_report.to_summary_dict()
        
        assert summary["total_claims"] == 3
        assert summary["verified"] == 1
        assert summary["disputed"] == 1
        assert "overall_reliability" in summary


# =============================================================================
# Test Class: Claim Extraction
# =============================================================================

class TestExtractClaimsFromMarkdown:
    """Tests for extract_claims_from_markdown function."""
    
    def test_extract_percentage_claims(self, sample_markdown):
        """Test extraction of percentage claims."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        # Should find "37.5%" claim
        percentages = [c for c in claims if "%" in c.claim_text]
        assert len(percentages) >= 1
    
    def test_extract_money_claims(self, sample_markdown):
        """Test extraction of money claims."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        # Should find "$200 billion", "$5 billion", "$13 billion", etc.
        money_claims = [c for c in claims if "$" in c.claim_text]
        assert len(money_claims) >= 1
    
    def test_extract_date_claims(self, sample_markdown):
        """Test extraction of date claims."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        # Should find claims with years
        date_claims = [c for c in claims if "2024" in c.claim_text or "2027" in c.claim_text]
        assert len(date_claims) >= 1
    
    def test_claim_has_section_context(self, sample_markdown):
        """Test that claims have section context."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        # Some claims should have section info
        sections = [c.source_section for c in claims if c.source_section]
        assert len(sections) >= 1
    
    def test_claim_categorization(self, sample_markdown):
        """Test that claims are categorized."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        categories = [c.category for c in claims]
        assert ClaimCategory.STATISTIC in categories
    
    def test_empty_markdown(self):
        """Test with empty markdown."""
        claims = extract_claims_from_markdown("")
        assert len(claims) == 0
    
    def test_markdown_without_claims(self):
        """Test markdown without factual claims."""
        markdown = """
# Introduction

This is a general overview document with opinions.
We think the future looks promising.
"""
        claims = extract_claims_from_markdown(markdown)
        # May find some claims or not depending on patterns
        # Main test is that it doesn't error


# =============================================================================
# Test Class: Claim Categorization
# =============================================================================

class TestCategorizeClaim:
    """Tests for categorize_claim function."""
    
    def test_statistic_claim(self):
        """Test statistic categorization."""
        claim = "Revenue increased by 25% to $500 million."
        category = categorize_claim(claim)
        assert category == ClaimCategory.STATISTIC
    
    def test_temporal_claim(self):
        """Test temporal categorization."""
        claim = "The company was founded in 2015."
        category = categorize_claim(claim)
        assert category == ClaimCategory.TEMPORAL
    
    def test_quote_claim(self):
        """Test quote categorization."""
        claim = 'The CEO said "we are committed to growth."'
        category = categorize_claim(claim)
        assert category == ClaimCategory.QUOTE
    
    def test_comparative_claim(self):
        """Test comparative categorization."""
        # Use text that matches comparative pattern (more than, less than, greater than)
        claim = "Product X sold more than three times as many units as Product Y."
        category = categorize_claim(claim)
        assert category == ClaimCategory.COMPARATIVE
    
    def test_scientific_claim(self):
        """Test scientific categorization."""
        claim = "Research studies have discovered new evidence."
        category = categorize_claim(claim)
        assert category == ClaimCategory.SCIENTIFIC
    
    def test_other_claim(self):
        """Test other categorization."""
        claim = "The sky appears blue on clear days."
        category = categorize_claim(claim)
        assert category == ClaimCategory.OTHER


# =============================================================================
# Test Class: FactCheckerAgent
# =============================================================================

class TestFactCheckerAgent:
    """Tests for FactCheckerAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = FactCheckerAgent()
        
        assert agent.model == "gpt-4o-mini"
        assert agent._verification_agent is None  # Lazy loaded
        assert len(agent._verification_cache) == 0
    
    def test_agent_initialization_custom_model(self):
        """Test agent with custom model."""
        agent = FactCheckerAgent(model="gpt-4o")
        assert agent.model == "gpt-4o"
    
    def test_prioritize_claims(self, sample_claim):
        """Test claim prioritization."""
        agent = FactCheckerAgent()
        
        claims = [
            FactualClaim(
                claim_text="General statement",
                category=ClaimCategory.OTHER,
            ),
            sample_claim,  # STATISTIC, quantitative
            FactualClaim(
                claim_text="10x growth",
                category=ClaimCategory.COMPARATIVE,
                is_quantitative=True,
            ),
        ]
        
        prioritized = agent._prioritize_claims(claims)
        
        # Statistics and comparatives should be first
        assert prioritized[0].category in [ClaimCategory.STATISTIC, ClaimCategory.COMPARATIVE]
    
    def test_get_cache_key(self, sample_claim):
        """Test cache key generation."""
        agent = FactCheckerAgent()
        
        key1 = agent._get_cache_key(sample_claim)
        key2 = agent._get_cache_key(sample_claim)
        
        # Same claim should produce same key
        assert key1 == key2
    
    def test_build_verification_query(self, sample_claim):
        """Test verification query building."""
        agent = FactCheckerAgent()
        
        query = agent._build_verification_query(sample_claim)
        
        assert "fact check" in query
        assert len(query) > 10
    
    def test_check_collected_sources_with_match(self, sample_claim):
        """Test checking against collected sources with match."""
        agent = FactCheckerAgent()
        
        sources = [
            {
                "title": "AI Market Report",
                "url": "https://example.com/report",
                "snippet": "The AI market grew by 37.5% in 2024, reaching significant milestones.",
                "credibility_score": 80,
            }
        ]
        
        result = agent._check_collected_sources(sample_claim, sources)
        
        # Should find a match
        assert result is not None
        assert result.status == VerificationStatus.VERIFIED
    
    def test_check_collected_sources_no_match(self, sample_claim):
        """Test checking against collected sources with no match."""
        agent = FactCheckerAgent()
        
        sources = [
            {
                "title": "Unrelated Article",
                "url": "https://example.com/other",
                "snippet": "Weather forecast for tomorrow is sunny.",
                "credibility_score": 70,
            }
        ]
        
        result = agent._check_collected_sources(sample_claim, sources)
        
        # Should not find a match
        assert result is None
    
    def test_parse_verification_response_verified(self, sample_claim):
        """Test parsing verified response."""
        agent = FactCheckerAgent()
        
        response = "The claim is verified and confirmed by multiple sources including reuters.com."
        result = agent._parse_verification_response(sample_claim, response)
        
        assert result.status == VerificationStatus.VERIFIED
    
    def test_parse_verification_response_disputed(self, sample_claim):
        """Test parsing disputed response."""
        agent = FactCheckerAgent()
        
        response = "The claim contradicts official data. Sources refute this incorrect statement."
        result = agent._parse_verification_response(sample_claim, response)
        
        assert result.status == VerificationStatus.DISPUTED
    
    def test_parse_verification_response_uncertain(self, sample_claim):
        """Test parsing uncertain response."""
        agent = FactCheckerAgent()
        
        response = "Could not find reliable sources. The evidence is insufficient and unclear."
        result = agent._parse_verification_response(sample_claim, response)
        
        assert result.status == VerificationStatus.UNCERTAIN
    
    def test_annotate_markdown(self, sample_markdown, sample_verification_report):
        """Test markdown annotation."""
        agent = FactCheckerAgent()
        
        # Add a disputed result that matches text in sample_markdown
        claim = FactualClaim(
            claim_text="The AI market is expected to reach $500 billion by 2027",  # Not exact match
            line_number=10,
        )
        
        annotated = agent.annotate_markdown(sample_markdown, sample_verification_report)
        
        # Should still contain original content
        assert "## Executive Summary" in annotated


# =============================================================================
# Test Class: Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Tests for module-level helper functions."""
    
    def test_create_fact_checker_agent(self):
        """Test factory function."""
        agent = create_fact_checker_agent()
        assert isinstance(agent, FactCheckerAgent)
    
    def test_create_fact_checker_agent_custom_model(self):
        """Test factory with custom model."""
        agent = create_fact_checker_agent(model="gpt-4o")
        assert agent.model == "gpt-4o"
    
    def test_get_fact_checker(self):
        """Test get_fact_checker function."""
        checker = get_fact_checker()
        assert isinstance(checker, FactCheckerAgent)


# =============================================================================
# Test Class: Integration Tests
# =============================================================================

class TestFactCheckerIntegration:
    """Integration tests for fact checking workflow."""
    
    def test_full_extraction_and_categorization(self, sample_markdown):
        """Test full claim extraction workflow."""
        claims = extract_claims_from_markdown(sample_markdown)
        
        # Should extract multiple claims
        assert len(claims) >= 3
        
        # Should have different categories
        categories = set(c.category for c in claims)
        assert len(categories) >= 1
    
    def test_report_generation(self, sample_claim):
        """Test full report generation."""
        results = [
            VerificationResult(
                claim=sample_claim,
                status=VerificationStatus.VERIFIED,
                confidence=0.9,
            ),
            VerificationResult(
                claim=FactualClaim(claim_text="Another claim"),
                status=VerificationStatus.UNCERTAIN,
                confidence=0.5,
            ),
        ]
        
        report = VerificationReport(
            document_title="Test Report",
            results=results,
        )
        report.calculate_statistics()
        
        assert report.total_claims == 2
        assert report.verified_count == 1
        assert report.overall_reliability > 0
        
        # Should generate valid markdown
        markdown = report.to_markdown_section()
        assert "## Verification Status" in markdown
