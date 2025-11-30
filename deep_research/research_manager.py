"""
Research Manager
Orchestrates the 5-agent pipeline for deep research

Pipeline:
    1. QueryAnalyzerAgent → Classifies query and extracts research parameters
    2. PlannerAgent → Creates strategic search plan based on analysis
    3. SearchAgent → Performs web searches and summarizes results
    4. WriterAgent → Synthesizes results into comprehensive report
    5. EmailAgent → Converts to HTML and sends via Gmail SMTP
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from agents import Runner, trace, get_current_trace
from deep_research.research_agents import (
    create_query_analyzer_agent,
    create_planner_agent,
    create_search_agent,
    create_writer_agent,
    create_email_agent,
    estimate_search_count,
    get_source_validator,
    validate_search_results,
)
from deep_research.research_agents.academic_agent import (
    AcademicResearchAgent,
    create_academic_research_agent,
    should_use_academic_search,
    get_academic_filters_from_query_analysis,
)
from .models import WebSearchPlan, ResearchSummary, ReportData, QueryAnalysis, SourceMetrics
from .models.source_validation import (
    SourceMetadata,
    SourceCredibility,
    ValidationResult,
    ValidationStatistics,
    InclusionDecision,
    DomainCategory,
)
from .models.academic_models import AcademicSearchResult, AcademicSearchFilters
from .report_formatter import format_research_report, add_methodology_section
from dataclasses import dataclass
from typing import Callable

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result with summary and sources"""
    summary: str
    sources: List[Dict[str, str]]  # List of {url, title, snippet}


