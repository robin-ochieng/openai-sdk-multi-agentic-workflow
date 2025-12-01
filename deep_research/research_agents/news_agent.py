"""
News Intelligence Agent for Deep Research.

Aggregates real-time news via WebSearchTool with focus on timelines.
Outputs chronological events with sentiment analysis and source scoring.

Features:
- Timeline-focused news aggregation
- Sentiment analysis for each event
- Source credibility scoring
- Trend detection and key development extraction
"""

import os
import re
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from agents import Agent, Runner, WebSearchTool

from deep_research.models.news_models import (
    NewsEvent,
    NewsTimeline,
    NewsSource,
    NewsCategory,
    Sentiment,
    SentimentIntensity,
    SentimentAnalysis,
)


# Configure logging
logger = logging.getLogger("deep_research.news_agent")


# =============================================================================
# Sentiment Analysis Utilities
# =============================================================================

# Sentiment keyword patterns
POSITIVE_KEYWORDS = {
    "strong": [
        "breakthrough", "triumph", "soaring", "surges", "skyrockets",
        "historic", "exceptional", "remarkable", "outstanding", "excellent",
    ],
    "moderate": [
        "growth", "gains", "improves", "advances", "success", "positive",
        "progress", "boost", "rises", "increases", "wins", "achieves",
    ],
    "weak": [
        "stable", "steady", "maintains", "holds", "continues", "supports",
    ],
}

NEGATIVE_KEYWORDS = {
    "strong": [
        "crash", "collapse", "crisis", "disaster", "catastrophe", "plummets",
        "devastating", "severe", "critical", "emergency", "scandal",
    ],
    "moderate": [
        "decline", "falls", "drops", "losses", "concerns", "struggles",
        "challenges", "difficulties", "issues", "problems", "risks",
    ],
    "weak": [
        "slows", "uncertain", "mixed", "cautious", "wary", "hesitant",
    ],
}

# Source credibility patterns (simplified scoring)
HIGH_CREDIBILITY_SOURCES = [
    "reuters", "associated press", "ap news", "bbc", "npr", "pbs",
    "wall street journal", "wsj", "financial times", "ft.com",
    "the economist", "bloomberg", "nature", "science",
    "new york times", "washington post", "guardian",
]

MEDIUM_CREDIBILITY_SOURCES = [
    "cnn", "msnbc", "fox news", "abc news", "cbs news", "nbc news",
    "usa today", "time", "newsweek", "forbes", "business insider",
    "techcrunch", "wired", "the verge", "ars technica",
]

LOW_CREDIBILITY_SOURCES = [
    "buzzfeed", "huffpost", "daily mail", "sun", "mirror",
    "tabloid", "gossip", "rumor",
]


def analyze_sentiment(text: str) -> SentimentAnalysis:
    """
    Analyze sentiment of text using keyword matching.
    
    Args:
        text: Text to analyze.
        
    Returns:
        SentimentAnalysis with classification and confidence.
    """
    text_lower = text.lower()
    
    positive_score = 0.0
    negative_score = 0.0
    key_phrases = []
    
    # Check positive keywords
    for intensity, keywords in POSITIVE_KEYWORDS.items():
        weight = {"strong": 3.0, "moderate": 2.0, "weak": 1.0}[intensity]
        for keyword in keywords:
            if keyword in text_lower:
                positive_score += weight
                key_phrases.append(f"+{keyword}")
    
    # Check negative keywords
    for intensity, keywords in NEGATIVE_KEYWORDS.items():
        weight = {"strong": 3.0, "moderate": 2.0, "weak": 1.0}[intensity]
        for keyword in keywords:
            if keyword in text_lower:
                negative_score += weight
                key_phrases.append(f"-{keyword}")
    
    # Determine overall sentiment
    total = positive_score + negative_score
    if total == 0:
        sentiment = Sentiment.NEUTRAL
        intensity = SentimentIntensity.WEAK
        confidence = 0.3
    elif positive_score > negative_score * 2:
        sentiment = Sentiment.POSITIVE
        intensity = SentimentIntensity.STRONG if positive_score > 6 else SentimentIntensity.MODERATE
        confidence = min(0.9, positive_score / (total + 1) * 0.9)
    elif negative_score > positive_score * 2:
        sentiment = Sentiment.NEGATIVE
        intensity = SentimentIntensity.STRONG if negative_score > 6 else SentimentIntensity.MODERATE
        confidence = min(0.9, negative_score / (total + 1) * 0.9)
    elif abs(positive_score - negative_score) < 2:
        sentiment = Sentiment.MIXED
        intensity = SentimentIntensity.MODERATE
        confidence = 0.6
    elif positive_score > negative_score:
        sentiment = Sentiment.POSITIVE
        intensity = SentimentIntensity.WEAK
        confidence = 0.5
    else:
        sentiment = Sentiment.NEGATIVE
        intensity = SentimentIntensity.WEAK
        confidence = 0.5
    
    return SentimentAnalysis(
        sentiment=sentiment,
        intensity=intensity,
        confidence=confidence,
        key_phrases=key_phrases[:5],  # Limit to top 5
    )


