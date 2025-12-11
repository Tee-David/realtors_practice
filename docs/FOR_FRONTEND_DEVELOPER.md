# For Frontend Developer - Quick Integration Guide

**Version:** v3.2.2
**Last Updated:** 2025-12-11
**Status:** ✅ 100% Production Ready

---

## 🎯 What You Need to Know

This API lets your frontend:
1. **Trigger scrapes** from GitHub Actions (cloud-based, no local scraping)
2. **Query properties** from Firestore (real-time database)
3. **Export data** to CSV/Excel
4. **Get time estimates** to prevent timeouts

**Everything is ready to use. Just copy 3 files and start building.**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Copy Integration Files

Copy these 3 files from `frontend/` to your project:

```
frontend/
├── types.ts        → Copy to: lib/api/types.ts
├── api-client.ts   → Copy to: lib/api/client.ts
└── hooks.tsx       → Copy to: lib/api/hooks.tsx
```

### Step 2: Install Dependencies

```bash
npm install swr axios
```

### Step 3: Use in Your Components

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

**That's it! You're done.**

---

## 📡 API Base URL

**Development:**
```
http://localhost:5000
```

**Production (when backend is deployed):**
```
https://your-backend-url.com
```

Update the base URL in `api-client.ts` (line 4).

---

## 🔥 Most Important Endpoints

### 1. Trigger Scrape from Frontend

```typescript
import { apiClient } from '@/lib/api/client';

const triggerScrape = async () => {
  const result = await apiClient.github.triggerScrape({
    max_pages: 15,      // Pages per site
    geocode: 1,         // Enable geocoding (0 or 1)
    sites: ['npc']      // Optional: specific sites (leave empty for all)
  });

  console.log('Workflow started:', result.run_url);
};
```

**What happens:**
- Frontend calls API endpoint
- API triggers GitHub Actions workflow
- Workflow scrapes sites in the cloud (takes 5-30 minutes)
- Data automatically uploaded to Firestore
- Frontend queries Firestore for results

**Workflow File:** `.github/workflows/scrape-production.yml`

### 2. Get Time Estimate (Prevent Timeouts)

```typescript
const estimate = await apiClient.github.estimateScrapeTime({
  max_pages: 15,
  geocode: 1
});

console.log(`Estimated time: ${estimate.estimated_duration_text}`);
console.log(`Risk level: ${estimate.timeout_risk}`); // safe, warning, or danger

if (estimate.timeout_risk === 'danger') {
  alert('This will take too long! Try fewer pages.');
}
```

### 3. Query Properties from Firestore

```typescript
// Get all properties
const { properties } = useProperties();

// Search with filters
const { properties } = useProperties({
  filters: {
    price_max: 50000000,
    bedrooms_min: 3,
    location_area: 'Lekki'
  },
  limit: 20
});

// Get newest listings
const newest = await apiClient.firestore.getNewest(10);

// Get hot deals
const deals = await apiClient.firestore.getHotDeals(20);
```

### 4. Export Data

```typescript
const exportFile = await apiClient.export.generate({
  format: 'excel',           // or 'csv'
  filters: {
    price_max: 100000000
  },
  filename: 'properties.xlsx'
});

console.log('Download:', exportFile.download_url);
```

---

## 📊 Property Data Structure

Each property has 9 categories with 85+ fields:

```typescript
interface Property {
  basic_info: {
    title: string;
    listing_url: string;
    source: string;
    status: 'available' | 'sold' | 'rented';
    listing_type: 'sale' | 'rent' | 'lease';  // Auto-detected
  };

  property_details: {
    property_type: string;
    bedrooms: number;
    bathrooms: number;
    furnishing: 'furnished' | 'semi-furnished' | 'unfurnished';  // Auto-detected
    condition: 'new' | 'renovated' | 'old';  // Auto-detected
  };

  financial: {
    price: number;
    currency: 'NGN';
    price_per_sqm: number;
    price_per_bedroom: number;
  };

  location: {
    address: string;
    area: string;        // e.g., "Lekki"
    lga: string;         // e.g., "Eti-Osa"
    state: string;       // "Lagos"
    coordinates: {       // GeoPoint (lat, lng)
      latitude: number;
      longitude: number;
    };
    landmarks: string[];  // 50+ Lagos landmarks
  };

  amenities: {
    features: string[];   // ["Pool", "Gym", "Security"]
    security: string[];
    utilities: string[];
  };

  media: {
    images: Array<{
      url: string;
      order: number;
    }>;
    videos: string[];
    virtual_tour: string;
  };

  agent_info: {
    name: string;
    contact: string;
    agency: string;
  };

  metadata: {
    quality_score: number;       // 0-100
    view_count: number;
    inquiry_count: number;
    days_on_market: number;
    scrape_timestamp: Date;
  };

  tags: {
    premium: boolean;            // Auto-tagged (price ≥100M or 4+ BR)
    hot_deal: boolean;           // Auto-tagged (<15M per bedroom)
    featured: boolean;
  };
}
```

---

## 🎨 Complete Examples

### Dashboard Component

```typescript
import { useDashboard } from '@/lib/api/hooks';

export default function Dashboard() {
  const { data, isLoading } = useDashboard();

  if (isLoading) return <Skeleton />;

  return (
    <div>
      <StatCard title="Total Properties" value={data.total_properties} />
      <StatCard title="For Sale" value={data.total_for_sale} />
      <StatCard title="For Rent" value={data.total_for_rent} />
      <StatCard title="Premium" value={data.premium_properties} />

      <PriceChart
        min={data.price_range.min}
        max={data.price_range.max}
        avg={data.price_range.avg}
      />

      <TopAreas areas={data.top_areas} />
    </div>
  );
}
```

