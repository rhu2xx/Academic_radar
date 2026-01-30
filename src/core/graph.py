"""
LangGraph orchestration for Academic Radar.
Defines the agent workflow and execution flow.
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from src.core.state import ResearchState, GraphMode
from src.agents.profiler import profiler_node
from src.agents.abstractor import abstractor_node
from src.agents.scout import scout_node
from src.agents.analyst import analyst_node
from src.agents.publisher import publisher_node

logger = logging.getLogger(__name__)


def should_skip_profiler(state: ResearchState) -> Literal["run_profiler", "skip_profiler"]:
    """
    Conditional edge: Decide if we need to run the profiler.
    
    - If mode is 'search' and profile exists, skip profiler
    - Otherwise, run profiler
    """
    mode = state['mode']
    
    if mode == GraphMode.SEARCH:
        # In search mode, we expect profile to exist
        logger.info("Mode: SEARCH - Skipping profiler")
        return "skip_profiler"
    else:
        # In profile or full mode, run profiler
        logger.info(f"Mode: {mode.value} - Running profiler")
        return "run_profiler"


def should_continue_to_search(state: ResearchState) -> Literal["continue_search", "end"]:
    """
    Conditional edge: After profiling, decide if we should search.
    
    - If mode is 'profile', stop after profiling
    - Otherwise, continue to search pipeline
    """
    mode = state['mode']
    
    if mode == GraphMode.PROFILE:
        logger.info("Mode: PROFILE - Stopping after profiler")
        return "end"
    else:
        logger.info("Continuing to search pipeline")
        return "continue_search"


def should_publish(state: ResearchState) -> Literal["publish", "end"]:
    """
    Conditional edge: Decide if we should publish results.
    
    - If we have analyzed papers, publish
    - Otherwise, end
    """
    if state.get('analyzed_papers'):
        logger.info(f"Found {len(state['analyzed_papers'])} papers to publish")
        return "publish"
    else:
        logger.info("No papers to publish")
        return "end"


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    
    The graph structure:
    
        START
          ↓
    [Conditional: Should Run Profiler?]
          ↓                    ↓
      Profiler           (Skip Profiler)
          ↓                    ↓
    [Conditional: Continue to Search?]
          ↓                    ↓
      Abstractor             END
          ↓
        Scout
          ↓
       Analyst
          ↓
    [Conditional: Should Publish?]
          ↓                    ↓
      Publisher               END
          ↓
        END
    
    Returns:
        Compiled StateGraph
    """
    # Create the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("profiler", profiler_node)
    workflow.add_node("abstractor", abstractor_node)
    workflow.add_node("scout", scout_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("publisher", publisher_node)
    
    # Add a router node as entry point
    workflow.add_conditional_edges(
        "profiler",
        should_continue_to_search,
        {
            "continue_search": "abstractor",
            "end": END
        }
    )
    
    # Set entry point based on mode
    # We'll use a simple approach: always start with profiler, but it will be smart about caching
    workflow.set_entry_point("profiler")
    
    # Linear flow through search pipeline
    workflow.add_edge("abstractor", "scout")
    workflow.add_edge("scout", "analyst")
    
    # After analyst: decide if we publish
    workflow.add_conditional_edges(
        "analyst",
        should_publish,
        {
            "publish": "publisher",
            "end": END
        }
    )
    
    # Publisher always ends
    workflow.add_edge("publisher", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("✅ LangGraph compiled successfully")
    return app


def visualize_graph(output_path: str = "graph.png"):
    """
    Generate a visualization of the graph structure.
    Requires: pip install pygraphviz
    
    Args:
        output_path: Where to save the image
    """
    try:
        app = build_graph()
        
        # Get mermaid representation
        mermaid = app.get_graph().draw_mermaid()
        print("Graph structure (Mermaid):")
        print(mermaid)
        
        # Try to save PNG if pygraphviz is available
        try:
            img = app.get_graph().draw_png()
            with open(output_path, 'wb') as f:
                f.write(img)
            logger.info(f"Graph visualization saved to {output_path}")
        except Exception as e:
            logger.warning(f"Could not save PNG (install pygraphviz): {e}")
            
    except Exception as e:
        logger.error(f"Visualization failed: {e}")


if __name__ == "__main__":
    # Test graph building
    logging.basicConfig(level=logging.INFO)
    visualize_graph()
