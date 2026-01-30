"""
Node A: The Profiler
Extracts research profile from user's PDF papers.
"""
import json
import logging
from pathlib import Path
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.models import ResearchProfile
from src.core.prompts import PROFILER_SYSTEM_PROMPT, PROFILER_USER_PROMPT
from src.core.state import ResearchState
from src.tools.pdf_parser import PDFParser
from src.tools.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


class ProfilerAgent:
    """Agent that builds research profiles from user's papers."""
    
    def __init__(self):
        self.llm = LLMFactory.create_chat_model(temperature=0.3)  # Lower temp for extraction
        self.pdf_parser = PDFParser()
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the profiler node.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with research profile
        """
        logger.info("🧬 Running Profiler Agent...")
        
        profile_path = Path(state['profile_path'])
        
        # Check if profile already exists (cached)
        if profile_path.exists():
            logger.info(f"✅ Found cached profile at {profile_path}")
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                state['profile'] = ResearchProfile(**profile_data)
                return state
            except Exception as e:
                logger.warning(f"Failed to load cached profile: {e}. Regenerating...")
        
        # Extract profile from PDFs
        try:
            profile = self._build_profile_from_pdfs(state['user_papers_dir'])
            
            # Cache the profile
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.model_dump(), f, indent=2, default=str)
            
            logger.info(f"💾 Saved profile to {profile_path}")
            state['profile'] = profile
            
        except Exception as e:
            error_msg = f"Profiler failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _build_profile_from_pdfs(self, papers_dir: str) -> ResearchProfile:
        """
        Extract research profile from user's PDFs.
        
        Args:
            papers_dir: Directory containing user's papers
            
        Returns:
            ResearchProfile object
        """
        papers_path = Path(papers_dir)
        if not papers_path.exists():
            raise FileNotFoundError(f"Papers directory not found: {papers_dir}")
        
        # Find all PDFs
        pdf_files = list(papers_path.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {papers_dir}")
        
        logger.info(f"Found {len(pdf_files)} PDF(s) to analyze")
        
        # Extract text from PDFs
        papers_content = []
        source_papers = []
        
        for pdf_file in pdf_files[:5]:  # Limit to 5 papers to avoid token limits
            logger.info(f"Processing {pdf_file.name}...")
            try:
                text = self.pdf_parser.extract_text(str(pdf_file), max_pages=10)
                truncated_text = self.pdf_parser.smart_truncate(text, max_chars=6000)
                papers_content.append(f"=== {pdf_file.name} ===\n{truncated_text}")
                source_papers.append(str(pdf_file))
            except Exception as e:
                logger.warning(f"Failed to process {pdf_file.name}: {e}")
        
        if not papers_content:
            raise ValueError("Failed to extract text from any PDF")
        
        # Call LLM to extract profile
        combined_content = "\n\n".join(papers_content)
        
        messages = [
            SystemMessage(content=PROFILER_SYSTEM_PROMPT),
            HumanMessage(content=PROFILER_USER_PROMPT.format(papers_content=combined_content))
        ]
        
        logger.info("Calling LLM to extract research profile...")
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.content.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            profile_data = json.loads(response_text)
            profile_data['source_papers'] = source_papers
            
            profile = ResearchProfile(**profile_data)
            logger.info(f"✅ Profile extracted successfully")
            logger.info(f"  Core Task: {profile.core_task}")
            logger.info(f"  Pain Points: {', '.join(profile.pain_points)}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Raw response: {response.content}")
            raise ValueError(f"Could not parse profile from LLM response: {e}")


# Node function for LangGraph
def profiler_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for ProfilerAgent."""
    agent = ProfilerAgent()
    return agent.run(state)
