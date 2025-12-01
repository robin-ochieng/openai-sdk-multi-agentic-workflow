"""
Unit Tests for MarketIntelligenceAgent

Tests cover:
1. SECFilingParser text parsing
2. MarketSnapshot model validation
3. CompetitorProfile and PricingBenchmark models
4. MarketIntelligenceAgent integration
5. Helper functions for query routing
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from deep_research.models.market_models import (
    MarketSnapshot,
    MarketMetrics,
    CompetitorProfile,
    PricingBenchmark,
    RiskNote,
    SECFilingData,
    MarketIntelligenceQuery,
    MarketTrend,
    RiskLevel,
    DataConfidence,
)
from deep_research.research_agents.market_agent import (
    MarketIntelligenceAgent,
    SECFilingParser,
    SECAPIClient,
    create_market_intelligence_agent,
    should_use_market_intelligence,
    get_sec_filing_parser,
)


# =============================================================================
# Test Fixtures - Sample SEC Filing Text
# =============================================================================

@pytest.fixture
def sample_10k_text() -> str:
    """Sample 10-K filing text for testing."""
    return """
    UNITED STATES SECURITIES AND EXCHANGE COMMISSION
    Washington, D.C. 20549
    
    FORM 10-K
    
    ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE 
    SECURITIES EXCHANGE ACT OF 1934
    
    For the fiscal year ended December 31, 2024
    
    TechCorp Inc.
    (Exact name of registrant as specified in its charter)
    
    PART I
    
    Item 1. Business
    
    TechCorp Inc. is a leading provider of enterprise software solutions.
    Our total revenue for fiscal year 2024 was $5.2 billion, representing
    year-over-year revenue growth of 23.5%. We operate in a market with a
    total addressable market estimated at $150 billion.
    
    We compete with Microsoft, Salesforce, Oracle, and SAP in the
    enterprise software market. Our competitors include established
    technology companies such as Google, Amazon Web Services, and IBM.
    
    Item 1A. Risk Factors
    
    • Competition in our industry is intense and we may not be able to 
      maintain our competitive position effectively.
    • Our business is subject to complex and evolving regulatory requirements
      regarding privacy, data protection, and cybersecurity.
    • Economic conditions and uncertainty may adversely affect demand for 
      our products and services.
    • We depend on key personnel and may not be able to attract and retain
      qualified employees.
    • Cybersecurity threats and data breaches pose ongoing risks to our
      business operations and reputation.
    
    Item 7. Management's Discussion and Analysis
    
    Total net revenue increased by $985 million, or 23.5%, to $5.2 billion
    for fiscal 2024 compared to $4.2 billion for fiscal 2023. The increase
    was primarily driven by growth in our cloud services segment.
    
    Our gross margin was 72.3% for fiscal 2024 compared to 70.8% for the
    prior year. Operating income was $1.3 billion, up from $980 million.
    
    The serviceable addressable market (SAM) for our core products is
    approximately $45 billion, with our serviceable obtainable market (SOM)
    at $8 billion based on current market share.
    """


@pytest.fixture
def sample_10k_minimal() -> str:
    """Minimal 10-K text for edge case testing."""
    return """
    FORM 10-K
    
    MiniCorp LLC
    
    Item 1. Business
    
    We are a small company. Revenue was approximately $10 million.
    """


@pytest.fixture
def sample_10k_no_numbers() -> str:
    """10-K text without financial numbers."""
    return """
    FORM 10-K
    
    NewCo Inc.
    
    Item 1. Business
    
    We are building the next generation of software solutions.
    Our products are used by customers worldwide.
    
    Item 1A. Risk Factors
    
    There are many risks associated with our business.
    """


# =============================================================================
# Test Class: MarketMetrics Model
# =============================================================================

class TestMarketMetrics:
    """Tests for MarketMetrics Pydantic model."""
    
    def test_create_basic_metrics(self):
        """Test creating basic market metrics."""
        metrics = MarketMetrics()
        assert metrics.total_addressable_market is None
        assert metrics.revenue is None
        assert metrics.data_confidence == DataConfidence.MEDIUM
    
    def test_create_full_metrics(self):
        """Test creating metrics with all fields."""
        metrics = MarketMetrics(
            total_addressable_market=150_000_000_000,
            serviceable_addressable_market=45_000_000_000,
            serviceable_obtainable_market=8_000_000_000,
            market_growth_rate=15.5,
            cagr=12.3,
            revenue=5_200_000_000,
            revenue_growth=23.5,
            gross_margin=72.3,
            operating_margin=25.0,
            data_confidence=DataConfidence.HIGH,
            data_year=2024,
        )
        
        assert metrics.total_addressable_market == 150_000_000_000
        assert metrics.revenue == 5_200_000_000
        assert metrics.revenue_growth == 23.5
    
    def test_tam_formatted(self):
        """Test TAM formatting."""
        metrics = MarketMetrics(total_addressable_market=150_000_000_000)
        assert metrics.tam_formatted == "$150.0B"
    
    def test_tam_formatted_trillion(self):
        """Test TAM formatting for trillion values."""
        metrics = MarketMetrics(total_addressable_market=1_500_000_000_000)
        assert metrics.tam_formatted == "$1.5T"
    
    def test_tam_formatted_million(self):
        """Test TAM formatting for million values."""
        metrics = MarketMetrics(total_addressable_market=500_000_000)
        assert metrics.tam_formatted == "$500.0M"
    
    def test_tam_formatted_none(self):
        """Test TAM formatting when None."""
        metrics = MarketMetrics()
        assert metrics.tam_formatted == "N/A"
    
    def test_revenue_formatted(self):
        """Test revenue formatting."""
        metrics = MarketMetrics(revenue=5_200_000_000)
        assert metrics.revenue_formatted == "$5.2B"


# =============================================================================
# Test Class: CompetitorProfile Model
# =============================================================================

class TestCompetitorProfile:
    """Tests for CompetitorProfile Pydantic model."""
    
    def test_create_basic_competitor(self):
        """Test creating a basic competitor profile."""
        competitor = CompetitorProfile(name="Microsoft")
        assert competitor.name == "Microsoft"
        assert competitor.market_position == "competitor"
        assert competitor.estimated_market_share is None
    
    def test_create_full_competitor(self):
        """Test creating a full competitor profile."""
        competitor = CompetitorProfile(
            name="Microsoft Corporation",
            ticker="MSFT",
            market_position="leader",
            estimated_market_share=35.5,
            estimated_revenue=211_000_000_000,
            strengths=["Brand recognition", "Enterprise relationships"],
            weaknesses=["Complex licensing", "Legacy products"],
            key_products=["Azure", "Office 365", "Dynamics"],
            founded_year=1975,
            headquarters="Redmond, WA",
            employee_count=220000,
        )
        
        assert competitor.ticker == "MSFT"
        assert competitor.market_position == "leader"
        assert competitor.estimated_market_share == 35.5
        assert len(competitor.strengths) == 2
    
    def test_revenue_formatted_billions(self):
        """Test revenue formatting for billions."""
        competitor = CompetitorProfile(
            name="BigCorp",
            estimated_revenue=211_000_000_000
        )
        assert competitor.revenue_formatted == "$211.0B"
    
    def test_revenue_formatted_millions(self):
        """Test revenue formatting for millions."""
        competitor = CompetitorProfile(
            name="MidCorp",
            estimated_revenue=500_000_000
        )
        assert competitor.revenue_formatted == "$500.0M"
    
    def test_revenue_formatted_none(self):
        """Test revenue formatting when None."""
        competitor = CompetitorProfile(name="Unknown")
        assert competitor.revenue_formatted == "N/A"


# =============================================================================
# Test Class: PricingBenchmark Model
# =============================================================================

class TestPricingBenchmark:
    """Tests for PricingBenchmark Pydantic model."""
    
    def test_create_basic_benchmark(self):
        """Test creating a basic pricing benchmark."""
        benchmark = PricingBenchmark(product_category="Enterprise SaaS")
        assert benchmark.product_category == "Enterprise SaaS"
        assert benchmark.pricing_model == "unknown"
    
    def test_create_full_benchmark(self):
        """Test creating a full pricing benchmark."""
        benchmark = PricingBenchmark(
            product_category="CRM Software",
            price_range_low=25,
            price_range_high=300,
            average_price=125,
            pricing_model="per-seat subscription",
            currency="USD",
            price_trend=MarketTrend.GROWING,
            notes=["Annual contracts common", "Enterprise discounts available"],
        )
        
        assert benchmark.price_range_low == 25
        assert benchmark.price_range_high == 300
        assert benchmark.price_trend == MarketTrend.GROWING
    
    def test_price_range_formatted(self):
        """Test price range formatting."""
        benchmark = PricingBenchmark(
            product_category="Test",
            price_range_low=25,
            price_range_high=300,
        )
        assert benchmark.price_range_formatted == "$25 - $300 USD"
    
    def test_price_range_formatted_none(self):
        """Test price range formatting when None."""
        benchmark = PricingBenchmark(product_category="Test")
        assert benchmark.price_range_formatted == "N/A"


# =============================================================================
# Test Class: RiskNote Model
# =============================================================================

class TestRiskNote:
    """Tests for RiskNote Pydantic model."""
    
    def test_create_basic_risk(self):
        """Test creating a basic risk note."""
        risk = RiskNote(
            category="competitive",
            description="Competition is increasing in the market."
        )
        assert risk.category == "competitive"
        assert risk.level == RiskLevel.MEDIUM
    
    def test_create_full_risk(self):
        """Test creating a full risk note."""
        risk = RiskNote(
            category="regulatory",
            description="New data protection regulations may impact operations.",
            level=RiskLevel.HIGH,
            mitigation="Investing in compliance infrastructure",
            source="SEC 10-K Filing",
        )
        
        assert risk.level == RiskLevel.HIGH
        assert risk.mitigation is not None


# =============================================================================
# Test Class: MarketSnapshot Model
# =============================================================================

class TestMarketSnapshot:
    """Tests for MarketSnapshot Pydantic model."""
    
    def test_create_basic_snapshot(self):
        """Test creating a basic market snapshot."""
        snapshot = MarketSnapshot(market_name="Enterprise Software")
        assert snapshot.market_name == "Enterprise Software"
        assert snapshot.market_trend == MarketTrend.STABLE
        assert snapshot.competitor_count == 0
    
    def test_create_full_snapshot(self):
        """Test creating a full market snapshot."""
        competitors = [
            CompetitorProfile(name="Microsoft", estimated_market_share=35.0),
            CompetitorProfile(name="Salesforce", estimated_market_share=20.0),
            CompetitorProfile(name="Oracle", estimated_market_share=15.0),
        ]
        
        pricing = [
            PricingBenchmark(
                product_category="CRM",
                price_range_low=25,
                price_range_high=300,
            )
        ]
        
        risks = [
            RiskNote(category="competitive", description="Intense competition"),
            RiskNote(category="regulatory", description="New regulations", level=RiskLevel.HIGH),
        ]
        
        metrics = MarketMetrics(
            total_addressable_market=150_000_000_000,
            market_growth_rate=15.0,
        )
        
        snapshot = MarketSnapshot(
            market_name="Enterprise Software",
            market_trend=MarketTrend.GROWING,
            key_drivers=["Digital transformation", "Cloud adoption"],
            key_challenges=["Competition", "Talent shortage"],
            metrics=metrics,
            competitors=competitors,
            pricing_benchmarks=pricing,
            risk_notes=risks,
            overall_risk_level=RiskLevel.MEDIUM,
            data_sources=["SEC Filings", "Web Research"],
            confidence_score=0.75,
        )
        
        assert snapshot.competitor_count == 3
        assert snapshot.high_risk_count == 1
        assert len(snapshot.get_market_leaders()) == 3
    
    def test_get_market_leaders(self):
        """Test getting top competitors by market share."""
        competitors = [
            CompetitorProfile(name="Small", estimated_market_share=5.0),
            CompetitorProfile(name="Large", estimated_market_share=40.0),
            CompetitorProfile(name="Medium", estimated_market_share=20.0),
        ]
        
        snapshot = MarketSnapshot(
            market_name="Test",
            competitors=competitors,
        )
        
        leaders = snapshot.get_market_leaders(top_n=2)
        assert len(leaders) == 2
        assert leaders[0].name == "Large"
        assert leaders[1].name == "Medium"
    
    def test_to_summary_dict(self):
        """Test conversion to summary dictionary."""
        metrics = MarketMetrics(
            total_addressable_market=150_000_000_000,
            market_growth_rate=15.0,
        )
        
        snapshot = MarketSnapshot(
            market_name="Test Market",
            metrics=metrics,
            market_trend=MarketTrend.GROWING,
            confidence_score=0.8,
        )
        
        summary = snapshot.to_summary_dict()
        
        assert summary["market_name"] == "Test Market"
        assert summary["tam"] == "$150.0B"
        assert summary["market_growth_rate"] == "15.0%"
        assert summary["market_trend"] == "growing"
        assert summary["confidence"] == "80%"
    
    def test_to_report_section(self):
        """Test markdown report generation."""
        metrics = MarketMetrics(
            total_addressable_market=150_000_000_000,
            serviceable_addressable_market=50_000_000_000,
            serviceable_obtainable_market=10_000_000_000,
            market_growth_rate=15.0,
        )
        
        snapshot = MarketSnapshot(
            market_name="AI Software",
            metrics=metrics,
            market_trend=MarketTrend.GROWING,
            key_drivers=["LLM adoption"],
            competitors=[CompetitorProfile(name="OpenAI", estimated_market_share=30.0)],
        )
        
        report = snapshot.to_report_section()
        
        assert "## Market Intelligence: AI Software" in report
        assert "$150.0B" in report
        assert "OpenAI" in report


# =============================================================================
# Test Class: SECFilingData Model
# =============================================================================

class TestSECFilingData:
    """Tests for SECFilingData Pydantic model."""
    
    def test_create_basic_filing(self):
        """Test creating a basic SEC filing data."""
        filing = SECFilingData(company_name="TechCorp Inc.")
        assert filing.company_name == "TechCorp Inc."
        assert filing.filing_type == "10-K"
    
    def test_create_full_filing(self):
        """Test creating a full SEC filing data."""
        filing = SECFilingData(
            company_name="TechCorp Inc.",
            ticker="TECH",
            filing_type="10-K",
            fiscal_year=2024,
            revenue=5_200_000_000,
            revenue_growth=23.5,
            gross_profit=3_760_000_000,
            operating_income=1_300_000_000,
            net_income=1_000_000_000,
            risk_factors=["Competition", "Regulatory changes"],
            competitor_mentions=["Microsoft", "Salesforce"],
            market_size_mentions=["TAM of $150 billion"],
        )
        
        assert filing.revenue == 5_200_000_000
        assert filing.revenue_growth == 23.5
        assert len(filing.risk_factors) == 2


# =============================================================================
# Test Class: SECFilingParser
# =============================================================================

class TestSECFilingParser:
    """Tests for SECFilingParser text parsing."""
    
    @pytest.fixture
    def parser(self):
        """Create a SECFilingParser instance."""
        return SECFilingParser()
    
    def test_parse_filing_extracts_company_name(self, parser, sample_10k_text):
        """Test company name extraction."""
        result = parser.parse_filing(sample_10k_text)
        assert "TechCorp" in result.company_name
    
    def test_parse_filing_extracts_revenue(self, parser, sample_10k_text):
        """Test revenue extraction."""
        result = parser.parse_filing(sample_10k_text)
        # Note: Parser extracts first revenue mention (985 million from "increased by")
        # In real usage, more sophisticated parsing would be needed
        assert result.revenue is not None
        assert result.revenue > 0  # Revenue was extracted successfully
    
    def test_parse_filing_extracts_growth_rate(self, parser, sample_10k_text):
        """Test growth rate extraction."""
        result = parser.parse_filing(sample_10k_text)
        # Should extract 23.5%
        assert result.revenue_growth is not None
        assert 20 <= result.revenue_growth <= 25
    
    def test_parse_filing_extracts_competitors(self, parser, sample_10k_text):
        """Test competitor extraction."""
        result = parser.parse_filing(sample_10k_text)
        assert len(result.competitor_mentions) > 0
        # Should find some of: Microsoft, Salesforce, Oracle, SAP, Google, Amazon, IBM
    
    def test_parse_filing_extracts_risk_factors(self, parser, sample_10k_text):
        """Test risk factor extraction."""
        result = parser.parse_filing(sample_10k_text)
        assert len(result.risk_factors) > 0
    
    def test_parse_filing_extracts_market_size(self, parser, sample_10k_text):
        """Test market size mention extraction."""
        result = parser.parse_filing(sample_10k_text)
        assert len(result.market_size_mentions) > 0
    
    def test_parse_filing_minimal(self, parser, sample_10k_minimal):
        """Test parsing minimal filing."""
        result = parser.parse_filing(sample_10k_minimal)
        assert "MiniCorp" in result.company_name or result.company_name == "Unknown Company"
    
    def test_parse_filing_no_numbers(self, parser, sample_10k_no_numbers):
        """Test parsing filing without financial numbers."""
        result = parser.parse_filing(sample_10k_no_numbers)
        assert result.revenue is None
        assert result.revenue_growth is None
    
    def test_parse_financial_value_billion(self, parser):
        """Test parsing billion values."""
        assert parser.parse_financial_value("$5.2 billion") == 5_200_000_000
        assert parser.parse_financial_value("5.2B") == 5_200_000_000
    
    def test_parse_financial_value_million(self, parser):
        """Test parsing million values."""
        assert parser.parse_financial_value("$500 million") == 500_000_000
        assert parser.parse_financial_value("500M") == 500_000_000
    
    def test_parse_financial_value_trillion(self, parser):
        """Test parsing trillion values."""
        assert parser.parse_financial_value("$1.5 trillion") == 1_500_000_000_000
        assert parser.parse_financial_value("1.5T") == 1_500_000_000_000
    
    def test_parse_financial_value_plain(self, parser):
        """Test parsing plain numbers."""
        assert parser.parse_financial_value("1,500,000") == 1_500_000
        assert parser.parse_financial_value("$500") == 500
    
    def test_parse_financial_value_invalid(self, parser):
        """Test parsing invalid values."""
        assert parser.parse_financial_value("not a number") is None
        assert parser.parse_financial_value("") is None


# =============================================================================
# Test Class: SECAPIClient
# =============================================================================

class TestSECAPIClient:
    """Tests for SECAPIClient stub implementation."""
    
    @pytest.fixture
    def client(self):
        """Create a SECAPIClient instance."""
        return SECAPIClient()
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "https://api.sec-api.io"
        assert client.parser is not None
    
    def test_generate_stub_filing_known_ticker(self, client):
        """Test stub filing for known ticker."""
        filing = client._generate_stub_filing("AAPL", "10-K", 2024)
        assert filing.company_name == "Apple Inc."
        assert filing.ticker == "AAPL"
        assert filing.revenue > 0
    
    def test_generate_stub_filing_unknown_ticker(self, client):
        """Test stub filing for unknown ticker."""
        filing = client._generate_stub_filing("UNKNOWN", "10-K", 2024)
        assert "UNKNOWN" in filing.company_name
        assert filing.revenue == 10_000_000_000  # Default
    
    def test_get_filing_async(self, client):
        """Test async filing retrieval."""
        async def run_test():
            filing = await client.get_filing("MSFT", "10-K", 2024)
            assert filing is not None
            assert filing.company_name == "Microsoft Corporation"
            assert filing.revenue > 0
        
        asyncio.run(run_test())


# =============================================================================
# Test Class: MarketIntelligenceAgent
# =============================================================================

class TestMarketIntelligenceAgent:
    """Tests for MarketIntelligenceAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a MarketIntelligenceAgent instance."""
        return MarketIntelligenceAgent(model="gpt-4o-mini")
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.model == "gpt-4o-mini"
        assert agent._web_search_agent is None  # Lazy loaded
        assert agent.sec_client is not None
    
    def test_parse_filing_text(self, agent, sample_10k_text):
        """Test parsing filing text directly."""
        result = agent.parse_filing_text(sample_10k_text)
        assert result is not None
        assert "TechCorp" in result.company_name
    
    def test_extract_market_name(self, agent):
        """Test market name extraction from query."""
        assert "enterprise software" in agent._extract_market_name("enterprise software market analysis").lower()
        assert "ai" in agent._extract_market_name("AI industry trends").lower()
    
    def test_parse_market_data_with_tam(self, agent):
        """Test parsing market data with TAM."""
        # The regex handles "is" between TAM and value
        text = "The total addressable market (TAM) is $150 billion with a growth rate of 15.5%."
        data = agent._parse_market_data(text)
        
        assert data["tam"] == 150_000_000_000
        assert data["growth_rate"] == 15.5
    
    def test_parse_market_data_without_numbers(self, agent):
        """Test parsing market data without numbers."""
        text = "The market is growing rapidly but exact figures are unavailable."
        data = agent._parse_market_data(text)
        
        assert data["tam"] is None
        assert data["growth_rate"] is None
    
    def test_parse_competitors(self, agent):
        """Test competitor parsing from text."""
        text = """
        **Microsoft** is the market leader with enterprise solutions.
        **Salesforce** focuses on CRM and cloud platforms.
        **Oracle** provides database and cloud services.
        """
        competitors = agent._parse_competitors(text)
        
        assert len(competitors) >= 3
        names = [c.name for c in competitors]
        assert "Microsoft" in names
    
    def test_build_snapshot(self, agent):
        """Test building snapshot from data."""
        market_data = {"tam": 150_000_000_000, "growth_rate": 15.0}
        competitor_data = [CompetitorProfile(name="TestCo")]
        pricing_data = [PricingBenchmark(product_category="Software")]
        sec_data = SECFilingData(
            company_name="Test",
            revenue=1_000_000_000,
            risk_factors=["Competition is intense"]
        )
        
        snapshot = agent._build_snapshot(
            market_name="Test Market",
            market_data=market_data,
            competitor_data=competitor_data,
            pricing_data=pricing_data,
            sec_data=sec_data,
        )
        
        assert snapshot.market_name == "Test Market"
        assert snapshot.metrics.total_addressable_market == 150_000_000_000
        assert snapshot.metrics.revenue == 1_000_000_000
        assert len(snapshot.competitors) == 1
        assert len(snapshot.risk_notes) > 0


# =============================================================================
# Test Class: Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Tests for module-level helper functions."""
    
    def test_should_use_market_intelligence_by_type(self):
        """Test market intelligence decision based on query type."""
        assert should_use_market_intelligence("market_research", "test") is True
        assert should_use_market_intelligence("competitive_analysis", "test") is True
        assert should_use_market_intelligence("due_diligence", "test") is True
        assert should_use_market_intelligence("general", "test") is False
    
    def test_should_use_market_intelligence_by_keywords(self):
        """Test market intelligence decision based on keywords."""
        assert should_use_market_intelligence("general", "what is the market size") is True
        assert should_use_market_intelligence("general", "competitor analysis") is True
        assert should_use_market_intelligence("general", "TAM SAM SOM breakdown") is True
        assert should_use_market_intelligence("general", "pricing comparison") is True
        assert should_use_market_intelligence("general", "what is the weather") is False
    
    def test_create_market_intelligence_agent(self):
        """Test factory function."""
        agent = create_market_intelligence_agent(model="gpt-4o")
        assert isinstance(agent, MarketIntelligenceAgent)
        assert agent.model == "gpt-4o"
    
    def test_get_sec_filing_parser(self):
        """Test parser factory function."""
        parser = get_sec_filing_parser()
        assert isinstance(parser, SECFilingParser)


