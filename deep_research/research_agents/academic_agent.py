"""
Academic Research Agent for Deep Research.

Fetches peer-reviewed papers using Semantic Scholar API with WebSearchTool fallback.
Provides filtering by year range, citations, and fields of study.

Features:
- Semantic Scholar API integration (with graceful fallback)
- Academic source credibility scoring
- Citation-based relevance ranking
- Field of study filtering
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlencode, quote_plus

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from agents import Agent, Runner, WebSearchTool

from deep_research.models.academic_models import (
    AcademicSource,
    AcademicSearchQuery,
    AcademicSearchResult,
    AcademicSearchFilters,
    Author,
    PublicationVenue,
    FieldOfStudy,
)


# Configure logging
logger = logging.getLogger("deep_research.academic_agent")


# Semantic Scholar API configuration
SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

# Default fields to request from Semantic Scholar API
DEFAULT_PAPER_FIELDS = [
    "paperId",
    "title",
    "abstract",
    "year",
    "citationCount",
    "influentialCitationCount",
    "referenceCount",
    "authors",
    "venue",
    "publicationVenue",
    "externalIds",
    "url",
    "openAccessPdf",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "isOpenAccess",
]


class SemanticScholarClient:
    """
    Client for Semantic Scholar API.
    
    Handles API requests with rate limiting, error handling,
    and graceful degradation when API is unavailable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Semantic Scholar client.
        
        Args:
            api_key: Optional API key for higher rate limits.
        """
        self.api_key = api_key or SEMANTIC_SCHOLAR_API_KEY
        self.base_url = SEMANTIC_SCHOLAR_API_BASE
        self._last_request_time = 0.0
        self._min_request_interval = 0.1  # 100ms between requests (public API limit)
        
        if self.api_key:
            self._min_request_interval = 0.01  # 10ms with API key
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "DeepResearchAgent/1.0",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers
    
    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        fields: Optional[List[str]] = None,
        year_range: Optional[Tuple[int, int]] = None,
        fields_of_study: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], int, bool]:
        """
        Search for papers using Semantic Scholar API.
        
        Args:
            query: Search query string.
            limit: Maximum number of results.
            offset: Pagination offset.
            fields: Fields to include in response.
            year_range: Optional (min_year, max_year) tuple.
            fields_of_study: Optional list of fields to filter by.
        
        Returns:
            Tuple of (papers_list, total_count, success_flag)
        """
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available, cannot use Semantic Scholar API")
            return [], 0, False
        
        await self._rate_limit()
        
        # Build query parameters
        params = {
            "query": query,
            "limit": min(limit, 100),  # API max is 100
            "offset": offset,
            "fields": ",".join(fields or DEFAULT_PAPER_FIELDS),
        }
        
        # Add year filter if specified
        if year_range:
            params["year"] = f"{year_range[0]}-{year_range[1]}"
        
        # Add fields of study filter
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        
        url = f"{self.base_url}/paper/search"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                )
                
                if response.status_code == 200:
                    data = response.json()
                    papers = data.get("data", [])
                    total = data.get("total", len(papers))
                    logger.info(f"Semantic Scholar returned {len(papers)} papers (total: {total})")
                    return papers, total, True
                elif response.status_code == 429:
                    logger.warning("Semantic Scholar rate limit exceeded")
                    return [], 0, False
                else:
                    logger.warning(f"Semantic Scholar API error: {response.status_code}")
                    return [], 0, False
                    
        except httpx.TimeoutException:
            logger.warning("Semantic Scholar API timeout")
            return [], 0, False
        except Exception as e:
            logger.error(f"Semantic Scholar API error: {e}")
            return [], 0, False
    
    async def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific paper.
        
        Args:
            paper_id: Semantic Scholar paper ID.
        
        Returns:
            Paper details dict or None if failed.
        """
        if not HTTPX_AVAILABLE:
            return None
        
        await self._rate_limit()
        
        url = f"{self.base_url}/paper/{paper_id}"
        params = {"fields": ",".join(DEFAULT_PAPER_FIELDS)}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching paper details: {e}")
            return None


