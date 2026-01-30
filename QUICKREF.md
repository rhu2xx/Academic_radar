# 🎯 Academic Radar - Quick Reference Card

## Installation (One Command)

```bash
# Linux/Mac
./quickstart.sh

# Windows
quickstart.bat
```

## Essential Commands

```bash
# Setup check
python setup.py

# Build profile (one-time)
python main.py --mode profile

# Run weekly search
python main.py --mode search

# Test without email
python main.py --mode search --skip-email

# Full run (profile + search)
python main.py --mode full
```

## File Locations

| What | Where |
|------|-------|
| Your papers | `data/user_papers/*.pdf` |
| Cached profile | `cache/profile.json` |
| Logs | `academic_radar.log` |
| Config | `.env` |
| Results | Email inbox |

## Required Secrets (GitHub Actions)

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `OPENALEX_EMAIL`
- `SMTP_USER`
- `SMTP_PASS`
- `RECIPIENT_EMAIL`

## Key Configuration (.env)

```env
# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7

# Search
SEARCH_DAYS_BACK=7
MAX_PAPERS_TO_ANALYZE=5

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASS=app_password
RECIPIENT_EMAIL=you@email.com
```

## Workflow Overview

1. **Profile** (once): `python main.py --mode profile`
2. **Search** (weekly): Automated by GitHub Actions
3. **Receive**: Email with discoveries
4. **Read**: Papers with high borrowability scores
5. **Apply**: Adapt methods to your work

## Troubleshooting Quick Checks

```bash
# Check setup
python setup.py

# View logs
tail -f academic_radar.log

# Test LLM
python -c "from src.tools.llm_factory import LLMFactory; LLMFactory.create_chat_model()"

# Verify profile
cat cache/profile.json
```

## Common Issues

| Issue | Fix |
|-------|-----|
| No papers found | Increase `SEARCH_DAYS_BACK` to 14 or 30 |
| LLM errors | Check API key, try different model |
| Email fails | Use Gmail App Password |
| PDF errors | Ensure PDFs are text-based, not scanned |
| Import errors | Run `pip install -r requirements.txt` |

## Gmail App Password Setup

1. Enable 2FA: [Google Account Security](https://myaccount.google.com/security)
2. Generate App Password: [App Passwords](https://myaccount.google.com/apppasswords)
3. Use in `.env` as `SMTP_PASS`

## Understanding Results

### Borrowability Scores

- **0.9-1.0**: 🟢 Nearly plug-and-play
- **0.7-0.9**: 🟡 Moderate adaptation needed
- **0.5-0.7**: 🟠 Interesting but requires rethinking
- **<0.5**: ❌ Rejected (not shown)

### Email Format

Each paper shows:
1. **Title & Field** - What domain it's from
2. **Score** - How applicable it is
3. **Isomorphic Connection** - Why it matters
4. **Methodology** - What technique it uses
5. **How to Apply** - Practical advice

## Agent Architecture

```
Profiler → Abstractor → Scout → Analyst → Publisher
   ↓           ↓          ↓         ↓         ↓
Profile    Queries    Papers   Scored    Email
```

## Customization Points

| What | Where |
|------|-------|
| Prompts | `src/core/prompts.py` |
| Search logic | `src/agents/scout.py` |
| Scoring | `src/agents/analyst.py` |
| Email template | `src/core/prompts.py` |
| LLM settings | `.env` |

## Resources

- **Full Documentation**: `docs/USAGE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Contributing**: `CONTRIBUTING.md`
- **Example Profile**: `docs/example_profile.md`

## Getting Help

1. Check logs: `academic_radar.log`
2. Run setup: `python setup.py`
3. Read docs: `docs/TROUBLESHOOTING.md`
4. Open issue: GitHub Issues

## Pro Tips

✅ **Use 3-5 recent papers** for best profile quality  
✅ **Start with 7-day searches**, increase if needed  
✅ **Review profile.json** - you can edit it manually  
✅ **Check generated queries** - they should make sense  
✅ **Read "practical application"** advice critically  
✅ **Re-profile every 6-12 months** as research evolves  

## Quick Test

```bash
# Full test run
python setup.py && \
python main.py --mode profile && \
python main.py --mode search --skip-email && \
echo "✅ All tests passed!"
```

---

**Need more detail? See `docs/USAGE.md`**  
**Having issues? See `docs/TROUBLESHOOTING.md`**

**Happy discovering! 🚀**
