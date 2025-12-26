# GitHub Actions Scrape Failure Diagnostic Guide

**Created**: 2025-12-26
**Status**: Investigating scrape failures

---

## 🔍 COMMON FAILURE CAUSES

### 1. **Firebase Credentials Issue** ❌ UNLIKELY
**Status**: ✅ Credentials file exists and is valid
- File: `backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json`
- Format: Valid JSON with all required fields
- Project ID: `realtor-s-practice`

**GitHub Secret Setup**: Ensure `FIREBASE_CREDENTIALS` secret contains:
```bash
# Copy the ENTIRE content of the credentials file:
cat backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
```

Go to: **Settings → Secrets and variables → Actions → Repository secrets**
- Secret name: `FIREBASE_CREDENTIALS`
- Value: Paste the entire JSON content

### 2. **Workflow Configuration** ✅ CORRECT
The workflow is properly configured:
- Timeout: 120 minutes per session
- Max parallel: 10 sessions
- Batching: 1 site per session (reliable)
- Dependencies: All required packages listed

### 3. **Scraping Dependencies** ⚠️ VERIFY
**Playwright installation**:
```yaml
- name: Install Playwright and browsers
  run: |
    playwright install chromium
    playwright install-deps chromium
```

**Potential Issue**: Playwright might fail on GitHub Actions runners
- **Fix**: Add `playwright install-deps` before `playwright install chromium`

### 4. **Enabled Sites** ⚠️ CHECK THIS
**Command in workflow** (line 324):
```bash
python backend/scripts/enable_sites.py $SITES_SPACE
```

**Verify locally**:
```bash
cd backend
python scripts/enable_sites.py npc
```

If this fails, the scraper won't find any sites to scrape!

### 5. **Export Directory Structure** ⚠️ CRITICAL
The consolidate step expects:
```
session-exports/
  └── session-1-exports/
      └── sites/
          └── npc/
              ├── npc_cleaned.csv
              └── npc_raw.csv
```

**If missing**, upload will fail with:
```
ERROR: No export files found in exports/sites!
```

### 6. **Scraping Timeout** ⚠️ LIKELY CAUSE
**Current timeout**: 120 minutes per session
**With detail scraping**: 1 site can take 80-100 minutes

**Symptoms**:
- Sessions timeout without completing
- No export files generated
- Consolidate step fails with "No files found"

**Fix Options**:
1. Increase timeout to 180 minutes per session
2. Disable detail scraping (faster)
3. Reduce page cap from 8 to 5

---

## 🧪 LOCAL TESTING

### Test 1: Verify Credentials Work
```bash
cd backend
export FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json"
python -c "
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate('realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
print('SUCCESS: Firestore connected')
"
```

### Test 2: Test Single Site Scrape
```bash
cd backend
# Enable one site
python scripts/enable_sites.py npc

# Run quick scrape (2 pages, headless, no geocode)
FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json" \
FIRESTORE_ENABLED=1 \
RP_PAGE_CAP=2 \
RP_GEOCODE=0 \
RP_HEADLESS=1 \
python main.py
```

**Expected output**:
- `exports/sites/npc/` directory created
- CSV files generated
- Firestore upload logs

### Test 3: Test Upload Script
```bash
cd backend
export FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json"
python scripts/upload_sessions_to_firestore.py
```

**Expected output**:
```
FIREBASE INITIALIZATION
[SUCCESS] Loaded Firebase credentials from ...
FINDING SESSION EXPORT FILES
Found X CSV files
Total properties uploaded: Y
```

---

## 🔧 RECOMMENDED FIXES

### Fix 1: Increase Session Timeout
**File**: `.github/workflows/scrape-production.yml` (line 268)

**Before**:
```yaml
timeout-minutes: 120  # 2 hours per session
```

**After**:
```yaml
timeout-minutes: 180  # 3 hours per session (safer for detail scraping)
```

### Fix 2: Add Better Error Logging
**File**: `.github/workflows/scrape-production.yml` (line 326)

**Add before `python backend/main.py`**:
```yaml
# Run scraper with verbose logging
set -e  # Exit on error
set -x  # Print commands
python backend/main.py 2>&1 | tee scrape-session-${{ matrix.session.session_id }}.log
```

### Fix 3: Verify Export Files Before Upload
**File**: `.github/workflows/scrape-production.yml` (line 475)

**Add after line 481**:
```yaml
# Debug: Show directory structure
echo "Directory structure:"
find exports/sites -type f -name "*.csv" -o -name "*.xlsx" 2>/dev/null || echo "No files found"
```

### Fix 4: Test with Single Site First
**Manually trigger workflow with**:
- sites: `["npc"]`
- max_pages: `2`
- geocode: `0`

This should complete in ~15 minutes and help identify the issue.

---

## 📊 CHECKING WORKFLOW STATUS

### Method 1: GitHub Web UI
1. Go to: **Actions** tab
2. Click on latest "Production Scraper" run
3. Expand failed step
4. Look for error messages

### Method 2: Via API (if gh CLI available)
```bash
gh run list --workflow=scrape-production.yml --limit 5
gh run view <run-id>  # Get run-id from above
gh run view <run-id> --log-failed
```

---

## 🎯 MOST LIKELY ISSUES (In Order)

1. **Session Timeout** (80% likely)
   - Detail scraping takes too long
   - Fix: Increase timeout to 180 minutes

2. **Export Files Not Generated** (15% likely)
   - Scraping completes but produces no files
   - Fix: Check `enable_sites.py` script works
   - Fix: Verify scraping produces CSV files locally

3. **Consolidation Fails** (5% likely)
   - Export files exist but aren't found
   - Fix: Debug directory structure in workflow

4. **Firestore Upload Fails** (<1% likely)
   - Credentials are correct
   - Upload script is well-tested
   - Would show specific error in logs

---

## 🚀 NEXT STEPS

1. **Run local test** (Test 2 above) to verify everything works
2. **Check GitHub Actions logs** for actual error message
3. **Apply Fix 1** (increase timeout) as preventive measure
4. **Apply Fix 2** (better logging) to get more info
5. **Test with single site** to isolate issue

---

## 📝 WORKFLOW MODIFICATION CHECKLIST

When editing `.github/workflows/scrape-production.yml`:

- [ ] Line 268: Increase `timeout-minutes` from 120 to 180
- [ ] Line 326: Add verbose logging (`set -x`)
- [ ] Line 481: Add directory structure debug
- [ ] Test manually with `sites: ["npc"]`, `max_pages: 2`
- [ ] Monitor logs for actual error message
- [ ] Verify export files are created
- [ ] Confirm Firestore upload succeeds

---

**Generated**: 2025-12-26
**Status**: Ready for debugging