def _parse_semantic_scholar_paper(paper_data: Dict[str, Any]) -> AcademicSource:
    """
    Parse Semantic Scholar API response into AcademicSource.
    
    Args:
        paper_data: Raw paper data from API.
    
    Returns:
        AcademicSource object.
    """
    # Parse authors
    authors = []
    for author_data in paper_data.get("authors", []):
        authors.append(Author(
            name=author_data.get("name", "Unknown"),
            author_id=author_data.get("authorId"),
        ))
    
    # Parse venue type
    venue_type = PublicationVenue.UNKNOWN
    pub_venue = paper_data.get("publicationVenue", {})
    if pub_venue:
        venue_type_str = pub_venue.get("type", "").lower()
        if "journal" in venue_type_str:
            venue_type = PublicationVenue.JOURNAL
        elif "conference" in venue_type_str:
            venue_type = PublicationVenue.CONFERENCE
    
    # Check for arXiv (preprint)
    external_ids = paper_data.get("externalIds", {}) or {}
    arxiv_id = external_ids.get("ArXiv")
    if arxiv_id and venue_type == PublicationVenue.UNKNOWN:
        venue_type = PublicationVenue.PREPRINT
    
    # Parse fields of study
    fields = []
    for field in paper_data.get("s2FieldsOfStudy", []) or []:
        if field.get("category"):
            fields.append(field["category"])
    if not fields:
        fields = paper_data.get("fieldsOfStudy", []) or []
    
    # Get URLs
    url = paper_data.get("url")
    pdf_url = None
    open_access_pdf = paper_data.get("openAccessPdf", {})
    if open_access_pdf:
        pdf_url = open_access_pdf.get("url")
    
    # Calculate quality score based on citations and venue
    citation_count = paper_data.get("citationCount", 0) or 0
    quality_score = min(1.0, citation_count / 500)  # Normalize, cap at 500 citations
    
    # Boost for journals/conferences
    if venue_type in (PublicationVenue.JOURNAL, PublicationVenue.CONFERENCE):
        quality_score = min(1.0, quality_score + 0.2)
    
    return AcademicSource(
        title=paper_data.get("title", "Untitled"),
        authors=authors,
        venue=paper_data.get("venue", "") or "",
        venue_type=venue_type,
        year=paper_data.get("year"),
        paper_id=paper_data.get("paperId"),
        doi=external_ids.get("DOI"),
        arxiv_id=arxiv_id,
        url=url,
        pdf_url=pdf_url,
        abstract=paper_data.get("abstract"),
        citation_count=citation_count,
        influential_citation_count=paper_data.get("influentialCitationCount"),
        reference_count=paper_data.get("referenceCount"),
        fields_of_study=fields,
        is_open_access=paper_data.get("isOpenAccess", False) or False,
        quality_score=quality_score,
        source_api="semantic_scholar",
    )


