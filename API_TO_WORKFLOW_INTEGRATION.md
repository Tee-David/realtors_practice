# API to GitHub Workflow Integration - Complete Guide

## Overview

This document explains how the frontend can trigger scraping workflows via API endpoints and how those workflows interact with Firestore.

**IMPORTANT:** All workflows now upload directly to Firestore during scraping (not from master workbook).

---

## Architecture

```
Frontend → API Endpoint → GitHub Actions Workflow → Scrape → Firestore Upload (DIRECT)
                                                           ↓
                                                     Master Workbook (BACKUP)
```

### Key Components:

1. **API Server** (`api_server.py`) - REST API with GitHub Actions integration endpoints
2. **GitHub Workflows** (4 workflows) - Automated scraping pipelines
3. **Firestore** - PRIMARY data store with enterprise schema
4. **Master Workbook** - BACKUP/ANALYSIS only (not primary)

---

## Available Workflows

### 1. `scrape.yml` - Main Workflow (Triggered by Frontend)

**Purpose:** Standard scraping workflow for frontend integration

**Triggers:**
- `repository_dispatch` with event type `trigger-scrape` (API triggered)
- `workflow_dispatch` (manual UI trigger)

**Features:**
- ✅ Firestore upload during scrape (PRIMARY)
- ✅ Auto-detects batch size
- ✅ Conditional job execution
- ✅ Enterprise schema (9 categories, 85+ fields)
- ✅ Master workbook as backup

**Used by:** `/api/github/trigger-scrape` endpoint

---

### 2. `scrape-large-batch.yml` - Multi-Session Workflow

**Purpose:** Handle large batches with parallel sessions

**Triggers:**
- `workflow_dispatch` (manual UI trigger only)

**Features:**
- ✅ Splits sites into multiple sessions
- ✅ Parallel execution (3 sessions at once)
- ✅ Firestore upload in each session
- ✅ Consolidated master workbook at end

**Used by:** Manual trigger for large batches (20+ sites)

---

### 3. `test-quick-scrape.yml` - Quick Test Workflow

**Purpose:** Fast testing with single site

**Triggers:**
- `workflow_dispatch` (manual UI trigger only)

**Features:**
- ✅ Single site, limited pages
- ✅ Firestore upload during scrape
- ✅ Fast execution (3-5 minutes)
- ✅ Good for testing/debugging

**Used by:** Testing and debugging

---

### 4. `upload-only.yml` - Upload Existing Data

**Purpose:** Upload existing master workbook to Firestore

**Triggers:**
- `workflow_dispatch` (manual UI trigger only)

**Features:**
- ✅ Upload from existing workbook
- ✅ Cleanup stale listings
- ✅ No scraping involved

**Used by:** One-time data migrations or re-uploads

---

## API Endpoints for Frontend

### 1. Trigger Scraping Workflow

**Endpoint:** `POST /api/github/trigger-scrape`

**Description:** Triggers the main `scrape.yml` workflow via GitHub's repository_dispatch API

**Required Environment Variables:**
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx  # PAT with 'repo' scope
GITHUB_OWNER=Tee-David                  # Repository owner
GITHUB_REPO=realtors_practice           # Repository name
```

**Request Body:**
```json
{
  "page_cap": 20,              // Optional: pages per site (default: 20)
  "geocode": 1,                // Optional: enable geocoding 0/1 (default: 1)
  "sites": ["npc", "jiji"]     // Optional: specific sites (empty = all enabled)
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Scraper workflow triggered successfully",
  "run_url": "https://github.com/Tee-David/realtors_practice/actions",
  "parameters": {
    "page_cap": 20,
    "geocode": 1,
    "sites": ["npc", "jiji"]
  }
}
```

**Response (Error):**
```json
{
  "error": "Missing GitHub configuration",
  "details": "Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables"
}
```

**Example Usage (Frontend):**
```typescript
const triggerScrape = async (pageCount: number, sites?: string[]) => {
  const response = await fetch('/api/github/trigger-scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      page_cap: pageCount,
      geocode: 1,
      sites: sites || []
    })
  });

  const data = await response.json();
  if (data.success) {
    console.log('Workflow triggered:', data.run_url);
    return data;
  } else {
    throw new Error(data.error);
  }
};
```

---

### 2. Get Workflow Status

**Endpoint:** `GET /api/notifications/workflow-status/<run_id>`

**Description:** Get real-time status of a running workflow

**Response:**
```json
{
  "run_id": 123456,
  "status": "in_progress",        // queued, in_progress, completed
  "conclusion": null,              // success, failure, cancelled (when completed)
  "progress": {
    "current_step": "Processing exports",
    "percent_complete": 65,
    "estimated_time_remaining": "15 minutes"
  },
  "started_at": "2025-11-11T10:00:00Z",
  "completed_at": null
}
```

**Example Usage (Frontend):**
```typescript
const checkWorkflowStatus = async (runId: number) => {
  const response = await fetch(`/api/notifications/workflow-status/${runId}`);
  const data = await response.json();
  return data;
};

