"""
FastAPI Backend for Deep Research Agent
Provides REST API with Server-Sent Events for real-time updates
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime
from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_research.research_manager import ResearchManager

app = FastAPI(title="Deep Research Agent API")

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    query: str
    email: Optional[str] = None


class ResearchResponse(BaseModel):
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Deep Research Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/research": "Start a new research task",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


async def research_event_stream(query: str, email: Optional[str] = None):
    """
    Stream research progress as Server-Sent Events
    
    Args:
        query: Research query
        email: Optional email address for report delivery
    """
    manager = ResearchManager()
    
    def send_event(event_type: str, data: dict):
        """Format SSE event"""
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"
    
    try:
        # Send initial log
        yield send_event('log', {
            'logs': [{
                'id': '1',
                'timestamp': datetime.now().isoformat(),
                'message': '🚀 Initializing Deep Research Agent...',
                'emoji': '🚀',
                'type': 'info'
            }]
        })
        
        yield send_event('progress', {'step': 'planning', 'percentage': 0})
        
        # Step 1: Plan searches
        yield send_event('log', {
            'logs': [{
                'id': '2',
                'timestamp': datetime.now().isoformat(),
                'message': 'STEP 1: Planning Research Strategy',
                'emoji': '🎯',
                'type': 'info'
            }]
        })
        
        search_plan = await manager.plan_searches(query)
        
        yield send_event('planning_complete', {
            'plan': {
                'searches': [
                    {
                        'query': s.query,
                        'purpose': s.reason if hasattr(s, 'reason') else '',
                        'focus_areas': []
                    }
                    for s in search_plan.searches
                ]
            }
        })
        
        yield send_event('log', {
            'logs': [{
                'id': '3',
                'timestamp': datetime.now().isoformat(),
                'message': f'✅ Created plan with {len(search_plan.searches)} searches',
                'emoji': '✅',
                'type': 'success'
            }]
        })
        
        yield send_event('progress', {'step': 'searching', 'percentage': 25})
        
        # Step 2: Perform searches
        yield send_event('log', {
            'logs': [{
                'id': '4',
                'timestamp': datetime.now().isoformat(),
                'message': 'STEP 2: Performing Web Searches',
                'emoji': '🌐',
                'type': 'info'
            }]
        })
        
        search_results = await manager.perform_searches(search_plan)
        
        yield send_event('searching_complete', {
            'results': [
                {
                    'query': search_plan.searches[i].query,
                    'summary': result[:200] + '...' if len(result) > 200 else result,
                    'charCount': len(result)
                }
                for i, result in enumerate(search_results)
            ]
        })
        
        yield send_event('log', {
            'logs': [{
                'id': '5',
                'timestamp': datetime.now().isoformat(),
                'message': f'✅ Completed {len(search_results)} searches',
                'emoji': '✅',
                'type': 'success'
            }]
        })
        
        yield send_event('progress', {'step': 'writing', 'percentage': 50})
        
        # Step 3: Write report
        yield send_event('log', {
            'logs': [{
                'id': '6',
                'timestamp': datetime.now().isoformat(),
                'message': 'STEP 3: Synthesizing Research Report',
                'emoji': '✍️',
                'type': 'info'
            }]
        })
        
        report_data = await manager.write_report(query, search_results)
        
        # Calculate word count from the markdown report
        word_count = len(report_data.markdown_report.split())
        
        yield send_event('writing_complete', {
            'report': {
                'title': query,
                'summary': report_data.short_summary,
                'content': report_data.markdown_report,
                'markdown_report': report_data.markdown_report,
                'short_summary': report_data.short_summary,
                'word_count': word_count,
                'sources': []
            },
            'email_requested': bool(email)
        })
        
        yield send_event('log', {
            'logs': [{
                'id': '7',
                'timestamp': datetime.now().isoformat(),
                'message': f'✅ Generated report: ~{word_count} words',
                'emoji': '✅',
                'type': 'success'
            }]
        })
        
        if email:
            yield send_event('progress', {'step': 'email', 'percentage': 75})
        else:
            yield send_event('progress', {'step': 'writing', 'percentage': 100})
        
        # Step 4: Send email (if requested)
        if email:
            yield send_event('log', {
                'logs': [{
                    'id': '8',
                    'timestamp': datetime.now().isoformat(),
                    'message': f'STEP 4: Sending Report to {email}',
                    'emoji': '📧',
                    'type': 'info'
                }]
            })
            
            try:
                email_result = await manager.send_email(
                    query=query,
                    report_data=report_data,
                    recipient_email=email
                )
                
                yield send_event('email_sent', email_result)

                if email_result.get('status') == 'success':
                    yield send_event('log', {
                        'logs': [{
                            'id': '9',
                            'timestamp': datetime.now().isoformat(),
                            'message': f'✅ Email sent successfully to {email}',
                            'emoji': '✅',
                            'type': 'success'
                        }]
                    })
                else:
                    yield send_event('log', {
                        'logs': [{
                            'id': '9',
                            'timestamp': datetime.now().isoformat(),
                            'message': f"⚠️ Email sending failed: {email_result.get('message', 'Unknown error')}",
                            'emoji': '⚠️',
                            'type': 'warning'
                        }]
                    })
            except Exception as e:
                yield send_event('log', {
                    'logs': [{
                        'id': '9',
                        'timestamp': datetime.now().isoformat(),
                        'message': f'⚠️ Email sending failed: {str(e)}',
                        'emoji': '⚠️',
                        'type': 'warning'
                    }]
                })
                yield send_event('email_sent', {
                    'status': 'error',
                    'message': str(e),
                })
            
            yield send_event('progress', {'step': 'email', 'percentage': 100})
        
        # Final completion
        yield send_event('complete', {
            'message': 'Research complete!',
            'trace_url': manager.trace_url or ''
        })
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield send_event('error', {
            'message': f'Error: {str(e)}'
        })
        yield send_event('log', {
            'logs': [{
                'id': 'error',
                'timestamp': datetime.now().isoformat(),
                'message': f'❌ Error: {str(e)}',
                'emoji': '❌',
                'type': 'error'
            }]
        })


@app.post("/api/research")
async def start_research(request: ResearchRequest):
    """
    Start a new research task with SSE streaming
    
    Args:
        request: Research request with query and optional email
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    if not request.query or len(request.query.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Query must be at least 5 characters long"
        )
    
    return StreamingResponse(
        research_event_stream(request.query, request.email),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Deep Research Agent API Server")
    print("📍 API: http://localhost:7863")
    print("📍 Docs: http://localhost:7863/docs")
    uvicorn.run(app, host="0.0.0.0", port=7863, log_level="info")