def score_source_credibility(source_name: str, url: str = "") -> float:
    """
    Score source credibility based on name patterns.
    
    Args:
        source_name: Name of the source.
        url: URL of the source.
        
    Returns:
        Credibility score from 0-100.
    """
    name_lower = source_name.lower()
    url_lower = url.lower()
    combined = f"{name_lower} {url_lower}"
    
    # Check high credibility sources
    for source in HIGH_CREDIBILITY_SOURCES:
        if source in combined:
            return 85.0 + (hash(source) % 10)  # 85-95
    
    # Check medium credibility sources
    for source in MEDIUM_CREDIBILITY_SOURCES:
        if source in combined:
            return 60.0 + (hash(source) % 15)  # 60-75
    
    # Check low credibility sources
    for source in LOW_CREDIBILITY_SOURCES:
        if source in combined:
            return 30.0 + (hash(source) % 10)  # 30-40
    
    # Check for government/edu domains
    if ".gov" in url_lower or ".edu" in url_lower:
        return 80.0
    
    # Check for org domains
    if ".org" in url_lower:
        return 65.0
    
    # Default score for unknown sources
    return 50.0


def categorize_news(text: str, keywords: List[str] = None) -> NewsCategory:
    """
    Categorize news content based on text analysis.
    
    Args:
        text: Text to categorize.
        keywords: Optional keywords to help categorization.
        
    Returns:
        NewsCategory enum value.
    """
    text_lower = text.lower()
    
    category_patterns = {
        NewsCategory.TECHNOLOGY: [
            "tech", "software", "hardware", "ai", "artificial intelligence",
            "startup", "silicon valley", "apple", "google", "microsoft",
            "innovation", "digital", "cyber", "cloud", "data",
        ],
        NewsCategory.BUSINESS: [
            "company", "corporation", "ceo", "earnings", "revenue",
            "acquisition", "merger", "market", "stock", "investor",
            "profit", "quarterly", "fiscal",
        ],
        NewsCategory.FINANCE: [
            "bank", "banking", "interest rate", "federal reserve", "fed",
            "inflation", "economy", "gdp", "recession", "bond",
            "currency", "forex", "crypto", "bitcoin",
        ],
        NewsCategory.POLITICS: [
            "president", "congress", "senate", "election", "vote",
            "democrat", "republican", "legislation", "bill", "policy",
            "government", "administration", "campaign",
        ],
        NewsCategory.SCIENCE: [
            "research", "study", "scientists", "discovery", "experiment",
            "nasa", "space", "climate", "physics", "biology",
            "laboratory", "journal", "peer-reviewed",
        ],
        NewsCategory.HEALTH: [
            "health", "medical", "doctor", "hospital", "disease",
            "vaccine", "fda", "treatment", "patient", "clinical",
            "pandemic", "covid", "virus",
        ],
        NewsCategory.WORLD: [
            "international", "foreign", "global", "united nations", "un",
            "treaty", "diplomatic", "ambassador", "summit",
        ],
        NewsCategory.BREAKING: [
            "breaking", "just in", "developing", "urgent", "alert",
        ],
    }
    
    scores = {cat: 0 for cat in NewsCategory}
    
    for category, patterns in category_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                scores[category] += 1
    
    # Include keywords in scoring
    if keywords:
        keywords_lower = " ".join(keywords).lower()
        for category, patterns in category_patterns.items():
            for pattern in patterns:
                if pattern in keywords_lower:
                    scores[category] += 0.5
    
    # Get highest scoring category
    best_category = max(scores, key=scores.get)
    
    if scores[best_category] > 0:
        return best_category
    return NewsCategory.OTHER


