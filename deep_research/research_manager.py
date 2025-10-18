"""
Research Manager
Orchestrates the 4-agent pipeline for deep research
"""

import os
import asyncio
from typing import Dict, List
from dotenv import load_dotenv

from agents import Runner, trace, get_current_trace
from deep_research.research_agents import (
    create_planner_agent,
    create_search_agent,
    create_writer_agent,
    create_email_agent
)
from .models import WebSearchPlan, ResearchSummary


class ResearchManager:
    """
    Manages the deep research workflow using 4 specialized agents
    
    Pipeline:
    1. Planner Agent → Creates search strategy (5 searches)
    2. Search Agent → Performs searches and summarizes results
    3. Writer Agent → Synthesizes results into comprehensive report
    4. Email Agent → Converts to HTML and emails via Gmail SMTP
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the Research Manager
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: Model to use for all agents (default: gpt-4o)
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        # Initialize all agents
        self.planner_agent = create_planner_agent(self.api_key, self.model)
        self.search_agent = create_search_agent(self.api_key, self.model)
        self.writer_agent = create_writer_agent(self.api_key, self.model)
        self.email_agent = create_email_agent(self.api_key, self.model)
        
        # Track progress
        self.current_status = "Idle"
        self.trace_url = None
    
    async def plan_searches(self, query: str) -> WebSearchPlan:
        """
        Step 1: Use the planner_agent to plan which searches to run
        
        Args:
            query: Research query from user
            
        Returns:
            WebSearchPlan with 5 targeted searches
        """
        self.current_status = "Planning searches..."
        print(f"\n{'='*60}")
        print("🔍 STEP 1: Planning Research Strategy")
        print(f"{'='*60}")
        print(f"Query: {query}")
        print("\nPlanning searches...")
        
        result = await Runner.run(
            self.planner_agent,
            f"Query: {query}"
        )
        
        print(f"✅ Will perform {len(result.final_output.searches)} searches")
        for i, search in enumerate(result.final_output.searches, 1):
            print(f"   {i}. {search.query}")
            print(f"      Reason: {search.reason}")
        
        return result.final_output
    
    async def perform_searches(self, search_plan: WebSearchPlan) -> List[str]:
        """
        Step 2: Call search() for each item in the search plan
        
        Args:
            search_plan: Plan from planner agent
            
        Returns:
            List of search result summaries
        """
        self.current_status = "Searching and summarizing..."
        print(f"\n{'='*60}")
        print("🌐 STEP 2: Performing Web Searches")
        print(f"{'='*60}")
        
        tasks = [
            asyncio.create_task(self.search(item))
            for item in search_plan.searches
        ]
        results = await asyncio.gather(*tasks)
        
        print(f"✅ Finished searching - collected {len(results)} summaries")
        return results
    
    async def search(self, item) -> str:
        """
        Use the search agent to run a web search for each item in the search plan
        
        Args:
            item: WebSearchItem from search plan
            
        Returns:
            Search result summary
        """
        print(f"\n   🔎 Searching: {item.query}")
        
        input_data = f"Search term: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(self.search_agent, input_data)
        
        print(f"   ✅ Complete ({len(result.final_output)} chars)")
        
        return result.final_output
    
    async def write_report(self, query: str, search_results: List[str]):
        """
        Step 3: Use the writer agent to write a report based on the search results
        
        Args:
            query: Original research query
            search_results: List of summarized search results
            
        Returns:
            ReportData with full markdown report
        """
        self.current_status = "Writing comprehensive report..."
        print(f"\n{'='*60}")
        print("✍️  STEP 3: Writing Comprehensive Report")
        print(f"{'='*60}")
        print("Thinking about report structure...")
        
        input_data = (
            f"Original query: {query}\n\n"
            f"Summarized search results: {search_results}"
        )
        
        result = await Runner.run(self.writer_agent, input_data)
        
        report_length = len(result.final_output.markdown_report)
        word_count = len(result.final_output.markdown_report.split())
        
        print(f"✅ Report written: {word_count} words, {report_length} characters")
        print(f"📝 Summary: {result.final_output.short_summary}")
        
        return result.final_output
    
    async def send_email(self, report) -> Dict[str, str]:
        """
        Step 4: Use the email agent to send an email with the report
        
        Args:
            report: ReportData from writer agent
            
        Returns:
            Status dict from email sending
        """
        self.current_status = "Converting to HTML and sending email..."
        print(f"\n{'='*60}")
        print("📧 STEP 4: Sending Email via Gmail SMTP")
        print(f"{'='*60}")
        print("Converting report to HTML...")
        
        result = await Runner.run(
            self.email_agent,
            report.markdown_report
        )
        
        # Extract the function call result from the agent's output
        # The email agent uses a function_tool that returns a dict
        if hasattr(result, 'final_output'):
            email_status = result.final_output
        else:
            email_status = {"status": "unknown", "message": "No output from email agent"}
        
        print(f"✅ Email sent!")
        print(f"📬 Check your inbox: {os.getenv('RECIPIENT_EMAIL')}")
        
        return email_status
    
    async def run(self, query: str) -> str:
        """
        Run the complete deep research process
        
        Args:
            query: Research query from user
            
        Returns:
            Markdown report content
        """
        # Create trace for monitoring
        current_trace = get_current_trace()
        trace_id = current_trace.trace_id if current_trace else "unknown"
        self.trace_url = f"https://platform.openai.com/traces/trace?trace_id={trace_id}"
        
        with trace("Research trace"):
            print(f"\n{'='*80}")
            print("🎯 DEEP RESEARCH AGENT - Starting Research Process")
            print(f"{'='*80}")
            print(f"📊 View trace: {self.trace_url}")
            
            # Step 1: Plan searches
            search_plan = await self.plan_searches(query)
            
            # Step 2: Perform searches
            search_results = await self.perform_searches(search_plan)
            
            # Step 3: Write report
            report = await self.write_report(query, search_results)
            
            # Step 4: Send email
            await self.send_email(report)
            
            self.current_status = "Complete! ✅"
            
            print(f"\n{'='*80}")
            print("🎉 RESEARCH COMPLETE!")
            print(f"{'='*80}")
            print(f"📧 Report sent to: {os.getenv('RECIPIENT_EMAIL')}")
            print(f"📊 Trace URL: {self.trace_url}")
            print(f"{'='*80}\n")
            
            return report.markdown_report
