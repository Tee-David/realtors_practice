# Firebase Firestore & Advanced Export System Guide

**Last Updated:** 2025-10-21
**Features:** Queryable database + Multi-format export with advanced filtering

---

## 🎯 **Overview**

This guide covers the complete Firebase Firestore integration and advanced export system that allows you to:

1. **Query data without downloading** - Fast Firestore queries from anywhere
2. **Export in multiple formats** - Excel, CSV, JSON, Parquet
3. **Advanced filtering** - Complex filters on any field
4. **Custom column selection** - Export only what you need
5. **$0 cost** - Free tier covers your usage

---

## 📊 **Architecture**

```
Data Flow:
──────────

GitHub Actions Workflow
    │
    ├─> Scrape properties (main.py)
    ├─> Process & clean data (watcher.py)
    ├─> Create master workbook
    │
    └─> Upload to Firebase Firestore
         │
         ├─> Collection: "properties"
         ├─> ~1,000 documents (properties)
         │
         └─> Frontend Access:
              ├─> Query directly (fast, no download)
              ├─> Export on demand (filtered data)
              └─> Download in any format
```

---

## 🚀 **Quick Start**

### **Step 1: Setup Firebase** (One-time, ~30 minutes)

1. **Create Firebase Project**
   - Go to https://console.firebase.google.com/
   - Click "Add project"
   - Name: "realtors-practice" (or your choice)
   - Disable Google Analytics (optional)
   - Click "Create project"

2. **Enable Firestore**
   - In Firebase Console, click "Firestore Database"
   - Click "Create database"
   - Choose "Start in production mode"
   - Select location: "us-central" (or nearest to you)
   - Click "Enable"

3. **Create Service Account**
   - Go to Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save the JSON file securely
   - **DO NOT commit this file to Git!**

4. **Add to GitHub Secrets**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `FIREBASE_CREDENTIALS`
   - Value: Paste entire content of service account JSON file
   - Click "Add secret"

---

### **Step 2: Upload Data to Firestore**

```bash
# Set environment variable (local testing)
set FIREBASE_SERVICE_ACCOUNT=path/to/service-account.json

# Or use credentials directly
set FIREBASE_CREDENTIALS={"type":"service_account",...}

# Upload master workbook to Firestore
python scripts/upload_to_firestore.py
```

**Output:**
```
============================================================
Uploading to Firebase Firestore
============================================================

✓ Loaded Firebase credentials from service-account.json
Loading master workbook: exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
✓ Loaded 1,250 properties

  ✓ Uploaded 500/1,250 properties (40.0%)
  ✓ Uploaded 1,000/1,250 properties (80.0%)

============================================================
Upload Complete!
============================================================
✓ Successfully uploaded: 1,250 properties

Firestore collection: 'properties'
Total documents: 1,250
============================================================
```

---

## 🔍 **API Endpoints**

### **1. Query Firestore** (No Download Required)

**Endpoint:** `POST /api/firestore/query`

**Request:**
```json
{
  "filters": {
    "location": "Lekki",
    "price_min": 5000000,
    "price_max": 50000000,
    "bedrooms_min": 3,
    "bathrooms_min": 2,
    "property_type": "Flat",
    "source": "npc",
    "quality_score_min": 0.7
  },
  "sort_by": "price",
  "sort_desc": true,
  "limit": 50,
  "offset": 0
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "3 Bedroom Luxury Apartment in Lekki",
      "price": 45000000,
      "location": "Lekki Phase 1",
      "bedrooms": 3,
      "bathrooms": 3,
      "property_type": "Flat",
      "source": "npc",
      "quality_score": 0.89,
      "listing_url": "https://...",
      "images": ["url1", "url2"]
    }
  ],
  "count": 25,
  "filters_applied": {...},
  "sort_by": "price",
  "sort_desc": true
}
```

---

### **2. Generate Export** (Multiple Formats)

**Endpoint:** `POST /api/export/generate`

**Request:**
```json
{
  "format": "excel",
  "filters": {
    "location": "Lekki",
    "price_min": 5000000,
    "price_max": 50000000,
    "bedrooms_min": 3
  },
  "columns": ["title", "price", "location", "bedrooms", "bathrooms"],
  "sort_by": "price",
  "sort_desc": false,
  "include_images": false,
  "filename": "lekki_properties"
}
```

**Response:**
```json
{
  "success": true,
  "download_url": "/api/export/download/lekki_properties_20251021_103000.xlsx",
  "filename": "lekki_properties_20251021_103000.xlsx",
  "format": "excel",
  "record_count": 245,
  "file_size_bytes": 524288,
  "file_size_mb": 0.5,
  "filters_applied": {...},
  "columns": ["title", "price", "location", "bedrooms", "bathrooms"]
}
```

---

### **3. Download Export**

**Endpoint:** `GET /api/export/download/{filename}`

Downloads the generated file directly to browser.

---

### **4. Get Available Formats**

**Endpoint:** `GET /api/export/formats`

**Response:**
```json
{
  "formats": [
    {
      "format": "excel",
      "extension": ".xlsx",
      "description": "Microsoft Excel format - Best for manual analysis and sharing",
      "supports_formulas": true,
      "file_size": "Medium",
      "recommended_for": "General use, business reports, manual analysis"
    },
    {
      "format": "csv",
      "extension": ".csv",
      "description": "Comma-Separated Values - Universal compatibility",
      "file_size": "Small",
      "recommended_for": "Import into other tools, lightweight storage"
    },
    {
      "format": "json",
      "extension": ".json",
      "description": "JSON format - Best for programmatic access and APIs",
      "recommended_for": "Web applications, API integration"
    },
    {
      "format": "parquet",
      "extension": ".parquet",
      "description": "Apache Parquet - Optimized columnar format",
      "file_size": "Very Small (compressed)",
      "recommended_for": "Data analysis, analytics, big data processing"
    }
  ],
  "available_filters": {
    "location": "Filter by location (exact match)",
    "price_min": "Minimum price",
    "price_max": "Maximum price",
    "bedrooms_min": "Minimum bedrooms",
    "bathrooms_min": "Minimum bathrooms",
    "property_type": "Property type (Flat, House, Land, etc.)",
    "source": "Data source (npc, propertypro, jiji, etc.)",
    "quality_score_min": "Minimum quality score (0.0 - 1.0)"
  }
}
```

