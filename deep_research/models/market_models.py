"""
Market Intelligence Models for Deep Research Agent.

Provides Pydantic schemas for market research including:
- MarketSnapshot: Comprehensive market analysis with metrics
- CompetitorProfile: Individual competitor information
- MarketMetrics: Key financial and market metrics
- PricingBenchmark: Pricing comparison data
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class MarketTrend(str, Enum):
    """Market trend indicators."""
    
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    EMERGING = "emerging"
    DISRUPTED = "disrupted"


class RiskLevel(str, Enum):
    """Risk level classification."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataConfidence(str, Enum):
    """Confidence level for extracted data."""
    
    HIGH = "high"        # From verified sources (SEC filings, official reports)
    MEDIUM = "medium"    # From reputable sources (analyst reports, trusted blogs)
    LOW = "low"          # From general sources (news, estimates)
    ESTIMATED = "estimated"  # Calculated or inferred


class CompetitorProfile(BaseModel):
    """Profile of a market competitor."""
    
    name: str = Field(
        ...,
        description="Company name"
    )
    ticker: Optional[str] = Field(
        default=None,
        description="Stock ticker symbol if public"
    )
    market_position: str = Field(
        default="competitor",
        description="Market position (leader, challenger, niche, emerging)"
    )
    estimated_market_share: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Estimated market share percentage"
    )
    estimated_revenue: Optional[float] = Field(
        default=None,
        ge=0,
        description="Estimated annual revenue in USD"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Key competitive strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Key competitive weaknesses"
    )
    key_products: List[str] = Field(
        default_factory=list,
        description="Main products or services"
    )
    founded_year: Optional[int] = Field(
        default=None,
        description="Year company was founded"
    )
    headquarters: Optional[str] = Field(
        default=None,
        description="Company headquarters location"
    )
    employee_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated number of employees"
    )
    funding_total: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total funding raised (for private companies)"
    )
    
    @property
    def revenue_formatted(self) -> str:
        """Format revenue in human-readable form."""
        if self.estimated_revenue is None:
            return "N/A"
        if self.estimated_revenue >= 1_000_000_000:
            return f"${self.estimated_revenue / 1_000_000_000:.1f}B"
        elif self.estimated_revenue >= 1_000_000:
            return f"${self.estimated_revenue / 1_000_000:.1f}M"
        else:
            return f"${self.estimated_revenue:,.0f}"


class PricingBenchmark(BaseModel):
    """Pricing benchmark data."""
    
    product_category: str = Field(
        ...,
        description="Product or service category"
    )
    price_range_low: Optional[float] = Field(
        default=None,
        ge=0,
        description="Low end of price range"
    )
    price_range_high: Optional[float] = Field(
        default=None,
        ge=0,
        description="High end of price range"
    )
    average_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="Average market price"
    )
    pricing_model: str = Field(
        default="unknown",
        description="Pricing model (subscription, per-seat, usage-based, etc.)"
    )
    currency: str = Field(
        default="USD",
        description="Currency for prices"
    )
    price_trend: MarketTrend = Field(
        default=MarketTrend.STABLE,
        description="Price trend direction"
    )
    notes: List[str] = Field(
        default_factory=list,
        description="Additional pricing notes"
    )
    
    @property
    def price_range_formatted(self) -> str:
        """Format price range in human-readable form."""
        if self.price_range_low is None and self.price_range_high is None:
            return "N/A"
        low = f"${self.price_range_low:,.0f}" if self.price_range_low else "?"
        high = f"${self.price_range_high:,.0f}" if self.price_range_high else "?"
        return f"{low} - {high} {self.currency}"


class RiskNote(BaseModel):
    """Market risk note."""
    
    category: str = Field(
        ...,
        description="Risk category (regulatory, competitive, technology, etc.)"
    )
    description: str = Field(
        ...,
        description="Risk description"
    )
    level: RiskLevel = Field(
        default=RiskLevel.MEDIUM,
        description="Risk severity level"
    )
    mitigation: Optional[str] = Field(
        default=None,
        description="Potential mitigation strategies"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source of risk information"
    )


