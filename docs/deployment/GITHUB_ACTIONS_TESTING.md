# GitHub Actions Testing Guide

**Complete guide to test and verify the scraper deployment on GitHub Actions**

---

## 📋 Table of Contents

1. [Pre-Testing Checklist](#pre-testing-checklist)
2. [Testing Methods](#testing-methods)
3. [Verification Steps](#verification-steps)
4. [Troubleshooting](#troubleshooting)
5. [Monitoring](#monitoring)

---

## Pre-Testing Checklist

Before testing, ensure:

- [ ] Code pushed to GitHub repository
- [ ] Workflow file exists at `.github/workflows/scrape.yml`
- [ ] `config.yaml` or `config.example.yaml` exists
- [ ] At least one site is enabled in config
- [ ] GitHub Actions is enabled for the repository

**Enable GitHub Actions**:
1. Go to your GitHub repository
2. Click **Settings** → **Actions** → **General**
3. Under "Actions permissions", select **Allow all actions and reusable workflows**
4. Click **Save**

---

## Testing Methods

### Method 1: Manual Trigger (Recommended for First Test)

**Best for**: Initial testing, controlled testing

**Steps**:

1. **Go to Actions Tab**
   - Navigate to `https://github.com/Tee-David/realtors_practice/actions`
   - Or click "Actions" tab in your repo

2. **Select Workflow**
   - Click "Nigerian Real Estate Scraper" on the left sidebar
   - You should see the workflow details

3. **Run Workflow**
   - Click **"Run workflow"** button (top right)
   - A form appears with options:
     - **Branch**: `main` (or your default branch)
     - **Max pages per site**: `5` (start small for testing)
     - **Enable geocoding**: `1` (or `0` to disable)
     - **Specific sites**: Leave empty (uses config.yaml enabled sites)
   - Click green **"Run workflow"** button

4. **Wait for Workflow to Start**
   - Refresh the page after ~5-10 seconds
   - You should see a new workflow run appear with status "Queued" or "In progress"

**Expected Duration**: 5-15 minutes for first run (includes setup time)

---

### Method 2: Repository Dispatch (Frontend Trigger)

**Best for**: Testing frontend integration

**Prerequisites**:
- GitHub Personal Access Token (PAT) with `repo` scope
- Token stored securely

**Using cURL**:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -d '{"event_type":"trigger-scrape","client_payload":{"page_cap":5,"geocode":1}}'
```

**Success Response**:
- HTTP 204 (No Content)
- No response body
- Workflow should appear in Actions tab within 10-30 seconds

**Using Postman**:
1. **Method**: POST
2. **URL**: `https://api.github.com/repos/Tee-David/realtors_practice/dispatches`
3. **Headers**:
   ```
   Accept: application/vnd.github+json
   Authorization: Bearer YOUR_GITHUB_TOKEN
   X-GitHub-Api-Version: 2022-11-28
   ```
4. **Body** (raw JSON):
   ```json
   {
     "event_type": "trigger-scrape",
     "client_payload": {
       "page_cap": 5,
       "geocode": 1
     }
   }
   ```
5. **Send** → Should get 204 response

---

### Method 3: Scheduled Run

**Best for**: Production automation

**Note**: Scheduled runs trigger automatically at 3 AM UTC daily.

**To test scheduled trigger**:
1. Wait until 3:00 AM UTC
2. Check Actions tab at ~3:05 AM UTC
3. Verify workflow ran automatically

**Time Zones**:
- 3 AM UTC = 4 AM WAT (West Africa Time, during standard time)
- 3 AM UTC = 3 AM GMT (during standard time)

**Temporarily Change Schedule** (for testing):

Edit `.github/workflows/scrape.yml`:
```yaml
schedule:
  # Run every hour (for testing)
  - cron: '0 * * * *'

  # Or run every 15 minutes (aggressive testing)
  - cron: '*/15 * * * *'
```

**Remember**: Change it back after testing!

---

## Verification Steps

### Step 1: Check Workflow Started

1. Go to **Actions** tab
2. You should see a new run:
   - ✅ Status: "Queued" or "In progress" (yellow dot)
   - ✅ Workflow name: "Nigerian Real Estate Scraper"
   - ✅ Trigger: "workflow_dispatch" (manual) or "repository_dispatch" (API)

**If not appearing**:
- Wait 30-60 seconds and refresh
- Check workflow file syntax (`.github/workflows/scrape.yml`)
- Verify GitHub Actions is enabled

---

### Step 2: Monitor Workflow Execution

**Click on the workflow run** to see details.

**Expected Steps** (in order):

1. ✅ **Set up job** (~10 seconds)
   - Prepares runner environment

2. ✅ **📥 Checkout code** (~5 seconds)
   - Downloads your repository code

3. ✅ **🐍 Set up Python 3.11** (~10 seconds)
   - Installs Python 3.11

4. ✅ **📦 Install Python dependencies** (~30-60 seconds)
   - Installs packages from requirements.txt
   - Should show: `pip install -r requirements.txt`

5. ✅ **🎭 Install Playwright and browsers** (~45-90 seconds)
   - Installs Playwright and Chromium browser
   - This is the slowest setup step

6. ✅ **⚙️ Configure scraper** (~2 seconds)
   - Prepares config.yaml

7. ✅ **🚀 Run scraper** (~3-10 minutes, depends on page_cap)
   - Main scraping happens here
   - Should show log output from main.py
   - Check for "Scraping site: ..." messages

8. ✅ **🧹 Process exports with watcher** (~5-15 seconds)
   - Runs watcher.py to clean data
   - Generates master workbook

9. ✅ **📝 Generate summary** (~5 seconds)
   - Creates workflow summary

10. ✅ **📤 Upload artifacts** (~10-30 seconds each)
    - Uploads raw exports
    - Uploads cleaned data
    - Uploads logs

11. ✅ **Post steps** (~5 seconds)
    - Cleanup tasks

**Total Expected Time**:
- **First run**: 8-15 minutes (includes setup)
- **Subsequent runs**: 5-12 minutes (cached dependencies)

---

### Step 3: Check Logs

Click on each step to see detailed logs:

**✅ What to look for in "🚀 Run scraper" logs**:

```
🔧 Configuration:
  - Page cap: 5
  - Geocoding: 1
  - Headless: 1

🏃 Starting scraper...
Starting scraper...
Loaded configuration for 50 sites
Enabled sites: ['npc', 'propertypro', 'jiji']
Scraping npc...
  Page 1/5 - Found 20 listings
  Page 2/5 - Found 18 listings
  ...
Scraped npc: 90 listings
Exporting to CSV...
Exporting to XLSX...
✅ Scraping complete!
```

**❌ Common issues in logs**:
- `playwright: command not found` → Playwright installation failed
- `ModuleNotFoundError` → Dependency installation incomplete
- `No sites enabled` → Check config.yaml
- `TimeoutError` → Site not responding (expected occasionally)

---

### Step 4: Download Artifacts

After workflow completes:

1. **Scroll to bottom** of workflow run page
2. **Artifacts section** appears:
   - `scraper-exports-raw-123` → Raw CSV/XLSX files
   - `scraper-exports-cleaned-123` → Cleaned data + master workbook
   - `scraper-logs-123` → Logs

3. **Click artifact name** to download (ZIP file)

4. **Extract and verify**:
   ```
   scraper-exports-cleaned-123/
   ├── MASTER_CLEANED_WORKBOOK.xlsx  ← Main output
   ├── metadata.json                  ← Scraping metadata
   └── npc/
       ├── npc_cleaned.csv
       └── npc_cleaned.parquet
   ```

**✅ Success Criteria**:
- `MASTER_CLEANED_WORKBOOK.xlsx` exists
- File size > 10 KB
- Contains sheets for each scraped site
- Listings have data (title, price, location)

---

### Step 5: Check Workflow Summary

After workflow completes:

1. Click on **Summary** (in left sidebar of workflow run)
2. Verify summary shows:
   - Sites scraped count
   - Files generated count
   - Cleaned files count
   - Master workbook status

**Example Summary**:
```
📊 Scrape Summary

### Raw Exports
- Sites scraped: 3
- Files generated: 6

### Cleaned Data
- Cleaned files: 8
- Master workbook: ✅ (250 KB)

### Recent Errors
No errors found ✅

Workflow: #123
Triggered by: workflow_dispatch
Date: 2025-10-18 14:30:00 UTC
```

---

## Troubleshooting

### Issue 1: Workflow Not Starting

**Symptoms**:
- No workflow run appears in Actions tab
- GitHub shows no activity

**Solutions**:

1. **Check GitHub Actions is enabled**:
   ```
   Settings → Actions → General → Allow all actions
   ```

2. **Verify workflow file syntax**:
   ```bash
   # Locally, install actionlint
   brew install actionlint  # Mac
   # OR
   go install github.com/rhysd/actionlint/cmd/actionlint@latest

   # Check workflow syntax
   actionlint .github/workflows/scrape.yml
   ```

3. **Check branch**:
   - Workflow must be on default branch (main/master)
   - Check branch in workflow trigger settings

---

### Issue 2: Playwright Installation Fails

**Symptoms**:
```
Error: browserType.launch: Executable doesn't exist
```

**Solutions**:

**Option A**: Use requests-only mode (edit config.yaml):
```yaml
global_settings:
  scraper:
    fallback_chain: ["requests"]  # Skip Playwright
```

**Option B**: Install system dependencies (edit workflow):
```yaml
- name: Install Playwright deps
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
      libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
      libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
    playwright install chromium
```

---

### Issue 3: Scraper Returns Zero Listings

**Symptoms**:
- Workflow completes successfully
- But artifacts show 0 listings

**Solutions**:

1. **Check enabled sites**:
   ```bash
   # Verify config.yaml has enabled: true
   cat config.yaml | grep -A 2 "site_key:"
   ```

2. **Increase page cap** (may need more pages):
   ```yaml
   # Re-run with:
   page_cap: 20  # Instead of 5
   ```

3. **Enable debug logging**:
   Edit workflow `.github/workflows/scrape.yml`:
   ```yaml
   env:
     RP_DEBUG: 1  # Enable debug mode
   ```

4. **Check site logs** in artifact:
   ```
   logs/scraper.log
   # Look for site-specific errors
   ```

---

### Issue 4: Timeout (Workflow Exceeds 60 Minutes)

**Symptoms**:
- Workflow cancelled after 60 minutes
- Last step: "🚀 Run scraper" (incomplete)

**Solutions**:

1. **Reduce enabled sites**:
   ```yaml
   # In config.yaml, enable only 3-5 sites
   ```

2. **Reduce page cap**:
   ```
   page_cap: 10  # Instead of 20 or 30
   ```

3. **Disable geocoding** (faster):
   ```
   geocode: 0
   ```

4. **Increase timeout** (max 6 hours):
   ```yaml
   # In .github/workflows/scrape.yml
   jobs:
     scrape:
       timeout-minutes: 180  # 3 hours
   ```

---

### Issue 5: Artifacts Not Uploading

**Symptoms**:
- Workflow shows: "No files found"
- Artifacts section empty

**Solutions**:

1. **Check exports directory exists**:
   Add debug step to workflow:
   ```yaml
   - name: Debug - List exports
     run: |
       echo "Contents of exports/"
       ls -R exports/ || echo "exports/ not found"
   ```

2. **Verify scraper ran**:
   - Check "🚀 Run scraper" step completed
   - Look for "Exported X listings" in logs

---

## Monitoring

### Daily Monitoring Checklist

**Every day** (or after each scheduled run):

1. ☑️ **Check workflow ran**:
   - Go to Actions tab
   - Verify run from scheduled trigger
   - Status should be ✅ (green checkmark)

2. ☑️ **Check for errors**:
   - Click on workflow run
   - Look for red ❌ steps
   - Read error messages in logs

3. ☑️ **Download latest artifacts**:
   - Download `scraper-exports-cleaned-XXX`
   - Verify data quality
   - Check listing counts

4. ☑️ **Review summary**:
   - Check sites scraped count
   - Verify master workbook generated
   - Note any warnings

---

### Weekly Monitoring Tasks

**Every week**:

1. 📊 **Review trends**:
   - Compare listing counts week-over-week
   - Identify sites with declining data
   - Adjust configs as needed

2. 🔍 **Artifact cleanup** (optional):
   - GitHub retains artifacts for 30 days
   - Download important runs before expiration
   - No action needed unless storage is limited

3. 🔄 **Update selectors** (if needed):
   - If sites change structure
   - Update `config.yaml` selectors
   - Test with manual workflow run

---

### Setting Up Notifications

**Get alerted when workflow fails**:

**Option 1: GitHub Email Notifications** (built-in):
1. GitHub Settings → Notifications
2. Enable "Actions" notifications
3. Receive email on workflow failure

**Option 2: Slack Webhook** (advanced):
Add to workflow:
```yaml
- name: Notify Slack on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"❌ Scraper workflow failed! Check: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
```

---

## Success Metrics

**Your GitHub Actions deployment is successful if**:

- ✅ Workflow runs without errors
- ✅ Completes in <15 minutes
- ✅ Generates artifacts (cleaned data + logs)
- ✅ Master workbook has listings (>0 records)
- ✅ Scheduled runs trigger automatically
- ✅ Frontend can trigger via repository_dispatch
- ✅ Can download and use exported data

---

## Quick Test Commands

```bash
# 1. Verify workflow file syntax (local)
cat .github/workflows/scrape.yml

# 2. Trigger workflow via API
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -d '{"event_type":"trigger-scrape","client_payload":{"page_cap":5}}'

# 3. Check latest workflow run
gh run list --limit 1  # Requires GitHub CLI

# 4. Download latest artifact
gh run download  # Requires GitHub CLI
```

---

## Next Steps After Successful Test

1. ✅ **Adjust configuration**:
   - Increase `page_cap` to desired value (e.g., 20-30)
   - Enable more sites as needed
   - Configure geocoding preferences

2. ✅ **Set up frontend**:
   - Implement repository_dispatch trigger
   - Create UI for triggering scrapes
   - Display workflow status

3. ✅ **Monitor production**:
   - Check daily scheduled runs
   - Download artifacts regularly
   - Adjust selectors when sites change

4. ✅ **Optimize**:
   - Fine-tune page caps per site
   - Adjust timeout based on actual runtime
   - Enable/disable geocoding based on needs

---

## Contact & Support

**Issues**:
- GitHub Issues: Create issue in repository
- Check workflow logs for detailed errors

**Documentation**:
- `FREE_DEPLOYMENT.md` - Deployment guide
- `README.md` - Project overview
- `docs/guides/FRONTEND_INTEGRATION.md` - Frontend integration

---

**Last Updated**: 2025-10-18
**Status**: Ready for Testing ✅
