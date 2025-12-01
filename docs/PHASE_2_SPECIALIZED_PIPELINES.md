# Phase 2: Specialized Research Pipelines

> **Status**: ✅ Complete  
> **Branch**: `version2-enhancements`  
> **Total New Tests**: 222 (50 Academic + 55 Market + 117 News/FactChecker)

## Overview

Phase 2 extends the deep research agent with four specialized research pipelines, each targeting specific research domains with tailored data sources, parsing logic, and output formats.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Phase 2: Specialized Pipelines                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Academic      │  │    Market       │  │     News        │              │
│  │   Research      │  │  Intelligence   │  │  Intelligence   │              │
│  │    Agent        │  │     Agent       │  │     Agent       │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Semantic Scholar│  │   SEC Filings   │  │  WebSearchTool  │              │
│  │      API        │  │   + Web Data    │  │   (Real-time)   │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│                          ┌─────────────────┐                                 │
│                          │  Fact Checker   │                                 │
│                          │     Agent       │                                 │
│                          └────────┬────────┘                                 │
│                                   │                                          │
│                                   ▼                                          │
│                          ┌─────────────────┐                                 │
│                          │   Verification  │                                 │
│                          │     Report      │                                 │
│                          └─────────────────┘                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [Academic Research Agent](#1-academic-research-agent)
2. [Market Intelligence Agent](#2-market-intelligence-agent)
3. [News Intelligence Agent](#3-news-intelligence-agent)
4. [Fact Checker Agent](#4-fact-checker-agent)
5. [ResearchManager Integration](#5-researchmanager-integration)
6. [Data Models Reference](#6-data-models-reference)
7. [Usage Examples](#7-usage-examples)
8. [Testing](#8-testing)

---

## 1. Academic Research Agent

### Purpose
Fetches peer-reviewed papers from Semantic Scholar with WebSearchTool fallback for comprehensive scholarly research.

### Location
- **Agent**: `deep_research/research_agents/academic_agent.py`
- **Models**: `deep_research/models/academic_models.py`
- **Tests**: `tests/test_academic_agent.py` (50 tests)

### Key Components

#### SemanticScholarClient
HTTP client for the Semantic Scholar API with rate limiting and error handling.

```python
from deep_research.research_agents.academic_agent import SemanticScholarClient

client = SemanticScholarClient(api_key="optional_key")
papers = await client.search_papers(
    query="transformer neural networks",
    limit=10,
    year_range=(2020, 2024),
    min_citations=50
)
```

#### AcademicResearchAgent
Main agent combining API search with web fallback.

```python
from deep_research.research_agents import create_academic_research_agent

agent = create_academic_research_agent(model="gpt-4o-mini")
result = await agent.search_academic(
    query="machine learning in healthcare",
    filters=AcademicSearchFilters(
        year_start=2020,
        min_citations=10,
        fields_of_study=[FieldOfStudy.MACHINE_LEARNING, FieldOfStudy.MEDICINE]
    )
)
```

### Features

| Feature | Description |
|---------|-------------|
| **Semantic Scholar API** | Primary source for peer-reviewed papers |
| **WebSearchTool Fallback** | Falls back to web search when API unavailable |
| **Year Range Filtering** | Filter papers by publication year |
| **Citation Thresholds** | Minimum citation count filtering |
| **Field of Study** | Filter by academic discipline |
| **Credibility Scoring** | Score based on citations, venue, recency |

### Academic Filters

```python
class AcademicSearchFilters(BaseModel):
    year_start: Optional[int] = None        # e.g., 2020
    year_end: Optional[int] = None          # e.g., 2024
    min_citations: int = 0                  # Minimum citation count
    fields_of_study: List[FieldOfStudy] = [] # Academic disciplines
    venue_types: List[PublicationVenue] = [] # Journal, conference, etc.
    open_access_only: bool = False          # Only open access papers
    limit: int = 20                         # Max results
```

### Routing Logic

The `should_use_academic_search()` function determines when to use this agent:

```python
# Triggered by:
# - query_type in ["academic", "scientific", "technical"]
# - Keywords: "research", "study", "peer-reviewed", "journal", "citation"
# - Fields: medicine, biology, physics, computer science, etc.
```

---

## 2. Market Intelligence Agent

### Purpose
Aggregates data from SEC filings and market sources to build comprehensive market snapshots with competitor analysis.

### Location
- **Agent**: `deep_research/research_agents/market_agent.py`
- **Models**: `deep_research/models/market_models.py`
- **Tests**: `tests/test_market_agent.py` (55 tests)

### Key Components

#### SECFilingParser
Regex-based parser for extracting financial data from 10-K filings.

```python
from deep_research.research_agents.market_agent import SECFilingParser

parser = SECFilingParser()
filing_data = parser.parse_filing(filing_text)

print(f"Revenue: ${filing_data.revenue:,.0f}")
print(f"Growth: {filing_data.revenue_growth}%")
print(f"TAM: {filing_data.market_size_mentions}")
```

#### Extraction Patterns

| Data Type | Regex Pattern |
|-----------|---------------|
| Revenue | `revenue\|net sales\|total revenue` + `$X billion/million` |
| Growth Rate | `grew\|growth\|increased` + `X%` |
| TAM/SAM/SOM | `total addressable market\|TAM` + `$X billion` |
| Competitors | `compete with\|competitors include` + company names |
| Risk Factors | `Item 1A. Risk Factors` section parsing |

#### MarketIntelligenceAgent
Combines SEC data with web search for complete market analysis.

```python
from deep_research.research_agents import create_market_intelligence_agent

agent = create_market_intelligence_agent(model="gpt-4o-mini")
snapshot = await agent.analyze_market(
    query="enterprise software market analysis",
    tickers=["MSFT", "CRM", "ORCL"]
)
```

### MarketSnapshot Output

```python
class MarketSnapshot(BaseModel):
    market_name: str                    # "Enterprise Software"
    analysis_date: datetime
    metrics: MarketMetrics              # TAM, SAM, SOM, growth rates
    competitors: List[CompetitorProfile] # Market players
    pricing_benchmarks: List[PricingBenchmark]
    risk_notes: List[RiskNote]          # Industry risks
    data_sources: List[str]             # Source attribution
```

### Features

| Feature | Description |
|---------|-------------|
| **SEC Filing Parsing** | Extract financials from 10-K/10-Q filings |
| **TAM/SAM/SOM Extraction** | Market sizing from filings and reports |
| **Competitor Analysis** | Identify and profile market players |
| **Pricing Benchmarks** | Industry pricing intelligence |
| **Risk Assessment** | Risk factors with severity levels |
| **Stub API Support** | Works without SEC API key (mock data) |

### Routing Logic

```python
# Triggered by:
# - query_type in ["market_research", "competitive_analysis"]
# - Keywords: "market share", "competitor", "SEC filing", "revenue"
# - Keywords: "TAM", "market size", "industry analysis"
```

---

## 3. News Intelligence Agent

### Purpose
Aggregates real-time news with chronological timeline focus, sentiment analysis, and source credibility scoring.

### Location
- **Agent**: `deep_research/research_agents/news_agent.py`
- **Models**: `deep_research/models/news_models.py`
- **Tests**: `tests/test_news_agent.py` (66 tests)

### Key Components

#### Sentiment Analysis
Keyword-based sentiment classification with intensity levels.

```python
from deep_research.research_agents.news_agent import analyze_sentiment

result = analyze_sentiment("Stock prices soared after breakthrough announcement")
print(f"Sentiment: {result.sentiment}")      # POSITIVE
print(f"Intensity: {result.intensity}")      # STRONG
print(f"Confidence: {result.confidence}")    # 0.85
print(f"Key phrases: {result.key_phrases}")  # ["+soared", "+breakthrough"]
```

#### Sentiment Keywords

| Intensity | Positive | Negative |
|-----------|----------|----------|
| **Strong** | breakthrough, triumph, soaring, skyrockets | crash, collapse, crisis, disaster |
| **Moderate** | growth, gains, success, progress | decline, losses, struggles, challenges |
| **Weak** | stable, steady, maintains | slows, uncertain, cautious |

#### Source Credibility Scoring

```python
from deep_research.research_agents.news_agent import score_source_credibility

score = score_source_credibility("Reuters", "https://reuters.com/article")
# Returns: 85-95 (high credibility)

score = score_source_credibility("Daily Mail", "https://dailymail.co.uk")
# Returns: 30-40 (low credibility)
```

| Tier | Score Range | Sources |
|------|-------------|---------|
| **High** | 85-95 | Reuters, AP, BBC, WSJ, NYT, Nature |
| **Medium** | 60-75 | CNN, Forbes, TechCrunch, Wired |
| **Low** | 30-40 | Tabloids, gossip sites |
| **Default** | 50 | Unknown sources |

#### NewsIntelligenceAgent

```python
from deep_research.research_agents import create_news_intelligence_agent

agent = create_news_intelligence_agent(model="gpt-4o-mini")
timeline = await agent.search_news(
    query="OpenAI GPT announcements",
    days_back=7,
    max_events=20
)

print(timeline.to_markdown_timeline())
```

### NewsTimeline Output

```python
class NewsTimeline(BaseModel):
    topic: str                          # Search topic
    events: List[NewsEvent]             # Chronological events
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    overall_sentiment: Sentiment        # POSITIVE/NEGATIVE/NEUTRAL/MIXED
    sentiment_trend: str                # "improving", "declining", "stable"
    total_sources: int
    average_credibility: float
    key_developments: List[str]         # Major events
```

### NewsEvent Model

```python
class NewsEvent(BaseModel):
    headline: str
    summary: str
    event_date: Optional[datetime]
    category: NewsCategory              # TECHNOLOGY, BUSINESS, etc.
    entities: List[str]                 # People, organizations mentioned
    sources: List[NewsSource]
    sentiment: SentimentAnalysis
    reliability_tier: str               # "high", "medium", "low"
    is_breaking: bool
    is_verified: bool                   # Multiple source confirmation
```

### Features

| Feature | Description |
|---------|-------------|
| **Real-time Aggregation** | WebSearchTool for latest news |
| **Chronological Timelines** | Events sorted by date |
| **Sentiment Analysis** | Positive/negative/neutral classification |
| **Source Scoring** | Credibility based on domain reputation |
| **Entity Extraction** | People, organizations, places |
| **News Categorization** | Technology, business, politics, etc. |
| **Trend Detection** | Sentiment trend over time |
| **Deduplication** | Removes similar headlines |

### Routing Logic

```python
# Triggered by:
# - query_type in ["news", "current_events", "breaking_news"]
# - is_time_sensitive = True
# - Keywords: "latest", "recent", "today", "breaking", "developing"
```

---

## 4. Fact Checker Agent

### Purpose
Scans drafted markdown reports, extracts factual claims, cross-checks against validated sources, and annotates with verification confidence levels.

### Location
- **Agent**: `deep_research/research_agents/fact_checker_agent.py`
- **Models**: `deep_research/models/news_models.py` (shared)
- **Tests**: `tests/test_fact_checker.py` (51 tests)

### Key Components

#### Claim Extraction
Regex-based extraction of verifiable claims from markdown.

```python
from deep_research.research_agents.fact_checker_agent import extract_claims_from_markdown

claims = extract_claims_from_markdown("""
# Market Analysis

The global AI market reached $150 billion in 2024, growing 25% year-over-year.
According to Gartner, "AI adoption will triple by 2026."
Microsoft acquired Activision in 2023 for $69 billion.
""")

for claim in claims:
    print(f"[{claim.category}] {claim.claim_text}")
```

#### Claim Categories

| Category | Pattern Examples |
|----------|------------------|
| **STATISTIC** | `$150 billion`, `25%`, `3x growth` |
| **TEMPORAL** | `in 2024`, `founded in 1998` |
| **QUOTE** | `"AI adoption will triple"`, `X said Y` |
| **COMPARATIVE** | `more than 50%`, `3x faster` |
| **SCIENTIFIC** | `study shows`, `research indicates` |
| **EVENT** | `acquired in 2023`, `launched yesterday` |

#### FactCheckerAgent

```python
from deep_research.research_agents import create_fact_checker_agent

checker = create_fact_checker_agent(model="gpt-4o-mini")
report = await checker.verify_report(
    markdown=draft_report,
    max_claims=20,
    collected_sources=research_sources
)

print(report.to_markdown_section())
```

### Verification Status

| Status | Emoji | Description |
|--------|-------|-------------|
| **VERIFIED** | ✅ | Confirmed by multiple reliable sources |
| **UNCERTAIN** | ⚠️ | Insufficient evidence or conflicting sources |
| **DISPUTED** | ❌ | Contradicted by reliable sources |
| **UNVERIFIABLE** | ❓ | Cannot be fact-checked (opinion, prediction) |

### VerificationReport Output

```python
class VerificationReport(BaseModel):
    document_title: str
    results: List[VerificationResult]
    total_claims: int
    verified_count: int
    uncertain_count: int
    disputed_count: int
    unverifiable_count: int
    overall_reliability: float          # 0.0 - 1.0
```

### Generated Markdown Section

```markdown
## Verification Status

**🟢 High Reliability** (85% verified)

### Claim Summary

| Status | Count |
|--------|-------|
| ✅ Verified | 12 |
| ⚠️ Uncertain | 2 |
| ❌ Disputed | 1 |
| ❓ Unverifiable | 0 |
| **Total** | **15** |

### ⚠️ Disputed Claims

- **Claim:** The market grew 50% in Q3.
  - **Correction:** Actual growth was 32% according to SEC filings.
  - **Explanation:** Disputed by 2 source(s). May need correction.
```

### Features

| Feature | Description |
|---------|-------------|
| **Claim Extraction** | Regex patterns for statistics, dates, quotes |
| **Priority Scoring** | Statistics and comparatives checked first |
| **Source Cross-Check** | Verifies against collected research sources |
| **Web Verification** | Falls back to web search for confirmation |
| **Caching** | MD5-based caching to avoid re-verification |
| **Inline Annotations** | Adds `[✅ VERIFIED]` etc. to claims |
| **Report Generation** | Markdown summary with statistics |

---

## 5. ResearchManager Integration

All four specialized agents are integrated into the main `ResearchManager` class.

### Lazy Initialization

```python
class ResearchManager:
    @property
    def academic_agent(self) -> AcademicResearchAgent:
        """Lazy-load academic research agent."""
        if self._academic_agent is None:
            self._academic_agent = create_academic_research_agent(model=self.model)
        return self._academic_agent
    
    @property
    def market_agent(self) -> MarketIntelligenceAgent:
        """Lazy-load market intelligence agent."""
        ...
    
    @property
    def news_agent(self) -> NewsIntelligenceAgent:
        """Lazy-load news intelligence agent."""
        ...
    
    @property
    def fact_checker(self) -> FactCheckerAgent:
        """Lazy-load fact checker agent."""
        ...
```

### Automatic Routing in perform_searches()

```python
async def perform_searches(self, plan: WebSearchPlan, analysis: QueryAnalysis):
    # Determine which specialized agents to use
    use_academic = should_use_academic_search(analysis)
    use_market_intel = should_use_market_intelligence(analysis)
    use_news = should_use_news_search(analysis)
    
    if use_academic:
        academic_results = await self._perform_academic_search(plan, analysis)
        # Merge into collected_sources
    
    if use_market_intel:
        market_snapshot = await self._perform_market_intelligence(analysis)
        # Add market data to report
    
    # Standard web searches continue...
```

### Fact-Checking in write_report()

```python
async def write_report(self, query, search_results, analysis):
    # ... generate initial report ...
    
    # Run fact-checking before final formatting
    print("   🔍 Running fact-check on report claims...")
    self.verification_report = await self.fact_checker.verify_report(
        formatted_markdown,
        max_claims=15,
        collected_sources=self.collected_sources
    )
    
    # Inject verification section
    if self.verification_report.total_claims > 0:
        verification_section = self.verification_report.to_markdown_section()
        # Insert before Sources/References section
```

---

## 6. Data Models Reference

### Academic Models (`academic_models.py`)

| Model | Description |
|-------|-------------|
| `AcademicSource` | Paper with title, authors, venue, citations |
| `AcademicSearchFilters` | Year range, citations, fields of study |
| `AcademicSearchResult` | Collection with statistics |
| `Author` | Name, affiliation, h-index |
| `FieldOfStudy` | Enum: CS, AI, Medicine, Physics, etc. |
| `PublicationVenue` | Enum: Journal, Conference, Preprint |

### Market Models (`market_models.py`)

| Model | Description |
|-------|-------------|
| `MarketSnapshot` | Complete market analysis |
| `MarketMetrics` | TAM, SAM, SOM, growth rates |
| `CompetitorProfile` | Company with market share, strengths |
| `PricingBenchmark` | Product pricing data |
| `RiskNote` | Risk with severity and category |
| `SECFilingData` | Parsed 10-K/10-Q data |

### News Models (`news_models.py`)

| Model | Description |
|-------|-------------|
| `NewsEvent` | Single news item with sentiment |
| `NewsTimeline` | Chronological event collection |
| `NewsSource` | Publication with credibility score |
| `SentimentAnalysis` | Sentiment, intensity, confidence |
| `FactualClaim` | Extracted claim for verification |
| `VerificationResult` | Single claim verification |
| `VerificationReport` | Document-level summary |

---

## 7. Usage Examples

### Academic Research Query

```python
manager = ResearchManager()

# Query triggers academic routing automatically
report = await manager.run(
    "What are the latest advances in transformer architectures for NLP?"
)

# Access academic results
if manager.academic_results:
    print(f"Found {len(manager.academic_results.sources)} papers")
    for paper in manager.academic_results.sources[:3]:
        print(f"- {paper.title} ({paper.citation_count} citations)")
```

### Market Intelligence Query

```python
report = await manager.run(
    "Analyze the competitive landscape of the cloud computing market"
)

# Access market snapshot
if manager.market_snapshot:
    print(f"Market: {manager.market_snapshot.market_name}")
    print(f"TAM: {manager.market_snapshot.metrics.tam_formatted}")
    for competitor in manager.market_snapshot.competitors[:3]:
        print(f"- {competitor.name}: {competitor.market_share}% share")
```

### News Timeline Query

```python
report = await manager.run(
    "What are the latest developments in AI regulation?"
)

# Access news timeline
if manager.news_timeline:
    print(manager.news_timeline.to_markdown_timeline())
```

### Manual Fact-Checking

```python
from deep_research.research_agents import verify_markdown_claims

report = await verify_markdown_claims(
    markdown=my_report_text,
    max_claims=20,
    sources=my_sources
)

print(f"Reliability: {report.overall_reliability:.0%}")
print(f"Disputed claims: {report.disputed_count}")
```

---

## 8. Testing

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_academic_agent.py` | 50 | Models, API client, agent, routing |
| `test_market_agent.py` | 55 | Models, parser, agent, routing |
| `test_news_agent.py` | 66 | Sentiment, scoring, timeline, agent |
| `test_fact_checker.py` | 51 | Extraction, categorization, verification |

### Running Tests

```powershell
# All Phase 2 tests
python -m pytest tests/test_academic_agent.py tests/test_market_agent.py tests/test_news_agent.py tests/test_fact_checker.py -v

# Full test suite (334 tests)
python -m pytest tests/ -v
```

### Test Categories

Each test file covers:

1. **Model Tests** - Pydantic model creation and validation
2. **Utility Tests** - Helper functions (parsing, scoring, extraction)
3. **Agent Tests** - Agent initialization and methods
4. **Integration Tests** - End-to-end workflows
5. **Edge Cases** - Empty inputs, malformed data, error handling

---

## Architecture Decisions

### 1. Lazy Loading
All specialized agents use lazy initialization to avoid overhead when not needed.

### 2. Graceful Fallbacks
- Academic: Semantic Scholar → WebSearchTool
- Market: SEC API → Stub data → WebSearchTool
- All agents handle API failures gracefully

### 3. Caching
- Fact-checker uses MD5-based claim caching
- Academic agent caches search results
- Market snapshot cached per session

### 4. Separation of Concerns
- Models in `models/` directory
- Agents in `research_agents/` directory
- Clear interfaces between components

### 5. Extensibility
- New specialized agents follow the same pattern
- Routing logic in dedicated `should_use_*` functions
- Factory functions for agent creation

---

## Future Enhancements

1. **Patent Research Agent** - USPTO/EPO patent database integration
2. **Social Media Agent** - Twitter/Reddit sentiment and trending topics
3. **Government Data Agent** - Census, BLS, and regulatory data
4. **Multi-language Support** - Non-English source handling
5. **Real-time Streaming** - Live news feed integration

---

*Last Updated: December 2025*
*Phase 2 Implementation Complete*
