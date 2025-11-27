"""
Supabase Database Integration for Deep Research Agent
Handles persistence of research runs, logs, and evidence
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[Supabase] supabase-py not installed. Run: pip install supabase")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ResearchLog:
    """Represents a log entry from the research process"""
    channel: str  # 'planner', 'web', 'synthesizer', 'editor'
    level: str    # 'info', 'warn', 'error'
    message: str
    timestamp: str


@dataclass
class Evidence:
    """Represents a piece of evidence/source from research"""
    evidence_id: str
    title: str
    url: str
    snippet: str
    favicon: Optional[str] = None


class SupabaseClient:
    """
    Client for interacting with Supabase database
    Handles research persistence operations
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialized = False
        self._init_client()
    
    def _init_client(self):
        """Initialize Supabase client from environment variables"""
        if not SUPABASE_AVAILABLE:
            print("[Supabase] Client not available (supabase-py not installed)")
            return
        
        url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("[Supabase] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
            return
        
        try:
            self.client = create_client(url, key)
            self._initialized = True
            print(f"[Supabase] Connected to {url}")
        except Exception as e:
            print(f"[Supabase] Failed to initialize client: {e}")
    
    @property
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self._initialized and self.client is not None
    
    # ==========================================
    # Research Run Operations
    # ==========================================
    
    async def create_run(
        self,
        run_id: str,
        query: str,
        email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new research run record"""
        if not self.is_configured:
            return None
        
        try:
            data = {
                "run_id": run_id,
                "query": query,
                "email": email,
                "status": "running",
                "current_step": "planning",
                "progress": {"planning": 0, "research": 0, "writing": 0, "email": 0},
                "started_at": datetime.now().isoformat()
            }
            
            result = self.client.table("research_runs").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] Error creating run: {e}")
            return None
    
    async def update_run(
        self,
        run_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing research run"""
        if not self.is_configured:
            return None
        
        try:
            # Add updated timestamp
            updates["updated_at"] = datetime.now().isoformat()
            
            result = self.client.table("research_runs")\
                .update(updates)\
                .eq("run_id", run_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] Error updating run: {e}")
            return None
    
    async def update_progress(
        self,
        run_id: str,
        step: str,
        percentage: int
    ) -> Optional[Dict[str, Any]]:
        """Update the progress of a research run"""
        if not self.is_configured:
            return None
        
        try:
            # Get current progress
            result = self.client.table("research_runs")\
                .select("progress")\
                .eq("run_id", run_id)\
                .single()\
                .execute()
            
            if result.data:
                progress = result.data.get("progress", {})
                progress[step] = percentage
                
                return await self.update_run(run_id, {
                    "current_step": step,
                    "progress": progress
                })
            return None
        except Exception as e:
            print(f"[Supabase] Error updating progress: {e}")
            return None
    
    async def complete_run(
        self,
        run_id: str,
        report_markdown: str,
        status: str = "done",
        error_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark a research run as complete"""
        if not self.is_configured:
            return None
        
        try:
            word_count = len(report_markdown.split()) if report_markdown else 0
            
            updates = {
                "status": status,
                "report_markdown": report_markdown,
                "word_count": word_count,
                "completed_at": datetime.now().isoformat(),
                "progress": {"planning": 100, "research": 100, "writing": 100, "email": 100}
            }
            
            if error_message:
                updates["error_message"] = error_message
            
            return await self.update_run(run_id, updates)
        except Exception as e:
            print(f"[Supabase] Error completing run: {e}")
            return None
    
    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a research run by ID"""
        if not self.is_configured:
            return None
        
        try:
            result = self.client.table("research_runs")\
                .select("*")\
                .eq("run_id", run_id)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            print(f"[Supabase] Error getting run: {e}")
            return None
    
    async def get_runs(
        self,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get a list of research runs"""
        if not self.is_configured:
            return []
        
        try:
            query = self.client.table("research_runs")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)
            
            if status:
                query = query.eq("status", status)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] Error getting runs: {e}")
            return []
    
    # ==========================================
    # Log Operations
    # ==========================================
    
    async def add_log(
        self,
        run_id: str,
        log: ResearchLog
    ) -> Optional[Dict[str, Any]]:
        """Add a log entry for a research run"""
        if not self.is_configured:
            return None
        
        try:
            data = {
                "run_id": run_id,
                "channel": log.channel,
                "level": log.level,
                "message": log.message,
                "log_timestamp": log.timestamp
            }
            
            result = self.client.table("research_logs").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] Error adding log: {e}")
            return None
    
    async def add_logs(
        self,
        run_id: str,
        logs: List[ResearchLog]
    ) -> List[Dict[str, Any]]:
        """Add multiple log entries for a research run"""
        if not self.is_configured or not logs:
            return []
        
        try:
            data = [
                {
                    "run_id": run_id,
                    "channel": log.channel,
                    "level": log.level,
                    "message": log.message,
                    "log_timestamp": log.timestamp
                }
                for log in logs
            ]
            
            result = self.client.table("research_logs").insert(data).execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] Error adding logs: {e}")
            return []
    
    async def get_logs(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a research run"""
        if not self.is_configured:
            return []
        
        try:
            result = self.client.table("research_logs")\
                .select("*")\
                .eq("run_id", run_id)\
                .order("sequence_num", desc=False)\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] Error getting logs: {e}")
            return []
    
    # ==========================================
    # Evidence Operations
    # ==========================================
    
    async def add_evidence(
        self,
        run_id: str,
        evidence: Evidence
    ) -> Optional[Dict[str, Any]]:
        """Add evidence/source for a research run"""
        if not self.is_configured:
            return None
        
        try:
            data = {
                "run_id": run_id,
                "evidence_id": evidence.evidence_id,
                "title": evidence.title,
                "url": evidence.url,
                "snippet": evidence.snippet,
                "favicon": evidence.favicon
            }
            
            result = self.client.table("research_evidence")\
                .upsert(data, on_conflict="run_id,evidence_id")\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] Error adding evidence: {e}")
            return None
    
    async def add_evidence_batch(
        self,
        run_id: str,
        evidence_list: List[Evidence]
    ) -> List[Dict[str, Any]]:
        """Add multiple evidence items for a research run"""
        if not self.is_configured or not evidence_list:
            return []
        
        try:
            data = [
                {
                    "run_id": run_id,
                    "evidence_id": e.evidence_id,
                    "title": e.title,
                    "url": e.url,
                    "snippet": e.snippet,
                    "favicon": e.favicon
                }
                for e in evidence_list
            ]
            
            result = self.client.table("research_evidence")\
                .upsert(data, on_conflict="run_id,evidence_id")\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] Error adding evidence batch: {e}")
            return []
    
    async def get_evidence(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for a research run"""
        if not self.is_configured:
            return []
        
        try:
            result = self.client.table("research_evidence")\
                .select("*")\
                .eq("run_id", run_id)\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] Error getting evidence: {e}")
            return []
    
    # ==========================================
    # Full Run Operations
    # ==========================================
    
    async def get_full_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a research run with all logs and evidence"""
        if not self.is_configured:
            return None
        
        try:
            run = await self.get_run(run_id)
            if not run:
                return None
            
            logs = await self.get_logs(run_id)
            evidence = await self.get_evidence(run_id)
            
            return {
                **run,
                "logs": logs,
                "evidence": evidence
            }
        except Exception as e:
            print(f"[Supabase] Error getting full run: {e}")
            return None
    
    async def delete_run(self, run_id: str) -> bool:
        """Delete a research run and all associated data"""
        if not self.is_configured:
            return False
        
        try:
            # Delete run (logs and evidence will cascade delete)
            self.client.table("research_runs")\
                .delete()\
                .eq("run_id", run_id)\
                .execute()
            return True
        except Exception as e:
            print(f"[Supabase] Error deleting run: {e}")
            return False


# Global instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


# Convenience function for sync contexts
def is_supabase_configured() -> bool:
    """Check if Supabase is configured"""
    return get_supabase_client().is_configured
