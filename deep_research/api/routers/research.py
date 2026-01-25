"""
Deep Research Agent API - Research Router
Endpoints for research operations with SSE streaming support.
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from ..schemas import (
    ResearchRequest,
    ResearchStartResponse,
    ResearchStatus,
    ResearchRun,
    ResearchHistory,
    ResearchEvidence,
    BaseResponse,
)
from ..dependencies import (
    OptionalUserDep,
    AuthenticatedUserDep,
    RateLimitedUserDep,
    SupabaseDep,
    SettingsDep,
    ClientIPDep,
)
from ..config import get_tier_limits

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research"])


# ==========================================
# Helper Functions
# ==========================================

def generate_run_id() -> str:
    """Generate a unique run ID."""
    timestamp = int(datetime.now(timezone.utc).timestamp())
    unique_part = uuid4().hex[:12]
    return f"run_{timestamp}_{unique_part}"


async def log_usage(
    supabase,
    user_id: Optional[str],
    action_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    """Log a usage event to the database."""
    if not supabase:
        return
    
    try:
        supabase.table("usage_logs").insert({
            "user_id": user_id,
            "action_type": action_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "metadata": metadata or {},
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log usage: {e}")


async def increment_daily_count(supabase, user_id: str):
    """Increment the user's daily research count."""
    if not supabase:
        return
    
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        
        # Get current profile
        profile = supabase.table("user_profiles").select("last_research_date, daily_research_count").eq("id", user_id).single().execute()
        
        if profile.data:
            last_date = profile.data.get("last_research_date")
            
            if last_date == today:
                # Same day - increment
                supabase.table("user_profiles").update({
                    "daily_research_count": profile.data.get("daily_research_count", 0) + 1
                }).eq("id", user_id).execute()
            else:
                # New day - reset to 1
                supabase.table("user_profiles").update({
                    "daily_research_count": 1,
                    "last_research_date": today,
                }).eq("id", user_id).execute()
                
    except Exception as e:
        logger.error(f"Failed to increment daily count: {e}")


# ==========================================
# Research Endpoints
# ==========================================

@router.post(
    "/start",
    response_model=ResearchStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start new research",
    description="Start a new research task. Returns a run_id and stream URL for progress updates.",
)
async def start_research(
    request: ResearchRequest,
    user: RateLimitedUserDep,  # Enforces rate limits
    supabase: SupabaseDep,
    settings: SettingsDep,
    client_ip: ClientIPDep,
) -> ResearchStartResponse:
    """
    Start a new research task.
    
    Rate limits apply based on user tier:
    - anonymous/free: 2 research/day
    - pro: 20 research/day
    - enterprise: unlimited
    
    Returns a run_id that can be used to:
    - Stream progress via SSE at /api/research/{run_id}/stream
    - Get status at /api/research/{run_id}
    """
    run_id = generate_run_id()
    
    # Check research depth permission
    tier_limits = get_tier_limits(user.tier)
    allowed_depths = {
        "quick": ["quick", "standard", "deep", "comprehensive"],
        "standard": ["quick", "standard", "deep", "comprehensive"],
        "deep": ["quick", "standard", "deep", "comprehensive"],
        "comprehensive": ["comprehensive"],
    }
    max_depth = tier_limits["max_research_depth"]
    
    if request.depth not in allowed_depths.get(max_depth, ["quick", "standard"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": f"Research depth '{request.depth}' requires a higher subscription tier",
                "max_allowed": max_depth,
                "upgrade_url": "/pricing",
            },
        )
    
    # Create research run in database
    if supabase:
        try:
            run_data = {
                "run_id": run_id,
                "query": request.query,
                "email": request.email,
                "status": "pending",
                "current_step": "planning",
                "user_id": str(user.id) if user.is_authenticated else None,
                "progress": {"planning": 0, "research": 0, "writing": 0, "email": 0},
            }
            
            supabase.table("research_runs").insert(run_data).execute()
            
            # Log usage
            await log_usage(
                supabase,
                user_id=str(user.id) if user.is_authenticated else None,
                action_type="research_started",
                resource_id=run_id,
                ip_address=client_ip,
                metadata={"query": request.query[:100], "depth": request.depth},
            )
            
            # Increment daily count for authenticated users
            if user.is_authenticated:
                await increment_daily_count(supabase, str(user.id))
                
        except Exception as e:
            logger.error(f"Failed to create research run: {e}")
            # Continue anyway - research can still run without persistence
    
    logger.info(f"Research started: {run_id} by {user.email or 'anonymous'}")
    
    return ResearchStartResponse(
        success=True,
        message="Research started",
        run_id=run_id,
        stream_url=f"/api/research/{run_id}/stream",
    )