class AcademicResearchAgent:
    """
    Agent for academic/scholarly research.
    
    Uses Semantic Scholar API with WebSearchTool fallback for
    comprehensive academic paper discovery.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the academic research agent.
        
        Args:
            api_key: Optional Semantic Scholar API key.
            model: Model for LLM-based operations.
        """
        self.ss_client = SemanticScholarClient(api_key)
        self.model = model
        self._web_search_agent = None
    
    @property
    def web_search_agent(self) -> Agent:
        """Lazy-load web search agent for fallback."""
        if self._web_search_agent is None:
            self._web_search_agent = Agent(
                name="AcademicWebSearchAgent",
                instructions=(
                    "You are an academic research assistant. Search for scholarly articles, "
                    "research papers, and academic content. Focus on peer-reviewed sources, "
                    "university publications, and reputable academic databases. "
                    "Summarize findings with proper citations."
                ),
                model=self.model,
                tools=[WebSearchTool()],
            )
        return self._web_search_agent
    
    async def search(
        self,
        query: str,
        filters: Optional[AcademicSearchFilters] = None,
        limit: int = 10,
    ) -> AcademicSearchResult:
        """
        Search for academic papers.
        
        Args:
            query: Search query.
            filters: Optional search filters.
            limit: Maximum results to return.
        
        Returns:
            AcademicSearchResult with papers and statistics.
        """
        start_time = time.time()
        filters = filters or AcademicSearchFilters()
        
        logger.info(f"Academic search: {query} (limit: {limit})")
        
        # Try Semantic Scholar first
        papers, total, success = await self._search_semantic_scholar(
            query, filters, limit
        )
        
        source_api = "semantic_scholar"
        
        # Fallback to web search if Semantic Scholar fails
        if not success or not papers:
            logger.info("Falling back to web search for academic content")
            papers = await self._search_web_fallback(query, filters, limit)
            source_api = "web_search_fallback"
            total = len(papers)
        
        # Apply additional filtering
        filtered_papers = self._apply_filters(papers, filters)
        
        # Sort by relevance/citations
        filtered_papers = sorted(
            filtered_papers,
            key=lambda p: (p.relevance_score, p.citation_count),
            reverse=True
        )[:limit]
        
        # Calculate relevance scores
        for i, paper in enumerate(filtered_papers):
            # Base relevance on position and citations
            position_score = 1.0 - (i / max(len(filtered_papers), 1)) * 0.5
            citation_score = min(1.0, paper.citation_count / 100)
            paper.relevance_score = (position_score + citation_score) / 2
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        result = AcademicSearchResult(
            query=query,
            papers=filtered_papers,
            total_results=total,
            source_api=source_api,
            search_duration_ms=elapsed_ms,
            filters_applied=filters,
        )
        result.calculate_statistics()
        
        logger.info(
            f"Academic search complete: {len(filtered_papers)} papers, "
            f"avg citations: {result.avg_citation_count:.1f}, "
            f"duration: {elapsed_ms}ms"
        )
        
        return result
    
    async def _search_semantic_scholar(
        self,
        query: str,
        filters: AcademicSearchFilters,
        limit: int,
    ) -> Tuple[List[AcademicSource], int, bool]:
        """Search using Semantic Scholar API."""
        year_range = None
        if filters.year_min or filters.year_max:
            year_range = (
                filters.year_min or 1900,
                filters.year_max or datetime.now().year
            )
        
        papers_data, total, success = await self.ss_client.search_papers(
            query=query,
            limit=limit,
            year_range=year_range,
            fields_of_study=filters.fields_of_study if filters.fields_of_study else None,
        )
        
        if not success:
            return [], 0, False
        
        papers = [_parse_semantic_scholar_paper(p) for p in papers_data]
        return papers, total, True
    
    async def _search_web_fallback(
        self,
        query: str,
        filters: AcademicSearchFilters,
        limit: int,
    ) -> List[AcademicSource]:
        """Fallback to web search for academic content."""
        # Enhance query for academic content
        academic_query = f"academic research paper: {query}"
        if filters.year_min:
            academic_query += f" after:{filters.year_min}"
        
        try:
            result = await Runner.run(
                self.web_search_agent,
                f"Search for academic papers on: {academic_query}. "
                f"Focus on peer-reviewed research, cite sources with titles and authors."
            )
            
            # Parse web search results into AcademicSource objects
            papers = self._parse_web_search_results(result.final_output)
            return papers
            
        except Exception as e:
            logger.error(f"Web search fallback failed: {e}")
            return []
    
    def _parse_web_search_results(self, content: str) -> List[AcademicSource]:
        """
        Parse web search output into AcademicSource objects.
        
        This is a best-effort extraction since web search results
        won't have structured metadata like the API.
        """
        papers = []
        
        # Basic extraction - look for patterns that might indicate papers
        # This is a simplified implementation; real version would use NLP
        lines = content.split("\n")
        current_title = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for potential paper titles (usually in bold or with years)
            if "**" in line or any(str(year) in line for year in range(2015, 2026)):
                # Extract title (remove markdown)
                title = line.replace("**", "").strip()
                if len(title) > 20:  # Reasonable title length
                    papers.append(AcademicSource(
                        title=title[:200],
                        summary=line,
                        source_api="web_search_fallback",
                        quality_score=0.5,  # Lower quality score for web results
                    ))
        
        return papers[:10]  # Limit results
    
    def _apply_filters(
        self,
        papers: List[AcademicSource],
        filters: AcademicSearchFilters,
    ) -> List[AcademicSource]:
        """Apply post-search filters to papers."""
        filtered = papers
        
        # Filter by year range
        if filters.year_min:
            filtered = [p for p in filtered if p.year and p.year >= filters.year_min]
        if filters.year_max:
            filtered = [p for p in filtered if p.year and p.year <= filters.year_max]
        
        # Filter by minimum citations
        if filters.min_citations > 0:
            filtered = [p for p in filtered if p.citation_count >= filters.min_citations]
        
        # Filter by fields of study
        if filters.fields_of_study:
            filter_fields_lower = [f.lower() for f in filters.fields_of_study]
            filtered = [
                p for p in filtered
                if any(
                    f.lower() in filter_fields_lower
                    for f in p.fields_of_study
                )
            ]
        
        # Filter by venue types
        if filters.venue_types:
            filtered = [p for p in filtered if p.venue_type in filters.venue_types]
        
        # Filter by open access
        if filters.open_access_only:
            filtered = [p for p in filtered if p.is_open_access]
        
        return filtered


