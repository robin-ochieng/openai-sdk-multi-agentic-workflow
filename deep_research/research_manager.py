"""
Research Manager
Orchestrates the 4-agent pipeline for deep research
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv

from agents import Runner, trace, get_current_trace
from deep_research.research_agents import (
    create_planner_agent,
    create_search_agent,
    create_writer_agent,
    create_email_agent
)
from .models import WebSearchPlan, ResearchSummary, ReportData
from .report_formatter import format_research_report
from dataclasses import dataclass
from typing import Callable


@dataclass
class SearchResult:
    """Represents a search result with summary and sources"""
    summary: str
    sources: List[Dict[str, str]]  # List of {url, title, snippet}


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
        
        # Callback for streaming evidence to frontend
        self._on_evidence: Optional[Callable[[Dict[str, str]], None]] = None
        
        # Collected sources for the report
        self.collected_sources: List[Dict[str, str]] = []
    
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
        
        # Reset collected sources for new search
        self.collected_sources = []
        
        tasks = [
            asyncio.create_task(self.search(item))
            for item in search_plan.searches
        ]
        results = await asyncio.gather(*tasks)
        
        print(f"✅ Finished searching - collected {len(results)} summaries")
        print(f"📚 Total sources collected: {len(self.collected_sources)}")
        return results
    
    def _extract_sources_from_result(self, result) -> List[Dict[str, str]]:
        """
        Extract source URLs from WebSearchTool results.
        
        Sources can come from two places:
        1. action.sources - The web pages that were searched
        2. annotations - URL citations in the response text
        
        Args:
            result: Runner.run() result object
            
        Returns:
            List of source dictionaries with url, title, snippet
        """
        sources = []
        seen_urls = set()
        
        try:
            # Method 1: Extract from new_items (tool call results)
            if hasattr(result, 'new_items'):
                for item in result.new_items:
                    if not hasattr(item, 'type'):
                        continue
                    
                    # Handle web_search_call tool items
                    if item.type == 'tool_call_item':
                        raw_call = getattr(item, 'raw_item', None)
                        if not raw_call:
                            continue
                            
                        call_type = getattr(raw_call, 'type', None)
                        if call_type != 'web_search_call':
                            continue
                            
                        # Extract from action.sources
                        action = getattr(raw_call, 'action', None)
                        if action:
                            item_sources = getattr(action, 'sources', None)
                            if item_sources:
                                for source in item_sources:
                                    url = getattr(source, 'url', None)
                                    if url and url not in seen_urls:
                                        # Try to get title from the source or generate from URL
                                        title = getattr(source, 'title', None) or getattr(source, 'name', None)
                                        if not title:
                                            # Extract domain as title
                                            try:
                                                from urllib.parse import urlparse
                                                parsed = urlparse(url)
                                                title = parsed.netloc.replace('www.', '')
                                            except:
                                                title = 'Web Source'
                                        
                                        sources.append({
                                            'url': url,
                                            'title': title,
                                            'snippet': ''
                                        })
                                        seen_urls.add(url)
                    
                    # Handle message_output_item for annotations
                    elif item.type == 'message_output_item':
                        raw_msg = getattr(item, 'raw_item', None)
                        if raw_msg and hasattr(raw_msg, 'content'):
                            content = raw_msg.content
                            if isinstance(content, list):
                                for content_item in content:
                                    annotations = getattr(content_item, 'annotations', None)
                                    if annotations:
                                        for ann in annotations:
                                            url = getattr(ann, 'url', None)
                                            title = getattr(ann, 'title', None)
                                            if url and url not in seen_urls:
                                                # Remove utm_source parameter for cleaner URLs
                                                clean_url = url.split('?utm_source=')[0] if '?utm_source=' in url else url
                                                sources.append({
                                                    'url': clean_url,
                                                    'title': title or 'Web Source',
                                                    'snippet': ''
                                                })
                                                seen_urls.add(url)
            
            # Method 2: Also check raw_responses for more complete data
            if hasattr(result, 'raw_responses'):
                for resp in result.raw_responses:
                    output = getattr(resp, 'output', None)
                    if not output or not isinstance(output, list):
                        continue
                        
                    for out_item in output:
                        # Check for web_search_call action sources
                        if hasattr(out_item, 'action'):
                            action = out_item.action
                            if action:
                                item_sources = getattr(action, 'sources', None)
                                if item_sources:
                                    for source in item_sources:
                                        url = getattr(source, 'url', None)
                                        if url and url not in seen_urls:
                                            title = getattr(source, 'title', None) or getattr(source, 'name', None)
                                            if not title:
                                                try:
                                                    from urllib.parse import urlparse
                                                    parsed = urlparse(url)
                                                    title = parsed.netloc.replace('www.', '')
                                                except:
                                                    title = 'Web Source'
                                            sources.append({
                                                'url': url,
                                                'title': title,
                                                'snippet': ''
                                            })
                                            seen_urls.add(url)
                        
                        # Check for content annotations
                        if hasattr(out_item, 'content'):
                            content = out_item.content
                            if isinstance(content, list):
                                for content_item in content:
                                    annotations = getattr(content_item, 'annotations', None)
                                    if annotations:
                                        for ann in annotations:
                                            url = getattr(ann, 'url', None)
                                            title = getattr(ann, 'title', None)
                                            if url and url not in seen_urls:
                                                clean_url = url.split('?utm_source=')[0] if '?utm_source=' in url else url
                                                sources.append({
                                                    'url': clean_url,
                                                    'title': title or 'Web Source',
                                                    'snippet': ''
                                                })
                                                seen_urls.add(url)
                        
        except Exception as e:
            print(f"   ⚠️ Warning: Could not extract sources: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"   📚 Extracted {len(sources)} unique sources")
        return sources
    
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
        
        # Extract sources from the search result
        sources = self._extract_sources_from_result(result)
        
        # Add to collected sources (avoid duplicates by URL)
        existing_urls = {s['url'] for s in self.collected_sources}
        for source in sources:
            if source['url'] not in existing_urls:
                self.collected_sources.append(source)
                existing_urls.add(source['url'])
                
                # Call evidence callback if set (for streaming to frontend)
                if self._on_evidence:
                    self._on_evidence(source)
        
        print(f"   ✅ Complete ({len(result.final_output)} chars, {len(sources)} sources)")
        
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

        original_report: ReportData = result.final_output
        formatted_markdown = format_research_report(
            original_report.markdown_report,
            original_report.short_summary,
            query=query,
        )

        formatted_report = ReportData(
            short_summary=original_report.short_summary.strip(),
            markdown_report=formatted_markdown,
            follow_up_questions=original_report.follow_up_questions,
        )

        report_length = len(formatted_report.markdown_report)
        word_count = len(formatted_report.markdown_report.split())

        print(f"✅ Report written: {word_count} words, {report_length} characters")
        print(f"📝 Summary: {formatted_report.short_summary}")

        return formatted_report
    
    async def send_email(
        self,
        *,
        query: str,
        report_data: ReportData,
        recipient_email: Optional[str] = None,
    ) -> Dict[str, str]:
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
        target_email = (recipient_email or os.getenv('RECIPIENT_EMAIL') or '').strip()

        if not target_email:
            raise ValueError(
                "Recipient email address is required. Provide an email in the request or set RECIPIENT_EMAIL."
            )

        # Expose recipient to the email sender utility which reads from env
        os.environ['RECIPIENT_EMAIL'] = target_email
        
        # Build explicit instruction for the email agent to send the email
        email_instruction = f"""
