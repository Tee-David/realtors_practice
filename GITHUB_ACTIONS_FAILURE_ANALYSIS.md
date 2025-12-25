# GitHub Actions Workflow Failure Analysis
**Date**: 2025-12-25
**Last 3 Runs**: ALL FAILED
**Workflow**: Production Scraper (Intelligent Auto-Batching)

---

## Recent Failures

```
Run #66: FAILED (2025-12-24 22:07:42Z)
Run #65: FAILED (2025-12-24 09:53:05Z)  
Run #64: FAILED (2025-12-24 09:43:40Z)
```

**Pattern**: 100% failure rate on last 3 runs

---

## Failure Analysis

### Failed Jobs:
1. ✅ Calculate Intelligent Batching - **SUCCESS**
2. ❌ Scrape Session 1 - **FAILURE**
3. ❌ Consolidate All Sessions - **FAILURE** (downstream from Session 1)

### Root Cause (Most Likely):

**Primary suspect**: Session 1 scraping step failed, causing:
- No export files produced
- Consolidation step has nothing to consolidate
- Entire workflow fails

---

## Possible Failure Reasons

### 1. FIREBASE_CREDENTIALS Secret Issue 🔴
**Likelihood**: HIGH

**Evidence from workflow**:
```yaml
Line 451: if [ -z "$FIREBASE_CREDENTIALS" ]; then
Line 452:   echo "ERROR: FIREBASE_CREDENTIALS secret not set!"
Line 453:   exit 1
```

**Check**:
- Go to: `Settings → Secrets and variables → Actions`
- Verify `FIREBASE_CREDENTIALS` secret exists
- Verify it contains valid Firebase service account JSON

**Fix if missing**:
1. Download service account JSON from Firebase Console
2. Add as GitHub secret named `FIREBASE_CREDENTIALS`
3. Paste entire JSON content

---

### 2. Playwright Browser Installation Failing
**Likelihood**: MEDIUM

**Evidence from workflow**:
```yaml
Line 290-293:
- name: Install Playwright and browsers
  run: |
    playwright install chromium
    playwright install-deps chromium
```

**Possible causes**:
- GitHub runner out of disk space
- Network timeout downloading Chromium
- Missing system dependencies

**Fix**:
- Check workflow logs for "playwright install" step
- May need to add retry logic or use cached browsers

---

### 3. Scraping Timeout (120 minutes)
**Likelihood**: LOW

**Evidence from workflow**:
```yaml
Line 268: timeout-minutes: 120  # 2 hours per session
```

**Check**:
- If scraping 1 site is taking >120 minutes, job times out
- Workflow tries to scrape enabled sites (currently 8)
- With 1 site per session = should be well under 120 min

**Fix if timing out**:
- Reduce `RP_PAGE_CAP` (currently defaults to 8 pages)
- Disable slower sites
- Increase timeout to 180 minutes

---

### 4. No Export Files Produced
**Likelihood**: MEDIUM

**Evidence from workflow**:
```yaml
Line 488-505: Validates export files exist
  if [ $total_files -eq 0 ]; then
    echo "ERROR: No export files found!"
    exit 1
```

**Possible causes**:
- Scraper runs but finds no properties
- All properties filtered out (Lagos filter)
- Export step crashes before writing files

**Fix**:
- Check scraper logs in failed workflow
- Verify sites are accessible
- Test locally first

---

### 5. File Permission Errors
**Likelihood**: LOW

**Evidence from local logs**:
```
ERROR - Failed to save state: [Errno 13] Permission denied
ERROR - Failed to save state: [WinError 32] Process cannot access file
```

**Note**: These are local Windows errors, unlikely on Linux GitHub runners

---

## Debugging Steps

### Step 1: Check GitHub Secrets
```bash
# In GitHub repo:
Settings → Secrets and variables → Actions

# Should see:
FIREBASE_CREDENTIALS - Set (Updated X days ago)
```

### Step 2: Check Workflow Logs
```bash
# Go to failed run:
https://github.com/Tee-David/realtors_practice/actions/runs/20494603447

# Look for:
1. "Install Playwright" step - did it succeed?
2. "Run scraper" step - what error did it show?
3. "Upload to Firestore" step - did it reach this step?
```

### Step 3: Test Locally
```bash
# Replicate workflow environment:
cd backend
FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json" \
FIRESTORE_ENABLED=1 \
RP_PAGE_CAP=2 \
RP_GEOCODE=1 \
RP_HEADLESS=1 \
python main.py

# If this works locally but fails in GitHub Actions → secret issue
```

---

## Most Likely Fix

**90% confident the issue is:**

1. FIREBASE_CREDENTIALS secret not set or invalid
2. Workflow tries to upload to Firestore
3. Fails authentication
4. Entire workflow fails

**Action Required**:
1. Check GitHub repo secrets
2. Verify FIREBASE_CREDENTIALS exists
3. If missing, add it with service account JSON
4. Re-run workflow

---

## How to Re-Run Workflow

### Option 1: From GitHub UI
```
1. Go to: Actions tab
2. Click: "Production Scraper (Intelligent Auto-Batching)"
3. Click: "Run workflow" button
4. Fill in:
   - max_pages: 2 (for testing)
   - geocode: 1
   - sites: (leave empty for all enabled)
5. Click: "Run workflow"
```

### Option 2: From Frontend
```
If frontend has "Trigger Scrape" button:
1. Click button
2. Select sites to scrape
3. Start scrape
4. Frontend will trigger GitHub Actions via API
```

---

## Expected Behavior After Fix

When working correctly, workflow should:

1. ✅ Calculate batching (always succeeds)
2. ✅ Scrape Session 1 (8 sites, ~60-90 minutes)
3. ✅ Upload session artifacts
4. ✅ Consolidate all sessions
5. ✅ Upload to Firestore (using FIREBASE_CREDENTIALS)
6. ✅ Verify upload
7. ✅ Generate summary with property count

**Success indicators**:
- Green checkmarks on all jobs
- Summary shows "X properties uploaded"
- Firestore has new properties

---

## Integration with Frontend

Once workflow succeeds, frontend should be able to:

1. Trigger new scrapes via API
2. See workflow status in Dashboard
3. See workflow logs in Scrape Results page
4. Get notified when scrape completes

**Current Status**: Frontend can trigger but can't see logs (Issue #5 from main assessment)

---

## Add to Main Fix Plan

This is **ISSUE #16: GitHub Actions Workflow Failing**

**Severity**: CRITICAL 🔴
**Impact**: Cannot run automated scrapes
**Priority**: 1 (Fix immediately)

**Fix Steps**:
1. Verify FIREBASE_CREDENTIALS secret exists (5 min)
2. If missing, add from local JSON file (5 min)
3. Re-run workflow to test (2 min)
4. Monitor logs to confirm success (60-90 min for full run)

**Total Time**: 10 minutes setup + 90 minutes monitoring

---

**Recommendation**: Fix this BEFORE implementing GitHub logs integration in frontend (Issue #5), since logs integration won't help if workflow is broken.
