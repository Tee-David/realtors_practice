# Complete Frontend Integration Guide

**For Frontend Developers**: Everything you need to integrate the Real Estate Scraper API

---

## Quick Start (5 Minutes)

### 1. API Server is Ready
The API server runs on: `http://localhost:5000`

**Start the server** (Backend will do this):
```bash
python api_server.py
```

### 2. Test API Health
```bash
curl http://localhost:5000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T01:30:00.000Z",
  "version": "3.1.0"
}
```

---

## How to Trigger a Scrape

### Option 1: Via REST API (Recommended)

**Endpoint**: `POST /api/scrape/start`

**Example** (JavaScript/React):
```javascript
const triggerScrape = async () => {
  const response = await fetch('http://localhost:5000/api/scrape/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sites: ['npc', 'jiji', 'propertypro'],  // Optional: specific sites
      max_pages: 20,                           // Optional: pages per site
      geocode: true,                           // Optional: enable geocoding
      headless: true                           // Optional: headless browser
    })
  });

  const data = await response.json();
  console.log(data);
  // { "status": "started", "scrape_id": "scrape_123", "sites": 3 }
};
```

**Full cURL Example**:
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{
    "sites": ["npc", "jiji", "propertypro"],
    "max_pages": 20,
    "geocode": true
  }'
```

### Option 2: Trigger All Sites

**Scrape all 51 sites**:
```javascript
const triggerFullScrape = async () => {
  const response = await fetch('http://localhost:5000/api/scrape/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      max_pages: 20,
      geocode: true
    })
  });

  return await response.json();
};
```

### Option 3: Via GitHub Actions (Production)

**Trigger via API** (requires GitHub token):
```javascript
const triggerGitHubScrape = async () => {
  const response = await fetch('http://localhost:5000/api/github/trigger-scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_GITHUB_TOKEN'  // Backend sets this
    },
    body: JSON.stringify({
      max_pages: 20,
      geocode: true
    })
  });

  return await response.json();
};
```

---

## Monitor Scrape Progress

### Check Scrape Status

**Endpoint**: `GET /api/scrape/status`

```javascript
const checkStatus = async () => {
  const response = await fetch('http://localhost:5000/api/scrape/status');
  const data = await response.json();

  console.log(data);
  // {
  //   "status": "running",
  //   "sites_completed": 10,
  //   "sites_total": 51,
  //   "properties_scraped": 234,
  //   "elapsed_time": "1h 23m"
  // }
};
```

### Poll for Updates

```javascript
const monitorScrape = () => {
  const interval = setInterval(async () => {
    const status = await checkStatus();

    if (status.status === 'completed') {
      clearInterval(interval);
      console.log('Scrape complete!');
    }

    // Update UI with progress
    updateProgressBar(status.sites_completed, status.sites_total);
  }, 5000); // Check every 5 seconds
};
```

---

## Get Scraped Data

### Get All Properties from Firestore

**Endpoint**: `GET /api/firestore/properties`

```javascript
const getProperties = async (limit = 20, offset = 0) => {
  const response = await fetch(
    `http://localhost:5000/api/firestore/properties?limit=${limit}&offset=${offset}`
  );

  const data = await response.json();
  return data.properties;
};
```

**Response**:
```json
{
  "properties": [
    {
      "basic_info": {
        "title": "4 Bedroom Duplex in Lekki",
        "source": "Nigeria Property Centre",
        "listing_url": "https://...",
        "status": "available"
      },
      "property_details": {
        "property_type": "Duplex",
        "bedrooms": 4,
        "bathrooms": 3,
        "furnishing": "furnished"
      },
      "financial": {
        "price": 85000000,
        "price_currency": "NGN",
        "price_per_bedroom": 21250000
      },
      "location": {
        "area": "Lekki",
        "lga": "Eti-Osa",
        "state": "Lagos",
        "coordinates": { "lat": 6.4474, "lng": 3.4705 }
      },
      "amenities": {
        "features": ["Swimming pool", "24hr power", "Security"]
      },
      "media": {
        "images": [
          { "url": "https://...", "order": 0 }
        ]
      },
      "tags": {
        "premium": true,
        "hot_deal": false
      },
      "uploaded_at": "2025-11-17T01:30:00.000Z"
    }
  ],
  "total": 1234,
  "limit": 20,
  "offset": 0
}
```

### Search Properties

**Endpoint**: `POST /api/firestore/search`

```javascript
const searchProperties = async (filters) => {
  const response = await fetch('http://localhost:5000/api/firestore/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filters: {
        min_price: 50000000,
        max_price: 100000000,
        bedrooms: 4,
        area: "Lekki",
        property_type: "Duplex"
      },
      limit: 20
    })
  });

  return await response.json();
};
```

### Get Premium Properties

**Endpoint**: `GET /api/firestore/premium`

```javascript
const getPremiumProperties = async () => {
  const response = await fetch('http://localhost:5000/api/firestore/premium?limit=10');
  return await response.json();
};
```

### Get Properties by Location

**Endpoint**: `GET /api/firestore/properties/by-area/:area`

```javascript
const getPropertiesByArea = async (area) => {
  const response = await fetch(
    `http://localhost:5000/api/firestore/properties/by-area/${area}?limit=20`
  );
  return await response.json();
};

