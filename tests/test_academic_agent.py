"""
Unit Tests for AcademicResearchAgent

Tests cover:
1. SemanticScholarClient API mocking
2. AcademicSource parsing and validation
3. Filter application (year, citations, fields)
4. WebSearchTool fallback behavior
5. Integration with ResearchManager
"""

import pytest
import json
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from deep_research.models.academic_models import (
    AcademicSource,
    AcademicSearchFilters,
    AcademicSearchQuery,
    AcademicSearchResult,
    Author,
    PublicationVenue,
    FieldOfStudy,
)
from deep_research.research_agents.academic_agent import (
    AcademicResearchAgent,
    SemanticScholarClient,
    create_academic_research_agent,
    should_use_academic_search,
    get_academic_filters_from_query_analysis,
    _parse_semantic_scholar_paper,
)


# =============================================================================
# Test Fixtures - Mock API Responses
# =============================================================================

@pytest.fixture
def mock_semantic_scholar_paper() -> Dict[str, Any]:
    """Single paper response from Semantic Scholar API."""
    return {
        "paperId": "abc123def456",
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "year": 2017,
        "citationCount": 95000,
        "influentialCitationCount": 15000,
        "referenceCount": 42,
        "authors": [
            {"authorId": "auth1", "name": "Ashish Vaswani"},
            {"authorId": "auth2", "name": "Noam Shazeer"},
            {"authorId": "auth3", "name": "Niki Parmar"},
            {"authorId": "auth4", "name": "Jakob Uszkoreit"},
            {"authorId": "auth5", "name": "Llion Jones"},
            {"authorId": "auth6", "name": "Aidan N. Gomez"},
            {"authorId": "auth7", "name": "Lukasz Kaiser"},
            {"authorId": "auth8", "name": "Illia Polosukhin"},
        ],
        "venue": "NeurIPS",
        "publicationVenue": {"type": "Conference"},
        "externalIds": {
            "DOI": "10.48550/arXiv.1706.03762",
            "ArXiv": "1706.03762",
        },
        "url": "https://www.semanticscholar.org/paper/abc123def456",
        "openAccessPdf": {"url": "https://arxiv.org/pdf/1706.03762.pdf"},
        "fieldsOfStudy": ["Computer Science"],
        "s2FieldsOfStudy": [
            {"category": "Computer Science"},
            {"category": "Machine Learning"},
        ],
        "isOpenAccess": True,
    }


@pytest.fixture
def mock_semantic_scholar_papers_list() -> List[Dict[str, Any]]:
    """Multiple papers response from Semantic Scholar API."""
    return [
        {
            "paperId": "paper1",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "abstract": "We introduce a new language representation model.",
            "year": 2019,
            "citationCount": 70000,
            "influentialCitationCount": 10000,
            "referenceCount": 50,
            "authors": [
                {"authorId": "auth1", "name": "Jacob Devlin"},
                {"authorId": "auth2", "name": "Ming-Wei Chang"},
            ],
            "venue": "NAACL",
            "publicationVenue": {"type": "Conference"},
            "externalIds": {"DOI": "10.18653/v1/N19-1423"},
            "url": "https://semanticscholar.org/paper/paper1",
            "openAccessPdf": {"url": "https://arxiv.org/pdf/1810.04805.pdf"},
            "fieldsOfStudy": ["Computer Science"],
            "s2FieldsOfStudy": [{"category": "Natural Language Processing"}],
            "isOpenAccess": True,
        },
        {
            "paperId": "paper2",
            "title": "GPT-4 Technical Report",
            "abstract": "We report the development of GPT-4.",
            "year": 2023,
            "citationCount": 5000,
            "influentialCitationCount": 500,
            "referenceCount": 100,
            "authors": [{"authorId": "openai", "name": "OpenAI Team"}],
            "venue": "arXiv",
            "publicationVenue": {"type": "Preprint"},
            "externalIds": {"ArXiv": "2303.08774"},
            "url": "https://semanticscholar.org/paper/paper2",
            "openAccessPdf": None,
            "fieldsOfStudy": ["Computer Science"],
            "s2FieldsOfStudy": [{"category": "Artificial Intelligence"}],
            "isOpenAccess": False,
        },
        {
            "paperId": "paper3",
            "title": "ResNet: Deep Residual Learning",
            "abstract": "Deeper neural networks are more difficult to train.",
            "year": 2016,
            "citationCount": 150000,
            "influentialCitationCount": 25000,
            "referenceCount": 35,
            "authors": [
                {"authorId": "kh", "name": "Kaiming He"},
                {"authorId": "xz", "name": "Xiangyu Zhang"},
            ],
            "venue": "CVPR",
            "publicationVenue": {"type": "Conference"},
            "externalIds": {"DOI": "10.1109/CVPR.2016.90"},
            "url": "https://semanticscholar.org/paper/paper3",
            "openAccessPdf": {"url": "https://arxiv.org/pdf/1512.03385.pdf"},
            "fieldsOfStudy": ["Computer Science"],
            "s2FieldsOfStudy": [{"category": "Computer Vision"}],
            "isOpenAccess": True,
        },
    ]


