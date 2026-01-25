"""
Deep Research Agent API - Logging Middleware
Request/response logging for debugging and monitoring.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all incoming requests and outgoing responses.
    Adds request ID for tracing and measures response time.
    """
    
    # Paths to exclude from detailed logging
    EXCLUDE_PATHS = {"/health", "/favicon.ico"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)
        
        # Log incoming request
        start_time = time.time()
        
        # Get user info if available
        user_info = ""
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            if user.is_authenticated:
                user_info = f" user={user.email}"
            else:
                user_info = " user=anonymous"
        
        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path}"
            f"{user_info}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"[{request_id}] <-- {response.status_code} "
                f"({duration:.3f}s)"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] <-- ERROR: {str(e)} "
                f"({duration:.3f}s)"
            )
            raise


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
