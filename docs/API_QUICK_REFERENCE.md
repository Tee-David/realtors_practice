# API Quick Reference for Frontend Developers

**Base URL:** `http://localhost:5000` (local) or your deployed URL

**Total Endpoints:** 58

---

## 🚀 Getting Started (3 Steps)

### 1. Start the API Server

```bash
python api_server.py
```

Server runs on: `http://localhost:5000`

### 2. Test Health Endpoint

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T10:00:00"
}
```

### 3. Import Postman Collection

File: `docs/POSTMAN_COLLECTION.json`

Import this into Postman to test all 58 endpoints with examples.

---

## 📋 Most Important Endpoints

### 🔥 Firestore Query (Fast Cloud Queries)

```javascript
// POST /api/firestore/query
const response = await fetch('/api/firestore/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filters: {
      location: "Lekki",
      price_min: 5000000,
      price_max: 50000000,
      bedrooms_min: 3
    },
    limit: 50,
    sort_by: "price",
    sort_desc: false
  })
});

const data = await response.json();
// Returns: { results: [...], count: 25, filters_applied: {...} }
```

**Filters Available:**
- `location` - Exact match
- `price_min`, `price_max` - Price range
- `bedrooms_min`, `bathrooms_min` - Minimum rooms
- `property_type` - "Flat", "House", "Land", etc.
- `source` - "npc", "jiji", "propertypro", etc.
- `quality_score_min` - 0.0 to 1.0

---

### 📥 Export Data (4 Formats)

```javascript
// POST /api/export/generate
const response = await fetch('/api/export/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    format: "excel",  // or "csv", "json", "parquet"
    filters: {
      price_max: 50000000,
      bedrooms_min: 3
    },
    columns: ["title", "price", "location", "bedrooms"],
    include_images: false,
    filename: "lekki_properties"
  })
});

const data = await response.json();
// Returns: { download_url: "/api/export/download/...", filename: "...", record_count: 245 }

// Download the file
window.location.href = data.download_url;
```

---

### ⏰ Schedule Scraping

```javascript
// POST /api/schedule/scrape
const response = await fetch('/api/schedule/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scheduled_time: "2025-10-22T15:00:00",  // ISO format
    page_cap: 10,
    sites: ["npc", "jiji"]
  })
});

const data = await response.json();
// Returns: { job_id: 1, scheduled_time: "...", status: "scheduled", cancel_url: "..." }

// Check job status
const status = await fetch(`/api/schedule/jobs/${data.job_id}`);

// Cancel job
await fetch(`/api/schedule/jobs/${data.job_id}/cancel`, { method: 'POST' });
```

---

### 🔧 Trigger Scraping

```javascript
// POST /api/scrape/start
const response = await fetch('/api/scrape/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sites: ["npc", "jiji"],  // Optional: specific sites
    max_pages: 10,            // Optional: pages per site
    geocode: true             // Optional: enable geocoding
  })
});

const data = await response.json();
// Returns: { scrape_id: "abc123", status: "running" }