@pytest.fixture
def mock_semantic_scholar_response(mock_semantic_scholar_papers_list):
    """Full API response structure."""
    return {
        "total": 15000,
        "data": mock_semantic_scholar_papers_list,
    }


# =============================================================================
# Test Class: AcademicSource Model
# =============================================================================

class TestAcademicSource:
    """Tests for AcademicSource Pydantic model."""
    
    def test_create_basic_academic_source(self):
        """Test creating a basic AcademicSource."""
        source = AcademicSource(
            title="Test Paper",
            summary="A test paper about AI.",
        )
        assert source.title == "Test Paper"
        assert source.summary == "A test paper about AI."
        assert source.citation_count == 0
        assert source.quality_score == 0.0
    
    def test_create_full_academic_source(self):
        """Test creating an AcademicSource with all fields."""
        authors = [
            Author(name="John Doe", author_id="jd123", affiliation="MIT"),
            Author(name="Jane Smith", author_id="js456", affiliation="Stanford"),
        ]
        source = AcademicSource(
            title="Comprehensive AI Study",
            authors=authors,
            venue="Nature Machine Intelligence",
            venue_type=PublicationVenue.JOURNAL,
            year=2024,
            paper_id="nat123",
            doi="10.1038/s42256-024-00001",
            abstract="A comprehensive study of AI systems.",
            summary="AI systems analysis.",
            citation_count=500,
            influential_citation_count=100,
            fields_of_study=["Artificial Intelligence", "Machine Learning"],
            relevance_score=0.95,
            quality_score=0.88,
            is_open_access=True,
            source_api="semantic_scholar",
        )
        
        assert source.title == "Comprehensive AI Study"
        assert len(source.authors) == 2
        assert source.venue_type == PublicationVenue.JOURNAL
        assert source.citation_count == 500
        assert source.relevance_score == 0.95
        assert source.is_open_access is True
    
    def test_author_names_property(self):
        """Test the author_names computed property."""
        authors = [
            Author(name="Alice"),
            Author(name="Bob"),
            Author(name="Charlie"),
        ]
        source = AcademicSource(title="Test", authors=authors)
        assert source.author_names == ["Alice", "Bob", "Charlie"]
    
    def test_citation_badge_highly_cited(self):
        """Test citation badge for highly cited papers."""
        source = AcademicSource(title="Popular", citation_count=5000)
        assert "Highly Cited" in source.citation_badge
        assert "5000" in source.citation_badge
    
    def test_citation_badge_well_cited(self):
        """Test citation badge for well-cited papers."""
        source = AcademicSource(title="Good", citation_count=250)
        assert "Well Cited" in source.citation_badge
    
    def test_citation_badge_cited(self):
        """Test citation badge for moderately cited papers."""
        source = AcademicSource(title="Moderate", citation_count=50)
        assert "Cited" in source.citation_badge
    
    def test_citation_badge_few_citations(self):
        """Test citation badge for papers with few citations."""
        source = AcademicSource(title="New", citation_count=5)
        assert "5 citations" in source.citation_badge
    
    def test_formatted_citation(self):
        """Test the formatted academic citation."""
        authors = [Author(name="Smith, J."), Author(name="Doe, J.")]
        source = AcademicSource(
            title="Important Discovery",
            authors=authors,
            year=2023,
            venue="Science",
            doi="10.1126/science.abc123",
        )
        citation = source.formatted_citation
        assert "Smith, J." in citation
        assert "2023" in citation
        assert "Important Discovery" in citation
        assert "Science" in citation
        assert "DOI" in citation
    
    def test_formatted_citation_many_authors(self):
        """Test citation truncates to first 3 authors with et al."""
        authors = [Author(name=f"Author{i}") for i in range(10)]
        source = AcademicSource(title="Multi-author Paper", authors=authors, year=2022)
        citation = source.formatted_citation
        assert "Author0" in citation
        assert "Author1" in citation
        assert "Author2" in citation
        assert "et al." in citation
        assert "Author9" not in citation
    
    def test_to_source_dict(self):
        """Test conversion to standard source dictionary."""
        source = AcademicSource(
            title="Dict Test Paper",
            abstract="This is the abstract of the paper.",
            url="https://example.com/paper",
            quality_score=0.8,
            citation_count=100,
            year=2023,
        )
        result = source.to_source_dict()
        
        assert result["url"] == "https://example.com/paper"
        assert result["title"] == "Dict Test Paper"
        assert result["credibility_score"] == 80
        assert "Academic" in result["credibility_badge"]
        assert result["credibility_level"] == "high"
        assert result["source_type"] == "academic"
        assert result["citation_count"] == 100
        assert result["year"] == 2023


