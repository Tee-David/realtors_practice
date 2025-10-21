# Frontend Integration Guide

**Date**: October 21, 2025
**API Version**: 2.2
**Total Endpoints**: 69 (62 Core + 7 Email Notifications)

---

## Quick Start

### 1. API Base URL

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
// Production: https://your-domain.com/api
```

### 2. Basic Setup (JavaScript/TypeScript)

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
```

### 3. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## Priority Endpoints (MUST IMPLEMENT)

These are the essential endpoints your frontend MUST integrate to provide core functionality.

### 1. Start Scraping ⭐⭐⭐⭐⭐

**Endpoint**: `POST /api/scrape/start`

**Purpose**: Trigger scraping for selected sites

**Request**:
```javascript
const startScraping = async (sites, options = {}) => {
  const response = await api.post('/scrape/start', {
    sites: sites,           // ['npc', 'propertypro', 'jiji']
    max_pages: options.maxPages || 20,
    geocoding: options.geocoding !== false,
  });
  return response.data;
};

// Usage
const result = await startScraping(['npc', 'propertypro'], {
  maxPages: 30,
  geocoding: true
});
```

**Response**:
```json
{
  "status": "started",
  "message": "Scraping started for 2 sites",
  "sites": ["npc", "propertypro"],
  "start_time": "2025-10-20T10:30:00",
  "process_id": 12345
}
```

**UI Recommendation**:
- Site selection dropdown/checkboxes
- "Max pages" slider (10-50)
- "Enable geocoding" checkbox
- "Start Scraping" button

---

### 2. Check Scraping Status ⭐⭐⭐⭐⭐

**Endpoint**: `GET /api/scrape/status`

**Purpose**: Monitor scraping progress in real-time

**Request**:
```javascript
const getScrapingStatus = async () => {
  const response = await api.get('/scrape/status');
  return response.data;
};

// Poll every 5 seconds while scraping
const pollStatus = () => {
  const interval = setInterval(async () => {
    const status = await getScrapingStatus();

    if (status.status === 'idle') {
      clearInterval(interval);
      // Scraping complete
    }

    // Update UI with progress
    updateProgressBar(status);
  }, 5000);
};
```

**Response**:
```json
{
  "status": "running",
  "current_site": "propertypro",
  "sites_completed": 1,
  "total_sites": 2,
  "start_time": "2025-10-20T10:30:00",
  "elapsed_seconds": 320,
  "is_running": true
}
```

**UI Recommendation**:
- Progress bar showing sites_completed/total_sites
- Current site being scraped
- Elapsed time counter
- Auto-refresh every 5 seconds

---

### 3. Search Properties ⭐⭐⭐⭐⭐

**Endpoint**: `POST /api/query`

**Purpose**: Advanced property search with filters

**Request**:
```javascript
const searchProperties = async (filters) => {
  const response = await api.post('/query', {
    filters: {
      bedrooms: { gte: 3 },                    // 3+ bedrooms
      price: { lte: 30000000 },                // Under ₦30M
      location: { contains: 'Lekki' },         // Location contains "Lekki"
      property_type: { contains: 'Flat' },
    },
    sort: { field: 'price', order: 'asc' },
    limit: 50,
    offset: 0,
  });
  return response.data;
};

// Usage
const results = await searchProperties({
  bedrooms: { gte: 3 },
  price: { between: [20000000, 40000000] },
  location: { contains: 'Lekki' },
});
```

**Response**:
```json
{
  "results": [
    {
      "title": "3 Bedroom Flat in Lekki Phase 1",
      "price": 25000000,
      "location": "Lekki Phase 1, Lagos",
      "bedrooms": 3,
      "bathrooms": 3,
      "property_type": "Flat",
      "listing_url": "https://...",
      "source": "npc",
      "images": ["url1", "url2"],
      "coordinates": {"lat": 6.4474, "lng": 3.4701}
    }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

**Filter Operators**:
- `eq` - Equal to
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `between` - Between two values [min, max]
- `contains` - Text contains (case-insensitive)

**UI Recommendation**:
- Search form with:
  - Bedroom dropdown (1-6+)
  - Price range slider (min/max)
  - Location autocomplete
  - Property type dropdown
  - "Search" button
- Results grid with pagination
- Sort options (price, date, bedrooms)

---

### 4. Natural Language Search ⭐⭐⭐⭐⭐

**Endpoint**: `POST /api/search/natural`

**Purpose**: Search with plain English queries

**Request**:
```javascript
const naturalSearch = async (query) => {
  const response = await api.post('/search/natural', {
    query: query,
    limit: 50,
  });
  return response.data;
};

// Usage
const results = await naturalSearch("3 bedroom flat in Lekki under 30 million");
```

**Response**:
```json
{
  "query": "3 bedroom flat in Lekki under 30 million",
  "parsed": {
    "filters": {
      "bedrooms": { "gte": 3 },
      "property_type": { "contains": "Flat" },
      "location": { "contains": "Lekki" },
      "price": { "lte": 30000000 }
    },
    "confidence": 0.95
  },
  "results": [...],
  "total": 87
}
```

**UI Recommendation**:
- Single search bar with placeholder: "e.g., 3 bedroom flat in Lekki under 30M"
- Auto-suggestions as user types
- Show parsed filters to user for confirmation
- Confidence indicator

---

### 5. Get All Properties ⭐⭐⭐⭐

**Endpoint**: `GET /api/data/master`

**Purpose**: Fetch all scraped properties (for browse/listing pages)

**Request**:
```javascript
const getAllProperties = async (limit = 100, offset = 0) => {
  const response = await api.get('/data/master', {
    params: { limit, offset }
  });
  return response.data;
};