class MarketMetrics(BaseModel):
    """Key market metrics extracted from filings and reports."""
    
    # Market sizing
    total_addressable_market: Optional[float] = Field(
        default=None,
        ge=0,
        description="TAM in USD"
    )
    serviceable_addressable_market: Optional[float] = Field(
        default=None,
        ge=0,
        description="SAM in USD"
    )
    serviceable_obtainable_market: Optional[float] = Field(
        default=None,
        ge=0,
        description="SOM in USD"
    )
    
    # Growth metrics
    market_growth_rate: Optional[float] = Field(
        default=None,
        description="Annual market growth rate percentage"
    )
    cagr: Optional[float] = Field(
        default=None,
        description="Compound Annual Growth Rate percentage"
    )
    
    # Company-specific metrics (from SEC filings)
    revenue: Optional[float] = Field(
        default=None,
        ge=0,
        description="Annual revenue in USD"
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Year-over-year revenue growth percentage"
    )
    gross_margin: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Gross margin percentage"
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin percentage"
    )
    net_income: Optional[float] = Field(
        default=None,
        description="Net income in USD"
    )
    
    # Additional metrics
    customer_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of customers"
    )
    average_revenue_per_user: Optional[float] = Field(
        default=None,
        ge=0,
        description="ARPU in USD"
    )
    churn_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Customer churn rate percentage"
    )
    
    # Confidence and sourcing
    data_confidence: DataConfidence = Field(
        default=DataConfidence.MEDIUM,
        description="Confidence level for the metrics"
    )
    data_year: Optional[int] = Field(
        default=None,
        description="Year the data corresponds to"
    )
    
    @property
    def tam_formatted(self) -> str:
        """Format TAM in human-readable form."""
        return self._format_currency(self.total_addressable_market)
    
    @property
    def sam_formatted(self) -> str:
        """Format SAM in human-readable form."""
        return self._format_currency(self.serviceable_addressable_market)
    
    @property
    def som_formatted(self) -> str:
        """Format SOM in human-readable form."""
        return self._format_currency(self.serviceable_obtainable_market)
    
    @property
    def revenue_formatted(self) -> str:
        """Format revenue in human-readable form."""
        return self._format_currency(self.revenue)
    
    def _format_currency(self, value: Optional[float]) -> str:
        """Format currency value."""
        if value is None:
            return "N/A"
        if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.1f}T"
        elif value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        else:
            return f"${value:,.0f}"