# =============================================================================
# Test Class: AcademicSearchFilters
# =============================================================================

class TestAcademicSearchFilters:
    """Tests for AcademicSearchFilters model."""
    
    def test_default_filters(self):
        """Test default filter values."""
        filters = AcademicSearchFilters()
        assert filters.year_min is None
        assert filters.year_max is None
        assert filters.min_citations == 0
        assert filters.fields_of_study == []
        assert filters.venue_types == []
        assert filters.open_access_only is False
    
    def test_year_range_filters(self):
        """Test year range filtering."""
        filters = AcademicSearchFilters(year_min=2020, year_max=2024)
        assert filters.year_min == 2020
        assert filters.year_max == 2024
    
    def test_year_range_validation_error(self):
        """Test that year_max must be >= year_min."""
        with pytest.raises(ValueError, match="year_max must be >= year_min"):
            AcademicSearchFilters(year_min=2024, year_max=2020)
    
    def test_min_citations_filter(self):
        """Test minimum citations filter."""
        filters = AcademicSearchFilters(min_citations=100)
        assert filters.min_citations == 100
    
    def test_fields_of_study_filter(self):
        """Test fields of study filter."""
        filters = AcademicSearchFilters(
            fields_of_study=["Computer Science", "Mathematics"]
        )
        assert len(filters.fields_of_study) == 2
        assert "Computer Science" in filters.fields_of_study
    
    def test_venue_types_filter(self):
        """Test venue types filter."""
        filters = AcademicSearchFilters(
            venue_types=[PublicationVenue.JOURNAL, PublicationVenue.CONFERENCE]
        )
        assert PublicationVenue.JOURNAL in filters.venue_types
        assert PublicationVenue.PREPRINT not in filters.venue_types


# =============================================================================
# Test Class: AcademicSearchResult
# =============================================================================

class TestAcademicSearchResult:
    """Tests for AcademicSearchResult model."""
    
    def test_empty_result(self):
        """Test empty search result."""
        result = AcademicSearchResult(query="test query")
        assert result.query == "test query"
        assert result.papers == []
        assert result.total_results == 0
    
    def test_result_with_papers(self):
        """Test search result with papers."""
        papers = [
            AcademicSource(title="Paper 1", citation_count=100, year=2023),
            AcademicSource(title="Paper 2", citation_count=50, year=2022),
        ]
        result = AcademicSearchResult(
            query="machine learning",
            papers=papers,
            total_results=1000,
        )
        assert len(result.papers) == 2
        assert result.total_results == 1000
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        papers = [
            AcademicSource(
                title="Paper 1", 
                citation_count=100, 
                year=2023,
                fields_of_study=["AI", "ML"]
            ),
            AcademicSource(
                title="Paper 2", 
                citation_count=200, 
                year=2023,
                fields_of_study=["AI"]
            ),
            AcademicSource(
                title="Paper 3", 
                citation_count=300, 
                year=2022,
                fields_of_study=["ML"]
            ),
        ]
        result = AcademicSearchResult(query="test", papers=papers)
        result.calculate_statistics()
        
        assert result.avg_citation_count == 200.0
        assert result.year_distribution[2023] == 2
        assert result.year_distribution[2022] == 1
        assert result.field_distribution["AI"] == 2
        assert result.field_distribution["ML"] == 2
        assert result.returned_results == 3
    
    def test_get_top_papers_by_citations(self):
        """Test getting top papers by citation count."""
        papers = [
            AcademicSource(title="Low", citation_count=10),
            AcademicSource(title="High", citation_count=1000),
            AcademicSource(title="Medium", citation_count=100),
        ]
        result = AcademicSearchResult(query="test", papers=papers)
        
        top = result.get_top_papers(n=2, by="citations")
        assert len(top) == 2
        assert top[0].title == "High"
        assert top[1].title == "Medium"
    
    def test_get_top_papers_by_year(self):
        """Test getting top papers by year (most recent first)."""
        papers = [
            AcademicSource(title="Old", year=2010),
            AcademicSource(title="New", year=2024),
            AcademicSource(title="Mid", year=2020),
        ]
        result = AcademicSearchResult(query="test", papers=papers)
        
        top = result.get_top_papers(n=2, by="year")
        assert top[0].title == "New"
        assert top[1].title == "Mid"
    
    def test_to_search_summaries(self):
        """Test converting results to search summaries for writer."""
        papers = [
            AcademicSource(
                title="Important Paper",
                authors=[Author(name="Smith, J.")],
                year=2023,
                citation_count=500,
                abstract="This paper presents novel findings.",
            )
        ]
        result = AcademicSearchResult(query="test", papers=papers)
        summaries = result.to_search_summaries()
        
        assert len(summaries) == 1
        summary = summaries[0]
        assert "Important Paper" in summary
        assert "Smith, J." in summary
        assert "2023" in summary
        assert "500" in summary


