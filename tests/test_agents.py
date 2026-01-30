"""
Sample test file demonstrating how to test Academic Radar agents.

Run with: pytest tests/test_agents.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core.models import ResearchProfile, SearchQuery, QueryType, PaperMetadata, AnalyzedPaper
from src.core.state import ResearchState, GraphMode


class TestProfilerAgent:
    """Test cases for the Profiler agent."""
    
    @pytest.fixture
    def sample_profile_data(self):
        return {
            "core_task": "Spatiotemporal forecasting",
            "mathematical_framework": "Graph neural networks, temporal modeling",
            "pain_points": ["Memory bottlenecks", "Inference latency"],
            "domain_keywords": ["traffic", "prediction"],
            "methodologies": ["GNN", "LSTM"],
            "source_papers": ["test.pdf"]
        }
    
    @pytest.fixture
    def sample_state(self):
        return {
            "mode": GraphMode.PROFILE,
            "user_papers_dir": "data/user_papers",
            "profile_path": "cache/test_profile.json",
            "profile": None,
            "queries": [],
            "raw_papers": [],
            "analyzed_papers": [],
            "email_content": None,
            "skip_email": True,
            "errors": []
        }
    
    @patch('src.agents.profiler.LLMFactory')
    @patch('src.agents.profiler.PDFParser')
    def test_profiler_creates_profile(self, mock_pdf_parser, mock_llm_factory, sample_profile_data, sample_state):
        """Test that profiler agent creates a valid profile."""
        from src.agents.profiler import ProfilerAgent
        
        # Mock PDF parser
        mock_pdf_parser.return_value.extract_text.return_value = "Sample paper text"
        mock_pdf_parser.return_value.smart_truncate.return_value = "Sample paper text"
        
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = f"```json\n{sample_profile_data}\n```"
        mock_llm.invoke.return_value = mock_response
        mock_llm_factory.create_chat_model.return_value = mock_llm
        
        # Run profiler
        agent = ProfilerAgent()
        result_state = agent.run(sample_state)
        
        # Assertions
        assert result_state['profile'] is not None
        assert isinstance(result_state['profile'], ResearchProfile)
        assert result_state['profile'].core_task == "Spatiotemporal forecasting"
        assert len(result_state['profile'].pain_points) == 2


class TestAbstractorAgent:
    """Test cases for the Abstractor agent."""
    
    @pytest.fixture
    def sample_profile(self):
        return ResearchProfile(
            core_task="Traffic prediction",
            mathematical_framework="Graph neural networks",
            pain_points=["Memory issues"],
            domain_keywords=["traffic", "roads"],
            methodologies=["GNN", "LSTM"]
        )
    
    @pytest.fixture
    def sample_state(self, sample_profile):
        return {
            "mode": GraphMode.SEARCH,
            "user_papers_dir": "data/user_papers",
            "profile_path": "cache/profile.json",
            "profile": sample_profile,
            "queries": [],
            "raw_papers": [],
            "analyzed_papers": [],
            "email_content": None,
            "skip_email": True,
            "errors": []
        }
    
    @patch('src.agents.abstractor.LLMFactory')
    def test_abstractor_generates_queries(self, mock_llm_factory, sample_state):
        """Test that abstractor generates diverse query types."""
        from src.agents.abstractor import AbstractorAgent
        
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """```json
[
  {
    "query_type": "direct",
    "query_string": "traffic prediction graph neural networks",
    "rationale": "Direct domain search",
    "expected_domains": ["Transportation"]
  },
  {
    "query_type": "abstracted",
    "query_string": "spatiotemporal graph forecasting",
    "rationale": "Find isomorphic methods",
    "expected_domains": ["Computer Vision", "Social Networks"]
  },
  {
    "query_type": "solution_seeking",
    "query_string": "memory efficient graph models",
    "rationale": "Solves memory issues",
    "expected_domains": ["Machine Learning"]
  }
]
```"""
        mock_llm.invoke.return_value = mock_response
        mock_llm_factory.create_chat_model.return_value = mock_llm
        
        # Run abstractor
        agent = AbstractorAgent()
        result_state = agent.run(sample_state)
        
        # Assertions
        assert len(result_state['queries']) == 3
        query_types = {q.query_type for q in result_state['queries']}
        assert QueryType.DIRECT in query_types
        assert QueryType.ABSTRACTED in query_types
        assert QueryType.SOLUTION_SEEKING in query_types


class TestScoutAgent:
    """Test cases for the Scout agent."""
    
    @pytest.fixture
    def sample_queries(self):
        return [
            SearchQuery(
                query_type=QueryType.DIRECT,
                query_string="test query",
                rationale="test",
                expected_domains=["Test"]
            )
        ]
    
    @pytest.fixture
    def sample_state(self, sample_queries):
        return {
            "mode": GraphMode.SEARCH,
            "user_papers_dir": "data/user_papers",
            "profile_path": "cache/profile.json",
            "profile": None,
            "queries": sample_queries,
            "raw_papers": [],
            "analyzed_papers": [],
            "email_content": None,
            "skip_email": True,
            "errors": []
        }
    
    @patch('src.agents.scout.OpenAlexClient')
    def test_scout_searches_and_deduplicates(self, mock_client_class, sample_state):
        """Test that scout searches and deduplicates results."""
        from src.agents.scout import ScoutAgent
        
        # Mock OpenAlex client
        mock_client = MagicMock()
        mock_paper = PaperMetadata(
            title="Test Paper",
            authors=["Author 1"],
            abstract="Test abstract",
            publication_date=datetime.utcnow(),
            openalex_id="W12345",
            cited_by_count=10
        )
        mock_client.search_papers.return_value = [mock_paper, mock_paper]  # Duplicate
        mock_client_class.return_value = mock_client
        
        # Run scout
        agent = ScoutAgent()
        result_state = agent.run(sample_state)
        
        # Assertions
        assert len(result_state['raw_papers']) == 1  # Deduplicated
        assert result_state['raw_papers'][0].openalex_id == "W12345"


class TestAnalystAgent:
    """Test cases for the Analyst agent."""
    
    @pytest.fixture
    def sample_paper(self):
        return PaperMetadata(
            title="Test Paper",
            authors=["Author 1"],
            abstract="This paper uses tensor decomposition for video compression",
            publication_date=datetime.utcnow(),
            openalex_id="W12345",
            primary_field="Computer Vision",
            cited_by_count=10
        )
    
    @pytest.fixture
    def sample_profile(self):
        return ResearchProfile(
            core_task="Traffic prediction",
            mathematical_framework="Graph neural networks",
            pain_points=["Memory bottlenecks"],
            domain_keywords=["traffic"],
            methodologies=["GNN"]
        )
    
    @pytest.fixture
    def sample_state(self, sample_paper, sample_profile):
        return {
            "mode": GraphMode.SEARCH,
            "user_papers_dir": "data/user_papers",
            "profile_path": "cache/profile.json",
            "profile": sample_profile,
            "queries": [],
            "raw_papers": [sample_paper],
            "analyzed_papers": [],
            "email_content": None,
            "skip_email": True,
            "errors": []
        }
    
    @patch('src.agents.analyst.LLMFactory')
    def test_analyst_scores_borrowability(self, mock_llm_factory, sample_state):
        """Test that analyst scores paper borrowability."""
        from src.agents.analyst import AnalystAgent
        
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """```json
{
  "borrowability_score": 0.85,
  "methodology_summary": "Uses tensor decomposition",
  "isomorphic_connection": "Even though this paper is about video compression, it uses tensor decomposition which addresses memory bottlenecks.",
  "practical_application": "Apply to traffic tensors",
  "confidence": "HIGH"
}
```"""
        mock_llm.invoke.return_value = mock_response
        mock_llm_factory.create_chat_model.return_value = mock_llm
        
        # Run analyst
        agent = AnalystAgent()
        result_state = agent.run(sample_state)
        
        # Assertions
        assert len(result_state['analyzed_papers']) == 1
        paper = result_state['analyzed_papers'][0]
        assert paper.borrowability_score == 0.85
        assert paper.confidence == "HIGH"
        assert "tensor decomposition" in paper.methodology_summary


class TestPublisherAgent:
    """Test cases for the Publisher agent."""
    
    @pytest.fixture
    def sample_analyzed_paper(self):
        metadata = PaperMetadata(
            title="Test Paper",
            authors=["Author 1"],
            abstract="Abstract",
            publication_date=datetime.utcnow(),
            openalex_id="W12345",
            url="https://example.com",
            primary_field="Computer Vision",
            cited_by_count=10
        )
        return AnalyzedPaper(
            metadata=metadata,
            borrowability_score=0.85,
            methodology_summary="Uses tensor decomposition",
            isomorphic_connection="Test connection",
            practical_application="Apply this way",
            confidence="HIGH",
            source_query_type=QueryType.ABSTRACTED
        )
    
    @pytest.fixture
    def sample_state(self, sample_analyzed_paper):
        return {
            "mode": GraphMode.SEARCH,
            "user_papers_dir": "data/user_papers",
            "profile_path": "cache/profile.json",
            "profile": None,
            "queries": [],
            "raw_papers": [],
            "analyzed_papers": [sample_analyzed_paper],
            "email_content": None,
            "skip_email": True,  # Don't actually send email in tests
            "errors": []
        }
    
    def test_publisher_generates_email(self, sample_state):
        """Test that publisher generates email content."""
        from src.agents.publisher import PublisherAgent
        
        # Run publisher
        agent = PublisherAgent()
        result_state = agent.run(sample_state)
        
        # Assertions
        assert result_state['email_content'] is not None
        email = result_state['email_content']
        assert email.papers_count == 1
        assert "Test Paper" in email.html_body
        assert "0.85" in email.html_body
        assert "Test connection" in email.plain_text_body


# Integration test
class TestFullWorkflow:
    """Integration tests for the complete workflow."""
    
    @patch('src.agents.profiler.LLMFactory')
    @patch('src.agents.abstractor.LLMFactory')
    @patch('src.agents.scout.OpenAlexClient')
    @patch('src.agents.analyst.LLMFactory')
    def test_full_search_workflow(self, mock_analyst_llm, mock_client_class, mock_abstractor_llm, mock_profiler_llm):
        """Test the complete search workflow end-to-end."""
        # This would mock all agents and test the full graph execution
        # Implementation left as exercise
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