### Search Component

```typescript
import { useState } from 'react';
import { useProperties } from '@/lib/api/hooks';

export default function PropertySearch() {
  const [filters, setFilters] = useState({
    price_max: 100000000,
    bedrooms_min: 2,
    location_area: ''
  });

  const { properties, total, isLoading } = useProperties({ filters });

  return (
    <div>
      <SearchFilters filters={filters} onChange={setFilters} />

      {isLoading ? (
        <Skeleton />
      ) : (
        <div>
          <p>{total} properties found</p>
          <PropertyGrid properties={properties} />
        </div>
      )}
    </div>
  );
}
```

### Scrape Trigger Component

```typescript
import { useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function ScrapeTrigger() {
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({
    max_pages: 15,
    geocode: 1,
    sites: []  // Empty = all enabled sites
  });

  const handleTrigger = async () => {
    setLoading(true);

    // Get time estimate first
    const estimate = await apiClient.github.estimateScrapeTime(params);

    if (estimate.timeout_risk === 'danger') {
      alert(`Too long! Estimated: ${estimate.estimated_duration_text}`);
      setLoading(false);
      return;
    }

    // Trigger scrape
    const result = await apiClient.github.triggerScrape(params);

    alert(`Scrape started! Check status at: ${result.run_url}`);
    setLoading(false);
  };

  return (
    <div>
      <h2>Trigger New Scrape</h2>

      <input
        type="number"
        value={params.max_pages}
        onChange={(e) => setParams({ ...params, max_pages: parseInt(e.target.value) })}
        placeholder="Pages per site"
      />

      <label>
        <input
          type="checkbox"
          checked={params.geocode === 1}
          onChange={(e) => setParams({ ...params, geocode: e.target.checked ? 1 : 0 })}
        />
        Enable Geocoding
      </label>

      <button onClick={handleTrigger} disabled={loading}>
        {loading ? 'Starting...' : 'Start Scrape'}
      </button>
    </div>
  );
}
```

---

## 📚 Complete Documentation

### Main Files (Start Here)

1. **`frontend/README.md`** - Complete integration guide with all examples
2. **`frontend/API_ENDPOINTS_ACTUAL.md`** - All 90 endpoints documented
3. **`frontend/types.ts`** - TypeScript type definitions
4. **`frontend/api-client.ts`** - HTTP client implementation
5. **`frontend/hooks.tsx`** - React hooks with SWR

### Additional Documentation

- **`docs/frontend/TIME_ESTIMATION_ENDPOINT.md`** - Detailed time estimation guide
- **`docs/frontend/FRONTEND_INTEGRATION_GUIDE.md`** - Extended integration guide
- **`docs/frontend/POSTMAN_GUIDE.md`** - API testing with Postman

---

## ⚠️ Important Notes

### Workflow File Name

**Correct:** `.github/workflows/scrape-production.yml`
**Old/Wrong:** `.github/workflows/scrape-production.yml` ❌

If you see references to `scrape-production.yml` in old documentation, it's outdated. The actual workflow is `scrape-production.yml`.

### API Endpoint Count

**Total:** 90 endpoints
- 72 core endpoints (scraping, sites, data, exports, etc.)
- 18 Firestore enterprise endpoints (queries, filters, search)

### Firestore Schema Version

**Current:** Enterprise Schema v3.2 (9 categories, 85+ fields)

---

## 🆘 Common Issues

### Issue 1: "Can't trigger scrape from frontend"

**Solution:** Make sure API server is running locally:
```bash
cd backend
python api_server.py
```

### Issue 2: "Firestore queries returning empty"

**Solution:** You need to run a scrape first to populate Firestore:
```typescript
// Trigger scrape
await apiClient.github.triggerScrape({ max_pages: 2, geocode: 1 });

// Wait 5-10 minutes for workflow to complete
// Then query Firestore
const properties = await apiClient.firestore.getNewest(10);
```

### Issue 3: "Scrape timing out"

**Solution:** Use time estimation before triggering:
```typescript
const estimate = await apiClient.github.estimateScrapeTime({ max_pages: 15 });

if (estimate.timeout_risk !== 'safe') {
  // Reduce max_pages or disable some sites
  console.log('Recommendations:', estimate.recommendations);
}
```

---

## ✅ Checklist for Integration

- [ ] Copied 3 files from `frontend/` to your project
- [ ] Installed `swr` and `axios`
- [ ] Updated base URL in `api-client.ts`
- [ ] API server running (`python api_server.py`)
- [ ] Tested health endpoint (`/api/health`)
- [ ] Triggered test scrape (2-3 sites, 2 pages)
- [ ] Verified Firestore data populated
- [ ] Built dashboard component
- [ ] Built search component
- [ ] Built scrape trigger component

---

## 🎯 Next Steps

1. **Test locally** - Copy files, install deps, run API server
2. **Build dashboard** - Use `useDashboard()` hook
3. **Build search** - Use `useProperties()` with filters
4. **Add scrape trigger** - Use `apiClient.github.triggerScrape()`
5. **Deploy backend** - Deploy to Render/Railway/Vercel
6. **Update frontend base URL** - Point to deployed backend

---

**Need Help?**

- Check `frontend/README.md` for detailed examples
- Check `frontend/API_ENDPOINTS_ACTUAL.md` for all 90 endpoints
- All TypeScript types are in `frontend/types.ts`

**Everything is tested and production-ready. Just copy, paste, and build!** 🚀