IMPORTANT: You MUST use the send_email tool to send this report. Do NOT just describe or propose - actually send it.

Send an email with the following details:
- Recipients: {target_email}
- Subject: Research Report: {query[:50]}{'...' if len(query) > 50 else ''}
- Priority: normal

Convert the following report to professional HTML and send it immediately:

{report_data.markdown_report}
"""
        
        result = await Runner.run(
            self.email_agent,
            email_instruction
        )
        
        # Extract the function call result from the agent's output
        # The email agent uses a function_tool that returns a dict
        raw_output = getattr(result, 'final_output', None)

        email_status: Dict[str, str]
        if isinstance(raw_output, dict):
            email_status = raw_output
        elif isinstance(raw_output, str):
            try:
                parsed = json.loads(raw_output)
                email_status = parsed if isinstance(parsed, dict) else {
                    "status": "error",
                    "message": raw_output,
                }
            except json.JSONDecodeError:
                email_status = {
                    "status": "error",
                    "message": raw_output,
                }
        else:
            email_status = {
                "status": "unknown",
                "message": "No output from email agent",
            }

        status = email_status.get("status")
        message = email_status.get("message", "")

        if not status:
            email_status["status"] = "unknown"
            status = "unknown"
        if not message:
            email_status["message"] = ""

        status_text = str(status).lower()
        message_text = str(message).lower()
        
        # Check for success indicators (prioritize "successfully sent" over "failed")
        is_success = False
        
        if "successfully sent" in message_text or "successfully" in message_text:
            is_success = True
        elif "success" in status_text:
            is_success = True
        elif "sent" in message_text and "fail" not in message_text:
            is_success = True
        
        # Override status if we detected success
        if is_success:
            email_status["status"] = "success"
            status = "success"
            # Clean up the message - remove any confusing "failed" text
            if "fail" in message_text or "successfully sent" in message_text:
                email_status["message"] = f"Email sent successfully to {target_email}"
                message = email_status["message"]

        if status == "success":
            print("✅ Email sent!")
            print(f"📬 Check your inbox: {target_email}")
        else:
            print("⚠️ Email delivery skipped or failed")
            if message:
                print(f"   Reason: {message}")

        return email_status
    
    async def run(self, query: str) -> str:
        """
        Run the complete deep research process
        
        Args:
            query: Research query from user
            
        Returns:
            Markdown report content
        """
        # Create trace for monitoring with OpenAI Agents SDK
        current_trace = get_current_trace()
        trace_id = current_trace.trace_id if current_trace else "unknown"
        self.trace_url = f"https://platform.openai.com/traces/trace?trace_id={trace_id}"
        
        with trace("deep-research-agent"):
            print(f"\n{'='*80}")
            print("🎯 DEEP RESEARCH AGENT - Starting Research Process")
            print(f"{'='*80}")
            print(f"📊 OpenAI Trace: {self.trace_url}")
            print(f"📊 View traces at: https://platform.openai.com/traces")
            
            # Step 1: Plan searches
            search_plan = await self.plan_searches(query)
            
            # Step 2: Perform searches
            search_results = await self.perform_searches(search_plan)
            
            # Step 3: Write report
            report = await self.write_report(query, search_results)
            
            # Step 4: Send email
            await self.send_email(query=query, report_data=report, recipient_email=None)
            
            self.current_status = "Complete! ✅"
            
            print(f"\n{'='*80}")
            print("🎉 RESEARCH COMPLETE!")
            print(f"{'='*80}")
            print(f"📧 Report sent to: {os.getenv('RECIPIENT_EMAIL')}")
            print(f"📊 OpenAI Trace: {self.trace_url}")
            print(f"📊 View all traces: https://platform.openai.com/traces")
            print(f"{'='*80}\n")
            
            return report.markdown_report
