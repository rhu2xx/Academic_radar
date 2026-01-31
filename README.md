# 🎯 Academic Radar: Your Research Scout for the Unknown Unknowns.

As researchers, we often get stuck in our own bubbles. We read the same journals, cite the same authors, and solve problems the same way everyone else in our field does. But often, the solution to your hardest problem has already been solved—just in a field you never check.

**Academic Radar** is an AI tool built to bridge that gap. It doesn't just look for what you study; it looks for how you study it.

**The "Isomorphic" Magic**: Let's say you are building a model to predict Stock Market Trends. You are stuck because the data is too noisy. Academic Radar analyzes your problem and realizes that mathematically, your "noisy stock data" looks exactly like "erratic heart signals" in Cardiology. It then recommends a medical paper on ECG Signal Denoising. Even though the paper is about hearts, the math is exactly what you need for stocks.

That is Isomorphic Search: Finding the same mathematical shape in a different domain.

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
git clone git@github.com:rhu2xx/Academic_radar.git
cd Academic_radar
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

<details>
<summary><b>📖 How to Get API Keys</b></summary>

#### 🤖 DeepSeek API Key (Recommended - Cheapest)

1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up and verify your email
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `sk-...`)
6. **Cost:** ~$0.14 per million tokens (cheapest option)

#### 🔍 OpenAlex Email (Required for Fast Access)

1. Use any valid email address
2. Add to `.env`: `OPENALEX_EMAIL=your@email.com`
3. This gives you **10x faster API access** (100 req/sec vs 10 req/sec)
4. **Optional:** Get premium API key at [openalex.org/account](https://openalex.org/account) for 1M daily requests

#### 📧 Gmail SMTP Password (For Email Notifications)

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Enable **2-Step Verification** (required)
3. Search for **App Passwords** in settings
4. Select **Mail** and your device
5. Click **Generate** - copy the 16-character password
6. Use this password in `.env` (NOT your regular Gmail password)

**Troubleshooting:**
- If you don't see "App Passwords", enable 2FA first
- Gmail blocks regular passwords for security

#### Alternative LLM Providers

**OpenAI (More Expensive):**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create account and add payment method
3. Click **Create new secret key**
4. Set `.env`: `LLM_PROVIDER=openai` and `OPENAI_API_KEY=sk-...`
5. **Cost:** ~$10 per million tokens

**Anthropic Claude:**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up and verify
3. Navigate to **API Keys**
4. Set `.env`: `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=sk-...`
5. **Cost:** ~$15 per million tokens

</details>

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

## 🤖 Automate with GitHub Actions

Get weekly paper discoveries delivered automatically - no manual running required!

### Prerequisites

- ✅ Completed steps 1-3 above (installed, configured, created profile)
- ✅ GitHub account with this repository

### Setup Instructions

#### Step 1: Prepare Your Repository

```bash
# 1. Make sure your profile is ready
python main.py --mode profile

# 2. Commit essential files
git add cache/profile.json
git add .github/workflows/weekly_radar.yml
git commit -m "Setup automated radar workflow"
git push
```

#### Step 2: Add GitHub Secrets

Go to your repository on GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets one by one:

| Secret Name | Value | Example | Required |
|-------------|-------|---------|----------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | `sk-abc123...` | ✅ Yes |
| `OPENALEX_EMAIL` | Your email for OpenAlex | `you@email.com` | ✅ Yes |
| `SMTP_USER` | Your Gmail address | `you@gmail.com` | ✅ Yes |
| `SMTP_PASS` | Gmail app password (16 chars) | `abcd efgh ijkl mnop` | ✅ Yes |
| `RECIPIENT_EMAIL` | Where to send reports | `you@email.com` | ✅ Yes |

<details>
<summary><b>💡 How to Add Secrets (Click to expand)</b></summary>

1. Click **"New repository secret"**
2. Enter **Name** (e.g., `DEEPSEEK_API_KEY`)
3. Enter **Secret** (paste your API key)
4. Click **"Add secret"**
5. Repeat for all 5 secrets

**Screenshot Guide:**
```
Repository → Settings → Secrets and variables → Actions
                                                    ↓
                                    [New repository secret] button
```

</details>

#### Step 3: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see **"Weekly Academic Radar Scan"** workflow

#### Step 4: Test the Workflow

**Manual test run:**

1. Go to **Actions** tab
2. Click **"Weekly Academic Radar Scan"**
3. Click **"Run workflow"** dropdown (right side)
4. Select `mode: search`
5. Click green **"Run workflow"** button

**Wait 2-3 minutes**, then:
- ✅ Check workflow status (should show green ✓)
- ✅ Check your email inbox
- ✅ Check repository - `cache/sent_papers.json` should be updated

#### Step 5: Verify Automation

The workflow runs **automatically every Monday at 9:00 AM UTC**.

You can also run it manually anytime from the Actions tab.



### 📅 Customizing Schedule

Edit `.github/workflows/weekly_radar.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

**Common schedules:**
- `'0 9 * * 1'` - Every Monday 9 AM
- `'0 9 * * 1,4'` - Monday and Thursday 9 AM  
- `'0 9 1,15 * *'` - 1st and 15th of month 9 AM
- `'0 9 * * *'` - Every day 9 AM

**Convert to your timezone:**
- UTC 9 AM = PST 1 AM = EST 4 AM = CST 3 PM = JST 6 PM

---

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
