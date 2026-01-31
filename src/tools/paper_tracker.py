"""
Paper Tracker - Prevents duplicate paper notifications.
Maintains a history of papers that have been sent to the user.
"""
import json
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Set, List, Optional

logger = logging.getLogger(__name__)


class PaperTracker:
    """
    Tracks papers that have been sent to prevent duplicates.
    
    Stores paper OpenAlex IDs and normalized titles in a JSON file with timestamps.
    Automatically cleans up old entries to prevent unbounded growth.
    """
    
    def __init__(self, cache_file: str = "./cache/sent_papers.json"):
        """
        Initialize the paper tracker.
        
        Args:
            cache_file: Path to the tracking file
        """
        self.cache_file = Path(cache_file)
        cache_data = self._load_cache()
        self.sent_papers = cache_data.get('papers', {})
        self.sent_titles = cache_data.get('titles', {})
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normalize a paper title for duplicate detection.
        
        Removes punctuation, extra spaces, and converts to lowercase
        to catch papers with slightly different formatting.
        
        Args:
            title: Original paper title
            
        Returns:
            Normalized title string
        """
        if not title:
            return ""
        
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common punctuation and special characters
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Strip leading/trailing spaces
        normalized = normalized.strip()
        
        return normalized
    
    def _load_cache(self) -> dict:
        """
        Load the cache of sent papers.
        
        Returns:
            Dict with 'papers' (id -> timestamp) and 'titles' (normalized_title -> timestamp)
        """
        if not self.cache_file.exists():
            logger.info("No paper tracking cache found, creating new one")
            return {'papers': {}, 'titles': {}}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle legacy format (just dict of papers)
                if isinstance(data, dict) and 'papers' not in data:
                    logger.info("Converting legacy cache format to new format with title tracking")
                    result = {
                        'papers': data,
                        'titles': {}
                    }
                    logger.info(f"Loaded {len(data)} previously sent papers from cache (legacy format)")
                    return result
                
                # New format with both papers and titles
                papers_count = len(data.get('papers', {}))
                titles_count = len(data.get('titles', {}))
                logger.info(f"Loaded {papers_count} papers and {titles_count} normalized titles from cache")
                return data
                
        except Exception as e:
            logger.warning(f"Failed to load paper cache: {e}, starting fresh")
            return {'papers': {}, 'titles': {}}
    
    def _save_cache(self):
        """Save the cache to disk."""
        try:
            # Create cache directory if needed
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'papers': self.sent_papers,
                'titles': self.sent_titles
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.debug(f"Saved {len(self.sent_papers)} papers and {len(self.sent_titles)} titles to cache")
        except Exception as e:
            logger.error(f"Failed to save paper cache: {e}")
    
    def is_duplicate(self, paper_id: str, title: Optional[str] = None) -> bool:
        """
        Check if a paper has been sent before.
        
        Checks both by OpenAlex ID and by normalized title to catch
        papers that appear with different IDs or URLs.
        
        Args:
            paper_id: OpenAlex ID of the paper
            title: Paper title (optional, for title-based deduplication)
            
        Returns:
            True if paper was already sent
        """
        # Check by ID first
        if paper_id in self.sent_papers:
            return True
        
        # Also check by normalized title if provided
        if title:
            normalized_title = self.normalize_title(title)
            if normalized_title and normalized_title in self.sent_titles:
                logger.debug(f"Duplicate detected by title: '{title[:50]}...'")
                return True
        
        return False
    
    def mark_as_sent(self, paper_id: str, title: Optional[str] = None):
        """
        Mark a paper as sent.
        
        Args:
            paper_id: OpenAlex ID of the paper
            title: Paper title (optional, for title-based tracking)
        """
        timestamp = datetime.utcnow().isoformat()
        self.sent_papers[paper_id] = timestamp
        
        if title:
            normalized_title = self.normalize_title(title)
            if normalized_title:
                self.sent_titles[normalized_title] = timestamp
        
        self._save_cache()
    
    def mark_multiple_as_sent(self, paper_ids: List[str], titles: Optional[List[str]] = None):
        """
        Mark multiple papers as sent.
        
        Args:
            paper_ids: List of OpenAlex IDs
            titles: List of paper titles (optional, must match paper_ids order)
        """
        timestamp = datetime.utcnow().isoformat()
        
        for i, paper_id in enumerate(paper_ids):
            self.sent_papers[paper_id] = timestamp
            
            # Track by title if provided
            if titles and i < len(titles):
                normalized_title = self.normalize_title(titles[i])
                if normalized_title:
                    self.sent_titles[normalized_title] = timestamp
        
        self._save_cache()
        logger.info(f"Marked {len(paper_ids)} papers as sent")
    
    def filter_duplicates(self, papers: List) -> List:
        """
        Filter out papers that have been sent before.
        
        Checks both by OpenAlex ID and by normalized title.
        
        Args:
            papers: List of PaperMetadata or AnalyzedPaper objects
            
        Returns:
            List with duplicates removed
        """
        new_papers = []
        duplicate_count = 0
        
        for paper in papers:
            # Handle both PaperMetadata and AnalyzedPaper
            paper_id = getattr(paper, 'openalex_id', None)
            title = getattr(paper, 'title', None)
            
            if hasattr(paper, 'metadata'):
                paper_id = paper.metadata.openalex_id
                title = paper.metadata.title
            
            if not paper_id:
                logger.warning("Paper missing OpenAlex ID, including anyway")
                new_papers.append(paper)
                continue
            
            # Check for duplicates by both ID and title
            if self.is_duplicate(paper_id, title):
                duplicate_count += 1
                logger.debug(f"Filtering duplicate: {title[:50] if title else 'Unknown'}")
            else:
                new_papers.append(paper)
        
        if duplicate_count > 0:
            logger.info(f"Filtered out {duplicate_count} duplicate papers (already sent)")
        
        return new_papers
    
    def cleanup_old_entries(self, days_to_keep: int = 365):
        """
        Remove entries older than specified days to prevent unbounded growth.
        
        Args:
            days_to_keep: Keep entries from the last N days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        old_papers_count = len(self.sent_papers)
        old_titles_count = len(self.sent_titles)
        
        self.sent_papers = {
            paper_id: timestamp
            for paper_id, timestamp in self.sent_papers.items()
            if datetime.fromisoformat(timestamp) > cutoff_date
        }
        
        self.sent_titles = {
            title: timestamp
            for title, timestamp in self.sent_titles.items()
            if datetime.fromisoformat(timestamp) > cutoff_date
        }
        
        removed_papers = old_papers_count - len(self.sent_papers)
        removed_titles = old_titles_count - len(self.sent_titles)
        
        if removed_papers > 0 or removed_titles > 0:
            logger.info(f"Cleaned up {removed_papers} old paper IDs and {removed_titles} old titles (older than {days_to_keep} days)")
            self._save_cache()
    
    def get_stats(self) -> dict:
        """
        Get statistics about tracked papers.
        
        Returns:
            Dict with tracking statistics
        """
        if not self.sent_papers:
            return {
                'total_sent': 0,
                'oldest_entry': None,
                'newest_entry': None
            }
        
        timestamps = [datetime.fromisoformat(ts) for ts in self.sent_papers.values()]
        
        return {
            'total_sent': len(self.sent_papers),
            'oldest_entry': min(timestamps).isoformat(),
            'newest_entry': max(timestamps).isoformat()
        }
