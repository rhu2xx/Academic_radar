#!/usr/bin/env python3
"""
Academic Radar - Main Entry Point
Orchestrates the multi-agent research pipeline.
"""
import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.core.graph import build_graph, GraphMode
from src.core.state import ResearchState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('academic_radar.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Academic Radar - Discover isomorphic research across domains"
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['profile', 'search', 'full'],
        default='search',
        help='Execution mode: profile (build profile only), search (use existing profile), full (both)'
    )
    parser.add_argument(
        '--papers-dir',
        type=str,
        default='./data/user_papers',
        help='Directory containing user PDFs (for profile mode)'
    )
    parser.add_argument(
        '--profile-path',
        type=str,
        default='./cache/profile.json',
        help='Path to cached research profile'
    )
    parser.add_argument(
        '--skip-email',
        action='store_true',
        help='Skip email delivery (useful for testing)'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info(f"🎯 Starting Academic Radar in '{args.mode}' mode")
        
        # Build the LangGraph
        graph = build_graph()
        
        # Prepare initial state
        initial_state: ResearchState = {
            "mode": GraphMode(args.mode),
            "user_papers_dir": args.papers_dir,
            "profile_path": args.profile_path,
            "profile": None,
            "queries": [],
            "raw_papers": [],
            "analyzed_papers": [],
            "email_content": None,
            "skip_email": args.skip_email,
            "errors": []
        }
        
        # Execute the graph
        logger.info("🚀 Executing agent workflow...")
        final_state = graph.invoke(initial_state)
        
        # Report results
        if final_state.get("errors"):
            logger.error(f"❌ Completed with {len(final_state['errors'])} errors:")
            for error in final_state['errors']:
                logger.error(f"  - {error}")
        else:
            logger.info("✅ Academic Radar completed successfully!")
            
            if args.mode in ['search', 'full']:
                analyzed = final_state.get('analyzed_papers', [])
                logger.info(f"📊 Found {len(analyzed)} relevant papers")
                
                if not args.skip_email:
                    logger.info("📧 Results delivered via email")
        
        return 0 if not final_state.get("errors") else 1
        
    except KeyboardInterrupt:
        logger.warning("⚠️  Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"💥 Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
