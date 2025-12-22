# Firestore Query Reference for Frontend
**Last Updated:** 2025-12-22 (v3.3.0)
**Status:** ✅ Price filtering FIXED!

---

## Quick Start

The Firestore query endpoints now use **nested field paths** from the enterprise schema. This guide shows you exactly how to filter and sort properties.

---

## 🎯 Common Use Cases

### 1. Filter by Price Range

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    price_min: 5000000,      // ₦5M minimum
    price_max: 50000000      // ₦50M maximum
  },
  limit: 20
});
```

**API Request:**
```json
POST /api/firestore/query
{
  "filters": {
    "price_min": 5000000,
    "price_max": 50000000
  },
  "limit": 20
}
```

---

### 2. Filter by Location

```typescript
// By area
const { properties } = useFirestoreProperties({
  filters: {
    "location.area": "Lekki"
  }
});

// By LGA (Local Government Area)
const { properties } = useFirestoreProperties({
  filters: {
    "location.lga": "Eti-Osa"
  }
});

// By state
const { properties } = useFirestoreProperties({
  filters: {
    "location.state": "Lagos"
  }
});
```

**API Request:**
```json
POST /api/firestore/query
{
  "filters": {
    "location.area": "Victoria Island",
    "location.lga": "Eti-Osa",
    "location.state": "Lagos"
  }
}
```

---

### 3. Filter by Bedrooms/Bathrooms

```typescript
// Exact match
const { properties } = useFirestoreProperties({
  filters: {
    bedrooms: 3,        // Exactly 3 bedrooms
    bathrooms: 2        // Exactly 2 bathrooms
  }
});

// Minimum values
const { properties } = useFirestoreProperties({
  filters: {
    bedrooms_min: 2,    // 2+ bedrooms
    bathrooms_min: 1    // 1+ bathrooms
  }
});
```

**API Request:**
```json
POST /api/firestore/query
{
  "filters": {
    "bedrooms": 3,
    "bathrooms_min": 2
  }
}
```

---

### 4. Filter by Property Type

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    property_type: "Flat"
  }
});
```

**Common Property Types:**
- `"Flat"` / `"Apartment"`
- `"Detached Duplex"` / `"Semi Detached Duplex"`
- `"Terrace"` / `"Terraced Duplex"`
- `"House"` / `"Bungalow"`
- `"Land"` / `"Residential Land"`
- `"Commercial Property"` / `"Office Space"`

---

### 5. Filter by Furnishing

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    furnishing: "Furnished"
  }
});
```

**Furnishing Values:**
- `"Furnished"` - Fully furnished
- `"Semi-Furnished"` - Partially furnished
- `"Unfurnished"` - Empty property

---

### 6. Filter by Source/Site

```typescript
// By source (site name)
const { properties } = useFirestoreProperties({
  filters: {
    source: "npc"
  }
});

// By site key
const { properties } = useFirestoreProperties({
  filters: {
    site_key: "propertypro"
  }
});
```

**Popular Sources:**
- `"npc"` - Nigeria Property Centre
- `"propertypro"` - PropertyPro.ng
- `"privatepropertyng"` - PrivateProperty
- `"tolet"` - ToLet.com.ng

---

### 7. Filter by Status

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    status: "available"
  }
});
```

**Status Values:**
- `"available"` - Currently available
- `"sold"` - Already sold
- `"rented"` - Already rented
- `"pending"` - Under negotiation

---

### 8. Filter by Listing Type

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    listing_type: "sale"
  }
});
```

**Listing Types:**
- `"sale"` - For sale
- `"rent"` - For rent
- `"shortlet"` - Short-term rental

---

### 9. Filter by Quality Score

```typescript
// Only high-quality listings
const { properties } = useFirestoreProperties({
  filters: {
    quality_score_min: 0.7
  }
});
```

**Quality Score Range:** 0.0 - 1.0
- `0.8+` - Excellent quality
- `0.6-0.8` - Good quality
- `<0.6` - Lower quality (may have missing data)

---

## 🔀 Sorting

### Sort by Price

```typescript
// Cheapest first
const { properties } = useFirestoreProperties({
  filters: { price_min: 1000000 },
  sort_by: "price",
  sort_desc: false
});