# =============================================================================
# Test Class: Semantic Scholar Paper Parsing
# =============================================================================

class TestSemanticScholarParsing:
    """Tests for parsing Semantic Scholar API responses."""
    
    def test_parse_complete_paper(self, mock_semantic_scholar_paper):
        """Test parsing a complete paper response."""
        source = _parse_semantic_scholar_paper(mock_semantic_scholar_paper)
        
        assert source.title == "Attention Is All You Need"
        assert source.year == 2017
        assert source.citation_count == 95000
        assert source.paper_id == "abc123def456"
        assert source.doi == "10.48550/arXiv.1706.03762"
        assert source.arxiv_id == "1706.03762"
        assert len(source.authors) == 8
        assert source.authors[0].name == "Ashish Vaswani"
        assert source.is_open_access is True
        assert source.venue_type == PublicationVenue.CONFERENCE
        assert "Computer Science" in source.fields_of_study or "Machine Learning" in source.fields_of_study
    
    def test_parse_minimal_paper(self):
        """Test parsing a minimal paper response."""
        minimal = {
            "paperId": "min123",
            "title": "Minimal Paper",
        }
        source = _parse_semantic_scholar_paper(minimal)
        
        assert source.title == "Minimal Paper"
        assert source.paper_id == "min123"
        assert source.citation_count == 0
        assert source.authors == []
        assert source.venue_type == PublicationVenue.UNKNOWN
    
    def test_parse_paper_quality_score(self, mock_semantic_scholar_paper):
        """Test that quality score is calculated properly."""
        source = _parse_semantic_scholar_paper(mock_semantic_scholar_paper)
        # High citations + conference venue should result in high quality
        assert source.quality_score >= 0.7
    
    def test_parse_preprint_detection(self):
        """Test that arXiv papers are detected as preprints."""
        paper = {
            "paperId": "arxiv123",
            "title": "Preprint Paper",
            "externalIds": {"ArXiv": "2401.12345"},
        }
        source = _parse_semantic_scholar_paper(paper)
        assert source.venue_type == PublicationVenue.PREPRINT


# =============================================================================
# Test Class: SemanticScholarClient
# =============================================================================