def extract_date_from_text(text: str) -> Optional[datetime]:
    """
    Extract date from text using common patterns.
    
    Args:
        text: Text containing potential date.
        
    Returns:
        Extracted datetime or None.
    """
    # Common date patterns
    patterns = [
        # ISO format: 2024-01-15
        (r"(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
        # US format: 01/15/2024 or 1/15/2024
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%m/%d/%Y"),
        # Written format: January 15, 2024
        (r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})", None),
        # Short written: Jan 15, 2024
        (r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})", None),
    ]
    
    # Month mapping for written formats
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    
    for pattern, fmt in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if fmt:
                try:
                    return datetime.strptime(match.group(), fmt)
                except ValueError:
                    continue
            else:
                # Handle written format
                month_str = match.group(1).lower()
                day = int(match.group(2))
                year = int(match.group(3))
                month = months.get(month_str, 1)
                try:
                    return datetime(year, month, day)
                except ValueError:
                    continue
    
    # Check for relative dates
    text_lower = text.lower()
    now = datetime.now()
    
    if "today" in text_lower:
        return now
    if "yesterday" in text_lower:
        return now - timedelta(days=1)
    if "last week" in text_lower:
        return now - timedelta(weeks=1)
    if "last month" in text_lower:
        return now - timedelta(days=30)
    
    return None


def extract_entities(text: str) -> List[str]:
    """
    Extract named entities from text using pattern matching.
    
    Simple implementation - in production, use NER model.
    
    Args:
        text: Text to extract entities from.
        
    Returns:
        List of extracted entity names.
    """
    entities = []
    
    # Pattern for capitalized multi-word phrases (potential org/person names)
    # Matches: "Apple Inc.", "John Smith", "United Nations"
    name_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b"
    matches = re.findall(name_pattern, text)
    
    # Filter out common false positives
    stopwords = {
        "The", "This", "That", "These", "Those", "What", "Which",
        "When", "Where", "Why", "How", "For", "And", "But", "Not",
        "From", "With", "About", "After", "Before", "During",
    }
    
    for match in matches:
        if match not in stopwords and len(match) > 2:
            entities.append(match)
    
    # Deduplicate while preserving order
    seen = set()
    unique_entities = []
    for entity in entities:
        if entity not in seen:
            seen.add(entity)
            unique_entities.append(entity)
    
    return unique_entities[:10]  # Limit to top 10


# =============================================================================
# News Intelligence Agent
# =============================================================================

