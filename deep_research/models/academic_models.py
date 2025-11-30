"""
Academic Research Models for Deep Research Agent.

Provides Pydantic schemas for academic/scholarly research including:
- AcademicSource: Peer-reviewed paper metadata
- AcademicSearchQuery: Search parameters with filtering
- AcademicSearchResult: Collection of papers with statistics
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class FieldOfStudy(str, Enum):
    """Academic fields of study for filtering."""
    
    COMPUTER_SCIENCE = "Computer Science"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    MACHINE_LEARNING = "Machine Learning"
    DATA_SCIENCE = "Data Science"
    NATURAL_LANGUAGE_PROCESSING = "Natural Language Processing"
    COMPUTER_VISION = "Computer Vision"
    ROBOTICS = "Robotics"
    MATHEMATICS = "Mathematics"
    STATISTICS = "Statistics"
    PHYSICS = "Physics"
    BIOLOGY = "Biology"
    CHEMISTRY = "Chemistry"
    MEDICINE = "Medicine"
    NEUROSCIENCE = "Neuroscience"
    PSYCHOLOGY = "Psychology"
    ECONOMICS = "Economics"
    BUSINESS = "Business"
    ENGINEERING = "Engineering"
    MATERIALS_SCIENCE = "Materials Science"
    ENVIRONMENTAL_SCIENCE = "Environmental Science"
    OTHER = "Other"


class PublicationVenue(str, Enum):
    """Types of publication venues."""
    
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    WORKSHOP = "workshop"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    UNKNOWN = "unknown"


class Author(BaseModel):
    """Author information for academic papers."""
    
    name: str = Field(
        ...,
        description="Full name of the author"
    )
    author_id: Optional[str] = Field(
        default=None,
        description="Unique identifier from source (e.g., Semantic Scholar ID)"
    )
    affiliation: Optional[str] = Field(
        default=None,
        description="Author's institutional affiliation"
    )
    h_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="Author's h-index if available"
    )


class AcademicSource(BaseModel):
    """
    Represents a peer-reviewed academic paper or scholarly source.
    
    Captures comprehensive metadata for academic research including
    bibliographic information, metrics, and relevance scoring.
    """
    
    # Core bibliographic fields
    title: str = Field(
        ...,
        description="Full title of the paper"
    )
    authors: List[Author] = Field(
        default_factory=list,
        description="List of authors with metadata"
    )
    venue: str = Field(
        default="",
        description="Publication venue (journal, conference, etc.)"
    )
    venue_type: PublicationVenue = Field(
        default=PublicationVenue.UNKNOWN,
        description="Type of publication venue"
    )
    year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Publication year"
    )
    
    # Identifiers
    paper_id: Optional[str] = Field(
        default=None,
        description="Unique identifier from source API"
    )
    doi: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier"
    )
    arxiv_id: Optional[str] = Field(
        default=None,
        description="arXiv identifier if available"
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to access the paper"
    )
    pdf_url: Optional[str] = Field(
        default=None,
        description="Direct URL to PDF if available"
    )
    
    # Content
    abstract: Optional[str] = Field(
        default=None,
        description="Paper abstract"
    )
    summary: str = Field(
        default="",
        description="AI-generated summary of key findings"
    )
    
    # Metrics
    citation_count: int = Field(
        default=0,
        ge=0,
        description="Number of citations"
    )
    influential_citation_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of influential citations (if available)"
    )
    reference_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of references in the paper"
    )
    
    # Classification
    fields_of_study: List[str] = Field(
        default_factory=list,
        description="Academic fields this paper belongs to"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords or topics"
    )
    
    # Relevance and quality
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance to the search query (0-1)"
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated quality based on venue, citations, etc. (0-1)"
    )
    
    # Metadata
    is_open_access: bool = Field(
        default=False,
        description="Whether the paper is freely accessible"
    )
    source_api: str = Field(
        default="semantic_scholar",
        description="API source (semantic_scholar, web_search, etc.)"
    )
    retrieved_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this paper was retrieved"
    )
    
    @property
    def author_names(self) -> List[str]:
        """Get list of author names."""
        return [a.name for a in self.authors]
    
    @property
    def citation_badge(self) -> str:
        """Generate a citation badge based on citation count."""
        if self.citation_count >= 1000:
            return f"🏆 Highly Cited ({self.citation_count})"
        elif self.citation_count >= 100:
            return f"⭐ Well Cited ({self.citation_count})"
        elif self.citation_count >= 10:
            return f"📚 Cited ({self.citation_count})"
        else:
            return f"📄 {self.citation_count} citations"
    
    @property
    def formatted_citation(self) -> str:
        """Generate a formatted academic citation."""
        authors_str = ", ".join(self.author_names[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        
        year_str = f" ({self.year})" if self.year else ""
        venue_str = f". {self.venue}" if self.venue else ""
        doi_str = f" DOI: {self.doi}" if self.doi else ""
        
        return f"{authors_str}{year_str}. {self.title}{venue_str}.{doi_str}"
    
    def to_source_dict(self) -> Dict[str, Any]:
        """Convert to standard source dictionary format for integration."""
        # Build URL - prefer direct URL, then PDF URL, then DOI
        url = self.url or self.pdf_url or (f"https://doi.org/{self.doi}" if self.doi else "")
        return {
            "url": url,
            "title": self.title,
            "snippet": self.abstract[:300] + "..." if self.abstract and len(self.abstract) > 300 else self.abstract or self.summary,
            "credibility_score": int(self.quality_score * 100),
            "credibility_badge": f"📚 Academic ({int(self.quality_score * 100)})",
            "credibility_level": "high" if self.quality_score >= 0.7 else "medium",
            "source_type": "academic",
            "citation_count": self.citation_count,
            "year": self.year,
        }


class AcademicSearchFilters(BaseModel):
    """Filters for academic paper search."""
    
    year_min: Optional[int] = Field(
        default=None,
        ge=1900,
        description="Minimum publication year"
    )
    year_max: Optional[int] = Field(
        default=None,
        le=2100,
        description="Maximum publication year"
    )
    min_citations: int = Field(
        default=0,
        ge=0,
        description="Minimum citation count"
    )
    fields_of_study: List[str] = Field(
        default_factory=list,
        description="Filter by fields of study"
    )
    venue_types: List[PublicationVenue] = Field(
        default_factory=list,
        description="Filter by venue types (journal, conference, etc.)"
    )
    open_access_only: bool = Field(
        default=False,
        description="Only return open access papers"
    )
    
    @field_validator('year_max')
    @classmethod
    def validate_year_range(cls, v, info):
        """Ensure year_max >= year_min."""
        year_min = info.data.get('year_min')
        if v is not None and year_min is not None and v < year_min:
            raise ValueError("year_max must be >= year_min")
        return v


class AcademicSearchQuery(BaseModel):
    """Query parameters for academic paper search."""
    
    query: str = Field(
        ...,
        min_length=3,
        description="Search query string"
    )
    filters: AcademicSearchFilters = Field(
        default_factory=AcademicSearchFilters,
        description="Search filters"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )
    sort_by: str = Field(
        default="relevance",
        description="Sort order: relevance, citations, year"
    )
    include_abstract: bool = Field(
        default=True,
        description="Whether to fetch abstracts"
    )


class AcademicSearchResult(BaseModel):
    """Result of an academic paper search."""
    
    query: str = Field(
        ...,
        description="Original search query"
    )
    papers: List[AcademicSource] = Field(
        default_factory=list,
        description="List of matching papers"
    )
    total_results: int = Field(
        default=0,
        ge=0,
        description="Total number of matching papers"
    )
    returned_results: int = Field(
        default=0,
        ge=0,
        description="Number of papers returned in this response"
    )
    
    # Statistics
    avg_citation_count: float = Field(
        default=0.0,
        description="Average citations across results"
    )
    year_distribution: Dict[int, int] = Field(
        default_factory=dict,
        description="Distribution of papers by year"
    )
    field_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of papers by field"
    )
    
    # Metadata
    source_api: str = Field(
        default="semantic_scholar",
        description="API used for search"
    )
    search_duration_ms: int = Field(
        default=0,
        ge=0,
        description="Search duration in milliseconds"
    )
    filters_applied: Optional[AcademicSearchFilters] = Field(
        default=None,
        description="Filters that were applied"
    )
    
    def calculate_statistics(self):
        """Calculate aggregate statistics from papers."""
        if not self.papers:
            return
        
        # Average citations
        total_citations = sum(p.citation_count for p in self.papers)
        self.avg_citation_count = total_citations / len(self.papers)
        
        # Year distribution
        year_dist: Dict[int, int] = {}
        for paper in self.papers:
            if paper.year:
                year_dist[paper.year] = year_dist.get(paper.year, 0) + 1
        self.year_distribution = year_dist
        
        # Field distribution
        field_dist: Dict[str, int] = {}
        for paper in self.papers:
            for field in paper.fields_of_study:
                field_dist[field] = field_dist.get(field, 0) + 1
        self.field_distribution = field_dist
        
        self.returned_results = len(self.papers)
    
    def get_top_papers(self, n: int = 5, by: str = "citations") -> List[AcademicSource]:
        """Get top N papers by specified metric."""
        if by == "citations":
            return sorted(self.papers, key=lambda p: p.citation_count, reverse=True)[:n]
        elif by == "relevance":
            return sorted(self.papers, key=lambda p: p.relevance_score, reverse=True)[:n]
        elif by == "year":
            return sorted(self.papers, key=lambda p: p.year or 0, reverse=True)[:n]
        else:
            return self.papers[:n]
    
    def to_search_summaries(self) -> List[str]:
        """Convert academic results to search summaries for writer agent."""
        summaries = []
        for paper in self.papers[:10]:  # Limit to top 10
            summary_parts = [
                f"**{paper.title}**",
                f"Authors: {', '.join(paper.author_names[:3])}{'...' if len(paper.authors) > 3 else ''}",
                f"Year: {paper.year or 'N/A'} | Citations: {paper.citation_count}",
            ]
            if paper.abstract:
                summary_parts.append(f"Abstract: {paper.abstract[:500]}...")
            if paper.summary:
                summary_parts.append(f"Key Findings: {paper.summary}")
            
            summaries.append("\n".join(summary_parts))
        
        return summaries
