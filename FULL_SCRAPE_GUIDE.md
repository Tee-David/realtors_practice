# Full Production Scrape Guide

Complete instructions for running a full 51-site scrape with Firestore verification.

---

## Step 1: Trigger the Workflow

### Option A: GitHub UI (Recommended)

1. Visit: https://github.com/Tee-David/realtors_practice/actions

2. Click **"Production Scraper (Intelligent Auto-Batching)"** in left sidebar

3. Click **"Run workflow"** button (top right)

4. Settings:
   - Branch: `main`
   - Max pages per site: `20`
   - Geocoding: `1` (enabled)
   - Force sites per session: *(leave empty for auto-calculation)*

5. Click **"Run workflow"**

### What Happens

The workflow will show you the intelligent batching strategy:

```
## Intelligent Batching Strategy

**Configuration:**
- Max pages per site: 20
- Geocoding: Enabled

**Batching:**
- Sites per session: 24
- Total sessions: 3
- Max parallel: 3

**Time Estimate:**
- Total: 346.2 min (5.77 hours)
- Status: SAFE: 346min well within 350min limit
```

---

## Step 2: Monitor Progress (Optional)

### A. GitHub Actions UI

Watch real-time progress at:
https://github.com/Tee-David/realtors_practice/actions

You'll see:
- ✅ Calculate job (2 min) - Shows batching strategy
- 🔄 Session 1, 2, 3 (5-6 hours) - Running in parallel
- ✅ Consolidate job (5 min) - Final merge

### B. List Recent Workflows

```bash
python list_workflows.py
```

Output:
```
================================================================================
RECENT WORKFLOW RUNS
================================================================================

✓ Run #123: Production Scraper (Intelligent Auto-Batching)
   ID: 12345678
   Status: in_progress - N/A
   Created: 2025-11-16 14:30:00
   Branch: main
   URL: https://github.com/...
```

### C. Monitor Firestore Uploads (Real-time)

```bash
python monitor_firestore.py --interval 30
```

Output (updates every 30 seconds):
```
================================================================================
FIRESTORE MONITORING - Real-time Property Upload Tracking
================================================================================
Collection: properties
Check interval: 30 seconds
Started: 2025-11-16 14:30:00
================================================================================

[14:30:30] Total: 0 properties (+0 in last 30s, 0.00/sec)
[14:31:00] Total: 45 properties (+45 in last 30s, 1.50/sec)
  Recent uploads:
    - npc: 4 Bedroom Duplex in Lekki Phase 1... (Lekki, N85,000,000)
    - jiji: 3 Bedroom Flat for Rent in Yaba... (Yaba, N2,500,000)
    - cwlagos: Luxury 5 Bedroom Detached House... (Ikoyi, N250,000,000)

[14:31:30] Total: 103 properties (+58 in last 30s, 1.93/sec)
...
```

Press `Ctrl+C` to stop monitoring.

---

## Step 3: Wait for Completion

### Timeline

```
00:00 - Workflow starts
00:02 - Calculate job completes (batching strategy shown)
00:02 - 3 parallel scrape sessions start

Session Progress:
00:02-05:45 - Session 1 scraping 24 sites
00:02-05:45 - Session 2 scraping 24 sites  (parallel)
00:02-01:00 - Session 3 scraping 3 sites   (parallel)

05:45 - All sessions complete
05:45 - Consolidate job starts
05:50 - Workflow complete!
```

**Total Time**: ~5 hours 50 minutes

### How to Know It's Done

1. **GitHub UI**: Workflow shows green checkmark
2. **Notifications**: GitHub sends email (if enabled)
3. **Monitor script**: Stops seeing new uploads

---

## Step 4: Verify Results

### Quick Check

```bash
python verify_full_scrape.py
```

This comprehensive script will show:

**1. Total Properties**
```
Total properties in Firestore: 1,234
```

**2. Breakdown by Source (All 51 sites)**
```
Source                         Count    % of Total
--------------------------------------------------------------------------------
npc                              156         12.6%
jiji                             142         11.5%
propertypro                      128         10.4%
...
--------------------------------------------------------------------------------
Total unique sources: 51
```

**3. Recent Uploads**
```
Properties uploaded in last 24 hours: 1,234

Recent uploads by source:
  npc: 156
  jiji: 142
  ...
```

**4. Enterprise Schema Verification**
```
Checking for all 9 required categories in sample document...
  [PASS] basic_info
  [PASS] property_details
  [PASS] financial
  [PASS] location
  [PASS] amenities
  [PASS] media
  [PASS] agent_info
  [PASS] metadata
  [PASS] tags

SCHEMA VERIFIED: All 9 categories present!
```

**5. Data Quality Metrics**
```
Average quality score: 68.5%
Quality range: 42.0% - 95.0%

Completeness:
  Properties with price: 1,180 (95.6%)
  Properties with location: 1,234 (100.0%)
  Properties with images: 1,050 (85.1%)
  Properties with bedrooms: 1,150 (93.2%)
```

**6. Auto-Tagging Verification**
```
Premium properties (auto-tagged): 87
Hot deals (auto-tagged): 143
```

**7. Sample Properties**
```
1. 4 Bedroom Duplex in Lekki Phase 1 with Swimming Pool...
   Source: npc
   Location: Lekki, Eti-Osa
   Price: N85,000,000
   Type: Duplex
   Bedrooms: 4
   URL: https://nigeriapropertycentre.com/...

...
```

**8. Final Summary**
```
================================================================================
VERIFICATION SUMMARY
================================================================================
Total Properties: 1,234
Sources Covered: 51 / 51 sites
Recent Uploads (24h): 1,234
Schema: PASS - All 9 categories
Average Quality: 68.5%
Premium Properties: 87
Hot Deals: 143

STATUS: SUCCESS - Firestore uploads confirmed!
All 1,234 properties successfully uploaded with enterprise schema.
================================================================================
```