class NewsIntelligenceAgent:
    """
    Agent for real-time news aggregation with timeline focus.
    
    Uses WebSearchTool to fetch recent news and builds chronological
    timelines with sentiment analysis and source scoring.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the news intelligence agent.
        
        Args:
            model: OpenAI model to use for agent.
        """
        self.model = model
        self._web_search_agent: Optional[Agent] = None
        
        # Timeline building
        self.events: List[NewsEvent] = []
        self.sources_seen: Dict[str, NewsSource] = {}
    
    @property
    def web_search_agent(self) -> Agent:
        """Lazy-load web search agent."""
        if self._web_search_agent is None:
            self._web_search_agent = Agent(
                name="NewsSearchAgent",
                instructions="""You are a news search specialist. 
                When searching for news:
                1. Focus on finding recent, timely news articles
                2. Include publication dates when available
                3. Note the source/publication for each result
                4. Capture the main headline and key facts
                5. Look for multiple sources to verify stories
                
                Format each news item clearly with:
                - Source name and URL
                - Publication date if available
                - Headline
                - Key summary points
                """,
                model=self.model,
                tools=[WebSearchTool()],
            )
        return self._web_search_agent
    
    async def search_news(
        self,
        query: str,
        days_back: int = 7,
        max_events: int = 20,
    ) -> NewsTimeline:
        """
        Search for news and build a timeline.
        
        Args:
            query: News search query.
            days_back: How many days back to search.
            max_events: Maximum number of events to return.
            
        Returns:
            NewsTimeline with chronologically ordered events.
        """
        logger.info(f"Searching news for: {query} (last {days_back} days)")
        
        # Reset state
        self.events = []
        self.sources_seen = {}
        
        # Build search queries for different time frames
        search_queries = self._build_news_queries(query, days_back)
        
        # Execute searches
        all_results = []
        for search_query in search_queries:
            try:
                result = await Runner.run(
                    self.web_search_agent,
                    f"Find recent news articles about: {search_query}. "
                    f"Focus on articles from the last {days_back} days. "
                    "Include publication dates, source names, and key facts."
                )
                all_results.append(result.final_output)
            except Exception as e:
                logger.error(f"News search failed for '{search_query}': {e}")
        
        # Parse results into events
        for result_text in all_results:
            events = self._parse_news_results(result_text, query)
            self.events.extend(events)
        
        # Build timeline
        timeline = self._build_timeline(query, max_events)
        
        logger.info(f"Built timeline with {len(timeline.events)} events")
        return timeline
    
    def _build_news_queries(self, query: str, days_back: int) -> List[str]:
        """Build search queries for news coverage."""
        queries = [
            f"{query} latest news",
            f"{query} recent developments",
        ]
        
        # Add breaking news query for very recent searches
        if days_back <= 3:
            queries.append(f"{query} breaking news today")
        
        # Add analysis query for longer timeframes
        if days_back >= 7:
            queries.append(f"{query} news analysis this week")
        
        return queries
    
    def _parse_news_results(self, text: str, topic: str) -> List[NewsEvent]:
        """
        Parse news search results into NewsEvent objects.
        
        Args:
            text: Raw search result text.
            topic: Original search topic.
            
        Returns:
            List of parsed NewsEvent objects.
        """
        events = []
        
        # Split by common separators (numbered items, bullet points, double newlines)
        sections = re.split(r'\n\n+|\d+\.\s+|\n[-•]\s+', text)
        
        for section in sections:
            section = section.strip()
            if len(section) < 50:  # Skip short sections
                continue
            
            # Extract headline (first line or sentence)
            lines = section.split('\n')
            headline = lines[0].strip()
            
            # Clean headline
            headline = re.sub(r'^[\d\.\-\*\•]+\s*', '', headline)  # Remove list markers
            headline = re.sub(r'\*+', '', headline)  # Remove markdown bold
            
            if len(headline) < 10 or len(headline) > 200:
                continue
            
            # Extract summary (remaining text)
            summary = ' '.join(lines[1:]).strip() if len(lines) > 1 else ""
            summary = re.sub(r'\s+', ' ', summary)[:500]  # Clean and limit
            
            # Combine for analysis
            full_text = f"{headline} {summary}"
            
            # Extract date
            event_date = extract_date_from_text(full_text)
            
            # Analyze sentiment
            sentiment = analyze_sentiment(full_text)
            
            # Categorize
            category = categorize_news(full_text)
            
            # Extract entities
            entities = extract_entities(full_text)
            
            # Extract source info from text
            source_info = self._extract_source_from_text(full_text)
            sources = [source_info] if source_info.name != "Unknown Source" else []
            
            # Calculate average source score
            avg_score = (
                sum(s.credibility_score for s in sources) / len(sources)
                if sources else 50.0
            )
            
            event = NewsEvent(
                headline=headline,
                summary=summary,
                event_date=event_date,
                published_date=event_date,  # Use same date if no distinction
                category=category,
                entities=entities,
                keywords=[topic],
                sources=sources,
                sentiment=sentiment,
                source_count=len(sources),
                average_source_score=avg_score,
                is_breaking="breaking" in full_text.lower(),
                is_verified=len(sources) >= 2 and avg_score >= 60,
            )
            
            events.append(event)
        
        return events
    
    def _extract_source_from_text(self, text: str) -> NewsSource:
        """Extract source information from text."""
        # Look for common source patterns
        source_patterns = [
            r'(?:from|source:|via|—)\s*([A-Za-z\s]+(?:News|Times|Post|Journal|Magazine)?)',
            r'\(([A-Za-z\s]+(?:News|Times|Post|Journal))\)',
            r'according to\s+([A-Za-z\s]+)',
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2:
                    score = score_source_credibility(name)
                    return NewsSource(
                        name=name,
                        credibility_score=score,
                    )
        
        # Look for URLs
        url_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.[a-z]+', text)
        if url_match:
            domain = url_match.group(1)
            score = score_source_credibility(domain, url_match.group(0))
            return NewsSource(
                name=domain.title(),
                url=url_match.group(0),
                credibility_score=score,
            )
        
        return NewsSource(name="Unknown Source", credibility_score=40.0)
    
    def _build_timeline(self, topic: str, max_events: int) -> NewsTimeline:
        """Build timeline from collected events."""
        # Deduplicate by headline similarity
        unique_events = self._deduplicate_events(self.events)
        
        # Sort chronologically (most recent first)
        unique_events.sort()
        
        # Limit to max events
        events = unique_events[:max_events]
        
        # Calculate date range
        dated_events = [e for e in events if e.event_date]
        date_start = min(e.event_date for e in dated_events) if dated_events else None
        date_end = max(e.event_date for e in dated_events) if dated_events else None
        
        # Calculate overall sentiment
        sentiment_counts = {s: 0 for s in Sentiment}
        for event in events:
            sentiment_counts[event.sentiment.sentiment] += 1
        
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Determine sentiment trend
        trend = self._calculate_sentiment_trend(events)
        
        # Collect unique sources
        all_sources = set()
        total_score = 0.0
        source_count = 0
        for event in events:
            for source in event.sources:
                if source.name not in all_sources:
                    all_sources.add(source.name)
                    total_score += source.credibility_score
                    source_count += 1
        
        avg_credibility = total_score / source_count if source_count > 0 else 50.0
        
        # Extract key developments (high reliability events)
        key_developments = [
            e.headline for e in events
            if e.reliability_tier == "high" or e.is_breaking
        ][:5]
        
        return NewsTimeline(
            topic=topic,
            events=events,
            date_range_start=date_start,
            date_range_end=date_end,
            overall_sentiment=overall_sentiment,
            sentiment_trend=trend,
            total_sources=len(all_sources),
            average_credibility=avg_credibility,
            key_developments=key_developments,
        )
    
    def _deduplicate_events(self, events: List[NewsEvent]) -> List[NewsEvent]:
        """Remove duplicate events based on headline similarity."""
        unique = []
        seen_headlines = set()
        
        for event in events:
            # Normalize headline for comparison
            normalized = re.sub(r'[^\w\s]', '', event.headline.lower())
            words = set(normalized.split())
            
            # Check if similar headline already exists
            is_duplicate = False
            for seen in seen_headlines:
                seen_words = set(seen.split())
                overlap = len(words & seen_words)
                total = len(words | seen_words)
                if total > 0 and overlap / total > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(event)
                seen_headlines.add(normalized)
        
        return unique
    
    def _calculate_sentiment_trend(self, events: List[NewsEvent]) -> str:
        """Calculate sentiment trend over time."""
        if len(events) < 3:
            return "stable"
        
        # Split events into halves
        mid = len(events) // 2
        first_half = events[mid:]  # Older events (sorted most recent first)
        second_half = events[:mid]  # Newer events
        
        def sentiment_score(evt: NewsEvent) -> float:
            scores = {
                Sentiment.POSITIVE: 1.0,
                Sentiment.NEUTRAL: 0.0,
                Sentiment.MIXED: 0.0,
                Sentiment.NEGATIVE: -1.0,
            }
            return scores.get(evt.sentiment.sentiment, 0.0)
        
        first_avg = sum(sentiment_score(e) for e in first_half) / len(first_half)
        second_avg = sum(sentiment_score(e) for e in second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        elif abs(first_avg) > 0.5 and abs(second_avg) > 0.5 and (first_avg * second_avg < 0):
            return "volatile"
        else:
            return "stable"


# =============================================================================
# Factory Functions
# =============================================================================

def create_news_intelligence_agent(model: str = "gpt-4o-mini") -> NewsIntelligenceAgent:
    """
    Factory function to create a NewsIntelligenceAgent.
    
    Args:
        model: OpenAI model to use.
        
    Returns:
        Configured NewsIntelligenceAgent instance.
    """
    return NewsIntelligenceAgent(model=model)


def should_use_news_search(query_analysis: Any) -> bool:
    """
    Determine if news search should be used based on query analysis.
    
    Args:
        query_analysis: QueryAnalysis object.
        
    Returns:
        True if news search is appropriate.
    """
    if not query_analysis:
        return False
    
    # Check query type
    news_types = ["news", "current_events", "breaking_news", "recent_developments"]
    if hasattr(query_analysis, "query_type"):
        if query_analysis.query_type.lower() in news_types:
            return True
    
    # Check for time-sensitive queries
    if hasattr(query_analysis, "is_time_sensitive"):
        if query_analysis.is_time_sensitive:
            return True
    
    # Check keywords
    if hasattr(query_analysis, "original_query"):
        query_lower = query_analysis.original_query.lower()
        news_keywords = [
            "latest", "recent", "news", "today", "yesterday",
            "this week", "breaking", "developing", "update",
            "current", "just announced", "just released",
        ]
        if any(kw in query_lower for kw in news_keywords):
            return True
    
    return False
