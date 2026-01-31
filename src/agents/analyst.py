"""
Node D: The Analyst
Analyzes papers for methodological borrowability.
"""
import json
import logging
import os
from typing import List, Optional, Set
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.models import AnalyzedPaper, PaperMetadata
from src.core.prompts import ANALYST_SYSTEM_PROMPT, ANALYST_USER_PROMPT
from src.core.state import ResearchState
from src.tools.llm_factory import LLMFactory
from src.tools.paper_tracker import PaperTracker

logger = logging.getLogger(__name__)


class AnalystAgent:
    """Agent that evaluates borrowability of discovered papers."""
    
    def __init__(self):
        self.llm = LLMFactory.create_chat_model(temperature=0.5)
        self.max_papers = int(os.getenv('MAX_PAPERS_TO_ANALYZE', 5))
        self.min_score = float(os.getenv('MIN_BORROWABILITY_SCORE', 0.5))
        self.tracker = PaperTracker()
    
    def _deduplicate_in_batch(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        """
        Remove duplicate papers by normalized title BEFORE LLM analysis.
        
        This prevents wasting LLM tokens on papers that will be filtered later.
        
        Args:
            papers: List of papers to deduplicate
            
        Returns:
            List of unique papers
        """
        seen_titles: Set[str] = set()
        unique_papers = []
        duplicates_removed = 0
        
        for paper in papers:
            normalized_title = self.tracker.normalize_title(paper.title)
            
            if normalized_title in seen_titles:
                duplicates_removed += 1
                logger.debug(f"🚫 Pre-analysis duplicate: '{paper.title[:60]}...'")
            else:
                seen_titles.add(normalized_title)
                unique_papers.append(paper)
        
        if duplicates_removed > 0:
            logger.info(f"🔍 Removed {duplicates_removed} duplicates BEFORE LLM analysis")
        
        return unique_papers
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the analyst node.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with analyzed papers
        """
        logger.info("🔬 Running Analyst Agent...")
        
        if not state.get('raw_papers'):
            error_msg = "No papers found. Run scout first."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        if not state.get('profile'):
            error_msg = "No profile found. Run profiler first."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        try:
            # Step 1: Remove duplicates BEFORE expensive LLM analysis
            raw_papers = state['raw_papers']
            deduplicated_papers = self._deduplicate_in_batch(raw_papers)
            
            if len(deduplicated_papers) < len(raw_papers):
                saved_llm_calls = len(raw_papers) - len(deduplicated_papers)
                logger.info(f"💰 Cost optimization: Avoided {saved_llm_calls} unnecessary LLM analyses")
            
            # Step 2: Select top papers to analyze
            papers_to_analyze = self._select_papers(deduplicated_papers)
            logger.info(f"Analyzing papers to find {self.max_papers} with score >= {self.min_score}...")
            
            analyzed_papers = []
            papers_analyzed_count = 0
            
            for paper in papers_to_analyze:
                # Stop if we already have enough high-quality papers
                if len(analyzed_papers) >= self.max_papers:
                    logger.info(f"✅ Target reached: {self.max_papers} papers collected")
                    break
                
                try:
                    papers_analyzed_count += 1
                    analysis = self._analyze_paper(paper, state['profile'])
                    
                    if analysis and analysis.borrowability_score >= self.min_score:
                        analyzed_papers.append(analysis)
                        logger.info(f"  ✓ {paper.title[:60]}... (score: {analysis.borrowability_score:.2f}) [{len(analyzed_papers)}/{self.max_papers}]")
                    else:
                        score_str = f"{analysis.borrowability_score:.2f}" if analysis else "N/A"
                        logger.info(f"  ✗ {paper.title[:60]}... (score: {score_str}, threshold: {self.min_score})")
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze paper: {e}")
                    continue
            
            logger.info(f"📊 Analyzed {papers_analyzed_count} papers, found {len(analyzed_papers)} above threshold")
            
            # Sort by borrowability score
            analyzed_papers.sort(key=lambda p: p.borrowability_score, reverse=True)
            
            state['analyzed_papers'] = analyzed_papers
            logger.info(f"✅ {len(analyzed_papers)} papers passed borrowability threshold")
            
        except Exception as e:
            error_msg = f"Analyst failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _select_papers(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        """
        Select most promising papers to analyze in depth.
        
        Since some papers may not pass the borrowability threshold,
        we return MORE than max_papers to ensure we can collect enough.
        
        Args:
            papers: All discovered papers
            
        Returns:
            Subset to analyze (typically 2-3x max_papers to account for filtering)
        """
        # Analyze up to 3x the target to account for papers below threshold
        analyze_limit = self.max_papers * 3
        
        # Filter papers with abstracts
        with_abstracts = [p for p in papers if p.abstract and len(p.abstract) > 100]
        
        if not with_abstracts:
            logger.warning("No papers with substantial abstracts found")
            return papers[:analyze_limit]
        
        # Diversify by field
        selected = []
        seen_fields = set()
        
        for paper in with_abstracts:
            if len(selected) >= analyze_limit:
                break
            
            field = paper.primary_field or 'Unknown'
            
            # Prefer papers from new fields
            if field not in seen_fields or len(selected) < analyze_limit // 2:
                selected.append(paper)
                seen_fields.add(field)
        
        # Fill remaining slots with any papers
        remaining = analyze_limit - len(selected)
        if remaining > 0:
            for paper in with_abstracts:
                if paper not in selected:
                    selected.append(paper)
                    if len(selected) >= analyze_limit:
                        break
        
        logger.info(f"📋 Selected {len(selected)} candidate papers (target: {self.max_papers} final papers)")
        return selected
    
    def _analyze_paper(self, paper: PaperMetadata, profile) -> Optional[AnalyzedPaper]:
        """
        Analyze a single paper for borrowability.
        
        Args:
            paper: Paper to analyze
            profile: User's research profile
            
        Returns:
            AnalyzedPaper or None if analysis fails
        """
        # Format the prompt
        user_prompt = ANALYST_USER_PROMPT.format(
            core_task=profile.core_task,
            mathematical_framework=profile.mathematical_framework,
            pain_points=', '.join(profile.pain_points),
            paper_title=paper.title,
            paper_abstract=paper.abstract,
            paper_methodology="[Abstract-based analysis]",  # We don't download full PDFs in this version
            paper_field=paper.primary_field or 'Unknown'
        )
        
        messages = [
            SystemMessage(content=ANALYST_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Handle markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            analysis_data = json.loads(response_text)
            
            # Create AnalyzedPaper object
            analyzed = AnalyzedPaper(
                metadata=paper,
                borrowability_score=analysis_data['borrowability_score'],
                methodology_summary=analysis_data['methodology_summary'],
                isomorphic_connection=analysis_data['isomorphic_connection'],
                practical_application=analysis_data['practical_application'],
                confidence=analysis_data['confidence'],
                source_query_type='abstracted'  # Default; could track this from Scout
            )
            
            return analyzed
            
        except Exception as e:
            logger.error(f"Failed to analyze paper '{paper.title}': {e}")
            return None


# Node function for LangGraph
def analyst_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for AnalystAgent."""
    agent = AnalystAgent()
    return agent.run(state)
