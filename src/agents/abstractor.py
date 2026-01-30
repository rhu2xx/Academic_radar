"""
Node B: The Abstractor
Generates diverse search queries to find isomorphic contributions.
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.models import SearchQuery, QueryType
from src.core.prompts import ABSTRACTOR_SYSTEM_PROMPT, ABSTRACTOR_USER_PROMPT
from src.core.state import ResearchState
from src.tools.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


class AbstractorAgent:
    """Agent that generates cross-domain search queries."""
    
    def __init__(self):
        self.llm = LLMFactory.create_chat_model(temperature=0.8)  # Higher temp for creativity
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Execute the abstractor node.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with search queries
        """
        logger.info("🎨 Running Abstractor Agent...")
        
        if not state.get('profile'):
            error_msg = "No profile found. Run profiler first."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
        
        try:
            queries = self._generate_queries(state['profile'])
            state['queries'] = queries
            
            logger.info(f"✅ Generated {len(queries)} search queries:")
            for q in queries:
                logger.info(f"  [{q.query_type.upper()}] {q.query_string}")
            
        except Exception as e:
            error_msg = f"Abstractor failed: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
        
        return state
    
    def _generate_queries(self, profile) -> list[SearchQuery]:
        """
        Generate diverse search queries from profile.
        
        Args:
            profile: ResearchProfile object
            
        Returns:
            List of SearchQuery objects
        """
        # Format the prompt
        user_prompt = ABSTRACTOR_USER_PROMPT.format(
            core_task=profile.core_task,
            mathematical_framework=profile.mathematical_framework,
            pain_points=', '.join(profile.pain_points),
            domain_keywords=', '.join(profile.domain_keywords),
            methodologies=', '.join(profile.methodologies)
        )
        
        messages = [
            SystemMessage(content=ABSTRACTOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        logger.info("Calling LLM to generate queries...")
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        try:
            response_text = response.content.strip()
            
            # Handle markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            queries_data = json.loads(response_text)
            
            # Validate and convert to SearchQuery objects
            queries = []
            for q_data in queries_data:
                try:
                    query = SearchQuery(**q_data)
                    queries.append(query)
                except Exception as e:
                    logger.warning(f"Invalid query data: {q_data}. Error: {e}")
            
            # Ensure we have queries of each type
            query_types = {q.query_type for q in queries}
            missing_types = set(QueryType) - query_types
            if missing_types:
                logger.warning(f"Missing query types: {missing_types}")
            
            return queries
            
        except Exception as e:
            logger.error(f"Failed to parse queries from LLM: {e}")
            logger.debug(f"Raw response: {response.content}")
            raise ValueError(f"Could not parse queries: {e}")


# Node function for LangGraph
def abstractor_node(state: ResearchState) -> ResearchState:
    """LangGraph node wrapper for AbstractorAgent."""
    agent = AbstractorAgent()
    return agent.run(state)
