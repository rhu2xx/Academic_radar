# Contributing to Academic Radar

Thank you for your interest in contributing! 🎉

## Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/academic-radar.git
cd academic-radar
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If you create this for testing tools
```

## Project Structure

```
academic-radar/
├── src/
│   ├── agents/          # The 5 LangGraph agent nodes
│   ├── core/            # State management, models, prompts
│   └── tools/           # Utilities (PDF parser, OpenAlex client, etc.)
├── tests/               # Unit tests (add here!)
├── main.py              # Entry point
└── setup.py             # Configuration checker
```

## How to Contribute

### 1. Add New Data Sources

Want to search beyond OpenAlex? Add support for:
- Semantic Scholar
- PubMed
- IEEE Xplore

Create a new client in `src/tools/` following the pattern in `openalex_client.py`.

### 2. Improve Isomorphism Detection

The core "magic" is in `src/core/prompts.py`. You can:
- Refine the ABSTRACTOR prompt for better cross-domain queries
- Enhance the ANALYST prompt for more accurate borrowability scoring
- Add domain-specific prompt variants

### 3. Add New Features

Ideas:
- **Web UI**: Streamlit/Gradio dashboard
- **Citation tracking**: Monitor when discovered papers cite your work
- **Collaboration detection**: Find researchers using similar methods
- **Batch profiling**: Analyze entire research groups

### 4. Testing

We need tests! Priority areas:
- Unit tests for each agent
- Integration tests for the full graph
- Mock LLM responses for deterministic testing

### 5. Documentation

- Add examples of successful "isomorphic discoveries"
- Write tutorials for specific research domains
- Create video walkthroughs

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions focused (Single Responsibility Principle)

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request with a description of changes

## Questions?

Open an issue or discussion on GitHub!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
