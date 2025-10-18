# Platform Compatibility Guide

## Overview

This document outlines compatibility and deployment information for the Nigerian Real Estate Scraper on **Firebase Cloud Platform**.

---

## ✅ Firebase Cloud Platform Deployment

### Compatibility Status

**✅ FULLY COMPATIBLE** with Firebase Cloud Platform (Google Cloud).

The scraper runs as serverless Cloud Functions with:
- **Cloud Functions** - Serverless Python execution
- **Cloud Storage** - Unlimited data storage
- **Cloud Scheduler** - Automated scheduled scraping
- **Cloud Logging** - Real-time logs and monitoring
- **Scalability** - Auto-scales based on demand

### Why Firebase?

**Advantages**:
- ✅ **No Server Management** - Fully serverless, no maintenance
- ✅ **Global CDN** - Fast data access worldwide
- ✅ **Auto-Scaling** - Handles traffic spikes automatically
- ✅ **Cost-Effective** - Pay only for actual usage (~$1-5/month)
- ✅ **Built-in Monitoring** - Logs, metrics, and alerts included
- ✅ **Automatic Backups** - Data versioning and lifecycle management
- ✅ **Easy Frontend Integration** - Firebase SDK for web/mobile apps

**Use Cases**:
- Scheduled daily/weekly scraping
- Data storage and sharing via CDN
- Integration with web/mobile frontends
- Automated data processing pipelines

---

## 📚 Deployment Documentation

For complete Firebase deployment instructions, see:

**Quick Start**: [FIREBASE_QUICKSTART.md](../FIREBASE_QUICKSTART.md)
- Fast setup guide (15-30 minutes)
- Essential commands
- Cost estimates
- Troubleshooting

**Complete Guide**: [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md)
- Step-by-step walkthrough
- Detailed explanations
- Advanced configuration
- Security best practices
- Monitoring and optimization

---

## 🏗️ Architecture

### Firebase Deployment Flow

```
┌─────────────────────────────────────────────────────┐
│                Firebase Cloud Platform               │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────┐        ┌─────────────────┐   │
│  │  Cloud Scheduler │─────▶  │ Cloud Functions │   │
│  │  (Cron jobs)     │        │ (Scraper)       │   │
│  └──────────────────┘        └────────┬────────┘   │
│                                        │             │
│                                        ▼             │
│                              ┌─────────────────┐    │
│                              │  Cloud Storage  │    │
│                              │  (Exports)      │    │
│                              └─────────────────┘    │
│                                                       │
│  ┌──────────────────┐        ┌─────────────────┐   │
│  │  Cloud Logging   │        │  Cloud Monitor  │   │
│  │  (Logs)          │        │  (Metrics)      │   │
│  └──────────────────┘        └─────────────────┘   │
│                                                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Frontend/API    │
              │  (Next.js/React) │
              └──────────────────┘
```

### Components

**1. Cloud Functions**
- Python 3.11 runtime
- Serverless execution
- Automatic scaling
- 540s max timeout (9 minutes)
- 256MB - 2GB memory options

**2. Cloud Storage**
- Object storage (similar to S3)
- Unlimited capacity
- Global CDN delivery
- Versioning support
- Lifecycle policies

**3. Cloud Scheduler**
- Cron-based scheduling
- Reliable triggers
- Timezone support
- Retry on failure

**4. Cloud Logging**
- Real-time log streaming
- Advanced filtering
- Error tracking
- Log retention (30 days free tier)

---

## 💰 Cost Analysis

### Firebase Pricing Plans

**Spark Plan (Free)**:
- ❌ Cloud Functions: NOT available
- ✅ Cloud Storage: 1GB free
- ❌ Cloud Scheduler: NOT available
- **Use case**: Testing, development only

**Blaze Plan (Pay-as-you-go)**:
- ✅ Cloud Functions: First 2M invocations free, then $0.40/million
- ✅ Cloud Storage: First 5GB free, then $0.026/GB/month
- ✅ Cloud Scheduler: First 3 jobs free, then $0.10/job/month
- ✅ Cloud Build: First 120 build-minutes free per day
- **Use case**: Production deployment (REQUIRED)

### Cost Breakdown

**Light Usage** (1 daily scrape, 5-10 sites, 20 pages each):

| Service | Monthly Usage | Free Tier | Billable | Cost |
|---------|---------------|-----------|----------|------|
| Cloud Functions (invocations) | 30 | 2M | 0 | $0.00 |
| Cloud Functions (compute time) | 60 GB-seconds | 400K | 0 | $0.00 |
| Cloud Functions (memory) | 60 GB-seconds | 400K | 0 | $0.00 |
| Cloud Storage (storage) | 500MB | 5GB | 0 | $0.00 |
| Cloud Storage (operations) | 150 | 50K | 0 | $0.00 |
| Cloud Storage (egress) | 2GB | 1GB | 1GB | $0.12 |
| Cloud Scheduler | 1 job | 3 | 0 | $0.00 |
| **TOTAL** | | | | **~$0.12/month** |

