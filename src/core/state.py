"""
LangGraph state definition for Academic Radar.
Defines the shared state that flows through all agent nodes.
"""
from enum import Enum
from typing import TypedDict, List, Optional
from src.core.models import (
    ResearchProfile,
    SearchQuery,
    PaperMetadata,
    AnalyzedPaper,
    EmailReport
)


class GraphMode(str, Enum):
    """Execution modes for the graph."""
    PROFILE = "profile"  # Only run profiler
    SEARCH = "search"    # Use existing profile to search
    FULL = "full"        # Profile + search


class ResearchState(TypedDict):
    """
    The state object passed between LangGraph nodes.
    Each agent reads/writes specific fields.
    """
    # Execution control
    mode: GraphMode
    skip_email: bool
    
    # Node A: Profiler inputs/outputs
    user_papers_dir: str  # Path to user's PDFs
    profile_path: str     # Where to cache profile.json
    profile: Optional[ResearchProfile]  # Extracted profile
    
    # Node B: Abstractor outputs
    queries: List[SearchQuery]  # Generated search queries
    
    # Node C: Scout outputs
    raw_papers: List[PaperMetadata]  # Papers found on OpenAlex
    
    # Node D: Analyst outputs
    analyzed_papers: List[AnalyzedPaper]  # Papers with borrowability scores
    
    # Node E: Publisher outputs
    email_content: Optional[EmailReport]
    
    # Error tracking
    errors: List[str]  # Accumulated errors (non-fatal)