---

## Step 5: Check Firebase Console (Visual Verification)

1. Visit: https://console.firebase.google.com/project/realtor-s-practice/firestore

2. Click on **"properties"** collection

3. You should see:
   - **1,000+** documents (all properties)
   - Each document has nested structure with 9 categories
   - Click any document to see full schema

4. Example document structure:
   ```
   properties/hash123
   ├── basic_info
   │   ├── title
   │   ├── source
   │   ├── listing_url
   │   └── ...
   ├── property_details
   │   ├── property_type
   │   ├── bedrooms
   │   └── ...
   ├── financial
   │   ├── price
   │   └── ...
   ├── location
   │   ├── area
   │   ├── lga
   │   └── ...
   ├── amenities
   ├── media
   ├── agent_info
   ├── metadata
   ├── tags
   ├── uploaded_at
   └── updated_at
   ```

---

## Step 6: Test API Endpoints

Verify data is accessible via API:

```bash
# 1. Get total count
curl http://localhost:5000/api/firestore/dashboard

# 2. Get newest properties
curl http://localhost:5000/api/firestore/newest?limit=10

# 3. Get properties by area
curl http://localhost:5000/api/firestore/properties/by-area/Lekki?limit=20

# 4. Get premium properties
curl http://localhost:5000/api/firestore/premium?limit=10

# 5. Search properties
curl -X POST http://localhost:5000/api/firestore/search \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "min_price": 50000000,
      "max_price": 100000000,
      "bedrooms": 4
    },
    "limit": 10
  }'
```

---

## Expected Results

### Minimum Success Criteria

✅ **1,000+ properties** uploaded to Firestore
✅ **40+ sites** represented (out of 51)
✅ **All 9 schema categories** present in each document
✅ **Average quality ≥ 50%**
✅ **Schema verification passes**
✅ **API endpoints return data**

### Typical Results

Based on previous scrapes:

- **Total Properties**: 1,200-1,500
- **Sites Covered**: 45-51 out of 51
- **Average Quality**: 60-75%
- **Premium Properties**: 80-120
- **Hot Deals**: 120-180
- **Completeness**:
  - Price: 95%+
  - Location: 100%
  - Images: 80-90%
  - Bedrooms: 90%+

---

## Troubleshooting

### Issue: Fewer than 1,000 properties

**Possible Causes**:
- Some sites down or blocking requests
- Quality filter too strict (40% threshold)
- Network issues during scrape

**Check**:
```bash
# Check which sites succeeded
python verify_full_scrape.py
# Look at "Breakdown by Source" section
```

### Issue: Missing sources

**Possible Causes**:
- Site returned zero results
- Site blocking automated access
- Network timeout

**Solution**:
- Check workflow logs for specific site errors
- Re-run scrape for missing sites individually

### Issue: Schema validation fails

**Possible Causes**:
- Old code version (pre-v3.1)
- Firestore transformation error

**Solution**:
```bash
# Check a sample document
python -c "
from google.cloud import firestore
import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json'
db = firestore.Client.from_service_account_json(os.environ['FIREBASE_SERVICE_ACCOUNT'])
doc = next(db.collection('properties').limit(1).stream())
print(list(doc.to_dict().keys()))
"
# Should show: ['basic_info', 'property_details', 'financial', ...]
```

### Issue: API returns empty results

**Possible Causes**:
- Scrape still running
- Firestore indexes not built
- API server not connected to Firestore

**Solution**:
1. Wait for scrape to complete
2. Check Firestore console manually
3. Restart API server

---

## Post-Scrape Actions

### 1. Download Artifacts (Optional)

GitHub Actions saves consolidated exports:

1. Go to workflow run page
2. Scroll to "Artifacts" section
3. Download: `consolidated-exports-<run_number>`
4. Contains: Master workbook with all properties

### 2. Update Frontend

If you have a frontend application:

```bash
# Frontend can now fetch properties
curl http://localhost:5000/api/firestore/properties?limit=20

# Or use React hooks
const { properties, isLoading } = useFirestoreProperties({ limit: 20 });
```

### 3. Set Up Monitoring (Optional)

Schedule regular verification:

```bash
# Check Firestore daily
0 9 * * * python /path/to/verify_full_scrape.py > /path/to/verification.log
```

---

## Quick Reference

### Start Scrape
GitHub UI → Actions → Production Scraper → Run workflow

### Monitor Progress
```bash
python list_workflows.py              # Check status
python monitor_firestore.py           # Watch uploads
```

### Verify Results
```bash
python verify_full_scrape.py          # Full verification
```

### View in Firebase
https://console.firebase.google.com/project/realtor-s-practice/firestore

### Test API
```bash
curl http://localhost:5000/api/firestore/dashboard
```

---

## Summary

1. ✅ **Trigger**: GitHub Actions → Run workflow
2. ⏱️ **Wait**: ~5-6 hours (with intelligent batching)
3. ✅ **Verify**: Run `verify_full_scrape.py`
4. 🎉 **Success**: 1,000+ properties in Firestore!

The intelligent batching system ensures:
- ✅ No timeouts (auto-calculates safe batch sizes)
- ✅ All data uploads to Firestore in real-time
- ✅ Enterprise schema (9 categories) applied
- ✅ Quality filtering and auto-tagging active
- ✅ Parallel execution for maximum speed

---

**Last Updated**: 2025-11-16
**Version**: 3.2 (Intelligent Batching)
**Status**: ✅ Ready for Full Production Scrape
