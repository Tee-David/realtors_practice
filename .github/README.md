# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the Nigerian Real Estate Scraper.

## Workflows

### `scrape.yml` - Main Scraper Workflow

**Purpose**: Automate property scraping from Nigerian real estate websites with quality filtering.

**Triggers**:
1. **Repository Dispatch** (`trigger-scrape`) - Triggered by frontend via GitHub API
2. **Manual** - Via GitHub Actions UI (workflow_dispatch)

**No Automatic Schedule**: You control when scraping runs (removed daily 3 AM schedule).

**Duration**: 5-15 minutes (depending on number of sites and pages)

**Outputs**:
- Raw CSV/XLSX exports (per site) - quality filtered
- Cleaned/normalized data
- Master consolidated workbook
- Scraping logs with quality metrics

**Artifacts Retention**: 30 days

---

### `tests.yml` - Automated Testing Workflow

**Purpose**: Run comprehensive test suite on code changes.

**Triggers**:
1. **Push to main** - When changes affect core/, tests/, api_server.py, or requirements.txt
2. **Pull requests** - On PR to main branch
3. **Manual** - Via GitHub Actions UI

**Duration**: ~2-5 minutes

**Tests Run**:
- Incremental scraping
- Duplicate detection
- Quality scoring (1-100%)
- Saved searches
- Scheduler logic
- Health monitoring
- Price history
- Natural language search

**Status**: 100/100 tests passing ✓

---

## Configuration

### Environment Variables (scrape.yml)

- `RP_PAGE_CAP` - Max pages to scrape per site (default: 20)
- `RP_GEOCODE` - Enable geocoding (1=yes, 0=no, default: 1)
- `RP_HEADLESS` - Run browser in headless mode (always 1 for GitHub Actions)
- `RP_NO_IMAGES` - Block images for faster scraping (always 1)
- `RP_DEBUG` - Enable debug logging (default: 0)
- `RP_MIN_QUALITY` - Minimum quality score for exports (default: 40)

### Manual Trigger Inputs (scrape.yml)

When triggering manually via GitHub Actions UI:

- **page_cap**: Number of pages to scrape per site (default: 20)
- **geocode**: Enable/disable geocoding (1 or 0, default: 1)
- **sites**: Comma-separated list of sites (leave empty for all enabled sites)

### Repository Dispatch Payload (API/Frontend)

When triggering via API (frontend integration):

```json
{
  "event_type": "trigger-scrape",
  "client_payload": {
    "page_cap": 20,
    "geocode": 1,
    "sites": ""
  }
}
```

---

## How to Trigger

### 1. Manual Trigger (GitHub UI)

1. Go to **Actions** tab in repository
2. Select **"Nigerian Real Estate Scraper"** workflow
3. Click **"Run workflow"**
4. Fill in parameters (or use defaults)
5. Click **"Run workflow"** button

### 2. API Trigger (Frontend)

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -d '{"event_type":"trigger-scrape","client_payload":{"page_cap":10}}'
```

### 3. Programmatic Control

**No automatic schedule** - You control when scraping runs via:
- GitHub Actions UI (manual trigger)
- Frontend trigger (repository_dispatch)
- API calls (via GitHub API)

---

## Quality Filtering (NEW)

**Automatic Data Quality Assurance**:
- All listings scored 0-100% based on completeness
- Default threshold: 40% (requires title, price, location, URL)
- Listings below threshold automatically rejected
- Quality stats included in logs

**Example Output**:
```
INFO - npc: Quality filter rejected 3/3 listings (below 40% threshold). Avg quality: 17.5%
INFO - cwlagos: All 44 listings passed quality filter (>= 40%). Avg quality: 76.9%
INFO - Exported 43 listings for cwlagos (avg quality: 77.2%)
```

**Configuration**:
- Global: `config.yaml` → `quality.min_quality_score: 40`
- Per-site: Add override in site config
- Environment: `RP_MIN_QUALITY=50`

---

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab
2. Select workflow from sidebar
3. Click on specific run to see details

### Download Artifacts

1. Go to completed workflow run
2. Scroll to **Artifacts** section at bottom
3. Click artifact name to download (ZIP file)

**Artifacts Available**:
- `scraper-exports-raw-{run}` (raw per-site data)
- `scraper-exports-cleaned-{run}` (cleaned + master workbook)
- `scraper-logs-{run}` (logs with quality metrics)

### Check Logs

1. Click on workflow run
2. Click on any step to expand logs
3. Look for:
   - Quality filtering stats
   - Sites with low quality scores
   - Errors (red X) or warnings

---

## Artifacts

Each successful run produces 3 artifacts:

1. **scraper-exports-raw-XXX** (30-day retention)
   - Contains raw CSV/XLSX files per site
   - Only high-quality listings (passed quality filter)
   - Directory structure: `exports/sites/{site}/`

2. **scraper-exports-cleaned-XXX** (30-day retention)
   - Contains cleaned/normalized data
   - Includes `MASTER_CLEANED_WORKBOOK.xlsx`
   - Deduplicated and quality-filtered
   - Directory structure: `exports/cleaned/`

3. **scraper-logs-XXX** (7-day retention)
   - Contains scraper.log with quality stats
   - Useful for identifying problematic sites
   - Shows which sites need selector improvements

---

## Workflow Steps (scrape.yml)

1. **Setup** (~2 minutes)
   - Checkout code
   - Set up Python 3.11
   - Install dependencies
   - Install Playwright browsers

2. **Scraping** (~3-10 minutes)
   - Configure scraper from config.yaml
   - Run main.py with parallel scraping
   - Apply quality filtering automatically
   - Scrape enabled sites only

3. **Processing** (~10-30 seconds)
   - Run watcher.py
   - Clean and normalize data
   - Generate master workbook
   - Track quality metrics

4. **Summary Generation**
   - Count exports (raw + cleaned)
   - List recent errors/warnings
   - Generate workflow summary

5. **Upload** (~30-60 seconds)
   - Upload raw exports (quality-filtered)
   - Upload cleaned data
   - Upload logs with quality stats

---

## Troubleshooting

### Workflow Not Starting

- Check GitHub Actions is enabled (Settings → Actions)
- Verify workflow file syntax
- Ensure on main/default branch
- Manual trigger only (no automatic schedule)

### Low Quality Exports (Many Rejected)

**Symptoms**: Logs show "Quality filter rejected X/Y listings"

**Solutions**:
1. Add site-specific selectors to config.yaml
2. Lower quality threshold for specific sites
3. Disable detail scraping for problematic sites
4. Check logs to identify missing fields

**Example Fix**:
```yaml
sites:
  npc:
    detail_selectors:
      price: [".price", ".listing-price"]
      location: [".location", ".address"]
      bedrooms: [".bedrooms"]