// Example
const lekki = await getPropertiesByArea('Lekki');
```

---

## React Hooks (Ready to Use)

### useScraper Hook

```typescript
import { useState, useCallback } from 'react';

interface ScrapeOptions {
  sites?: string[];
  max_pages?: number;
  geocode?: boolean;
}

export const useScraper = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startScrape = useCallback(async (options: ScrapeOptions = {}) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/scrape/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });

      if (!response.ok) throw new Error('Failed to start scrape');

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getStatus = useCallback(async () => {
    const response = await fetch('http://localhost:5000/api/scrape/status');
    return await response.json();
  }, []);

  return { startScrape, getStatus, isLoading, error };
};
```

**Usage**:
```typescript
function ScrapeButton() {
  const { startScrape, isLoading } = useScraper();

  const handleClick = async () => {
    await startScrape({ max_pages: 20, geocode: true });
    alert('Scrape started!');
  };

  return (
    <button onClick={handleClick} disabled={isLoading}>
      {isLoading ? 'Starting...' : 'Start Scrape'}
    </button>
  );
}
```

### useProperties Hook

```typescript
import { useState, useEffect } from 'react';

export const useProperties = (limit = 20, offset = 0) => {
  const [properties, setProperties] = useState([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProperties = async () => {
      setIsLoading(true);
      const response = await fetch(
        `http://localhost:5000/api/firestore/properties?limit=${limit}&offset=${offset}`
      );
      const data = await response.json();
      setProperties(data.properties);
      setTotal(data.total);
      setIsLoading(false);
    };

    fetchProperties();
  }, [limit, offset]);

  return { properties, total, isLoading };
};
```

**Usage**:
```typescript
function PropertyList() {
  const { properties, total, isLoading } = useProperties(20, 0);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Properties ({total})</h2>
      {properties.map(prop => (
        <PropertyCard key={prop.metadata.hash} property={prop} />
      ))}
    </div>
  );
}
```

---

## TypeScript Types

```typescript
// Property Schema
export interface Property {
  basic_info: {
    title: string;
    source: string;
    listing_url: string;
    status: 'available' | 'sold' | 'rented';
    listing_type: 'sale' | 'rent' | 'lease' | 'shortlet';
  };
  property_details: {
    property_type: string;
    bedrooms: number;
    bathrooms: number;
    toilets?: number;
    bq?: number;
    land_size?: string;
    furnishing?: 'furnished' | 'semi-furnished' | 'unfurnished';
    condition?: 'new' | 'renovated' | 'old';
  };
  financial: {
    price: number;
    price_currency: string;
    price_per_sqm?: number;
    price_per_bedroom?: number;
    initial_deposit?: number;
    payment_plan?: string;
  };
  location: {
    full_address: string;
    area: string;
    lga: string;
    state: string;
    coordinates?: {
      lat: number;
      lng: number;
    };
    landmarks: string[];
  };
  amenities: {
    features: string[];
    security: string[];
    utilities: string[];
  };
  media: {
    images: Array<{
      url: string;
      caption?: string;
      order: number;
    }>;
    videos: string[];
    virtual_tour_url?: string;
  };
  agent_info: {
    agent_name?: string;
    contact_info?: string;
    agent_verified: boolean;
  };
  metadata: {
    hash: string;
    quality_score: number;
    scrape_timestamp: string;
    view_count: number;
    inquiry_count: number;
    days_on_market: number;
  };
  tags: {
    premium: boolean;
    hot_deal: boolean;
    featured: boolean;
    promo_tags: string[];
  };
  uploaded_at: string;
  updated_at: string;
}

