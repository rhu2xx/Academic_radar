# Academic Radar - Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Building Your Research Profile](#building-your-research-profile)
4. [Running Searches](#running-searches)
5. [Understanding Results](#understanding-results)
6. [Automation](#automation)
7. [Advanced Usage](#advanced-usage)

---

## Installation

### Option 1: Quick Start (Recommended)

**Linux/Mac:**
```bash
chmod +x quickstart.sh
./quickstart.sh
```

**Windows:**
```batch
quickstart.bat
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/user_papers cache

# Copy environment template
cp .env.example .env
```

---

## Configuration

### 1. Edit `.env` File

Open `.env` and configure:

```env
# Choose ONE LLM provider
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
# OR
DEEPSEEK_API_KEY=sk-...

# OpenAlex (required)
OPENALEX_EMAIL=your_email@example.com

# Email delivery (required)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
RECIPIENT_EMAIL=where_to_send_reports@example.com
```

### 2. Gmail Setup (Recommended)

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use this password in `SMTP_PASS`

### 3. Test Configuration

```bash
python setup.py
```

This checks:
- Environment variables
- Directory structure
- LLM connection
- Available papers

---

## Building Your Research Profile

### Step 1: Add Your Papers

Place 3-5 of your recent research papers in `data/user_papers/`:

```bash
cp ~/Downloads/my_paper_2024.pdf data/user_papers/
cp ~/Downloads/my_conference_paper.pdf data/user_papers/
```

**Tips:**
- Use your actual research papers (not reviews or textbooks)
- PDFs should be text-based (not scanned images)
- 3-5 papers provide the best balance
- More recent papers = more accurate profile

### Step 2: Generate Profile

```bash
python main.py --mode profile
```

This will:
1. Extract text from your PDFs
2. Call the LLM to analyze your research
3. Generate a `cache/profile.json` file
4. Save it for future use

**What gets extracted:**
- Core research task
- Mathematical frameworks
- Pain points and constraints
- Domain keywords
- Current methodologies

### Step 3: Review Profile

```bash
cat cache/profile.json
```

Check if it accurately represents your work. You can manually edit this file if needed!

---

## Running Searches

### Basic Search

```bash
python main.py --mode search
```

This will:
1. Load your cached profile
2. Generate diverse search queries
3. Search OpenAlex for recent papers (last 7 days)
4. Analyze papers for borrowability
5. Email you the results

### Full Run (Profile + Search)

```bash
python main.py --mode full
```

Use this if you want to rebuild the profile and search in one go.

### Test Mode (No Email)

```bash
python main.py --mode search --skip-email
```

Results are generated but not emailed. Check logs to see what was found.

---

## Understanding Results

### Email Structure

You'll receive an email with:

**Header:**
- Number of discoveries
- Date of the scan

**For each paper:**
- **Title & Metadata**: Paper title, field, authors, date
- **Borrowability Score**: 0.0-1.0 (higher = more applicable)
- **Isomorphic Connection**: The key insight explaining why this paper matters to you
- **Methodology**: What technique the paper uses
- **How to Apply**: Practical advice for adapting the method

### Interpreting Scores

- **0.9-1.0**: Near-perfect fit; same math, different domain
- **0.7-0.9**: Strong relevance; moderate adaptation needed
- **0.5-0.7**: Interesting idea; requires significant rethinking
- **<0.5**: Rejected (not shown in email)

### Example Result

```
📄 "Efficient Tensor Decomposition for Video Streaming"
   Field: Computer Vision | Borrowability: 0.89
   
   💡 Even though this paper is about video compression, it uses 
   Tucker decomposition to reduce memory footprint by 73%—which 
   directly addresses your constraint: "OOM errors in traffic 
   prediction models."
   
   🔧 Apply Tucker decomposition to your traffic tensor 
   (time × location × features) before feeding to GNN.
```

---

## Automation

### GitHub Actions Setup

1. **Push your repository to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/academic-radar.git
git push -u origin main
```

2. **Add GitHub Secrets:**

Go to: `Settings → Secrets and variables → Actions → New repository secret`

Add these secrets:
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
- `OPENALEX_EMAIL`
- `SMTP_USER`
- `SMTP_PASS`
- `RECIPIENT_EMAIL`

3. **Commit your profile:**
```bash
git add cache/profile.json
git commit -m "Add research profile"
git push
```

4. **Enable Actions:**

The workflow runs automatically every Monday at 9:00 UTC.

### Manual Trigger

Go to: `Actions → Weekly Academic Radar Scan → Run workflow`

---

## Advanced Usage

### Custom Search Parameters

Edit `.env`:

```env
# Search last 30 days instead of 7
SEARCH_DAYS_BACK=30

# Analyze top 10 papers instead of 5
MAX_PAPERS_TO_ANALYZE=10

# Use a specific model
LLM_MODEL=gpt-4-turbo-preview

# Adjust creativity (0.0-1.0)
LLM_TEMPERATURE=0.8
```

### Customizing Prompts

Edit `src/core/prompts.py` to:
- Change how profiles are extracted
- Adjust query generation strategy
- Modify borrowability criteria
- Customize email templates

Example - make queries more aggressive:

```python
ABSTRACTOR_SYSTEM_PROMPT = """
... 
Generate 10-15 queries instead of 5-8, being extremely creative...
"""
```

### Running Individual Agents

```python
from src.agents.profiler import ProfilerAgent
from src.agents.abstractor import AbstractorAgent

# Just generate queries from existing profile
agent = AbstractorAgent()
state = {
    'profile': your_profile,
    'queries': [],
    'errors': []
}
result = agent.run(state)
print(result['queries'])
```

### Adding New Data Sources

Create a new client in `src/tools/`:

```python
# src/tools/semantic_scholar_client.py
class SemanticScholarClient:
    def search_papers(self, query: str) -> List[PaperMetadata]:
        # Implementation
        pass
```

Then integrate into Scout agent:

```python
# src/agents/scout.py
from src.tools.semantic_scholar_client import SemanticScholarClient

class ScoutAgent:
    def __init__(self):
        self.openalex = OpenAlexClient(...)
        self.semantic_scholar = SemanticScholarClient(...)
```

### Visualizing the Graph

```bash
python -c "from src.core.graph import visualize_graph; visualize_graph()"
```

Requires: `pip install pygraphviz`

---

## Best Practices

### For Better Profiles
1. Use your most representative recent papers
2. Include papers that show your current direction
3. Avoid papers that are too broad or too narrow
4. Re-profile every 6-12 months as your research evolves

### For Better Search Results
1. Start with 7-day searches (default)
2. If no results, increase to 14 or 30 days
3. Lower borrowability threshold for more exploratory results
4. Review generated queries - do they make sense?

### For Better Analysis
1. Use GPT-4 or Claude Opus for highest quality
2. Increase `MAX_PAPERS_TO_ANALYZE` if you want more diversity
3. Check papers from different fields are being surfaced
4. Read the "practical application" advice critically

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

Quick checks:
```bash
# Test setup
python setup.py

# Check logs
tail -f academic_radar.log

# Verify profile
cat cache/profile.json

# Test LLM connection
python -c "from src.tools.llm_factory import LLMFactory; print(LLMFactory.create_chat_model())"
```

---

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/academic-radar/issues)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

Happy discovering! 🎯
