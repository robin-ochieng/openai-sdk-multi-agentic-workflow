"""
Unit tests for Source Validator Agent.

Tests cover:
- High-quality source validation (academic, government, major news)
- Outdated source detection and penalization
- Suspicious/blocked domain handling
- Domain classification accuracy
- Credibility scoring calculations
- Batch validation statistics
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from deep_research.models.source_validation import (
    SourceMetadata,
    SourceCredibility,
    CredibilityScores,
    ValidationResult,
    ValidationStatistics,
    CredibilityLevel,
    InclusionDecision,
    DomainCategory,
    ExclusionReason,
)
from deep_research.research_agents.source_validator_agent import (
    DomainClassifier,
    SourceValidator,
    validate_search_results,
    get_source_validator,
    get_domain_classifier,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def domain_classifier():
    """Get a domain classifier with default configuration."""
    return DomainClassifier()


@pytest.fixture
def source_validator():
    """Get a source validator with default configuration."""
    return SourceValidator()


@pytest.fixture
def high_quality_source():
    """Create a high-quality academic source."""
    return SourceMetadata(
        url="https://arxiv.org/abs/2024.12345",
        title="Advances in Neural Network Architecture",
        snippet="A comprehensive study on transformer improvements...",
        publication_date=datetime.utcnow() - timedelta(days=15),
    )


@pytest.fixture
def government_source():
    """Create a government source."""
    return SourceMetadata(
        url="https://www.cdc.gov/health-guidelines/2024",
        title="CDC Health Guidelines 2024",
        snippet="Official guidelines for public health measures...",
        publication_date=datetime.utcnow() - timedelta(days=30),
    )


@pytest.fixture
def outdated_source():
    """Create an outdated source (3 years old)."""
    return SourceMetadata(
        url="https://techblog.example.com/old-article",
        title="Tech Trends 2021",
        snippet="Analysis of technology trends...",
        publication_date=datetime.utcnow() - timedelta(days=1100),
    )


@pytest.fixture
def social_media_source():
    """Create a social media source."""
    return SourceMetadata(
        url="https://twitter.com/user/status/12345",
        title="Tweet about topic",
        snippet="User opinion on the matter...",
        publication_date=datetime.utcnow() - timedelta(days=5),
    )


@pytest.fixture
def user_generated_source():
    """Create a user-generated content source."""
    return SourceMetadata(
        url="https://medium.com/@user/article-title",
        title="My thoughts on AI",
        snippet="Personal perspective on artificial intelligence...",
        publication_date=datetime.utcnow() - timedelta(days=60),
    )


@pytest.fixture
def blocked_domain_source():
    """Create a source from a blocked domain."""
    return SourceMetadata(
        url="https://example.com/fake-news",
        title="Definitely Real News",
        snippet="Trust us...",
        publication_date=datetime.utcnow(),
    )


# ============================================================================
# SourceMetadata Tests
# ============================================================================

class TestSourceMetadata:
    """Tests for SourceMetadata model."""
    
    def test_url_validation_adds_https(self):
        """URLs without scheme should get https:// added."""
        source = SourceMetadata(
            url="arxiv.org/abs/12345",
            title="Test"
        )
        assert source.url.startswith("https://")
    
    def test_url_validation_preserves_existing_scheme(self):
        """URLs with scheme should be preserved."""
        source = SourceMetadata(
            url="http://legacy-site.com/page",
            title="Test"
        )
        assert source.url.startswith("http://")
    
    def test_extract_domain(self):
        """Domain extraction from URL works correctly."""
        source = SourceMetadata(
            url="https://www.arxiv.org/abs/12345",
            title="Test"
        )
        assert source.extract_domain() == "arxiv.org"
    
    def test_extract_domain_without_www(self):
        """Domain extraction removes www prefix."""
        source = SourceMetadata(
            url="https://www.nature.com/articles/123",
            title="Test"
        )
        assert source.extract_domain() == "nature.com"
    
    def test_empty_url_raises_error(self):
        """Empty URL should raise validation error."""
        with pytest.raises(ValueError):
            SourceMetadata(url="", title="Test")


# ============================================================================
# CredibilityScores Tests
# ============================================================================

