# 🎯 Academic Radar - Project Summary

## Overview

**Academic Radar** is a multi-agent research pipeline that discovers **isomorphic contributions** across scientific domains. Unlike traditional literature search, it finds papers from completely different fields that solve your specific mathematical constraints using methods you might not know.

## Project Structure

```
academic-radar/
├── .github/
│   └── workflows/
│       └── weekly_radar.yml      # GitHub Actions automation
├── docs/
│   ├── example_profile.md        # Sample research profile
│   ├── TROUBLESHOOTING.md        # Common issues & solutions
│   └── USAGE.md                  # Comprehensive usage guide
├── src/
│   ├── agents/                   # The 5 LangGraph nodes
│   │   ├── __init__.py
│   │   ├── profiler.py          # Node A: Profile extraction
│   │   ├── abstractor.py        # Node B: Query generation
│   │   ├── scout.py             # Node C: OpenAlex search
│   │   ├── analyst.py           # Node D: Borrowability scoring
│   │   └── publisher.py         # Node E: Email delivery
│   ├── core/                     # Core system components
│   │   ├── __init__.py
│   │   ├── state.py             # LangGraph state definition
│   │   ├── models.py            # Data models (Pydantic)
│   │   ├── prompts.py           # System prompts for all agents
│   │   └── graph.py             # LangGraph orchestration
│   └── tools/                    # Utility functions
│       ├── __init__.py
│       ├── pdf_parser.py        # PDF text extraction
│       ├── openalex_client.py   # OpenAlex API wrapper
│       └── llm_factory.py       # LLM initialization
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── CONTRIBUTING.md               # Contribution guide
├── LICENSE                       # MIT License
├── main.py                       # Main entry point
├── quickstart.sh                 # Quick setup (Linux/Mac)
├── quickstart.bat                # Quick setup (Windows)
├── README.md                     # Project README
├── requirements.txt              # Python dependencies
└── setup.py                      # Configuration checker
```

## System Architecture

### LangGraph Workflow

```
START
  ↓
[Should Run Profiler?]
  ↓              ↓
Profiler    (Skip if profile exists)
  ↓              ↓
[Continue to Search?]
  ↓              ↓
Abstractor      END
  ↓
Scout (OpenAlex Search)
  ↓
Analyst (Borrowability Scoring)
  ↓
[Should Publish?]
  ↓              ↓
Publisher       END
  ↓
END
```

### Agent Details

#### 1. **Profiler Agent** (`src/agents/profiler.py`)
- **Input**: User's PDF papers
- **Process**: 
  - Extracts text from PDFs (up to 10 pages each)
  - Uses LLM to identify:
    - Core research task
    - Mathematical frameworks
    - Pain points/constraints
    - Domain keywords
    - Current methodologies
- **Output**: `cache/profile.json` (cached for reuse)

#### 2. **Abstractor Agent** (`src/agents/abstractor.py`)
- **Input**: Research profile
- **Process**: Generates 3 types of queries:
  - **Direct**: Domain-specific keywords
  - **Abstracted**: Mathematical patterns (removes domain nouns)
  - **Solution-Seeking**: Targets pain points
- **Output**: 5-8 diverse search queries
- **Key Innovation**: Abstracts domain terminology to find isomorphic methods

#### 3. **Scout Agent** (`src/agents/scout.py`)
- **Input**: Search queries
- **Process**:
  - Executes queries on OpenAlex API
  - Applies date filter (last 7 days by default)
  - Deduplicates by OpenAlex ID
  - Rate-limited (3s delay)
- **Output**: List of paper metadata
- **Features**: Polite pool access, retry logic

#### 4. **Analyst Agent** (`src/agents/analyst.py`)
- **Input**: Papers + Research profile
- **Process**:
  - Selects top 5 papers (diversified by field)
  - For each paper:
    - Extracts methodology from abstract
    - Scores borrowability (0.0-1.0)
    - Generates isomorphic connection statement
    - Provides practical application advice
  - Filters papers below 0.5 threshold
- **Output**: Analyzed papers with scores
- **Key Prompt**: "Even though this paper is about X, it uses Y which addresses your Z"

#### 5. **Publisher Agent** (`src/agents/publisher.py`)
- **Input**: Analyzed papers
- **Process**:
  - Formats HTML email with paper cards
  - Includes plain text fallback
  - Color-codes by borrowability score
- **Output**: Delivered email
- **Transport**: SMTP with TLS

## Key Technologies

### Core Stack
- **Python 3.10+**: Main language
- **LangGraph 0.0.20**: Agent orchestration
- **LangChain 0.1.0**: LLM integration
- **Pydantic 2.5.3**: Data validation

### LLM Providers (Choose one)
- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic**: Claude 3 Opus/Sonnet
- **Deepseek**: Cost-effective alternative

