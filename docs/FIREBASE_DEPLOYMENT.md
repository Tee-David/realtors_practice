# Firebase Deployment Guide - Step by Step

**Complete guide to deploy the Nigerian Real Estate Scraper on Firebase Cloud Platform.**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Firebase Project Setup](#step-1-firebase-project-setup)
4. [Install Firebase CLI](#step-2-install-firebase-cli)
5. [Project Configuration](#step-3-project-configuration)
6. [Deploy Cloud Functions](#step-4-deploy-cloud-functions)
7. [Configure Cloud Storage](#step-5-configure-cloud-storage)
8. [Schedule Automated Scraping](#step-6-schedule-automated-scraping)
9. [Monitoring & Logs](#step-7-monitoring--logs)
10. [Cost Management](#step-8-cost-management)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

Firebase (Google Cloud Platform) provides:
- ✅ **Cloud Functions** - Serverless scraper execution
- ✅ **Cloud Storage** - Unlimited data storage
- ✅ **Cloud Scheduler** - Automated daily/weekly runs
- ✅ **Scalability** - Auto-scales based on demand
- ✅ **Monitoring** - Built-in logs and metrics

**Why Firebase?**
- No server management (serverless)
- Global CDN for data access
- Pay only for what you use
- Automatic backups and versioning
- Easy integration with frontends

---

## Prerequisites

Before starting, you need:

- ✅ Google account (Gmail)
- ✅ Credit/debit card (for Blaze plan - required for Cloud Functions)
- ✅ Node.js installed (for Firebase CLI)
- ✅ Basic command line knowledge
- ✅ Your scraper project code

**Important**: Cloud Functions requires the **Blaze (Pay-as-you-go)** plan, but costs are minimal (~$5-10/month for this scraper).

---

## Step 1: Firebase Project Setup

### 1.1 Create Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Click "Add Project"**
3. **Enter Project Details**:
   - **Project Name**: `nigeria-realtors-scraper` (or your choice)
   - **Project ID**: Auto-generated (e.g., `nigeria-realtors-scraper-abc123`)
   - **Google Analytics**: Enable (optional, recommended for monitoring)
4. **Click "Create Project"**
5. Wait for setup to complete (~30 seconds)
6. **Click "Continue"**

### 1.2 Upgrade to Blaze Plan

**Important**: Cloud Functions require Blaze plan.

1. **In Firebase Console**, click ⚙️ **Settings** (bottom left)
2. **Go to "Usage and Billing"**
3. **Click "Modify Plan"**
4. **Select "Blaze Plan"**
5. **Add Billing Account**:
   - Enter credit/debit card info
   - Set spending limit (optional): $20/month (safety cap)
6. **Confirm upgrade**

✅ **Free tier included**: 2M function invocations, 5GB storage, 10GB bandwidth per month.

### 1.3 Enable Required APIs

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project**: `nigeria-realtors-scraper`
3. **Go to "APIs & Services" → "Enable APIs and Services"**
4. **Enable these APIs** (search and click "Enable"):
   - ✅ Cloud Functions API
   - ✅ Cloud Storage API
   - ✅ Cloud Scheduler API
   - ✅ Cloud Build API
   - ✅ Cloud Logging API

---

## Step 2: Install Firebase CLI

### 2.1 Install Node.js (if not installed)

**Windows**:
1. Download from https://nodejs.org/ (LTS version)
2. Run installer
3. Verify: Open Command Prompt and run:
   ```bash
   node --version
   npm --version
   ```

**Mac/Linux**:
```bash
# Using Homebrew (Mac)
brew install node

# Using apt (Ubuntu/Debian)
sudo apt update
sudo apt install nodejs npm

# Verify
node --version
npm --version
```

### 2.2 Install Firebase CLI

**All Platforms**:
```bash
# Install Firebase CLI globally
npm install -g firebase-tools

# Verify installation
firebase --version
```

You should see version number (e.g., `13.0.0`).

### 2.3 Login to Firebase

```bash
# Login via browser
firebase login

# A browser window will open
# Select your Google account
# Click "Allow"
```

✅ **Success message**: "Success! Logged in as your-email@gmail.com"

### 2.4 Verify Project Access

```bash
# List your Firebase projects
firebase projects:list

# You should see your project
```

---

## Step 3: Project Configuration

### 3.1 Prepare Your Project Structure

```bash
# Navigate to your project
cd C:\Users\DELL\Desktop\Dynamic realtors_practice

# Your current structure
# realtors_practice/
# ├── main.py
# ├── watcher.py
# ├── core/
# ├── parsers/
# ├── config.yaml
# └── requirements.txt
```

### 3.2 Initialize Firebase

```bash
# Initialize Firebase in your project
firebase init
```

**Interactive Setup**:

1. **Which Firebase features?** (Use spacebar to select, Enter to confirm)
   - ✅ **Functions** (Cloud Functions for scheduled scraping)
   - ✅ **Storage** (Cloud Storage for exports)
   - ⬜ Hosting (optional - if you want to host a frontend)
   - Press `Enter`

2. **Select a default Firebase project**:
   - Choose: `Use an existing project`
   - Select: `nigeria-realtors-scraper` (your project)

3. **Functions Setup**:
   - **Language**: Select `Python`
   - **Source directory**: Press `Enter` (use default `functions`)
   - **Install dependencies**: `Yes`

4. **Storage Setup**:
   - **Storage rules file**: Press `Enter` (use default `storage.rules`)

5. **Hosting Setup** (if selected):
   - **Public directory**: Press `Enter` (skip or use default)

✅ **Firebase initialization complete!**

### 3.3 Project Structure After Init

```
realtors_practice/
├── main.py                  # Your scraper (will be moved)
├── watcher.py              # Your watcher (will be moved)
├── core/                   # Your core modules
├── parsers/                # Your parsers
├── config.yaml             # Your config
├── requirements.txt        # Your dependencies
│
├── functions/              # NEW - Firebase Functions
│   ├── main.py            # Cloud Function entry point (we'll create)
│   ├── requirements.txt   # Function dependencies (we'll update)
│   └── ...
│
├── storage.rules          # NEW - Storage security rules
├── firebase.json          # NEW - Firebase config
└── .firebaserc           # NEW - Project config
```

### 3.4 Create Cloud Function

Create `functions/main.py`:

```python
# functions/main.py
"""
Firebase Cloud Functions for Nigeria Real Estate Scraper.
"""

import os
import sys
from pathlib import Path
from firebase_functions import scheduler_fn, https_fn
from firebase_admin import initialize_app, storage
import logging

# Initialize Firebase
initialize_app()

# Add parent directory to path to import scraper modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import run_scraper
from watcher import process_exports

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@scheduler_fn.on_schedule(schedule="0 3 * * *")  # Daily at 3 AM UTC
def scheduled_scrape(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled scraper function - runs daily at 3 AM.
    """
    logger.info("Starting scheduled scrape...")

    try:
        # Set environment variables for scraper
        os.environ['RP_HEADLESS'] = '1'
        os.environ['RP_GEOCODE'] = '1'
        os.environ['RP_PAGE_CAP'] = '20'

        # Run scraper
        logger.info("Running scraper...")
        results = run_scraper()

        # Process exports with watcher
        logger.info("Processing exports...")
        process_exports()

        # Upload to Cloud Storage
        logger.info("Uploading to Cloud Storage...")
        upload_exports_to_storage()

        logger.info(f"Scrape complete! Results: {results}")

    except Exception as e:
        logger.error(f"Scrape failed: {e}", exc_info=True)
        raise


@https_fn.on_request()
def scrape_sites(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP-triggered scraper function.

    Trigger via:
    curl https://your-region-your-project.cloudfunctions.net/scrape_sites
    """
    logger.info("Manual scrape triggered via HTTP...")

    try:
        # Set environment variables
        os.environ['RP_HEADLESS'] = '1'
        os.environ['RP_GEOCODE'] = '1'

        # Get parameters from request
        page_cap = req.args.get('page_cap', '20')
        os.environ['RP_PAGE_CAP'] = page_cap

        # Run scraper
        results = run_scraper()

        # Process exports
        process_exports()

        # Upload to storage
        upload_exports_to_storage()

        return https_fn.Response(
            f"Scrape complete! Results: {results}",
            status=200
        )

    except Exception as e:
        logger.error(f"Scrape failed: {e}", exc_info=True)
        return https_fn.Response(f"Error: {str(e)}", status=500)


def upload_exports_to_storage():
    """Upload exports to Firebase Cloud Storage."""
    bucket = storage.bucket()

    # Upload raw site exports
    exports_dir = Path('exports/sites')
    if exports_dir.exists():
        for site_dir in exports_dir.iterdir():
            if site_dir.is_dir():
                for file_path in site_dir.glob('*'):
                    if file_path.is_file():
                        blob_path = f"exports/sites/{site_dir.name}/{file_path.name}"
                        blob = bucket.blob(blob_path)
                        blob.upload_from_filename(str(file_path))
                        logger.info(f"Uploaded: {blob_path}")

    # Upload cleaned data
    cleaned_dir = Path('exports/cleaned')
    if cleaned_dir.exists():
        for file_path in cleaned_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(cleaned_dir)
                blob_path = f"exports/cleaned/{relative_path}"
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(str(file_path))
                logger.info(f"Uploaded: {blob_path}")

    logger.info("All exports uploaded to Cloud Storage")
```

### 3.5 Update Functions Requirements

Update `functions/requirements.txt`:

```txt
# Firebase dependencies
firebase-functions>=0.4.0
firebase-admin>=6.2.0
google-cloud-storage>=2.10.0

# Scraper dependencies (from your main requirements.txt)
pyyaml>=6.0
beautifulsoup4>=4.11.0
openpyxl>=3.1.0
playwright>=1.40.0
requests>=2.28.0
lxml>=4.9.0
python-dateutil>=2.8.0
pandas>=2.0.0
pyarrow>=12.0.0

# Additional dependencies
flask>=3.0.0
flask-cors>=4.0.0
```

### 3.6 Copy Your Code to Functions

```bash
# Copy core modules to functions
cp -r core functions/
cp -r parsers functions/
cp config.yaml functions/
cp config.example.yaml functions/

# Create exports directories
mkdir -p functions/exports/sites
mkdir -p functions/exports/cleaned
mkdir -p functions/logs
```

### 3.7 Modify main.py for Cloud Functions

Create `functions/scraper_wrapper.py`:

```python
# functions/scraper_wrapper.py
"""
Wrapper to make main.py compatible with Cloud Functions.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def run_scraper():
    """Run the scraper and return results."""
    # Import your main scraper logic
    from main import main as scraper_main

    # Run scraper
    results = scraper_main()

    return results

def process_exports():
    """Process exports with watcher."""
    from watcher import main as watcher_main

    # Run watcher
    watcher_main(['--once'])
```

---

## Step 4: Deploy Cloud Functions

### 4.1 Configure Function Settings

Edit `firebase.json`:

```json
{
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "runtime": "python311",
      "region": "us-central1",
      "timeout": "540s",
      "memory": "1GB",
      "maxInstances": 3
    }
  ],
  "storage": {
    "rules": "storage.rules"
  }
}
```

**Settings Explained**:
- `runtime`: Python 3.11 (latest)
- `timeout`: 540s (9 minutes max for scraping)
- `memory`: 1GB (enough for scraping + data processing)
- `maxInstances`: 3 (limit concurrent runs to control costs)

### 4.2 Deploy Functions

```bash
# Deploy all functions
firebase deploy --only functions

# Or deploy specific function
firebase deploy --only functions:scheduled_scrape
firebase deploy --only functions:scrape_sites
```

**What happens**:
1. Code is uploaded to Google Cloud
2. Dependencies are installed
3. Functions are deployed
4. URLs are generated

✅ **Success output**:
```
✔  functions[scheduled_scrape(us-central1)] Deployed successfully
✔  functions[scrape_sites(us-central1)] Deployed successfully

Function URL (scrape_sites): https://us-central1-nigeria-realtors-scraper.cloudfunctions.net/scrape_sites
```

**Save this URL** - you can trigger scraping manually with it!

### 4.3 Test Function

```bash
# Trigger HTTP function manually
curl https://us-central1-your-project.cloudfunctions.net/scrape_sites

# Or test locally first
firebase emulators:start
```

---

## Step 5: Configure Cloud Storage

### 5.1 Storage Rules

Edit `storage.rules`:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {

    // Exports - Public read, authenticated write
    match /exports/{allPaths=**} {
      allow read: if true;  // Anyone can download
      allow write: if request.auth != null;  // Only authenticated users/functions can upload
    }

    // Logs - Private (only functions can access)
    match /logs/{allPaths=**} {
      allow read, write: if false;  // No public access
    }
  }
}
```

### 5.2 Deploy Storage Rules

```bash
firebase deploy --only storage
```

### 5.3 View Storage in Console

1. Go to **Firebase Console** → **Storage**
2. You'll see your bucket: `your-project-id.appspot.com`
3. After first scrape, files will appear in `exports/`

---

## Step 6: Schedule Automated Scraping

### 6.1 Cloud Scheduler (Automatic)

The `@scheduler_fn.on_schedule` decorator automatically creates a Cloud Scheduler job when you deploy.

**Default Schedule**: Daily at 3 AM UTC

**View/Edit Schedule**:
1. Go to **Google Cloud Console**
2. Navigate to **Cloud Scheduler**
3. You'll see: `firebase-schedule-scheduled_scrape-us-central1`
4. Click to edit schedule

### 6.2 Custom Schedules

Edit `functions/main.py`:

```python
# Daily at 3 AM UTC
@scheduler_fn.on_schedule(schedule="0 3 * * *")

# Every 12 hours
@scheduler_fn.on_schedule(schedule="0 */12 * * *")

# Weekly on Sundays at 2 AM
@scheduler_fn.on_schedule(schedule="0 2 * * 0")

# Weekdays only at 4 AM
@scheduler_fn.on_schedule(schedule="0 4 * * 1-5")
```

After changing, redeploy:
```bash
firebase deploy --only functions
```

### 6.3 Manual Triggers

**Via HTTP**:
```bash
curl https://us-central1-your-project.cloudfunctions.net/scrape_sites?page_cap=10
```

**Via Firebase Console**:
1. Go to **Firebase Console** → **Functions**
2. Find `scrape_sites`
3. Click **"..."** → **"Test function"**
4. Click **"Run"**

**Via gcloud CLI**:
```bash
gcloud functions call scrape_sites --region us-central1
```

---

## Step 7: Monitoring & Logs

### 7.1 View Logs in Firebase Console

1. Go to **Firebase Console** → **Functions**
2. Click on function name (e.g., `scheduled_scrape`)
3. Click **"Logs"** tab
4. See real-time execution logs

### 7.2 View Logs via CLI

```bash
# Real-time logs
firebase functions:log --only scheduled_scrape

# Last 100 lines
firebase functions:log --limit 100

# Filter by severity
firebase functions:log --only scheduled_scrape --filter "severity>=ERROR"
```

### 7.3 Cloud Logging (Advanced)

1. Go to **Google Cloud Console** → **Logging** → **Logs Explorer**
2. Filter by:
   - Resource: `Cloud Function`
   - Function name: `scheduled_scrape`
3. Advanced queries:
   ```
   resource.type="cloud_function"
   resource.labels.function_name="scheduled_scrape"
   severity="ERROR"
   ```

### 7.4 Set Up Alerts

1. **Cloud Console** → **Monitoring** → **Alerting**
2. **Create Policy**
3. **Condition**: "Cloud Function Error Rate"
4. **Notification**: Email/SMS when errors spike

---

## Step 8: Cost Management

### 8.1 Monitor Costs

1. **Firebase Console** → **Settings** → **Usage and Billing**
2. View costs by service:
   - Cloud Functions invocations
   - Storage usage
   - Bandwidth (downloads)

### 8.2 Set Budget Alerts

1. **Google Cloud Console** → **Billing** → **Budgets & Alerts**
2. **Create Budget**:
   - Amount: $20/month (or your limit)
   - Email alerts at: 50%, 75%, 90%, 100%

### 8.3 Optimize Costs

**Reduce Function Execution Time**:
```yaml
# config.yaml - reduce pages
global_settings:
  pagination:
    max_pages: 15  # Instead of 30
```

**Reduce Memory**:
```json
// firebase.json
"memory": "512MB"  // Instead of 1GB if scraper works with less
```

**Limit Sites**:
```bash
# Enable only high-priority sites
python scripts/enable_sites.py npc propertypro jiji
```

**Use Storage Lifecycle Rules**:
```javascript
// Delete old exports after 30 days
// Firebase Console → Storage → Lifecycle
```

### 8.4 Estimated Monthly Costs

**Typical Usage** (1 daily scrape, 5-10 sites, 20 pages each):

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Functions | 30 invocations/month × 2 min each | ~$0.20 |
| Cloud Functions Memory | 1GB × 60 min/month | ~$0.10 |
| Cloud Storage | 500MB stored | ~$0.01 |
| Storage Bandwidth | 2GB downloads | ~$0.24 |
| Cloud Scheduler | 1 job | Free |
| **Total** | | **~$0.55/month** |

**Heavy Usage** (1 daily scrape, 50 sites, 30 pages each):

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Functions | 30 invocations × 9 min each | ~$1.50 |
| Cloud Functions Memory | 1GB × 270 min/month | ~$0.45 |
| Cloud Storage | 2GB stored | ~$0.05 |
| Storage Bandwidth | 10GB downloads | ~$1.20 |
| **Total** | | **~$3.20/month** |

---

## Troubleshooting

### Problem 1: "Billing account required"

**Error**: "Cloud Functions requires Blaze plan"

**Solution**:
1. Firebase Console → Settings → Usage and Billing
2. Click "Modify Plan"
3. Select "Blaze Plan"
4. Add payment method

### Problem 2: "playwright: command not found"

**Error**: Function fails when trying to use Playwright

**Solution**: Use requests-only mode in `functions/config.yaml`:
```yaml
global_settings:
  scraper:
    fallback_chain: ["requests"]
```

Or install Playwright in Cloud Function:
```bash
# Add to functions/requirements.txt
playwright==1.40.0

# Then in functions/main.py (before scraping)
from playwright.sync_api import sync_playwright
import subprocess
subprocess.run(["playwright", "install", "chromium"])
```

### Problem 3: "Function timeout"

**Error**: "Function execution took longer than 540000ms and was aborted"

**Solution**:
1. Reduce pages per site:
   ```yaml
   # config.yaml
   max_pages: 10
   ```

2. Or split scraping across multiple functions:
   ```python
   # One function per site category
   @scheduler_fn.on_schedule(schedule="0 3 * * 1")  # Monday
   def scrape_batch_1(event):
       # Scrape sites 1-10

   @scheduler_fn.on_schedule(schedule="0 3 * * 2")  # Tuesday
   def scrape_batch_2(event):
       # Scrape sites 11-20
   ```

### Problem 4: "Out of memory"

**Error**: "Memory limit exceeded"

**Solution**:
1. Increase memory in `firebase.json`:
   ```json
   "memory": "2GB"
   ```

2. Or reduce concurrent sites:
   ```bash
   # Enable fewer sites
   python scripts/enable_sites.py npc propertypro jiji
   ```

### Problem 5: "Permission denied" (Storage)

**Error**: "Failed to upload to Cloud Storage: Permission denied"

**Solution**:
1. Check storage rules allow function writes
2. Verify Firebase Admin SDK is initialized:
   ```python
   from firebase_admin import initialize_app
   initialize_app()
   ```

### Problem 6: "Function not deploying"

**Error**: "Deployment failed"

**Solutions**:
```bash
# Clear cache and redeploy
rm -rf functions/__pycache__
firebase deploy --only functions --force

# Check for syntax errors
cd functions
python -m py_compile main.py

# View deployment logs
firebase functions:log
```

### Problem 7: "Module not found"

**Error**: "ModuleNotFoundError: No module named 'core'"

**Solution**:
```bash
# Ensure all modules are in functions/
ls -la functions/
# Should show: core/, parsers/, config.yaml

# Update sys.path in functions/main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

---

## Data Access & Download

### Download Exports

**Via gsutil CLI**:
```bash
# Install gsutil
pip install gsutil

# Download all exports
gsutil -m cp -r gs://your-project-id.appspot.com/exports ./local-exports

# Download specific site
gsutil cp gs://your-project-id.appspot.com/exports/cleaned/npc/* ./npc-data/
```

**Via Firebase Console**:
1. Firebase Console → Storage
2. Navigate to `exports/cleaned/`
3. Click file → Download

**Via Public URL** (if made public):
```
https://storage.googleapis.com/your-project-id.appspot.com/exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
```

---

## Security Best Practices

### 1. Secure API Keys

Never commit Firebase credentials:
```bash
# .gitignore
firebase-credentials.json
.firebase/
functions/.env
```

### 2. Restrict Storage Access

```javascript
// storage.rules - restrict by IP or auth
match /exports/{allPaths=**} {
  allow read: if request.auth != null;  // Require authentication
  allow write: if false;  // Only functions can write
}
```

### 3. Environment Variables

Store secrets in Firebase config:
```bash
# Set secrets
firebase functions:config:set scraperapi.key="your-api-key"

# Access in code
import os
api_key = os.environ.get('SCRAPERAPI_KEY')
```

### 4. IAM Permissions

Limit who can deploy:
1. Cloud Console → IAM & Admin
2. Add member with role: `Cloud Functions Developer`

---

## Next Steps

Once deployed:

1. **Monitor first run**: Check logs after scheduled scrape
2. **Verify exports**: Check Storage for scraped data
3. **Set up alerts**: Email notifications for errors
4. **Optimize costs**: Adjust memory/timeout based on actual usage
5. **Optional - API**: Deploy REST API for frontend integration
6. **Optional - Frontend**: Deploy Next.js frontend to Firebase Hosting

---

## Summary Checklist

- [ ] Firebase project created
- [ ] Upgraded to Blaze plan
- [ ] Firebase CLI installed and logged in
- [ ] Project initialized with Functions + Storage
- [ ] `functions/main.py` created
- [ ] `functions/requirements.txt` updated
- [ ] Code copied to `functions/` directory
- [ ] `firebase.json` configured
- [ ] Functions deployed successfully
- [ ] Storage rules deployed
- [ ] Cloud Scheduler job created
- [ ] Test scrape successful
- [ ] Logs monitored for errors
- [ ] Exports visible in Storage
- [ ] Budget alerts configured

---

**Deployment Status**: Production Ready ✅

**Estimated Setup Time**: 30-60 minutes

**Monthly Cost**: $1-5 (typical usage)

**Last Updated**: 2025-10-18
