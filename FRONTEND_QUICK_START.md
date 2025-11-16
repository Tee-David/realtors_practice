# Frontend Developer - 5-Minute Quick Start

Get your Nigerian Real Estate frontend up and running in **5 minutes**. Zero backend knowledge required.

## ⚡ Super Quick Setup

### Step 1: Copy 3 Files (30 seconds)

Copy these to your Next.js/React project:

```bash
# Copy to your project
frontend/types.ts      → your-project/lib/api/types.ts
frontend/api-client.ts → your-project/lib/api/client.ts
frontend/hooks.tsx     → your-project/lib/api/hooks.tsx
```

### Step 2: Install Dependencies (30 seconds)

```bash
npm install swr axios
# or
yarn add swr axios
```

### Step 3: Add API URL (30 seconds)

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
```

### Step 4: Start Coding (4 minutes)

You're done! Start using:

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, isLoading } = useProperties();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{properties.length} Properties</h1>
      {properties.map(p => (
        <div key={p.hash}>
          <h2>{p.basic_info.title}</h2>
          <p>{p.financial.currency} {p.financial.price.toLocaleString()}</p>
          <p>{p.location.area}, {p.location.lga}</p>
        </div>
      ))}
    </div>
  );
}
```

**That's it!** You now have access to 90 API endpoints and 500+ properties from Firestore.

---

## 🎯 What You Get

### Real-Time Data
- **500-2000+ properties** from 51 Nigerian real estate sites
- **Auto-updated** via GitHub Actions (running now!)
- **Enterprise schema** with 9 categories, 85+ fields
- **Firestore backend** - blazing fast queries

### React Hooks (Zero Config)

```typescript
// All properties
const { properties } = useProperties();

// For sale only
const { properties } = usePropertiesForSale();

// For rent only
const { properties } = usePropertiesForRent();

// Premium properties
const { properties } = usePremiumProperties();

// Search
const { properties } = usePropertySearch('Lagos Island');

// Dashboard stats
const { stats } = useDashboard();

// Scraper status
const { status, isRunning } = useScraperStatus();
```

### TypeScript Support

Full autocomplete for:
- All 90 API endpoints
- Enterprise schema (9 categories, 85+ fields)
- All request/response types
- Error handling

---

## 📝 Common Patterns

### Display Properties

```typescript
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading, error } = useProperties({
    limit: 20,
    offset: 0
  });

  if (isLoading) return <Loader />;
  if (error) return <Error message={error.message} />;

  return (
    <div>
      <h1>{total} Properties Available</h1>
      <div className="grid grid-cols-3 gap-4">
        {properties.map(property => (
          <PropertyCard key={property.hash} property={property} />
        ))}
      </div>
    </div>
  );
}
```

### Search Properties

```typescript
import { useState } from 'react';
import { usePropertySearch } from '@/lib/api/hooks';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const { properties, isLoading } = usePropertySearch(query);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search properties..."
      />
      {isLoading ? <Loader /> : <Results properties={properties} />}
    </div>
  );
}
```

### Property Details

```typescript
import { useRouter } from 'next/router';
import { useProperty } from '@/lib/api/hooks';

export default function PropertyPage() {
  const router = useRouter();
  const { property, isLoading } = useProperty(router.query.hash as string);

  if (isLoading) return <Loader />;
  if (!property) return <div>Not found</div>;

  const { basic_info, financial, location, property_details } = property;

  return (
    <div>
      <h1>{basic_info.title}</h1>
      <p className="price">
        {financial.currency} {financial.price.toLocaleString()}
      </p>
      <p>{location.area}, {location.lga}</p>
      <div>
        <span>{property_details.bedrooms} beds</span>
        <span>{property_details.bathrooms} baths</span>
      </div>
    </div>
  );
}
```

### Dashboard

```typescript
import { useDashboard } from '@/lib/api/hooks';

export default function Dashboard() {
  const { stats } = useDashboard();

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard title="Total" value={stats.total_properties} />
      <StatCard title="For Sale" value={stats.for_sale_count} />
      <StatCard title="For Rent" value={stats.for_rent_count} />
      <StatCard title="Premium" value={stats.premium_count} />
    </div>
  );
}
```

