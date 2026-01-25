"""
Deep Research Agent API - Users Router
Endpoints for user profile management and API key operations.
"""

import logging
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas import (
    UserProfile,
    UserProfileUpdate,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreated,
    APIKeyList,
    UsageStats,
    UsageHistory,
    BaseResponse,
)
from ..dependencies import (
    AuthenticatedUserDep,
    SupabaseDep,
    SettingsDep,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


# ==========================================
# Profile Endpoints
# ==========================================

@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get user profile",
    description="Returns the authenticated user's full profile including subscription info.",
)
async def get_profile(
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> UserProfile:
    """Get the current user's profile."""
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
                detail="Profile not found. Please contact support.",
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


@router.patch(
    "/profile",
    response_model=UserProfile,
    summary="Update user profile",
    description="Update the authenticated user's profile. Only full_name and avatar_url can be changed.",
)
async def update_profile(
    update: UserProfileUpdate,
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> UserProfile:
    """Update the current user's profile."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    # Build update dict (only non-None values)
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    
    try:
        result = supabase.table("user_profiles").update(update_data).eq("id", str(user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return UserProfile(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


# ==========================================
# API Key Endpoints
# ==========================================

def generate_api_key() -> str:
    """Generate a new API key with prefix."""
    # Generate 32 random bytes and encode as base64
    random_bytes = secrets.token_bytes(32)
    key = secrets.token_urlsafe(32)
    return f"drk_{key}"


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(key.encode()).hexdigest()


def get_key_prefix(key: str) -> str:
    """Get the prefix of an API key for display."""
    if key.startswith("drk_") and len(key) > 12:
        return key[:12]
    return key[:8]


@router.get(
    "/api-keys",
    response_model=APIKeyList,
    summary="List API keys",
    description="List all API keys for the authenticated user.",
)
async def list_api_keys(
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
    page: int = 1,
    page_size: int = 20,
) -> APIKeyList:
    """List the user's API keys."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        # Get total count
        count_result = supabase.table("api_keys").select("id", count="exact").eq("user_id", str(user.id)).execute()
        total = count_result.count or 0
        
        # Get paginated results
        offset = (page - 1) * page_size
        result = supabase.table("api_keys").select("*").eq("user_id", str(user.id)).order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        keys = [APIKeyResponse(**key) for key in result.data] if result.data else []
        
        return APIKeyList(
            total=total,
            page=page,
            page_size=page_size,
            has_more=total > offset + page_size,
            keys=keys,
        )
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys",
        )


@router.post(
    "/api-keys",
    response_model=APIKeyCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key. The full key is only shown once!",
)
async def create_api_key(
    request: APIKeyCreate,
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
    settings: SettingsDep,
) -> APIKeyCreated:
    """
    Create a new API key.
    
    ⚠️ The full key is only returned once in this response!
    Store it securely - it cannot be retrieved again.
    """
    if not settings.feature_api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key feature is not enabled",
        )
    
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    # Generate new key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    key_prefix = get_key_prefix(api_key)
    
    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)
    
    try:
        # Check if user has too many keys (limit to 10)
        count_result = supabase.table("api_keys").select("id", count="exact").eq("user_id", str(user.id)).eq("is_active", True).execute()
        
        if count_result.count and count_result.count >= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum of 10 active API keys allowed. Please delete an existing key first.",
            )
        
        # Insert new key
        key_data = {
            "user_id": str(user.id),
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "name": request.name,
            "scopes": request.scopes,
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        
        result = supabase.table("api_keys").insert(key_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create API key",
            )
        
        created_key = result.data[0]
        
        logger.info(f"API key created for user {user.email}: {key_prefix}...")
        
        return APIKeyCreated(
            id=created_key["id"],
            name=created_key["name"],
            key_prefix=key_prefix,
            key=api_key,  # Only time the full key is returned!
            scopes=created_key["scopes"],
            expires_at=created_key.get("expires_at"),
            is_active=True,
            created_at=created_key["created_at"],
            usage_count=0,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )


@router.delete(
    "/api-keys/{key_id}",
    response_model=BaseResponse,
    summary="Delete API key",
    description="Permanently delete an API key.",
)
async def delete_api_key(
    key_id: UUID,
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> BaseResponse:
    """Delete an API key."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        # Verify the key belongs to the user
        check = supabase.table("api_keys").select("id").eq("id", str(key_id)).eq("user_id", str(user.id)).execute()
        
        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        
        # Delete the key
        supabase.table("api_keys").delete().eq("id", str(key_id)).execute()
        
        logger.info(f"API key {key_id} deleted by user {user.email}")
        
        return BaseResponse(
            success=True,
            message="API key deleted successfully",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key",
        )


@router.patch(
    "/api-keys/{key_id}/revoke",
    response_model=BaseResponse,
    summary="Revoke API key",
    description="Revoke an API key without deleting it (can be reactivated).",
)
async def revoke_api_key(
    key_id: UUID,
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> BaseResponse:
    """Revoke an API key (soft delete)."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        result = supabase.table("api_keys").update({"is_active": False}).eq("id", str(key_id)).eq("user_id", str(user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        
        return BaseResponse(
            success=True,
            message="API key revoked successfully",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key",
        )


# ==========================================
# Usage Endpoints
# ==========================================

@router.get(
    "/usage",
    response_model=UsageStats,
    summary="Get usage statistics",
    description="Get the authenticated user's usage statistics.",
)
async def get_usage_stats(
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> UsageStats:
    """Get usage statistics for the current user."""
    if not supabase:
        # Return empty stats if no database
        return UsageStats()
    
    try:
        # Get profile for credits
        profile = supabase.table("user_profiles").select("credits_balance, daily_research_count").eq("id", str(user.id)).single().execute()
        
        # Get research count for today
        today = datetime.now(timezone.utc).date().isoformat()
        today_research = supabase.table("usage_logs").select("id", count="exact").eq("user_id", str(user.id)).eq("action_type", "research_started").gte("created_at", today).execute()
        
        # Get research count for this month
        first_of_month = datetime.now(timezone.utc).replace(day=1).date().isoformat()
        month_research = supabase.table("usage_logs").select("id", count="exact").eq("user_id", str(user.id)).eq("action_type", "research_started").gte("created_at", first_of_month).execute()
        
        return UsageStats(
            research_today=today_research.count or 0,
            research_this_month=month_research.count or 0,
            api_calls_today=0,  # Would need Redis for accurate tracking
            api_calls_this_month=0,
            credits_used_this_month=0,
            credits_remaining=profile.data.get("credits_balance", 0) if profile.data else 0,
        )
        
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        return UsageStats()