// Poll for updates every 10 seconds
const pollWorkflowStatus = (runId: number) => {
  const interval = setInterval(async () => {
    const status = await checkWorkflowStatus(runId);

    if (status.status === 'completed') {
      clearInterval(interval);
      if (status.conclusion === 'success') {
        console.log('Workflow completed successfully!');
        // Fetch data from Firestore
      } else {
        console.error('Workflow failed:', status.conclusion);
      }
    } else {
      console.log(`Progress: ${status.progress.percent_complete}%`);
    }
  }, 10000);
};
```

---

### 3. List Recent Workflow Runs

**Endpoint:** `GET /api/github/workflow-runs`

**Query Parameters:**
- `per_page`: Number of runs to return (default: 5, max: 100)
- `workflow_id`: Filter by specific workflow (optional)

**Response:**
```json
{
  "total_count": 25,
  "workflow_runs": [
    {
      "id": 123456,
      "name": "Nigerian Real Estate Scraper",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-11-11T10:00:00Z",
      "updated_at": "2025-11-11T10:15:00Z",
      "html_url": "https://github.com/..."
    }
  ]
}
```

---

### 4. Estimate Scrape Time

**Endpoint:** `POST /api/github/estimate-scrape-time`

**Description:** Estimate duration before triggering

**Request Body:**
```json
{
  "page_cap": 20,
  "geocode": 1,
  "sites": []  // empty = all enabled sites
}
```

**Response:**
```json
{
  "estimated_duration_minutes": 45,
  "estimated_duration_text": "~45 minutes",
  "site_count": 5,
  "batch_type": "small",
  "sessions": 1,
  "breakdown": {
    "scraping_time": 30,
    "geocoding_time": 10,
    "processing_time": 5
  }
}
```

---

## Firestore Upload Architecture

### How It Works Now (FIXED):

1. **Frontend triggers scrape** via `/api/github/trigger-scrape`
2. **GitHub Actions workflow starts** (`scrape.yml`)
3. **Scraper runs** with Firebase credentials
4. **Properties upload to Firestore DIRECTLY** during scraping (main.py:238-250)
5. **Master workbook created** as backup (watcher.py)
6. **Workflow completes** - data is in Firestore

### What Uploads to Firestore:

**During Scraping (PRIMARY):**
- ✅ Each property uploads immediately after scraping
- ✅ Enterprise schema transformation applied
- ✅ Auto-detection (listing_type, furnishing, condition)
- ✅ Auto-tagging (premium, hot_deal)
- ✅ Location intelligence (area, LGA, landmarks)

**Schema Structure:**
```
properties/{hash}/
├── basic_info.*         (title, source, status, listing_type)
├── property_details.*   (type, bedrooms, bathrooms, furnishing, condition)
├── financial.*          (price, currency, price_per_sqm, payment_plan)
├── location.*           (address, area, lga, state, coordinates, landmarks)
├── amenities.*          (features, security, utilities)
├── media.*              (images, videos, virtual_tour)
├── agent_info.*         (name, contact, agency)
├── metadata.*           (quality_score, view_count, search_keywords, timestamps)
└── tags.*               (premium, hot_deal, featured)
```

---

## Frontend Integration Steps

### Step 1: Set Up Environment Variables

On your backend server (where `api_server.py` runs):

```bash
# GitHub Integration
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxx"
export GITHUB_OWNER="Tee-David"
export GITHUB_REPO="realtors_practice"

# Firebase (if you also want local API access to Firestore)
export FIREBASE_SERVICE_ACCOUNT="path/to/service-account.json"
```

### Step 2: Add GitHub Secret (For Workflows)

1. Go to: https://github.com/Tee-David/realtors_practice/settings/secrets/actions
2. Add secret named `FIREBASE_CREDENTIALS`
3. Value: Full JSON content of Firebase service account file

### Step 3: Trigger Scrape from Frontend

```typescript
// triggers/scrape.ts
import { useState } from 'react';

export const useScrapeTriggering = () => {
  const [isTriggering, setIsTriggering] = useState(false);
  const [runId, setRunId] = useState<number | null>(null);

  const triggerScrape = async (options: {
    pageCount: number;
    sites?: string[];
    enableGeocoding?: boolean;
  }) => {
    setIsTriggering(true);
    try {
      const response = await fetch('/api/github/trigger-scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_cap: options.pageCount,
          geocode: options.enableGeocoding ? 1 : 0,
          sites: options.sites || []
        })
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error);
      }

      // Extract run ID from URL (optional, for status tracking)
      // Note: GitHub API doesn't return run_id immediately
      // You'll need to poll /api/github/workflow-runs to get the latest run

      return data;
    } finally {
      setIsTriggering(false);
    }
  };

  return { triggerScrape, isTriggering, runId };
};
```

### Step 4: Monitor Workflow Progress

```typescript
// hooks/useWorkflowStatus.ts
import { useEffect, useState } from 'react';