// Usage with pagination
const page1 = await getAllProperties(50, 0);   // First 50
const page2 = await getAllProperties(50, 50);  // Next 50
```

**Response**:
```json
{
  "data": [...],
  "total_records": 1680,
  "limit": 100,
  "offset": 0
}
```

**UI Recommendation**:
- Default landing page shows recent properties
- Pagination controls (Next/Prev, page numbers)
- Infinite scroll option
- "Load more" button

---

## Optional Endpoints (NICE TO HAVE)

These endpoints add advanced features but aren't required for basic functionality.

### 6. Price Drops ⭐⭐⭐⭐

**Endpoint**: `GET /api/price-drops`

**Purpose**: Show properties with recent price reductions

**Request**:
```javascript
const getPriceDrops = async (minDropPercent = 10, days = 30) => {
  const response = await api.get('/price-drops', {
    params: {
      min_drop_pct: minDropPercent,
      days: days
    }
  });
  return response.data;
};
```

**Response**:
```json
{
  "price_drops": [
    {
      "property_id": "hash_abc123",
      "title": "3 Bedroom Flat",
      "old_price": 30000000,
      "new_price": 25000000,
      "price_drop": 5000000,
      "price_drop_pct": 16.67,
      "days_since_drop": 3
    }
  ],
  "total": 15
}
```

**UI Recommendation**:
- "Price Drops" page or widget
- Badge showing "16% OFF" on property cards
- Filter by minimum drop percentage

---

### 7. Saved Searches ⭐⭐⭐⭐

**Endpoint**: `POST /api/searches` (Create), `GET /api/searches` (List)

**Purpose**: Save user search criteria for alerts

**Create Search**:
```javascript
const saveSearch = async (userId, searchName, criteria) => {
  const response = await api.post('/searches', {
    user_id: userId,
    name: searchName,
    criteria: criteria,
    alert_frequency: 'daily',  // or 'weekly', 'instant'
  });
  return response.data;
};

// Usage
const saved = await saveSearch('user123', 'Lekki Flats', {
  bedrooms: { gte: 3 },
  location: { contains: 'Lekki' },
  price: { lte: 30000000 },
});
```

**List Saved Searches**:
```javascript
const getSavedSearches = async (userId) => {
  const response = await api.get('/searches', {
    params: { user_id: userId }
  });
  return response.data;
};
```

**UI Recommendation**:
- "Save this search" button on search results page
- User dashboard showing saved searches
- Alert frequency selector (instant/daily/weekly)
- "New matches" badge when new properties match criteria

---

### 8. Health Monitoring ⭐⭐⭐

**Endpoint**: `GET /api/health/overall`

**Purpose**: Admin dashboard showing site performance

**Request**:
```javascript
const getSystemHealth = async () => {
  const response = await api.get('/health/overall');
  return response.data;
};
```

**Response**:
```json
{
  "overall_status": "healthy",
  "total_sites": 50,
  "healthy_sites": 45,
  "warning_sites": 3,
  "critical_sites": 2,
  "total_scrapes_7d": 150,
  "total_listings_7d": 12500,
  "last_updated": "2025-10-20T10:30:00"
}
```

**UI Recommendation**:
- Admin dashboard page
- Color-coded status indicators (green/yellow/red)
- Charts showing trends over time
- Alert notifications for critical sites

---

### 9. Quality Scoring ⭐⭐⭐

**Endpoint**: `POST /api/quality/score`

**Purpose**: Filter properties by data quality

**Request**:
```javascript
const filterByQuality = async (listings, minScore = 0.7) => {
  const response = await api.post('/quality/score', {
    listings: listings,
    min_score: minScore,
  });
  return response.data;
};
```

**Response**:
```json
{
  "high_quality": 42,
  "medium_quality": 15,
  "low_quality": 8,
  "filtered_listings": [...]  // Only high-quality listings
}
```

**UI Recommendation**:
- "Quality filter" toggle (show only high-quality listings)
- Quality badge on property cards (High/Medium/Low)
- Admin setting for minimum quality threshold

---

### 10. Market Trends ⭐⭐⭐

**Endpoint**: `GET /api/market-trends`

**Purpose**: Show price trends and market insights

**Request**:
```javascript
const getMarketTrends = async (days = 30, location = null) => {
  const response = await api.get('/market-trends', {
    params: { days, location }
  });
  return response.data;
};
```

**Response**:
```json
{
  "trend": "stable",
  "avg_price_change_pct": 2.3,
  "total_price_changes": 45,
  "price_increases": 28,
  "price_decreases": 17,
  "hottest_locations": ["Lekki", "Ikoyi", "VI"]
}
```

**UI Recommendation**:
- "Market Insights" page
- Charts showing price trends
- "Hot locations" list
- Average price change indicator

---

## Utility Endpoints (AS NEEDED)

### Site Management

**List All Sites**: `GET /api/sites`
```javascript
const getAllSites = async () => {
  const response = await api.get('/sites');
  return response.data;
};
```

**Enable/Disable Site**: `PATCH /api/sites/<site_key>/toggle`
```javascript
const toggleSite = async (siteKey, enabled) => {
  const response = await api.patch(`/sites/${siteKey}/toggle`, {
    enabled: enabled
  });
  return response.data;
};
```

---

### Logs & Statistics

**Get Recent Logs**: `GET /api/logs`
```javascript
const getLogs = async (limit = 100, level = 'ERROR') => {
  const response = await api.get('/logs', {
    params: { limit, level }
  });
  return response.data;
};
```

**Get Statistics**: `GET /api/stats/overview`
```javascript
const getStats = async () => {
  const response = await api.get('/stats/overview');
  return response.data;
};
```

---

## Complete API Reference

### Scraping Management (4 endpoints)
- `POST /api/scrape/start` - Start scraping ⭐⭐⭐⭐⭐
- `GET /api/scrape/status` - Get status ⭐⭐⭐⭐⭐
- `POST /api/scrape/stop` - Stop scraping ⭐⭐⭐
- `GET /api/scrape/history` - Get history ⭐⭐

### Site Configuration (6 endpoints)
- `GET /api/sites` - List all sites ⭐⭐⭐
- `GET /api/sites/<key>` - Get specific site ⭐⭐
- `POST /api/sites` - Add new site ⭐⭐
- `PUT /api/sites/<key>` - Update site ⭐⭐
- `DELETE /api/sites/<key>` - Delete site ⭐
- `PATCH /api/sites/<key>/toggle` - Enable/disable ⭐⭐⭐

### Data Query (6 endpoints)
- `GET /api/data/sites` - List data files ⭐⭐
- `GET /api/data/sites/<key>` - Get site data ⭐⭐⭐
- `GET /api/data/master` - Get master workbook ⭐⭐⭐⭐⭐
- `GET /api/data/search` - Search data ⭐⭐⭐
- `POST /api/query` - Advanced query ⭐⭐⭐⭐⭐
- `GET /api/query/summary` - Query summary ⭐⭐

### Price History (4 endpoints)
- `GET /api/price-history/<id>` - Get price history ⭐⭐⭐
- `GET /api/price-drops` - Get price drops ⭐⭐⭐⭐
- `GET /api/stale-listings` - Get stale listings ⭐⭐⭐
- `GET /api/market-trends` - Market trends ⭐⭐⭐⭐

### Natural Language Search (2 endpoints)
- `POST /api/search/natural` - NL search ⭐⭐⭐⭐⭐
- `GET /api/search/suggestions` - Get suggestions ⭐⭐⭐

### Saved Searches (6 endpoints)
- `GET /api/searches` - List searches ⭐⭐⭐⭐
- `POST /api/searches` - Create search ⭐⭐⭐⭐
- `GET /api/searches/<id>` - Get search ⭐⭐⭐
- `PUT /api/searches/<id>` - Update search ⭐⭐⭐
- `DELETE /api/searches/<id>` - Delete search ⭐⭐⭐
- `GET /api/searches/<id>/stats` - Search stats ⭐⭐⭐

### Health Monitoring (4 endpoints)
- `GET /api/health/overall` - Overall health ⭐⭐⭐
- `GET /api/health/sites/<key>` - Site health ⭐⭐
- `GET /api/health/alerts` - Active alerts ⭐⭐⭐
- `GET /api/health/top-performers` - Top sites ⭐⭐

### Duplicates & Quality (2 endpoints)
- `POST /api/duplicates/detect` - Detect duplicates ⭐⭐
- `POST /api/quality/score` - Score quality ⭐⭐⭐

### Logs & Statistics (8 endpoints)
- `GET /api/logs` - Get logs ⭐⭐
- `GET /api/logs/errors` - Get errors ⭐⭐⭐
- `GET /api/logs/site/<key>` - Site logs ⭐⭐
- `GET /api/stats/overview` - Overview ⭐⭐⭐
- `GET /api/stats/sites` - Site stats ⭐⭐
- `GET /api/stats/trends` - Trends ⭐⭐⭐

### Utilities (4 endpoints)
- `GET /api/health` - Health check ⭐⭐⭐⭐⭐
- `POST /api/validate/url` - Validate URL ⭐
- `POST /api/filter/location` - Filter location ⭐⭐
- `POST /api/rate-limit/check` - Rate limit check ⭐

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "error": "Error message",
  "status": 400,
  "details": "Additional error details"
}
```