// API Response Types
export interface PropertiesResponse {
  properties: Property[];
  total: number;
  limit: number;
  offset: number;
}

export interface ScrapeStatusResponse {
  status: 'idle' | 'running' | 'completed' | 'failed';
  sites_completed: number;
  sites_total: number;
  properties_scraped: number;
  elapsed_time: string;
}
```

---

## Complete API Endpoints Reference

### Scraping Control
- `POST /api/scrape/start` - Start scraping
- `GET /api/scrape/status` - Check scrape status
- `POST /api/scrape/stop` - Stop current scrape
- `GET /api/scrape/history` - Get scrape history

### Firestore Data Access
- `GET /api/firestore/properties` - Get all properties (paginated)
- `GET /api/firestore/dashboard` - Dashboard statistics
- `GET /api/firestore/newest` - Newest listings
- `GET /api/firestore/premium` - Premium properties
- `GET /api/firestore/hot-deals` - Hot deal properties
- `POST /api/firestore/search` - Advanced search
- `GET /api/firestore/properties/by-area/:area` - Properties by area
- `GET /api/firestore/properties/by-lga/:lga` - Properties by LGA
- `GET /api/firestore/property/:hash` - Single property details

### Site Configuration
- `GET /api/sites` - List all sites
- `GET /api/sites/enabled` - List enabled sites only
- `POST /api/sites/:site_key/enable` - Enable a site
- `POST /api/sites/:site_key/disable` - Disable a site

### Statistics
- `GET /api/stats/overview` - Overall statistics
- `GET /api/stats/sites` - Per-site statistics
- `GET /api/stats/trends` - Trend analysis

---

## Environment Setup (Backend Handles This)

The backend will set these environment variables:

```bash
FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
FIRESTORE_ENABLED=1
RP_GEOCODE=1
RP_PAGE_CAP=20
RP_HEADLESS=1
```

**Frontend doesn't need to worry about this!**

---

## Error Handling

```typescript
const handleScrape = async () => {
  try {
    const result = await fetch('http://localhost:5000/api/scrape/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ max_pages: 20 })
    });

    if (!result.ok) {
      const error = await result.json();
      throw new Error(error.message || 'Failed to start scrape');
    }

    const data = await result.json();
    console.log('Scrape started:', data);
  } catch (error) {
    console.error('Error:', error.message);
    alert(`Failed: ${error.message}`);
  }
};
```

---

## Production Deployment (GitHub Actions)

### Option 1: Trigger via Backend API

```javascript
// Backend handles GitHub token
const triggerProductionScrape = async () => {
  const response = await fetch('http://localhost:5000/api/github/trigger-scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      max_pages: 20,
      geocode: true
    })
  });

  return await response.json();
};
```

### Option 2: Direct GitHub API (Not Recommended)

If you want to call GitHub directly (backend provides token):

```javascript
const triggerGitHub = async (githubToken) => {
  const response = await fetch(
    'https://api.github.com/repos/Tee-David/realtors_practice/actions/workflows/scrape-production.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${githubToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: {
          max_pages: '20',
          geocode: '1'
        }
      })
    }
  );

  return response.status === 204; // 204 = success
};
```

---

## Testing Checklist

### 1. Test API Health
```bash
curl http://localhost:5000/api/health
```
✅ Should return `{"status": "healthy"}`

### 2. Test Scrape Trigger
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 1}'
```
✅ Should start scraping