export const useWorkflowStatus = (runId: number | null) => {
  const [status, setStatus] = useState<any>(null);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    if (!runId) return;

    setIsPolling(true);
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/notifications/workflow-status/${runId}`);
        const data = await response.json();
        setStatus(data);

        if (data.status === 'completed') {
          clearInterval(interval);
          setIsPolling(false);
        }
      } catch (error) {
        console.error('Failed to fetch workflow status:', error);
      }
    }, 10000); // Poll every 10 seconds

    return () => {
      clearInterval(interval);
      setIsPolling(false);
    };
  }, [runId]);

  return { status, isPolling };
};
```

### Step 5: Fetch Data from Firestore

After workflow completes, data is immediately available via Firestore endpoints:

```typescript
// Fetch properties
const fetchProperties = async (filters: any) => {
  const response = await fetch('/api/firestore/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters)
  });
  return response.json();
};

// Example: Get latest 50 properties
const getLatestProperties = () => fetchProperties({
  limit: 50,
  order_by: 'metadata.scrape_timestamp',
  order_direction: 'desc'
});

// Example: Search for properties in Lekki
const searchLekki = () => fetchProperties({
  filters: {
    'location.area': 'Lekki',
    'basic_info.listing_type': 'sale'
  },
  limit: 100
});
```

---

## Testing the Integration

### Test 1: Trigger Workflow Manually

```bash
curl -X POST http://localhost:5000/api/github/trigger-scrape \
  -H "Content-Type: application/json" \
  -d '{
    "page_cap": 5,
    "geocode": 0,
    "sites": ["npc"]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Scraper workflow triggered successfully",
  "run_url": "https://github.com/Tee-David/realtors_practice/actions"
}
```

### Test 2: Check Workflow Status

1. Go to: https://github.com/Tee-David/realtors_practice/actions
2. Find the latest workflow run
3. Click to view logs
4. Look for: `✓ Firebase credentials configured (Firestore upload enabled)`
5. Look for: `npc: [SUCCESS] Uploaded X listings to Firestore (PRIMARY STORE)`

### Test 3: Verify Firestore Upload

1. Go to: https://console.firebase.google.com/project/realtor-s-practice/firestore
2. Check `properties` collection
3. Verify documents exist with enterprise schema
4. Check `basic_info.source = "npc"`

### Test 4: Query via API

```bash
curl -X POST http://localhost:5000/api/firestore/search \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"basic_info.source": "npc"},
    "limit": 10
  }'
```

---

## Troubleshooting

### Issue: "Missing GitHub configuration"

**Cause:** Environment variables not set

**Solution:**
```bash
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_OWNER="Tee-David"
export GITHUB_REPO="realtors_practice"
```

### Issue: "Firestore upload disabled"

**Cause:** `FIREBASE_CREDENTIALS` secret not set in GitHub

**Solution:**
1. Go to repo settings → Secrets → Actions
2. Add `FIREBASE_CREDENTIALS` with full JSON content

### Issue: Workflow triggered but no data in Firestore

**Cause:** Check workflow logs for errors

**Solution:**
1. Go to workflow run in GitHub Actions
2. Check "Run scraper" step logs
3. Look for error messages
4. Verify Firebase credentials are valid

### Issue: Can't find run_id to poll status

**Cause:** GitHub repository_dispatch doesn't return run_id immediately

**Solution:**
1. Use `/api/github/workflow-runs` to get latest runs
2. Match by timestamp or payload
3. Start polling once you have run_id

---

## Summary

### ✅ What's Fixed:

1. **All 4 workflows upload to Firestore DIRECTLY** during scraping
2. **Master workbook is BACKUP only** (not primary data store)
3. **Frontend can trigger scrapes** via `/api/github/trigger-scrape`
4. **Frontend can monitor progress** via `/api/notifications/workflow-status/<run_id>`
5. **Data immediately available** in Firestore after workflow completes

### ✅ Workflows Fixed:

- ✅ `scrape.yml` - Main workflow (frontend triggers this)
- ✅ `scrape-large-batch.yml` - Multi-session workflow
- ✅ `test-quick-scrape.yml` - Quick test workflow
- ✅ `upload-only.yml` - Already correct (uploads from workbook)

### ✅ Integration Tested:

- ✅ API endpoint exists and documented
- ✅ Workflow triggers via repository_dispatch
- ✅ Firebase credentials passed correctly
- ✅ Firestore upload happens during scraping
- ✅ Enterprise schema applied automatically

**Your frontend developer can now confidently integrate with the API!**
