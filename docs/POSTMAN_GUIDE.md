# Postman Testing Guide - Real Estate Scraper API

**Complete guide for testing all 23 API endpoints**

---

## Table of Contents

1. [Setup](#setup)
2. [Testing Workflow](#testing-workflow)
3. [Endpoint Categories](#endpoint-categories)
4. [Common Use Cases](#common-use-cases)
5. [Troubleshooting](#troubleshooting)
6. [Integration with Frontend](#integration-with-frontend)

---

## Setup

### 1. Import Postman Collection

1. **Open Postman** (Download from [postman.com](https://www.postman.com/downloads/))
2. **Click "Import"** button (top left)
3. **Select File**: `docs/POSTMAN_COLLECTION.json`
4. **Import**: Collection will appear in left sidebar

### 2. Start API Server

```bash
# Navigate to project directory
cd C:\Users\DELL\Desktop\Dynamic realtors_practice

# Start API server
python api_server.py

# Server will start on http://localhost:5000
# You should see: "Running on http://127.0.0.1:5000"
```

### 3. Configure Environment (Optional)

If you want to use a different base URL:

1. **Postman**: Environments tab → Create Environment
2. **Add Variable**:
   - Variable: `base_url`
   - Initial Value: `http://localhost:5000/api`
   - Current Value: `http://localhost:5000/api`
3. **Select Environment** from dropdown (top right)

**Default**: Collection uses `http://localhost:5000/api` built-in

---

## Testing Workflow

### Recommended Testing Order

Test endpoints in this order for best results:

```
1. Health Check → Verify API is running
2. List Sites → See available sites
3. Get Site Details → Check specific site config
4. Start Scraping → Trigger a test scrape run
5. Get Scraping Status → Monitor progress
6. Get Logs → View scrape logs
7. List Data Files → Check scraped data
8. Get Site Data → View property listings
9. Search Data → Test search functionality
10. Get Stats → View statistics
```

### Quick Test Script (5 Minutes)

**Test Core Functionality**:

1. ✅ **Health Check** → Confirm API is alive
2. ✅ **List Sites** → Verify sites loaded
3. ✅ **Start Scrape** (1 site, 5 pages) → Quick scrape
4. ✅ **Monitor Status** → Check if running
5. ✅ **View Logs** → See scrape progress
6. ✅ **Get Data** → Confirm data exported

---

## Endpoint Categories

### 1. Health (1 endpoint)

#### `GET /api/health`

**Purpose**: Verify API server is running

**Test**:
```bash
curl http://localhost:5000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T16:00:00.000000",
  "version": "1.0.0"
}
```

**Success Criteria**: Status 200, `status: "healthy"`

---

### 2. Scraping Management (4 endpoints)

#### `POST /api/scrape/start`

**Purpose**: Start a new scraping run

**Postman Request**:
- **Method**: POST
- **URL**: `{{base_url}}/scrape/start`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):

```json
{
  "sites": ["npc"],
  "max_pages": 5,
  "geocoding": false
}
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Scraping started",
  "pid": 12345,
  "sites": ["npc"],
  "started_at": "2025-10-18T16:00:00"
}
```

**Success Criteria**:
- Status 200
- `success: true`
- `pid` is a number
- `started_at` is recent timestamp

**Common Variations**:
```json
// Scrape all enabled sites
{
  "sites": []
}

// Multiple sites, more pages
{
  "sites": ["npc", "propertypro"],
  "max_pages": 20,
  "geocoding": true
}

// Just one site, minimal pages (fastest test)
{
  "sites": ["npc"],
  "max_pages": 2,
  "geocoding": false
}
```

#### `GET /api/scrape/status`

**Purpose**: Check if scraper is running

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/scrape/status`

**Expected Response (Running)**:
```json
{
  "running": true,
  "pid": 12345,
  "started_at": "2025-10-18T16:00:00",
  "elapsed_seconds": 120,
  "sites": ["npc"],
  "current_site": "npc"
}
```

**Expected Response (Not Running)**:
```json
{
  "running": false,
  "last_run": "2025-10-18T15:00:00",
  "last_duration_seconds": 600
}
```

**Testing Tips**:
- Call immediately after `start` → Should show `running: true`
- Poll every 10 seconds to monitor progress
- When complete → `running: false` with duration

#### `POST /api/scrape/stop`

**Purpose**: Stop currently running scrape

**Postman Request**:
- **Method**: POST
- **URL**: `{{base_url}}/scrape/stop`

**Expected Response (Success)**:
```json
{
  "success": true,
  "message": "Scraping stopped",
  "pid": 12345
}
```

**Expected Response (Not Running)**:
```json
{
  "success": false,
  "message": "No scraping process is running"
}
```

**Testing Tip**: Start a scrape first, then immediately stop it

#### `GET /api/scrape/history`

**Purpose**: View past scraping runs

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/scrape/history?limit=10`

**Query Params**:
- `limit`: Number of runs to return (optional, default: 10)

**Expected Response**:
```json
{
  "total_runs": 25,
  "history": [
    {
      "run_id": 1,
      "started_at": "2025-10-18T15:00:00",
      "completed_at": "2025-10-18T15:10:00",
      "duration_seconds": 600,
      "sites_scraped": ["npc", "propertypro"],
      "total_listings": 1500,
      "success": true
    }
  ]
}
```

**Success Criteria**: Returns array of past runs with metadata

---

### 3. Site Configuration (6 endpoints)

#### `GET /api/sites`

**Purpose**: List all configured sites

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/sites`

**Expected Response**:
```json
{
  "total_sites": 50,
  "enabled_sites": 5,
  "sites": [
    {
      "key": "npc",
      "name": "Nigeria Property Centre",
      "url": "https://nigeriapropertycentre.com/",
      "enabled": true,
      "parser": "specials"
    }
  ]
}
```

**Success Criteria**:
- Returns all 50 sites
- Shows which are enabled
- Each site has key, name, url, enabled, parser

#### `GET /api/sites/{site_key}`

**Purpose**: Get detailed configuration for one site

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/sites/npc`

**Expected Response**:
```json
{
  "key": "npc",
  "name": "Nigeria Property Centre",
  "url": "https://nigeriapropertycentre.com/",
  "enabled": true,
  "parser": "specials",
  "selectors": {
    "card": "li.property-list",
    "title": "h2",
    "price": ".price"
  },
  "overrides": {
    "max_pages": 40
  }
}
```

**Test Different Sites**:
- `/api/sites/npc` → NPC config
- `/api/sites/propertypro` → PropertyPro config
- `/api/sites/jiji` → Jiji config

#### `POST /api/sites`

**Purpose**: Add a new site dynamically

**Postman Request**:
- **Method**: POST
- **URL**: `{{base_url}}/sites`
- **Headers**: `Content-Type: application/json`
- **Body**:

```json
{
  "key": "testsite",
  "name": "Test Real Estate Site",
  "url": "https://testsite.com",
  "enabled": true,
  "parser": "specials",
  "selectors": {
    "card": ".property-card",
    "title": "h3.title",
    "price": ".price",
    "location": ".location"
  }
}
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Site 'testsite' added successfully",
  "site": { /* full site config */ }
}
```

**Important**: This updates `config.yaml` file!

**Testing Tips**:
- After adding, call `GET /api/sites` to confirm it's listed
- Check `config.yaml` file to see it was written
- Try adding duplicate → Should get error

#### `PUT /api/sites/{site_key}`

**Purpose**: Update existing site configuration

**Postman Request**:
- **Method**: PUT
- **URL**: `{{base_url}}/sites/testsite`
- **Body**:

```json
{
  "enabled": false,
  "overrides": {
    "max_pages": 50
  }
}
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Site 'testsite' updated successfully",
  "site": { /* updated config */ }
}
```

**Common Updates**:
```json
// Disable site
{ "enabled": false }

// Change max pages
{ "overrides": { "max_pages": 100 } }

// Update selectors
{ "selectors": { "card": ".new-selector" } }
```

#### `DELETE /api/sites/{site_key}`

**Purpose**: Remove a site from configuration

**Postman Request**:
- **Method**: DELETE
- **URL**: `{{base_url}}/sites/testsite`

**Expected Response**:
```json
{
  "success": true,
  "message": "Site 'testsite' deleted successfully"
}
```

**Warning**: Permanently removes site from `config.yaml`

**Testing Tip**: Delete the "testsite" you added earlier

#### `PATCH /api/sites/{site_key}/toggle`

**Purpose**: Quick enable/disable toggle

**Postman Request**:
- **Method**: PATCH
- **URL**: `{{base_url}}/sites/npc/toggle`

**Expected Response**:
```json
{
  "success": true,
  "message": "Site 'npc' is now disabled",
  "enabled": false
}
```

**Testing Flow**:
1. First call → Disables (if was enabled)
2. Second call → Enables (if was disabled)
3. Third call → Disables again (toggle)

---

### 4. Logs & Errors (3 endpoints)

#### `GET /api/logs`

**Purpose**: View recent log entries

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/logs?limit=100&level=INFO`

**Query Params**:
- `limit`: Number of lines (default: 100)
- `level`: Filter by level (INFO, WARNING, ERROR, DEBUG)

**Expected Response**:
```json
{
  "total_lines": 500,
  "returned_lines": 100,
  "logs": [
    {
      "timestamp": "2025-10-18 16:00:00",
      "level": "INFO",
      "message": "Scraping npc started"
    }
  ]
}
```

**Test Variations**:
- `?limit=50` → Last 50 lines
- `?level=ERROR` → Only errors
- `?level=WARNING` → Only warnings

#### `GET /api/logs/errors`

**Purpose**: Get only ERROR level logs

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/logs/errors?limit=50`

**Expected Response**:
```json
{
  "total_errors": 12,
  "errors": [
    {
      "timestamp": "2025-10-18 15:00:00",
      "level": "ERROR",
      "message": "Failed to scrape lamudi: Connection timeout"
    }
  ]
}
```

**Success Criteria**: Only ERROR level entries returned

#### `GET /api/logs/site/{site_key}`

**Purpose**: Get logs for specific site

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/logs/site/npc?limit=50`

**Expected Response**:
```json
{
  "site": "npc",
  "total_lines": 80,
  "logs": [
    {
      "timestamp": "2025-10-18 16:00:00",
      "level": "INFO",
      "message": "Scraping npc completed: 750 listings"
    }
  ]
}
```

**Test Different Sites**:
- `/api/logs/site/npc` → NPC logs
- `/api/logs/site/propertypro` → PropertyPro logs

---

### 5. Data Query (4 endpoints)

#### `GET /api/data/sites`

**Purpose**: List available data files

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/data/sites`

**Expected Response**:
```json
{
  "total_sites": 25,
  "sites": [
    {
      "site_key": "npc",
      "site_name": "Nigeria Property Centre",
      "files": [
        {
          "filename": "2025-10-18_15-30-00_npc.csv",
          "size_bytes": 250000,
          "created_at": "2025-10-18T15:30:00",
          "record_count": 750
        }
      ]
    }
  ]
}
```

**Success Criteria**: Shows all sites with exported data files

#### `GET /api/data/sites/{site_key}`

**Purpose**: Get actual scraped data for a site

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/data/sites/npc?limit=50&offset=0&format=json`

**Query Params**:
- `limit`: Number of records (default: 100)
- `offset`: Pagination offset (default: 0)
- `format`: "json" or "csv" (default: json)

**Expected Response**:
```json
{
  "site": "npc",
  "total_records": 750,
  "returned_records": 50,
  "offset": 0,
  "data": [
    {
      "title": "3 Bedroom Flat in Lekki",
      "price": "50000000",
      "location": "Lekki Phase 1",
      "property_type": "Flat",
      "bedrooms": 3,
      "bathrooms": 2,
      "listing_url": "https://nigeriapropertycentre.com/...",
      "scrape_timestamp": "2025-10-18T15:30:00"
    }
  ]
}
```

**Pagination Testing**:
- `?limit=50&offset=0` → First 50 records
- `?limit=50&offset=50` → Records 51-100
- `?limit=50&offset=100` → Records 101-150

#### `GET /api/data/master`

**Purpose**: Get data from consolidated master workbook

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/data/master?site=npc&limit=100`

**Query Params**:
- `site` (optional): Filter by site sheet
- `limit`: Number of records (default: 100)
- `offset`: Pagination (default: 0)

**Expected Response**:
```json
{
  "source": "MASTER_CLEANED_WORKBOOK.xlsx",
  "sheet": "npc",
  "total_sheets": 25,
  "total_records": 431,
  "returned_records": 100,
  "data": [ /* property listings */ ]
}
```

**Test Variations**:
- No `site` param → Returns all data from all sheets
- `?site=npc` → Only NPC sheet
- `?site=propertypro` → Only PropertyPro sheet

#### `GET /api/data/search`

**Purpose**: Search across all scraped data

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/data/search?query=lekki&property_type=flat&min_price=30000000&max_price=60000000&limit=50`

**Query Params** (All Optional):
- `query`: Full-text search (title + location)
- `property_type`: Filter by type (flat, house, land, etc.)
- `location`: Filter by location
- `min_price`: Minimum price
- `max_price`: Maximum price
- `bedrooms`: Number of bedrooms
- `site`: Filter by source site
- `limit`: Results limit (default: 50)
- `offset`: Pagination (default: 0)

**Expected Response**:
```json
{
  "query": "lekki",
  "filters_applied": {
    "property_type": "flat",
    "min_price": 30000000,
    "max_price": 60000000
  },
  "total_matches": 125,
  "returned_records": 50,
  "results": [ /* matching properties */ ]
}
```

**Search Examples**:
```
// Find all properties in Lekki
?query=lekki

// 3-bedroom flats under 50M
?property_type=flat&bedrooms=3&max_price=50000000

// Land in Victoria Island
?query=victoria island&property_type=land

// Properties from specific site
?site=npc&limit=100
```

---

### 6. Statistics (3 endpoints)

#### `GET /api/stats/overview`

**Purpose**: Overall statistics summary

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/stats/overview`

**Expected Response**:
```json
{
  "total_sites": 50,
  "enabled_sites": 5,
  "total_listings": 12450,
  "total_files": 75,
  "last_scrape": "2025-10-18T15:00:00",
  "total_scrapes": 25,
  "average_listings_per_site": 248.6,
  "storage_used_mb": 42.5
}
```

**Success Criteria**: All metrics are numbers, last_scrape is recent

#### `GET /api/stats/sites`

**Purpose**: Per-site performance statistics

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/stats/sites`

**Expected Response**:
```json
{
  "sites": [
    {
      "site_key": "npc",
      "site_name": "Nigeria Property Centre",
      "enabled": true,
      "total_scrapes": 10,
      "last_scrape": "2025-10-18T15:00:00",
      "last_count": 750,
      "average_count": 720,
      "total_listings": 7200,
      "health_status": "healthy",
      "avg_scrape_duration_seconds": 900
    }
  ]
}
```

**Health Status Values**:
- `healthy`: Scraped recently, good count
- `warning`: Scraped but low count
- `critical`: Not scraped recently or errors

#### `GET /api/stats/trends`

**Purpose**: Historical trends over time

**Postman Request**:
- **Method**: GET
- **URL**: `{{base_url}}/stats/trends?days=7`

**Query Params**:
- `days`: Number of days to analyze (default: 7)

**Expected Response**:
```json
{
  "period_days": 7,
  "start_date": "2025-10-11",
  "end_date": "2025-10-18",
  "trends": [
    {
      "date": "2025-10-18",
      "total_listings": 1500,
      "sites_scraped": 5,
      "scrapes_count": 3
    }
  ],
  "growth_rate": 12.5,
  "most_active_site": "npc"
}
```

**Test Variations**:
- `?days=1` → Today only
- `?days=7` → Last week
- `?days=30` → Last month

---

## Common Use Cases

### Use Case 1: Quick Test Scrape

**Goal**: Scrape one site with minimal pages to verify everything works

**Steps**:
1. `POST /api/scrape/start`
   ```json
   {
     "sites": ["npc"],
     "max_pages": 2,
     "geocoding": false
   }
   ```
2. Wait 30 seconds
3. `GET /api/scrape/status` → Verify completed
4. `GET /api/data/sites/npc?limit=10` → View results

**Expected Time**: 1-2 minutes

---

### Use Case 2: Frontend Trigger Workflow

**Goal**: Simulate frontend triggering a scrape and monitoring progress

**Steps**:
1. **User clicks "Scrape Now" button**
   → Frontend calls `POST /api/scrape/start`

2. **Frontend polls status every 10 seconds**
   → `GET /api/scrape/status` until `running: false`

3. **Display logs in real-time**
   → `GET /api/logs?limit=50` every 10 seconds

4. **Show results when complete**
   → `GET /api/data/sites/npc`

**Postman Testing**:
- Start scrape → Get `pid`
- Call status endpoint 5-6 times (manually simulate polling)
- Check logs after each status call
- View data when status shows `running: false`

---

### Use Case 3: Dynamic Site Management

**Goal**: Add a new site from frontend UI without touching code

**Steps**:
1. **User fills form**: Site name, URL, selectors
2. **Frontend submits**: `POST /api/sites`
   ```json
   {
     "key": "newsite",
     "name": "New Site",
     "url": "https://newsite.com",
     "enabled": true,
     "parser": "specials",
     "selectors": { /* from form */ }
   }
   ```
3. **Verify addition**: `GET /api/sites` → See new site
4. **Test scrape**: `POST /api/scrape/start` with new site
5. **Check results**: `GET /api/data/sites/newsite`

**Result**: New site added to `config.yaml` automatically

---

### Use Case 4: Search Property Listings

**Goal**: Client wants to find 3-bedroom flats in Lekki under ₦50M

**Steps**:
1. **Frontend search form** → User enters:
   - Location: "Lekki"
   - Property Type: "Flat"
   - Bedrooms: 3
   - Max Price: 50,000,000

2. **API Call**: `GET /api/data/search?query=lekki&property_type=flat&bedrooms=3&max_price=50000000`

3. **Display results** → Frontend shows matching properties

**Postman Test**:
```
GET {{base_url}}/data/search?query=lekki&property_type=flat&bedrooms=3&max_price=50000000&limit=20
```

---

## Troubleshooting

### Issue: "Connection Refused" Error

**Problem**: Cannot connect to API

**Solution**:
1. Verify API server is running: `python api_server.py`
2. Check server output shows: `Running on http://127.0.0.1:5000`
3. Test with curl: `curl http://localhost:5000/api/health`
4. Check firewall isn't blocking port 5000

---

### Issue: "Module Not Found" When Starting Server

**Problem**: Missing dependencies

**Solution**:
```bash
pip install flask flask-cors pandas
```

---

### Issue: Empty Response from Data Endpoints

**Problem**: No data returned from `/api/data/sites/npc`

**Solution**:
1. Check if any scraping has been done: `GET /api/data/sites`
2. If no files, run a scrape first: `POST /api/scrape/start`
3. Wait for scrape to complete: `GET /api/scrape/status`
4. Try data endpoint again

---

### Issue: "Site Not Found" Error

**Problem**: Adding site with duplicate key

**Solution**:
- Use unique site keys
- Check existing sites first: `GET /api/sites`
- Delete duplicate if needed: `DELETE /api/sites/{key}`

---

### Issue: Scraping Never Completes

**Problem**: Status always shows `running: true`

**Solution**:
1. Check logs: `GET /api/logs/errors` → Look for errors
2. Stop stuck process: `POST /api/scrape/stop`
3. Start with smaller parameters:
   ```json
   {
     "sites": ["npc"],
     "max_pages": 2,
     "geocoding": false
   }
   ```

---

## Integration with Frontend

### Next.js Example

**Trigger Scrape from Frontend**:

```typescript
// app/api/trigger-scrape.ts
export async function POST(request: Request) {
  const { sites, max_pages } = await request.json();

  const response = await fetch('http://localhost:5000/api/scrape/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sites, max_pages, geocoding: true })
  });

  return response.json();
}
```

**Monitor Status with SWR**:

```typescript
// hooks/useScrapeStatus.ts
import useSWR from 'swr';

export function useScrapeStatus() {
  const { data, error } = useSWR(
    'http://localhost:5000/api/scrape/status',
    fetcher,
    { refreshInterval: 5000 } // Poll every 5 seconds
  );

  return { status: data, isLoading: !error && !data, error };
}
```

**Display Data**:

```typescript
// components/PropertyList.tsx
const { data } = useSWR('http://localhost:5000/api/data/sites/npc?limit=50');

return (
  <div>
    {data?.data.map(property => (
      <PropertyCard key={property.listing_url} property={property} />
    ))}
  </div>
);
```

---

## Summary

### Quick Reference: All 23 Endpoints

| Category | Endpoint | Method | Purpose |
|----------|----------|--------|---------|
| **Health** | `/api/health` | GET | Health check |
| **Scraping** | `/api/scrape/start` | POST | Start scraping |
| | `/api/scrape/status` | GET | Check status |
| | `/api/scrape/stop` | POST | Stop scraping |
| | `/api/scrape/history` | GET | View history |
| **Sites** | `/api/sites` | GET | List all sites |
| | `/api/sites/{key}` | GET | Get site details |
| | `/api/sites` | POST | Add new site |
| | `/api/sites/{key}` | PUT | Update site |
| | `/api/sites/{key}` | DELETE | Delete site |
| | `/api/sites/{key}/toggle` | PATCH | Toggle enable/disable |
| **Logs** | `/api/logs` | GET | Get logs |
| | `/api/logs/errors` | GET | Get errors only |
| | `/api/logs/site/{key}` | GET | Site-specific logs |
| **Data** | `/api/data/sites` | GET | List data files |
| | `/api/data/sites/{key}` | GET | Get site data |
| | `/api/data/master` | GET | Get master workbook |
| | `/api/data/search` | GET | Search all data |
| **Stats** | `/api/stats/overview` | GET | Overall stats |
| | `/api/stats/sites` | GET | Per-site stats |
| | `/api/stats/trends` | GET | Historical trends |

---

**Testing Complete?** ✅

After testing all endpoints in Postman, you can confidently hand this collection to your frontend developer. They'll have everything they need to integrate the API quickly and correctly.

**Questions?** Check troubleshooting section or review individual endpoint documentation above.

---

**Created**: 2025-10-18
**Version**: 1.0.0
**Author**: Real Estate Scraper Backend Team
