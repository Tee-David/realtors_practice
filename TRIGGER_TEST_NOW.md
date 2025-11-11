# Trigger Test Scrape Now - Quick Guide

## ✅ Secret Added - Ready to Test!

You've added the `FIREBASE_CREDENTIALS` secret. Now let's test if it works.

---

## Easiest Way: Manual Trigger (30 seconds)

### **Step 1: Go to Workflow**

Click this link:
**https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml**

### **Step 2: Click "Run workflow"**

- You'll see a dropdown button on the right side
- Click it

### **Step 3: Fill in Parameters**

- **Site to test**: `npc`
- **Max pages to scrape**: `5`

### **Step 4: Click "Run workflow" (green button)**

Wait 5-10 seconds, then refresh the page. You'll see a new workflow run appear.

### **Step 5: Click on the New Run**

It will show as "queued" or "in_progress" (yellow dot).

### **Step 6: Monitor Progress**

Click on the workflow run to see live logs. Watch the "Run test scrape" step.

---

## What to Look For in Logs

### ✅ SUCCESS Pattern:

```
Run test scrape
  Starting scrape...
  Site: npc
  Max pages: 5

  ✓ Firebase credentials configured (Firestore upload enabled)

  Realtors Practice Scraper Entry
  ...
  npc: [SUCCESS] Uploaded 15 listings to Firestore (PRIMARY STORE)
  Exported 15 listings for npc
  Successful sites: 1 / 1 | Total listings: 15
```

**Key message:** `[SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)`

### ❌ FAILURE Pattern:

```
Run test scrape
  Starting scrape...
  Site: npc
  Max pages: 5

  ⚠ No Firebase credentials (Firestore upload disabled)
```

**Key message:** `No Firebase credentials` = Secret not working

---

## After Workflow Completes

### Check Firestore Console:

1. **Go to:** https://console.firebase.google.com/project/realtor-s-practice/firestore

2. **Click:** `properties` collection (should appear on left side)

3. **Verify:**
   - Collection has documents (not empty)
   - Count matches upload count from logs
   - Click a document to see nested structure

4. **Sample Document Structure:**
   ```
   properties/{hash}/
   ├── basic_info
   │   ├── title: "..."
   │   ├── source: "npc"
   │   ├── listing_type: "sale" or "rent"
   ├── financial
   │   ├── price: 50000000
   │   ├── currency: "NGN"
   ├── location
   │   ├── area: "Lekki"
   │   ├── lga: "Eti-Osa"
   ├── property_details
   │   ├── bedrooms: 4
   │   ├── bathrooms: 5
   ├── tags
   │   ├── premium: true
   │   └── hot_deal: false
   └── ... (5 more categories)
   ```

---

## Alternative: API Trigger (if you have GITHUB_TOKEN)

If you have a GitHub Personal Access Token:

```bash
set GITHUB_TOKEN=your_token_here
python trigger_test.py
```

This will trigger the workflow programmatically.

---

## Expected Timeline

- **Trigger:** Instant
- **Queue:** 5-30 seconds
- **Setup:** 1-2 minutes (install dependencies)
- **Scrape:** 1-2 minutes (5 pages from NPC)
- **Upload:** 5-10 seconds
- **Total:** 3-5 minutes

---

## Quick Links

- **Trigger Workflow:** https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml
- **View All Runs:** https://github.com/Tee-David/realtors_practice/actions
- **Firestore Console:** https://console.firebase.google.com/project/realtor-s-practice/firestore
- **Repository Secrets:** https://github.com/Tee-David/realtors_practice/settings/secrets/actions

---

## What to Report Back

After the workflow completes, let me know:

1. ✅ **Did logs show:** `[SUCCESS] Uploaded X listings to Firestore`?
2. ✅ **Firestore console:** How many documents in `properties` collection?
3. ✅ **Sample document:** Does it have the nested structure (9 categories)?

If all three are YES - **WE'RE DONE! It's working!** 🎉

If any are NO - share the workflow run URL and I'll debug further.

---

## Ready?

**Click here to start:** https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml

Then click "Run workflow" and fill in:
- Site: `npc`
- Pages: `5`

**I'll wait for your results!** 🚀
