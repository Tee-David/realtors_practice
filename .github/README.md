# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the Nigerian Real Estate Scraper.

## Workflows

### `scrape.yml` - Main Scraper Workflow

**Purpose**: Automate property scraping from Nigerian real estate websites.

**Triggers**:
1. **Repository Dispatch** (`trigger-scrape`) - Triggered by frontend via GitHub API
2. **Schedule** - Daily at 3 AM UTC (4 AM WAT)
3. **Manual** - Via GitHub Actions UI

**Duration**: 5-15 minutes (depending on number of sites and pages)

**Outputs**:
- Raw CSV/XLSX exports (per site)
- Cleaned/normalized data
- Master consolidated workbook
- Scraping logs

**Artifacts Retention**: 30 days

## Configuration

### Environment Variables (in workflow)

- `RP_PAGE_CAP` - Max pages to scrape per site (default: 20)
- `RP_GEOCODE` - Enable geocoding (1=yes, 0=no, default: 1)
- `RP_HEADLESS` - Run browser in headless mode (always 1 for GitHub Actions)
- `RP_NO_IMAGES` - Block images for faster scraping (always 1)
- `RP_DEBUG` - Enable debug logging (default: 0)

### Manual Trigger Inputs

When triggering manually via GitHub Actions UI:

- **page_cap**: Number of pages to scrape per site
- **geocode**: Enable/disable geocoding (1 or 0)
- **sites**: Comma-separated list of sites (leave empty for all enabled)

### Repository Dispatch Payload

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

### 3. Scheduled (Automatic)

Runs automatically daily at 3 AM UTC. No action needed.

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab
2. Select workflow from sidebar
3. Click on specific run to see details

### Download Artifacts

1. Go to completed workflow run
2. Scroll to **Artifacts** section at bottom
3. Click artifact name to download (ZIP file)

### Check Logs

1. Click on workflow run
2. Click on any step to expand logs
3. Look for errors (red X) or warnings

## Artifacts

Each successful run produces 3 artifacts:

1. **scraper-exports-raw-XXX** (30-day retention)
   - Contains raw CSV/XLSX files per site
   - Directory structure: `exports/sites/{site}/`

2. **scraper-exports-cleaned-XXX** (30-day retention)
   - Contains cleaned/normalized data
   - Includes `MASTER_CLEANED_WORKBOOK.xlsx`
   - Directory structure: `exports/cleaned/`

3. **scraper-logs-XXX** (7-day retention)
   - Contains scraper.log and other logs
   - Useful for troubleshooting

## Workflow Steps

1. **Setup** (~2 minutes)
   - Checkout code
   - Set up Python 3.11
   - Install dependencies
   - Install Playwright browsers

2. **Scraping** (~3-10 minutes)
   - Configure scraper
   - Run main.py
   - Scrape enabled sites

3. **Processing** (~10-30 seconds)
   - Run watcher.py
   - Clean and normalize data
   - Generate master workbook

4. **Upload** (~30-60 seconds)
   - Upload raw exports
   - Upload cleaned data
   - Upload logs

## Troubleshooting

### Workflow Not Starting

- Check GitHub Actions is enabled (Settings → Actions)
- Verify workflow file syntax
- Ensure on main/default branch

### Playwright Installation Fails

**Solution 1**: Use requests-only mode (faster, no browser)
```yaml
# Edit config.yaml
global_settings:
  scraper:
    fallback_chain: ["requests"]
```

**Solution 2**: Install system dependencies
(Already handled in workflow)

### Scraper Returns 0 Listings

- Check enabled sites in config.yaml
- Increase page_cap (may need more pages)
- Enable debug mode (RP_DEBUG=1)
- Check site logs in artifacts

### Timeout (>60 minutes)

- Reduce number of enabled sites
- Decrease page_cap
- Disable geocoding
- Increase timeout-minutes in workflow

## Cost & Limits

**GitHub Actions Free Tier**:
- 2,000 minutes/month for private repos
- Unlimited for public repos

**Estimated Usage**:
- ~10 minutes per run
- 30 runs/month (daily) = 300 minutes/month
- Well within free tier limits

**Artifact Storage**:
- 500 MB for free tier
- Artifacts auto-delete after retention period

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

## Customization

### Change Schedule

Edit `scrape.yml`:
```yaml
schedule:
  # Every 12 hours
  - cron: '0 */12 * * *'

  # Weekly on Sundays
  - cron: '0 3 * * 0'

  # Weekdays only
  - cron: '0 3 * * 1-5'
```

### Add Notifications

```yaml
# Add to workflow (after failure step)
- name: Send email notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Scraper Failed
    body: Check logs at ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

### Increase Timeout

```yaml
jobs:
  scrape:
    timeout-minutes: 180  # 3 hours (max: 360 for free tier)
```

## Documentation

- **Testing Guide**: `GITHUB_ACTIONS_TESTING.md`
- **Deployment Guide**: `FREE_DEPLOYMENT.md`
- **Frontend Integration**: `docs/guides/FRONTEND_INTEGRATION.md` (GitHub Actions section)

## Support

**Issues**: Create GitHub issue in repository
**Logs**: Check workflow run logs in Actions tab
**Docs**: See project README.md and docs/ directory

---

**Last Updated**: 2025-10-18
**Workflow Version**: 1.0
