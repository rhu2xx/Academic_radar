"""
Node C: The Scout
Searches OpenAlex for papers matching the generated queries.
"""
import logging
import os
import random
from datetime import datetime, timedelta
from typing import List, Set

from src.core.models import PaperMetadata, QueryType
from src.core.state import ResearchState
from src.tools.openalex_client import OpenAlexClient
from src.tools.paper_tracker import PaperTracker

logger = logging.getLogger(__name__)


class ScoutAgent:
    """Agent that searches for papers on OpenAlex with deep search saturation."""
    
    def __init__(self):
        email = os.getenv('OPENALEX_EMAIL')
        if not email:
            raise ValueError("OPENALEX_EMAIL not set in environment")
        
        # Optional API key for premium access
        api_key = os.getenv('OPENALEX_API_KEY')
        
        self.client = OpenAlexClient(
            email=email, 
            api_key=api_key,
            rate_limit_delay=3.0
        )
        self.search_days_back = int(os.getenv('SEARCH_DAYS_BACK', 7))
        self.max_results_per_query = int(os.getenv('MAX_RESULTS_PER_QUERY', 20))
        self.tracker = PaperTracker()
        
        # Deep Search Configuration
        self.target_new_papers = int(os.getenv('TARGET_NEW_PAPERS', 5))
        self.max_pages_to_scan = int(os.getenv('MAX_PAGES_TO_SCAN', 5))
        
        logger.info(f"Scout configured: target={self.target_new_papers} new papers, max_pages={self.max_pages_to_scan}")
    
    def _select_sort_strategy(self, query_type: QueryType) -> str:
        """
        Select sort strategy based on query type using stochastic mixing.
        
        For direct queries: Always use recency (publication_date:desc)
        For isomorphic/solution queries: Probabilistic mix to surface older relevant papers
        
        Args:
            query_type: The type of query being executed
            
        Returns:
            Sort string for OpenAlex API
        """
        if query_type == QueryType.DIRECT:
            # Direct queries: Always prioritize recent papers
            strategy = 'publication_date:desc'
            logger.debug(f"  🎲 Sort strategy [DIRECT]: {strategy} (deterministic)")
            return strategy
        
        # Isomorphic & Solution-seeking queries: Stochastic mix
        # This helps surface older highly-relevant papers that might be missed
        rand = random.random()
        
        if rand < 0.40:
            # 40% chance: Relevance score (best for finding deep math matches)
            strategy = 'relevance_score:desc'
            emoji = "🎯"
        elif rand < 0.70:
            # 30% chance: Citation count (finds high-impact papers)
            strategy = 'cited_by_count:desc'
            emoji = "⭐"
        else:
            # 30% chance: Recency (newest papers)
            strategy = 'publication_date:desc'
            emoji = "📅"
        
        logger.info(f"  🎲 Sort strategy [{query_type.upper()}]: {emoji} {strategy}")
        return strategy
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the scout node with deep search saturation.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with discovered papers
        """
        logger.info("🔍 Running Scout Agent (Deep Search Mode)...")
        
        if not state.get('queries'):
            error_msg = "No queries found. Run abstractor first."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        try:
            # Use saturation loop to find target number of new papers
            new_papers = self._search_until_saturated(state['queries'])
            
            state['raw_papers'] = new_papers
            
            logger.info(f"✅ Deep search complete: {len(new_papers)} new papers discovered")
            
        except Exception as e:
            error_msg = f"Scout failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _search_until_saturated(self, queries) -> List[PaperMetadata]:
        """
        Deep search with saturation loop - keeps fetching pages until target is met.
        
        Args:
            queries: List of SearchQuery objects
            
        Returns:
            List of NEW (unseen) PaperMetadata
        """
        # Calculate date filter
        from_date = datetime.utcnow() - timedelta(days=self.search_days_back)
        logger.info(f"🔍 Deep search: papers published after {from_date.date()}")
        logger.info(f"🎯 Target: {self.target_new_papers} new papers (max {self.max_pages_to_scan} pages per query)")
        
        all_new_papers = []
        seen_ids: Set[str] = set()  # Track IDs within this search session
        
        for query in queries:
            logger.info(f"📋 Query [{query.query_type}]: {query.query_string}")
            
            # Select sort strategy based on query type
            sort_strategy = self._select_sort_strategy(query.query_type)
            
            query_new_papers = []
            page = 1
            
            # Saturation loop for this query
            while page <= self.max_pages_to_scan:
                try:
                    # Fetch one page with selected sort strategy
                    papers = self.client.search_papers(
                        query=query.query_string,
                        from_date=from_date,
                        max_results=self.max_results_per_query,
                        page=page,
                        sort=sort_strategy
                    )
                    
                    if not papers:
                        logger.info(f"  📭 Page {page}: No more results available")
                        break
                    
                    # Check each paper for duplicates
                    page_new_count = 0
                    page_duplicate_count = 0
                    
                    for paper in papers:
                        # Skip if seen in this search session
                        if paper.openalex_id in seen_ids:
                            page_duplicate_count += 1
                            continue
                        
                        # Check if already sent historically (by ID and title)
                        if self.tracker.is_duplicate(paper.openalex_id, paper.title):
                            page_duplicate_count += 1
                            continue
                        
                        # This is a NEW paper!
                        query_new_papers.append(paper)
                        seen_ids.add(paper.openalex_id)
                        page_new_count += 1
                    
                    logger.info(f"  📄 Page {page}: {page_new_count} new, {page_duplicate_count} duplicates")
                    
                    # Check if we've met the target for this query
                    if len(query_new_papers) >= self.target_new_papers:
                        logger.info(f"  ✅ Target reached: {len(query_new_papers)} new papers found")
                        break
                    
                    # If this page had mostly duplicates, dig deeper
                    if page_new_count > 0 and page < self.max_pages_to_scan:
                        logger.info(f"  ⛏️  Digging to page {page + 1} to find more new papers...")
                        page += 1
                    else:
                        break
                        
                except Exception as e:
                    logger.warning(f"  ⚠️  Page {page} failed: {e}")
                    break
            
            # Add this query's new papers to the total
            all_new_papers.extend(query_new_papers)
            logger.info(f"  🎯 Query total: {len(query_new_papers)} new papers")
        
        # Sort by publication date (newest first)
        all_new_papers.sort(key=lambda p: p.publication_date, reverse=True)
        
        # Log statistics
        if all_new_papers:
            fields = {}
            for paper in all_new_papers:
                field = paper.primary_field or 'Unknown'
                fields[field] = fields.get(field, 0) + 1
            
            logger.info("📊 Field distribution:")
            for field, count in sorted(fields.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"  • {field}: {count}")
        else:
            logger.warning("📭 No new papers found across all queries")
        
        return all_new_papers


# Node function for LangGraph
def scout_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for ScoutAgent."""
    agent = ScoutAgent()
    return agent.run(state)
