# Firestore Integration Guide

## The Problem

Your frontend wasn't seeing properties from Firestore because:

1. ✅ **Firestore has 352 properties** - Verified
2. ✅ **API endpoint `/api/firestore/query` works** - Tested successfully
3. ✅ **CORS is enabled** - Flask app has CORS configured
4. ✅ **API client has `queryFirestore()` method** - Already defined
5. ❌ **BUT: No React hooks for Firestore queries existed!**

The existing `useProperties()` hook in `hooks.tsx` was fetching from `/data/sites` (Excel/CSV files), NOT from Firestore.

## The Solution

Created new Firestore-specific React hooks in `useFirestore.tsx`:

### 1. Basic Firestore Hook

```tsx
import { useFirestoreProperties } from './useFirestore';

const { properties, count, isLoading, error } = useFirestoreProperties({
  limit: 20,
  sort_by: 'uploaded_at',
  sort_desc: true
});
```

### 2. Filtered Queries

```tsx
const { properties, isLoading } = useFirestoreProperties({
  filters: {
    'location.state': 'Lagos',
    'property_details.bedrooms': 3,
    'financial.price': 25000000
  },
  limit: 50,
  sort_by: 'financial.price',
  sort_desc: false
});
```

### 3. Search Hook

```tsx
import { useFirestoreSearch } from './useFirestore';

const search = useFirestoreSearch();

// Search by location
search.byState('Lagos');

// Search by bedrooms
search.byBedrooms(3);

// Access results
const { properties, count, isLoading } = search;
```

### 4. Pagination Hook

```tsx
import { useFirestorePagination } from './useFirestore';

const {
  properties,
  hasMore,
  loadMore,
  isLoading,
  totalCount
} = useFirestorePagination(
  {
    filters: { 'location.state': 'Lagos' }
  },
  20 // page size
);
```

## Firestore Data Structure

Your Firestore uses a **nested schema**. Access fields using dot notation:

```typescript
// ❌ WRONG - Won't work
filters: {
  price: 25000000,
  bedrooms: 3,
  location: 'Lekki'
}

// ✅ CORRECT - Use nested paths
filters: {
  'financial.price': 25000000,
  'property_details.bedrooms': 3,
  'location.location_text': 'Lekki'
}
```

### Full Schema Reference

```typescript
{
  basic_info: {
    title: string,
    listing_url: string,
    status: string,
    site_key: string,
    source: string,
    listing_type: string
  },

  financial: {
    price: number,
    price_currency: string,
    service_charge: number,
    price_negotiable: boolean
  },

  property_details: {
    bedrooms: number,
    bathrooms: number,
    property_type: string,
    furnishing: string,
    land_size: string
  },

  location: {
    location_text: string,
    state: string,
    lga: string,
    area: string,
    coordinates: { lat: number, lng: number }
  },

  amenities: {
    features: string[],
    utilities: string[],
    security: string[]
  },

  media: {
    images: Array<{ url: string, caption: string }>,
    videos: string[],
    floor_plan_url: string
  },

  metadata: {
    quality_score: number,
    scrape_timestamp: string,
    days_on_market: number,
    hash: string
  }
}
```

## Quick Start

### Step 1: Import the hooks

```tsx
import { useFirestoreProperties } from './useFirestore';
```

### Step 2: Use in your component

```tsx
function PropertyListPage() {
  const { properties, isLoading, error } = useFirestoreProperties({
    limit: 20,
    sort_by: 'uploaded_at',
    sort_desc: true
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Properties ({properties.length})</h1>
      {properties.map((property, index) => (
        <div key={index}>
          <h3>{property.basic_info?.title}</h3>
          <p>Price: ₦{property.financial?.price?.toLocaleString()}</p>
          <p>Location: {property.location?.location_text}</p>
          <p>Bedrooms: {property.property_details?.bedrooms}</p>
        </div>
      ))}
    </div>
  );
}
```

### Step 3: Add filtering

```tsx
const [state, setState] = useState('Lagos');
const [bedrooms, setBedrooms] = useState(3);

const { properties, isLoading } = useFirestoreProperties({
  filters: {
    'location.state': state,
    'property_details.bedrooms': bedrooms
  },
  limit: 20
});
```

## API Server

Make sure the API server is running:

```bash
cd functions
python api_server.py
```

Or with environment variables:

```bash
FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json" \
python api_server.py
```

The API will be available at `http://localhost:5000`

## Complete Example

See `PropertyListExample.tsx` for full working examples including:
- Simple property list
- Filtered search
- Interactive search UI
- Infinite scroll pagination

## Troubleshooting

### Properties not loading?

1. **Check API server is running**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Verify Firestore connection**
   ```bash
   python verify_firestore_data.py
   ```

3. **Check browser console** for CORS or network errors

4. **Verify API client base URL** in your component:
   ```tsx
   import { RealEstateApiClient } from './api-client';

   const client = new RealEstateApiClient({
     baseUrl: 'http://localhost:5000/api'
   });
   ```

### CORS errors?

The API server already has CORS enabled. If you still see CORS errors:

1. Check the API server is running on the correct port (5000)
2. Verify your frontend is making requests to `http://localhost:5000/api`
3. Check browser network tab for the actual request URL

### Empty results?

If you get 0 results when you expect data:

1. **Remove all filters** and try a basic query first
2. **Check filter field names** - use nested paths like `'financial.price'` not `'price'`
3. **Verify data exists** - run `python verify_firestore_data.py`

## Summary

✅ **352 properties available in Firestore**
✅ **API endpoint working correctly**
✅ **CORS enabled**
✅ **New React hooks created**
✅ **Example components provided**

Your frontend can now fetch listings from Firestore! Use the new hooks in `useFirestore.tsx` instead of the old `useProperties()` hook.