---

## 🏗️ Property Data Structure

Every property has this structure:

```typescript
property = {
  // Basic Info
  basic_info: {
    title: "5 Bedroom Detached Duplex",
    source: "npc",
    status: "for_sale",
    listing_type: "sale"
  },

  // Property Details
  property_details: {
    property_type: "Detached Duplex",
    bedrooms: 5,
    bathrooms: 5,
    furnishing: "unfurnished"
  },

  // Financial
  financial: {
    price: 85000000,
    currency: "NGN",
    price_per_sqm: 150000,
    price_per_bedroom: 17000000
  },

  // Location
  location: {
    address: "Lekki Phase 1",
    area: "Lekki",
    lga: "Eti-Osa",
    state: "Lagos",
    coordinates: { lat: 6.4, lng: 3.4 }
  },

  // Amenities
  amenities: {
    features: ["Swimming Pool", "Gym", "24/7 Security"],
    security: ["CCTV", "Security Guard"],
    utilities: ["Water", "Electricity"]
  },

  // Media
  media: {
    images: [
      { url: "https://...", order: 1 },
      { url: "https://...", order: 2 }
    ],
    videos: [],
    virtual_tour: ""
  },

  // Agent Info
  agent_info: {
    name: "John Doe",
    contact: "08012345678",
    agency: "ABC Realty"
  },

  // Metadata
  metadata: {
    quality_score: 85.5,
    view_count: 120,
    search_keywords: ["lekki", "duplex", "5 bedroom"]
  },

  // Tags
  tags: {
    premium: true,
    hot_deal: false,
    featured: true
  }
}
```

---

## 🚀 Advanced Features

### Trigger Scraping

```typescript
import { apiClient } from '@/lib/api/client';

// Start scraping
await apiClient.scraping.start({
  sites: ['npc', 'cwlagos'],
  max_pages: 10,
  geocoding: false
});

// Check status
const status = await apiClient.scraping.status();
console.log(status.is_running); // true/false
console.log(status.progress.completed_sites); // 2/2
```

### Trigger GitHub Actions (Parallel Scraping)

```typescript
import { apiClient } from '@/lib/api/client';

// Trigger large-scale scrape (51 sites in parallel)
await apiClient.github.triggerScrape({
  sites_per_session: 20,
  page_cap: 20,
  geocode: 1
});

// This runs 3 parallel sessions in GitHub Actions
// Expected time: 1-2 hours
// Result: 500-2000+ properties in Firestore
```

### Filter Properties

```typescript
// For sale properties
const { properties } = usePropertiesForSale({ limit: 20 });

// For rent properties
const { properties } = usePropertiesForRent({ limit: 20 });

// Premium properties
const { properties } = usePremiumProperties({ limit: 20 });

// By location (LGA)
const { properties } = usePropertiesByLGA('Eti-Osa');

// By area
const { properties } = usePropertiesByArea('Lekki');

// Verified only
const { properties } = useVerifiedProperties();

// Furnished only
const { properties } = useFurnishedProperties();
```

---

## 🎨 UI Components (Copy & Paste)

### Property Card

```typescript
import { Property } from '@/lib/api/types';
import Image from 'next/image';

export function PropertyCard({ property }: { property: Property }) {
  return (
    <div className="border rounded-lg overflow-hidden hover:shadow-lg transition">
      {/* Image */}
      {property.media.images?.[0] && (
        <div className="relative h-48">
          <Image
            src={property.media.images[0].url}
            alt={property.basic_info.title}
            fill
            className="object-cover"
          />
          {property.tags.premium && (
            <span className="absolute top-2 right-2 bg-yellow-500 text-white px-2 py-1 text-xs rounded">
              Premium
            </span>
          )}
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        <h3 className="font-bold text-lg mb-2 line-clamp-2">
          {property.basic_info.title}
        </h3>

        <p className="text-2xl font-bold text-blue-600 mb-2">
          {property.financial.currency} {property.financial.price.toLocaleString()}
        </p>

        <p className="text-gray-600 text-sm mb-3">
          {property.location.area}, {property.location.lga}
        </p>

        <div className="flex gap-4 text-sm text-gray-600">
          <span>{property.property_details.bedrooms} beds</span>
          <span>{property.property_details.bathrooms} baths</span>
          <span>{property.property_details.property_type}</span>
        </div>
      </div>
    </div>
  );
}
```

