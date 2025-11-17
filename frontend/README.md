# Frontend Developer Guide

Complete guide for integrating the Nigerian Real Estate API into your frontend application. All 90 endpoints are production-ready with full TypeScript support.

## 🎯 Quick Start

**3 Steps to Integration**:

### 1. Copy Integration Files

Copy these files to your project:
```
frontend/
├── types.ts        → lib/api/types.ts
├── api-client.ts   → lib/api/client.ts
└── hooks.tsx       → lib/api/hooks.tsx
```

### 2. Install Dependencies

```bash
npm install swr axios
# or
yarn add swr axios
```

### 3. Start Using

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading } = useProperties();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{total} Properties Available</h1>
      {properties.map(property => (
        <PropertyCard key={property.hash} property={property} />
      ))}
    </div>
  );
}
```

That's it! You're ready to build.

---

## 📚 What's Included

### TypeScript Types ([types.ts](types.ts))

Complete type definitions for all 90 endpoints with enterprise schema (9 categories, 85+ fields).

### API Client ([api-client.ts](api-client.ts))

HTTP client with error handling for all 90 endpoints organized by category.

### React Hooks ([hooks.tsx](hooks.tsx))

SWR-powered hooks for automatic data fetching with real-time updates.

---

## 🔌 API Endpoints

**Base URL**: `https://realtors-practice-api.onrender.com/api` (Production)

**Total**: 90 endpoints across 17 categories

**Full Reference**: [API_ENDPOINTS_ACTUAL.md](API_ENDPOINTS_ACTUAL.md)

---

## 💡 Common Use Cases

### Display All Properties

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading } = useProperties();

  if (isLoading) return <Skeleton />;

  return (
    <div>
      <h1>{total} Properties</h1>
      <PropertyGrid properties={properties} />
    </div>
  );
}
```

### Search Properties

```typescript
import { usePropertySearch } from '@/lib/api/hooks';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const { properties, isLoading } = usePropertySearch(query);

  return (
    <div>
      <SearchInput value={query} onChange={setQuery} />
      {isLoading ? <Skeleton /> : <PropertyResults properties={properties} />}
    </div>
  );
}
```

### Monitor Scraping Progress

```typescript
import { useScraperStatus } from '@/lib/api/hooks';

export default function ScraperMonitor() {
  const { status, isRunning, progress } = useScraperStatus();

  if (!isRunning) return <div>No scraping in progress</div>;

  return (
    <div>
      <ProgressBar
        current={progress.completed_sites}
        total={progress.total_sites}
      />
      <p>Completed: {progress.completed_sites}/{progress.total_sites}</p>
    </div>
  );
}
```

---

## 🏗️ Component Examples

### Property Card

```typescript
import { Property } from '@/lib/api/types';

export function PropertyCard({ property }: { property: Property }) {
  const { basic_info, property_details, financial, location } = property;

  return (
    <div className="property-card">
      <img src={property.media.images?.[0]?.url} alt={basic_info.title} />
      <h3>{basic_info.title}</h3>
      <p className="price">
        {financial.currency} {financial.price.toLocaleString()}
      </p>
      <p className="location">{location.area}, {location.lga}</p>
      <div className="details">
        <span>{property_details.bedrooms} beds</span>
        <span>{property_details.bathrooms} baths</span>
      </div>
      {property.tags.premium && <Badge>Premium</Badge>}
    </div>
  );
}
```

### Dashboard

```typescript
import { useDashboard } from '@/lib/api/hooks';

export default function Dashboard() {
  const { stats, isLoading } = useDashboard();

  if (isLoading) return <Skeleton />;

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard title="Total Properties" value={stats.total_properties} />
      <StatCard title="For Sale" value={stats.for_sale_count} />
      <StatCard title="For Rent" value={stats.for_rent_count} />
      <StatCard title="Premium" value={stats.premium_count} />
    </div>
  );
}
```

---

## 🔧 Configuration

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
```

Update API client:

```typescript
// lib/api/client.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
```

---

## 📖 Full Documentation

- **All Endpoints**: [API_ENDPOINTS_ACTUAL.md](API_ENDPOINTS_ACTUAL.md) - Complete reference
- **TypeScript Types**: [types.ts](types.ts) - Type definitions
- **API Client**: [api-client.ts](api-client.ts) - HTTP client
- **React Hooks**: [hooks.tsx](hooks.tsx) - Data fetching hooks

---

## 🐛 Troubleshooting

### CORS Errors
API server has CORS enabled. Check you're using correct base URL.

### TypeScript Errors
Make sure all three files (types.ts, api-client.ts, hooks.tsx) are copied and dependencies installed.

### No Data Returned
1. Run a scrape first to populate Firestore
2. Test endpoint with curl
3. Check browser console

---

## 🚀 Next Steps

1. ✅ Copy integration files
2. ✅ Install dependencies (swr, axios)
3. ✅ Configure environment variables
4. ✅ Start building with hooks
5. ✅ Refer to [API_ENDPOINTS_ACTUAL.md](API_ENDPOINTS_ACTUAL.md)

---

**Version**: 3.2.0 (GitHub Actions + Streaming Firestore)
**Last Updated**: 2025-11-17
**Status**: ✅ Production Ready

---

## 🎬 Trigger Scraping from Frontend

### Option 1: Direct API Call (Recommended)

Start a scrape directly from your frontend:

```typescript
import { apiClient } from '@/lib/api/client';

// Start scrape with all 51 sites
const startFullScrape = async () => {
  const response = await apiClient.startScrape({
    max_pages: 20,
    geocode: true,
    enable_all_sites: true
  });

  return response.data; // { message, sites_count, max_pages }
};
```

### Option 2: GitHub Actions (Cloud-Based)

Trigger GitHub Actions workflow via API:

```typescript
const triggerGitHubScrape = async () => {
  const response = await fetch(
    'https://api.github.com/repos/Tee-David/realtors_practice/actions/workflows/scrape-production.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github+json',
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
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

  // Monitor at: https://github.com/Tee-David/realtors_practice/actions
};
```

**Key Features**:
- ✅ Scrapes all 51 real estate sites
- ✅ Uploads to Firestore in real-time (streaming architecture)
- ✅ 20 pages per site (configurable)
- ✅ Geocoding enabled
- ✅ Runs for 5-6 hours (intelligent batching)
- ✅ Properties available immediately via API

---

**Need more help?** See [../README.md](../README.md) for complete project documentation.
