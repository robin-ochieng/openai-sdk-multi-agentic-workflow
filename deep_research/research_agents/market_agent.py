"""
Market Intelligence Agent for Deep Research.

Aggregates data from SEC filings and market sources to generate
comprehensive market snapshots with metrics, competitors, and risks.

Features:
- SEC 10-K/10-Q filing parsing (stub API, ready for sec-api integration)
- Market blog and analyst report aggregation via web search
- Revenue, growth rate, TAM/SAM/SOM extraction
- Competitor landscape analysis
- Pricing benchmark collection
- Risk assessment
"""

import os
import re
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlencode, quote_plus

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from agents import Agent, Runner, WebSearchTool

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


# Configure logging
logger = logging.getLogger("deep_research.market_agent")


# SEC API configuration (stub - ready for sec-api.io integration)
SEC_API_KEY = os.getenv("SEC_API_KEY", "")
SEC_API_BASE = "https://api.sec-api.io"


# =============================================================================
# SEC Filing Parser
# =============================================================================

class SECFilingParser:
    """
    Parser for SEC filing text.
    
    Extracts financial metrics, risk factors, market mentions,
    and competitor references from 10-K/10-Q filings.
    """
    
    # Patterns for extracting financial data
    REVENUE_PATTERNS = [
        r"(?:total\s+)?(?:net\s+)?revenue[s]?\s*(?:was|were|of)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?",
        r"revenue[s]?\s*(?:increased|decreased|grew)?\s*(?:to|by)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?",
        r"\$?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?\s*(?:in\s+)?(?:total\s+)?revenue",
    ]
    
    GROWTH_PATTERNS = [
        r"revenue\s+(?:increased|grew|growth)\s*(?:of|by)?\s*([\d.]+)\s*%",
        r"([\d.]+)\s*%\s*(?:revenue\s+)?(?:increase|growth|grew)",
        r"year[- ]over[- ]year\s+(?:revenue\s+)?(?:growth|increase)\s*(?:of)?\s*([\d.]+)\s*%",
    ]
    
    TAM_PATTERNS = [
        r"(?:total\s+)?addressable\s+market\s*(?:of|is|was|estimated\s+at)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:trillion|billion|million|T|B|M)?",
        r"TAM\s*(?:of|is|was|estimated\s+at)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:trillion|billion|million|T|B|M)?",
        r"market\s+(?:size|opportunity)\s*(?:of|is|was|estimated\s+at)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:trillion|billion|million|T|B|M)?",
    ]
    
    COMPETITOR_PATTERNS = [
        r"(?:competitors?|competition)\s+(?:include[s]?|such\s+as|from)\s+([A-Z][a-zA-Z\s,&]+?)(?:\.|,\s*and|\s+and\s+other)",
        r"(?:compete[s]?\s+with|competing\s+with)\s+([A-Z][a-zA-Z\s,&]+?)(?:\.|,)",
    ]
    
    RISK_SECTION_MARKERS = [
        "RISK FACTORS",
        "Item 1A",
        "Risk Factors",
    ]
    
    def __init__(self):
        """Initialize the SEC filing parser."""
        self._compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._compiled_patterns["revenue"] = [
            re.compile(p, re.IGNORECASE) for p in self.REVENUE_PATTERNS
        ]
        self._compiled_patterns["growth"] = [
            re.compile(p, re.IGNORECASE) for p in self.GROWTH_PATTERNS
        ]
        self._compiled_patterns["tam"] = [
            re.compile(p, re.IGNORECASE) for p in self.TAM_PATTERNS
        ]
        self._compiled_patterns["competitors"] = [
            re.compile(p, re.IGNORECASE) for p in self.COMPETITOR_PATTERNS
        ]
    
    def parse_filing(self, text: str, filing_type: str = "10-K") -> SECFilingData:
        """
        Parse SEC filing text and extract structured data.
        
        Args:
            text: Raw filing text.
            filing_type: Type of filing (10-K, 10-Q, etc.).
        
        Returns:
            SECFilingData with extracted information.
        """
        logger.info(f"Parsing {filing_type} filing ({len(text)} chars)")
        
        # Extract company name (usually at the start)
        company_name = self._extract_company_name(text)
        
        # Extract financial metrics
        revenue = self._extract_revenue(text)
        revenue_growth = self._extract_growth_rate(text)
        
        # Extract market size mentions
        market_mentions = self._extract_market_size(text)
        
        # Extract competitors
        competitors = self._extract_competitors(text)
        
        # Extract risk factors
        risk_factors = self._extract_risk_factors(text)
        
        return SECFilingData(
            company_name=company_name,
            filing_type=filing_type,
            revenue=revenue,
            revenue_growth=revenue_growth,
            market_size_mentions=market_mentions,
            competitor_mentions=competitors,
            risk_factors=risk_factors,
        )
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name from filing."""
        # Look for common patterns
        patterns = [
            r"FORM\s+10-K\s+.*?([A-Z][A-Za-z\s,\.]+(?:Inc|Corp|LLC|Ltd|Company|Co)\.?)",
            r"([A-Z][A-Za-z\s]+(?:Inc|Corp|LLC|Ltd|Company|Co)\.?)\s+\(Exact name",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:5000], re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Company"
    
    def _extract_revenue(self, text: str) -> Optional[float]:
        """Extract revenue figure from filing."""
        for pattern in self._compiled_patterns["revenue"]:
            match = pattern.search(text)
            if match:
                value_str = match.group(1).replace(",", "")
                try:
                    value = float(value_str)
                    # Apply multiplier based on context
                    context = match.group(0).lower()
                    if "trillion" in context or " t " in context.lower():
                        value *= 1_000_000_000_000
                    elif "billion" in context or " b " in context.lower():
                        value *= 1_000_000_000
                    elif "million" in context or " m " in context.lower():
                        value *= 1_000_000
                    return value
                except ValueError:
                    continue
        return None
    
    def _extract_growth_rate(self, text: str) -> Optional[float]:
        """Extract revenue growth rate from filing."""
        for pattern in self._compiled_patterns["growth"]:
            match = pattern.search(text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def _extract_market_size(self, text: str) -> List[str]:
        """Extract market size mentions from filing."""
        mentions = []
        for pattern in self._compiled_patterns["tam"]:
            for match in pattern.finditer(text):
                mentions.append(match.group(0).strip())
        return mentions[:5]  # Limit to top 5
    
    def _extract_competitors(self, text: str) -> List[str]:
        """Extract competitor names from filing."""
        competitors = set()
        for pattern in self._compiled_patterns["competitors"]:
            for match in pattern.finditer(text):
                # Split by common delimiters
                names = re.split(r",\s*|\s+and\s+", match.group(1))
                for name in names:
                    name = name.strip()
                    if len(name) > 2 and name[0].isupper():
                        competitors.add(name)
        return list(competitors)[:10]  # Limit to top 10
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract key risk factors from filing."""
        risks = []
        
        # Find risk section
        risk_section = ""
        for marker in self.RISK_SECTION_MARKERS:
            idx = text.find(marker)
            if idx != -1:
                # Get next ~10000 chars as risk section
                risk_section = text[idx:idx + 10000]
                break
        
        if not risk_section:
            return []
        
        # Extract bullet points or numbered items
        risk_patterns = [
            r"(?:•|◦|▪|○)\s*([A-Z][^•◦▪○\n]{20,200})",
            r"\n\s*(?:\d+\.|\([a-z]\))\s*([A-Z][^\n]{20,200})",
        ]
        
        for pattern in risk_patterns:
            for match in re.finditer(pattern, risk_section):
                risk_text = match.group(1).strip()
                if len(risk_text) > 30:
                    risks.append(risk_text)
        
        return risks[:10]  # Limit to top 10 risks
    
    def parse_financial_value(self, text: str) -> Optional[float]:
        """
        Parse a financial value string into a number.
        
        Handles formats like:
        - "$1.5 billion"
        - "1,500,000"
        - "$500M"
        """
        text = text.strip().replace(",", "").replace("$", "")
        
        # Find number and multiplier
        match = re.match(r"([\d.]+)\s*(trillion|billion|million|T|B|M)?", text, re.IGNORECASE)
        if not match:
            return None
        
        try:
            value = float(match.group(1))
            multiplier = match.group(2)
            
            if multiplier:
                multiplier = multiplier.lower()
                if multiplier in ("trillion", "t"):
                    value *= 1_000_000_000_000
                elif multiplier in ("billion", "b"):
                    value *= 1_000_000_000
                elif multiplier in ("million", "m"):
                    value *= 1_000_000
            
            return value
        except ValueError:
            return None