class TestSemanticScholarClient:
    """Tests for SemanticScholarClient API interactions."""
    
    @pytest.fixture
    def client(self):
        """Create a SemanticScholarClient instance."""
        return SemanticScholarClient()
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "https://api.semanticscholar.org/graph/v1"
        assert client._min_request_interval >= 0.01
    
    def test_client_with_api_key(self):
        """Test client with API key has faster rate limit."""
        client = SemanticScholarClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"
        assert client._min_request_interval == 0.01
    
    def test_get_headers_without_key(self, client):
        """Test headers without API key."""
        headers = client._get_headers()
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert "x-api-key" not in headers
    
    def test_get_headers_with_key(self):
        """Test headers with API key."""
        client = SemanticScholarClient(api_key="my_key")
        headers = client._get_headers()
        assert headers["x-api-key"] == "my_key"
    
    def test_search_papers_success(
        self, client, mock_semantic_scholar_response
    ):
        """Test successful paper search with mocked response."""
        async def run_test():
            with patch("deep_research.research_agents.academic_agent.HTTPX_AVAILABLE", True):
                with patch("httpx.AsyncClient") as mock_client_class:
                    # Setup mock response
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_semantic_scholar_response
                    
                    mock_client = AsyncMock()
                    mock_client.get.return_value = mock_response
                    mock_client.__aenter__.return_value = mock_client
                    mock_client.__aexit__.return_value = None
                    mock_client_class.return_value = mock_client
                    
                    papers, total, success = await client.search_papers("transformers")
                    
                    assert success is True
                    assert total == 15000
                    assert len(papers) == 3
        
        asyncio.run(run_test())
    
    def test_search_papers_rate_limit(self, client):
        """Test handling of rate limit response."""
        async def run_test():
            with patch("deep_research.research_agents.academic_agent.HTTPX_AVAILABLE", True):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_response = MagicMock()
                    mock_response.status_code = 429
                    
                    mock_client = AsyncMock()
                    mock_client.get.return_value = mock_response
                    mock_client.__aenter__.return_value = mock_client
                    mock_client.__aexit__.return_value = None
                    mock_client_class.return_value = mock_client
                    
                    papers, total, success = await client.search_papers("test")
                    
                    assert success is False
                    assert papers == []
        
        asyncio.run(run_test())
    
    def test_search_papers_httpx_not_available(self, client):
        """Test graceful handling when httpx is not available."""
        async def run_test():
            with patch("deep_research.research_agents.academic_agent.HTTPX_AVAILABLE", False):
                papers, total, success = await client.search_papers("test")
                
                assert success is False
                assert papers == []
                assert total == 0
        
        asyncio.run(run_test())


# =============================================================================
# Test Class: AcademicResearchAgent
# =============================================================================

class TestAcademicResearchAgent:
    """Tests for AcademicResearchAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create an AcademicResearchAgent instance."""
        return AcademicResearchAgent(model="gpt-4o-mini")
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.model == "gpt-4o-mini"
        assert agent._web_search_agent is None  # Lazy loaded
    
    def test_search_success(
        self, agent, mock_semantic_scholar_response
    ):
        """Test successful search."""
        async def run_test():
            with patch.object(
                agent.ss_client, 
                "search_papers",
                return_value=(mock_semantic_scholar_response["data"], 15000, True)
            ):
                result = await agent.search("transformers", limit=10)
                
                assert isinstance(result, AcademicSearchResult)
                assert result.query == "transformers"
                assert len(result.papers) > 0
                assert result.source_api == "semantic_scholar"
        
        asyncio.run(run_test())
    
    def test_search_with_filters(self, agent):
        """Test search with filters applied."""
        async def run_test():
            mock_papers = [
                {
                    "paperId": "p1",
                    "title": "Recent Paper",
                    "year": 2023,
                    "citationCount": 50,
                },
                {
                    "paperId": "p2",
                    "title": "Old Paper",
                    "year": 2018,
                    "citationCount": 200,
                },
                {
                    "paperId": "p3",
                    "title": "Uncited Paper",
                    "year": 2023,
                    "citationCount": 5,
                },
            ]
            
            filters = AcademicSearchFilters(
                year_min=2020,
                min_citations=20,
            )
            
            with patch.object(
                agent.ss_client,
                "search_papers",
                return_value=(mock_papers, 3, True)
            ):
                result = await agent.search("AI", filters=filters, limit=10)
                
                # Only "Recent Paper" should pass (2023, 50 citations)
                assert len(result.papers) == 1
                assert result.papers[0].title == "Recent Paper"
        
        asyncio.run(run_test())
    
    def test_fallback_to_web_search(self, agent):
        """Test fallback when Semantic Scholar fails."""
        async def run_test():
            with patch.object(
                agent.ss_client,
                "search_papers",
                return_value=([], 0, False)
            ):
                with patch.object(
                    agent,
                    "_search_web_fallback",
                    return_value=[AcademicSource(title="Web Result")]
                ):
                    result = await agent.search("test")
                    
                    assert result.source_api == "web_search_fallback"
                    assert len(result.papers) == 1
        
        asyncio.run(run_test())
    
    def test_apply_filters_year_min(self, agent):
        """Test year minimum filter application."""
        papers = [
            AcademicSource(title="New", year=2023),
            AcademicSource(title="Old", year=2015),
        ]
        filters = AcademicSearchFilters(year_min=2020)
        
        filtered = agent._apply_filters(papers, filters)
        
        assert len(filtered) == 1
        assert filtered[0].title == "New"
    
    def test_apply_filters_year_max(self, agent):
        """Test year maximum filter application."""
        papers = [
            AcademicSource(title="New", year=2023),
            AcademicSource(title="Old", year=2015),
        ]
        filters = AcademicSearchFilters(year_max=2020)
        
        filtered = agent._apply_filters(papers, filters)
        
        assert len(filtered) == 1
        assert filtered[0].title == "Old"
    
    def test_apply_filters_min_citations(self, agent):
        """Test minimum citations filter application."""
        papers = [
            AcademicSource(title="Popular", citation_count=100),
            AcademicSource(title="Unpopular", citation_count=5),
        ]
        filters = AcademicSearchFilters(min_citations=50)
        
        filtered = agent._apply_filters(papers, filters)
        
        assert len(filtered) == 1
        assert filtered[0].title == "Popular"
    
    def test_apply_filters_fields_of_study(self, agent):
        """Test fields of study filter application."""
        papers = [
            AcademicSource(
                title="AI Paper", 
                fields_of_study=["Artificial Intelligence"]
            ),
            AcademicSource(
                title="Bio Paper", 
                fields_of_study=["Biology"]
            ),
        ]
        filters = AcademicSearchFilters(fields_of_study=["Artificial Intelligence"])
        
        filtered = agent._apply_filters(papers, filters)
        
        assert len(filtered) == 1
        assert filtered[0].title == "AI Paper"
    
    def test_apply_filters_open_access(self, agent):
        """Test open access filter application."""
        papers = [
            AcademicSource(title="Open", is_open_access=True),
            AcademicSource(title="Closed", is_open_access=False),
        ]
        filters = AcademicSearchFilters(open_access_only=True)
        
        filtered = agent._apply_filters(papers, filters)
        
        assert len(filtered) == 1
        assert filtered[0].title == "Open"


