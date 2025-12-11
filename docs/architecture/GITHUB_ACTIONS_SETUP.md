# GitHub Actions Setup Guide

> **Complete guide to setting up automatic Firestore uploads with GitHub Actions**

---

## 🔧 Setup Required

### Step 1: Add Firebase Credentials to GitHub Secrets

Your Firebase credentials file needs to be added as a GitHub Secret so the workflow can access it.

#### Instructions:

1. **Get your Firebase credentials file content:**
   ```bash
   # On your local machine, read the Firebase credentials file
   cat realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
   ```

2. **Copy the entire JSON content** (it should look like this):
   ```json
   {
     "type": "service_account",
     "project_id": "realtor-s-practice",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-...@realtor-s-practice.iam.gserviceaccount.com",
     ...
   }
   ```

3. **Add to GitHub Secrets:**
   - Go to your GitHub repository: `https://github.com/Tee-David/realtors_practice`
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **"New repository secret"**
   - Name: `FIREBASE_CREDENTIALS`
   - Value: Paste the entire JSON content from step 1
   - Click **"Add secret"**

---

## 🚀 How It Works

### Workflow Steps (Automatic)

When you trigger a scrape (manually or via API):

```
1. GitHub Actions spins up Ubuntu server
   ↓
2. Installs Python 3.11 + dependencies
   ↓
3. Runs scraper (main.py)
   → Scrapes 5 sites in parallel
   → Saves to exports/sites/
   ↓
4. Runs watcher (watcher.py --once)
   → Cleans and deduplicates data
   → Creates MASTER_CLEANED_WORKBOOK.xlsx
   ↓
5. **NEW: Uploads to Firestore** ⭐
   → Reads MASTER_CLEANED_WORKBOOK.xlsx
   → Uploads to Firebase Firestore
   → Collection: "properties"
   → Auto-merge (updates existing, adds new)
   ↓
6. Creates GitHub Artifacts (backup)
   → Raw exports (30 days)
   → Cleaned exports (30 days)
   → Logs (7 days)
```

---

## 📊 What Gets Uploaded to Firestore

### Collection: `properties`

Each property is stored as a document with this structure:

```javascript
{
  // Property Details
  title: "3 Bedroom Flat in Lekki Phase 1",
  price: 25000000,
  location: "Lekki Phase 1, Lagos",
  bedrooms: 3,
  bathrooms: 3,
  property_type: "Flat",
  land_size: "500 sqm",

  // Description & Media
  description: "Fully furnished apartment with...",
  images: "url1,url2,url3",

  // Agent Contact
  agent_name: "John Doe",
  agent_phone: "+234 801 234 5678",

  // Metadata
  source: "cwlagos",
  listing_url: "https://cwlagos.com/property/...",
  scrape_timestamp: "2025-10-21T10:00:00",
  hash: "abc123def456",  // Unique ID (prevents duplicates)
  quality_score: 0.85,   // 0.0 to 1.0 (data completeness)

  // Coordinates (if geocoded)
  coordinates: {
    latitude: 6.4474,
    longitude: 3.4701
  },

  // Firebase Metadata
  uploaded_at: <server_timestamp>,
  updated_at: <server_timestamp>
}
```

### Key Features:

- ✅ **Automatic deduplication** - Uses `hash` field as document ID
- ✅ **Merge updates** - Existing documents are updated, not duplicated
- ✅ **Quality filtering** - Only properties with quality_score ≥ 40% are uploaded
- ✅ **Fast queries** - Indexed for location, price, bedrooms, type, etc.

---

## 🔍 Querying Firestore Data

### From Your Frontend:

```javascript
// Search for properties in Lekki under ₦30M
const response = await fetch('/api/firestore/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filters: {
      location: 'Lekki',
      price_max: 30000000,
      bedrooms_min: 3,
      property_type: 'Flat'
    },
    limit: 50,
    sort_by: 'price',
    sort_desc: false
  })
});

const data = await response.json();
console.log(data.results);  // Array of properties
console.log(data.count);    // Total matching: 142
```

### From API Server:

The API server (`api_server.py`) already has the Firestore query endpoint configured:

```python
# POST /api/firestore/query
@app.route('/api/firestore/query', methods=['POST'])
def query_firestore():
    # Queries Firestore with filters
    # Returns: { results: [...], count: 142, filters_applied: {...} }
```

---

## ⚙️ Workflow Configuration Changes

### 1. Timeout Increased (FIXED ✅)

**Problem:** Workflow was stopping after 60 minutes
**Solution:** Increased to 180 minutes (3 hours)

```yaml
jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 180  # Was 60, now 180
```

### 2. Firestore Upload Added (NEW ✅)

**New Step:** Automatic upload after cleaning

```yaml
- name: Upload to Firestore
  env:
    FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
  run: |
    echo "Uploading data to Firestore..."

    # Create temporary credentials file
    echo "$FIREBASE_CREDENTIALS" > firebase-temp-credentials.json

    # Set environment variable
    export FIREBASE_SERVICE_ACCOUNT=firebase-temp-credentials.json

    # Run upload
    python scripts/upload_to_firestore.py

    # Clean up credentials
    rm firebase-temp-credentials.json

    echo "Firestore upload complete!"
```

### 3. Summary Enhanced (IMPROVED ✅)

**New:** Shows Firestore upload status in workflow summary