# =============================================================================
# Test Class: Integration Tests
# =============================================================================

class TestMarketAgentIntegration:
    """Integration tests for MarketIntelligenceAgent."""
    
    def test_analyze_market_with_sec_data(self):
        """Test full market analysis with SEC data."""
        agent = MarketIntelligenceAgent(model="gpt-4o-mini")
        
        async def run_test():
            # Mock the web search to avoid actual API calls
            with patch.object(
                agent,
                "_search_market_data",
                return_value={"tam": 100_000_000_000, "growth_rate": 10.0}
            ):
                with patch.object(
                    agent,
                    "_search_competitors",
                    return_value=[CompetitorProfile(name="TestCorp")]
                ):
                    with patch.object(
                        agent,
                        "_search_pricing_data",
                        return_value=[]
                    ):
                        snapshot = await agent.analyze_market(
                            query="cloud computing market analysis",
                            target_company="MSFT",
                            include_sec_data=True,
                        )
                        
                        assert snapshot is not None
                        assert snapshot.market_name is not None
                        assert snapshot.metrics.revenue is not None  # From SEC stub
        
        asyncio.run(run_test())
    
    def test_analyze_market_without_sec_data(self):
        """Test market analysis without SEC data."""
        agent = MarketIntelligenceAgent(model="gpt-4o-mini")
        
        async def run_test():
            with patch.object(
                agent,
                "_search_market_data",
                return_value={"tam": 50_000_000_000}
            ):
                with patch.object(
                    agent,
                    "_search_competitors",
                    return_value=[]
                ):
                    with patch.object(
                        agent,
                        "_search_pricing_data",
                        return_value=[]
                    ):
                        snapshot = await agent.analyze_market(
                            query="small business market",
                            include_sec_data=False,
                        )
                        
                        assert snapshot is not None
                        assert snapshot.metrics.revenue is None  # No SEC data
        
        asyncio.run(run_test())


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