### 3. Test Status Check
```bash
curl http://localhost:5000/api/scrape/status
```
✅ Should show progress

### 4. Test Firestore Data
```bash
curl http://localhost:5000/api/firestore/properties?limit=5
```
✅ Should return properties

---

## Common Integration Patterns

### Pattern 1: Button to Start Scrape

```typescript
function ScrapeButton() {
  const [isLoading, setIsLoading] = useState(false);

  const handleScrape = async () => {
    setIsLoading(true);

    try {
      await fetch('http://localhost:5000/api/scrape/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_pages: 20 })
      });

      alert('Scrape started successfully!');
    } catch (error) {
      alert('Failed to start scrape');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button onClick={handleScrape} disabled={isLoading}>
      {isLoading ? 'Starting...' : 'Start Full Scrape'}
    </button>
  );
}
```

### Pattern 2: Progress Bar

```typescript
function ScrapeProgress() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch('http://localhost:5000/api/scrape/status');
      const data = await res.json();
      setStatus(data);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  if (!status) return null;

  const progress = (status.sites_completed / status.sites_total) * 100;

  return (
    <div>
      <div className="progress-bar" style={{ width: `${progress}%` }} />
      <p>{status.sites_completed} / {status.sites_total} sites</p>
      <p>{status.properties_scraped} properties scraped</p>
    </div>
  );
}
```

### Pattern 3: Property List with Pagination

```typescript
function PropertyList() {
  const [page, setPage] = useState(0);
  const { properties, total } = useProperties(20, page * 20);

  return (
    <div>
      {properties.map(property => (
        <PropertyCard key={property.metadata.hash} property={property} />
      ))}

      <button onClick={() => setPage(p => p - 1)} disabled={page === 0}>
        Previous
      </button>
      <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * 20 >= total}>
        Next
      </button>
    </div>
  );
}
```

---

## Summary for Frontend Developer

### What You Need to Know

1. **API runs on**: `http://localhost:5000`
2. **Start scrape**: `POST /api/scrape/start`
3. **Get data**: `GET /api/firestore/properties`
4. **All data is in Firestore** with enterprise schema (9 categories)
5. **No authentication needed** (for local development)

### What You Don't Need to Worry About

1. ❌ Environment variables (backend handles)
2. ❌ Firebase credentials (backend handles)
3. ❌ Scraping logic (backend handles)
4. ❌ Data transformation (backend handles)

### Quick Integration (Copy-Paste Ready)

```javascript
// 1. Start scrape
const startScrape = () => fetch('http://localhost:5000/api/scrape/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ max_pages: 20 })
});

// 2. Get properties
const getProperties = () => fetch('http://localhost:5000/api/firestore/properties?limit=20')
  .then(res => res.json());

// 3. Search properties
const searchProperties = (filters) => fetch('http://localhost:5000/api/firestore/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ filters })
}).then(res => res.json());
```

**That's it!** Three functions cover 90% of use cases.

---

## Need Help?

- **API Documentation**: See `docs/FRONTEND_INTEGRATION_GUIDE.md` (1,100+ lines)
- **Postman Collection**: Import `docs/Nigerian_Real_Estate_API.postman_collection.json`
- **Quick Reference**: See `docs/API_QUICKSTART.md`

---

**Last Updated**: 2025-11-17
**API Version**: 3.1.0
**Status**: ✅ Production Ready
