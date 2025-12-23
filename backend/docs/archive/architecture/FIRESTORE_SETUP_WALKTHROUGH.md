# 🔥 Firebase Firestore Setup - Complete Walkthrough

**Date:** 2025-10-21
**Time Required:** ~30-45 minutes
**Cost:** $0 (Free tier)

This guide walks you through setting up Firebase Firestore from scratch, even before your frontend is ready.

---

## 📋 **Prerequisites**

- ✅ Google account (Gmail)
- ✅ Internet browser
- ✅ Master workbook created (from scraper)
- ✅ Python environment with packages installed

---

## 🚀 **Step-by-Step Setup**

### **STEP 1: Create Firebase Project** (5 minutes)

1. **Go to Firebase Console**
   - Open your browser
   - Visit: https://console.firebase.google.com/
   - Click **"Sign in with Google"** (use your Gmail account)

2. **Create New Project**
   - Click **"Add project"** or **"Create a project"**
   - **Project name:** `realtors-practice` (or any name you prefer)
   - Click **"Continue"**

3. **Disable Google Analytics** (Optional - Recommended for simplicity)
   - Toggle **"Enable Google Analytics"** to **OFF**
   - Click **"Create project"**
   - Wait ~30 seconds for project creation
   - Click **"Continue"** when ready

✅ **Checkpoint:** You should now see the Firebase Console dashboard

---

### **STEP 2: Enable Firestore Database** (3 minutes)

1. **Navigate to Firestore**
   - In the left sidebar, click **"Build"** → **"Firestore Database"**
   - Or click on **"Firestore Database"** card in the dashboard

2. **Create Database**
   - Click **"Create database"** button

3. **Choose Security Rules**
   - Select **"Start in production mode"** (more secure)
   - Click **"Next"**

   > **Note:** We'll use service account authentication (not public access)

4. **Choose Location**
   - Select a location close to you or your users:
     - **US:** `us-central1` (Iowa) - Good for US/Global
     - **Europe:** `europe-west1` (Belgium) - Good for Europe
     - **Asia:** `asia-southeast1` (Singapore) - Good for Asia
   - ⚠️ **Important:** Location cannot be changed later!
   - Click **"Enable"**
   - Wait ~1-2 minutes for Firestore to be created

✅ **Checkpoint:** You should see an empty Firestore Database with "Start collection" button

---

### **STEP 3: Create Service Account** (5 minutes)

This is your authentication key for uploading data from GitHub Actions and your API.

1. **Go to Project Settings**
   - Click the **⚙️ gear icon** next to "Project Overview" (top-left)
   - Click **"Project settings"**

2. **Navigate to Service Accounts**
   - Click the **"Service accounts"** tab (top menu)
   - You should see a section called "Firebase Admin SDK"

3. **Generate Private Key**
   - In the "Firebase Admin SDK" section, verify:
     - Language: **Python** (should be selected)
   - Click **"Generate new private key"** button
   - A popup will appear: **"Generate new private key?"**
   - Click **"Generate key"**

4. **Download JSON File**
   - A JSON file will download automatically
   - **Filename:** Something like `realtors-practice-xxxxx-firebase-adminsdk-xxxxx.json`
   - **Save this file securely!** 🔐

   ⚠️ **IMPORTANT SECURITY NOTES:**
   - This file gives FULL access to your Firebase project
   - **NEVER commit this to Git**
   - **NEVER share this file publicly**
   - Store it in a secure location on your computer

5. **Rename File (Optional but Recommended)**
   - Rename to something simple: `firebase-service-account.json`
   - Move to a secure folder: e.g., `C:\Users\DELL\firebase\`

✅ **Checkpoint:** You have downloaded `firebase-service-account.json`

---

### **STEP 4: Install Firebase Admin SDK** (2 minutes)

Open your terminal and install the Firebase Admin SDK for Python:

```bash
pip install firebase-admin
```

**Expected output:**
```
Successfully installed firebase-admin-6.x.x
Successfully installed google-cloud-firestore-2.x.x
...
```

✅ **Checkpoint:** Firebase Admin SDK installed successfully

---

### **STEP 5: Test Firebase Connection** (5 minutes)

Let's verify everything works before uploading data.

1. **Create Test Script**

Create a file `test_firebase.py`:

```python
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('C:/Users/DELL/firebase/firebase-service-account.json')
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# Test: Write a document
test_ref = db.collection('test').document('hello')
test_ref.set({
    'message': 'Hello from Python!',
    'timestamp': firestore.SERVER_TIMESTAMP
})

print("✓ Successfully connected to Firestore!")
print("✓ Test document created in 'test' collection")

# Test: Read the document back
doc = test_ref.get()
if doc.exists:
    print(f"✓ Document data: {doc.to_dict()}")
else:
    print("✗ Document not found")