```yaml
# Firestore upload status
echo "### Firestore Upload" >> $GITHUB_STEP_SUMMARY
if [ -f "exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx" ]; then
  echo "✅ Data uploaded to Firestore" >> $GITHUB_STEP_SUMMARY
  echo "- Collection: \`properties\`" >> $GITHUB_STEP_SUMMARY
  echo "- Queryable via: \`POST /api/firestore/query\`" >> $GITHUB_STEP_SUMMARY
else
  echo "⚠️ No data to upload" >> $GITHUB_STEP_SUMMARY
fi
```

---

## 🐛 Troubleshooting

### Issue: "FIREBASE_CREDENTIALS secret not found"

**Solution:** Make sure you added the secret in GitHub Settings (see Step 1 above)

### Issue: "Firestore upload failed"

**Possible causes:**
1. Invalid Firebase credentials
2. Firestore rules blocking writes
3. Network timeout

**Check:**
- GitHub Actions logs → "Upload to Firestore" step
- Look for error messages

### Issue: "No data uploaded (master workbook not found)"

**Cause:** Watcher didn't create the master workbook
**Solution:**
- Check if scraper found any listings
- Review scraper logs for errors

### Issue: "Workflow timed out after 180 minutes"

**Cause:** Too many sites or pages configured
**Solution:**
- Reduce `page_cap` parameter (default: 20)
- Disable some sites in `config.yaml`
- Disable geocoding (`geocode: 0`)

---

## 📈 Performance Metrics

### Expected Times (180 min timeout):

| Configuration | Duration | Properties | Sites |
|--------------|----------|------------|-------|
| 5 sites, 2 pages | ~45 min | ~100 | 5 |
| 5 sites, 10 pages | ~90 min | ~500 | 5 |
| 5 sites, 20 pages | ~150 min | ~1000 | 5 |
| All sites (82), 5 pages | ⚠️ May timeout | ~4000 | 82 |

**Recommendations:**
- For daily scrapes: 5-10 sites, 10 pages each
- For weekly scrapes: All enabled sites, 20 pages each
- For testing: 2-3 sites, 2 pages each

---

## 🎯 Best Practices

### 1. Scraping Frequency

**Recommended:**
- **Daily:** 5-10 sites, 10-15 pages each
- **Weekly:** All sites, 20-30 pages each
- **Testing:** 2-3 sites, 2 pages max

### 2. Firestore Costs

**Free Tier Limits (Firebase Spark Plan):**
- **Reads:** 50,000 per day
- **Writes:** 20,000 per day
- **Storage:** 1 GB

**Your Usage (estimated):**
- **Writes per scrape:** ~500 documents = 500 writes
- **Daily reads (10K users):** ~30,000 reads
- **Storage:** ~1 MB per 1000 properties

**Verdict:** ✅ Will stay within FREE tier for a long time

### 3. Data Quality

**Quality Filtering:**
- Minimum quality score: 30% (configurable in `config.yaml`)
- Lower quality listings are excluded from upload
- Quality score based on:
  - Has title (20%)
  - Has price (25%)
  - Has location (20%)
  - Has bedrooms (15%)
  - Has description (10%)
  - Has agent contact (10%)

---

## 🔄 Workflow Triggers

### 1. Manual Trigger (GitHub UI)

1. Go to: `https://github.com/Tee-David/realtors_practice/actions`
2. Click **"Nigerian Real Estate Scraper"**
3. Click **"Run workflow"** dropdown
4. Set parameters:
   - Max pages: `20` (default)
   - Geocoding: `1` (enabled) or `0` (disabled)
   - Sites: Leave empty for all enabled sites
5. Click **"Run workflow"**

### 2. API Trigger (From Frontend)

```javascript
// Trigger scrape from your frontend
const triggerScrape = async () => {
  const response = await fetch('/api/github/trigger-scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      page_cap: 20,
      geocode: 1,
      sites: ['npc', 'jiji', 'propertypro']  // Optional
    })
  });

  const data = await response.json();
  console.log(data.message);  // "Scraper workflow triggered successfully"
  console.log(data.run_url);  // GitHub Actions run URL
};
```

### 3. Scheduled Trigger (Manual Scheduling)

```javascript
// Schedule scrape for tomorrow at 3 PM
const scheduleScrape = async () => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(15, 0, 0, 0);

  const response = await fetch('/api/schedule/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scheduled_time: tomorrow.toISOString(),
      page_cap: 20,
      geocode: 1
    })
  });

  const data = await response.json();
  console.log(data.job_id);  // Job ID for tracking
  console.log(data.scheduled_time);  // Confirmation
};
```

---

## 📝 Summary Checklist

Before running your first GitHub Actions scrape:

- [ ] Firebase credentials added to GitHub Secrets (`FIREBASE_CREDENTIALS`)
- [ ] Workflow file updated (`.github/workflows/scrape-production.yml`)
- [ ] Firestore database created in Firebase Console
- [ ] API server running locally for testing (`python api_server.py`)
- [ ] Test Firestore query endpoint works (`POST /api/firestore/query`)

---

## 🎉 You're All Set!

Your scraper will now:
1. ✅ Run for up to 3 hours (180 min timeout)
2. ✅ Automatically upload to Firestore
3. ✅ Store backups in GitHub Artifacts
4. ✅ Provide queryable data via API
5. ✅ Update existing records (no duplicates)

**Next:** Test by triggering a scrape manually and checking Firestore for uploaded data!

---

**Questions?** Check `docs/ARCHITECTURE.md` or GitHub Issues.
