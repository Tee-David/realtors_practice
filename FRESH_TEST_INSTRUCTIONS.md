# Fresh Firestore Test - NPC Quick Scrape

## ✅ Firestore Cleanup Complete

**Deleted:** 33 documents from 3 collections
- `aggregates`: 1 document
- `properties`: 29 documents
- `site_metadata`: 3 documents

**Status:** Firestore is now completely empty and ready for fresh test!

---

## 🚀 Run the Test Scrape

### **Option 1: GitHub Actions (Recommended)**

This will test the FULL workflow including Firebase credentials from GitHub Secrets.

**Steps:**

1. **Go to workflow**:
   - https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml

2. **Click "Run workflow"** (dropdown button on the right)

3. **Fill in parameters**:
   - **Site to test**: `npc`
   - **Max pages to scrape**: `5`

4. **Click "Run workflow"** (green button)

5. **Wait 3-5 minutes** for completion

---

### **Option 2: Local Test (Quick)**

This tests locally with your Firebase credentials.

**Run:**
```bash
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
set RP_PAGE_CAP=5
set RP_GEOCODE=0
set RP_HEADLESS=1
set RP_NO_AUTO_WATCHER=1
python main.py
```

**Look for:**
```
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
```

---

## 🔍 What to Check

### **1. In Workflow Logs (GitHub Actions)**

Look for these messages in the "Run test scrape" step:

```bash
✓ Firebase credentials configured (Firestore upload enabled)
```

Then in the scrape output:
```bash
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
Successful sites: 1 / 1 | Total listings: X
```

### **2. In Firestore Console**

**Go to:** https://console.firebase.google.com/project/realtor-s-practice/firestore

**Check:**
1. Click **"properties"** collection
2. You should see new documents (one per property)
3. Click on any document to see the enterprise schema:

```
Document ID: {hash}
├── basic_info
│   ├── title: "4 bedroom Detached Duplex..."
│   ├── source: "npc"
│   ├── status: "active"
│   ├── listing_type: "sale" (auto-detected)
│   └── listing_url: "https://..."
├── property_details
│   ├── type: "Detached Duplex"
│   ├── bedrooms: 4
│   ├── bathrooms: 5
│   ├── furnishing: "unfurnished" (inferred)
│   └── condition: "new" (inferred)
├── financial
│   ├── price: 180000000
│   ├── currency: "NGN"
│   ├── price_per_sqm: 450000
│   └── price_per_bedroom: 45000000
├── location
│   ├── full_address: "Lekki, Lagos"
│   ├── area: "Lekki"
│   ├── lga: "Eti-Osa"
│   ├── state: "Lagos"
│   └── coordinates: {GeoPoint}
├── amenities
│   ├── features: ["Swimming pool", "Gym", "24hr power"]
│   ├── security: ["Gated estate", "24hr security"]
│   └── utilities: ["Borehole", "Solar power"]
├── media
│   ├── images: [{url, order, caption}]
│   └── total_images: 15
├── agent_info
│   ├── name: "..."
│   └── contact: "..."
├── metadata
│   ├── quality_score: 0.85
│   ├── view_count: 0
│   ├── search_keywords: ["lekki", "detached duplex", ...]
│   ├── scrape_timestamp: {timestamp}
│   └── last_updated: {timestamp}
└── tags
    ├── premium: true (auto-tagged)
    └── hot_deal: false
```

### **3. Verify Auto-Detection Working**

Check these fields are populated automatically:
- ✅ `basic_info.listing_type` - Should be "sale" or "rent" (detected from description)
- ✅ `property_details.furnishing` - Should be "furnished", "semi-furnished", or "unfurnished"
- ✅ `property_details.condition` - Should be "new", "renovated", or "good"
- ✅ `tags.premium` - Should be true for properties ≥100M or 4+ bedrooms
- ✅ `tags.hot_deal` - Should be true for properties <15M per bedroom

---

## 📊 Expected Results

### **GitHub Actions Workflow**

**Duration:** 3-5 minutes
**Steps:**
1. ✅ Checkout code
2. ✅ Set up Python
3. ✅ Install dependencies
4. ✅ Install Playwright
5. ✅ Enable NPC site
6. ✅ Run test scrape (with Firestore upload)
7. ✅ Process exports with watcher (backup)
8. ✅ Upload results as artifacts

### **Properties Scraped**

**Expected:** 50-150 properties from 5 pages of NPC

**Enterprise Schema:**
- 9 major categories
- 85+ structured fields
- Auto-detection active
- Auto-tagging active
- Location intelligence active

### **Firestore Collections After Test**

1. **`properties`** - X documents (one per property)
2. **`site_metadata`** - 1 document (NPC scrape stats)
3. **`aggregates`** - Statistics (optional)

---

## ✅ Success Criteria

### **Workflow Logs Should Show:**

```
✓ Firebase credentials configured (Firestore upload enabled)
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
Successful sites: 1 / 1 | Total listings: X
```

### **Firestore Console Should Show:**

- ✅ `properties` collection exists
- ✅ X documents in `properties` (one per scraped listing)
- ✅ Each document has nested structure with 9 categories
- ✅ `basic_info.source = "npc"`
- ✅ `basic_info.listing_type` auto-detected
- ✅ `tags.premium` and `tags.hot_deal` auto-tagged
- ✅ `location.area`, `location.lga` extracted
- ✅ `metadata.quality_score` calculated

### **Master Workbook (Backup):**

- ✅ Created in `exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx`
- ✅ Has "npc" sheet with X rows
- ✅ Downloadable from workflow artifacts

---

## 🐛 Troubleshooting

### **If no "[SUCCESS] Uploaded" message:**

1. Check if `FIREBASE_CREDENTIALS` secret is set in GitHub
2. Check workflow logs for "Firebase credentials configured"
3. Check for error messages in scrape step

### **If Firestore console shows 0 documents:**

1. Check workflow completed successfully (green checkmark)
2. Check scrape step logs for actual upload count
3. Verify Firebase credentials are valid JSON
4. Check Firestore security rules allow writes

### **If properties missing fields:**

This is normal - not all properties have all fields. Check:
- `basic_info.*` - Should always be populated
- `financial.price` - Should always be populated
- Other fields - Optional depending on listing data

---

## 📝 What to Report Back

After running the test, let me know:

1. ✅ **Workflow status**: Success or failure?
2. ✅ **Upload count**: How many properties uploaded?
3. ✅ **Firestore console**: Do you see documents in `properties` collection?
4. ✅ **Auto-detection**: Are `listing_type`, `furnishing`, `condition` populated?
5. ✅ **Auto-tagging**: Are `premium` and `hot_deal` tags applied?

---

## 🎯 Summary

**Firestore Status:** ✅ Empty (33 documents deleted)
**NPC Site:** ✅ Enabled (config.yaml updated)
**Workflow:** ✅ Updated (Firestore uploads during scrape)
**Architecture:** ✅ Fixed (Firestore is PRIMARY, not master workbook)

**Ready to test!**

Choose Option 1 (GitHub Actions) to test the full workflow, or Option 2 (Local) for quick verification.

The key thing to look for: **"[SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)"** in the logs!
