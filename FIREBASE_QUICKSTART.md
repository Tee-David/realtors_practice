# Firebase Deployment - Quick Start

**⚡ Fast Firebase deployment guide - bookmark this page!**

---

## 🚀 5-Minute Setup

### 1. Prerequisites
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login
```

### 2. Create Firebase Project
```bash
# Go to https://console.firebase.google.com/
# Click "Add Project"
# Name: "nigeria-realtors-scraper"
# Enable Google Analytics (optional)
```

### 3. Initialize Firebase in Your Project
```bash
cd ~/realtors_practice

# Initialize Firebase
firebase init

# Select:
# - Functions (Cloud Functions for scheduled scraping)
# - Storage (for storing exports)
# - Hosting (optional - for frontend)

# Choose existing project: nigeria-realtors-scraper
# Language: Python
# Install dependencies: Yes
```

### 4. Install Dependencies
```bash
# Add to functions/requirements.txt
pip install -r requirements.txt
pip install firebase-admin google-cloud-storage
```

### 5. Deploy
```bash
# Deploy functions
firebase deploy --only functions

# Deploy storage rules
firebase deploy --only storage
```

---

## 📋 Essential Commands

```bash
# Deploy everything
firebase deploy

# Deploy functions only
firebase deploy --only functions

# Deploy storage only
firebase deploy --only storage

# View logs
firebase functions:log

# Test locally
firebase emulators:start
```

---

## 🔧 Quick Configuration

### Enable Required APIs
```bash
# Go to Google Cloud Console
# https://console.cloud.google.com/

# Enable these APIs:
# - Cloud Functions API
# - Cloud Storage API
# - Cloud Scheduler API
# - Cloud Build API
```

### Set Environment Variables
```bash
# Set Firebase config
firebase functions:config:set \
  scraper.headless=true \
  scraper.page_cap=20 \
  scraper.geocode=true
```

### Create Storage Bucket
```bash
# Bucket created automatically:
# your-project-id.appspot.com
```

---

## 📊 Costs Estimate

**Free Tier (Spark Plan)**:
- ❌ Cloud Functions: NOT available
- ✅ Storage: 1GB free
- ❌ Cloud Scheduler: NOT available

**Blaze Plan (Pay-as-you-go)**:
- ✅ Cloud Functions: First 2M invocations free
- ✅ Storage: First 5GB free
- ✅ Cloud Scheduler: First 3 jobs free

**Estimated Monthly Cost for This Scraper**:
- Cloud Functions: ~$5-10/month (1 daily run)
- Storage: ~$0.05/month (500MB)
- Scheduler: Free (1 job)
- **Total**: ~$5-10/month

---

## 🕒 Schedule Scraping

### Using Cloud Scheduler
```bash
# Create scheduled function (in functions/main.py)
# Automatically triggers daily at 3 AM

# Deploy
firebase deploy --only functions

# Scheduler created automatically
```

### Manual Trigger
```bash
# Trigger via HTTP
curl https://your-region-your-project.cloudfunctions.net/scrapeSites
```

---

## 📁 Data Access

### Download Exports
```bash
# Using gsutil
gsutil -m cp -r gs://your-project-id.appspot.com/exports ./local-exports

# Or download via Firebase Console:
# https://console.firebase.google.com/project/your-project/storage
```

### Access via URL
```bash
# Public URLs (if made public):
# https://storage.googleapis.com/your-project-id.appspot.com/exports/cleaned/master.xlsx
```

---

## 🔍 Monitoring

### View Logs
```bash
# Real-time logs
firebase functions:log --only scrapeSites

# Or in console:
# https://console.firebase.google.com/project/your-project/functions/logs
```

### Check Storage Usage
```bash
# Firebase Console → Storage
# Shows files, sizes, and usage
```

---

## 🆘 Troubleshooting Quick Fixes

### "Firebase CLI not found"
```bash
npm install -g firebase-tools
```

### "Billing account required"
```bash
# Upgrade to Blaze plan in Firebase Console
# Settings → Usage and Billing → Modify Plan
```

### "Function timeout"
```bash
# Increase timeout in functions/main.py
# Default: 60s, Max: 540s (9 minutes)
```

### "Out of memory"
```bash
# Increase memory allocation
# Default: 256MB, Options: 512MB, 1GB, 2GB
```

---

## 📚 Next Steps

1. **Deploy Functions**: `firebase deploy --only functions`
2. **Set Up Scheduler**: Enable Cloud Scheduler in console
3. **Configure Storage Rules**: Secure your data
4. **Monitor Costs**: Check Firebase Console → Usage

---

## 🔗 Important Links

- **Firebase Console**: https://console.firebase.google.com/
- **Cloud Console**: https://console.cloud.google.com/
- **Pricing**: https://firebase.google.com/pricing
- **Full Guide**: [docs/FIREBASE_DEPLOYMENT.md](docs/FIREBASE_DEPLOYMENT.md)

---

**Deployment Time**: 15-30 minutes
**Monthly Cost**: ~$5-10
**Status**: Production Ready ✅