// Monitor progress
const progress = await fetch(`/api/scrape/status/${data.scrape_id}`);
```

---

## 📊 Complete Endpoint List

### 1. Health & Status (2)
- `GET /api/health` - API health check
- `GET /api/status` - Detailed system status

### 2. Scraping Control (5)
- `POST /api/scrape/start` - Start scraping
- `GET /api/scrape/status/<id>` - Get scrape status
- `POST /api/scrape/stop/<id>` - Stop scraping
- `GET /api/scrape/history` - Scrape history
- `GET /api/scrape/active` - Active scrapes

### 3. Site Management (7)
- `GET /api/sites` - List all sites
- `GET /api/sites/enabled` - Enabled sites only
- `POST /api/sites/<name>/enable` - Enable site
- `POST /api/sites/<name>/disable` - Disable site
- `GET /api/sites/<name>/config` - Get site config
- `PUT /api/sites/<name>/config` - Update config
- `DELETE /api/sites/<name>` - Delete site

### 4. Data Query (6)
- `GET /api/properties` - List properties (paginated)
- `GET /api/properties/<id>` - Get property details
- `POST /api/properties/search` - Advanced search
- `GET /api/properties/filter` - Filter properties
- `GET /api/properties/count` - Count properties
- `GET /api/properties/recent` - Recent listings

### 5. Analytics (5)
- `GET /api/analytics/summary` - Overall summary
- `GET /api/analytics/by-location` - By location stats
- `GET /api/analytics/by-type` - By property type stats
- `GET /api/analytics/price-distribution` - Price ranges
- `GET /api/analytics/trends` - Market trends

### 6. Price Tracking (4)
- `GET /api/price-history/<property_id>` - Property price history
- `GET /api/price-changes` - Recent price changes
- `GET /api/price-drops` - Properties with price drops
- `GET /api/price-alerts` - Set up price alerts

### 7. Exports (5)
- `GET /api/exports` - List available exports
- `POST /api/exports/create` - Create new export
- `GET /api/exports/<id>` - Get export details
- `GET /api/exports/<id>/download` - Download export
- `DELETE /api/exports/<id>` - Delete export

### 8. Master Workbook (3)
- `GET /api/workbook/info` - Workbook metadata
- `GET /api/workbook/sheets` - List sheets
- `GET /api/workbook/download` - Download workbook

### 9. Firestore (1) ⭐ **NEW**
- `POST /api/firestore/query` - Query Firestore with filters

### 10. Advanced Export (3) ⭐ **NEW**
- `POST /api/export/generate` - Generate filtered export
- `GET /api/export/download/<filename>` - Download export
- `GET /api/export/formats` - Available formats

### 11. GitHub Actions (4) ⭐ **NEW**
- `POST /api/github/trigger-scrape` - Trigger workflow
- `GET /api/github/workflow-runs` - Get workflow runs
- `GET /api/github/artifacts` - List artifacts
- `GET /api/github/artifact/<id>/download` - Download artifact

### 12. Scheduled Scraping (4) ⭐ **NEW**
- `POST /api/schedule/scrape` - Schedule future scrape
- `GET /api/schedule/jobs` - List scheduled jobs
- `GET /api/schedule/jobs/<id>` - Get job status
- `POST /api/schedule/jobs/<id>/cancel` - Cancel job

### 13. Configuration (5)
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration
- `GET /api/config/defaults` - Get default config
- `POST /api/config/validate` - Validate config
- `POST /api/config/reset` - Reset to defaults

### 14. Utilities (4)
- `GET /api/geocode/<address>` - Geocode address
- `POST /api/validate/url` - Validate URL
- `GET /api/robots/<domain>` - Check robots.txt
- `POST /api/test/parser` - Test parser

---

## 🎨 React Example Component

```tsx
import { useState, useEffect } from 'react';

export default function PropertySearch() {
  const [properties, setProperties] = useState([]);
  const [filters, setFilters] = useState({
    location: '',
    price_max: 50000000,
    bedrooms_min: 3
  });

  const searchProperties = async () => {
    const response = await fetch('/api/firestore/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filters, limit: 50 })
    });

    const data = await response.json();
    setProperties(data.results);
  };

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
    window.location.href = data.download_url;
  };

  return (
    <div>
      <h1>Property Search</h1>

      {/* Filters */}
      <div>
        <input
          placeholder="Location"
          value={filters.location}
          onChange={(e) => setFilters({...filters, location: e.target.value})}
        />
        <input
          type="number"
          placeholder="Max Price"
          value={filters.price_max}
          onChange={(e) => setFilters({...filters, price_max: Number(e.target.value)})}
        />
        <button onClick={searchProperties}>Search</button>
        <button onClick={exportToExcel}>Export to Excel</button>
      </div>

      {/* Results */}
      <div>
        {properties.map((property, idx) => (
          <div key={idx}>
            <h3>{property.title}</h3>
            <p>₦{property.price?.toLocaleString()} • {property.bedrooms} beds</p>
            <p>{property.location}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔑 Environment Variables Needed

For full functionality, set these environment variables:

```bash
# GitHub Actions integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_OWNER=your_github_username
GITHUB_REPO=realtors_practice

# Firebase/Firestore
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-service-account.json

# Optional
API_PORT=5000
DEBUG=false
```

---

## 📚 Additional Resources

- **Full API Documentation:** `docs/FRONTEND_INTEGRATION_GUIDE.md`
- **Firestore Setup:** `FIRESTORE_SETUP_WALKTHROUGH.md`
- **Postman Collection:** `docs/POSTMAN_COLLECTION.json`
- **Branch Protection:** `docs/BRANCH_PROTECTION.md`

---

## 🐛 Common Issues & Solutions

**Issue:** "Connection refused" error
**Solution:** Make sure API server is running (`python api_server.py`)

**Issue:** "Firestore credentials not found"
**Solution:** Set `FIREBASE_SERVICE_ACCOUNT` environment variable

**Issue:** "CORS error" when calling from frontend
**Solution:** API has CORS enabled. Check if calling correct URL.

**Issue:** Empty results from Firestore query
**Solution:** Make sure data is uploaded (`python scripts/upload_to_firestore.py`)

---

**Happy Coding! 🚀**

For questions or issues, refer to the full documentation or create an issue on GitHub.