class TestCredibilityScores:
    """Tests for CredibilityScores model."""
    
    def test_calculate_overall_default_weights(self):
        """Overall score calculation with default weights."""
        scores = CredibilityScores(
            authority=80,
            recency=60,
            objectivity=70,
            corroboration=50
        )
        # Expected: 80*0.35 + 60*0.25 + 70*0.25 + 50*0.15 = 28 + 15 + 17.5 + 7.5 = 68
        assert scores.calculate_overall() == 68
    
    def test_calculate_overall_custom_weights(self):
        """Overall score calculation with custom weights."""
        scores = CredibilityScores(
            authority=100,
            recency=100,
            objectivity=100,
            corroboration=100
        )
        custom_weights = {
            "authority": 0.25,
            "recency": 0.25,
            "objectivity": 0.25,
            "corroboration": 0.25
        }
        assert scores.calculate_overall(custom_weights) == 100
    
    def test_score_bounds(self):
        """Scores must be between 0 and 100."""
        # Valid scores
        valid = CredibilityScores(
            authority=0,
            recency=100,
            objectivity=50,
            corroboration=75
        )
        assert valid.authority == 0
        assert valid.recency == 100
        
        # Invalid scores should raise
        with pytest.raises(ValueError):
            CredibilityScores(authority=-10, recency=50, objectivity=50, corroboration=50)
        
        with pytest.raises(ValueError):
            CredibilityScores(authority=50, recency=150, objectivity=50, corroboration=50)


# ============================================================================
# DomainClassifier Tests
# ============================================================================

class TestDomainClassifier:
    """Tests for DomainClassifier."""
    
    def test_classify_academic_domain(self, domain_classifier):
        """Academic domains should be classified correctly."""
        category, adjustment = domain_classifier.classify_domain("arxiv.org")
        assert category == DomainCategory.ACADEMIC
        assert adjustment > 0  # Should have positive bonus
    
    def test_classify_government_domain(self, domain_classifier):
        """Government domains should be classified correctly."""
        category, adjustment = domain_classifier.classify_domain("cdc.gov")
        assert category == DomainCategory.GOVERNMENT
        assert adjustment > 0
    
    def test_classify_government_tld(self, domain_classifier):
        """Domains ending in .gov should be classified as government."""
        category, adjustment = domain_classifier.classify_domain("health.gov")
        assert category == DomainCategory.GOVERNMENT
        assert adjustment > 0
    
    def test_classify_major_news(self, domain_classifier):
        """Major news outlets should be classified correctly."""
        category, adjustment = domain_classifier.classify_domain("reuters.com")
        assert category == DomainCategory.MAJOR_NEWS
        assert adjustment > 0
    
    def test_classify_social_media(self, domain_classifier):
        """Social media should be flagged with penalty."""
        category, adjustment = domain_classifier.classify_domain("twitter.com")
        assert category == DomainCategory.SOCIAL_MEDIA
        assert adjustment < 0  # Should have penalty
    
    def test_classify_user_generated(self, domain_classifier):
        """User-generated content should be flagged."""
        category, adjustment = domain_classifier.classify_domain("medium.com")
        assert category == DomainCategory.USER_GENERATED
        assert adjustment < 0
    
    def test_classify_unknown_domain(self, domain_classifier):
        """Unknown domains should be neutral."""
        category, adjustment = domain_classifier.classify_domain("unknown-site.io")
        assert category == DomainCategory.UNKNOWN
        assert adjustment == 0
    
    def test_is_blocked(self, domain_classifier):
        """Blocked domains should be detected."""
        is_blocked, reason = domain_classifier.is_blocked("example.com")
        assert is_blocked is True
        assert reason is not None
    
    def test_is_not_blocked(self, domain_classifier):
        """Non-blocked domains should pass."""
        is_blocked, reason = domain_classifier.is_blocked("legitimate-site.com")
        assert is_blocked is False
        assert reason is None
    
    def test_recency_fresh(self, domain_classifier):
        """Fresh sources (< 30 days) should get bonus."""
        recent_date = datetime.utcnow() - timedelta(days=10)
        adjustment, label = domain_classifier.get_recency_adjustment(recent_date)
        assert adjustment > 0
        assert label == "fresh"
    
    def test_recency_outdated(self, domain_classifier):
        """Outdated sources (> 2 years) should get penalty."""
        old_date = datetime.utcnow() - timedelta(days=800)
        adjustment, label = domain_classifier.get_recency_adjustment(old_date)
        assert adjustment < 0
        assert label == "outdated"
    
    def test_recency_unknown(self, domain_classifier):
        """Unknown publication date should be neutral."""
        adjustment, label = domain_classifier.get_recency_adjustment(None)
        assert adjustment == 0
        assert label == "unknown"