# =============================================================================
# SEC API Client (Stub)
# =============================================================================

class SECAPIClient:
    """
    Client for SEC API (sec-api.io or similar).
    
    This is a stub implementation that can be replaced with
    actual API integration when sec-api credentials are available.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize SEC API client."""
        self.api_key = api_key or SEC_API_KEY
        self.base_url = SEC_API_BASE
        self.parser = SECFilingParser()
    
    async def get_filing(
        self,
        ticker: str,
        filing_type: str = "10-K",
        fiscal_year: Optional[int] = None,
    ) -> Optional[SECFilingData]:
        """
        Fetch and parse SEC filing for a company.
        
        This is a stub that returns mock data.
        Replace with actual API call when credentials available.
        
        Args:
            ticker: Stock ticker symbol.
            filing_type: Type of filing (10-K, 10-Q).
            fiscal_year: Fiscal year for filing.
        
        Returns:
            Parsed SEC filing data or None.
        """
        logger.info(f"Fetching {filing_type} for {ticker} (stub mode)")
        
        # Stub implementation - return mock data
        # In production, this would call sec-api.io
        if not self.api_key:
            logger.warning("SEC API key not configured, using stub data")
            return self._generate_stub_filing(ticker, filing_type, fiscal_year)
        
        # Actual API call would go here
        # url = f"{self.base_url}/filings/10k/{ticker}"
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        #     if response.status_code == 200:
        #         return self.parser.parse_filing(response.text, filing_type)
        
        return self._generate_stub_filing(ticker, filing_type, fiscal_year)
    
    def _generate_stub_filing(
        self,
        ticker: str,
        filing_type: str,
        fiscal_year: Optional[int],
    ) -> SECFilingData:
        """Generate stub filing data for testing."""
        current_year = fiscal_year or datetime.now().year - 1
        
        # Sample company data based on ticker patterns
        company_data = {
            "AAPL": ("Apple Inc.", 394_328_000_000, 8.1),
            "MSFT": ("Microsoft Corporation", 211_915_000_000, 16.4),
            "GOOGL": ("Alphabet Inc.", 282_836_000_000, 9.0),
            "AMZN": ("Amazon.com, Inc.", 574_785_000_000, 11.8),
            "NVDA": ("NVIDIA Corporation", 60_922_000_000, 125.9),
        }
        
        if ticker.upper() in company_data:
            name, revenue, growth = company_data[ticker.upper()]
        else:
            name = f"{ticker} Corporation"
            revenue = 10_000_000_000  # $10B default
            growth = 5.0
        
        return SECFilingData(
            company_name=name,
            ticker=ticker.upper(),
            filing_type=filing_type,
            fiscal_year=current_year,
            revenue=revenue,
            revenue_growth=growth,
            risk_factors=[
                "Competition in our industry is intense",
                "Our business is subject to regulatory risks",
                "Economic conditions may adversely affect demand",
                "We depend on key personnel",
                "Cybersecurity threats pose ongoing risks",
            ],
            competitor_mentions=["Microsoft", "Google", "Amazon"],
            market_size_mentions=[
                f"Total addressable market estimated at ${revenue * 5 / 1_000_000_000:.0f} billion"
            ],
        )
    
    async def search_filings(
        self,
        query: str,
        filing_types: List[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant SEC filings.
        
        Stub implementation returns empty list.
        """
        logger.info(f"Searching SEC filings for: {query}")
        return []


# =============================================================================
# Market Intelligence Agent
# =============================================================================

class MarketIntelligenceAgent:
    """
    Agent for market research and competitive intelligence.
    
    Combines SEC filing data with web search to build
    comprehensive market snapshots.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the market intelligence agent.
        
        Args:
            model: Model for LLM-based operations.
        """
        self.model = model
        self.sec_client = SECAPIClient()
        self.filing_parser = SECFilingParser()
        self._web_search_agent = None
        self._market_analyst_agent = None
    
    @property
    def web_search_agent(self) -> Agent:
        """Lazy-load web search agent."""
        if self._web_search_agent is None:
            self._web_search_agent = Agent(
                name="MarketWebSearchAgent",
                instructions=(
                    "You are a market research analyst. Search for market data, "
                    "industry reports, competitor information, and pricing data. "
                    "Focus on reputable sources like industry publications, "
                    "analyst reports, and company websites. "
                    "Extract specific numbers for TAM/SAM/SOM, growth rates, "
                    "market share, and pricing information."
                ),
                model=self.model,
                tools=[WebSearchTool()],
            )
        return self._web_search_agent
    
    @property
    def market_analyst_agent(self) -> Agent:
        """Lazy-load market analyst agent for synthesis."""
        if self._market_analyst_agent is None:
            self._market_analyst_agent = Agent(
                name="MarketAnalystAgent",
                instructions=(
                    "You are a senior market analyst. Synthesize market data "
                    "from multiple sources into actionable insights. "
                    "Identify key market trends, competitive dynamics, "
                    "and strategic opportunities. Be specific with numbers "
                    "and cite your reasoning."
                ),
                model=self.model,
            )
        return self._market_analyst_agent
    
    async def analyze_market(
        self,
        query: str,
        target_company: Optional[str] = None,
        target_market: Optional[str] = None,
        include_sec_data: bool = True,
    ) -> MarketSnapshot:
        """
        Perform comprehensive market analysis.
        
        Args:
            query: Market research query.
            target_company: Specific company to analyze.
            target_market: Target market or industry.
            include_sec_data: Whether to include SEC filing data.
        
        Returns:
            MarketSnapshot with comprehensive analysis.
        """
        start_time = time.time()
        logger.info(f"Starting market analysis: {query}")
        
        # Initialize snapshot
        market_name = target_market or self._extract_market_name(query)
        snapshot = MarketSnapshot(
            market_name=market_name,
            data_sources=[],
        )
        
        # Gather data from multiple sources in parallel
        tasks = []
        
        # Web search for market data
        tasks.append(self._search_market_data(query, market_name))
        
        # Search for competitors
        tasks.append(self._search_competitors(query, market_name))
        
        # Search for pricing data
        tasks.append(self._search_pricing_data(query, market_name))
        
        # Get SEC data if requested and company specified
        if include_sec_data and target_company:
            tasks.append(self._get_sec_insights(target_company))
        
        # Run all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        market_data = results[0] if not isinstance(results[0], Exception) else {}
        competitor_data = results[1] if not isinstance(results[1], Exception) else []
        pricing_data = results[2] if not isinstance(results[2], Exception) else []
        sec_data = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None
        
        # Build snapshot from gathered data
        snapshot = self._build_snapshot(
            market_name=market_name,
            market_data=market_data,
            competitor_data=competitor_data,
            pricing_data=pricing_data,
            sec_data=sec_data,
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Market analysis complete in {elapsed:.2f}s")
        
        return snapshot
    
    def _extract_market_name(self, query: str) -> str:
        """Extract market name from query."""
        # Common market indicators
        market_words = ["market", "industry", "sector", "space"]
        words = query.lower().split()
        
        for i, word in enumerate(words):
            if word in market_words and i > 0:
                # Return preceding words as market name
                return " ".join(words[max(0, i-3):i]).title()
        
        # Default to first few significant words
        return " ".join(words[:3]).title() + " Market"
    
    async def _search_market_data(
        self,
        query: str,
        market_name: str,
    ) -> Dict[str, Any]:
        """Search for market sizing and growth data."""
        try:
            search_query = f"{market_name} market size TAM SAM growth rate 2024"
            
            result = await Runner.run(
                self.web_search_agent,
                f"Find market size data for: {search_query}. "
                "Look for TAM (Total Addressable Market), SAM (Serviceable Addressable Market), "
                "market growth rates, and CAGR projections. "
                "Cite specific numbers and sources."
            )
            
            # Parse the response for metrics
            return self._parse_market_data(result.final_output)
            
        except Exception as e:
            logger.error(f"Market data search failed: {e}")
            return {}
    
    def _parse_market_data(self, text: str) -> Dict[str, Any]:
        """Parse market data from search results."""
        data = {
            "tam": None,
            "sam": None,
            "som": None,
            "growth_rate": None,
            "cagr": None,
            "raw_text": text,
        }
        
        # Extract TAM - allows words between keyword and value (e.g., "TAM is $150 billion")
        tam_match = re.search(
            r"(?:TAM|total\s+addressable\s+market)[^$\d]*\$?\s*([\d.]+)\s*(trillion|billion|million|T|B|M)?",
            text, re.IGNORECASE
        )
        if tam_match:
            data["tam"] = self.filing_parser.parse_financial_value(
                f"{tam_match.group(1)} {tam_match.group(2) or ''}"
            )
        
        # Extract growth rate - allows words between keyword and value
        growth_match = re.search(
            r"(?:growth\s+rate|CAGR)[^0-9]*([\d.]+)\s*%",
            text, re.IGNORECASE
        )
        if growth_match:
            try:
                data["growth_rate"] = float(growth_match.group(1))
            except ValueError:
                pass
        
        return data
    
    async def _search_competitors(
        self,
        query: str,
        market_name: str,
    ) -> List[CompetitorProfile]:
        """Search for competitor information."""
        try:
            result = await Runner.run(
                self.web_search_agent,
                f"Find the top competitors in the {market_name}. "
                "For each competitor, find: company name, market position, "
                "estimated revenue, market share if available, key products, "
                "and strengths/weaknesses."
            )
            
            return self._parse_competitors(result.final_output)
            
        except Exception as e:
            logger.error(f"Competitor search failed: {e}")
            return []
    
    def _parse_competitors(self, text: str) -> List[CompetitorProfile]:
        """Parse competitor data from search results."""
        competitors = []
        
        # Look for company names with context
        # This is a simplified parser - could use NLP for better results
        company_patterns = [
            r"(?:^|\n)\s*(?:\d+\.\s*)?([A-Z][A-Za-z0-9\s]+(?:Inc|Corp|Ltd|LLC)?)\s*[-–:]",
            r"\*\*([A-Z][A-Za-z0-9\s]+)\*\*",
        ]
        
        seen_names = set()
        for pattern in company_patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip()
                if name and len(name) > 2 and name not in seen_names:
                    seen_names.add(name)
                    competitors.append(CompetitorProfile(
                        name=name,
                        market_position="competitor",
                    ))
        
        return competitors[:10]
    
    async def _search_pricing_data(
        self,
        query: str,
        market_name: str,
    ) -> List[PricingBenchmark]:
        """Search for pricing benchmark data."""
        try:
            result = await Runner.run(
                self.web_search_agent,
                f"Find pricing information for products/services in the {market_name}. "
                "Look for: price ranges, pricing models (subscription, per-seat, etc.), "
                "average prices, and pricing trends."
            )
            
            return self._parse_pricing(result.final_output, market_name)
            
        except Exception as e:
            logger.error(f"Pricing search failed: {e}")
            return []
    
    def _parse_pricing(self, text: str, market_name: str) -> List[PricingBenchmark]:
        """Parse pricing data from search results."""
        benchmarks = []
        
        # Look for price patterns
        price_pattern = r"\$\s*([\d,]+(?:\.\d{2})?)\s*(?:[-–to]+\s*\$?\s*([\d,]+(?:\.\d{2})?))?\s*(?:per\s+)?(\w+)?"
        
        for match in re.finditer(price_pattern, text):
            try:
                low = float(match.group(1).replace(",", ""))
                high = float(match.group(2).replace(",", "")) if match.group(2) else None
                unit = match.group(3) or "unit"
                
                benchmarks.append(PricingBenchmark(
                    product_category=market_name,
                    price_range_low=low,
                    price_range_high=high or low * 2,
                    average_price=(low + (high or low)) / 2,
                    pricing_model=f"per {unit}" if unit else "unknown",
                ))
            except (ValueError, AttributeError):
                continue
        
        return benchmarks[:5]
    
    async def _get_sec_insights(
        self,
        company: str,
    ) -> Optional[SECFilingData]:
        """Get SEC filing insights for a company."""
        # Extract ticker if it looks like one
        ticker = company.upper() if len(company) <= 5 else None
        
        if ticker:
            return await self.sec_client.get_filing(ticker)
        
        return None
    
    def _build_snapshot(
        self,
        market_name: str,
        market_data: Dict[str, Any],
        competitor_data: List[CompetitorProfile],
        pricing_data: List[PricingBenchmark],
        sec_data: Optional[SECFilingData],
    ) -> MarketSnapshot:
        """Build MarketSnapshot from gathered data."""
        # Build metrics
        metrics = MarketMetrics(
            total_addressable_market=market_data.get("tam"),
            serviceable_addressable_market=market_data.get("sam"),
            serviceable_obtainable_market=market_data.get("som"),
            market_growth_rate=market_data.get("growth_rate"),
            cagr=market_data.get("cagr"),
        )
        
        # Add SEC data if available
        if sec_data:
            metrics.revenue = sec_data.revenue
            metrics.revenue_growth = sec_data.revenue_growth
            metrics.data_confidence = DataConfidence.HIGH
        
        # Build risk notes from SEC data
        risk_notes = []
        if sec_data and sec_data.risk_factors:
            for risk_text in sec_data.risk_factors[:5]:
                # Categorize risk
                category = "general"
                if "competition" in risk_text.lower():
                    category = "competitive"
                elif "regulat" in risk_text.lower():
                    category = "regulatory"
                elif "economic" in risk_text.lower():
                    category = "economic"
                elif "cyber" in risk_text.lower() or "security" in risk_text.lower():
                    category = "cybersecurity"
                
                risk_notes.append(RiskNote(
                    category=category,
                    description=risk_text[:200],
                    level=RiskLevel.MEDIUM,
                    source="SEC 10-K Filing",
                ))
        
        # Determine market trend
        market_trend = MarketTrend.STABLE
        if metrics.market_growth_rate:
            if metrics.market_growth_rate > 20:
                market_trend = MarketTrend.GROWING
            elif metrics.market_growth_rate < 0:
                market_trend = MarketTrend.DECLINING
        
        # Build data sources list
        data_sources = []
        if market_data.get("raw_text"):
            data_sources.append("Web Search - Market Reports")
        if competitor_data:
            data_sources.append("Web Search - Competitor Analysis")
        if pricing_data:
            data_sources.append("Web Search - Pricing Data")
        if sec_data:
            data_sources.append(f"SEC {sec_data.filing_type} Filing")
        
        # Calculate confidence score
        confidence = 0.3  # Base
        if metrics.total_addressable_market:
            confidence += 0.2
        if competitor_data:
            confidence += 0.15
        if sec_data:
            confidence += 0.25
        if pricing_data:
            confidence += 0.1
        
        return MarketSnapshot(
            market_name=market_name,
            market_trend=market_trend,
            metrics=metrics,
            competitors=competitor_data,
            pricing_benchmarks=pricing_data,
            risk_notes=risk_notes,
            overall_risk_level=RiskLevel.MEDIUM if risk_notes else RiskLevel.LOW,
            data_sources=data_sources,
            data_freshness="recent" if sec_data else "varies",
            confidence_score=min(confidence, 1.0),
        )
    
    def parse_filing_text(self, text: str, filing_type: str = "10-K") -> SECFilingData:
        """
        Parse raw SEC filing text.
        
        Public method for direct filing parsing without API.
        
        Args:
            text: Raw filing text.
            filing_type: Type of filing.
        
        Returns:
            Parsed SECFilingData.
        """
        return self.filing_parser.parse_filing(text, filing_type)


# =============================================================================
# Factory Functions
# =============================================================================

def create_market_intelligence_agent(
    model: str = "gpt-4o-mini"
) -> MarketIntelligenceAgent:
    """
    Factory function to create a MarketIntelligenceAgent.
    
    Args:
        model: Model for LLM operations.
    
    Returns:
        Configured MarketIntelligenceAgent instance.
    """
    return MarketIntelligenceAgent(model=model)


def should_use_market_intelligence(query_type: str, query: str) -> bool:
    """
    Determine if market intelligence should be used based on query.
    
    Args:
        query_type: Query type from QueryAnalyzerAgent.
        query: Original query string.
    
    Returns:
        True if market intelligence is recommended.
    """
    # Query types that need market intelligence
    market_types = {
        "market_research",
        "competitive_analysis",
        "due_diligence",
        "trend_analysis",
    }
    
    if query_type.lower() in market_types:
        return True
    
    # Keywords that suggest market research
    market_keywords = [
        "market size",
        "market share",
        "tam",
        "sam",
        "som",
        "addressable market",
        "competitor",
        "competitive",
        "pricing",
        "revenue",
        "growth rate",
        "industry analysis",
        "market trend",
        "market opportunity",
        "market landscape",
        "market leader",
    ]
    
    query_lower = query.lower()
    return any(kw in query_lower for kw in market_keywords)


def get_sec_filing_parser() -> SECFilingParser:
    """Get a SECFilingParser instance."""
    return SECFilingParser()
