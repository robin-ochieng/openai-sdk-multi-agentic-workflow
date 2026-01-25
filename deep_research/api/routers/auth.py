"""
Deep Research Agent API - Auth Router
Endpoints for authentication and session management.
Note: Actual authentication is handled by Supabase Auth on the frontend.
This router provides backend session validation and user info.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request

from ..schemas import (
    AuthResponse, 
    UserProfile, 
    CurrentUser,
    BaseResponse,
    ErrorResponse,
)
from ..dependencies import (
    CurrentUserDep,
    AuthenticatedUserDep,
    OptionalUserDep,
    SupabaseDep,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==========================================
# Session Endpoints
# ==========================================

@router.get(
    "/me",
    response_model=AuthResponse,
    summary="Get current user",
    description="Returns the currently authenticated user's profile. Returns null user if not authenticated.",
)
async def get_current_user(
    user: OptionalUserDep,
    supabase: SupabaseDep,
) -> AuthResponse:
    """
    Get the current authenticated user.
    
    This endpoint validates the JWT token and returns user profile information.
    If not authenticated, returns success with null user.
    """
    if not user.is_authenticated:
        return AuthResponse(
            success=True,
            message="Not authenticated",
            user=None,
        )
    
    # Fetch full profile from database
    profile = None
    if supabase:
        try:
            result = supabase.table("user_profiles").select("*").eq("id", str(user.id)).single().execute()
            if result.data:
                profile = UserProfile(**result.data)
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
    
    return AuthResponse(
        success=True,
        message="Authenticated",
        user=profile,
    )


@router.get(
    "/session",
    summary="Validate session",
    description="Validates the current session and returns session info.",
)
async def validate_session(user: OptionalUserDep) -> dict:
    """
    Validate the current session.
    
    Returns session validity and basic user info.
    Useful for frontend session checks.
    """
    return {
        "valid": user.is_authenticated,
        "user_id": str(user.id) if user.is_authenticated else None,
        "email": user.email if user.is_authenticated else None,
        "tier": user.tier,
    }


@router.post(
    "/logout",
    response_model=BaseResponse,
    summary="Logout",
    description="Invalidates the current session. Note: Actual token invalidation happens on the frontend with Supabase.",
)
async def logout(user: AuthenticatedUserDep) -> BaseResponse:
    """
    Logout the current user.
    
    Note: Since we use Supabase Auth with JWT tokens, the actual logout
    happens on the frontend by clearing the session. This endpoint
    can be used for logging/audit purposes or future server-side session management.
    """
    logger.info(f"User {user.email} logged out")
    
    return BaseResponse(
        success=True,
        message="Logged out successfully",
    )


# ==========================================
# Profile Endpoints (convenience wrappers)
# ==========================================

@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get user profile",
    description="Alias for /users/profile - returns the authenticated user's full profile.",
)
async def get_profile(
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> UserProfile:
    """
    Get the current user's profile.
    Requires authentication.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        result = supabase.table("user_profiles").select("*").eq("id", str(user.id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return UserProfile(**result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile",
        )


# ==========================================
# Rate Limit Info
# ==========================================

@router.get(
    "/limits",
    summary="Get rate limits",
    description="Returns rate limit information for the current user or anonymous access.",
)
async def get_rate_limits(user: OptionalUserDep) -> dict:
    """
    Get rate limit information for the current user.
    
    Returns limits based on subscription tier:
    - anonymous: 2 research/day
    - free: 2 research/day  
    - pro: 20 research/day
    - enterprise: unlimited
    """
    from ..config import get_tier_limits
    
    tier_limits = get_tier_limits(user.tier)
    
    return {
        "tier": user.tier,
        "is_authenticated": user.is_authenticated,
        "limits": {
            "research_per_day": tier_limits["research_per_day"],
            "research_per_month": tier_limits["research_per_month"],
            "api_calls_per_minute": tier_limits["api_calls_per_minute"],
            "max_research_depth": tier_limits["max_research_depth"],
            "concurrent_research": tier_limits["concurrent_research"],
        },
        "usage": {
            "research_today": user.daily_research_count,
            "research_remaining": max(0, tier_limits["research_per_day"] - user.daily_research_count) 
                if tier_limits["research_per_day"] != -1 else -1,
        },
        "features": tier_limits["features"],
    }
