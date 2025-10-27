# Frontend Developer Quick Start Guide

**Welcome!** This guide will get you up and running with the Nigerian Real Estate Scraper API in 10 minutes.

---

## 🚀 Quick Start (5 Minutes)

### 1. API Base URL

Your backend is deployed and live on Firebase:

```javascript
const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';
```

### 2. Test the API

Open your browser or use curl:

```bash
# Health check
curl https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/health

# Get all sites
curl https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/sites

# Get properties
curl https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/properties
```

### 3. Basic React/Next.js Integration

```javascript
// lib/api.js
const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';

export async function fetchSites() {
  const response = await fetch(`${API_BASE_URL}/api/sites`);
  if (!response.ok) throw new Error('Failed to fetch sites');
  return response.json();
}

export async function searchProperties(query) {
  const response = await fetch(`${API_BASE_URL}/api/search/natural`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!response.ok) throw new Error('Search failed');
  return response.json();
}

export async function startScrape(sites, maxPages = 10) {
  const response = await fetch(`${API_BASE_URL}/api/scrape/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sites, max_pages: maxPages })
  });
  if (!response.ok) throw new Error('Failed to start scrape');
  return response.json();
}
```

---

## 📋 Essential Endpoints

### Core Endpoints You'll Use Most

#### 1. Get All Sites
```javascript
GET /api/sites
// Returns: { total: 51, enabled: 1, disabled: 50, sites: [...] }
```

#### 2. Search Properties (Natural Language)
```javascript
POST /api/search/natural
Body: { "query": "3 bedroom flat in Lekki under 30 million" }
// Returns: { results: [...], count: 25, query: "..." }
```

#### 3. Get All Properties
```javascript
GET /api/properties?limit=50&offset=0
// Returns: { properties: [...], total: 1500, page: 1, per_page: 50 }
```

#### 4. Start Scraping
```javascript
POST /api/scrape/start
Body: { "sites": ["npc", "propertypro"], "max_pages": 10 }
// Returns: { status: "started", sites: [...], estimated_time: "5 minutes" }
```

#### 5. Check Scrape Status
```javascript
GET /api/scrape/status
// Returns: { running: true, progress: 50, current_site: "npc", ... }
```

---

## 🎨 Complete React Example

### Custom Hook for API

```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';

const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';

export function useSites() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/sites`)
      .then(res => res.json())
      .then(data => {
        setSites(data.sites);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { sites, loading, error };
}

export function useProperties(limit = 50, offset = 0) {
  const [properties, setProperties] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/properties?limit=${limit}&offset=${offset}`)
      .then(res => res.json())
      .then(data => {
        setProperties(data.properties);
        setTotal(data.total);
        setLoading(false);
      });
  }, [limit, offset]);

  return { properties, total, loading };
}
```

### Example Component

```javascript
// components/PropertySearch.jsx
import { useState } from 'react';

const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';

export function PropertySearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/search/natural`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="property-search">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., 3 bedroom flat in Lekki under 30M"
          className="search-input"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div className="results">
        {results.map((property, index) => (
          <div key={index} className="property-card">
            <h3>{property.title}</h3>
            <p className="price">{property.price}</p>
            <p className="location">{property.location}</p>
            <a href={property.listing_url} target="_blank" rel="noopener noreferrer">
              View Details
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔥 Next.js App Router Example

```javascript
// app/properties/page.jsx
import { PropertyList } from '@/components/PropertyList';

async function getProperties() {
  const res = await fetch(
    'https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/properties?limit=50',
    { cache: 'no-store' } // Always fetch fresh data
  );

  if (!res.ok) throw new Error('Failed to fetch properties');
  return res.json();
}

export default async function PropertiesPage() {
  const data = await getProperties();

  return (
    <div>
      <h1>Properties ({data.total})</h1>
      <PropertyList properties={data.properties} />
    </div>
  );
}
```

---

## 📦 Environment Variables

Create `.env.local` in your Next.js project:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://us-central1-realtor-s-practice.cloudfunctions.net/api

# Optional: If authentication is enabled later
# NEXT_PUBLIC_API_KEY=your-api-key-here
```

Then use it:

```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

fetch(`${API_URL}/api/sites`)...
```

---

## 🎯 Common Use Cases

### 1. Display All Sites

```javascript
function SitesList() {
  const { sites, loading } = useSites();

  if (loading) return <div>Loading sites...</div>;

  return (
    <div>
      {sites.map(site => (
        <div key={site.site_key}>
          <h3>{site.name}</h3>
          <p>Status: {site.enabled ? 'Enabled' : 'Disabled'}</p>
          <a href={site.url}>{site.url}</a>
        </div>
      ))}
    </div>
  );
}
```