# =============================================================================
# Test Class: Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Tests for module-level helper functions."""
    
    def test_should_use_academic_search_by_type(self):
        """Test academic search decision based on query type."""
        assert should_use_academic_search("technical", "how to implement") is True
        assert should_use_academic_search("scientific", "test") is True
        assert should_use_academic_search("medical", "treatment") is True
        assert should_use_academic_search("general", "weather today") is False
    
    def test_should_use_academic_search_by_keywords(self):
        """Test academic search decision based on query keywords."""
        assert should_use_academic_search("general", "latest research on AI") is True
        assert should_use_academic_search("general", "peer-reviewed study") is True
        assert should_use_academic_search("general", "meta-analysis of data") is True
        assert should_use_academic_search("general", "what is the capital") is False
    
    def test_get_academic_filters_breaking_news(self):
        """Test filters for breaking/current queries."""
        analysis = {"time_sensitivity": "breaking", "required_depth": "detailed"}
        filters = get_academic_filters_from_query_analysis(analysis)
        
        current_year = datetime.now().year
        assert filters.year_min == current_year - 1
    
    def test_get_academic_filters_current(self):
        """Test filters for current queries."""
        analysis = {"time_sensitivity": "current", "required_depth": "detailed"}
        filters = get_academic_filters_from_query_analysis(analysis)
        
        current_year = datetime.now().year
        assert filters.year_min == current_year - 3
    
    def test_get_academic_filters_comprehensive_depth(self):
        """Test filters for comprehensive depth queries."""
        analysis = {"time_sensitivity": "any", "required_depth": "comprehensive"}
        filters = get_academic_filters_from_query_analysis(analysis)
        
        assert filters.min_citations == 10
    
    def test_get_academic_filters_exhaustive_depth(self):
        """Test filters for exhaustive depth queries."""
        analysis = {"time_sensitivity": "any", "required_depth": "exhaustive"}
        filters = get_academic_filters_from_query_analysis(analysis)
        
        assert filters.min_citations == 20


# =============================================================================
# Test Class: Factory Function
# =============================================================================

class TestFactoryFunction:
    """Tests for create_academic_research_agent factory."""
    
    def test_create_default_agent(self):
        """Test creating agent with defaults."""
        agent = create_academic_research_agent()
        assert isinstance(agent, AcademicResearchAgent)
        assert agent.model == "gpt-4o-mini"
    
    def test_create_custom_agent(self):
        """Test creating agent with custom settings."""
        agent = create_academic_research_agent(
            api_key="my_key",
            model="gpt-4o"
        )
        assert agent.model == "gpt-4o"
        assert agent.ss_client.api_key == "my_key"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
