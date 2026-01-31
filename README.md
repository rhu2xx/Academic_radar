# 🎯 Academic Radar

Discover cross-domain research insights automatically. This AI agent searches papers from different fields that solve your specific research challenges.

**Example:** Working on traffic flow optimization? It might find relevant tensor decomposition techniques from video compression research.

## 🏗️ How It Works

5 AI agents working together:

1. **Profiler** - Learns your research interests from your papers
2. **Abstractor** - Generates cross-domain search queries  
3. **Scout** - Searches 250M+ papers on OpenAlex
4. **Analyst** - Scores methodological relevance (0-1)
5. **Publisher** - Emails you weekly discoveries

## 🚀 Quick Start

### 1. Install

```bash
git clone <your-repo>
cd academic-radar
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file:

```bash
# Required
LLM_PROVIDER=deepseek                    # or openai/anthropic
DEEPSEEK_API_KEY=your_key_here
OPENALEX_EMAIL=your@email.com            # For faster API access

# Email (optional - needed for weekly automation)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
RECIPIENT_EMAIL=your@email.com
```

### 3. Create Your Profile

```bash
# Put your papers in data/user_papers/
mkdir -p data/user_papers
cp your_papers/*.pdf data/user_papers/

# Extract research profile (one-time)
python main.py --mode profile
```

### 4. Search for Papers

```bash
# Manual search
python main.py --mode search

# Full pipeline (profile + search + email)
python main.py --mode full
```

## 📧 Weekly Automation

Set up GitHub Actions to run automatically every Monday:

1. Add repository secrets: `DEEPSEEK_API_KEY`, `SMTP_USER`, `SMTP_PASS`, `RECIPIENT_EMAIL`, `OPENALEX_EMAIL`
2. Commit your `cache/profile.json`
3. Enable Actions in repository settings

Done! You'll receive weekly emails with discoveries.

## ⚙️ Key Settings

Edit `.env` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_PAPERS_TO_ANALYZE` | 5 | Papers to analyze per run |
| `SEARCH_DAYS_BACK` | 7 | How far back to search |
| `MIN_BORROWABILITY_SCORE` | 0.5 | Minimum relevance score (0-1) |
| `MAX_RESULTS_PER_QUERY` | 20 | Papers fetched per query |

## 📊 Example Output

**Email:** "🎯 Academic Radar: 3 Discoveries This Week"

```
📄 Efficient Tensor Decomposition for Video Streaming
   Computer Vision • Score: 0.89
   
   💡 This paper uses Tucker decomposition to reduce memory 
   by 73%—directly addressing your "OOM errors in traffic 
   prediction models" constraint.
   
   🔗 Apply low-rank tensor approximation to your 
   spatiotemporal traffic data.
```

## 🔧 Advanced Features

- **No Duplicates**: Tracks sent papers by ID and title
- **Smart Sorting**: Probabilistic mix of relevance/citations/recency
- **English Only**: Filters non-English papers automatically
- **Cost Optimized**: Deduplicates before expensive LLM analysis
- **iOS Compatible**: Email CSS works on all devices

## 📁 Project Structure

```
academic-radar/
├── src/agents/          # 5 AI agents
├── src/core/            # State management
├── src/tools/           # OpenAlex, PDF parsing
├── main.py              # Entry point
└── .github/workflows/   # Automation
```

## 🤝 Contributing

Contributions welcome! Ideas:
- Add Semantic Scholar/PubMed support
- Improve prompt engineering
- Build web UI

## 📄 License

MIT License