### 2. Start Scraping from UI

```javascript
async function startScraping(selectedSites) {
  const response = await fetch(
    'https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/scrape/start',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sites: selectedSites, // ["npc", "propertypro"]
        max_pages: 20
      })
    }
  );

  const result = await response.json();
  console.log('Scraping started:', result);
}
```

### 3. Real-time Status Updates

```javascript
function ScrapeStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch(
        'https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/scrape/status'
      );
      const data = await res.json();
      setStatus(data);
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (!status?.running) return <div>No scraping in progress</div>;

  return (
    <div>
      <h3>Scraping: {status.current_site}</h3>
      <progress value={status.progress} max="100">{status.progress}%</progress>
      <p>{status.items_scraped} items scraped</p>
    </div>
  );
}
```

---

## 🎨 TypeScript Support

```typescript
// types/api.ts
export interface Site {
  site_key: string;
  name: string;
  url: string;
  enabled: boolean;
  parser: string;
}

export interface Property {
  title: string;
  price: string;
  location: string;
  property_type: string;
  bedrooms?: number;
  bathrooms?: number;
  listing_url: string;
  images: string[];
  source: string;
  scrape_timestamp: string;
}

export interface SearchResponse {
  results: Property[];
  count: number;
  query: string;
}

// api.ts
const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';

export async function fetchSites(): Promise<{ sites: Site[], total: number }> {
  const response = await fetch(`${API_BASE_URL}/api/sites`);
  if (!response.ok) throw new Error('Failed to fetch sites');
  return response.json();
}

export async function searchProperties(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search/natural`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!response.ok) throw new Error('Search failed');
  return response.json();
}
```

---

## 📚 Full API Documentation

For complete API documentation with all 68 endpoints, see:
- **[FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md)** - Complete API reference
- **[POSTMAN_GUIDE.md](./POSTMAN_GUIDE.md)** - Postman collection for testing
- **[Nigerian_Real_Estate_API.postman_collection.json](./Nigerian_Real_Estate_API.postman_collection.json)** - Import into Postman

---

## 🔧 Testing Your Integration

### 1. Test in Browser Console

Open browser console and paste:

```javascript
fetch('https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/health')
  .then(res => res.json())
  .then(data => console.log('API Health:', data));
```

### 2. Test with Postman

1. Import the Postman collection from `docs/Nigerian_Real_Estate_API.postman_collection.json`
2. Set base URL to: `https://us-central1-realtor-s-practice.cloudfunctions.net/api`
3. Test all endpoints

### 3. Test with curl

```bash
# Health check
curl https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/health

# Get sites
curl https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/sites

# Search
curl -X POST https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/search/natural \
  -H "Content-Type: application/json" \
  -d '{"query": "3 bedroom flat in Lekki"}'
```

---

## ⚡ Performance Tips

1. **Use SWR or React Query** for caching:
```bash
npm install swr
```

```javascript
import useSWR from 'swr';

const fetcher = url => fetch(url).then(res => res.json());

function Properties() {
  const { data, error } = useSWR(
    'https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/properties',
    fetcher
  );

  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;

  return <PropertyList properties={data.properties} />;
}
```

2. **Implement pagination** to avoid large payloads
3. **Use debouncing** for search inputs
4. **Cache API responses** appropriately

---

## 🐛 Troubleshooting

### CORS Issues
The API has CORS enabled. If you still face issues:
- Check if you're using the correct URL
- Ensure you're not blocking requests in browser extensions

### API Not Responding
- Check Firebase Console: https://console.firebase.google.com/project/realtor-s-practice/functions
- View logs for errors

### Authentication (When Enabled)
When authentication is enabled, include API key:

```javascript
fetch(`${API_URL}/api/sites`, {
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
```

---

## 🆘 Need Help?

1. **Full API Documentation**: `docs/FRONTEND_INTEGRATION_GUIDE.md`
2. **Authentication Guide**: `docs/FRONTEND_AUTH_GUIDE.md`
3. **Postman Collection**: `docs/Nigerian_Real_Estate_API.postman_collection.json`
4. **Firebase Deployment Info**: `FIREBASE_DEPLOYMENT_SUCCESS.md`

---

## 🎉 You're Ready!

You now have everything you need to integrate the Nigerian Real Estate Scraper API into your frontend application.

**Your API Base URL**:
```
https://us-central1-realtor-s-practice.cloudfunctions.net/api
```

Start building! 🚀