# Cleanup: Delete test document
test_ref.delete()
print("✓ Test document deleted")
print("\n🎉 Firebase Firestore is working correctly!")
```

2. **Update Path in Script**
   - Change the path to match where you saved your JSON file:
     ```python
     cred = credentials.Certificate('YOUR_PATH_HERE/firebase-service-account.json')
     ```

3. **Run Test Script**
   ```bash
   python test_firebase.py
   ```

**Expected output:**
```
✓ Successfully connected to Firestore!
✓ Test document created in 'test' collection
✓ Document data: {'message': 'Hello from Python!', 'timestamp': ...}
✓ Test document deleted

🎉 Firebase Firestore is working correctly!
```

✅ **Checkpoint:** Firebase connection test passed!

---

### **STEP 6: Upload Your Scraped Data** (10 minutes)

Now let's upload your actual property data to Firestore.

1. **Make Sure Master Workbook Exists**
   ```bash
   # Check if file exists
   dir exports\cleaned\MASTER_CLEANED_WORKBOOK.xlsx
   ```

   If file doesn't exist, create it:
   ```bash
   python watcher.py --once
   ```

2. **Set Environment Variable**

   **Option A: Command Line (Temporary)**
   ```bash
   # Windows
   set FIREBASE_SERVICE_ACCOUNT=C:\Users\DELL\firebase\firebase-service-account.json

   # Linux/Mac
   export FIREBASE_SERVICE_ACCOUNT=/path/to/firebase-service-account.json
   ```

   **Option B: System Environment (Permanent)**
   - Right-click **"This PC"** → **"Properties"**
   - Click **"Advanced system settings"**
   - Click **"Environment Variables"**
   - Under "User variables", click **"New"**
   - Variable name: `FIREBASE_SERVICE_ACCOUNT`
   - Variable value: `C:\Users\DELL\firebase\firebase-service-account.json`
   - Click **OK** → **OK** → **OK**
   - **Restart your terminal**

3. **Run Upload Script**
   ```bash
   python scripts/upload_to_firestore.py
   ```

**Expected output:**
```
============================================================
Uploading to Firebase Firestore
============================================================

✓ Loaded Firebase credentials from C:\Users\DELL\firebase\firebase-service-account.json
Loading master workbook: exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
✓ Loaded 61 properties

  ✓ Uploaded 61/61 properties (100.0%)

============================================================
Upload Complete!
============================================================
✓ Successfully uploaded: 61 properties

Firestore collection: 'properties'
Total documents: 61
============================================================
```

4. **Verify in Firebase Console**
   - Go back to Firebase Console: https://console.firebase.google.com/
   - Click on your project
   - Click **"Firestore Database"** in left sidebar
   - You should see a collection named **"properties"**
   - Click on it to see your uploaded documents
   - Each document ID is the property hash
   - Click on any document to see its data

✅ **Checkpoint:** Your property data is now in Firestore!

---

### **STEP 7: Add to GitHub Secrets** (5 minutes)

For GitHub Actions to upload data automatically, we need to add credentials to GitHub Secrets.

1. **Copy Service Account JSON Content**
   - Open `firebase-service-account.json` in a text editor
   - Select ALL content (Ctrl+A)
   - Copy (Ctrl+C)

2. **Go to GitHub Repository**
   - Open your browser
   - Go to: https://github.com/YOUR_USERNAME/realtors_practice
   - Click **"Settings"** tab (top menu)

3. **Add Secret**
   - In left sidebar, expand **"Secrets and variables"**
   - Click **"Actions"**
   - Click **"New repository secret"** button

4. **Configure Secret**
   - **Name:** `FIREBASE_CREDENTIALS`
   - **Secret:** Paste the entire JSON content (from step 1)
   - Click **"Add secret"**

5. **Verify Secret Added**
   - You should see `FIREBASE_CREDENTIALS` in the list
   - The value will be hidden (showing as `***`)

✅ **Checkpoint:** GitHub Actions can now access Firebase!

---

### **STEP 8: Test API Endpoints** (Optional - 10 minutes)

You can test Firestore queries even without a frontend!

1. **Start API Server**
   ```bash
   set FIREBASE_SERVICE_ACCOUNT=C:\Users\DELL\firebase\firebase-service-account.json
   python api_server.py
   ```

2. **Test Query Endpoint (Using curl or Postman)**

   **Using curl:**
   ```bash
   curl -X POST http://localhost:5000/api/firestore/query ^
     -H "Content-Type: application/json" ^
     -d "{\"filters\": {\"price_max\": 50000000}, \"limit\": 10}"
   ```

   **Using Postman:**
   - Method: `POST`
   - URL: `http://localhost:5000/api/firestore/query`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "filters": {
         "price_max": 50000000,
         "bedrooms_min": 3
       },
       "limit": 10
     }
     ```
   - Click **"Send"**

   **Expected Response:**
   ```json
   {
     "results": [
       {
         "title": "3 Bedroom Apartment",
         "price": 35000000,
         "location": "Lekki Phase 1",
         "bedrooms": 3,
         ...
       }
     ],
     "count": 10,
     "filters_applied": {...}
   }
   ```

3. **Test Export Endpoint**
   ```bash
   curl -X POST http://localhost:5000/api/export/generate ^
     -H "Content-Type: application/json" ^
     -d "{\"format\": \"excel\", \"filters\": {\"price_max\": 50000000}}"
   ```

   **Expected Response:**
   ```json
   {
     "success": true,
     "download_url": "/api/export/download/properties_export_20251021_120000.xlsx",
     "filename": "properties_export_20251021_120000.xlsx",
     "record_count": 25,
     "file_size_mb": 0.15
   }
   ```

4. **Download Export**
   - Open browser
   - Go to: `http://localhost:5000/api/export/download/properties_export_20251021_120000.xlsx`
   - File should download automatically

