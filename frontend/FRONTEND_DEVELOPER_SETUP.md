# Frontend Developer Setup Guide
## Nigerian Real Estate API Integration

**Last Updated:** 2025-10-30
**Status:** ✅ TESTED & VERIFIED

---

## Overview

This guide will help you integrate the Nigerian Real Estate API into your Next.js/React frontend. **Everything has been tested and verified to work** - just follow these steps exactly.

---

## Quick Start (3 Steps)

###  Step 1: Get the Latest Code

```bash
# Clone or pull the latest code
git clone https://github.com/Tee-David/realtors_practice.git
cd realtors_practice

# OR if you already have it:
git pull origin main
```

### Step 2: Start the API Server

```bash
# Install Python dependencies (if not done already)
pip install -r requirements.txt

# Start the API server
python api_server.py
```

You should see:
```
INFO - Starting API server on port 5000
Running on http://127.0.0.1:5000
```

### Step 3: Test the API

Open a new terminal and run:

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status":"healthy","timestamp":"2025-10-30T...", "version":"1.0.0"}
```

**If you see this response, you're ready to go!**

---

## Frontend Integration

### Option 1: Using the Provided TypeScript Files (RECOMMENDED)

We've created everything you need in the `frontend/` folder:

1. **`types.ts`** - All TypeScript types for the API
2. **`api-client.ts`** - Complete typed API client for all 67 endpoints
3. **`hooks.tsx`** - Ready-to-use React hooks with SWR

#### Installation

```bash
# In your Next.js project
cd your-nextjs-project

# Install required dependencies
npm install swr

# Copy the frontend files
cp ../realtors_practice/frontend/* ./lib/api/
```

#### Basic Usage

```typescript
// In your Next.js component
import { useProperties, useScrapeStatus } from '@/lib/api/hooks';

export default function Dashboard() {
  // Get properties from all sites
  const { properties, total, isLoading, error } = useProperties();

  // Get scraping status
  const { status, isRunning, progress, startScrape, stopScrape } = useScrapeStatus();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Properties: {total}</h1>

      {/* Scraping Control */}
      {isRunning ? (
        <div>
          <p>Scraping in progress: {progress}%</p>
          <button onClick={stopScrape}>Stop</button>
        </div>
      ) : (
        <button onClick={() => startScrape()}>Start Scraping</button>
      )}

      {/* Properties List */}
      {properties.map((property) => (
        <div key={property.hash}>
          <h3>{property.title}</h3>
          <p>{property.price_formatted}</p>
          <p>{property.location}</p>
        </div>
      ))}
    </div>
  );
}
```

### Option 2: Direct API Calls (Without TypeScript)

If you prefer to use plain fetch:

```javascript
// Fetch properties
const response = await fetch('http://localhost:5000/api/data/sites?limit=50');
const data = await response.json();
console.log(data.properties);

// Start scraping
const scrapeResponse = await fetch('http://localhost:5000/api/scrape/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sites: ['npc', 'propertypro'] })
});
const result = await scrapeResponse.json();
```

---

## Common Use Cases

### 1. Display Properties from All Sites

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function PropertyList() {
  const { properties, total, hasMore, isLoading } = useProperties(undefined, { limit: 20 });

  return (
    <div>
      <h2>All Properties ({total})</h2>
      {properties.map(p => (
        <PropertyCard key={p.hash} property={p} />
      ))}
      {hasMore && <button>Load More</button>}
    </div>
  );
}
```

### 2. Display Properties from Specific Site

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function SiteProperties() {
  const { properties, total } = useProperties('cwlagos'); // CW Real Estate

  return (
    <div>
      <h2>CW Real Estate ({total} listings)</h2>
      {properties.map(p => <PropertyCard key={p.hash} property={p} />)}
    </div>
  );
}
```

### 3. Search Properties

```typescript
import { useState } from 'react';
import { useSearch } from '@/lib/api/hooks';

export default function SearchProperties() {
  const [query, setQuery] = useState('');
  const { results, total, isLoading } = useSearch(query, query.length > 2);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search properties..."
      />
      {isLoading && <p>Searching...</p>}
      <p>{total} results</p>
      {results.map(p => <PropertyCard key={p.hash} property={p} />)}
    </div>
  );
}
```

### 4. Manage Sites

```typescript
import { useSites } from '@/lib/api/hooks';

