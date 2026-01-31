"""
OpenAlex API client.
Handles paper search with rate limiting and polite pool access.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.models import PaperMetadata

logger = logging.getLogger(__name__)


class OpenAlexClient:
    """
    Client for OpenAlex API.
    Supports both polite pool (email) and API key authentication.
    
    Rate limits:
    - No auth: 10 requests/second, 100,000/day
    - Polite pool (email): 100 requests/second, 100,000/day
    - API key: 100 requests/second, 1,000,000/day (Premium)
    """
    
    BASE_URL = "https://api.openalex.org"
    
    def __init__(
        self, 
        email: str, 
        api_key: Optional[str] = None,
        rate_limit_delay: float = 3.0
    ):
        """
        Initialize client.
        
        Args:
            email: Your email for polite pool access (10x faster)
            api_key: Optional API key for premium access (100x daily limit)
            rate_limit_delay: Delay between requests (seconds)
        """
        self.email = email
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = requests.Session()
        
        # Setup headers
        headers = {
            'User-Agent': f'AcademicRadar/1.0 (mailto:{email})',
            'Accept': 'application/json'
        }
        
        # Add API key if provided (premium access)
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
            logger.info("OpenAlex client initialized with API key (Premium: 1M requests/day)")
        else:
            logger.info("OpenAlex client initialized with polite pool (100K requests/day)")
        
        self.session.headers.update(headers)
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _request(self, endpoint: str, params: dict) -> dict:
        """
        Make rate-limited request with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
        """
        self._rate_limit()
        
        # Add polite pool email (still recommended even with API key)
        params['mailto'] = self.email
        
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        # Log rate limit info from response headers
        if 'X-RateLimit-Limit' in response.headers:
            limit = response.headers.get('X-RateLimit-Limit')
            remaining = response.headers.get('X-RateLimit-Remaining')
            logger.debug(f"Rate limit: {remaining}/{limit} requests remaining")
        
        return response.json()
    
    def search_papers(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        max_results: int = 50,
        page: int = 1,
        filter_params: Optional[dict] = None,
        sort: str = 'publication_date:desc'
    ) -> List[PaperMetadata]:
        """
        Search for papers on OpenAlex with pagination support.
        
        Args:
            query: Search query string
            from_date: Only return papers after this date
            max_results: Maximum papers to return per page
            page: Page number (1-indexed)
            filter_params: Additional OpenAlex filters
            sort: Sort order (publication_date:desc, relevance_score:desc, cited_by_count:desc)
            
        Returns:
            List of paper metadata
        """
        params = {
            'search': query,
            'per-page': min(max_results, 200),  # API limit
            'page': page,
            'sort': sort,
        }
        
        # Build filter string
        filters = []
        if from_date:
            date_str = from_date.strftime('%Y-%m-%d')
            filters.append(f'from_publication_date:{date_str}')
        
        # Only include English papers
        filters.append('language:en')
        
        if filter_params:
            for key, value in filter_params.items():
                filters.append(f'{key}:{value}')
        
        if filters:
            params['filter'] = ','.join(filters)
        
        logger.debug(f"Searching OpenAlex: '{query}' page {page} (max {max_results} results)")
        
        try:
            data = self._request('works', params)
            results = data.get('results', [])
            total_results = data.get('meta', {}).get('count', 0)
            
            papers = []
            for work in results[:max_results]:
                try:
                    paper = self._parse_work(work)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing work {work.get('id', 'unknown')}: {e}")
                    continue
            
            logger.debug(f"Found {len(papers)} papers on page {page} (total available: {total_results})")
            return papers
            
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
            return []
    
    def _parse_work(self, work: dict) -> PaperMetadata:
        """Parse OpenAlex work JSON into PaperMetadata."""
        # Extract authors
        authors = []
        for authorship in work.get('authorships', [])[:10]:  # Limit to first 10
            author = authorship.get('author', {}) or {}
            name = author.get('display_name')
            if name:
                authors.append(name)
        
        # Extract publication date
        pub_date_str = work.get('publication_date')
        pub_date = datetime.fromisoformat(pub_date_str) if pub_date_str else datetime.utcnow()
        
        # Extract primary field with robust null checking
        primary_topic = work.get('primary_topic') or {}
        domain = primary_topic.get('domain') or {}
        primary_field = domain.get('display_name', 'Unknown')
        
        # Extract abstract (try direct field first, then inverted index)
        abstract = work.get('abstract')
        if not abstract or abstract.strip() == '':
            # Try to reconstruct from abstract_inverted_index
            inverted_index = work.get('abstract_inverted_index')
            if inverted_index and isinstance(inverted_index, dict):
                try:
                    # Reconstruct abstract from inverted index
                    word_positions = []
                    for word, positions in inverted_index.items():
                        if isinstance(positions, list):
                            for pos in positions:
                                word_positions.append((pos, word))
                    
                    # Sort by position and join
                    word_positions.sort(key=lambda x: x[0])
                    abstract = ' '.join([word for pos, word in word_positions])
                except Exception as e:
                    logger.debug(f"Failed to reconstruct abstract from inverted index: {e}")
                    abstract = ''
        
        abstract = abstract or ''
        
        # Extract URL
        url = work.get('doi')
        if url and not url.startswith('http'):
            url = f"https://doi.org/{url}"
        if not url:
            url = work.get('id')  # Fallback to OpenAlex ID
        
        return PaperMetadata(
            title=work.get('title', 'Untitled'),
            authors=authors,
            abstract=abstract,
            publication_date=pub_date,
            doi=work.get('doi'),
            openalex_id=work.get('id', ''),
            url=url,
            primary_field=primary_field,
            cited_by_count=work.get('cited_by_count', 0)
        )
    
    def get_paper_by_doi(self, doi: str) -> Optional[PaperMetadata]:
        """
        Fetch a specific paper by DOI.
        
        Args:
            doi: Paper DOI
            
        Returns:
            PaperMetadata or None
        """
        try:
            data = self._request(f'works/doi:{doi}', {})
            return self._parse_work(data)
        except Exception as e:
            logger.error(f"Failed to fetch DOI {doi}: {e}")
            return None