# ============================================================================
# SourceValidator Tests
# ============================================================================

class TestSourceValidator:
    """Tests for SourceValidator."""
    
    def test_validate_high_quality_source(self, source_validator, high_quality_source):
        """High-quality academic sources should score well."""
        result = source_validator.validate_source(high_quality_source)
        
        assert result.overall_score >= 60
        assert result.credibility_level in (CredibilityLevel.HIGH, CredibilityLevel.MEDIUM)
        assert result.decision == InclusionDecision.INCLUDE
        assert result.domain_category == DomainCategory.ACADEMIC
        assert "⭐" in result.score_badge or "✓" in result.score_badge
    
    def test_validate_government_source(self, source_validator, government_source):
        """Government sources should score well."""
        result = source_validator.validate_source(government_source)
        
        assert result.overall_score >= 60
        assert result.decision == InclusionDecision.INCLUDE
        assert result.domain_category == DomainCategory.GOVERNMENT
    
    def test_validate_outdated_source(self, source_validator, outdated_source):
        """Outdated sources should receive penalties."""
        result = source_validator.validate_source(outdated_source)
        
        # Should have caveat or be excluded due to age
        assert any(
            "outdated" in r.reason_code.lower() or "dated" in r.reason_text.lower()
            for r in result.exclusion_reasons
        )
        assert result.scores.recency < 50
    
    def test_validate_social_media_source(self, source_validator, social_media_source):
        """Social media should receive low scores."""
        result = source_validator.validate_source(social_media_source)
        
        assert result.overall_score < 50
        assert result.credibility_level in (CredibilityLevel.LOW, CredibilityLevel.UNRELIABLE)
        assert result.domain_category == DomainCategory.SOCIAL_MEDIA
    
    def test_validate_blocked_source(self, source_validator, blocked_domain_source):
        """Blocked domains should be excluded."""
        result = source_validator.validate_source(blocked_domain_source)
        
        assert result.decision == InclusionDecision.EXCLUDE
        assert any(r.severity == "critical" for r in result.exclusion_reasons)
        assert any("blocked" in r.reason_code.lower() for r in result.exclusion_reasons)
    
    def test_validate_user_generated_source(self, source_validator, user_generated_source):
        """User-generated content should have caveats."""
        result = source_validator.validate_source(user_generated_source)
        
        assert result.domain_category == DomainCategory.USER_GENERATED
        # Should either be included with caveat or have low objectivity warning
        assert (
            result.decision == InclusionDecision.INCLUDE_WITH_CAVEAT or
            result.scores.objectivity < 50
        )
    
    def test_batch_validation(self, source_validator, high_quality_source, outdated_source, blocked_domain_source):
        """Batch validation should partition sources correctly."""
        sources = [high_quality_source, outdated_source, blocked_domain_source]
        result = source_validator.validate_sources(sources, "test query")
        
        assert result.statistics.total_sources == 3
        assert result.statistics.excluded >= 1  # At least blocked domain
        assert len(result.excluded_sources) >= 1
        assert result.statistics.average_score > 0
    
    def test_batch_validation_empty(self, source_validator):
        """Empty source list should return empty result."""
        result = source_validator.validate_sources([], "test query")
        
        assert result.statistics.total_sources == 0
        assert len(result.included_sources) == 0
        assert len(result.excluded_sources) == 0


# ============================================================================
# ValidationResult Tests
# ============================================================================