**Medium Usage** (1 daily scrape, 20-30 sites, 30 pages each):

| Service | Monthly Usage | Free Tier | Billable | Cost |
|---------|---------------|-----------|----------|------|
| Cloud Functions (invocations) | 30 | 2M | 0 | $0.00 |
| Cloud Functions (compute time) | 180 GB-seconds | 400K | 0 | $0.00 |
| Cloud Storage (storage) | 1.5GB | 5GB | 0 | $0.00 |
| Cloud Storage (egress) | 5GB | 1GB | 4GB | $0.48 |
| Cloud Scheduler | 1 job | 3 | 0 | $0.00 |
| **TOTAL** | | | | **~$0.50/month** |

**Heavy Usage** (1 daily scrape, all 50 sites, 30 pages each):

| Service | Monthly Usage | Free Tier | Billable | Cost |
|---------|---------------|-----------|----------|------|
| Cloud Functions (invocations) | 30 | 2M | 0 | $0.00 |
| Cloud Functions (compute time) | 540 GB-seconds | 400K | 140K | $0.20 |
| Cloud Storage (storage) | 3GB | 5GB | 0 | $0.00 |
| Cloud Storage (egress) | 15GB | 1GB | 14GB | $1.68 |
| Cloud Scheduler | 1 job | 3 | 0 | $0.00 |
| **TOTAL** | | | | **~$1.90/month** |

### Cost Optimization Tips

**1. Reduce Function Execution Time**:
```yaml
# config.yaml - Limit pages per site
global_settings:
  pagination:
    max_pages: 15  # Instead of 30
```

**2. Reduce Memory Allocation**:
```json
// firebase.json
"memory": "512MB"  // Instead of 1GB if possible
```

**3. Use Storage Lifecycle Policies**:
```javascript
// Delete old exports after 30 days
// Firebase Console → Storage → Lifecycle
{
  "action": {"type": "Delete"},
  "condition": {"age": 30}
}
```

**4. Compress Exports**:
```python
# Use Parquet instead of CSV (smaller files)
# Watcher already does this in exports/cleaned/
```

**5. Limit Geocoding**:
```bash
export RP_MAX_GEOCODES=100  # Instead of 200
```

**6. Set Budget Alerts**:
- Firebase Console → Settings → Usage and Billing
- Set budget: $10/month
- Alert at: 50%, 75%, 90%, 100%

---

## 🔒 Security Best Practices

### 1. Environment Variables

**Never hard-code secrets**:
```python
# BAD
api_key = "abc123xyz"

# GOOD
import os
api_key = os.getenv('SCRAPERAPI_KEY')
```

**Set via Firebase CLI**:
```bash
firebase functions:config:set scraperapi.key="your-key"
```

### 2. Storage Security Rules

**Restrict access** in `storage.rules`:
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Public read, authenticated write only
    match /exports/{allPaths=**} {
      allow read: if true;  // Anyone can download
      allow write: if request.auth != null;  // Only functions
    }

    // Or restrict read to authenticated users
    match /exports/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }

    // Private logs
    match /logs/{allPaths=**} {
      allow read, write: if false;  // No public access
    }
  }
}
```

### 3. IAM Permissions

**Principle of least privilege**:

1. Go to **Cloud Console** → **IAM & Admin**
2. Limit who can deploy:
   - `Cloud Functions Developer` - Can deploy functions
   - `Storage Admin` - Can manage storage
3. Use service accounts for CI/CD

### 4. .gitignore Sensitive Files

```bash
# .gitignore
firebase-credentials.json
.firebase/
functions/.env
*.key
*.pem
serviceAccountKey.json
```

### 5. Enable VPC Service Controls (Advanced)

For high-security requirements:
1. Cloud Console → VPC Service Controls
2. Create perimeter around Firebase services
3. Restrict API access to trusted networks

---

## 📊 Monitoring & Alerts

### Cloud Logging

**View Logs**:
1. Firebase Console → Functions → Logs
2. Cloud Console → Logging → Logs Explorer

**Filter Logs**:
```
resource.type="cloud_function"
resource.labels.function_name="scheduled_scrape"
severity="ERROR"
```

### Cloud Monitoring

**Create Dashboards**:
1. Cloud Console → Monitoring → Dashboards
2. Add charts:
   - Function execution count
   - Function execution time
   - Error rate
   - Storage usage

### Alerting Policies

**Set up alerts** for:

**1. High Error Rate**:
```
Metric: Cloud Function Error Rate
Condition: > 10% for 5 minutes
Notification: Email/SMS
```

**2. Long Execution Time**:
```
Metric: Function Execution Time
Condition: > 400s (approaching 540s timeout)
Notification: Email
```

**3. Budget Exceeded**:
```
Metric: Total Spend
Condition: > $10/month
Notification: Email
```

**4. Storage Nearly Full** (if you set quota):
```
Metric: Storage Usage
Condition: > 80% of quota
Notification: Email
```

---

## 🔧 Advanced Configuration

### Custom Domains

**Serve exports via custom domain**:

1. **Cloud Storage Static Website**:
   ```bash
   # Make bucket public
   gsutil iam ch allUsers:objectViewer gs://your-bucket

   # Set up load balancer with custom domain
   # Cloud Console → Network Services → Load Balancing
   ```

2. **Access via**:
   ```
   https://data.yourdomain.com/exports/cleaned/master.xlsx
   ```

### Multiple Environments

**Separate dev/staging/prod**:

```bash
# Create projects
firebase projects:create dev-scraper
firebase projects:create staging-scraper
firebase projects:create prod-scraper

