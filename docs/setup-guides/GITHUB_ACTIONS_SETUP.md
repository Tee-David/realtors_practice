# GitHub Actions Setup Guide

Complete guide for setting up and using GitHub Actions workflows for automated scraping.

---

## Prerequisites

### 1. GitHub Repository
- Repository must be on GitHub
- You must have admin/write access
- Actions must be enabled (Settings → Actions → Allow all actions)

### 2. Firebase Project (Optional, but Recommended)
- Firebase project created
- Service account credentials JSON file
- Firestore database enabled

### 3. GitHub Personal Access Token (For API Integration)
- Token with `repo` scope
- Used for triggering workflows from frontend

---

## Quick Setup (5 Minutes)

### Step 1: Add Firebase Credentials Secret

1. Get your Firebase service account JSON file
2. Go to your GitHub repository
3. Navigate to: **Settings** → **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `FIREBASE_CREDENTIALS`
6. Value: Paste entire JSON content from your service account file
7. Click **Add secret**

### Step 2: Test the Quick Test Workflow

1. Go to **Actions** tab in your repository
2. Click **Quick Test Scrape** workflow
3. Click **Run workflow** (green button)
4. Set parameters:
   - Site: `cwlagos` (default)
   - Pages: `3` (default)
5. Click **Run workflow**
6. Watch the progress in real-time

**Expected Result**: Workflow completes in 2-5 minutes, scraped data uploaded to Firestore

---

## Workflows Overview

### 1. Production Scraper (Auto-Scaling Multi-Session)

**File**: `.github/workflows/scrape-production.yml`

**Purpose**: Full production scrape of all 51 sites with parallel processing

**Features**:
- Auto-scaling: Automatically splits sites into optimal batches
- Parallel processing: Runs 3 sessions concurrently
- Fail-safe: Continues even if one session fails
- Firestore upload: Automatic upload during scraping
- Consolidation: Merges all session outputs
- Artifacts: Saves exports for 30 days

**Trigger Methods**:

#### A. Manual Trigger (GitHub UI)
1. Go to **Actions** tab
2. Select **Production Scraper (Auto-Scaling Multi-Session)**
3. Click **Run workflow**
4. Set parameters:
   - `sites_per_session`: 20 (default) - Number of sites per parallel session
   - `page_cap`: 20 (default) - Max pages to scrape per site
   - `geocode`: 1 (default) - Enable geocoding (1=yes, 0=no)
5. Click **Run workflow**

#### B. API Trigger (From Frontend)

**Endpoint**: `POST /api/github/trigger-scrape`

**Prerequisites**:
Set environment variables in your API server:
```bash
export GITHUB_TOKEN="ghp_your_personal_access_token_here"
export GITHUB_OWNER="your-github-username"
export GITHUB_REPO="repository-name"
```

**API Request**:
```bash
curl -X POST http://localhost:5000/api/github/trigger-scrape \
  -H "Content-Type: application/json" \
  -d '{
    "sites_per_session": 20,
    "page_cap": 20,
    "geocode": 1
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Scraper workflow triggered successfully",
  "run_url": "https://github.com/YOUR_ORG/YOUR_REPO/actions"
}
```

**Alternative (Direct GitHub API)**:
```bash
curl -X POST https://api.github.com/repos/YOUR_ORG/YOUR_REPO/dispatches \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{
    "event_type": "trigger-scrape",
    "client_payload": {
      "sites_per_session": "20",
      "page_cap": "20",
      "geocode": "1"
    }
  }'
```

---

### 2. Quick Test Scrape

**File**: `.github/workflows/test-quick-scrape.yml`

**Purpose**: Quick test of single site for development/testing

**Features**:
- Single site scraping (configurable)
- Quick test (3 pages default)
- Debug output enabled
- 10-minute timeout
- Artifact upload for results

**Trigger**: Manual only (workflow_dispatch)

**Parameters**:
- `site`: Site to test (default: `cwlagos`)
- `pages`: Max pages to scrape (default: `3`)

**Usage**:
1. Go to **Actions** tab
2. Select **Quick Test Scrape**
3. Click **Run workflow**
4. Set parameters (or use defaults)
5. Click **Run workflow**

---

## Session Strategy (Production Scraper)

### How Sessions Work

**For 51 sites with `sites_per_session=20`:**

