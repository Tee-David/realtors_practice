# Render Firebase Setup Guide

## Required Environment Variables in Render

To enable Firestore data access from your API, you need to set the Firebase credentials in Render.

### Step 1: Get Your Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **realtor-s-practice**
3. Click the gear icon (⚙️) → **Project settings**
4. Go to **Service accounts** tab
5. Click **"Generate new private key"**
6. Download the JSON file (e.g., `realtor-s-practice-firebase-adminsdk-fbsvc-xxxxxxxxxx.json`)
7. **IMPORTANT**: Keep this file secure - don't commit it to GitHub!

### Step 2: Add to Render Environment Variables

1. Go to your [Render Dashboard](https://dashboard.render.com/)
2. Select your **"real-estate-api"** web service
3. Go to **"Environment"** tab
4. Click **"Add Environment Variable"**

#### Add FIREBASE_CREDENTIALS:

- **Key**: `FIREBASE_CREDENTIALS`
- **Value**: Copy the **entire contents** of the JSON file you downloaded

  Example format:
  ```json
  {
    "type": "service_account",
    "project_id": "realtor-s-practice",
    "private_key_id": "xxx...",
    "private_key": "-----BEGIN PRIVATE KEY-----\nxxx...\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxxxx@realtor-s-practice.iam.gserviceaccount.com",
    "client_id": "xxx...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40realtor-s-practice.iam.gserviceaccount.com"
  }
  ```

5. Click **"Save Changes"**
6. Render will automatically redeploy with the new environment variable

### Step 3: Verify Setup

Once Render finishes redeploying, test the Firestore endpoints:

```bash
# Test dashboard (should return stats)
curl https://your-app-name.onrender.com/api/firestore/dashboard

# Test properties query
curl https://your-app-name.onrender.com/api/firestore/properties
```

If you get `"Firebase not configured"` error, check that:
1. The JSON is valid (no syntax errors)
2. The environment variable name is exactly `FIREBASE_CREDENTIALS`
3. Render has finished redeploying after adding the variable

---

## Available Firestore Endpoints

Once configured, your frontend can use these endpoints:

### Query & Search
- `GET /api/firestore/dashboard` - Dashboard statistics
- `GET /api/firestore/properties` - All properties (paginated)
- `POST /api/firestore/search` - Advanced search with filters
- `GET /api/firestore/top-deals` - Cheapest properties
- `GET /api/firestore/newest` - Newest listings
- `GET /api/firestore/premium` - Premium properties

### By Category
- `GET /api/firestore/for-sale` - For sale properties
- `GET /api/firestore/for-rent` - For rent properties
- `GET /api/firestore/land` - Land only
- `GET /api/firestore/properties/furnished` - Furnished properties
- `GET /api/firestore/properties/hot-deals` - Auto-tagged hot deals

### By Location
- `GET /api/firestore/properties/by-lga/<lga>` - Filter by LGA
- `GET /api/firestore/properties/by-area/<area>` - Filter by area

### By Site
- `GET /api/firestore/site/<site_key>` - Properties from specific site
- `GET /api/firestore/site-stats/<site_key>` - Site statistics

### Single Property
- `GET /api/firestore/property/<hash>` - Get property details by hash

### Export
- `POST /api/firestore/export` - Export to Excel/CSV/JSON

  Example request:
  ```json
  {
    "format": "excel",
    "filters": {
      "location": "Lekki",
      "property_type": "Flat / Apartment"
    },
    "limit": 1000
  }
  ```

---

## GitHub Actions Setup

The same credentials are needed for GitHub Actions to upload scraped data to Firestore.

### Add to GitHub Secrets

1. Go to your repository: https://github.com/Tee-David/realtors_practice
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `FIREBASE_CREDENTIALS`
5. Value: Same JSON content as used in Render
6. Click **"Add secret"**

This enables the workflow to upload scraped properties to Firestore automatically.

---

## Troubleshooting

### Error: "Firebase not configured"
- Check `FIREBASE_CREDENTIALS` is set in Render
- Verify JSON syntax is valid
- Ensure Render has redeployed after adding the variable

### Error: "Invalid credentials"
- Regenerate the service account key from Firebase Console
- Make sure you copied the entire JSON (including curly braces)
- Check for any copy-paste formatting issues

### Error: "Permission denied"
- Verify the service account has Firestore permissions
- In Firebase Console → IAM → ensure the service account has "Cloud Datastore User" role

---

## Security Notes

1. **NEVER** commit Firebase credentials to GitHub
2. The JSON file contains sensitive private keys
3. Rotate credentials regularly (every 90 days recommended)
4. Only use environment variables for production deployments
5. Keep `.gitignore` updated to exclude credential files

---

## Status Check

After setup, your API will have:
- ✅ Full Firestore query access
- ✅ Real-time property data from scrapes
- ✅ Export capabilities (Excel, CSV, JSON)
- ✅ Enterprise schema with 9 categories, 85+ fields
- ✅ Auto-tagging (premium, hot_deal, furnishing, etc.)
- ✅ Location intelligence (Lagos areas, LGAs, landmarks)