# Use different projects
firebase use dev
firebase deploy

firebase use prod
firebase deploy
```

### CI/CD Integration

**GitHub Actions** example:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Firebase

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: w9jds/firebase-action@master
        with:
          args: deploy --only functions
        env:
          FIREBASE_TOKEN: ${{ secrets.FIREBASE_TOKEN }}
```

### Cloud Run Alternative

For **very long-running scrapes** (>9 minutes):

```bash
# Deploy to Cloud Run instead of Cloud Functions
# Supports up to 60 minutes execution time

gcloud run deploy scraper \
  --source . \
  --platform managed \
  --region us-central1 \
  --timeout 3600 \
  --memory 2Gi
```

---

## 🚀 Performance Optimization

### 1. Use Minimum Memory

Start with 256MB, increase only if needed:
```json
// firebase.json
"memory": "256MB"
```

### 2. Warm Instances (Reduce Cold Starts)

```json
// firebase.json
"minInstances": 1  // Keep 1 instance warm (costs ~$5/month)
```

### 3. Optimize Dependencies

```bash
# Only install what you need
# Remove unused packages from requirements.txt
```

### 4. Use Caching

```python
# Cache geocoding results
# Cache parser configurations
# Your watcher already does this!
```

### 5. Parallel Site Scraping

```python
# Scrape multiple sites in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(scrape_site, enabled_sites)
```

---

## 🆘 Troubleshooting

### Common Issues

See [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md#troubleshooting) for detailed troubleshooting.

**Quick Fixes**:

| Issue | Solution |
|-------|----------|
| "Billing required" | Upgrade to Blaze plan |
| Function timeout | Reduce `max_pages` or increase timeout |
| Out of memory | Increase memory in `firebase.json` |
| Playwright fails | Use requests-only mode |
| Module not found | Ensure all code is in `functions/` |
| Permission denied | Check storage rules |

---

## 📞 Support Resources

- **Firebase Docs**: https://firebase.google.com/docs
- **Cloud Functions Docs**: https://cloud.google.com/functions/docs
- **Stack Overflow**: Tag `firebase` or `google-cloud-functions`
- **Firebase Community Slack**: https://firebase.community/

---

## ✅ Compatibility Checklist

### Firebase Deployment

- [x] Python 3.8+ compatible
- [x] Serverless architecture
- [x] Auto-scaling
- [x] Global CDN
- [x] Built-in monitoring
- [x] Cost-effective (~$1-5/month)
- [x] No server management required
- [x] Automatic backups
- [x] Easy frontend integration

---

## 📋 Quick Reference

### Essential Commands

```bash
# Deploy
firebase deploy --only functions
firebase deploy --only storage

# View logs
firebase functions:log

# Test locally
firebase emulators:start

# Set config
firebase functions:config:set key=value

# Download data
gsutil cp gs://bucket/path ./local/
```

### Important URLs

- **Firebase Console**: https://console.firebase.google.com/
- **Cloud Console**: https://console.cloud.google.com/
- **Storage Browser**: https://console.cloud.google.com/storage/
- **Function Logs**: https://console.cloud.google.com/logs/

---

**Status**: ✅ Production Ready
**Recommended Plan**: Blaze (Pay-as-you-go)
**Estimated Cost**: $1-5/month
**Last Updated**: 2025-10-18