```

### Playwright Installation Fails

**Solution 1**: Use requests-only mode (faster, no browser)
```yaml
# Edit config.yaml
fallback_order:
  - requests
```

**Solution 2**: Install system dependencies
(Already handled in workflow)

### Scraper Returns 0 Listings

**Check**:
1. Enabled sites in config.yaml (51 sites, only 5 enabled by default)
2. Quality threshold (lower if needed: `quality.min_quality_score: 20`)
3. Page cap (increase for more results)
4. Site-specific issues in logs

**Debug**:
```yaml
# In workflow, set:
RP_DEBUG: 1
RP_MIN_QUALITY: 20  # More lenient
```

### Timeout (>60 minutes)

- Reduce number of enabled sites
- Decrease page_cap
- Disable geocoding (`RP_GEOCODE=0`)
- Increase timeout-minutes in workflow

---

## Cost & Limits

**GitHub Actions Free Tier**:
- 2,000 minutes/month for private repos
- Unlimited for public repos

**Estimated Usage**:
- ~10 minutes per manual run
- No automatic daily runs
- Fully under your control

**Artifact Storage**:
- 500 MB for free tier
- Artifacts auto-delete after retention period
- Raw exports (~5-10 MB per run)
- Cleaned data (~2-5 MB per run)

**Total Cost**: $0/month (within free tier limits)

---

## Security

### Secrets

Store sensitive data in GitHub Secrets:
- Settings → Secrets and variables → Actions
- Add secrets like `GITHUB_TOKEN` (auto-provided)
- Access in workflow: `${{ secrets.SECRET_NAME }}`

### Token Permissions

- Workflow uses `GITHUB_TOKEN` (auto-provided)
- Minimum permissions: `contents: read`
- For repository_dispatch: PAT with `repo` scope

---

## Customization

### Add Custom Schedule (Optional)

If you want automatic runs, edit `scrape.yml`:

```yaml
on:
  repository_dispatch:
    types: [trigger-scrape]
  workflow_dispatch:
    # ...
  schedule:  # ADD THIS
    # Every 12 hours
    - cron: '0 */12 * * *'

    # Weekly on Sundays
    # - cron: '0 3 * * 0'

    # Weekdays only at 3 AM
    # - cron: '0 3 * * 1-5'
```

### Adjust Quality Threshold

**Global (all sites)**:
```yaml
# config.yaml
quality:
  min_quality_score: 50  # Stricter (70 = high quality)
```

**Per-Site**:
```yaml
sites:
  propertypro:
    overrides:
      min_quality_score: 60  # Expect better data

  npc:
    overrides:
      min_quality_score: 30  # More lenient
```

### Add Notifications

```yaml
# Add to scrape.yml (after failure step)
- name: Send notification on failure
  if: failure()
  run: |
    echo "Scraper workflow failed!"
    echo "Check logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

### Increase Timeout

```yaml
jobs:
  scrape:
    timeout-minutes: 120  # 2 hours (max: 360 for free tier)
```

---

## Testing Workflow (tests.yml)

**Automatic Testing**:
- Runs on push to main (when core/tests/api changed)
- Runs on pull requests to main
- Can be triggered manually

**Test Coverage**:
- 8/8 improvement features
- 100/100 tests passing
- Comprehensive test suite

**Duration**: 2-5 minutes

---

## Features Summary

✅ **Manual Control** - No automatic daily runs
✅ **Quality Filtering** - Auto-reject incomplete listings
✅ **Parallel Scraping** - 2-worker concurrent execution
✅ **Smart Deduplication** - Cross-site duplicate detection
✅ **Health Monitoring** - Track site performance
✅ **Incremental Updates** - Only scrape changed listings
✅ **Comprehensive Logs** - Quality metrics included
✅ **Automated Testing** - 100% test coverage

---

## Documentation

- **Main README**: `../README.md`
- **Quality Filtering**: `../docs/QUALITY_FILTERING.md`
- **Implementation Complete**: `../IMPLEMENTATION_COMPLETE.md`
- **User Guide**: `../USER_GUIDE.md`
- **Deployment Guides**: `../docs/deployment/`
- **Frontend Integration**: `../docs/FRONTEND_INTEGRATION_GUIDE.md`

---

## Support

**Issues**: Create GitHub issue in repository
**Logs**: Check workflow run logs in Actions tab
**Docs**: See project README.md and docs/ directory
**Quality Issues**: See `docs/QUALITY_FILTERING.md`

---

**Last Updated**: 2025-10-21
**Workflow Version**: 2.0 (Quality Filtering Enabled)
**Author**: Tee-David
