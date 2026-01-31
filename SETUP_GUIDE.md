# 🚀 GitHub Workflow Setup Guide

Complete guide to automate Academic Radar on GitHub Actions.

---

## 📋 Prerequisites

- GitHub account
- DeepSeek API key (or OpenAI/Anthropic)
- Gmail account with 2FA enabled
- Your research papers (PDFs)

---

## 🎯 Step-by-Step Setup

### Step 1: Clone and Prepare

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/academic-radar.git
cd academic-radar

# Create virtual environment (for local testing)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Create Your Research Profile (Local)

```bash
# 1. Add your papers
mkdir -p data/user_papers
cp /path/to/your/papers/*.pdf data/user_papers/

# 2. Create .env file
cp .env.example .env
nano .env  # Edit with your API keys

# 3. Generate profile
python main.py --mode profile

# 4. Verify profile was created
ls cache/profile.json
```

**Expected output:**
```
✅ cache/profile.json created
Contains: core_task, pain_points, methodologies, etc.
```

### Step 3: Test Locally (Optional but Recommended)

```bash
# Test search without sending email
python main.py --mode search --skip-email

# If successful, test full pipeline
python main.py --mode search
```

**Check:** You should receive an email with paper recommendations.

### Step 4: Get Required API Keys

#### 🤖 DeepSeek API Key

