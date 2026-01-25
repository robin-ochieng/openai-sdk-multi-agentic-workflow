"""
Deep Research Agent API - Configuration Module
Centralized settings using Pydantic BaseSettings for environment variable management.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Supports .env file loading via python-dotenv.
    """
    
    # ==========================================
    # Application
    # ==========================================
    app_name: str = "Deep Research Agent API"
    app_version: str = "2.0.0"
    environment: str = Field(default="development", description="development | staging | production")
    debug: bool = Field(default=True, description="Enable debug mode")
    
    # ==========================================
    # Server
    # ==========================================
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    
    # ==========================================
    # CORS
    # ==========================================
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    
    # ==========================================
    # Supabase
    # ==========================================
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_KEY")
    supabase_jwt_secret: Optional[str] = Field(default=None, alias="SUPABASE_JWT_SECRET")
    
    # Fallback to NEXT_PUBLIC_ variants
    next_public_supabase_url: Optional[str] = Field(default=None, alias="NEXT_PUBLIC_SUPABASE_URL")
    next_public_supabase_anon_key: Optional[str] = Field(default=None, alias="NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    @property
    def effective_supabase_url(self) -> Optional[str]:
        """Get Supabase URL from either env var format."""
        return self.supabase_url or self.next_public_supabase_url
    
    @property
    def effective_supabase_anon_key(self) -> Optional[str]:
        """Get Supabase anon key from either env var format."""
        return self.supabase_anon_key or self.next_public_supabase_anon_key
    
    # ==========================================
    # OpenAI
    # ==========================================
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    
    # ==========================================
    # Rate Limiting (requests per time window)
    # ==========================================
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    
    # Tier-based limits (per day for research, per minute for API)
    rate_limit_free_research_per_day: int = Field(default=2)
    rate_limit_pro_research_per_day: int = Field(default=20)
    rate_limit_enterprise_research_per_day: int = Field(default=-1, description="-1 = unlimited")
    
    rate_limit_free_api_per_minute: int = Field(default=10)
    rate_limit_pro_api_per_minute: int = Field(default=60)
    rate_limit_enterprise_api_per_minute: int = Field(default=300)
    
    # Anonymous user limits
    rate_limit_anonymous_research_per_day: int = Field(default=2)
    rate_limit_anonymous_api_per_minute: int = Field(default=5)
    
    # ==========================================
    # JWT / Auth
    # ==========================================
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_audience: str = Field(default="authenticated", description="Expected JWT audience")
    
    # ==========================================
    # Email (Gmail)
    # ==========================================
    gmail_email: Optional[str] = Field(default=None, alias="GMAIL_EMAIL")
    gmail_app_password: Optional[str] = Field(default=None, alias="GMAIL_APP_PASSWORD")
    
    # ==========================================
    # LangSmith Tracing
    # ==========================================
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="deep-research-agent", alias="LANGCHAIN_PROJECT")
    
    # ==========================================
    # Feature Flags
    # ==========================================
    feature_email_delivery: bool = Field(default=True, description="Enable email report delivery")
    feature_pdf_export: bool = Field(default=False, description="Enable PDF export (Phase 2)")
    feature_scheduled_research: bool = Field(default=False, description="Enable scheduled research (Phase 2)")
    feature_api_keys: bool = Field(default=True, description="Enable API key authentication")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars
        populate_by_name = True  # Allow both field name and alias


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Rate limit configurations per tier
TIER_LIMITS = {
    "free": {
        "research_per_day": 2,
        "research_per_month": 15,
        "api_calls_per_minute": 10,
        "api_calls_per_day": 100,
        "max_research_depth": "standard",
        "concurrent_research": 1,
        "features": ["basic_research", "email_delivery"],
    },
    "pro": {
        "research_per_day": 20,
        "research_per_month": 200,
        "api_calls_per_minute": 60,
        "api_calls_per_day": 5000,
        "max_research_depth": "deep",
        "concurrent_research": 3,
        "features": ["basic_research", "email_delivery", "pdf_export", "priority_processing"],
    },
    "enterprise": {
        "research_per_day": -1,  # Unlimited
        "research_per_month": -1,
        "api_calls_per_minute": 300,
        "api_calls_per_day": -1,
        "max_research_depth": "comprehensive",
        "concurrent_research": 10,
        "features": ["basic_research", "email_delivery", "pdf_export", "priority_processing", 
                    "scheduled_research", "api_access", "team_collaboration"],
    },
    "anonymous": {
        "research_per_day": 2,
        "research_per_month": 5,
        "api_calls_per_minute": 5,
        "api_calls_per_day": 20,
        "max_research_depth": "quick",
        "concurrent_research": 1,
        "features": ["basic_research"],
    },
}


def get_tier_limits(tier: str) -> dict:
    """Get rate limits for a subscription tier."""
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])