class ResearchManager:
    """
    Manages the deep research workflow using 5 specialized agents.
    
    Pipeline:
        1. QueryAnalyzerAgent → Classifies query, extracts entities, recommends depth
        2. PlannerAgent → Creates search strategy informed by analysis
        3. SearchAgent → Performs searches and summarizes results
        4. WriterAgent → Synthesizes results into comprehensive report
        5. EmailAgent → Converts to HTML and emails via Gmail SMTP
    
    Attributes:
        query_analysis: Cached analysis from the most recent query.
        collected_sources: Sources gathered during the search phase.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the Research Manager.
        
        Args:
            api_key: OpenAI API key (if None, reads from environment).
            model: Model to use for all agents (default: gpt-4o).
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        # Initialize all agents (including new QueryAnalyzerAgent)
        self.query_analyzer_agent = create_query_analyzer_agent(self.api_key, self.model)
        self.planner_agent = create_planner_agent(self.api_key, self.model)
        self.search_agent = create_search_agent(self.api_key, self.model)
        self.writer_agent = create_writer_agent(self.api_key, self.model)
        self.email_agent = create_email_agent(self.api_key, self.model)
        
        # Academic research agent (lazy initialization)
        self._academic_agent: Optional[AcademicResearchAgent] = None
        
        # Track progress
        self.current_status = "Idle"
        self.trace_url = None
        
        # Query analysis cache
        self.query_analysis: Optional[QueryAnalysis] = None
        
        # Academic search results cache
        self.academic_results: Optional[AcademicSearchResult] = None
        
        # Callback for streaming evidence to frontend
        self._on_evidence: Optional[Callable[[Dict[str, str]], None]] = None
        
        # Collected sources for the report
        self.collected_sources: List[Dict[str, str]] = []
        
        # Source validation statistics from most recent search
        self.validation_stats: Optional[ValidationStatistics] = None
        
        # Source validator instance
        self._source_validator = get_source_validator()
        
        logger.info(f"ResearchManager initialized with model={model}")
    
    @property
    def academic_agent(self) -> AcademicResearchAgent:
        """Lazy-load academic research agent."""
        if self._academic_agent is None:
            self._academic_agent = create_academic_research_agent(model=self.model)
        return self._academic_agent
    
    async def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Step 0: Analyze the research query to extract classification metadata.
        
        This step runs before planning to provide context that improves
        search strategy and report structure.
        
        Args:
            query: The user's research question.
            
        Returns:
            QueryAnalysis with classification, entities, and recommendations.
        """
        self.current_status = "Analyzing query..."
        print(f"\n{'='*60}")
        print("🧠 STEP 0: Analyzing Research Query")
        print(f"{'='*60}")
        print(f"Query: {query}")
        print("\nClassifying query type, extracting entities...")
        
        result = await Runner.run(
            self.query_analyzer_agent,
            f"Query: {query}"
        )
        
        analysis: QueryAnalysis = result.final_output
        self.query_analysis = analysis
        
        # Refine search count based on analysis
        refined_count = estimate_search_count(analysis)
        
        print(f"✅ Query Analysis Complete:")
        print(f"   Type: {analysis.query_type}")
        print(f"   Complexity: {analysis.complexity}")
        print(f"   Audience: {analysis.audience_level}")
        print(f"   Depth: {analysis.required_depth}")
        print(f"   Primary Entities: {', '.join(analysis.primary_entities[:5]) or 'None'}")
        print(f"   Recommended Searches: {refined_count}")
        print(f"   Estimated Time: {analysis.estimated_research_time} minutes")
        
        logger.info(
            f"Query analyzed: type={analysis.query_type}, "
            f"complexity={analysis.complexity}, "
            f"searches={refined_count}"
        )
        
        return analysis
    
    async def plan_searches(
        self, 
        query: str, 
        analysis: Optional[QueryAnalysis] = None
    ) -> WebSearchPlan:
        """
        Step 1: Use the planner_agent to plan which searches to run.
        
        If a QueryAnalysis is provided, it enriches the planner's context
        with entity information, recommended depth, and focus areas.
        
        Args:
            query: Research query from user.
            analysis: Optional QueryAnalysis from analyze_query().
            
        Returns:
            WebSearchPlan with targeted searches.
        """
        self.current_status = "Planning searches..."
        print(f"\n{'='*60}")
        print("🔍 STEP 1: Planning Research Strategy")
        print(f"{'='*60}")
        print(f"Query: {query}")
        
        # Build enriched prompt if analysis is available
        if analysis:
            search_count = estimate_search_count(analysis)
            enriched_prompt = self._build_enriched_planner_prompt(query, analysis, search_count)
            print(f"\nUsing query analysis to optimize search plan...")
            print(f"   Target searches: {search_count}")
            print(f"   Focus entities: {', '.join(analysis.primary_entities[:3]) or 'General'}")
        else:
            enriched_prompt = f"Query: {query}"
            print("\nPlanning searches (no prior analysis)...")
        
        result = await Runner.run(
            self.planner_agent,
            enriched_prompt
        )
        
        print(f"✅ Will perform {len(result.final_output.searches)} searches")
        for i, search in enumerate(result.final_output.searches, 1):
            print(f"   {i}. {search.query}")
            print(f"      Reason: {search.reason}")
        
        return result.final_output
    
    def _build_enriched_planner_prompt(
        self, 
        query: str, 
        analysis: QueryAnalysis,
        search_count: int
    ) -> str:
        """
        Build an enriched prompt for the planner using query analysis.
        
        Args:
            query: Original query.
            analysis: Query analysis results.
            search_count: Target number of searches.
            
        Returns:
            Enriched prompt string.
        """
        prompt_parts = [
            f"Query: {query}",
            "",
            "=== Query Analysis Context ===",
            f"Query Type: {analysis.query_type}",
            f"Complexity: {analysis.complexity}",
            f"Time Sensitivity: {analysis.time_sensitivity}",
            f"Audience: {analysis.audience_level}",
            f"Required Depth: {analysis.required_depth}",
            "",
        ]
        
        if analysis.primary_entities:
            prompt_parts.append(f"Primary Entities to Research: {', '.join(analysis.primary_entities)}")
        
        if analysis.secondary_entities:
            prompt_parts.append(f"Secondary/Related Topics: {', '.join(analysis.secondary_entities)}")
        
        if analysis.geographic_scope != "global":
            prompt_parts.append(f"Geographic Focus: {analysis.geographic_scope}")
        
        if analysis.time_range:
            prompt_parts.append(f"Time Range: {analysis.time_range}")
        
        if analysis.required_data_points:
            prompt_parts.append(f"Required Data Points: {', '.join(analysis.required_data_points)}")
        
        prompt_parts.extend([
            "",
            f"=== Planning Instructions ===",
            f"Generate exactly {search_count} search queries optimized for this research.",
            "Ensure searches cover all primary entities and required data points.",
            f"Tailor searches for a {analysis.audience_level} audience.",
        ])
        
        return "\n".join(prompt_parts)
    
    async def perform_searches(self, search_plan: WebSearchPlan) -> List[str]:
        """
        Step 2: Call search() for each item in the search plan.
        
        After searching, validates sources for credibility and filters out
        unreliable sources. Surviving sources are tagged with credibility badges.
        
        For technical/academic queries, also performs academic search using
        Semantic Scholar API to fetch peer-reviewed papers.
        
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
        self.academic_results = None
        self.validation_stats = None
        
        # Get original query from search plan
        original_query = ""
        if search_plan.searches:
            original_query = search_plan.searches[0].query
        
        # Determine if we should also perform academic search
        use_academic = False
        if self.query_analysis:
            use_academic = should_use_academic_search(
                self.query_analysis.query_type,
                original_query
            )
        
        # Perform web searches
        tasks = [
            asyncio.create_task(self.search(item))
            for item in search_plan.searches
        ]
        results = await asyncio.gather(*tasks)
        
        print(f"✅ Finished web searching - collected {len(results)} summaries")
        print(f"📚 Raw sources collected: {len(self.collected_sources)}")
        
        # Perform academic search if appropriate
        if use_academic:
            academic_summaries = await self._perform_academic_search(original_query)
            results.extend(academic_summaries)
            print(f"📚 Total sources after academic search: {len(self.collected_sources)}")
        
        # Validate and filter sources
        if self.collected_sources:
            validated_sources, stats = self._validate_collected_sources()
            self.validation_stats = stats
            
            print(f"\n🔍 Source Validation Results:")
            print(f"   ✅ Included: {stats.included} sources")
            print(f"   ⚠️  With caveats: {stats.included_with_caveat} sources")
            print(f"   ❌ Excluded: {stats.excluded} sources")
            print(f"   📊 Average credibility: {stats.average_score:.1f}/100")
            
            # Replace collected_sources with validated ones
            self.collected_sources = validated_sources
            print(f"📚 Final validated sources: {len(self.collected_sources)}")
        
        return results
    
    async def _perform_academic_search(self, query: str) -> List[str]:
        """
        Perform academic search using Semantic Scholar API.
        
        Called when QueryAnalysis indicates the query would benefit
        from peer-reviewed academic sources.
        
        Args:
            query: The research query.
            
        Returns:
            List of academic search summaries.
        """
        print(f"\n📚 Performing Academic Search...")
        
        # Get filters based on query analysis
        filters = AcademicSearchFilters()
        if self.query_analysis:
            filters = get_academic_filters_from_query_analysis({
                "time_sensitivity": self.query_analysis.time_sensitivity,
                "required_depth": self.query_analysis.required_depth,
            })
        
        try:
            # Search for academic papers
            result = await self.academic_agent.search(
                query=query,
                filters=filters,
                limit=10,
            )
            
            self.academic_results = result
            
            print(f"   Found {len(result.papers)} academic papers")
            if result.papers:
                print(f"   Avg citations: {result.avg_citation_count:.1f}")
                print(f"   Source: {result.source_api}")
            
            # Convert academic sources to standard source format and add to collected
            for paper in result.papers:
                source_dict = paper.to_source_dict()
                source_dict["source_type"] = "academic"
                self.collected_sources.append(source_dict)
            
            # Return summaries for the writer agent
            return result.to_search_summaries()
            
        except Exception as e:
            logger.error(f"Academic search failed: {e}")
            print(f"   ⚠️ Academic search failed: {e}")
            return []
    
    def _validate_collected_sources(self) -> tuple[List[Dict[str, str]], ValidationStatistics]:
        """
        Validate collected sources and filter by credibility.
        
        Returns:
            Tuple of (validated_sources_list, validation_statistics)
        """
        # Build query context from cached analysis if available
        query_context = ""
        if self.query_analysis:
            query_context = f"{self.query_analysis.query_type}: {', '.join(self.query_analysis.primary_entities)}"
        
        # Convert raw sources to SourceMetadata
        source_metadata_list = []
        for source in self.collected_sources:
            source_metadata_list.append(SourceMetadata(
                url=source.get("url", ""),
                title=source.get("title", ""),
                snippet=source.get("snippet", ""),
                publication_date=source.get("publication_date"),
            ))
        
        # Validate all sources
        validation_result = self._source_validator.validate_sources(
            source_metadata_list, 
            query_context
        )
        
        # Log excluded sources with reasons
        for excluded in validation_result.excluded_sources:
            reasons = [r.reason_text for r in excluded.exclusion_reasons]
            logger.warning(
                f"Source excluded: {excluded.source.url}",
                extra={
                    "domain": excluded.domain,
                    "score": excluded.overall_score,
                    "reasons": reasons
                }
            )
            print(f"   ❌ Excluded: {excluded.domain} (score: {excluded.overall_score})")
            for reason in reasons:
                print(f"      └─ {reason}")
        
        # Convert validated sources back to dict format with credibility badges
        validated_sources = []
        for credibility in validation_result.get_usable_sources():
            source_dict = {
                "url": credibility.source.url,
                "title": credibility.source.title,
                "snippet": credibility.source.snippet,
                "credibility_score": credibility.overall_score,
                "credibility_badge": credibility.score_badge,
                "credibility_level": credibility.credibility_level.value,
            }
            
            # Add caveats if any
            if credibility.decision == InclusionDecision.INCLUDE_WITH_CAVEAT:
                source_dict["caveats"] = [r.reason_text for r in credibility.exclusion_reasons]
            
            validated_sources.append(source_dict)
        
        return validated_sources, validation_result.statistics
    
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
    
    async def write_report(
        self, 
        query: str, 
        search_results: List[str],
        analysis: Optional[QueryAnalysis] = None
    ):
        """
        Step 3: Use the writer agent to write a report based on the search results.
        
        If QueryAnalysis is provided, it guides report structure, depth, and tone.
        Also incorporates source validation metrics for transparency.
        
        Args:
            query: Original research query.
            search_results: List of summarized search results.
            analysis: Optional QueryAnalysis for structure guidance.
            
        Returns:
            ReportData with full markdown report and metadata.
        """
        self.current_status = "Writing comprehensive report..."
        print(f"\n{'='*60}")
        print("✍️  STEP 3: Writing Comprehensive Report")
        print(f"{'='*60}")
        print("Thinking about report structure...")
        
        # Build enriched input if analysis is available
        if analysis:
            input_data = self._build_enriched_writer_prompt(query, search_results, analysis)
            print(f"   Using analysis to guide report structure...")
            print(f"   Target depth: {analysis.required_depth}")
            print(f"   Audience: {analysis.audience_level}")
        else:
            input_data = (
                f"Original query: {query}\n\n"
                f"Summarized search results: {search_results}"
            )
        
        result = await Runner.run(self.writer_agent, input_data)

        original_report: ReportData = result.final_output
        
        # Build source metrics from validation statistics
        source_metrics = self._build_source_metrics()
        
        # Build query analysis summary
        query_analysis_summary = self._build_query_analysis_summary(analysis) if analysis else None
        
        # Build planning notes
        planning_notes = self._build_planning_notes(analysis)
        
        # Format report and add methodology section
        formatted_markdown = format_research_report(
            original_report.markdown_report,
            original_report.short_summary,
            query=query,
        )
        
        # Add methodology & source quality section
        formatted_markdown = add_methodology_section(
            formatted_markdown,
            source_metrics=source_metrics,
            query_analysis_summary=query_analysis_summary,
            sources_with_credibility=self.collected_sources
        )

        # Create enhanced ReportData with all metadata
        formatted_report = ReportData(
            short_summary=original_report.short_summary.strip(),
            markdown_report=formatted_markdown,
            follow_up_questions=original_report.follow_up_questions,
            query_analysis_summary=query_analysis_summary,
            source_metrics=source_metrics,
            planning_notes=planning_notes,
            sources_with_credibility=self.collected_sources,
        )

        report_length = len(formatted_report.markdown_report)
        word_count = len(formatted_report.markdown_report.split())

        print(f"✅ Report written: {word_count} words, {report_length} characters")
        print(f"📝 Summary: {formatted_report.short_summary}")
        if source_metrics:
            print(f"📊 Source Quality: {source_metrics.average_score:.1f}/100 avg ({source_metrics.quality_tier})")

        return formatted_report
    
    def _build_source_metrics(self) -> Optional[SourceMetrics]:
        """
        Build SourceMetrics from validation statistics.
        
        Returns:
            SourceMetrics object or None if no validation was performed.
        """
        if not self.validation_stats:
            return None
        
        stats = self.validation_stats
        
        # Build category distribution from collected sources
        category_distribution: Dict[str, int] = {}
        for source in self.collected_sources:
            level = source.get("credibility_level", "unknown")
            category_distribution[level] = category_distribution.get(level, 0) + 1
        
        return SourceMetrics(
            total_sources=stats.total_sources,
            included_count=stats.included,
            caveat_count=stats.included_with_caveat,
            excluded_count=stats.excluded,
            average_score=stats.average_score,
            high_credibility_count=stats.high_credibility_count,
            category_distribution=category_distribution,
        )
    
    def _build_query_analysis_summary(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Build a serializable summary of query analysis.
        
        Args:
            analysis: QueryAnalysis object.
            
        Returns:
            Dictionary with key analysis attributes.
        """
        return {
            "query_type": analysis.query_type,
            "complexity": analysis.complexity,
            "audience_level": analysis.audience_level,
            "required_depth": analysis.required_depth,
            "time_sensitivity": analysis.time_sensitivity,
            "primary_entities": analysis.primary_entities[:5] if analysis.primary_entities else [],
            "recommended_search_count": analysis.recommended_search_count,
            "estimated_research_time": analysis.estimated_research_time,
        }
    
    def _build_planning_notes(self, analysis: Optional[QueryAnalysis]) -> str:
        """
        Build planning notes describing the research methodology.
        
        Args:
            analysis: Optional QueryAnalysis.
            
        Returns:
            Planning notes string.
        """
        notes_parts = []
        
        if analysis:
            notes_parts.append(f"Query classified as '{analysis.query_type}' with {analysis.complexity} complexity.")
            notes_parts.append(f"Targeted {analysis.audience_level} audience with {analysis.required_depth} depth.")
            if analysis.primary_entities:
                notes_parts.append(f"Primary research focus: {', '.join(analysis.primary_entities[:3])}.")
        
        if self.validation_stats:
            stats = self.validation_stats
            notes_parts.append(
                f"Source validation: {stats.included + stats.included_with_caveat} sources retained "
                f"({stats.excluded} excluded for low credibility)."
            )
            notes_parts.append(f"Average source credibility score: {stats.average_score:.1f}/100.")
        
        if not notes_parts:
            return "Standard research methodology applied."
        
        return " ".join(notes_parts)
    
    def _build_enriched_writer_prompt(
        self,
        query: str,
        search_results: List[str],
        analysis: QueryAnalysis
    ) -> str:
        """
        Build an enriched prompt for the writer using query analysis.
        
        Args:
            query: Original query.
            search_results: Search result summaries.
            analysis: Query analysis results.
            
        Returns:
            Enriched prompt string.
        """
        # Determine target word count based on depth
        depth_ranges = {
            "overview": (500, 1000),
            "detailed": (1500, 2500),
            "comprehensive": (3000, 5000),
            "exhaustive": (5000, 10000),
        }
        min_words, max_words = depth_ranges.get(analysis.required_depth, (1500, 2500))
        
        prompt_parts = [
            f"Original query: {query}",
            "",
            "=== Report Requirements (from Query Analysis) ===",
            f"Query Type: {analysis.query_type}",
            f"Target Audience: {analysis.audience_level}",
            f"Required Depth: {analysis.required_depth}",
            f"Target Word Count: {min_words}-{max_words} words",
            "",
        ]
        
        if analysis.recommended_sections:
            prompt_parts.append("Recommended Sections:")
            for section in analysis.recommended_sections:
                prompt_parts.append(f"  - {section}")
            prompt_parts.append("")
        
        if analysis.required_data_points:
            prompt_parts.append(f"Key Data Points to Include: {', '.join(analysis.required_data_points)}")
        
        if analysis.visualization_opportunities:
            prompt_parts.append(f"Visualization Opportunities: {', '.join(analysis.visualization_opportunities)}")
            prompt_parts.append("(Include markdown tables where data permits)")
        
        # Add source validation context if available
        if self.validation_stats:
            stats = self.validation_stats
            prompt_parts.extend([
                "",
                "=== Source Quality Context ===",
                f"Total sources validated: {stats.total_sources}",
                f"Sources included: {stats.included} high-quality, {stats.included_with_caveat} with caveats",
                f"Sources excluded: {stats.excluded} (low credibility)",
                f"Average credibility score: {stats.average_score:.1f}/100",
                "",
                "CITATION GUIDANCE:",
                "- Prefer citing high-credibility sources (⭐) for key claims",
                "- Note caveats when citing medium-credibility sources (⚠️)",
                "- Corroborate claims from lower-credibility sources with authoritative references",
            ])
        
        # Add validated sources with credibility badges
        if self.collected_sources:
            prompt_parts.extend([
                "",
                "=== Validated Sources with Credibility Scores ===",
            ])
            for i, source in enumerate(self.collected_sources[:15], 1):  # Limit to top 15
                badge = source.get("credibility_badge", "")
                url = source.get("url", "")
                title = source.get("title", "Source")
                prompt_parts.append(f"{i}. {badge} [{title}]({url})")
        
        prompt_parts.extend([
            "",
            "=== Search Results ===",
            str(search_results),
        ])
        
        return "\n".join(prompt_parts)
    
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
    
    async def run(self, query: str, skip_analysis: bool = False) -> str:
        """
        Run the complete deep research process.
        
        Args:
            query: Research query from user.
            skip_analysis: If True, skip query analysis step (backward compatible).
            
        Returns:
            Markdown report content.
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
            
            # Step 0: Analyze query (new step)
            analysis = None
            if not skip_analysis:
                analysis = await self.analyze_query(query)
            
            # Step 1: Plan searches (now with optional analysis context)
            search_plan = await self.plan_searches(query, analysis)
            
            # Step 2: Perform searches
            search_results = await self.perform_searches(search_plan)
            
            # Step 3: Write report (pass analysis for structure guidance)
            report = await self.write_report(query, search_results, analysis)
            
            # Step 4: Send email
            await self.send_email(query=query, report_data=report, recipient_email=None)
            
            self.current_status = "Complete! ✅"
            
            print(f"\n{'='*80}")
            print("🎉 RESEARCH COMPLETE!")
            print(f"{'='*80}")
            print(f"📧 Report sent to: {os.getenv('RECIPIENT_EMAIL')}")
            print(f"📊 OpenAI Trace: {self.trace_url}")
            print(f"📊 View all traces: https://platform.openai.com/traces")
            if analysis:
                print(f"📋 Query Type: {analysis.query_type} | Complexity: {analysis.complexity}")
            print(f"{'='*80}\n")
            
            return report.markdown_report