1. Visit [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up / Login
3. Click **API Keys** in left sidebar
4. Click **Create API Key**
5. Copy the key (starts with `sk-...`)
6. Save it somewhere safe

#### 📧 Gmail App Password

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** → Enable **2-Step Verification** (required)
3. Search "App Passwords" in the search bar
4. Select **Mail** and your device
5. Click **Generate**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

**Important:** Use the app password in GitHub Secrets, NOT your regular Gmail password.

#### 🔍 OpenAlex Email (Optional but Recommended)

- Use any valid email (your Gmail works)
- Gives you 10x faster API access (100 req/sec vs 10 req/sec)
- No signup needed, just add to secrets

### Step 5: Configure GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Value | Example |
|------------|-------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek key | `sk-abc123...` |
| `OPENALEX_EMAIL` | Your email | `your@email.com` |
| `SMTP_USER` | Your Gmail address | `your@gmail.com` |
| `SMTP_PASS` | Gmail app password | `abcdefghijklmnop` |
| `RECIPIENT_EMAIL` | Where to send emails | `your@email.com` |

**Screenshot guide:**
```
Repository → Settings → Secrets and variables → Actions → New repository secret
┌─────────────────────────────────────┐
│ Name: DEEPSEEK_API_KEY             │
│ Secret: sk-abc123...                │
│ [Add secret]                        │
└─────────────────────────────────────┘
```

### Step 6: Commit Cache Files

```bash
# Make sure .gitignore is correct
cat .gitignore | grep -E "(cache|profile|sent_papers)"
# Should NOT see: cache/, *.json blocking profile/sent_papers

# Commit profile and tracking files
git add cache/profile.json
git add cache/sent_papers.json  # If exists, otherwise it will be created
git add .gitignore
git add .github/workflows/weekly_radar.yml

git commit -m "Setup: Add research profile and workflow configuration"
git push origin main
```

**Verify on GitHub:**
- Go to your repo → `cache/` folder
- You should see `profile.json` (and maybe `sent_papers.json`)

### Step 7: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. If you see "Workflows aren't being run on this repository"
   - Click **I understand my workflows, go ahead and enable them**
4. You should see "Weekly Academic Radar Scan" workflow

### Step 8: Test the Workflow

**Manual test run:**

1. Go to **Actions** tab
2. Click **Weekly Academic Radar Scan** in left sidebar
3. Click **Run workflow** dropdown (right side)
4. Select `search` mode
5. Click **Run workflow** button

**Monitor the run:**
- Watch the real-time logs
- Should take 2-5 minutes
- Look for ✅ green checkmark

**Expected log output:**
```
🎯 Starting Academic Radar in 'search' mode
🧬 Profiler: Loading cached profile
🎨 Abstractor: Generating 3 search queries
🔍 Scout: Searching OpenAlex...
🔬 Analyst: Analyzing papers...
📧 Publisher: Sending email...
✅ Cache files updated and committed
```

### Step 9: Verify Success

**Check 1: Email received**
- Open your inbox
- Look for "🎯 Academic Radar: X Discoveries This Week"

**Check 2: Cache updated**
- Go to repository → `cache/sent_papers.json`
- Click to view file
- Should see commit: "🤖 Update cache files [skip ci]"

**Check 3: Workflow runs automatically**
- The workflow is scheduled for **every Monday at 9:00 AM UTC**
- You don't need to do anything, just wait for emails!

---

## 🔧 Troubleshooting

### Issue 1: "No module named 'langgraph'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: "SMTP authentication failed"

**Causes:**
- Using regular Gmail password instead of app password
- 2FA not enabled on Gmail
- Wrong SMTP_USER or SMTP_PASS in secrets

**Solution:**
1. Enable 2FA on Gmail
2. Generate new app password
3. Update `SMTP_PASS` secret with the 16-char password

### Issue 3: "No cached profile found"

**Solution:**
```bash
# Create profile locally first
python main.py --mode profile

# Commit to repository
git add cache/profile.json
git commit -m "Add research profile"
git push
```

### Issue 4: "Workflow not running automatically"

**Check:**
1. Is the workflow file at `.github/workflows/weekly_radar.yml`?
2. Is the schedule correct? Check `cron: '0 9 * * 1'`
3. Are GitHub Actions enabled? (Actions tab)
4. Wait until next Monday 9:00 AM UTC

### Issue 5: "Permission denied" when pushing cache

**Solution:**
Check workflow has write permissions:
```yaml
permissions:
  contents: write
```

### Issue 6: Receiving duplicate papers

**This is already fixed!** The system tracks papers by both ID and title.

If you still get duplicates:
```bash
# Clear the cache and let it rebuild
rm cache/sent_papers.json
git add cache/sent_papers.json
git commit -m "Reset paper tracking"
git push
```

---

## 🎛️ Customization

### Change Search Frequency

Edit `.github/workflows/weekly_radar.yml`:

```yaml
# Every Monday at 9 AM UTC
cron: '0 9 * * 1'

# Every day at 9 AM UTC
cron: '0 9 * * *'

# Every Sunday and Wednesday at 9 AM UTC
cron: '0 9 * * 0,3'
```

### Change Search Parameters

Add these as GitHub Secrets (optional):

| Secret Name | Default | Description |
|------------|---------|-------------|
| `MAX_PAPERS_TO_ANALYZE` | 5 | Papers to analyze per run |
| `SEARCH_DAYS_BACK` | 7 | Days to look back |
| `MIN_BORROWABILITY_SCORE` | 0.5 | Minimum relevance (0-1) |
| `MAX_RESULTS_PER_QUERY` | 20 | Papers per query |

### Update Your Research Profile

```bash
# 1. Add new papers locally
cp new_paper.pdf data/user_papers/

# 2. Regenerate profile
python main.py --mode profile

# 3. Commit updated profile
git add cache/profile.json
git commit -m "Update research profile with new interests"
git push

# Next workflow run will use the new profile
```

---

## 📊 Monitoring

### View Workflow History

1. Go to **Actions** tab
2. See all past runs with status (✅ success / ❌ failed)
3. Click any run to see detailed logs

### Download Logs

1. Click on a workflow run
2. Scroll to **Artifacts** section at bottom
3. Download `radar-logs.zip`
4. Contains: `academic_radar.log`, `cache/profile.json`

### Check Paper Tracking

View `cache/sent_papers.json` in your repo:
```json
{
  "papers": {
    "W1234567890": "2026-01-27 09:15:23"
  },
  "titles": {
    "attention is all you need": "2026-01-27 09:15:23"
  }
}
```

---

## 🎉 Success Checklist

- [ ] Repository cloned
- [ ] Profile created locally (`cache/profile.json`)
- [ ] All 5 GitHub secrets added
- [ ] Cache files committed to repository
- [ ] GitHub Actions enabled
- [ ] Manual workflow test successful
- [ ] Email received with paper recommendations
- [ ] `cache/sent_papers.json` updated automatically
- [ ] Scheduled workflow will run every Monday

**You're all set!** 🚀 Academic Radar will now automatically send you cross-domain research discoveries every week.

---

## 🆘 Getting Help

1. Check workflow logs in Actions tab
2. Review `academic_radar.log` artifact
3. Verify all secrets are set correctly
4. Test locally first: `python main.py --mode search --skip-email`
5. Open an issue on GitHub with error logs

---

## 🔒 Security Notes

- **Never commit `.env` file** (contains API keys)
- **Never share GitHub Secrets** publicly
- **Use app passwords** for Gmail (never regular password)
- **`[skip ci]` in commits** prevents infinite workflow loops
- **Secrets are encrypted** by GitHub and not visible in logs

---

## 💡 Pro Tips

1. **Test locally first** before enabling automation
2. **Start with weekly runs** before increasing frequency
3. **Monitor costs** on DeepSeek dashboard (typically <$1/month)
4. **Update profile** when your research focus changes
5. **Check spam folder** if emails don't arrive
6. **Use filters** to organize Academic Radar emails

---

**Congratulations!** You now have a fully automated research discovery system. 🎓✨
