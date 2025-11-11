# Debug: Firestore Upload Not Working

## Problem

Quick test scrape ran but nothing uploaded to Firestore.

## Possible Causes

### 1. **FIREBASE_CREDENTIALS Secret Not Set in GitHub** (MOST LIKELY)

**Check:**
1. Go to: https://github.com/Tee-David/realtors_practice/settings/secrets/actions
2. Look for secret named `FIREBASE_CREDENTIALS`
3. If it doesn't exist → **THIS IS THE PROBLEM**

**Solution:**
Follow instructions in `ADD_FIREBASE_SECRET.md`

### 2. **Secret Exists But Invalid JSON**

**Check workflow logs:**
1. Go to: https://github.com/Tee-David/realtors_practice/actions
2. Click on latest "Quick Test Scrape" run
3. Click on "Run test scrape" step
4. Look for error message

**Expected if credentials invalid:**
```
❌ ERROR: Invalid Firebase credentials JSON!
```

### 3. **Credentials Correct But main.py Didn't Upload**

**Check workflow logs for:**
```
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
```

**If you see this message:**
- Upload DID work
- Check Firestore console to verify

**If you DON'T see this message:**
- Check for error in logs
- Look for "Firestore upload failed" message

### 4. **Upload Worked But Firestore Still Empty**

**Possible reasons:**
- Wrong Firestore project
- Security rules blocking writes
- Network error during upload

---

## Diagnostic Steps

### Step 1: Check GitHub Secret

```bash
# You can't check secrets via API, must check manually
# Go to: https://github.com/Tee-David/realtors_practice/settings/secrets/actions
```

**Is `FIREBASE_CREDENTIALS` listed?**
- ✅ YES → Continue to Step 2
- ❌ NO → **ADD IT NOW** (follow `ADD_FIREBASE_SECRET.md`)

### Step 2: Check Latest Workflow Run Logs

1. **Go to:** https://github.com/Tee-David/realtors_practice/actions
2. **Find:** Latest "Quick Test Scrape" run
3. **Open:** Click on the run
4. **Check:** "Run test scrape" step

**What to look for:**

**SUCCESS Pattern:**
```
✓ Firebase credentials configured (Firestore upload enabled)
...
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
Successful sites: 1 / 1 | Total listings: X
```

**FAILURE Pattern 1 (No credentials):**
```
⚠ No Firebase credentials (Firestore upload disabled)
```

**FAILURE Pattern 2 (Invalid JSON):**
```
✓ Firebase credentials configured (Firestore upload enabled)
...
ERROR: Failed to initialize Firestore: <error message>
```

**FAILURE Pattern 3 (Upload failed):**
```
✓ Firebase credentials configured (Firestore upload enabled)
...
npc: Firestore upload failed: <error message>
```

### Step 3: Check Firestore Console

**Even if logs show success, verify in console:**

1. **Go to:** https://console.firebase.google.com/project/realtor-s-practice/firestore
2. **Check:** `properties` collection
3. **Count:** Number of documents
4. **Verify:** `basic_info.source = "npc"`

**If 0 documents:**
- Upload didn't actually work despite logs
- Check Firestore security rules
- Check Firebase project ID matches

### Step 4: Test Locally to Isolate Issue

```bash
# Test local upload
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
set RP_PAGE_CAP=1
set RP_GEOCODE=0
set RP_HEADLESS=1
set RP_NO_AUTO_WATCHER=1
python main.py
```

**Look for:**
```
npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)
```

**If local works but GitHub doesn't:**
- Problem is GitHub secret configuration
- Secret might be truncated or malformed

---

## Most Likely Issue: Missing GitHub Secret

Based on the symptoms, **99% chance the secret isn't set**.

### Quick Fix:

1. **Get the JSON content:**
   ```bash
   type realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
   ```

2. **Copy the ENTIRE output** (from `{` to `}`)

3. **Add to GitHub:**
   - Go to: https://github.com/Tee-David/realtors_practice/settings/secrets/actions
   - Click "New repository secret"
   - Name: `FIREBASE_CREDENTIALS`
   - Value: Paste the entire JSON
   - Click "Add secret"

4. **Re-run the workflow:**
   - Go to: https://github.com/Tee-David/realtors_practice/actions/workflows/test-quick-scrape.yml
   - Click "Run workflow"
   - Fill in: site=`npc`, pages=`5`
   - Click "Run workflow"

5. **Check logs again** - should now see upload success

---

## Verification Checklist

After fixing, verify ALL these checkpoints:

### Workflow Logs Should Show:
- ✅ `✓ Firebase credentials configured (Firestore upload enabled)`
- ✅ `npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)`
- ✅ `Successful sites: 1 / 1 | Total listings: X`
- ✅ No error messages about Firestore

### Firestore Console Should Show:
- ✅ `properties` collection exists
- ✅ X documents in collection (matching upload count)
- ✅ Documents have nested structure (9 categories)
- ✅ `basic_info.source = "npc"`
- ✅ `basic_info.listing_type` populated
- ✅ `tags.premium` or `tags.hot_deal` present

### API Should Return Data:
```bash
curl -X POST http://localhost:5000/api/firestore/search \
  -H "Content-Type: application/json" \
  -d '{"filters": {"basic_info.source": "npc"}, "limit": 10}'
```
Should return properties, not empty array.

---

## Still Not Working?

### Share These Details:

1. **GitHub Secret Status:**
   - Is `FIREBASE_CREDENTIALS` listed in secrets? (Yes/No)
   - When was it added? (Date)

2. **Workflow Run URL:**
   - https://github.com/Tee-David/realtors_practice/actions/runs/XXXXX

3. **Specific Error from Logs:**
   - Copy the exact error message from workflow logs

4. **Firestore Console:**
   - Screenshot of collections list
   - Number of documents in `properties` collection

5. **Local Test Result:**
   - Did local test upload work? (Yes/No)
   - If no, what error?

---

## Next Steps

**Right now, do this:**

1. Check if `FIREBASE_CREDENTIALS` secret exists
2. If NO → Add it (follow steps above)
3. If YES → Share the workflow run URL so I can see the actual logs
4. Re-run the workflow after adding/fixing the secret

**The fix is 2 minutes away once we know which of the 4 causes it is.**