---

## 💻 **Frontend Integration**

### **React/Next.js Example**

```tsx
// components/PropertySearch.tsx
'use client';

import { useState } from 'react';

export default function PropertySearch() {
  const [results, setResults] = useState([]);
  const [filters, setFilters] = useState({
    location: '',
    price_min: '',
    price_max: '',
    bedrooms_min: ''
  });

  // Query Firestore
  const searchProperties = async () => {
    const response = await fetch('/api/firestore/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filters: {
          ...filters,
          price_min: parseInt(filters.price_min) || undefined,
          price_max: parseInt(filters.price_max) || undefined,
          bedrooms_min: parseInt(filters.bedrooms_min) || undefined
        },
        sort_by: 'price',
        limit: 50
      })
    });

    const data = await response.json();
    setResults(data.results);
  };

  // Export to Excel
  const exportToExcel = async () => {
    const response = await fetch('/api/export/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        format: 'excel',
        filters,
        include_images: false
      })
    });

    const data = await response.json();

    // Download file
    window.location.href = data.download_url;
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Property Search</h1>

      {/* Filters */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          placeholder="Location (e.g., Lekki)"
          value={filters.location}
          onChange={(e) => setFilters({...filters, location: e.target.value})}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Min Price"
          value={filters.price_min}
          onChange={(e) => setFilters({...filters, price_min: e.target.value})}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Max Price"
          value={filters.price_max}
          onChange={(e) => setFilters({...filters, price_max: e.target.value})}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Min Bedrooms"
          value={filters.bedrooms_min}
          onChange={(e) => setFilters({...filters, bedrooms_min: e.target.value})}
          className="border p-2 rounded"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={searchProperties}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          🔍 Search
        </button>
        <button
          onClick={exportToExcel}
          className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          📥 Export to Excel
        </button>
      </div>

      {/* Results */}
      <div className="grid gap-4">
        {results.map((property, idx) => (
          <div key={idx} className="border p-4 rounded shadow">
            <h3 className="font-bold text-lg">{property.title}</h3>
            <p className="text-gray-600">
              ₦{property.price?.toLocaleString()} • {property.bedrooms} beds • {property.location}
            </p>
            <a
              href={property.listing_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              View Listing →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 💰 **Cost Breakdown**

### **Firestore FREE Tier**

| Resource | FREE Quota | Your Usage | Status |
|----------|-----------|------------|--------|
| **Storage** | 1 GB | ~50 MB (1,000 properties) | ✅ FREE |
| **Reads** | 50,000/day | ~5,000/day (100 users × 50 queries) | ✅ FREE |
| **Writes** | 20,000/day | ~1,000/day (daily upload) | ✅ FREE |
| **Deletes** | 20,000/day | ~100/day | ✅ FREE |

**Verdict: $0/month** ✅

### **If You Exceed FREE Tier (Unlikely)**

| Resource | After FREE | Cost Example |
|----------|-----------|--------------|
| **Storage** | $0.18/GB/month | Extra 1 GB = $0.18/month |
| **Reads** | $0.06 per 100k | 100k extra reads = $0.06 |
| **Writes** | $0.18 per 100k | 100k extra writes = $0.18 |

---

## 🛠️ **GitHub Actions Integration**

Update `.github/workflows/scrape-production.yml`:

```yaml
name: Scraper Workflow

on:
  repository_dispatch:
    types: [trigger-scrape]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install firebase-admin

      - name: Run scraper
        run: python main.py

      - name: Process exports
        run: python watcher.py --once

      - name: Upload to Firestore
        env:
          FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
        run: python scripts/upload_to_firestore.py

      - name: Upload artifacts (temporary backup)
        uses: actions/upload-artifact@v3
        with:
          name: scraper-exports
          path: exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx
          retention-days: 30
```

---

## 📝 **Summary**

### **What You Get:**

1. **Queryable Database**
   - ✅ Fast queries without downloading
   - ✅ Complex filtering (location, price, bedrooms, etc.)
   - ✅ Sorting and pagination
   - ✅ Real-time access from anywhere

2. **Advanced Export System**
   - ✅ 4 formats: Excel, CSV, JSON, Parquet
   - ✅ Custom column selection
   - ✅ Advanced filtering before export
   - ✅ Generated on demand (no storage cost)

3. **Zero Cost**
   - ✅ Firestore free tier: 50k reads/day
   - ✅ Export generates files temporarily (no storage)
   - ✅ Total cost: $0/month

4. **Scalable Architecture**
   - ✅ Handles thousands of properties
   - ✅ Fast queries (<200ms)
   - ✅ Global CDN (Firebase)
   - ✅ Production-ready

---

## 🚀 **Next Steps**

1. ✅ Setup Firebase (30 minutes)
2. ✅ Upload data to Firestore
3. ✅ Test query endpoint
4. ✅ Test export with filters
5. ✅ Integrate with frontend
6. ✅ Deploy to GitHub Actions

**Your data is now queryable from anywhere, with export on demand, at $0 cost!** 🎉
