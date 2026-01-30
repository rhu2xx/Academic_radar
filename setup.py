#!/usr/bin/env python3
"""
Setup script for initial configuration.
Helps users set up their environment and test the system.
"""
import os
import sys
from pathlib import Path


def check_environment():
    """Check if environment variables are configured."""
    print("🔍 Checking environment configuration...\n")
    
    required_vars = {
        'LLM': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DEEPSEEK_API_KEY'],
        'OpenAlex': ['OPENALEX_EMAIL'],
        'SMTP': ['SMTP_USER', 'SMTP_PASS', 'RECIPIENT_EMAIL']
    }
    
    all_ok = True
    
    for category, vars in required_vars.items():
        print(f"[{category}]")
        category_ok = False
        for var in vars:
            value = os.getenv(var)
            if value:
                print(f"  ✅ {var}: configured")
                category_ok = True
            else:
                print(f"  ❌ {var}: NOT SET")
        
        if not category_ok:
            all_ok = False
            print(f"  ⚠️  At least one {category} variable must be set!\n")
        else:
            print()
    
    return all_ok


def check_directories():
    """Check if required directories exist."""
    print("📁 Checking directories...\n")
    
    dirs = {
        'cache': 'Cache directory (for profile.json)',
        'data/user_papers': 'Your research papers (PDFs)',
        'data/papers': 'Downloaded papers from search'
    }
    
    for dir_path, description in dirs.items():
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}: exists")
        else:
            print(f"  📁 Creating {dir_path}...")
            path.mkdir(parents=True, exist_ok=True)
    
    print()


def check_papers():
    """Check if user has added their papers."""
    print("📄 Checking for user papers...\n")
    
    papers_dir = Path('data/user_papers')
    pdf_files = list(papers_dir.glob('*.pdf'))
    
    if pdf_files:
        print(f"  ✅ Found {len(pdf_files)} PDF(s):")
        for pdf in pdf_files[:5]:
            print(f"     - {pdf.name}")
        if len(pdf_files) > 5:
            print(f"     ... and {len(pdf_files) - 5} more")
    else:
        print("  ⚠️  No PDFs found in data/user_papers/")
        print("     Add your research papers there to create your profile.")
    
    print()


def test_llm_connection():
    """Test LLM connection."""
    print("🤖 Testing LLM connection...\n")
    
    try:
        from src.tools.llm_factory import LLMFactory
        from langchain_core.messages import HumanMessage
        
        llm = LLMFactory.create_chat_model(temperature=0.7)
        response = llm.invoke([HumanMessage(content="Say 'Hello from Academic Radar!'")])
        
        print(f"  ✅ LLM connected successfully")
        print(f"  Response: {response.content[:100]}...\n")
        return True
        
    except Exception as e:
        print(f"  ❌ LLM connection failed: {e}\n")
        return False


def main():
    print("=" * 60)
    print("  🎯 Academic Radar - Setup & Configuration Check")
    print("=" * 60)
    print()
    
    # Check .env file
    if not Path('.env').exists():
        print("⚠️  No .env file found!")
        print("   Copy .env.example to .env and configure your credentials.\n")
        return 1
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run checks
    env_ok = check_environment()
    check_directories()
    check_papers()
    
    if env_ok:
        llm_ok = test_llm_connection()
    else:
        print("⚠️  Skipping LLM test - fix environment variables first.\n")
        llm_ok = False
    
    # Summary
    print("=" * 60)
    if env_ok and llm_ok:
        print("✅ Setup looks good! You're ready to run Academic Radar.")
        print("\nNext steps:")
        print("  1. Place your papers in data/user_papers/")
        print("  2. Run: python main.py --mode profile")
        print("  3. Run: python main.py --mode search")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        return 1
    
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
