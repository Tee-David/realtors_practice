# How to Run the NPC Test Scrape on GitHub Actions

## Quick Instructions

### Step 1: Go to GitHub Actions

1. Open your repository: **https://github.com/Tee-David/realtors_practice**
2. Click on **"Actions"** tab (top menu)

### Step 2: Run the Test Workflow

1. In the left sidebar, click **"Quick Test Scrape"**
2. Click the **"Run workflow"** dropdown button (on the right)
3. Fill in the parameters:
   - **Site to test**: `npc`
   - **Max pages to scrape**: `5`
4. Click **"Run workflow"** (green button)

### Step 3: Monitor the Workflow

1. Wait 5-10 seconds, then refresh the page
2. You'll see a new workflow run appear (yellow dot = running)
3. Click on the workflow run to see live logs
4. The workflow will:
   - ✅ Enable NPC site only
   - ✅ Scrape 5 pages max
   - ✅ Process data with watcher
   - ✅ Transform to enterprise schema (9 categories, 85+ fields)
   - ✅ Upload to Firestore
   - ✅ Archive stale listings

### Step 4: Check the Results

**In GitHub Actions Logs:**
- Look for the "Upload to Firestore" step
- You should see:
  ```
  ✅ Firebase credentials validated
  Running upload script with enterprise schema (9 categories, 85+ fields)...
  ✅ Firestore upload completed successfully!
  ```

**In Firestore Console:**
1. Go to: **https://console.firebase.google.com/project/realtor-s-practice/firestore**
2. Click on the **"properties"** collection
3. You should see new documents with NPC properties
4. Click on any document to see the enterprise schema:
   - `basic_info.*` (title, source, status, listing_type)
   - `property_details.*` (type, bedrooms, bathrooms)
   - `financial.*` (price, currency, price_per_sqm)
   - `location.*` (address, area, LGA, coordinates)
   - `amenities.*` (features, security, utilities)
   - `media.*` (images array)
   - `agent_info.*` (name, contact)
   - `metadata.*` (quality_score, view_count, search_keywords)
   - `tags.*` (premium, hot_deal)

---

## What to Expect

### Workflow Duration
- **Total time**: 3-5 minutes
- Setup (1-2 min) → Scrape (1-2 min) → Process + Upload (30 sec)

### Expected Results
- **Pages scraped**: 5 pages from NPC
- **Properties**: ~50-150 listings (depending on NPC's pagination)
- **Firestore upload**: All properties transformed to enterprise schema
- **Artifacts**: Download `test-scrape-results` to see raw CSV/XLSX files

### Success Indicators
✅ Workflow status: Green checkmark
✅ "Upload to Firestore" step: Shows success message
✅ Firestore console: New documents in `properties` collection
✅ Each document: Has nested structure with 9 categories
✅ Auto-detection: `listing_type`, `furnishing`, `condition` fields populated
✅ Auto-tagging: `premium` and `hot_deal` tags applied where applicable

---

## Troubleshooting

### If "FIREBASE_CREDENTIALS secret not set" appears:
- You haven't added the Firebase secret yet
- Follow instructions in `ADD_FIREBASE_SECRET.md`
- Add the secret first, then re-run the workflow

### If "Master workbook not found":
- Watcher step failed
- Check the "Process exports with watcher" step logs
- May need to debug watcher.py

### If Firestore upload shows errors:
- Check the full error message in workflow logs
- Verify Firebase credentials are valid JSON
- Check Firestore security rules allow writes

---

## Alternative: Run Locally First (Optional)

If you want to test locally before running on GitHub:

```bash
# Already enabled NPC site (done)
# Set environment variables
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
set FIRESTORE_ENABLED=1
set RP_PAGE_CAP=5
set RP_GEOCODE=0
set RP_HEADLESS=1

# Run scraper
python main.py

# Process with watcher
python watcher.py --once

# Upload to Firestore
python scripts/upload_to_firestore.py --cleanup --max-age-days 30
```

Then check Firestore Console to verify the data is there.

---

## What This Tests

This test run validates:

1. ✅ **GitHub Actions workflow** runs successfully
2. ✅ **Firebase credentials secret** is properly configured
3. ✅ **Scraper** can fetch NPC listings
4. ✅ **Watcher** processes and cleans data
5. ✅ **Enterprise schema transformation** works correctly
6. ✅ **Firestore upload** succeeds
7. ✅ **Auto-detection** of listing_type, furnishing, condition
8. ✅ **Auto-tagging** of premium and hot_deal properties
9. ✅ **Location intelligence** extracts landmarks and LGA
10. ✅ **All 16 Firestore API endpoints** will work with this data

Once this test succeeds, you can confidently run larger batch scrapes knowing everything will upload to Firestore automatically!

---

## Ready to Run!

🚀 Go to: **https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml**

Click **"Run workflow"** → Fill in `npc` and `5` → Click **"Run workflow"** again

⏱️ Estimated completion: 3-5 minutes

📊 After completion: Check Firestore Console for the uploaded properties!