✅ **Checkpoint:** API endpoints working with Firestore!

---

## 🎉 **Setup Complete!**

You now have:
- ✅ Firebase project created
- ✅ Firestore database enabled
- ✅ Service account credentials downloaded
- ✅ Firebase Admin SDK installed
- ✅ Connection tested successfully
- ✅ Property data uploaded to Firestore
- ✅ GitHub secrets configured
- ✅ API endpoints tested

---

## 📊 **What You Can Do Now (Without Frontend)**

### **1. Query Data via API**
```bash
curl -X POST http://localhost:5000/api/firestore/query \
  -H "Content-Type: application/json" \
  -d '{"filters": {"location": "Lekki"}, "limit": 20}'
```

### **2. Export Filtered Data**
```bash
curl -X POST http://localhost:5000/api/export/generate \
  -H "Content-Type: application/json" \
  -d '{"format": "excel", "filters": {"bedrooms_min": 3}}'
```

### **3. View Data in Firebase Console**
- Go to: https://console.firebase.google.com/
- Click your project
- Click "Firestore Database"
- Browse your properties

### **4. Manually Query in Firebase Console**
- Click "Start collection" → "properties"
- Click any document to view details
- Use "Filter" button to test queries
- Example: `price <= 50000000`

---

## 🔒 **Security Best Practices**

### **DO:**
- ✅ Keep `firebase-service-account.json` secure
- ✅ Add to `.gitignore` (already done in your project)
- ✅ Use GitHub Secrets for automation
- ✅ Use environment variables locally
- ✅ Regenerate key if accidentally exposed

### **DON'T:**
- ❌ Commit service account JSON to Git
- ❌ Share JSON file publicly
- ❌ Hardcode credentials in code
- ❌ Email/Slack the JSON file

---

## 🐛 **Troubleshooting**

### **Error: "Could not load the default credentials"**
**Solution:** Set environment variable
```bash
set FIREBASE_SERVICE_ACCOUNT=C:\path\to\firebase-service-account.json
```

### **Error: "Permission denied"**
**Solution:**
1. Check service account JSON is correct
2. Verify Firestore is enabled in Firebase Console
3. Regenerate service account key if needed

### **Error: "Module 'firebase_admin' not found"**
**Solution:**
```bash
pip install firebase-admin
```

### **Upload script shows 0 properties**
**Solution:**
1. Check master workbook exists:
   ```bash
   dir exports\cleaned\MASTER_CLEANED_WORKBOOK.xlsx
   ```
2. If not, create it:
   ```bash
   python watcher.py --once
   ```

---

## 📞 **Next Steps**

### **For You (Backend):**
1. ✅ Firebase setup complete
2. ⏳ Wait for scraper to finish (optional)
3. ⏳ Test GitHub Actions workflow
4. ⏳ Monitor Firestore usage

### **For Frontend Developer:**
When they're ready, share:
1. Firebase project ID: `realtors-practice`
2. API endpoint: `POST /api/firestore/query`
3. Documentation: `docs/FIRESTORE_EXPORT_GUIDE.md`
4. Example queries (from this guide)

They can:
- Query Firestore directly from frontend (after you add them to Firebase)
- Use your Flask API endpoints
- Download exports in any format

---

## 💰 **Cost Monitoring**

### **Check Usage**
1. Go to Firebase Console
2. Click "Usage and billing" (left sidebar under "Project settings")
3. View current usage:
   - Stored data: ~5-10 MB (way under 1 GB limit)
   - Reads: Track daily queries
   - Writes: Track daily uploads

### **Set Budget Alert (Optional)**
1. Click "Set budget alert"
2. Set alert at: $1/month
3. You'll get email if you approach this (unlikely)

---

## ✅ **Verification Checklist**

Before considering setup complete, verify:

- [ ] Firebase project created
- [ ] Firestore database enabled
- [ ] Service account JSON downloaded and saved securely
- [ ] `firebase-admin` Python package installed
- [ ] Test script runs successfully
- [ ] Master workbook uploaded to Firestore
- [ ] Can see data in Firebase Console
- [ ] GitHub secret `FIREBASE_CREDENTIALS` added
- [ ] API query endpoint tested and working
- [ ] API export endpoint tested and working
- [ ] Service account JSON added to `.gitignore`

**All checked?** 🎉 You're ready to use Firestore!

---

**Setup completed?** You can now query your property data from anywhere, export in multiple formats, and your frontend developer can integrate when ready!
