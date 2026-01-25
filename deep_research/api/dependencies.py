"""
Deep Research Agent API - Dependency Injection
Shared dependencies for FastAPI route handlers.
"""

import logging
from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from .config import get_settings, Settings, get_tier_limits
from .schemas import CurrentUser, RateLimitInfo
from .middleware.auth import JWTValidator, APIKeyValidator

logger = logging.getLogger(__name__)


# ==========================================
# Security Schemes
# ==========================================

bearer_scheme = HTTPBearer(auto_error=False, description="Supabase JWT token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="API key for programmatic access")


# ==========================================
# Settings Dependency
# ==========================================

def get_app_settings() -> Settings:
    """Dependency to get application settings."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]


# ==========================================
# Supabase Client Dependency
# ==========================================

_supabase_client = None


def set_supabase_client(client):
    """Set the Supabase client for dependency injection."""
    global _supabase_client
    _supabase_client = client


def get_supabase_client():
    """Get the Supabase client instance."""
    return _supabase_client


SupabaseDep = Annotated[Optional[object], Depends(get_supabase_client)]


# ==========================================
# User Dependencies
# ==========================================

def get_current_user_from_request(request: Request) -> CurrentUser:
    """
    Get the current user from request state.
    Set by AuthMiddleware during request processing.
    """
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user
    
    # Return anonymous user if not set
    return CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        email="",
        tier="anonymous",
        is_authenticated=False,
        daily_research_count=0,
        daily_research_limit=2,
        can_research=True,
    )


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user_from_request)]


async def get_current_active_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header),
) -> CurrentUser:
    """
    Get the current authenticated user.
    Raises 401 if not authenticated.
    
    Use this dependency for endpoints that REQUIRE authentication.
    """
    user = get_current_user_from_request(request)
    
    if not user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


AuthenticatedUserDep = Annotated[CurrentUser, Depends(get_current_active_user)]


async def get_optional_user(request: Request) -> CurrentUser:
    """
    Get the current user, authenticated or anonymous.
    Never raises an error - returns anonymous user if not authenticated.
    
    Use this dependency for endpoints that work with or without authentication.
    """
    return get_current_user_from_request(request)


OptionalUserDep = Annotated[CurrentUser, Depends(get_optional_user)]


# ==========================================
# Rate Limiting Dependencies
# ==========================================

async def check_research_rate_limit(
    user: CurrentUser = Depends(get_optional_user),
    settings: Settings = Depends(get_app_settings),
) -> CurrentUser:
    """
    Check if the user can perform research based on rate limits.
    Raises 429 if limit exceeded.
    """
    if not settings.rate_limit_enabled:
        return user
    
    tier_limits = get_tier_limits(user.tier)
    daily_limit = tier_limits["research_per_day"]
    
    # -1 means unlimited
    if daily_limit == -1:
        return user
    
    if not user.can_research or user.daily_research_count >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily research limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "current_count": user.daily_research_count,
                "daily_limit": daily_limit,
                "tier": user.tier,
                "upgrade_url": "/pricing" if user.tier in ["free", "anonymous"] else None,
            },
            headers={"Retry-After": "86400"},  # 24 hours
        )
    
    return user


RateLimitedUserDep = Annotated[CurrentUser, Depends(check_research_rate_limit)]


def get_rate_limit_info(user: CurrentUser = Depends(get_optional_user)) -> RateLimitInfo:
    """Get rate limit information for the current user."""
    from datetime import datetime, timezone, timedelta
    
    tier_limits = get_tier_limits(user.tier)
    
    # Calculate reset time (next midnight UTC)
    now = datetime.now(timezone.utc)
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return RateLimitInfo(
        tier=user.tier,
        research_per_day=tier_limits["research_per_day"],
        research_remaining_today=max(0, tier_limits["research_per_day"] - user.daily_research_count),
        api_calls_per_minute=tier_limits["api_calls_per_minute"],
        api_calls_remaining=tier_limits["api_calls_per_minute"],  # Would need Redis for accurate tracking
        reset_at=tomorrow,
    )


RateLimitInfoDep = Annotated[RateLimitInfo, Depends(get_rate_limit_info)]


# ==========================================
# Tier-Based Feature Access
# ==========================================

def require_tier(*allowed_tiers: str):
    """
    Dependency factory that requires the user to have one of the allowed tiers.
    
    Usage:
        @router.get("/premium-feature")
        async def premium_feature(user: CurrentUser = Depends(require_tier("pro", "enterprise"))):
            ...
    """
    async def check_tier(user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if user.tier not in allowed_tiers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This feature requires a higher subscription tier",
                    "error_code": "TIER_REQUIRED",
                    "current_tier": user.tier,
                    "required_tiers": list(allowed_tiers),
                    "upgrade_url": "/pricing",
                },
            )
        return user
    
    return check_tier


def require_feature(feature_name: str):
    """
    Dependency factory that requires a specific feature to be enabled for the user's tier.
    
    Usage:
        @router.post("/export-pdf")
        async def export_pdf(user: CurrentUser = Depends(require_feature("pdf_export"))):
            ...
    """
    async def check_feature(user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        tier_limits = get_tier_limits(user.tier)
        
        if feature_name not in tier_limits.get("features", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"Feature '{feature_name}' is not available in your plan",
                    "error_code": "FEATURE_NOT_AVAILABLE",
                    "current_tier": user.tier,
                    "upgrade_url": "/pricing",
                },
            )
        return user
    
    return check_feature


# ==========================================
# Request Context
# ==========================================

def get_request_id(request: Request) -> str:
    """Get the request ID for tracing."""
    return getattr(request.state, "request_id", "unknown")


RequestIdDep = Annotated[str, Depends(get_request_id)]


def get_client_ip(request: Request) -> Optional[str]:
    """Get the client IP address."""
    # Check for forwarded header (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Fall back to direct connection
    if request.client:
        return request.client.host
    
    return None


ClientIPDep = Annotated[Optional[str], Depends(get_client_ip)]