class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_get_usable_sources(self, source_validator, high_quality_source, user_generated_source):
        """get_usable_sources should return include + caveat sources."""
        sources = [high_quality_source, user_generated_source]
        result = source_validator.validate_sources(sources)
        
        usable = result.get_usable_sources()
        assert len(usable) == len(result.included_sources) + len(result.caveat_sources)
    
    def test_get_top_sources(self, source_validator, high_quality_source, government_source):
        """get_top_sources should return highest scoring sources."""
        sources = [high_quality_source, government_source]
        result = source_validator.validate_sources(sources)
        
        top = result.get_top_sources(1)
        assert len(top) <= 1
        if len(top) > 0:
            # Top source should have highest score
            all_usable = result.get_usable_sources()
            max_score = max(s.overall_score for s in all_usable)
            assert top[0].overall_score == max_score
    
    def test_to_search_results(self, source_validator, high_quality_source):
        """to_search_results should convert to dict format."""
        result = source_validator.validate_sources([high_quality_source])
        
        search_results = result.to_search_results()
        assert len(search_results) > 0
        
        first = search_results[0]
        assert "url" in first
        assert "credibility_score" in first
        assert "credibility_badge" in first


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the validation pipeline."""
    
    def test_validate_search_results_function(self):
        """Test the convenience function for validating search results."""
        raw_results = [
            {"url": "https://nature.com/article", "title": "Nature Article", "snippet": "..."},
            {"url": "https://reddit.com/r/topic", "title": "Reddit Post", "snippet": "..."},
        ]
        
        validated, stats = validate_search_results(raw_results, "science query")
        
        assert stats.total_sources == 2
        assert len(validated) <= 2  # May have excluded some
        
        # Check that credibility metadata is added
        for result in validated:
            assert "credibility_score" in result
            assert "credibility_badge" in result
    
    def test_factory_functions(self):
        """Test factory functions return valid instances."""
        classifier = get_domain_classifier()
        validator = get_source_validator()
        
        assert isinstance(classifier, DomainClassifier)
        assert isinstance(validator, SourceValidator)
    
    def test_domain_classifier_handles_missing_config(self, tmp_path):
        """Classifier should handle missing config file gracefully."""
        # Create classifier pointing to non-existent config
        classifier = DomainClassifier(config_path=tmp_path / "nonexistent.json")
        
        # Should still work with defaults
        category, adjustment = classifier.classify_domain("unknown.com")
        assert category == DomainCategory.UNKNOWN
        assert adjustment == 0


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_malformed_url(self, source_validator):
        """Malformed URLs should be handled gracefully."""
        source = SourceMetadata(
            url="not-a-valid-url",
            title="Test"
        )
        # Should not raise, but may have low score
        result = source_validator.validate_source(source)
        assert result is not None
    
    def test_unicode_in_title(self, source_validator):
        """Unicode characters in title should be handled."""
        source = SourceMetadata(
            url="https://example.org/article",
            title="研究報告 - Technical Analysis 📊",
            snippet="Mixed language content..."
        )
        result = source_validator.validate_source(source)
        assert result is not None
    
    def test_very_long_url(self, source_validator):
        """Very long URLs should be handled."""
        long_path = "a" * 1000
        source = SourceMetadata(
            url=f"https://example.org/{long_path}",
            title="Test"
        )
        result = source_validator.validate_source(source)
        assert result is not None
    
    def test_future_publication_date(self, source_validator):
        """Future publication dates should not crash."""
        source = SourceMetadata(
            url="https://example.org/future",
            title="Future Article",
            publication_date=datetime.utcnow() + timedelta(days=30)
        )
        result = source_validator.validate_source(source)
        assert result is not None
        # Should get fresh/recent bonus (negative days = very recent)


# ============================================================================
# Score Badge Tests
# ============================================================================

class TestScoreBadges:
    """Tests for score badge generation."""
    
    def test_high_credibility_badge(self, source_validator, high_quality_source):
        """High credibility sources should get star badge."""
        result = source_validator.validate_source(high_quality_source)
        if result.credibility_level == CredibilityLevel.HIGH:
            assert "⭐" in result.score_badge
    
    def test_low_credibility_badge(self, source_validator, social_media_source):
        """Low credibility sources should get warning badge."""
        result = source_validator.validate_source(social_media_source)
        if result.credibility_level == CredibilityLevel.LOW:
            assert "⚠️" in result.score_badge
        elif result.credibility_level == CredibilityLevel.UNRELIABLE:
            assert "❌" in result.score_badge
    
    def test_badge_contains_score(self, source_validator, high_quality_source):
        """Badge should contain the numeric score."""
        result = source_validator.validate_source(high_quality_source)
        assert str(result.overall_score) in result.score_badge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