### Data & APIs
- **OpenAlex**: Open academic search engine
- **pymupdf**: PDF text extraction
- **requests + tenacity**: HTTP with retry logic

### Delivery
- **smtplib**: Email delivery
- **GitHub Actions**: Weekly automation

## Configuration

### Required Environment Variables

```env
# LLM (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...

# OpenAlex
OPENALEX_EMAIL=your@email.com

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=app_password
RECIPIENT_EMAIL=recipient@email.com
```

### Optional Settings

```env
PROFILE_CACHE_PATH=./cache/profile.json
MAX_PAPERS_TO_ANALYZE=5
SEARCH_DAYS_BACK=7
LLM_TEMPERATURE=0.7
LLM_MODEL=gpt-4-turbo-preview
```

## Usage

### Initial Setup

```bash
# Install
./quickstart.sh  # or quickstart.bat on Windows

# Verify
python setup.py
```

### Build Profile

```bash
# Add your papers
cp ~/papers/*.pdf data/user_papers/

# Generate profile
python main.py --mode profile
```

### Run Search

```bash
# Weekly search
python main.py --mode search

# Test without email
python main.py --mode search --skip-email
```

### Automate with GitHub Actions

1. Push to GitHub
2. Add secrets (API keys, SMTP creds)
3. Commit `cache/profile.json`
4. Runs every Monday at 9:00 UTC

## Key Features

### 1. Isomorphic Discovery
- Finds methods from different fields solving similar math problems
- Example: Traffic prediction ↔ Video compression (both use tensor decomposition)

### 2. Profile Caching
- One-time profile generation
- Reused across searches
- Update when research direction changes

### 3. Smart Query Generation
- Direct: Same domain
- Abstracted: Cross-domain
- Solution-seeking: Pain point focused

### 4. Borrowability Scoring
- 0.0-1.0 quantitative score
- Qualitative explanation
- Practical application advice

### 5. Rate-Limited & Respectful
- 3-second delays between API calls
- OpenAlex polite pool (10x faster)
- Retry logic for reliability

### 6. HTML Email Reports
- Beautiful formatting
- Color-coded scores
- Direct links to papers

## Customization Points

### Prompts (`src/core/prompts.py`)
- Modify extraction logic
- Adjust query generation
- Change borrowability criteria
- Customize email templates

### Search Parameters (`.env`)
- Date range (SEARCH_DAYS_BACK)
- Number of papers (MAX_PAPERS_TO_ANALYZE)
- LLM model and temperature

### Data Sources
- Add Semantic Scholar
- Add ArXiv directly
- Add PubMed for bio papers

### Agent Logic
- Enhance PDF section extraction
- Add citation tracking
- Implement paper downloading for full text
- Add collaborative filtering

## Performance

### Typical Run (search mode)
- **Duration**: 5-10 minutes
- **API calls**: 20-30 OpenAlex requests, 10-15 LLM calls
- **Cost**: $0.10-0.50 (using GPT-4)
- **Output**: 1-5 high-quality papers

### Optimization
- Use GPT-3.5 or Deepseek for lower cost
- Cache LLM responses
- Reduce MAX_PAPERS_TO_ANALYZE
- Shorter date ranges

## Limitations

1. **Abstract-only analysis**: Doesn't download full PDFs
2. **7-day window**: May miss older relevant papers
3. **LLM quality**: Dependent on prompt engineering
4. **OpenAlex coverage**: Not all papers are indexed
5. **No citation tracking**: Doesn't track if papers cite you

## Future Enhancements

### Near-term
- [ ] Download and analyze full PDFs
- [ ] Add more data sources
- [ ] Build web UI (Streamlit)
- [ ] Add paper bookmarking

### Long-term
- [ ] Citation tracking
- [ ] Researcher networking
- [ ] Batch profiling for teams
- [ ] Fine-tuned embedding models
- [ ] Graph visualization of research space

## Testing

### Manual Testing
```bash
# Test individual agents
python -c "from src.agents.profiler import ProfilerAgent; ..."

# Visualize graph
python -c "from src.core.graph import visualize_graph; visualize_graph()"

# Check logs
tail -f academic_radar.log
```

### Unit Tests (TODO)
```bash
pytest tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

Key areas:
- Add new data sources
- Improve prompts
- Write tests
- Build web UI
- Documentation

## License

MIT License - See [LICENSE](LICENSE)

## Support

- **Documentation**: `docs/` folder
- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions

## Credits

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [OpenAlex](https://openalex.org/) - Open academic data
- [LangChain](https://github.com/langchain-ai/langchain) - LLM integration

---

**Made with ❤️ for researchers who want to think beyond their field.**

Last updated: January 30, 2026