// Most expensive first
const { properties } = useFirestoreProperties({
  filters: { price_min: 1000000 },
  sort_by: "price",
  sort_desc: true
});
```

### Sort by Bedrooms

```typescript
const { properties } = useFirestoreProperties({
  sort_by: "bedrooms",
  sort_desc: true    // Most bedrooms first
});
```

### Sort by Upload Date

```typescript
// Newest first (default)
const { properties } = useFirestoreProperties({
  sort_by: "uploaded_at",
  sort_desc: true
});

// Oldest first
const { properties } = useFirestoreProperties({
  sort_by: "uploaded_at",
  sort_desc: false
});
```

### Available Sort Fields

- `"price"` - Financial value
- `"bedrooms"` - Number of bedrooms
- `"bathrooms"` - Number of bathrooms
- `"quality_score"` - Listing quality
- `"uploaded_at"` - When added to database
- `"updated_at"` - Last modification time

---

## 🎨 Complex Queries (Combining Filters)

### Example 1: Luxury Apartments in Lekki

```typescript
const { properties, isLoading } = useFirestoreProperties({
  filters: {
    "location.area": "Lekki",
    property_type: "Flat",
    bedrooms_min: 3,
    bathrooms_min: 2,
    price_min: 50000000,
    furnishing: "Furnished"
  },
  sort_by: "price",
  sort_desc: false,
  limit: 20
});
```

**Result:** Furnished 3+ bedroom flats in Lekki, ₦50M+, cheapest first.

---

### Example 2: Budget Homes for Rent

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    listing_type: "rent",
    price_max: 2000000,
    bedrooms_min: 2,
    "location.state": "Lagos"
  },
  sort_by: "price",
  sort_desc: false,
  limit: 50
});
```

**Result:** 2+ bedroom rentals in Lagos under ₦2M/year, cheapest first.

---

### Example 3: High-Quality Recent Listings

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    quality_score_min: 0.8,
    bedrooms: 4,
    property_type: "Detached Duplex"
  },
  sort_by: "uploaded_at",
  sort_desc: true,
  limit: 10
});
```

**Result:** Top 10 newest high-quality 4-bedroom detached duplexes.

---

### Example 4: Investment Properties

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    property_type: "Land",
    "location.lga": "Ibeju-Lekki",
    price_max: 20000000
  },
  sort_by: "price",
  sort_desc: false,
  limit: 30
});
```

**Result:** Affordable land in Ibeju-Lekki under ₦20M, cheapest first.

---

## 📄 Pagination

### Basic Pagination

```typescript
const [page, setPage] = useState(0);
const limit = 20;

const { properties, count } = useFirestoreProperties({
  filters: { bedrooms: 3 },
  limit: limit,
  offset: page * limit
});

// Next page
const nextPage = () => setPage(page + 1);

// Previous page
const prevPage = () => setPage(Math.max(0, page - 1));
```

### Infinite Scroll

```typescript
const { properties, refetch } = useFirestoreProperties({
  filters: { listing_type: "sale" },
  limit: 20
});

const loadMore = () => {
  // Fetch next batch
  refetch();
};
```

---

## 🔍 Search Integration

### Text Search (Full-Text)

```typescript
import { apiClient } from './api-client';

// Search in titles, descriptions, locations
const searchResults = await apiClient.searchProperties({
  query: "luxury apartment lekki",
  limit: 20
});
```

**Search Endpoint:** `GET /api/data/search?q=...&limit=...`

---

## 📊 Export Filtered Data

