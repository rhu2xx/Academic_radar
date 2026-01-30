# 🎯 Academic Radar

An intelligent, multi-agent research pipeline that discovers **isomorphic contributions** across scientific domains.

## 🌟 What Makes This Different?

Academic Radar doesn't just search for papers in your field—it finds solutions from **completely different domains** that solve your specific mathematical constraints. 

**Example:** If you're working on traffic flow optimization with memory bottlenecks, it might discover tensor decomposition techniques from video compression research.

## 🏗️ Architecture

Built on **LangGraph** with 5 specialized agents:

1. **🧬 The Profiler** - Extracts your research DNA from PDFs
2. **🎨 The Abstractor** - Generates cross-domain search queries
3. **🔍 The Scout** - Searches OpenAlex with intelligent filtering
4. **🔬 The Analyst** - Evaluates methodological "borrowability"
5. **📧 The Publisher** - Delivers insights via email

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI/Anthropic/Deepseek API key
- SMTP credentials (Gmail recommended)

### Installation

```bash
# Clone and navigate
cd academic-radar

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Setup Your Research Profile

```bash
# Place your papers in data/user_papers/
mkdir -p data/user_papers
cp /path/to/your/papers/*.pdf data/user_papers/

# Run profiler (one-time)
python main.py --mode profile
```

### Run Weekly Search

```bash
# Manual execution
python main.py --mode search

# Or let GitHub Actions handle it (see below)
```

## 🤖 GitHub Actions Automation

### Setup

1. **Add Secrets** to your repository:
   - `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
   - `SMTP_USER`
   - `SMTP_PASS`
   - `RECIPIENT_EMAIL`
   - `OPENALEX_EMAIL`

2. **Enable Actions** in your repository settings

3. **Commit your profile.json**:
   ```bash
   git add cache/profile.json
   git commit -m "Add research profile"
   git push
   ```

The workflow runs every Monday at 9:00 UTC and emails you discoveries.

## 📁 Project Structure

```
academic-radar/
├── src/
│   ├── agents/          # The 5 LangGraph nodes
│   │   ├── profiler.py
│   │   ├── abstractor.py
│   │   ├── scout.py
│   │   ├── analyst.py
│   │   └── publisher.py
│   ├── core/            # State & data models
│   │   ├── state.py
│   │   ├── models.py
│   │   └── graph.py
│   └── tools/           # Utilities
│       ├── pdf_parser.py
│       ├── openalex_client.py
│       └── llm_factory.py
├── main.py
├── requirements.txt
└── .github/workflows/weekly_radar.yml
```

## 🔧 Configuration

### LLM Selection

Set `LLM_MODEL` in `.env`:
- `gpt-4-turbo-preview` (Default)
- `claude-3-opus-20240229`
- `deepseek-chat`

### Search Parameters

- `MAX_PAPERS_TO_ANALYZE`: Top N papers to deep-dive (default: 5)
- `SEARCH_DAYS_BACK`: Days to look back (default: 7)
- `LLM_TEMPERATURE`: Creativity level (0.0-1.0, default: 0.7)

## 🛠️ Development

### Run Tests

```bash
pytest tests/
```

### Manual Agent Testing

```python
from src.core.graph import build_graph

graph = build_graph()
result = graph.invoke({
    "profile_path": "./cache/profile.json",
    "mode": "search"
})
```

## 📊 Example Output

**Email Subject:** "🎯 Academic Radar: 3 Isomorphic Discoveries This Week"

```
📄 "Efficient Tensor Decomposition for Video Streaming"
   Field: Computer Vision | Relevance: 0.89
   
   💡 Even though this paper is about video compression, it uses 
   Tucker decomposition to reduce memory footprint by 73%—which 
   directly addresses your constraint: "OOM errors in traffic 
   prediction models with long sequences."
   
   🔗 Key Method: Apply low-rank tensor approximation to your 
   spatiotemporal traffic tensors before feeding to the model.
```

## 🤝 Contributing

This is an open-source project! Contributions welcome:
- Add new data sources (Semantic Scholar, PubMed)
- Improve isomorphism detection prompts
- Build a web UI

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Data from [OpenAlex](https://openalex.org/)