```
Prepare Job:
  ↓
  Splits 51 sites into 3 sessions:
    - Session 1: Sites 1-20   (20 sites)
    - Session 2: Sites 21-40  (20 sites)
    - Session 3: Sites 41-51  (11 sites)
  ↓
Scrape Jobs (Matrix Strategy):
  ┌─────────────┬─────────────┬─────────────┐
  │  Session 1  │  Session 2  │  Session 3  │  ← Run in PARALLEL
  │  (20 sites) │  (20 sites) │  (11 sites) │
  └─────────────┴─────────────┴─────────────┘
  ↓
Consolidate Job:
  ↓
  Merges all session outputs
  ↓
  Creates master workbook
  ↓
  Uploads consolidated artifact
```

### Parallel Processing

**Configuration** (in `.github/workflows/scrape-production.yml`):
```yaml
strategy:
  max-parallel: 3        # Run 3 sessions concurrently
  fail-fast: false       # Don't cancel other sessions if one fails
  matrix:
    session: ${{ fromJson(needs.prepare.outputs.sessions) }}
```

**Benefit**:
- 51 sites in 3 sessions (parallel) ≈ **1-2 hours**
- vs. 51 sites sequentially ≈ **3-4 hours**
- **2-3x faster** with parallel processing

---

## Monitoring Workflow Progress

### Via GitHub UI

1. Go to **Actions** tab
2. Click on the running workflow
3. See real-time logs for each job
4. View consolidated summary at the end

### Via API (For Frontend Integration)

**Get Recent Workflow Runs**:
```bash
curl http://localhost:5000/api/github/workflow-runs
```

**Response**:
```json
{
  "total_count": 10,
  "workflow_runs": [
    {
      "id": 123456789,
      "name": "Production Scraper",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-11-16T10:00:00Z",
      "updated_at": "2025-11-16T11:30:00Z",
      "run_number": 42,
      "html_url": "https://github.com/..."
    }
  ]
}
```

**Get Workflow Status by Run ID**:
```bash
curl http://localhost:5000/api/notifications/workflow-status/123456789
```

---

## Downloading Artifacts

### Via GitHub UI

1. Go to **Actions** tab
2. Click on completed workflow run
3. Scroll to **Artifacts** section
4. Click on artifact name to download

**Available Artifacts**:
- `session-1-exports` - Exports from session 1
- `session-2-exports` - Exports from session 2
- `session-3-exports` - Exports from session 3
- `consolidated-exports-{run_number}` - Master workbook (all sessions merged)

### Via API

**List Artifacts**:
```bash
curl http://localhost:5000/api/github/artifacts
```

**Download Specific Artifact**:
```bash
curl http://localhost:5000/api/github/artifact/123456/download -o artifact.zip
```

---

## Advanced Configuration

### Customizing Batch Size

**Environment Variable**: `RP_BATCH_SIZE`

**Options**:
1. **Auto** (default): Calculated based on site count
   - ≤10 sites: No batching (all in one batch)
   - 11-30 sites: 10 sites per batch
   - 31-50 sites: 15 sites per batch
   - 51+ sites: 20 sites per batch

2. **Manual Override**: Set in workflow or environment
   ```yaml
   env:
     RP_BATCH_SIZE: 25  # Force 25 sites per batch
   ```

### Customizing Session Count

**Edit**: `.github/workflows/scrape-production.yml`

**Line 65**:
```yaml
sites_per_session = int("${{ ... }}" or "20")  # Change 20 to desired number
```

**Example**: For 10 sites per session (5 sessions total for 51 sites)
```yaml
sites_per_session = int("${{ ... }}" or "10")
```

### Customizing Parallel Sessions

**Edit**: `.github/workflows/scrape-production.yml`

**Line 95**:
```yaml
max-parallel: 3  # Change to 5 for more parallelism
```

**Note**: GitHub Actions has limits:
- **Free tier**: 20 concurrent jobs
- **Pro/Team**: Higher limits
- **Self-hosted runners**: No limit

---

## Troubleshooting

### Issue 1: Workflow Not Triggering

**Symptoms**: API request returns 200 but workflow doesn't start

**Check**:
1. Is `GITHUB_TOKEN` valid? Test with:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/user
   ```
2. Does token have `repo` scope?
3. Are Actions enabled in repository settings?

**Solution**: Regenerate token with correct scopes

---

### Issue 2: Firestore Upload Failing

**Symptoms**: Logs show `⚠ No Firebase credentials (Firestore upload disabled)`

**Check**:
1. Is `FIREBASE_CREDENTIALS` secret set in repository?
2. Is the JSON valid? Test locally:
   ```bash
   echo "$FIREBASE_CREDENTIALS" > test.json
   python -c "import json; json.load(open('test.json'))"
   ```

**Solution**: Re-add secret with valid JSON

---

### Issue 3: Session Timeout

**Symptoms**: Workflow cancelled after 3 hours

**Cause**: GitHub Actions has 6-hour timeout per job (default: 360 minutes)

**Solution**: Reduce `page_cap` or increase `sites_per_session`:
```yaml
# Reduce scraping time
env:
  RP_PAGE_CAP: 10  # Instead of 20
