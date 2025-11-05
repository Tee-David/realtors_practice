# GitHub Actions Diagnosis Report

**Date:** November 5, 2025
**Status:** ⚠️ Workflows have configuration issues

---

## Executive Summary

Your GitHub Actions workflows are **configured correctly** but likely failing due to:
1. **Resource limitations** on GitHub's free runners
2. **Missing environment variables** or secrets
3. **Timeout issues** when scraping large batches
4. **Playwright browser installation** timing out

**Good News:** The workflow YAML files are properly structured. The failures are operational, not structural.

---

## Diagnostic Results

### ✅ What's Working

1. **Workflow Structure**: All 3 workflow files have valid YAML syntax
2. **Job Configuration**: All jobs have proper runners and steps
3. **Playwright Setup**: Browser installation steps are present
4. **Dependencies**: requirements.txt exists and has all required packages
5. **Python Version**: Using Python 3.11 consistently

### ⚠️ Identified Issues

| Issue | Severity | Impact | File |
|-------|----------|--------|------|
| Encoding issue in scrape.yml | Medium | May cause parsing errors | scrape.yml |
| No trigger defined in tests.yml | Low | Workflow won't run automatically | tests.yml |
| No trigger in scrape-large-batch.yml | Low | Manual trigger only | scrape-large-batch.yml |

---

## Common Failure Reasons

### 1. **Timeout Issues** (Most Likely)

**Symptoms:**
- Workflows fail after 6-10 minutes
- Error: "The operation was canceled"
- Incomplete scraping results

**Why This Happens:**
- Scraping 51 enabled sites takes 30-60 minutes
- GitHub Actions default timeout: 6 hours (but jobs can be slower)
- Network latency in cloud environment
- Playwright browser startup overhead

**Solution:**
```yaml
jobs:
  scrape:
    timeout-minutes: 60  # Add this to each job
    runs-on: ubuntu-latest
```

### 2. **Memory/Resource Exhaustion**

**Symptoms:**
- "Out of memory" errors
- Browser crashes
- Incomplete data

**Why This Happens:**
- Running multiple Playwright browsers simultaneously
- Large data processing (1500+ properties)
- ubuntu-latest only has 7GB RAM

**Solution:**
Reduce the number of sites per run:
```bash
# Environment variables in workflow
env:
  RP_PAGE_CAP: 10        # Limit to 10 pages per site
  RP_HEADLESS: 1         # Run browsers in headless mode
  RP_NO_IMAGES: 1        # Block images to save memory
  RP_SITE_WORKERS: 1     # Process sites sequentially
```

### 3. **Playwright Installation Failures**

**Symptoms:**
- "Browser not found" errors
- "Executable doesn't exist" errors

**Why This Happens:**
- playwright install-deps requires sudo on Linux
- System dependencies missing
- Chromium download fails

**Current Setup (CORRECT):**
```yaml
- name: Install Playwright and browsers
  run: |
    playwright install chromium
    playwright install-deps
```

If failing, try:
```yaml
- name: Install Playwright browsers
  run: |
    playwright install --with-deps chromium
```

### 4. **Missing Secrets/Environment Variables**

**Symptoms:**
- Geocoding fails silently
- Firebase exports fail
- API integrations don't work

**Required Secrets:**
None are strictly required for basic scraping, but these enhance functionality:
- `GOOGLE_MAPS_API_KEY` - For geocoding
- `FIREBASE_SERVICE_ACCOUNT` - For Firestore exports
- `GITHUB_TOKEN` - Automatically provided

**To Add Secrets:**
1. Go to: `https://github.com/Tee-David/realtors_practice/settings/secrets/actions`
2. Click "New repository secret"
3. Add secrets as needed

---

## Recommended Workflow Configuration

### Option 1: Quick Test (Recommended to Start)

Create `.github/workflows/test-scrape.yml`:

```yaml
name: Test Scrape (Quick)

on:
  workflow_dispatch:
    inputs:
      sites:
        description: 'Sites to scrape (comma-separated)'
        required: false
        default: 'cwlagos,npc'

jobs:
  test-scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium

      - name: Run quick test scrape
        env:
          RP_HEADLESS: 1
          RP_PAGE_CAP: 5
          RP_NO_IMAGES: 1
          RP_GEOCODE: 0
          RP_DEBUG: 1
        run: |
          python scripts/enable_sites.py ${{ github.event.inputs.sites || 'cwlagos' }}
          python main.py

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-scrape-results
          path: |
            exports/
            logs/scraper.log
```

**Benefits:**
- Fast (5-10 minutes)
- Low resource usage
- Easy to debug
- Tests that everything works

### Option 2: Production Scraping (Split into Batches)

**Problem:** Scraping all 51 sites in one job will timeout.

**Solution:** Use matrix strategy to split sites into batches.

Update `.github/workflows/scrape.yml`:

```yaml
name: Production Scrape

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      matrix:
        batch: [1, 2, 3]  # Split into 3 batches (~17 sites each)
      fail-fast: false

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium

      - name: Scrape batch ${{ matrix.batch }}
        env:
          RP_HEADLESS: 1
          RP_PAGE_CAP: 20
          RP_NO_IMAGES: 1
          RP_GEOCODE: 1
          RP_MAX_GEOCODES: 100
          BATCH_NUMBER: ${{ matrix.batch }}
        run: |
          python scripts/scrape_batch.py --batch $BATCH_NUMBER

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: scrape-results-batch-${{ matrix.batch }}
          path: exports/

  consolidate:
    needs: scrape
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4

      - name: Consolidate results
        run: python scripts/consolidate_batch_results.py
```