```typescript
import { useFirestoreExport } from './useFirestoreExport';

function ExportButton() {
  const { exportData, isExporting } = useFirestoreExport();

  const handleExport = async () => {
    await exportData({
      format: 'csv',
      filters: {
        "location.area": "Ikoyi",
        price_min: 100000000
      },
      limit: 1000
    });
  };

  return (
    <button onClick={handleExport} disabled={isExporting}>
      {isExporting ? 'Exporting...' : 'Export to CSV'}
    </button>
  );
}
```

**Supported Formats:**
- `"csv"` - CSV file (recommended)
- `"json"` - JSON file
- `"excel"` - Excel XLSX file

---

## ⚠️ Important Notes

### 1. Filter Syntax

**✅ CORRECT:**
```json
{
  "filters": {
    "location.area": "Lekki",
    "price_min": 5000000
  }
}
```

**❌ WRONG:**
```json
{
  "filters": {
    "location": "Lekki",        // Won't work - use location.area
    "price": 5000000            // Won't work - use price_min/price_max
  }
}
```

### 2. Firestore Limitations

**Range Queries:**
- Can only have **one range filter** per query
- If using `price_min` + `price_max`, don't add `bedrooms_min` (use exact `bedrooms`)

**Workaround:**
```typescript
// WORKS: Price range only
{ price_min: 5000000, price_max: 50000000 }

// WORKS: Price range + exact bedrooms
{ price_min: 5000000, price_max: 50000000, bedrooms: 3 }

// WON'T WORK: Two range filters
{ price_min: 5000000, price_max: 50000000, bedrooms_min: 2 }
// Error: "Cannot have inequality filters on multiple properties"
```

**Solution:** Create a Firestore composite index for complex queries (ask backend to set up).

### 3. Performance Tips

**✅ Fast Queries:**
- Single equality filter + sort
- Price range + sort by price
- Location + property type

**⚠️ Slower Queries:**
- Multiple range filters (needs index)
- Large offsets (page 50+)
- No filters with large datasets

**Best Practices:**
- Always set `limit` (default: 50, max: 1000)
- Use `quality_score_min: 0.7` to filter out low-quality listings
- Prefer exact matches over ranges when possible

---

## 🆘 Troubleshooting

### Query Returns No Results

**Check:**
1. Are filter values correct? (case-sensitive)
2. Are you using nested paths? (`location.area` not `location`)
3. Is data available for those filters? (check in Firebase Console)

### Query Fails with "Composite Index Required"

**Solution:** Backend needs to create a Firestore index for your query combination. Report which filters you're combining.

### Query is Slow

**Solutions:**
1. Add `limit` to reduce results
2. Use exact matches instead of ranges
3. Request composite index for your query pattern

---

## 📚 Additional Resources

- **API Documentation:** `frontend/API_ENDPOINTS_ACTUAL.md`
- **Schema Reference:** `frontend/FIRESTORE_INTEGRATION_GUIDE.md`
- **React Hooks:** `frontend/useFirestore.tsx`
- **Export Hook:** `frontend/useFirestoreExport.tsx`
- **Examples:** `frontend/PropertyListExample.tsx`

---

## ✅ Testing Your Queries

### Quick Test (Browser Console)

```javascript
// Test price filtering
fetch('http://localhost:5000/api/firestore/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filters: {
      price_min: 10000000,
      price_max: 50000000
    },
    limit: 10
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

### Expected Response

```json
{
  "results": [
    {
      "basic_info": {
        "title": "...",
        "source": "npc",
        "status": "available"
      },
      "financial": {
        "price": 35000000,
        "price_currency": "NGN"
      },
      "property_details": {
        "bedrooms": 4,
        "bathrooms": 3,
        "property_type": "Detached Duplex"
      },
      "location": {
        "area": "Lekki",
        "lga": "Eti-Osa",
        "state": "Lagos"
      }
    }
  ],
  "count": 10,
  "filters_applied": {
    "price_min": 10000000,
    "price_max": 50000000
  }
}
```

---

**Questions?** Check the main frontend guide: `FOR_FRONTEND_DEVELOPER.md`