export default function SitesManager() {
  const { sites, enabled, disabled, toggleSite, isLoading } = useSites();

  return (
    <div>
      <h2>Sites ({enabled} enabled, {disabled} disabled)</h2>
      {sites.map(site => (
        <div key={site.site_key}>
          <span>{site.name}</span>
          <button onClick={() => toggleSite(site.site_key, !site.enabled)}>
            {site.enabled ? 'Disable' : 'Enable'}
          </button>
        </div>
      ))}
    </div>
  );
}
```

### 5. Monitor Scraping

```typescript
import { useScrapeStatus, useScrapeHistory } from '@/lib/api/hooks';

export default function ScrapingMonitor() {
  const { status, isRunning, progress, startScrape, stopScrape } = useScrapeStatus();
  const { scrapes } = useScrapeHistory(5);

  return (
    <div>
      {/* Current Status */}
      <div>
        <h3>Status: {status?.status}</h3>
        {isRunning && (
          <>
            <progress value={progress} max={100} />
            <p>{progress}% complete</p>
            <p>Current site: {status?.current_site}</p>
            <button onClick={stopScrape}>Stop</button>
          </>
        )}
        {!isRunning && (
          <button onClick={() => startScrape()}>Start Scraping</button>
        )}
      </div>

      {/* History */}
      <div>
        <h3>Recent Scrapes</h3>
        {scrapes.map(scrape => (
          <div key={scrape.id}>
            <p>{scrape.start_time}: {scrape.total_listings} listings</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 6. View Statistics

```typescript
import { useOverviewStats, useSiteStats, useMarketTrends } from '@/lib/api/hooks';

export default function StatsCard() {
  const { stats } = useOverviewStats();
  const { stats: siteStats } = useSiteStats();
  const { trends } = useMarketTrends();

  return (
    <div>
      <h2>Overview</h2>
      <p>Total Sites: {stats?.overview.total_sites}</p>
      <p>Total Listings: {stats?.overview.total_listings}</p>

      <h3>Top Sites</h3>
      {siteStats.slice(0, 5).map(site => (
        <div key={site.site_key}>
          <p>{site.name}: {site.total_listings} listings</p>
        </div>
      ))}

      <h3>Market Trends</h3>
      <p>Average Price: ₦{trends?.overall.avg_price?.toLocaleString()}</p>
      <p>Trend: {trends?.overall.price_trend}</p>
    </div>
  );
}
```

---

## All Available Hooks

### Data Fetching
- `useProperties(siteKey?, params?)` - Get properties
- `useSearch(query, enabled?)` - Search properties
- `useNaturalLanguageSearch(query, enabled?)` - Natural language search

### Scraping
- `useScrapeStatus()` - Get scraping status & controls
- `useScrapeHistory(limit?)` - Get scraping history

### Sites
- `useSites()` - List all sites + management functions
- `useSite(siteKey)` - Get specific site
- `useSiteStats()` - Get per-site statistics

### Statistics
- `useOverviewStats()` - Get overview stats
- `useTrendStats(days?)` - Get trend statistics

### Price Intelligence
- `useMarketTrends()` - Get market trends
- `usePriceDrops(minDropPercentage?, days?)` - Get price drops
- `usePriceHistory(propertyId)` - Get price history

### Saved Searches
- `useSavedSearches()` - List saved searches + CRUD
- `useSavedSearch(searchId)` - Get specific saved search

### Monitoring
- `useHealth()` - API health check
- `useLogs(params?)` - Get logs
- `useErrorLogs(limit?)` - Get error logs

### Email & Notifications
- `useEmailRecipients()` - Manage email recipients

### GitHub Actions
- `useWorkflowRuns(limit?)` - GitHub Actions workflow runs

### Scheduling
- `useScheduledJobs()` - Scheduled scraping jobs

### Export
- `useExportFormats()` - Export formats & generation

---

## API Endpoints Reference

See `API_ENDPOINTS_ACTUAL.md` for the complete list of all 67 endpoints.

Quick reference:

| Category | Endpoints | Documentation |
|----------|-----------|---------------|
| Health & Monitoring | 5 | `/api/health`, `/api/health/overall`, etc. |
| Scraping | 4 | `/api/scrape/start`, `/api/scrape/status`, etc. |
| Sites Management | 6 | `/api/sites`, `/api/sites/<key>`, etc. |
| Data Access | 4 | `/api/data/sites`, `/api/data/search`, etc. |
| Statistics | 3 | `/api/stats/overview`, `/api/stats/sites`, etc. |
| And 15 more... | 45 | See full documentation |

---

## Troubleshooting

### Problem: "Cannot import name 'URLValidator'"

**Solution:** Pull the latest code from GitHub:
```bash
git pull origin main
```

### Problem: "Connection refused" or "Failed to fetch"

**Solution:** Make sure the API server is running:
```bash
python api_server.py
```

### Problem: "CORS error"

**Solution:** The API server has CORS enabled by default. Make sure you're running it on `localhost:5000` and your frontend is accessing it correctly.

###  Problem: "Module not found: 'swr'"

**Solution:** Install SWR:
```bash
npm install swr
```

### Problem: Empty data or no properties

**Solution:** Run a scrape first:
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites":["cwlagos"]}'
```

---

## Working with Your Own Branch

To avoid committing directly to main:

```bash
# Create your frontend branch
git checkout -b frontend-integration

# Make your changes
# ... do your work ...

# Commit your changes
git add .
git commit -m "feat: Add frontend integration for properties page"

# Push your branch
git push origin frontend-integration

# Create a pull request on GitHub
```

---

## Testing Checklist

Before you start building, test these endpoints:

- [ ] Health check: `GET /api/health`
- [ ] List sites: `GET /api/sites`
- [ ] Get properties: `GET /api/data/sites?limit=10`
- [ ] Search: `GET /api/data/search?query=Lagos`
- [ ] Stats: `GET /api/stats/overview`
- [ ] Start scrape: `POST /api/scrape/start` (with body `{"sites":["cwlagos"]}`)
- [ ] Scrape status: `GET /api/scrape/status`

Use the provided `test_api_startup.py` script to verify:

```bash
python test_api_startup.py
```

---

## Example Next.js Project Structure

```
your-nextjs-project/
├── app/
│   ├── properties/
│   │   └── page.tsx          # Property listing page
│   ├── scraper/
│   │   └── page.tsx          # Scraper control panel
│   ├── sites/
│   │   └── page.tsx          # Sites management
│   └── dashboard/
│       └── page.tsx          # Overview dashboard
├── components/
│   ├── PropertyCard.tsx
│   ├── ScrapeControl.tsx
│   └── StatsCard.tsx
├── lib/
│   └── api/
│       ├── types.ts          # Copy from frontend/types.ts
│       ├── api-client.ts     # Copy from frontend/api-client.ts
│       └── hooks.tsx         # Copy from frontend/hooks.tsx
└── package.json
```

---

## Need Help?

If you encounter any issues:

1. **Check the API is running:** Visit `http://localhost:5000/api/health`
2. **Check the logs:** Look at `logs/scraper.log` in the backend folder
3. **Run the test script:** `python test_api_startup.py`
4. **Check your branch:** Make sure you pulled the latest code

---

## Quick Reference: Most Common Tasks

### Get all properties with pagination

```typescript
const { properties, total, hasMore } = useProperties(undefined, { limit: 20, offset: 0 });
```

### Start scraping specific sites

```typescript
const { startScrape } = useScrapeStatus();
await startScrape({ sites: ['npc', 'propertypro'], max_pages: 10 });
```

### Search with filters

```typescript
import { apiClient } from '@/lib/api/api-client';

const results = await apiClient.queryProperties({
  filters: {
    property_type: 'apartment',
    bedrooms: { min: 2, max: 4 },
    price: { max: 50000000 }
  },
  pagination: { limit: 20 }
});
```

### Enable/disable a site

```typescript
const { toggleSite } = useSites();
await toggleSite('npc', true);  // Enable
await toggleSite('propertypro', false);  // Disable
```

---

## Summary

You now have:

✅ Complete TypeScript types for all API responses
✅ Fully typed API client with all 67 endpoints
✅ Ready-to-use React hooks with SWR
✅ Example code for common use cases
✅ Troubleshooting guide

**The API is tested and working. Just copy the files, install SWR, and start building!**

---

**Questions?** Refer to:
- `API_ENDPOINTS_ACTUAL.md` - Complete endpoint documentation
- `frontend/types.ts` - All TypeScript types
- `frontend/api-client.ts` - API client source code
- `frontend/hooks.tsx` - React hooks source code
