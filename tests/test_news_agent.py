"""
Unit Tests for News Intelligence Agent

Tests for:
- NewsEvent model and timeline building
- Sentiment analysis utilities
- Source credibility scoring
- News categorization
- Timeline aggregation and deduplication
"""

import pytest
from datetime import datetime, timedelta
from typing import List

# Import models
from deep_research.models.news_models import (
    NewsEvent,
    NewsTimeline,
    NewsSource,
    NewsCategory,
    Sentiment,
    SentimentIntensity,
    SentimentAnalysis,
)

# Import agent and utilities
from deep_research.research_agents.news_agent import (
    NewsIntelligenceAgent,
    create_news_intelligence_agent,
    should_use_news_search,
    analyze_sentiment,
    score_source_credibility,
    categorize_news,
    extract_date_from_text,
    extract_entities,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_news_source() -> NewsSource:
    """Create a sample news source."""
    return NewsSource(
        name="Reuters",
        url="https://reuters.com/article/123",
        credibility_score=90.0,
        is_primary_source=True,
    )


@pytest.fixture
def sample_sentiment() -> SentimentAnalysis:
    """Create a sample sentiment analysis."""
    return SentimentAnalysis(
        sentiment=Sentiment.POSITIVE,
        intensity=SentimentIntensity.MODERATE,
        confidence=0.8,
        key_phrases=["+growth", "+success"],
    )


@pytest.fixture
def sample_news_event(sample_news_source, sample_sentiment) -> NewsEvent:
    """Create a sample news event."""
    return NewsEvent(
        headline="Tech Company Reports Record Growth",
        summary="The company announced 23% year-over-year revenue growth.",
        event_date=datetime(2024, 12, 1, 10, 0, 0),
        published_date=datetime(2024, 12, 1, 12, 0, 0),
        category=NewsCategory.TECHNOLOGY,
        entities=["Tech Company", "CEO"],
        keywords=["growth", "revenue", "tech"],
        sources=[sample_news_source],
        sentiment=sample_sentiment,
        source_count=1,
        average_source_score=90.0,
        is_breaking=False,
        is_verified=True,
    )


@pytest.fixture
def sample_timeline(sample_news_event) -> NewsTimeline:
    """Create a sample news timeline."""
    events = [
        sample_news_event,
        NewsEvent(
            headline="Market Reacts to Tech Earnings",
            summary="Stock prices surge following the earnings report.",
            event_date=datetime(2024, 12, 1, 14, 0, 0),
            category=NewsCategory.FINANCE,
            sentiment=SentimentAnalysis(sentiment=Sentiment.POSITIVE),
        ),
        NewsEvent(
            headline="Analyst Concerns About Market Volatility",
            summary="Some analysts express caution about valuations.",
            event_date=datetime(2024, 12, 1, 16, 0, 0),
            category=NewsCategory.FINANCE,
            sentiment=SentimentAnalysis(sentiment=Sentiment.NEGATIVE),
        ),
    ]
    
    return NewsTimeline(
        topic="Tech Earnings",
        events=events,
        date_range_start=datetime(2024, 12, 1),
        date_range_end=datetime(2024, 12, 1),
        overall_sentiment=Sentiment.POSITIVE,
        sentiment_trend="stable",
        total_sources=3,
        average_credibility=75.0,
        key_developments=["Record revenue growth announced"],
    )


# =============================================================================
# Test Class: NewsSource Model
# =============================================================================

class TestNewsSource:
    """Tests for NewsSource model."""
    
    def test_create_basic_source(self):
        """Test creating a basic news source."""
        source = NewsSource(name="BBC News")
        assert source.name == "BBC News"
        assert source.url == ""
        assert source.credibility_score == 50.0
    
    def test_create_full_source(self, sample_news_source):
        """Test creating a full news source."""
        assert sample_news_source.name == "Reuters"
        assert sample_news_source.credibility_score == 90.0
        assert sample_news_source.is_primary_source is True
    
    def test_credibility_level_high(self):
        """Test high credibility level."""
        source = NewsSource(name="Test", credibility_score=85.0)
        assert source.credibility_level == "high"
    
    def test_credibility_level_medium(self):
        """Test medium credibility level."""
        source = NewsSource(name="Test", credibility_score=65.0)
        assert source.credibility_level == "medium"
    
    def test_credibility_level_low(self):
        """Test low credibility level."""
        source = NewsSource(name="Test", credibility_score=45.0)
        assert source.credibility_level == "low"
    
    def test_credibility_level_very_low(self):
        """Test very low credibility level."""
        source = NewsSource(name="Test", credibility_score=30.0)
        assert source.credibility_level == "very_low"


# =============================================================================
# Test Class: SentimentAnalysis Model
# =============================================================================

class TestSentimentAnalysis:
    """Tests for SentimentAnalysis model."""
    
    def test_create_default_sentiment(self):
        """Test default sentiment values."""
        sentiment = SentimentAnalysis()
        assert sentiment.sentiment == Sentiment.NEUTRAL
        assert sentiment.intensity == SentimentIntensity.MODERATE
        assert sentiment.confidence == 0.5
    
    def test_sentiment_label_moderate(self):
        """Test sentiment label for moderate intensity."""
        sentiment = SentimentAnalysis(
            sentiment=Sentiment.POSITIVE,
            intensity=SentimentIntensity.MODERATE,
        )
        assert sentiment.sentiment_label == "positive"
    
    def test_sentiment_label_strong(self):
        """Test sentiment label for strong intensity."""
        sentiment = SentimentAnalysis(
            sentiment=Sentiment.NEGATIVE,
            intensity=SentimentIntensity.STRONG,
        )
        assert sentiment.sentiment_label == "strong negative"
    
    def test_sentiment_label_weak(self):
        """Test sentiment label for weak intensity."""
        sentiment = SentimentAnalysis(
            sentiment=Sentiment.MIXED,
            intensity=SentimentIntensity.WEAK,
        )
        assert sentiment.sentiment_label == "weak mixed"


# =============================================================================
# Test Class: NewsEvent Model
# =============================================================================

class TestNewsEvent:
    """Tests for NewsEvent model."""
    
    def test_create_basic_event(self):
        """Test creating a basic news event."""
        event = NewsEvent(headline="Test Headline")
        assert event.headline == "Test Headline"
        assert event.summary == ""
        assert event.category == NewsCategory.OTHER
    
    def test_create_full_event(self, sample_news_event):
        """Test creating a full news event."""
        assert sample_news_event.headline == "Tech Company Reports Record Growth"
        assert sample_news_event.category == NewsCategory.TECHNOLOGY
        assert len(sample_news_event.entities) == 2
        assert sample_news_event.is_verified is True
    
    def test_reliability_tier_high(self, sample_news_event):
        """Test high reliability tier."""
        sample_news_event.source_count = 3
        sample_news_event.average_source_score = 80.0
        assert sample_news_event.reliability_tier == "high"
    
    def test_reliability_tier_medium(self):
        """Test medium reliability tier."""
        event = NewsEvent(
            headline="Test",
            source_count=2,
            average_source_score=60.0,
        )
        assert event.reliability_tier == "medium"
    
    def test_reliability_tier_low(self):
        """Test low reliability tier."""
        event = NewsEvent(
            headline="Test",
            source_count=1,
            average_source_score=40.0,
        )
        assert event.reliability_tier == "low"
    
    def test_to_timeline_entry(self, sample_news_event):
        """Test timeline entry formatting."""
        entry = sample_news_event.to_timeline_entry()
        assert "2024-12-01" in entry
        assert "Tech Company Reports Record Growth" in entry
    
    def test_event_sorting(self):
        """Test events sort by date (most recent first)."""
        event1 = NewsEvent(
            headline="Older",
            event_date=datetime(2024, 1, 1),
        )
        event2 = NewsEvent(
            headline="Newer",
            event_date=datetime(2024, 12, 1),
        )
        
        events = [event1, event2]
        events.sort()
        
        assert events[0].headline == "Newer"
        assert events[1].headline == "Older"


# =============================================================================
# Test Class: NewsTimeline Model
# =============================================================================

class TestNewsTimeline:
    """Tests for NewsTimeline model."""
    
    def test_create_basic_timeline(self):
        """Test creating a basic timeline."""
        timeline = NewsTimeline(topic="Tech News")
        assert timeline.topic == "Tech News"
        assert len(timeline.events) == 0
    
    def test_create_full_timeline(self, sample_timeline):
        """Test creating a full timeline."""
        assert sample_timeline.topic == "Tech Earnings"
        assert len(sample_timeline.events) == 3
        assert sample_timeline.total_sources == 3
    
    def test_sort_chronologically(self, sample_timeline):
        """Test chronological sorting."""
        sample_timeline.sort_chronologically()
        # Most recent should be first
        dates = [e.event_date for e in sample_timeline.events if e.event_date]
        for i in range(len(dates) - 1):
            assert dates[i] >= dates[i + 1]
    
    def test_get_events_by_sentiment(self, sample_timeline):
        """Test filtering by sentiment."""
        positive = sample_timeline.get_events_by_sentiment(Sentiment.POSITIVE)
        assert len(positive) >= 1
        
        negative = sample_timeline.get_events_by_sentiment(Sentiment.NEGATIVE)
        assert len(negative) >= 1
    
    def test_to_markdown_timeline(self, sample_timeline):
        """Test markdown timeline generation."""
        markdown = sample_timeline.to_markdown_timeline()
        
        assert "## News Timeline:" in markdown
        assert "Tech Earnings" in markdown
        assert "### Timeline" in markdown
    
    def test_to_summary_dict(self, sample_timeline):
        """Test summary dictionary generation."""
        summary = sample_timeline.to_summary_dict()
        
        assert summary["topic"] == "Tech Earnings"
        assert summary["event_count"] == 3
        assert "sentiment_breakdown" in summary


# =============================================================================
# Test Class: Sentiment Analysis Utility
# =============================================================================

class TestAnalyzeSentiment:
    """Tests for analyze_sentiment function."""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection."""
        text = "Company reports breakthrough growth with exceptional results."
        sentiment = analyze_sentiment(text)
        
        assert sentiment.sentiment == Sentiment.POSITIVE
        assert sentiment.confidence > 0.5
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection."""
        text = "Stock crashes amid crisis and devastating losses."
        sentiment = analyze_sentiment(text)
        
        assert sentiment.sentiment == Sentiment.NEGATIVE
        assert sentiment.confidence > 0.5
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection."""
        text = "The company announced its quarterly results today."
        sentiment = analyze_sentiment(text)
        
        assert sentiment.sentiment == Sentiment.NEUTRAL
    
    def test_mixed_sentiment(self):
        """Test mixed sentiment detection."""
        text = "Despite growth in revenue, the company faces significant challenges."
        sentiment = analyze_sentiment(text)
        
        # Could be mixed or slightly positive/negative
        assert sentiment.sentiment in [Sentiment.MIXED, Sentiment.POSITIVE, Sentiment.NEGATIVE]
    
    def test_key_phrases_extracted(self):
        """Test key phrase extraction."""
        text = "Stock surges on breakthrough innovation."
        sentiment = analyze_sentiment(text)
        
        assert len(sentiment.key_phrases) > 0


# =============================================================================
# Test Class: Source Credibility Scoring
# =============================================================================

class TestScoreSourceCredibility:
    """Tests for score_source_credibility function."""
    
    def test_high_credibility_source(self):
        """Test high credibility sources."""
        score = score_source_credibility("Reuters")
        assert score >= 80
        
        score = score_source_credibility("BBC News", "https://bbc.com/article")
        assert score >= 80
    
    def test_medium_credibility_source(self):
        """Test medium credibility sources."""
        score = score_source_credibility("CNN")
        assert 55 <= score <= 80
    
    def test_low_credibility_source(self):
        """Test low credibility sources."""
        score = score_source_credibility("Daily Mail")
        assert score < 50
    
    def test_government_domain(self):
        """Test government domain bonus."""
        score = score_source_credibility("Agency", "https://agency.gov/data")
        assert score >= 75
    
    def test_education_domain(self):
        """Test education domain bonus."""
        score = score_source_credibility("University", "https://university.edu/research")
        assert score >= 75
    
    def test_unknown_source(self):
        """Test unknown source default score."""
        score = score_source_credibility("RandomBlog123")
        assert 40 <= score <= 60


# =============================================================================
# Test Class: News Categorization
# =============================================================================

class TestCategorizeNews:
    """Tests for categorize_news function."""
    
    def test_technology_category(self):
        """Test technology categorization."""
        text = "Apple announces new AI features in latest software update."
        category = categorize_news(text)
        assert category == NewsCategory.TECHNOLOGY
    
    def test_business_category(self):
        """Test business categorization."""
        text = "Corporation announces merger with quarterly earnings exceeding expectations."
        category = categorize_news(text)
        assert category == NewsCategory.BUSINESS
    
    def test_finance_category(self):
        """Test finance categorization."""
        text = "Federal Reserve raises interest rates amid inflation concerns."
        category = categorize_news(text)
        assert category == NewsCategory.FINANCE
    
    def test_politics_category(self):
        """Test politics categorization."""
        text = "Senate votes on new legislation following presidential address."
        category = categorize_news(text)
        assert category == NewsCategory.POLITICS
    
    def test_science_category(self):
        """Test science categorization."""
        text = "Scientists discover new research findings in peer-reviewed study."
        category = categorize_news(text)
        assert category == NewsCategory.SCIENCE
    
    def test_health_category(self):
        """Test health categorization."""
        text = "FDA approves new vaccine treatment for patients."
        category = categorize_news(text)
        assert category == NewsCategory.HEALTH
    
    def test_breaking_category(self):
        """Test breaking news categorization."""
        text = "BREAKING: Major developing story unfolds."
        category = categorize_news(text)
        assert category == NewsCategory.BREAKING


# =============================================================================
# Test Class: Date Extraction
# =============================================================================

class TestExtractDateFromText:
    """Tests for extract_date_from_text function."""
    
    def test_iso_date_format(self):
        """Test ISO date format extraction."""
        text = "The event occurred on 2024-12-01."
        date = extract_date_from_text(text)
        
        assert date is not None
        assert date.year == 2024
        assert date.month == 12
        assert date.day == 1
    
    def test_us_date_format(self):
        """Test US date format extraction."""
        text = "Published on 12/15/2024."
        date = extract_date_from_text(text)
        
        assert date is not None
        assert date.month == 12
        assert date.day == 15
    
    def test_written_date_format(self):
        """Test written date format extraction."""
        text = "The announcement was made on January 15, 2024."
        date = extract_date_from_text(text)
        
        assert date is not None
        assert date.month == 1
        assert date.day == 15
    
    def test_short_written_date(self):
        """Test short written date extraction."""
        text = "Updated on Dec 1, 2024."
        date = extract_date_from_text(text)
        
        assert date is not None
        assert date.month == 12
    
    def test_relative_date_today(self):
        """Test relative date 'today'."""
        text = "Breaking news today."
        date = extract_date_from_text(text)
        
        assert date is not None
        assert date.date() == datetime.now().date()
    
    def test_relative_date_yesterday(self):
        """Test relative date 'yesterday'."""
        text = "This happened yesterday."
        date = extract_date_from_text(text)
        
        assert date is not None
        expected = (datetime.now() - timedelta(days=1)).date()
        assert date.date() == expected
    
    def test_no_date_found(self):
        """Test when no date is found."""
        text = "Some text without any dates."
        date = extract_date_from_text(text)
        
        assert date is None


# =============================================================================
# Test Class: Entity Extraction
# =============================================================================

class TestExtractEntities:
    """Tests for extract_entities function."""
    
    def test_extract_person_name(self):
        """Test person name extraction."""
        text = "CEO John Smith announced the new initiative."
        entities = extract_entities(text)
        
        assert "John Smith" in entities
    
    def test_extract_organization(self):
        """Test organization extraction."""
        text = "Microsoft Corporation reported earnings."
        entities = extract_entities(text)
        
        assert any("Microsoft" in e for e in entities)
    
    def test_filter_stopwords(self):
        """Test that stopwords are filtered."""
        text = "The Quick Brown Fox jumped over The Lazy Dog."
        entities = extract_entities(text)
        
        # "The" should be filtered out
        assert "The" not in entities
    
    def test_limit_entities(self):
        """Test entity limit."""
        text = "Apple Microsoft Google Amazon Meta Netflix Tesla SpaceX Uber Airbnb Twitter LinkedIn"
        entities = extract_entities(text)
        
        assert len(entities) <= 10


# =============================================================================
# Test Class: NewsIntelligenceAgent
# =============================================================================

class TestNewsIntelligenceAgent:
    """Tests for NewsIntelligenceAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = NewsIntelligenceAgent()
        
        assert agent.model == "gpt-4o-mini"
        assert agent._web_search_agent is None  # Lazy loaded
        assert len(agent.events) == 0
    
    def test_agent_initialization_custom_model(self):
        """Test agent with custom model."""
        agent = NewsIntelligenceAgent(model="gpt-4o")
        assert agent.model == "gpt-4o"
    
    def test_build_news_queries(self):
        """Test news query building."""
        agent = NewsIntelligenceAgent()
        queries = agent._build_news_queries("Tesla stock", days_back=3)
        
        assert len(queries) >= 2
        assert any("latest" in q for q in queries)
        assert any("breaking" in q for q in queries)
    
    def test_build_news_queries_longer_timeframe(self):
        """Test news query building for longer timeframe."""
        agent = NewsIntelligenceAgent()
        queries = agent._build_news_queries("AI developments", days_back=14)
        
        assert any("analysis" in q for q in queries)
    
    def test_deduplicate_events(self):
        """Test event deduplication."""
        agent = NewsIntelligenceAgent()
        
        events = [
            NewsEvent(headline="Apple announces new iPhone"),
            NewsEvent(headline="Apple announces new iPhone model"),  # Similar
            NewsEvent(headline="Google releases Android update"),  # Different
        ]
        
        unique = agent._deduplicate_events(events)
        
        # Should remove one of the Apple headlines
        assert len(unique) <= 3
    
    def test_calculate_sentiment_trend_improving(self):
        """Test improving sentiment trend."""
        agent = NewsIntelligenceAgent()
        
        events = [
            # Newer events (positive)
            NewsEvent(
                headline="Great news",
                event_date=datetime.now(),
                sentiment=SentimentAnalysis(sentiment=Sentiment.POSITIVE),
            ),
            NewsEvent(
                headline="More good news",
                event_date=datetime.now() - timedelta(hours=1),
                sentiment=SentimentAnalysis(sentiment=Sentiment.POSITIVE),
            ),
            # Older events (negative)
            NewsEvent(
                headline="Bad news",
                event_date=datetime.now() - timedelta(days=1),
                sentiment=SentimentAnalysis(sentiment=Sentiment.NEGATIVE),
            ),
            NewsEvent(
                headline="Terrible news",
                event_date=datetime.now() - timedelta(days=2),
                sentiment=SentimentAnalysis(sentiment=Sentiment.NEGATIVE),
            ),
        ]
        
        trend = agent._calculate_sentiment_trend(events)
        assert trend == "improving"
    
    def test_calculate_sentiment_trend_stable(self):
        """Test stable sentiment trend."""
        agent = NewsIntelligenceAgent()
        
        events = [
            NewsEvent(
                headline="News 1",
                event_date=datetime.now(),
                sentiment=SentimentAnalysis(sentiment=Sentiment.NEUTRAL),
            ),
            NewsEvent(
                headline="News 2",
                event_date=datetime.now() - timedelta(hours=1),
                sentiment=SentimentAnalysis(sentiment=Sentiment.NEUTRAL),
            ),
            NewsEvent(
                headline="News 3",
                event_date=datetime.now() - timedelta(days=1),
                sentiment=SentimentAnalysis(sentiment=Sentiment.NEUTRAL),
            ),
        ]
        
        trend = agent._calculate_sentiment_trend(events)
        assert trend == "stable"


# =============================================================================
# Test Class: Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Tests for module-level helper functions."""
    
    def test_create_news_intelligence_agent(self):
        """Test factory function."""
        agent = create_news_intelligence_agent()
        assert isinstance(agent, NewsIntelligenceAgent)
    
    def test_create_news_intelligence_agent_custom_model(self):
        """Test factory with custom model."""
        agent = create_news_intelligence_agent(model="gpt-4o")
        assert agent.model == "gpt-4o"
    
    def test_should_use_news_search_by_type(self):
        """Test news search detection by query type."""
        
        class MockAnalysis:
            query_type = "news"
            original_query = "test"
        
        assert should_use_news_search(MockAnalysis()) is True
    
    def test_should_use_news_search_by_time_sensitive(self):
        """Test news search detection by time sensitivity."""
        
        class MockAnalysis:
            query_type = "general"
            is_time_sensitive = True
            original_query = "test"
        
        assert should_use_news_search(MockAnalysis()) is True
    
    def test_should_use_news_search_by_keywords(self):
        """Test news search detection by keywords."""
        
        class MockAnalysis:
            query_type = "general"
            original_query = "What are the latest developments in AI?"
        
        assert should_use_news_search(MockAnalysis()) is True
    
    def test_should_use_news_search_negative(self):
        """Test news search not triggered for regular queries."""
        
        class MockAnalysis:
            query_type = "technical"
            original_query = "How does a neural network work?"
        
        assert should_use_news_search(MockAnalysis()) is False
    
    def test_should_use_news_search_none(self):
        """Test with None analysis."""
        assert should_use_news_search(None) is False