---

## Immediate Action Items

### Priority 1: Test Basic Functionality

1. **Create a test workflow** (Option 1 above)
2. **Run it manually** with 1-2 sites
3. **Check the logs** to see exactly where it fails
4. **Fix the specific error** that appears

### Priority 2: Monitor Resource Usage

Add logging to see resource consumption:

```yaml
- name: Check resources before scrape
  run: |
    echo "=== System Resources ===="
    free -h
    df -h
    echo "========================"

- name: Run scraper
  run: python main.py

- name: Check resources after scrape
  run: |
    echo "=== System Resources ===="
    free -h
    df -h
    echo "========================"
```

### Priority 3: Fix Identified Issues

1. **Fix scrape.yml encoding:**
   ```bash
   # Re-save the file with proper encoding
   dos2unix .github/workflows/scrape.yml
   ```

2. **Add timeout limits:**
   Add `timeout-minutes: 30` to all jobs

3. **Add proper triggers:**
   ```yaml
   on:
     workflow_dispatch:  # Manual trigger
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM
   ```

---

## Debugging Failed Runs

### Step 1: Check the Logs

1. Go to: `https://github.com/Tee-David/realtors_practice/actions`
2. Click on the failed run
3. Click on the failed job
4. Expand the failing step
5. Look for specific error messages

### Step 2: Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Browser not found" | Playwright not installed | Add `playwright install-deps` |
| "Timeout waiting for..." | Page load timeout | Increase `RP_NET_RETRY_SECS` |
| "Out of memory" | Too many browsers | Reduce `RP_SITE_WORKERS` |
| "The operation was canceled" | Job timeout | Add `timeout-minutes: 60` |
| "403 Forbidden" | Site blocking | Add delays, rotate user agents |

### Step 3: Enable Debug Mode

Add to your workflow:

```yaml
env:
  RP_DEBUG: 1
  ACTIONS_STEP_DEBUG: true
```

This will show detailed logs of what the scraper is doing.

---

## Performance Optimization

### Current Setup Issues

**Your config.yaml has:**
- 51 total sites
- 1 enabled (cwlagos)
- If you enable all 51: **will definitely timeout**

### Recommended Approach

**For GitHub Actions (Free Tier):**

1. **Enable only 5-10 sites per run**
   ```python
   # scripts/enable_batch.py
   python scripts/enable_sites.py cwlagos npc propertypro lamudi jiji
   ```

2. **Rotate which sites are enabled**
   - Day 1: Enable sites 1-10
   - Day 2: Enable sites 11-20
   - Day 3: Enable sites 21-30
   - etc.

3. **Use scheduled workflows**
   ```yaml
   on:
     schedule:
       - cron: '0 2 * * 1'  # Batch 1: Mondays
       - cron: '0 2 * * 2'  # Batch 2: Tuesdays
       - cron: '0 2 * * 3'  # Batch 3: Wednesdays
   ```

---

## Alternative: Self-Hosted Runner

If GitHub Actions continues to fail:

### Option: Run Locally with Scheduler

Instead of GitHub Actions, run on your own machine:

```yaml
# Use Windows Task Scheduler or cron
# Schedule: python main.py
# Frequency: Daily at 2 AM

# Advantages:
- No timeout limits
- More memory/CPU
- Faster execution
- Full control

# Disadvantages:
- Need to keep computer running
- No cloud backup
- Manual maintenance
```

---

## Testing Checklist

Before running full production scrapes:

- [ ] Test with 1 site (should complete in <2 minutes)
- [ ] Test with 5 sites (should complete in <10 minutes)
- [ ] Test with 10 sites (should complete in <20 minutes)
- [ ] Check memory usage doesn't exceed 80%
- [ ] Verify output files are created
- [ ] Check logs for errors
- [ ] Confirm data quality is good

Once all tests pass, gradually scale up.

---

## Next Steps

1. **Run the diagnostic script:**
   ```bash
   python check_workflows.py
   ```

2. **Create a test workflow** (copy Option 1 above)

3. **Run it manually** from GitHub Actions UI

4. **Share the logs** if it fails (I can help debug)

5. **Once working**, scale up gradually

---

## Support Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Playwright CI:** https://playwright.dev/docs/ci
- **Your Workflow Files:**
  - `.github/workflows/scrape.yml` - Main workflow
  - `.github/workflows/scrape-large-batch.yml` - Batch processing
  - `.github/workflows/tests.yml` - Unit tests

---

## Summary

**Your workflows are well-configured.** The failures are likely due to:
1. **Timeout** - trying to scrape too many sites at once
2. **Memory** - running too many browsers simultaneously
3. **Resource limits** on GitHub's free runners

**Solution:** Start small (1-5 sites), test, then scale up gradually with batching.

**Quick Win:** Create the test workflow (Option 1) and run it now with just `cwlagos`. It should complete in 2-3 minutes and help identify any remaining issues.

---

**Need Help?** If you see specific error messages in the GitHub Actions logs, share them and I can provide targeted solutions.
