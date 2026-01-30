"""
Node C: The Scout
Searches OpenAlex for papers matching the generated queries.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import List, Set

from src.core.models import PaperMetadata
from src.core.state import ResearchState
from src.tools.openalex_client import OpenAlexClient

logger = logging.getLogger(__name__)


class ScoutAgent:
    """Agent that searches for papers on OpenAlex."""
    
    def __init__(self):
        email = os.getenv('OPENALEX_EMAIL')
        if not email:
            raise ValueError("OPENALEX_EMAIL not set in environment")
        
        self.client = OpenAlexClient(email=email, rate_limit_delay=3.0)
        self.search_days_back = int(os.getenv('SEARCH_DAYS_BACK', 7))
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the scout node.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with discovered papers
        """
        logger.info("🔍 Running Scout Agent...")
        
        if not state.get('queries'):
            error_msg = "No queries found. Run abstractor first."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        try:
            papers = self._search_all_queries(state['queries'])
            state['raw_papers'] = papers
            
            logger.info(f"✅ Found {len(papers)} unique papers")
            
        except Exception as e:
            error_msg = f"Scout failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _search_all_queries(self, queries) -> List[PaperMetadata]:
        """
        Execute all search queries and deduplicate results.
        
        Args:
            queries: List of SearchQuery objects
            
        Returns:
            Deduplicated list of PaperMetadata
        """
        # Calculate date filter
        from_date = datetime.utcnow() - timedelta(days=self.search_days_back)
        logger.info(f"Searching for papers published after {from_date.date()}")
        
        all_papers = []
        seen_ids: Set[str] = set()
        
        for query in queries:
            # Simplify query - take only first 3-5 key terms
            simplified_query = self._simplify_query(query.query_string)
            logger.info(f"Executing query: [{query.query_type}] {simplified_query}")
            
            try:
                papers = self.client.search_papers(
                    query=simplified_query,
                    from_date=from_date,
                    max_results=20  # Limit per query
                )
                
                # Deduplicate by OpenAlex ID
                new_papers = 0
                for paper in papers:
                    if paper.openalex_id not in seen_ids:
                        all_papers.append(paper)
                        seen_ids.add(paper.openalex_id)
                        new_papers += 1
                
                logger.info(f"  → Found {len(papers)} papers ({new_papers} new)")
                
            except Exception as e:
                logger.warning(f"Query failed: {e}")
                continue
        
        # Sort by publication date (newest first)
        all_papers.sort(key=lambda p: p.publication_date, reverse=True)
        
        # Log some statistics
        if all_papers:
            fields = {}
            for paper in all_papers:
                field = paper.primary_field or 'Unknown'
                fields[field] = fields.get(field, 0) + 1
            
            logger.info("Field distribution:")
            for field, count in sorted(fields.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"  {field}: {count}")
        
        return all_papers
    
    def _simplify_query(self, query_string: str) -> str:
        """
        Simplify a query by taking the most important keywords.
        OpenAlex works better with shorter, focused queries.
        
        Args:
            query_string: Original query
            
        Returns:
            Simplified query with 3-5 key terms
        """
        # Split into words and remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as'}
        words = query_string.lower().split()
        
        # Keep important words (not stop words)
        important_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Take first 3-5 most important terms
        key_terms = important_words[:5]
        
        simplified = ' '.join(key_terms)
        logger.debug(f"Simplified '{query_string}' -> '{simplified}'")
        
        return simplified


# Node function for LangGraph
def scout_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for ScoutAgent."""
    agent = ScoutAgent()
    return agent.run(state)