class MarketSnapshot(BaseModel):
    """
    Comprehensive market intelligence snapshot.
    
    Contains aggregated market data including:
    - Key metrics (TAM/SAM/SOM, revenue, growth rates)
    - Competitor analysis
    - Pricing benchmarks
    - Risk assessment
    """
    
    # Identification
    market_name: str = Field(
        ...,
        description="Name of the market or industry"
    )
    analysis_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date of analysis"
    )
    
    # Market overview
    market_description: str = Field(
        default="",
        description="Brief description of the market"
    )
    market_trend: MarketTrend = Field(
        default=MarketTrend.STABLE,
        description="Overall market trend"
    )
    key_drivers: List[str] = Field(
        default_factory=list,
        description="Key market growth drivers"
    )
    key_challenges: List[str] = Field(
        default_factory=list,
        description="Key market challenges"
    )
    
    # Core metrics
    metrics: MarketMetrics = Field(
        default_factory=MarketMetrics,
        description="Key market metrics"
    )
    
    # Competitive landscape
    competitors: List[CompetitorProfile] = Field(
        default_factory=list,
        description="List of competitors"
    )
    market_concentration: str = Field(
        default="fragmented",
        description="Market concentration (consolidated, fragmented, oligopoly)"
    )
    
    # Pricing intelligence
    pricing_benchmarks: List[PricingBenchmark] = Field(
        default_factory=list,
        description="Pricing benchmark data"
    )
    
    # Risk assessment
    risk_notes: List[RiskNote] = Field(
        default_factory=list,
        description="Market risk notes"
    )
    overall_risk_level: RiskLevel = Field(
        default=RiskLevel.MEDIUM,
        description="Overall market risk level"
    )
    
    # Data quality
    data_sources: List[str] = Field(
        default_factory=list,
        description="Sources used for this analysis"
    )
    data_freshness: str = Field(
        default="unknown",
        description="How recent the data is"
    )
    confidence_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the analysis"
    )
    
    @property
    def competitor_count(self) -> int:
        """Get number of tracked competitors."""
        return len(self.competitors)
    
    @property
    def high_risk_count(self) -> int:
        """Count high or critical risks."""
        return sum(
            1 for r in self.risk_notes 
            if r.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        )
    
    def get_market_leaders(self, top_n: int = 3) -> List[CompetitorProfile]:
        """Get top competitors by market share."""
        sorted_competitors = sorted(
            [c for c in self.competitors if c.estimated_market_share is not None],
            key=lambda c: c.estimated_market_share or 0,
            reverse=True
        )
        return sorted_competitors[:top_n]
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for reports."""
        return {
            "market_name": self.market_name,
            "analysis_date": self.analysis_date.isoformat(),
            "market_trend": self.market_trend.value,
            "tam": self.metrics.tam_formatted,
            "sam": self.metrics.sam_formatted,
            "som": self.metrics.som_formatted,
            "market_growth_rate": f"{self.metrics.market_growth_rate:.1f}%" if self.metrics.market_growth_rate else "N/A",
            "competitor_count": self.competitor_count,
            "market_leaders": [c.name for c in self.get_market_leaders()],
            "high_risks": self.high_risk_count,
            "overall_risk": self.overall_risk_level.value,
            "confidence": f"{self.confidence_score * 100:.0f}%",
        }
    
    def to_report_section(self) -> str:
        """Generate markdown section for research reports."""
        lines = [
            f"## Market Intelligence: {self.market_name}",
            "",
            f"**Analysis Date:** {self.analysis_date.strftime('%Y-%m-%d')}",
            f"**Market Trend:** {self.market_trend.value.title()}",
            f"**Confidence:** {self.confidence_score * 100:.0f}%",
            "",
            "### Market Size",
            f"- **TAM:** {self.metrics.tam_formatted}",
            f"- **SAM:** {self.metrics.sam_formatted}",
            f"- **SOM:** {self.metrics.som_formatted}",
        ]
        
        if self.metrics.market_growth_rate:
            lines.append(f"- **Growth Rate:** {self.metrics.market_growth_rate:.1f}% YoY")
        if self.metrics.cagr:
            lines.append(f"- **CAGR:** {self.metrics.cagr:.1f}%")
        
        if self.key_drivers:
            lines.extend(["", "### Key Drivers"])
            for driver in self.key_drivers:
                lines.append(f"- {driver}")
        
        if self.competitors:
            lines.extend(["", "### Competitive Landscape"])
            lines.append(f"**Market Concentration:** {self.market_concentration.title()}")
            lines.append("")
            for comp in self.get_market_leaders(5):
                share = f" ({comp.estimated_market_share:.1f}%)" if comp.estimated_market_share else ""
                lines.append(f"- **{comp.name}**{share} - {comp.market_position.title()}")
        
        if self.pricing_benchmarks:
            lines.extend(["", "### Pricing Benchmarks"])
            for pb in self.pricing_benchmarks:
                lines.append(f"- **{pb.product_category}:** {pb.price_range_formatted} ({pb.pricing_model})")
        
        if self.risk_notes:
            lines.extend(["", "### Risk Assessment"])
            lines.append(f"**Overall Risk Level:** {self.overall_risk_level.value.upper()}")
            for risk in self.risk_notes:
                emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(risk.level.value, "⚪")
                lines.append(f"- {emoji} **{risk.category}:** {risk.description}")
        
        if self.data_sources:
            lines.extend(["", "### Data Sources"])
            for source in self.data_sources:
                lines.append(f"- {source}")
        
        return "\n".join(lines)


class SECFilingData(BaseModel):
    """Parsed data from SEC filing (10-K, 10-Q, etc.)."""
    
    company_name: str = Field(..., description="Company name from filing")
    ticker: Optional[str] = Field(default=None, description="Stock ticker")
    filing_type: str = Field(default="10-K", description="Type of filing")
    filing_date: Optional[str] = Field(default=None, description="Filing date")
    fiscal_year: Optional[int] = Field(default=None, description="Fiscal year")
    
    # Financial metrics
    revenue: Optional[float] = Field(default=None, description="Total revenue")
    revenue_growth: Optional[float] = Field(default=None, description="Revenue growth %")
    gross_profit: Optional[float] = Field(default=None, description="Gross profit")
    operating_income: Optional[float] = Field(default=None, description="Operating income")
    net_income: Optional[float] = Field(default=None, description="Net income")
    total_assets: Optional[float] = Field(default=None, description="Total assets")
    total_liabilities: Optional[float] = Field(default=None, description="Total liabilities")
    
    # Business segments
    segments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Business segment breakdown"
    )
    
    # Risk factors
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Key risk factors from filing"
    )
    
    # Market data mentioned
    market_size_mentions: List[str] = Field(
        default_factory=list,
        description="Market size mentions from filing"
    )
    competitor_mentions: List[str] = Field(
        default_factory=list,
        description="Competitors mentioned"
    )
    
    # Raw text for reference
    raw_excerpts: Dict[str, str] = Field(
        default_factory=dict,
        description="Key text excerpts by section"
    )


class MarketIntelligenceQuery(BaseModel):
    """Query parameters for market intelligence."""
    
    query: str = Field(
        ...,
        min_length=3,
        description="Market research query"
    )
    target_company: Optional[str] = Field(
        default=None,
        description="Specific company to analyze"
    )
    target_market: Optional[str] = Field(
        default=None,
        description="Target market or industry"
    )
    include_competitors: bool = Field(
        default=True,
        description="Include competitor analysis"
    )
    include_pricing: bool = Field(
        default=True,
        description="Include pricing benchmarks"
    )
    include_risks: bool = Field(
        default=True,
        description="Include risk assessment"
    )
    data_sources: List[str] = Field(
        default_factory=lambda: ["sec_filings", "web_search"],
        description="Data sources to use"
    )