### Search Bar

```typescript
import { useState } from 'react';

export function SearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && onSearch(query)}
        placeholder="Search properties in Lagos..."
        className="w-full px-4 py-3 pr-12 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        onClick={() => onSearch(query)}
        className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-2 rounded"
      >
        Search
      </button>
    </div>
  );
}
```

### Filter Sidebar

```typescript
export function FilterSidebar({ onChange }: { onChange: (filters: any) => void }) {
  const [filters, setFilters] = useState({
    listing_type: 'all',
    min_price: '',
    max_price: '',
    bedrooms: '',
    area: ''
  });

  const handleChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onChange(newFilters);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Type</label>
        <select
          value={filters.listing_type}
          onChange={(e) => handleChange('listing_type', e.target.value)}
          className="w-full border rounded px-3 py-2"
        >
          <option value="all">All</option>
          <option value="sale">For Sale</option>
          <option value="rent">For Rent</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Price Range</label>
        <input
          type="number"
          placeholder="Min"
          value={filters.min_price}
          onChange={(e) => handleChange('min_price', e.target.value)}
          className="w-full border rounded px-3 py-2 mb-2"
        />
        <input
          type="number"
          placeholder="Max"
          value={filters.max_price}
          onChange={(e) => handleChange('max_price', e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Bedrooms</label>
        <select
          value={filters.bedrooms}
          onChange={(e) => handleChange('bedrooms', e.target.value)}
          className="w-full border rounded px-3 py-2"
        >
          <option value="">Any</option>
          <option value="1">1+</option>
          <option value="2">2+</option>
          <option value="3">3+</option>
          <option value="4">4+</option>
          <option value="5">5+</option>
        </select>
      </div>
    </div>
  );
}
```

---

## 📖 Documentation

- **All Endpoints**: [frontend/API_ENDPOINTS_ACTUAL.md](frontend/API_ENDPOINTS_ACTUAL.md)
- **Complete Guide**: [frontend/README.md](frontend/README.md)
- **Type Definitions**: [frontend/types.ts](frontend/types.ts)

---

## ✅ Checklist for Your Developer

- [ ] Copy 3 files (types.ts, api-client.ts, hooks.tsx)
- [ ] Install dependencies (`npm install swr axios`)
- [ ] Add `.env.local` with API URL
- [ ] Import and use hooks in components
- [ ] Test with properties page
- [ ] Build search functionality
- [ ] Add filters (optional)
- [ ] Deploy!

**Estimated Time**: 1-2 hours for basic integration, 1 day for full feature set

---

## 🆘 Troubleshooting

### No data showing?
Data is being scraped right now via GitHub Actions! Check back in 1-2 hours or trigger a quick test scrape.

### TypeScript errors?
Make sure all 3 files are copied and SWR + Axios are installed.

### CORS errors?
API has CORS enabled. Check your API URL in `.env.local`.

---

## 🎯 Next Steps

1. ✅ Copy the 3 files
2. ✅ Install dependencies
3. ✅ Start building pages
4. ✅ Reference [frontend/API_ENDPOINTS_ACTUAL.md](frontend/API_ENDPOINTS_ACTUAL.md) as needed

**Questions?** Everything is documented in the `frontend/` and `docs/` folders!

---

**Version**: 3.1.0
**Status**: ✅ Production Ready
**Data Source**: Live Firestore (500-2000+ properties)
**API Status**: https://realtors-practice-api.onrender.com/api/health