def create_academic_research_agent(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini"
) -> AcademicResearchAgent:
    """
    Factory function to create an AcademicResearchAgent.
    
    Args:
        api_key: Optional Semantic Scholar API key.
        model: Model for LLM operations.
    
    Returns:
        Configured AcademicResearchAgent instance.
    """
    return AcademicResearchAgent(api_key=api_key, model=model)


def should_use_academic_search(query_type: str, query: str) -> bool:
    """
    Determine if academic search should be used based on query analysis.
    
    Args:
        query_type: Query type from QueryAnalyzerAgent.
        query: Original query string.
    
    Returns:
        True if academic search is recommended.
    """
    # Query types that benefit from academic search
    academic_types = {
        "scientific",
        "technical",
        "medical",
        "academic",
        "research",
    }
    
    if query_type.lower() in academic_types:
        return True
    
    # Keywords that suggest academic content is valuable
    academic_keywords = [
        "research",
        "study",
        "studies",
        "paper",
        "papers",
        "peer-reviewed",
        "academic",
        "scientific",
        "journal",
        "citation",
        "literature review",
        "methodology",
        "empirical",
        "theoretical",
        "hypothesis",
        "experiment",
        "clinical trial",
        "meta-analysis",
        "systematic review",
    ]
    
    query_lower = query.lower()
    return any(kw in query_lower for kw in academic_keywords)


def get_academic_filters_from_query_analysis(
    query_analysis: Dict[str, Any]
) -> AcademicSearchFilters:
    """
    Create academic filters based on query analysis.
    
    Args:
        query_analysis: Query analysis summary dict.
    
    Returns:
        Configured AcademicSearchFilters.
    """
    filters = AcademicSearchFilters()
    
    # Set year range based on time sensitivity
    time_sensitivity = query_analysis.get("time_sensitivity", "any")
    current_year = datetime.now().year
    
    if time_sensitivity == "breaking":
        filters.year_min = current_year - 1
    elif time_sensitivity == "current":
        filters.year_min = current_year - 3
    elif time_sensitivity == "recent":
        filters.year_min = current_year - 5
    
    # Set minimum citations based on required depth
    depth = query_analysis.get("required_depth", "detailed")
    if depth == "comprehensive":
        filters.min_citations = 10
    elif depth == "exhaustive":
        filters.min_citations = 20
    
    return filters