@router.get(
    "/{run_id}",
    response_model=ResearchRun,
    summary="Get research status",
    description="Get the current status and results of a research run.",
)
async def get_research(
    run_id: str,
    user: OptionalUserDep,
    supabase: SupabaseDep,
) -> ResearchRun:
    """Get a research run by ID."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        result = supabase.table("research_runs").select("*").eq("run_id", run_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research run not found",
            )
        
        run = result.data
        
        # Check access: anonymous runs are public, otherwise must own
        run_user_id = run.get("user_id")
        if run_user_id and run_user_id != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this research run",
            )
        
        return ResearchRun(**run)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching research run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch research run",
        )


@router.get(
    "/{run_id}/stream",
    summary="Stream research progress",
    description="Server-Sent Events stream for real-time research progress updates.",
)
async def stream_research(
    run_id: str,
    user: OptionalUserDep,
    supabase: SupabaseDep,
):
    """
    Stream research progress as Server-Sent Events.
    
    Event types:
    - log: Progress log message
    - evidence: New source discovered
    - progress: Step progress update
    - report: Final report ready
    - error: Error occurred
    - done: Research complete
    """
    # Import the research manager
    try:
        from ...research_manager import ResearchManager
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Research manager not available",
        )
    
    # Verify run exists and user has access
    if supabase:
        try:
            result = supabase.table("research_runs").select("query, user_id, status").eq("run_id", run_id).single().execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Research run not found",
                )
            
            run = result.data
            run_user_id = run.get("user_id")
            
            if run_user_id and run_user_id != str(user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this research run",
                )
            
            query = run["query"]
            
            # Update status to running
            supabase.table("research_runs").update({"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}).eq("run_id", run_id).execute()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error accessing research run: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to access research run",
            )
    else:
        # No database - can't stream
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database required for streaming",
        )
    
    async def event_generator():
        """Generate SSE events for research progress."""
        manager = ResearchManager()
        evidence_queue = asyncio.Queue()
        evidence_counter = [0]
        
        def on_evidence(source: dict):
            evidence_counter[0] += 1
            evidence_queue.put_nowait({
                'id': f'src-{evidence_counter[0]}',
                'url': source.get('url', ''),
                'title': source.get('title', 'Untitled'),
                'snippet': source.get('snippet', ''),
            })
        
        manager._on_evidence = on_evidence
        
        def send_event(event_type: str, data: dict) -> str:
            return f"data: {json.dumps({'type': event_type, **data})}\n\n"
        
        try:
            yield send_event('log', {
                'logs': [{'id': '1', 'timestamp': datetime.now().isoformat(), 'message': '🚀 Starting research...'}]
            })
            
            # Run the research
            report = await manager.run(query, update_supabase=True, run_id=run_id)
            
            if report:
                yield send_event('report', {
                    'markdown': report.markdown_report,
                    'word_count': report.word_count or 0,
                })
                
                # Update run as complete
                if supabase:
                    supabase.table("research_runs").update({
                        "status": "done",
                        "report_markdown": report.markdown_report,
                        "word_count": report.word_count,
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                    }).eq("run_id", run_id).execute()
                    
                    # Log completion
                    await log_usage(
                        supabase,
                        user_id=str(user.id) if user.is_authenticated else None,
                        action_type="research_completed",
                        resource_id=run_id,
                    )
            
            yield send_event('done', {'message': 'Research complete'})
            
        except Exception as e:
            logger.error(f"Research error: {e}")
            yield send_event('error', {'message': str(e)})
            
            if supabase:
                supabase.table("research_runs").update({
                    "status": "error",
                    "error_message": str(e),
                }).eq("run_id", run_id).execute()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/history",
    response_model=ResearchHistory,
    summary="Get research history",
    description="Get the authenticated user's research history.",
)
async def get_research_history(
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
) -> ResearchHistory:
    """Get research history for the authenticated user."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        # Build query
        query = supabase.table("research_runs").select("*", count="exact").eq("user_id", str(user.id))
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        # Get total count
        count_query = supabase.table("research_runs").select("id", count="exact").eq("user_id", str(user.id))
        if status_filter:
            count_query = count_query.eq("status", status_filter)
        count_result = count_query.execute()
        total = count_result.count or 0
        
        # Get paginated results
        offset = (page - 1) * page_size
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        runs = [ResearchStatus(**r) for r in result.data] if result.data else []
        
        return ResearchHistory(
            total=total,
            page=page,
            page_size=page_size,
            has_more=total > offset + page_size,
            runs=runs,
        )
        
    except Exception as e:
        logger.error(f"Error fetching research history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch research history",
        )


@router.delete(
    "/{run_id}",
    response_model=BaseResponse,
    summary="Delete research run",
    description="Delete a research run and all associated data.",
)
async def delete_research(
    run_id: str,
    user: AuthenticatedUserDep,
    supabase: SupabaseDep,
) -> BaseResponse:
    """Delete a research run."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        # Verify ownership
        check = supabase.table("research_runs").select("user_id").eq("run_id", run_id).single().execute()
        
        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research run not found",
            )
        
        if check.data.get("user_id") != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this research run",
            )
        
        # Delete (cascade will handle logs and evidence)
        supabase.table("research_runs").delete().eq("run_id", run_id).execute()
        
        return BaseResponse(success=True, message="Research run deleted")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting research run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete research run",
        )


@router.get(
    "/{run_id}/evidence",
    response_model=list[ResearchEvidence],
    summary="Get research evidence",
    description="Get all sources/evidence collected during a research run.",
)
async def get_research_evidence(
    run_id: str,
    user: OptionalUserDep,
    supabase: SupabaseDep,
) -> list[ResearchEvidence]:
    """Get evidence for a research run."""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    
    try:
        # Verify access
        run = supabase.table("research_runs").select("user_id").eq("run_id", run_id).single().execute()
        
        if not run.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research run not found",
            )
        
        run_user_id = run.data.get("user_id")
        if run_user_id and run_user_id != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this research run",
            )
        
        # Get evidence
        result = supabase.table("research_evidence").select("*").eq("run_id", run_id).execute()
        
        return [ResearchEvidence(
            id=e["evidence_id"],
            title=e["title"],
            url=e["url"],
            snippet=e.get("snippet"),
            favicon=e.get("favicon"),
        ) for e in result.data] if result.data else []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch evidence",
        )
