"""
Deep Research Agent API - Authentication Middleware
Validates Supabase JWT tokens and API keys from incoming requests.
"""

import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime, timezone

import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..config import get_settings
from ..schemas import CurrentUser, ErrorResponse

logger = logging.getLogger(__name__)


# ==========================================
# JWT Token Validation
# ==========================================

class JWTValidator:
    """
    Validates Supabase JWT tokens.
    Extracts user claims and validates signature using JWT secret.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Validate a JWT token and extract claims.
        
        Returns:
            Tuple of (is_valid, claims_dict, error_message)
        """
        if not self.settings.supabase_jwt_secret:
            # If no JWT secret configured, try to decode without verification
            # This is less secure but allows development without full Supabase setup
            logger.warning("No SUPABASE_JWT_SECRET configured - skipping signature verification")
            try:
                claims = jwt.decode(
                    token, 
                    options={"verify_signature": False},
                    audience=self.settings.jwt_audience
                )
                return True, claims, None
            except jwt.ExpiredSignatureError:
                return False, None, "Token has expired"
            except jwt.InvalidTokenError as e:
                return False, None, f"Invalid token: {str(e)}"
        
        try:
            claims = jwt.decode(
                token,
                self.settings.supabase_jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
                audience=self.settings.jwt_audience
            )
            return True, claims, None
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidAudienceError:
            return False, None, "Invalid token audience"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
    
    def extract_user_id(self, claims: dict) -> Optional[str]:
        """Extract user ID from JWT claims."""
        return claims.get("sub")
    
    def extract_email(self, claims: dict) -> Optional[str]:
        """Extract email from JWT claims."""
        return claims.get("email")


# ==========================================
# API Key Validation
# ==========================================

class APIKeyValidator:
    """
    Validates API keys using SHA-256 hashing.
    Checks against the database for valid, non-expired keys.
    """
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def extract_prefix(key: str) -> str:
        """Extract the prefix portion of an API key for logging."""
        if key.startswith("drk_") and len(key) > 12:
            return key[:12] + "..."
        return key[:8] + "..." if len(key) > 8 else key
    
    async def validate_key(self, key: str, supabase_client) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Validate an API key against the database.
        
        Returns:
            Tuple of (is_valid, user_info_dict, error_message)
        """
        if not supabase_client:
            return False, None, "Database not configured"
        
        key_hash = self.hash_key(key)
        
        try:
            # Call the validation function in the database
            result = supabase_client.rpc(
                "validate_api_key",
                {"p_key": key}
            ).execute()
            
            if result.data and result.data.get("valid"):
                return True, result.data, None
            else:
                reason = result.data.get("reason", "Invalid API key") if result.data else "Invalid API key"
                return False, None, reason
                
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False, None, "API key validation failed"


# ==========================================
# Authentication Middleware
# ==========================================

class AuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that handles authentication for all requests.
    
    Supports:
    - Bearer token authentication (Supabase JWT)
    - API key authentication (X-API-Key header)
    - Anonymous access (for public endpoints)
    
    Sets request.state.user with CurrentUser info.
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    # Path prefixes that don't require authentication
    PUBLIC_PREFIXES = [
        "/api/auth/login",
        "/api/auth/signup",
        "/api/auth/callback",
        "/api/auth/forgot-password",
    ]
    
    def __init__(self, app, supabase_client=None):
        super().__init__(app)
        self.jwt_validator = JWTValidator()
        self.api_key_validator = APIKeyValidator()
        self._supabase_client = supabase_client
    
    @property
    def supabase_client(self):
        """Get Supabase client, checking app.state if not set directly."""
        if self._supabase_client is not None:
            return self._supabase_client
        # Try to get from app.state (set during lifespan)
        if hasattr(self.app, 'state') and hasattr(self.app.state, 'supabase_client'):
            return self.app.state.supabase_client
        return None
    
    async def dispatch(self, request: Request, call_next):
        """Process each request through authentication."""
        
        # Skip auth for public paths
        if self._is_public_path(request.url.path):
            request.state.user = self._anonymous_user()
            return await call_next(request)
        
        # Try to authenticate
        user = await self._authenticate(request)
        request.state.user = user
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (no auth required)."""
        if path in self.PUBLIC_PATHS:
            return True
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        return False
    
    async def _authenticate(self, request: Request) -> CurrentUser:
        """
        Attempt to authenticate the request.
        
        Priority:
        1. Bearer token (JWT)
        2. API key (X-API-Key header)
        3. Anonymous (if allowed)
        """
        
        # Check for Bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            is_valid, claims, error = self.jwt_validator.validate_token(token)
            
            if is_valid and claims:
                user_id = self.jwt_validator.extract_user_id(claims)
                email = self.jwt_validator.extract_email(claims)
                
                # Fetch full user profile from database
                profile = await self._get_user_profile(user_id)
                
                return CurrentUser(
                    id=user_id,
                    email=email or "",
                    tier=profile.get("subscription_tier", "free") if profile else "free",
                    is_authenticated=True,
                    daily_research_count=profile.get("daily_research_count", 0) if profile else 0,
                    daily_research_limit=self._get_daily_limit(profile.get("subscription_tier", "free") if profile else "free"),
                    can_research=self._can_research(profile) if profile else True,
                )
            else:
                logger.debug(f"JWT validation failed: {error}")
        
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            is_valid, user_info, error = await self.api_key_validator.validate_key(
                api_key, self.supabase_client
            )
            
            if is_valid and user_info:
                return CurrentUser(
                    id=user_info["user_id"],
                    email=user_info.get("email", ""),
                    tier=user_info.get("tier", "free"),
                    is_authenticated=True,
                    daily_research_count=0,  # Will be fetched when needed
                    daily_research_limit=self._get_daily_limit(user_info.get("tier", "free")),
                    can_research=True,
                )
            else:
                logger.debug(f"API key validation failed: {error}")
        
        # Return anonymous user
        return self._anonymous_user()
    
    async def _get_user_profile(self, user_id: str) -> Optional[dict]:
        """Fetch user profile from database."""
        if not self.supabase_client:
            return None
        
        try:
            result = self.supabase_client.table("user_profiles").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return None
    
    def _get_daily_limit(self, tier: str) -> int:
        """Get daily research limit for a tier."""
        limits = {"free": 2, "pro": 20, "enterprise": -1, "anonymous": 2}
        return limits.get(tier, 2)
    
    def _can_research(self, profile: dict) -> bool:
        """Check if user can perform research based on daily limit."""
        if not profile:
            return True
        
        tier = profile.get("subscription_tier", "free")
        limit = self._get_daily_limit(tier)
        
        if limit == -1:  # Unlimited
            return True
        
        # Check if last_research_date is today
        last_date = profile.get("last_research_date")
        today = datetime.now(timezone.utc).date()
        
        if last_date and str(last_date) == str(today):
            return profile.get("daily_research_count", 0) < limit
        else:
            return True  # New day, counter will reset
    
    def _anonymous_user(self) -> CurrentUser:
        """Create an anonymous user context."""
        from uuid import UUID
        return CurrentUser(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            email="",
            tier="anonymous",
            is_authenticated=False,
            daily_research_count=0,
            daily_research_limit=2,
            can_research=True,
        )


# ==========================================
# Security Scheme for OpenAPI docs
# ==========================================

bearer_scheme = HTTPBearer(auto_error=False)


async def get_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[str]:
    """Extract bearer token from request."""
    if credentials:
        return credentials.credentials
    return None
