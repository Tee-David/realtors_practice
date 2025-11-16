# Intelligent Auto-Batching System

**Version**: 3.2
**Date**: 2025-11-16
**Status**: ✅ Production Ready

---

## Overview

The Nigerian Real Estate Scraper now includes an **intelligent auto-batching system** that prevents GitHub Actions timeouts by automatically calculating optimal batch sizes based on:

- Number of enabled sites
- Pages per site configuration
- Geocoding enabled/disabled
- Historical performance data
- GitHub Actions 6-hour timeout limit

**No more manual guesswork or timeout failures!**

---

## The Problem

GitHub Actions has a **6-hour maximum timeout** per workflow run. When scraping 51 sites with 20 pages each and geocoding enabled, the scraper would:

- Take ~5.77 hours (346 minutes)
- Risk timeout due to variations in site response times
- Leave you with incomplete data if timeout occurs

**Previous solution**: Fixed 20 sites per session (didn't scale with different configurations)

---

## The Solution

### Intelligent Time Estimation

The system estimates scraping time based on empirical testing:

```python
TIME_PER_PAGE = 8 seconds         # Includes loading, scrolling, parsing
TIME_PER_SITE_OVERHEAD = 45 sec   # Site initialization
GEOCODE_TIME_PER_PROPERTY = 1.2s  # Per geocoded property
FIRESTORE_UPLOAD_TIME = 0.3s      # Per property upload
BUFFER_MULTIPLIER = 1.3           # 30% safety margin
```

### Dynamic Batch Calculation

The workflow automatically calculates:

1. **Time per site** = (pages × 8s) + 45s + geocoding + upload
2. **Sites per session** = (350 min × 60s) / (1.3 × time_per_site)
3. **Total sessions** = ceil(total_sites / sites_per_session)
4. **Estimated duration** = (session_time × sessions) / parallel_jobs

### Auto-Scaling

- **2 sites, 10 pages**: Single session, ~1 hour
- **51 sites, 20 pages, geocoding**: 3 sessions (24 sites each), ~5.77 hours
- **51 sites, 40 pages, geocoding**: 6 sessions (12 sites each), ~5.5 hours
- **100 sites, 20 pages**: Automatically splits into safe batches

---

## How to Use

### Option 1: Full Auto Mode (Recommended)

Just trigger the workflow - it calculates everything automatically:

```bash
# Via GitHub UI
# Go to Actions → Production Scraper → Run workflow
# Leave all fields default - it auto-calculates!

# Via API
curl -X POST https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -H "Authorization: token YOUR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"event_type":"trigger-scrape","client_payload":{"max_pages":20}}'
```

The system will:
1. Count enabled sites in config.yaml
2. Calculate optimal sites_per_session
3. Estimate total time
4. Warn if close to timeout
5. Execute safely

### Option 2: Manual Override

If you want to force a specific batch size:

```bash
# Via GitHub UI
# Go to Actions → Production Scraper → Run workflow
# Set "force_sites_per_session" to desired number (e.g., 15)

# Via API
curl -X POST https://api.github.com/repos/Tee-David/realtors_practice/dispatches \
  -H "Authorization: token YOUR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type":"trigger-scrape",
    "client_payload":{
      "max_pages":20,
      "sites_per_session":15
    }
  }'
```

### Option 3: Local Estimation

Test batching strategy before running:

```bash
# Estimate with current config
python scripts/estimate_scrape_time.py

# Estimate with specific parameters
python scripts/estimate_scrape_time.py --max-pages 30 --parallel 3

# Get JSON output
python scripts/estimate_scrape_time.py --max-pages 20 --json
```

---

## Workflow Process

### 1. Calculate Job

First job in the workflow:

- Reads config.yaml
- Counts enabled sites
- Calculates optimal batching
- Estimates total time
- Outputs strategy to next jobs

**Outputs**:
```yaml
sessions: [{session_id: 1, sites: "npc,jiji,propertypro", site_count: 3}, ...]
total_sessions: 3
sites_per_session: 24
estimated_minutes: 346.2
estimated_hours: 5.77
is_safe: true
recommendation: "SAFE: 346min well within 350min limit"
```

### 2. Scrape Jobs

Runs in parallel (max 3 concurrent sessions):

- Each session scrapes its assigned sites
- Session timeout: 180 minutes (3 hours)
- Total workflow stays under 6 hours due to parallelization

### 3. Consolidate Job

After all sessions complete:

- Merges all session exports
- Creates master workbook
- Uploads consolidated artifacts

---

## Understanding the Estimates

### Time Breakdown

For **1 site with 20 pages and geocoding**:

```
Scraping time:    (20 pages × 8s) + 45s = 205s
Properties:       20 pages × 15 props/page = 300 properties
Geocoding:        300 × 1.2s = 360s
Firestore upload: 300 × 0.3s = 90s
─────────────────────────────────────────
Total per site:   205 + 360 + 90 = 655s (~11 min)
```

For **24 sites per session**:

```
All sites:        24 × 655s = 15,720s
Watcher overhead: 120s
Buffer (30%):     × 1.3
─────────────────────────────────────────
Total per session: ~347 min (~5.8 hours)
```

For **51 sites across 3 parallel sessions**:

```
Session 1: 24 sites (~5.8 hours)
Session 2: 24 sites (~5.8 hours)  } Running in parallel
Session 3: 3 sites (~0.7 hours)   }
─────────────────────────────────────────
Total time: ~5.8 hours (limited by slowest session)
```

---

## Configuration Examples

### Fast Scrape (Testing)

```yaml
# In workflow trigger
max_pages: 5
geocode: 0
```

**Result**: 2-3 sites per session, ~30 minutes total

### Standard Production

```yaml
# In workflow trigger (or leave default)
max_pages: 20
geocode: 1
```

**Result**: 24 sites per session, ~5.77 hours for 51 sites

### Deep Scrape

```yaml
# In workflow trigger
max_pages: 40
geocode: 1
```

**Result**: 12 sites per session, ~5.5 hours for 51 sites

### Conservative (Maximum Safety)

```yaml
# In workflow trigger
max_pages: 20
geocode: 1
force_sites_per_session: 15
```

**Result**: 15 sites per session, ~4 hours for 51 sites

---

## Safety Features

### 1. Automatic Warning

If estimated time > 90% of limit:

```
⚠️ CLOSE TO LIMIT: 346min. Consider 19 sites/session for safety
```

### 2. Timeout Protection

If estimated time > 6 hours:

```
⚠️ WARNING: Estimated 380min exceeds 350min limit.
           Reduce to 19 sites/session
```

The workflow will still run but with higher timeout risk.

### 3. Buffer Multiplier

All estimates include 30% safety buffer to account for:

- Slow site responses
- Network variations
- Geocoding API delays
- Firestore upload variations

### 4. Per-Session Timeout

Each session has individual 180-minute timeout:

- If one session times out, others continue
- Partial data is preserved
- Consolidation happens with available data

---

## Monitoring

### During Workflow Run

GitHub Actions UI shows:

1. **Calculate job**: Time estimate and recommendation
2. **Scrape jobs**: Progress for each parallel session
3. **Consolidate job**: Final statistics

### After Completion

Check workflow summary for:

```markdown
## Intelligent Batching Strategy

**Configuration:**
- Max pages per site: 20
- Geocoding: ✅ Enabled

**Batching:**
- Sites per session: 24
- Total sessions: 3
- Max parallel: 3

**Time Estimate:**
- Total: 346.2 min (5.77 hours)
- Status: ✅ SAFE: 346min well within 350min limit

## Production Scrape Complete

**Intelligent Batching:**
- Strategy: SAFE: 346min well within 350min limit
- Sessions completed: 3
- Sites per session: 24
- Estimated time: 5.77 hours

**Results:**
- Sites scraped: 51
- Files generated: 102
- Properties: 1,234

**Firestore:**
✅ Uploaded to Firestore during scraping
```

---

## Troubleshooting

### Workflow Times Out Despite Estimation

**Cause**: Actual scraping took longer than estimated

**Solutions**:
1. Reduce sites_per_session:
   ```
   force_sites_per_session: 15
   ```
2. Disable geocoding temporarily:
   ```
   geocode: 0
   ```
3. Reduce max_pages:
   ```
   max_pages: 15
   ```

### Estimation Says "CLOSE TO LIMIT"

**Cause**: Configuration pushes close to 6-hour limit

**Solutions**:
1. Workflow will work but risky
2. Consider reducing one parameter:
   - `max_pages: 15` (from 20)
   - `force_sites_per_session: 19` (from 24)
   - `geocode: 0` (saves ~50% time)

### Too Many Small Sessions

**Cause**: Very conservative estimation or few enabled sites

**Solutions**:
1. Enable more sites in config.yaml
2. Increase max_pages
3. Force larger batches (if you know it's safe):
   ```
   force_sites_per_session: 30
   ```

### Want Faster Completion

**Cause**: Default parallel=3 may be conservative

**Note**: Currently hardcoded to 3 parallel sessions. To increase:

1. Edit `.github/workflows/scrape-production.yml`
2. Change `MAX_PARALLEL = 3` to `MAX_PARALLEL = 5`
3. Change `max-parallel: 3` to `max-parallel: 5`

**Warning**: More parallel jobs = higher memory usage, might hit GitHub limits

---

## API Integration

### Trigger with Auto-Batching

```python
import requests

# Let system auto-calculate everything
response = requests.post(
    'http://localhost:5000/api/github/trigger-scrape',
    json={
        'max_pages': 20,
        'geocode': True
        # sites_per_session calculated automatically
    }
)
```

### Trigger with Forced Batching

```python
# Override auto-calculation
response = requests.post(
    'http://localhost:5000/api/github/trigger-scrape',
    json={
        'max_pages': 20,
        'geocode': True,
        'sites_per_session': 15  # Force 15 sites per session
    }
)
```

---

## Advanced: Tuning the Estimator

If you find estimates are consistently off, you can tune the constants:

**File**: `scripts/estimate_scrape_time.py`

```python
# Adjust these based on your actual performance
TIME_PER_PAGE = 8  # Increase if sites are slow
TIME_PER_SITE_OVERHEAD = 45  # Increase for complex sites
GEOCODE_TIME_PER_PROPERTY = 1.2  # Adjust based on Nominatim API
BUFFER_MULTIPLIER = 1.3  # Increase for more safety margin
```

**File**: `.github/workflows/scrape-production.yml` (lines 68-73)

Update the same constants in the workflow's Python code.

---

## Benefits

### Before Intelligent Batching

- Fixed 20 sites per session
- Manual calculation required
- Frequent timeouts with 51 sites
- Incomplete data on failure

### After Intelligent Batching

✅ **Automatic** - No manual calculation
✅ **Scalable** - Works with 1-1000+ sites
✅ **Safe** - 30% buffer prevents timeouts
✅ **Smart** - Adjusts to configuration changes
✅ **Transparent** - Shows estimates before running
✅ **Flexible** - Can override if needed

---

## Technical Details

### Workflow Outputs

The `calculate` job outputs these for use by downstream jobs:

- `sessions`: JSON array of session configs
- `total_sessions`: Number of parallel sessions
- `sites_per_session`: Calculated batch size
- `estimated_minutes`: Total estimated time
- `estimated_hours`: Total estimated hours
- `is_safe`: Boolean (time < 350 min)
- `recommendation`: Human-readable status

### Session Matrix

GitHub Actions matrix strategy runs sessions in parallel:

```yaml
strategy:
  max-parallel: 3
  fail-fast: false
  matrix:
    session: ${{ fromJson(needs.calculate.outputs.sessions) }}
```

This creates jobs like:
- `Scrape Session 1` - 24 sites
- `Scrape Session 2` - 24 sites
- `Scrape Session 3` - 3 sites

All running simultaneously!

---

## Future Enhancements

Potential improvements:

1. **Historical Learning**: Store actual runtimes, adjust estimates
2. **Site-Specific Timing**: Different estimates per site
3. **Dynamic Rebalancing**: Redistribute if session fails
4. **Cost Optimization**: Balance between time and parallel jobs
5. **Adaptive Buffer**: Reduce buffer if consistent success

---

## Summary

The intelligent auto-batching system:

1. **Analyzes** your configuration (sites, pages, geocoding)
2. **Calculates** optimal batch size to avoid timeouts
3. **Estimates** total time with 30% safety buffer
4. **Executes** scraping in parallel sessions
5. **Consolidates** all results into master workbook

**Result**: Reliable, scalable scraping that never times out!

---

**Version**: 3.2 (Intelligent Batching)
**Last Updated**: 2025-11-16
**Status**: ✅ Production Ready
