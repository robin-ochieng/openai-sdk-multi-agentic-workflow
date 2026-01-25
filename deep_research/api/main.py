"""
Deep Research Agent API v2.0 - Main Application Factory
Production-ready FastAPI application with authentication, rate limiting, and modular routing.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings, Settings
from .middleware import AuthMiddleware, RequestLoggingMiddleware, setup_logging
from .routers import auth_router, users_router, research_router
from .dependencies import set_supabase_client
from .schemas import HealthCheck, ErrorResponse

logger = logging.getLogger(__name__)


# ==========================================
# Application Factory
# ==========================================

def create_app(settings: Settings = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        settings: Application settings. If None, loads from environment.
        
    Returns:
        Configured FastAPI application instance.
    """
    if settings is None:
        settings = get_settings()
    
    # Configure logging
    log_level = "DEBUG" if settings.debug else "INFO"
    setup_logging(log_level)
    
    # Create app with lifespan
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
## Deep Research Agent API v2.0

Production-ready API for AI-powered research with:

- 🔐 **Authentication** - Supabase Auth with JWT and API key support
- 📊 **Rate Limiting** - Tier-based limits (free: 2/day, pro: 20/day, enterprise: unlimited)
- 🔄 **Real-time Updates** - SSE streaming for research progress
- 📝 **Research History** - Persistent storage with user association
- 🔑 **API Keys** - Programmatic access for developers

### Authentication

Use one of:
- **Bearer Token**: `Authorization: Bearer <supabase_jwt>`
- **API Key**: `X-API-Key: drk_your_api_key`

### Rate Limits

| Tier | Research/Day | API Calls/Min |
|------|--------------|---------------|
| Anonymous | 2 | 5 |
| Free | 2 | 10 |
| Pro | 20 | 60 |
| Enterprise | Unlimited | 300 |
        """,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Store settings in app state
    app.state.settings = settings
    
    # ==========================================
    # CORS Middleware
    # ==========================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "Retry-After"],
    )
    
    # ==========================================
    # Custom Middleware (order matters - last added = first executed)
    # ==========================================
    
    # Request logging (runs first)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Auth middleware - Supabase client will be set later in lifespan
    # We pass None initially, and it will gracefully handle unauthenticated requests
    app.add_middleware(AuthMiddleware, supabase_client=None)
    
    # ==========================================
    # Exception Handlers
    # ==========================================
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                error="Internal server error",
                error_code="INTERNAL_ERROR",
            ).model_dump(),
        )
    
    # ==========================================
    # Core Endpoints
    # ==========================================
    
    @app.get("/", tags=["System"])
    async def root():
        """API root - returns basic info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else "Disabled in production",
            "health": "/health",
        }
    
    @app.get("/health", response_model=HealthCheck, tags=["System"])
    async def health_check():
        """
        Health check endpoint.
        
        Returns the health status of the API and its dependencies.
        """
        services = {}
        overall_status = "healthy"
        
        # Check Supabase connection
        try:
            from .dependencies import get_supabase_client
            client = get_supabase_client()
            if client:
                # Simple query to test connection
                client.table("research_runs").select("id").limit(1).execute()
                services["supabase"] = "healthy"
            else:
                services["supabase"] = "not_configured"
        except Exception as e:
            services["supabase"] = f"unhealthy: {str(e)[:50]}"
            overall_status = "degraded"
        
        # Check OpenAI
        if settings.openai_api_key:
            services["openai"] = "configured"
        else:
            services["openai"] = "not_configured"
            overall_status = "degraded"
        
        return HealthCheck(
            status=overall_status,
            version=settings.app_version,
            environment=settings.environment,
            timestamp=datetime.now(timezone.utc),
            services=services,
        )
    
    # ==========================================
    # Include Routers
    # ==========================================
    
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    
    logger.info(f"API v{settings.app_version} initialized ({settings.environment})")
    
    return app


# ==========================================
# Lifespan (Startup/Shutdown)
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes resources on startup and cleans up on shutdown.
    """
    settings = app.state.settings
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # ==========================================
    # Startup
    # ==========================================
    
    # Initialize Supabase client
    supabase_client = None
    if settings.effective_supabase_url and settings.supabase_service_key:
        try:
            from supabase import create_client
            supabase_client = create_client(
                settings.effective_supabase_url,
                settings.supabase_service_key,
            )
            set_supabase_client(supabase_client)
            # Store in app state for middleware to access
            app.state.supabase_client = supabase_client
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase: {e}")
    else:
        logger.warning("Supabase not configured - some features will be limited")
    
    yield
    
    # ==========================================
    # Shutdown
    # ==========================================
    logger.info("Shutting down API")


# ==========================================
# Default App Instance
# ==========================================

# Create default app instance for uvicorn
app = create_app()


# ==========================================
# CLI Entry Point
# ==========================================

def main():
    """Run the API server directly."""
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "deep_research.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()
