"""
Deep Research Agent API - Pydantic Schemas
Request and response models for all API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Literal, Any
from datetime import datetime
from uuid import UUID


# ==========================================
# Common / Base Schemas
# ==========================================

class BaseResponse(BaseModel):
    """Base response with success status."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Base for paginated responses."""
    total: int
    page: int = 1
    page_size: int = 20
    has_more: bool = False


# ==========================================
# Auth Schemas
# ==========================================

class TokenPayload(BaseModel):
    """JWT token payload from Supabase."""
    sub: str  # User ID
    email: Optional[str] = None
    aud: str = "authenticated"
    role: str = "authenticated"
    exp: int
    iat: int
    
    model_config = ConfigDict(extra="allow")


class UserBase(BaseModel):
    """Base user information."""
    id: UUID
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfile(UserBase):
    """Full user profile with subscription info."""
    subscription_tier: Literal["free", "pro", "enterprise"] = "free"
    subscription_status: Literal["active", "past_due", "canceled", "incomplete", "trialing"] = "active"
    credits_balance: int = 10
    daily_research_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """Fields that can be updated by the user."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class CurrentUser(BaseModel):
    """Current authenticated user context."""
    id: UUID
    email: str
    tier: Literal["free", "pro", "enterprise", "anonymous"] = "free"
    is_authenticated: bool = True
    
    # Rate limit info
    daily_research_count: int = 0
    daily_research_limit: int = 2
    can_research: bool = True


class AuthResponse(BaseResponse):
    """Auth endpoint response."""
    user: Optional[UserProfile] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


# ==========================================
# API Key Schemas
# ==========================================

class APIKeyCreate(BaseModel):
    """Request to create a new API key."""
    name: str = Field(..., min_length=1, max_length=100, description="Friendly name for the key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Days until expiration")
    scopes: List[str] = Field(
        default=["research:read", "research:write"],
        description="Permission scopes for the key"
    )


class APIKeyResponse(BaseModel):
    """API key info (without the actual key)."""
    id: UUID
    name: str
    key_prefix: str  # e.g., "drk_abc1..."
    scopes: List[str]
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class APIKeyCreated(APIKeyResponse):
    """Response when a new API key is created (includes the full key)."""
    key: str = Field(..., description="The full API key - only shown once!")


class APIKeyList(PaginatedResponse):
    """List of API keys."""
    keys: List[APIKeyResponse]


# ==========================================
# Research Schemas
# ==========================================

class ResearchRequest(BaseModel):
    """Request to start a new research task."""
    query: str = Field(..., min_length=10, max_length=2000, description="Research query")
    email: Optional[EmailStr] = Field(None, description="Email for report delivery")
    depth: Literal["quick", "standard", "deep", "comprehensive"] = Field(
        "standard", 
        description="Research depth level"
    )
    options: Optional[dict] = Field(None, description="Additional research options")


class ResearchProgress(BaseModel):
    """Research progress update."""
    planning: int = Field(0, ge=0, le=100)
    research: int = Field(0, ge=0, le=100)
    writing: int = Field(0, ge=0, le=100)
    email: int = Field(0, ge=0, le=100)


class ResearchStatus(BaseModel):
    """Current status of a research run."""
    run_id: str
    query: str
    status: Literal["idle", "running", "done", "error"]
    current_step: Literal["planning", "research", "writing", "email"]
    progress: ResearchProgress
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ResearchRun(ResearchStatus):
    """Full research run with report."""
    report_markdown: Optional[str] = None
    word_count: int = 0
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ResearchEvidence(BaseModel):
    """A source found during research."""
    id: str
    title: str
    url: str
    snippet: Optional[str] = None
    favicon: Optional[str] = None


class ResearchStartResponse(BaseResponse):
    """Response when starting a new research task."""
    run_id: str
    stream_url: str  # SSE endpoint for progress


class ResearchHistory(PaginatedResponse):
    """User's research history."""
    runs: List[ResearchStatus]


# ==========================================
# Usage Schemas
# ==========================================

class UsageStats(BaseModel):
    """User's usage statistics."""
    research_today: int = 0
    research_this_month: int = 0
    api_calls_today: int = 0
    api_calls_this_month: int = 0
    credits_used_this_month: int = 0
    credits_remaining: int = 0


class UsageLog(BaseModel):
    """Single usage log entry."""
    id: UUID
    action_type: str
    resource_id: Optional[UUID] = None
    tokens_used: int = 0
    credits_used: int = 0
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UsageHistory(PaginatedResponse):
    """Usage history response."""
    logs: List[UsageLog]
    stats: UsageStats


# ==========================================
# Rate Limit Schemas
# ==========================================

class RateLimitInfo(BaseModel):
    """Rate limit status for the current user."""
    tier: str
    research_per_day: int
    research_remaining_today: int
    api_calls_per_minute: int
    api_calls_remaining: int
    reset_at: datetime


class RateLimitExceeded(ErrorResponse):
    """Response when rate limit is exceeded."""
    error: str = "Rate limit exceeded"
    error_code: str = "RATE_LIMIT_EXCEEDED"
    retry_after: int  # Seconds until reset
    limit_info: RateLimitInfo


# ==========================================
# Health Check Schemas
# ==========================================

class HealthCheck(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    version: str
    environment: str
    timestamp: datetime
    services: dict = Field(default_factory=dict)


# ==========================================
# SSE Event Schemas
# ==========================================

class SSEEvent(BaseModel):
    """Server-Sent Event structure."""
    type: str
    data: Any


class LogEvent(BaseModel):
    """Log message event."""
    id: str
    timestamp: str
    message: str
    channel: Optional[str] = None
    level: str = "info"


class EvidenceEvent(BaseModel):
    """Evidence discovered event."""
    id: str
    title: str
    url: str
    snippet: Optional[str] = None
    favicon: Optional[str] = None


class ReportEvent(BaseModel):
    """Report completion event."""
    markdown: str
    html: Optional[str] = None
    word_count: int