**Common HTTP Status Codes**:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (site/resource doesn't exist)
- `500` - Internal Server Error

**Example Error Handler**:
```javascript
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;

    if (status === 400) {
      alert(`Invalid request: ${data.error}`);
    } else if (status === 404) {
      alert(`Not found: ${data.error}`);
    } else {
      alert(`Server error: ${data.error}`);
    }
  } else if (error.request) {
    // Request made but no response
    alert('Server not responding. Please try again.');
  } else {
    // Request setup error
    alert('Request failed. Please check your connection.');
  }
};

// Usage
try {
  const results = await searchProperties(filters);
} catch (error) {
  handleApiError(error);
}
```

---

## TypeScript Types

```typescript
// types/api.ts

export interface Property {
  title: string;
  price: number;
  location: string;
  listing_url: string;
  source: string;
  bedrooms?: number;
  bathrooms?: number;
  property_type?: string;
  images?: string[];
  coordinates?: {
    lat: number;
    lng: number;
  };
  scrape_timestamp?: string;
  hash?: string;
}

export interface SearchFilters {
  bedrooms?: { eq?: number; gte?: number; lte?: number; between?: [number, number] };
  price?: { eq?: number; gte?: number; lte?: number; between?: [number, number] };
  location?: { contains?: string; eq?: string };
  property_type?: { contains?: string; eq?: string };
}

export interface SearchResponse {
  results: Property[];
  total: number;
  limit: number;
  offset: number;
}

export interface ScrapeStatus {
  status: 'idle' | 'running' | 'completed' | 'error';
  current_site?: string;
  sites_completed: number;
  total_sites: number;
  start_time?: string;
  elapsed_seconds?: number;
  is_running: boolean;
}

export interface SavedSearch {
  id: string;
  user_id: string;
  name: string;
  criteria: SearchFilters;
  alert_frequency: 'instant' | 'daily' | 'weekly';
  created_at: string;
  last_checked?: string;
}

export interface PriceDrop {
  property_id: string;
  title: string;
  location: string;
  old_price: number;
  new_price: number;
  price_drop: number;
  price_drop_pct: number;
  days_since_drop: number;
}
```

---

## React Hooks (Optional)

Custom hooks to simplify API integration:

```typescript
// hooks/useApi.ts
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export const useScrapingStatus = (pollInterval = 5000) => {
  const [status, setStatus] = useState<ScrapeStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await api.get('/scrape/status');
        setStatus(response.data);

        // Stop polling if not running
        if (response.data.status === 'idle') {
          return false;
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval]);

  return { status, loading };
};

export const useProperties = (filters: SearchFilters, limit = 50) => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchProperties = async () => {
      setLoading(true);
      try {
        const response = await api.post('/query', {
          filters,
          limit,
          offset: 0,
        });
        setProperties(response.data.results);
        setTotal(response.data.total);
      } catch (error) {
        console.error('Failed to fetch properties:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, [filters, limit]);

  return { properties, loading, total };
};

export const usePriceDrops = (minDropPct = 10, days = 30) => {
  const [drops, setDrops] = useState<PriceDrop[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDrops = async () => {
      setLoading(true);
      try {
        const response = await api.get('/price-drops', {
          params: { min_drop_pct: minDropPct, days },
        });
        setDrops(response.data.price_drops);
      } catch (error) {
        console.error('Failed to fetch price drops:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDrops();
  }, [minDropPct, days]);

  return { drops, loading };
};
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# List all sites
curl http://localhost:5000/api/sites

# Start scraping
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 10}'

# Get scraping status
curl http://localhost:5000/api/scrape/status

# Search properties
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "bedrooms": {"gte": 3},
      "price": {"lte": 30000000},
      "location": {"contains": "Lekki"}
    },
    "limit": 10
  }'

# Natural language search
curl -X POST http://localhost:5000/api/search/natural \
  -H "Content-Type: application/json" \
  -d '{"query": "3 bedroom flat in Lekki under 30 million"}'

# Get price drops
curl "http://localhost:5000/api/price-drops?min_drop_pct=10&days=30"
```

---

## Firestore Query (Fast Cloud Database) ⭐⭐⭐⭐⭐

### Query Firestore Database

**Endpoint**: `POST /api/firestore/query`

**Purpose**: Query properties stored in Firebase Firestore with advanced filtering

**Request**:
```javascript
const queryFirestore = async (filters, options = {}) => {
  const response = await api.post('/firestore/query', {
    filters: filters,
    limit: options.limit || 50,
    sort_by: options.sortBy || 'scrape_timestamp',
    sort_desc: options.sortDesc !== false
  });
  return response.data;
};

// Usage
const results = await queryFirestore({
  location: 'Lekki',
  price_min: 5000000,
  price_max: 50000000,
  bedrooms_min: 3,
  property_type: 'Flat',
  quality_score_min: 0.7
});
```

**Available Filters**:
- `location` - Exact location match
- `price_min`, `price_max` - Price range
- `bedrooms_min`, `bathrooms_min` - Minimum rooms
- `property_type` - Property type (e.g., "Flat", "House", "Land")
- `source` - Data source (e.g., "npc", "jiji", "propertypro")
- `quality_score_min` - Minimum quality score (0.0 to 1.0)

**Response**:
```json
{
  "results": [
    {
      "title": "3 Bedroom Flat in Lekki Phase 1",
      "price": 25000000,
      "location": "Lekki",
      "bedrooms": 3,
      "bathrooms": 3,
      "property_type": "Flat",
      "listing_url": "https://...",
      "source": "npc",
      "quality_score": 0.85,
      "images": "url1,url2",
      "scrape_timestamp": "2025-10-21T10:00:00"
    }
  ],
  "count": 142,
  "filters_applied": {
    "location": "Lekki",
    "price_min": 5000000,
    "price_max": 50000000,
    "bedrooms_min": 3
  }
}
```

**UI Recommendation**:
- Fast search with Firestore (no need to download Excel files)
- Real-time results with filtering
- Quality score filter to show only high-quality listings
- Location-based filtering

### 2. Query Archived Properties (Price Prediction) ⭐⭐⭐⭐⭐

**Endpoint**: `POST /api/firestore/query-archive`

**Purpose**: Query ARCHIVED properties for price prediction & historical analysis

Archived properties are listings that haven't been seen in recent scrapes (>30 days old). These are automatically moved to `properties_archive` collection to keep the active collection clean while preserving historical data.

**Use Cases**:
- Price prediction models (train on historical data)
- Market trend analysis
- Track price changes over time
- Historical property database

**Request**: Same as `/api/firestore/query`

**Response**:
```json
{
  "results": [...],
  "count": 1250,
  "collection": "properties_archive",
  "note": "These are archived (stale) properties for historical analysis"
}
```

**UI Recommendation**:
- Separate "Historical Data" section for analysts/developers
- Export historical data for ML models
- Price trend visualization over time

---

## Advanced Export System ⭐⭐⭐⭐

### 1. Generate Filtered Export

**Endpoint**: `POST /api/export/generate`

**Purpose**: Create custom filtered exports in multiple formats

**Request**:
```javascript
const generateExport = async (format, filters, options = {}) => {
  const response = await api.post('/export/generate', {
    format: format,  // 'excel', 'csv', 'json', 'parquet'
    filters: filters,
    columns: options.columns || [],  // Empty = all columns
    include_images: options.includeImages !== undefined ? options.includeImages : false,
    filename: options.filename || 'export'
  });
  return response.data;
};

// Usage - Export Lekki properties to Excel
const exportResult = await generateExport('excel', {
  location: 'Lekki',
  price_max: 50000000,
  bedrooms_min: 3
}, {
  columns: ['title', 'price', 'location', 'bedrooms', 'listing_url'],
  filename: 'lekki_properties'
});

// Download the file
window.location.href = exportResult.download_url;
```

**Supported Formats**:
- `excel` - Excel workbook (.xlsx)
- `csv` - Comma-separated values (.csv)
- `json` - JSON array (.json)
- `parquet` - Apache Parquet (.parquet)

**Response**:
```json
{
  "success": true,
  "download_url": "/api/export/download/lekki_properties_20251021.xlsx",
  "filename": "lekki_properties_20251021.xlsx",
  "format": "excel",
  "record_count": 245,
  "file_size_mb": 2.4,
  "expires_in_seconds": 3600
}
```

### 2. Download Export

**Endpoint**: `GET /api/export/download/<filename>`

**Purpose**: Download a generated export file

**Request**:
```javascript
const downloadExport = (filename) => {
  window.location.href = `/api/export/download/${filename}`;
};

// Usage
downloadExport('lekki_properties_20251021.xlsx');
```

### 3. Get Available Export Formats

**Endpoint**: `GET /api/export/formats`

**Purpose**: List supported export formats

**Response**:
```json
{
  "formats": ["excel", "csv", "json", "parquet"],
  "default_format": "excel",
  "max_records_per_export": 100000
}
```

**UI Recommendation**:
- Export button with format dropdown
- Show record count before exporting
- Progress indicator during export generation
- Auto-download when ready

---

## Scheduled Scraping ⭐⭐⭐⭐

### 1. Schedule Future Scrape

**Endpoint**: `POST /api/schedule/scrape`

**Purpose**: Schedule a scrape to run at a specific future time

**Request**:
```javascript
const scheduleScrape = async (scheduledTime, options = {}) => {
  const response = await api.post('/schedule/scrape', {
    scheduled_time: scheduledTime,  // ISO format or Unix timestamp
    page_cap: options.pageCap || 20,
    geocode: options.geocode !== undefined ? (options.geocode ? 1 : 0) : 1,
    sites: options.sites || []  // Empty = all enabled sites
  });
  return response.data;
};

// Schedule scrape for tomorrow at 3 PM
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
tomorrow.setHours(15, 0, 0, 0);

const job = await scheduleScrape(tomorrow.toISOString(), {
  pageCap: 10,
  geocode: false,
  sites: ['npc', 'jiji']
});
```

**Response**:
```json
{
  "success": true,
  "job_id": 1,
  "scheduled_time": "2025-10-22T15:00:00Z",
  "delay_seconds": 86400,
  "status": "scheduled",
  "cancel_url": "/api/schedule/jobs/1/cancel",
  "check_status_url": "/api/schedule/jobs/1"
}
```

### 2. List Scheduled Jobs

**Endpoint**: `GET /api/schedule/jobs`

**Purpose**: Get all scheduled scraping jobs

**Request**:
```javascript
const getScheduledJobs = async () => {
  const response = await api.get('/schedule/jobs');
  return response.data;
};
```

**Response**:
```json
{
  "jobs": [
    {
      "job_id": 1,
      "scheduled_time": "2025-10-22T15:00:00Z",
      "page_cap": 10,
      "geocode": 0,
      "sites": ["npc", "jiji"],
      "status": "scheduled",
      "created_at": "2025-10-21T10:00:00Z"
    }
  ],
  "count": 1
}
```

### 3. Get Job Status

**Endpoint**: `GET /api/schedule/jobs/<id>`

**Purpose**: Check status of a specific scheduled job

**Request**:
```javascript
const getJobStatus = async (jobId) => {
  const response = await api.get(`/schedule/jobs/${jobId}`);
  return response.data;
};
```

**Response**:
```json
{
  "job_id": 1,
  "scheduled_time": "2025-10-22T15:00:00Z",
  "page_cap": 10,
  "geocode": 0,
  "sites": ["npc", "jiji"],
  "status": "scheduled",
  "created_at": "2025-10-21T10:00:00Z"
}
```

**Status Values**:
- `scheduled` - Waiting to run
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Execution failed
- `cancelled` - Cancelled by user

### 4. Cancel Scheduled Job

**Endpoint**: `POST /api/schedule/jobs/<id>/cancel`

**Purpose**: Cancel a scheduled job before it runs

**Request**:
```javascript
const cancelJob = async (jobId) => {
  const response = await api.post(`/schedule/jobs/${jobId}/cancel`);
  return response.data;
};
```

**Response**:
```json
{
  "success": true,
  "job_id": 1,
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

**UI Recommendation**:
- Calendar/datetime picker for scheduling
- List of scheduled jobs with countdown timers
- Cancel button for pending jobs
- Status badges (scheduled/running/completed)
- Auto-refresh job list

---

## GitHub Actions Integration (Serverless Deployment)

For serverless scraping using GitHub Actions instead of running a local Flask API server.

### Environment Variables

```bash
# .env.local
GITHUB_TOKEN=ghp_your_personal_access_token_here
GITHUB_OWNER=Tee-David
GITHUB_REPO=realtors_practice
```

### 1. Trigger Scraper Workflow ⭐⭐⭐⭐

**Endpoint**: `POST /api/github/trigger-scrape`

**Purpose**: Trigger GitHub Actions workflow to run scraper in the cloud

**Request**:
```javascript
const triggerGitHubScrape = async (options = {}) => {
  const response = await api.post('/github/trigger-scrape', {
    page_cap: options.pageCap || 20,
    geocode: options.geocode !== undefined ? (options.geocode ? 1 : 0) : 1,
    sites: options.sites || []  // Empty array = all enabled sites
  });
  return response.data;
};

// Usage
const result = await triggerGitHubScrape({
  pageCap: 30,
  geocode: true,
  sites: ['npc', 'propertypro']
});
```

**Response**:
```json
{
  "success": true,
  "message": "Scraper workflow triggered successfully",
  "run_url": "https://github.com/Tee-David/realtors_practice/actions",
  "parameters": {
    "page_cap": 30,
    "geocode": 1,
    "sites": ["npc", "propertypro"]
  }
}
```

**Error Response**:
```json
{
  "error": "Missing GitHub configuration",
  "details": "Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables"
}
```

**UI Recommendation**:
- "Trigger Cloud Scraper" button
- Site selection (multi-select)
- Pages per site slider
- Enable geocoding checkbox
- Link to GitHub Actions page to monitor progress

---

### 2. Get Workflow Runs ⭐⭐⭐⭐

**Endpoint**: `GET /api/github/workflow-runs`

**Purpose**: Monitor GitHub Actions workflow execution status

**Request**:
```javascript
const getWorkflowRuns = async (perPage = 5) => {
  const response = await api.get('/github/workflow-runs', {
    params: { per_page: perPage }
  });
  return response.data;
};

// Usage
const runs = await getWorkflowRuns(10);
```

**Response**:
```json
{
  "workflow_runs": [
    {
      "id": 12345678,
      "name": "Scraper Workflow",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-10-21T10:30:00Z",
      "updated_at": "2025-10-21T10:45:00Z",
      "html_url": "https://github.com/owner/repo/actions/runs/12345678",
      "run_number": 42
    }
  ],
  "total_count": 100
}
```

**Status Values**:
- `queued` - Workflow is waiting to start
- `in_progress` - Workflow is currently running
- `completed` - Workflow has finished

**Conclusion Values** (when status is "completed"):
- `success` - Workflow completed successfully
- `failure` - Workflow failed with errors
- `cancelled` - Workflow was cancelled manually
- `skipped` - Workflow was skipped

**UI Recommendation**:
- Table/list of recent runs with status badges
- Real-time polling (every 30 seconds while runs are active)
- Link to GitHub Actions page for each run
- Status indicators (green for success, red for failure, yellow for in_progress)

---

### 3. Get Artifacts (Scraped Data) ⭐⭐⭐⭐

**Endpoint**: `GET /api/github/artifacts`

**Purpose**: List available scraped data exports from GitHub Actions runs

**Request**:
```javascript
const getArtifacts = async (perPage = 10) => {
  const response = await api.get('/github/artifacts', {
    params: { per_page: perPage }
  });
  return response.data;
};

// Usage
const artifacts = await getArtifacts(20);
```

**Response**:
```json
{
  "artifacts": [
    {
      "id": 987654321,
      "name": "scraper-exports-42",
      "size_in_bytes": 1048576,
      "size_mb": 1.0,
      "created_at": "2025-10-21T10:45:00Z",
      "expired": false,
      "archive_download_url": "https://api.github.com/repos/owner/repo/actions/artifacts/987654321/zip"
    }
  ],
  "total_count": 25
}
```

**UI Recommendation**:
- Table of artifacts with name, size, and creation date
- Download button for each artifact
- Auto-refresh when new runs complete
- Show expiration status (artifacts expire after 30 days)

---

### 4. Download Artifact ⭐⭐⭐

**Endpoint**: `GET /api/github/artifact/<artifact_id>/download`

**Purpose**: Get download URL for a specific artifact

**Request**:
```javascript
const getArtifactDownloadUrl = async (artifactId) => {
  const response = await api.get(`/github/artifact/${artifactId}/download`);
  return response.data;
};

// Download artifact
const downloadArtifact = async (artifactId) => {
  const info = await getArtifactDownloadUrl(artifactId);

  // Frontend must download with Authorization header
  const githubToken = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
  const response = await fetch(info.download_url, {
    headers: {
      'Authorization': `Bearer ${githubToken}`
    }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${info.name}.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
};

// Usage
await downloadArtifact(987654321);
```

**Response**:
```json
{
  "artifact_id": 987654321,
  "name": "scraper-exports-42",
  "download_url": "https://api.github.com/repos/owner/repo/actions/artifacts/987654321/zip",
  "size_mb": 1.0,
  "note": "Use this URL with Authorization header to download"
}
```

**UI Recommendation**:
- Download button that triggers browser download
- Progress indicator during download
- Success/error notifications

---

### GitHub Integration Example Component

```tsx
// components/GitHubScraperControl.tsx
'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

export default function GitHubScraperControl() {
  const [runs, setRuns] = useState([]);
  const [artifacts, setArtifacts] = useState([]);
  const [loading, setLoading] = useState(false);

  const triggerScrape = async () => {
    setLoading(true);
    try {
      const result = await api.post('/github/trigger-scrape', {
        page_cap: 20,
        geocode: 1
      });
      alert(result.message);
      fetchWorkflowRuns();
    } catch (error) {
      alert(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflowRuns = async () => {
    try {
      const { workflow_runs } = await api.get('/github/workflow-runs', {
        params: { per_page: 5 }
      }).then(res => res.data);
      setRuns(workflow_runs);
    } catch (error) {
      console.error('Error fetching runs:', error);
    }
  };

  const fetchArtifacts = async () => {
    try {
      const { artifacts: artifactList } = await api.get('/github/artifacts', {
        params: { per_page: 10 }
      }).then(res => res.data);
      setArtifacts(artifactList);
    } catch (error) {
      console.error('Error fetching artifacts:', error);
    }
  };

  useEffect(() => {
    fetchWorkflowRuns();
    fetchArtifacts();
    const interval = setInterval(() => {
      fetchWorkflowRuns();
      fetchArtifacts();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">GitHub Actions Scraper</h2>

      {/* Trigger Button */}
      <button
        onClick={triggerScrape}
        disabled={loading}
        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:opacity-50 mb-6"
      >
        {loading ? 'Triggering...' : 'Trigger Cloud Scraper'}
      </button>

      {/* Workflow Runs */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-3">Recent Runs</h3>
        <div className="space-y-2">
          {runs.map(run => (
            <div key={run.id} className="border p-3 rounded flex justify-between items-center">
              <div>
                <div className="font-medium">Run #{run.run_number}</div>
                <div className="text-sm text-gray-600">
                  {new Date(run.created_at).toLocaleString()}
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded text-sm ${
                  run.conclusion === 'success' ? 'bg-green-100 text-green-800' :
                  run.conclusion === 'failure' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {run.status === 'completed' ? run.conclusion : run.status}
                </span>
                <a
                  href={run.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline text-sm"
                >
                  View →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Artifacts */}
      <div>
        <h3 className="text-xl font-semibold mb-3">Available Downloads</h3>
        <div className="space-y-2">
          {artifacts.map(artifact => (
            <div key={artifact.id} className="border p-3 rounded flex justify-between items-center">
              <div>
                <div className="font-medium">{artifact.name}</div>
                <div className="text-sm text-gray-600">
                  {artifact.size_mb} MB • {new Date(artifact.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={() => window.open(artifact.archive_download_url, '_blank')}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Email Notifications (SMTP Configuration) ⭐⭐⭐⭐

Configure email notifications to alert users when scrape sessions complete.

### 1. Configure SMTP Settings

**Endpoint**: `POST /api/email/configure`

**Purpose**: Set up SMTP server configuration for sending emails

**Request**:
```javascript
const configureSMTP = async (config) => {
  const response = await api.post('/email/configure', {
    smtp_host: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_user: 'your-email@gmail.com',
    smtp_password: 'your-app-password',
    smtp_use_tls: true,
    smtp_use_ssl: false,
    from_email: 'notifications@example.com',
    from_name: 'Real Estate Scraper'
  });
  return response.data;
};
```

**Response**:
```json
{
  "success": true,
  "message": "SMTP configuration saved successfully",
  "config": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "your-email@gmail.com",
    "from_email": "notifications@example.com",
    "from_name": "Real Estate Scraper"
  }
}
```

**UI Recommendation**:
- SMTP configuration form in settings page
- Fields for host, port, username, password
- TLS/SSL toggle switches
- "Save Configuration" button

---

### 2. Test SMTP Connection

**Endpoint**: `POST /api/email/test-connection`

**Purpose**: Verify SMTP configuration works correctly

**Request**:
```javascript
const testSMTPConnection = async () => {
  const response = await api.post('/email/test-connection');
  return response.data;
};
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully connected to smtp.gmail.com:587",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "authenticated": true
}
```

**UI Recommendation**:
- "Test Connection" button next to configuration form
- Show success/error message
- Green checkmark if successful, red X if failed

---

### 3. Get SMTP Configuration

**Endpoint**: `GET /api/email/config`

**Purpose**: Retrieve current SMTP configuration (password hidden)

**Request**:
```javascript
const getSMTPConfig = async () => {
  const response = await api.get('/email/config');
  return response.data;
};
```

**Response**:
```json
{
  "configured": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-email@gmail.com",
  "from_email": "notifications@example.com",
  "from_name": "Real Estate Scraper",
  "recipients_count": 3
}
```

---

### 4. Manage Email Recipients

**Endpoint**: `GET /api/email/recipients`

**Purpose**: Get list of email addresses that will receive notifications

**Request**:
```javascript
const getRecipients = async () => {
  const response = await api.get('/email/recipients');
  return response.data;
};
```

**Response**:
```json
{
  "recipients": [
    "admin@example.com",
    "manager@example.com",
    "developer@example.com"
  ],
  "count": 3
}
```

---

### 5. Add Email Recipient

**Endpoint**: `POST /api/email/recipients`

**Purpose**: Add a new email address to notification list

**Request**:
```javascript
const addRecipient = async (email) => {
  const response = await api.post('/email/recipients', {
    email: email
  });
  return response.data;
};

// Usage
await addRecipient('newuser@example.com');
```

**Response**:
```json
{
  "success": true,
  "message": "Recipient added successfully",
  "recipients": ["admin@example.com", "newuser@example.com"],
  "count": 2
}
```

**UI Recommendation**:
- Email input field with validation
- "Add" button
- List of current recipients below
- Each recipient should have a "Remove" button

---

### 6. Remove Email Recipient

**Endpoint**: `DELETE /api/email/recipients/<email>`

**Purpose**: Remove an email address from notification list

**Request**:
```javascript
const removeRecipient = async (email) => {
  const response = await api.delete(`/email/recipients/${encodeURIComponent(email)}`);
  return response.data;
};

// Usage
await removeRecipient('olduser@example.com');
```

**Response**:
```json
{
  "success": true,
  "message": "Recipient removed successfully",
  "recipients": ["admin@example.com"],
  "count": 1
}
```

---

### 7. Send Test Email

**Endpoint**: `POST /api/email/send-test`

**Purpose**: Send a test notification email to verify everything works

**Request**:
```javascript
const sendTestEmail = async (recipient = null) => {
  const body = recipient ? { recipient: recipient } : {};
  const response = await api.post('/email/send-test', body);
  return response.data;
};

// Send to specific address
await sendTestEmail('test@example.com');

// Send to all configured recipients
await sendTestEmail();
```

**Response**:
```json
{
  "success": true,
  "message": "Sent to 2/2 recipients",
  "results": [
    {"email": "admin@example.com", "success": true},
    {"email": "manager@example.com", "success": true}
  ]
}
```

**UI Recommendation**:
- "Send Test Email" button in settings
- Optional field to specify test recipient
- Show delivery status for each recipient

---

### Complete Email Notification Component Example

```typescript
// components/EmailNotificationSettings.tsx
import React, { useState, useEffect } from 'react';
import api from '../lib/api';

export default function EmailNotificationSettings() {
  const [config, setConfig] = useState(null);
  const [recipients, setRecipients] = useState([]);
  const [newRecipient, setNewRecipient] = useState('');
  const [smtpConfig, setSMTPConfig] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_user: '',
    smtp_password: '',
    smtp_use_tls: true,
    smtp_use_ssl: false,
    from_email: '',
    from_name: 'Real Estate Scraper'
  });
  const [testStatus, setTestStatus] = useState(null);

  // Load current configuration
  useEffect(() => {
    loadConfig();
    loadRecipients();
  }, []);

  const loadConfig = async () => {
    const data = await api.get('/email/config').then(res => res.data);
    setConfig(data);
  };

  const loadRecipients = async () => {
    const data = await api.get('/email/recipients').then(res => res.data);
    setRecipients(data.recipients);
  };

  const saveSMTPConfig = async () => {
    try {
      await api.post('/email/configure', smtpConfig);
      alert('SMTP configuration saved!');
      loadConfig();
    } catch (error) {
      alert('Error saving configuration: ' + error.response?.data?.error);
    }
  };

  const testConnection = async () => {
    try {
      const result = await api.post('/email/test-connection').then(res => res.data);
      setTestStatus(result.success ? 'success' : 'error');
      alert(result.message);
    } catch (error) {
      setTestStatus('error');
      alert('Connection failed: ' + error.response?.data?.error);
    }
  };

  const addRecipient = async () => {
    try {
      const data = await api.post('/email/recipients', { email: newRecipient }).then(res => res.data);
      setRecipients(data.recipients);
      setNewRecipient('');
    } catch (error) {
      alert('Error adding recipient: ' + error.response?.data?.error);
    }
  };

  const removeRecipient = async (email) => {
    try {
      const data = await api.delete(`/email/recipients/${encodeURIComponent(email)}`).then(res => res.data);
      setRecipients(data.recipients);
    } catch (error) {
      alert('Error removing recipient: ' + error.response?.data?.error);
    }
  };

  const sendTestEmail = async () => {
    try {
      const result = await api.post('/email/send-test').then(res => res.data);
      alert(result.message);
    } catch (error) {
      alert('Error sending test email: ' + error.response?.data?.error);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <h2 className="text-2xl font-bold">Email Notification Settings</h2>

      {/* SMTP Configuration */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">SMTP Configuration</h3>
        <div className="grid grid-cols-2 gap-4">
          <input
            placeholder="SMTP Host (e.g., smtp.gmail.com)"
            value={smtpConfig.smtp_host}
            onChange={(e) => setSMTPConfig({...smtpConfig, smtp_host: e.target.value})}
            className="border p-2 rounded"
          />
          <input
            type="number"
            placeholder="SMTP Port (587 or 465)"
            value={smtpConfig.smtp_port}
            onChange={(e) => setSMTPConfig({...smtpConfig, smtp_port: parseInt(e.target.value)})}
            className="border p-2 rounded"
          />
          <input
            placeholder="Username / Email"
            value={smtpConfig.smtp_user}
            onChange={(e) => setSMTPConfig({...smtpConfig, smtp_user: e.target.value})}
            className="border p-2 rounded"
          />
          <input
            type="password"
            placeholder="Password / App Password"
            value={smtpConfig.smtp_password}
            onChange={(e) => setSMTPConfig({...smtpConfig, smtp_password: e.target.value})}
            className="border p-2 rounded"
          />
          <input
            placeholder="From Email (optional)"
            value={smtpConfig.from_email}
            onChange={(e) => setSMTPConfig({...smtpConfig, from_email: e.target.value})}
            className="border p-2 rounded"
          />
          <input
            placeholder="From Name (optional)"
            value={smtpConfig.from_name}
            onChange={(e) => setSMTPConfig({...smtpConfig, from_name: e.target.value})}
            className="border p-2 rounded"
          />
        </div>

        <div className="flex gap-2 mt-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={smtpConfig.smtp_use_tls}
              onChange={(e) => setSMTPConfig({...smtpConfig, smtp_use_tls: e.target.checked})}
            />
            Use TLS
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={smtpConfig.smtp_use_ssl}
              onChange={(e) => setSMTPConfig({...smtpConfig, smtp_use_ssl: e.target.checked})}
            />
            Use SSL
          </label>
        </div>

        <div className="flex gap-2 mt-4">
          <button onClick={saveSMTPConfig} className="bg-blue-500 text-white px-4 py-2 rounded">
            Save Configuration
          </button>
          <button onClick={testConnection} className="bg-green-500 text-white px-4 py-2 rounded">
            Test Connection
          </button>
        </div>
      </div>

      {/* Email Recipients */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Email Recipients</h3>
        <div className="flex gap-2 mb-4">
          <input
            type="email"
            placeholder="email@example.com"
            value={newRecipient}
            onChange={(e) => setNewRecipient(e.target.value)}
            className="border p-2 rounded flex-1"
          />
          <button onClick={addRecipient} className="bg-blue-500 text-white px-4 py-2 rounded">
            Add Recipient
          </button>
        </div>

        <div className="space-y-2">
          {recipients.map((email) => (
            <div key={email} className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>{email}</span>
              <button
                onClick={() => removeRecipient(email)}
                className="bg-red-500 text-white px-3 py-1 rounded text-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        <button onClick={sendTestEmail} className="mt-4 bg-purple-500 text-white px-4 py-2 rounded">
          Send Test Email to All Recipients
        </button>
      </div>
    </div>
  );
}
```

**IMPORTANT NOTES**:
- **Gmail Users**: Use App Password instead of regular password (generate at: https://myaccount.google.com/apppasswords)
- **Port 587**: Use with TLS enabled
- **Port 465**: Use with SSL enabled
- **Security**: SMTP password is NOT exposed in GET requests
- **Automatic Emails**: When a scrape session completes in GitHub Actions, emails are sent automatically to all configured recipients

---

## Summary: Implementation Priority

### Phase 1 (Week 1) - Core Features
1. **Start Scraping** - `POST /api/scrape/start`
2. **Check Status** - `GET /api/scrape/status`
3. **Get All Properties** - `GET /api/data/master`
4. **Basic Search** - `POST /api/query`

### Phase 2 (Week 2) - Enhanced Search
5. **Natural Language Search** - `POST /api/search/natural`
6. **Search Suggestions** - `GET /api/search/suggestions`
7. **Site Management** - `GET /api/sites`, `PATCH /api/sites/<key>/toggle`

### Phase 3 (Week 3) - Advanced Features
8. **Price Drops** - `GET /api/price-drops`
9. **Saved Searches** - `POST /api/searches`, `GET /api/searches`
10. **Market Trends** - `GET /api/market-trends`
11. **Email Notifications** - `POST /api/email/configure`, `POST /api/email/recipients`

### Phase 4 (Optional) - Admin Features
12. **Health Monitoring** - `GET /api/health/overall`
13. **Quality Filtering** - `POST /api/quality/score`
14. **Statistics** - `GET /api/stats/overview`
15. **SMTP Management** - Full email notification settings page

---

## Questions?

If you encounter any issues or need clarification on any endpoint, please refer to:
- **IMPLEMENTATION_COMPLETE.md** - Complete feature documentation
- **API_QUICKSTART.md** - Quick start guide
- **API_README.md** - API overview

**Contact**: Backend developer for API support