```

---

### Issue 4: Out of Memory

**Symptoms**: Workflow fails with OOM error

**Cause**: Too many sites in one session

**Solution**: Reduce `sites_per_session`:
```yaml
sites_per_session = int("${{ ... }}" or "10")  # Instead of 20
```

---

## Best Practices

### For Testing

1. **Start with Quick Test**: Use `test-quick-scrape.yml` for single site
2. **Test Single Session**: Set `sites_per_session=51` for one large session
3. **Verify Firestore Upload**: Check Firestore console after test
4. **Check Artifacts**: Download and verify exports

### For Production

1. **Use Default Settings**: `sites_per_session=20`, `page_cap=20`
2. **Enable Geocoding**: Set `geocode=1` for location-based search
3. **Schedule Daily**: Add cron schedule to workflow
4. **Monitor Costs**: Check GitHub Actions usage (free tier: 2000 mins/month)

### For Scaling

1. **Increase Parallelism**: Set `max-parallel=5` (if allowed)
2. **Optimize Batch Size**: Test different `sites_per_session` values
3. **Disable Detail Scraping**: For less critical sites (saves time)
4. **Use Self-Hosted Runners**: For unlimited parallelism

---

## Scheduled Scraping (Automated)

### Add Cron Schedule

**Edit**: `.github/workflows/scrape-production.yml`

**Add under `on:`**:
```yaml
on:
  # Existing triggers
  repository_dispatch:
    types: [trigger-scrape]
  workflow_dispatch:
    # ...

  # Add this for daily scraping
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
```

**Cron Examples**:
- `0 2 * * *` - Daily at 2 AM UTC
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Weekly on Sunday at midnight
- `0 0 1 * *` - Monthly on the 1st at midnight

### Disable Scheduled Runs

**Comment out the schedule**:
```yaml
on:
  # schedule:
  #   - cron: '0 2 * * *'
```

---

## Cost Estimation

### GitHub Actions (Free Tier)

**Free Minutes**: 2000 minutes/month
**Overage Cost**: $0.008/minute (Linux runners)

**Estimated Usage**:
- Quick test (1 site, 3 pages): **5 minutes**
- Production scrape (51 sites, 20 pages, 3 sessions): **120 minutes** (40 mins per session × 3 parallel)
- Daily production scrapes: **120 mins × 30 days = 3600 minutes/month**

**Monthly Cost** (if running daily):
- Free tier: 2000 minutes
- Overage: 1600 minutes × $0.008 = **$12.80/month**

**Recommendation**: Use scheduled runs 2-3x per week instead of daily to stay within free tier

---

## Frontend Integration Example

### React Hook for Triggering Workflow

```typescript
import { useState } from 'react';

export function useTriggerScrape() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const triggerScrape = async (options?: {
    sitesPerSession?: number;
    pageCap?: number;
    geocode?: boolean;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/github/trigger-scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sites_per_session: options?.sitesPerSession || 20,
          page_cap: options?.pageCap || 20,
          geocode: options?.geocode !== false ? 1 : 0,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to trigger scrape');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { triggerScrape, loading, error };
}

// Usage
function ScrapeButton() {
  const { triggerScrape, loading, error } = useTriggerScrape();

  const handleClick = async () => {
    try {
      const result = await triggerScrape({
        sitesPerSession: 20,
        pageCap: 20,
        geocode: true,
      });

      console.log('Workflow triggered:', result.run_url);
      window.open(result.run_url, '_blank');
    } catch (err) {
      console.error('Failed to trigger scrape:', err);
    }
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? 'Triggering...' : 'Start Full Scrape'}
    </button>
  );
}
```

---

## Summary

✅ **Setup Complete** if you've:
1. Added `FIREBASE_CREDENTIALS` secret
2. Tested Quick Test workflow
3. Tested Production workflow (optional)

✅ **Ready for Production** if you've:
1. Verified Firestore uploads
2. Tested artifact downloads
3. Set up GitHub token for API integration (optional)

✅ **Ready for Automation** if you've:
1. Added cron schedule (optional)
2. Calculated monthly costs
3. Integrated with frontend (optional)

---

**Next Steps**:
1. Run first production scrape
2. Monitor results in Firestore
3. Download and verify artifacts
4. Set up scheduled runs (optional)
5. Integrate with frontend (optional)

**Support**: Check logs in GitHub Actions tab for detailed error messages
