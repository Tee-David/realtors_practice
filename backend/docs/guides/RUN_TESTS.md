# Complete Test Guide

## Test Results Summary (v3.3.0)

### ✅ Tests Completed (Without API Server)

**Test Suite:** `test_comprehensive_v3.3.0.py`
**Status:** 6/6 PASSED (9 skipped - require API server)

```
✅ PASSED Tests:
1. Firestore Environment - Credentials configured
2. Firestore Connection - Database accessible
3. Data Integrity - 10/10 documents have complete schema
4. No Workbook Dependencies - Legacy code removed
5. Documentation Complete - All files exist
6. Git Status - Working tree tracked

⏭️ SKIPPED Tests (require API server running):
- API Health Check
- Price Range Filtering
- Nested Field Queries
- Sort Field Mapping
- Complex Queries
- Export Endpoint
- Archive Queries
- Pagination
- Legacy Endpoints Check
```

---

## How to Run Full API Tests

### Step 1: Start the API Server

**Terminal 1:**
```bash
cd functions
python api_server.py
```

**Wait for:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

### Step 2: Run API & Frontend Tests

**Terminal 2:**
```bash
# From project root
python test_api_and_frontend.py
```

---

## What Gets Tested (API & Frontend Suite)

### 🎯 Critical Tests (Price Filtering Fix)
1. ✅ API Health Check
2. ✅ **Price Range Filtering** (CRITICAL FIX)
3. ✅ Location Filtering (Nested Path)
4. ✅ Property Type Filtering
5. ✅ Bedrooms Filtering
6. ✅ Combined Filters (Complex Query)

### 🔀 Sorting Tests
7. ✅ Sort by Price (Ascending)
8. ✅ Sort by Price (Descending)
9. ✅ Sort by Bedrooms

### 📄 Pagination Tests
10. ✅ Pagination - Page 1
11. ✅ Pagination - Page 2

### 📊 Export Tests
12. ✅ Export as JSON
13. ✅ Export as CSV

### ⚛️ Frontend Hook Compatibility
14. ✅ useFirestoreProperties Hook
15. ✅ useFirestoreSearch Hook
16. ✅ useFirestorePagination Hook

### 🏗️ Data Structure
17. ✅ Response Structure Validation

**Total:** 17 comprehensive tests

---

## Quick Test (Manual)

### Test 1: Price Filtering (Most Important!)

```bash
curl -X POST http://localhost:5000/api/firestore/query \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "price_min": 5000000,
      "price_max": 50000000
    },
    "limit": 5
  }'
```

**Expected Response:**
```json
{
  "results": [
    {
      "financial": {
        "price": 35000000
      },
      "property_details": {
        "bedrooms": 3,
        "property_type": "Flat"
      },
      "location": {
        "area": "Lekki"
      }
    }
  ],
  "count": 5
}
```

### Test 2: Complex Filter (What Frontend Will Use)

```bash
curl -X POST http://localhost:5000/api/firestore/query \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "location.area": "Lekki",
      "price_min": 10000000,
      "price_max": 50000000,
      "bedrooms": 3,
      "property_type": "Flat"
    },
    "sort_by": "price",
    "sort_desc": false,
    "limit": 10
  }'
```

### Test 3: Export (CSV)

```bash
curl -X POST http://localhost:5000/api/firestore/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "limit": 100
  }' \
  --output test_export.csv
```

---

## Frontend Hook Examples

### Example 1: Basic Property List

```typescript
import { useFirestoreProperties } from './useFirestore';

function PropertyList() {
  const { properties, isLoading, error } = useFirestoreProperties({
    limit: 20
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {properties.map(prop => (
        <PropertyCard key={prop.id} property={prop} />
      ))}
    </div>
  );
}
```

### Example 2: Filtered Search

```typescript
const { properties } = useFirestoreProperties({
  filters: {
    'location.area': 'Lekki',
    price_min: 5000000,
    price_max: 50000000,
    bedrooms: 3
  },
  sort_by: 'price',
  sort_desc: false,
  limit: 20
});
```

### Example 3: Pagination

```typescript
const [page, setPage] = useState(0);
const limit = 20;

const { properties, count } = useFirestoreProperties({
  limit: limit,
  offset: page * limit
});

const totalPages = Math.ceil(count / limit);
```

---

## Test Results Checklist

Before marking frontend as ready, verify:

- [ ] **Firestore Connection** - Can connect to database
- [ ] **Price Filtering** - Price ranges work correctly
- [ ] **Nested Paths** - location.area, financial.price work
- [ ] **Sorting** - Price, bedrooms sorting works
- [ ] **Pagination** - Multiple pages accessible
- [ ] **Complex Queries** - Multiple filters combine correctly
- [ ] **Export** - CSV/JSON export functional
- [ ] **Response Structure** - Matches TypeScript types
- [ ] **Frontend Hooks** - All hooks compatible

---

## Troubleshooting

### Test Fails: "API server not running"

**Solution:**
```bash
cd functions
python api_server.py
```

Wait for "Running on http://localhost:5000" message.

### Test Fails: "No data found"

**Cause:** Firestore collection empty or filters too restrictive.

**Solution:**
- Run scraper to populate data
- Use broader filters (remove price_min/max)
- Check Firestore Console for actual data

### Test Fails: "Composite index required"

**Cause:** Firestore needs index for complex query.

**Solution:**
1. Go to Firebase Console → Firestore → Indexes
2. Create composite index for field combination
3. Wait for "Enabled" status
4. Re-run test

---

## Expected Test Results

### Without API Server
```
Passed: 6
Failed: 0
Skipped: 9
Status: ✅ SUCCESS
```

### With API Server
```
Passed: 17
Failed: 0
Status: ✅ SUCCESS (Frontend Ready)
```

---

## Next Steps After All Tests Pass

1. ✅ **Share with Frontend Developer:**
   - `frontend/FIRESTORE_QUERY_REFERENCE.md`
   - `FOR_FRONTEND_DEVELOPER.md`

2. ✅ **Create Firestore Indexes** (5 minutes)
   - See `IMPROVEMENTS_V3.3.0.md` section 4.A.1

3. ✅ **Deploy API Server** (when ready)
   - Test with production Firestore
   - Update frontend API_URL

4. ✅ **Monitor Performance**
   - Check query speeds
   - Monitor Firestore costs
   - Add caching if needed

---

## Summary

**Current Status:**
- ✅ Core architecture: Verified
- ✅ Firestore connection: Working
- ✅ Data integrity: Confirmed
- ⏳ API endpoints: Ready to test (need server running)
- ⏳ Frontend integration: Ready to test (need server running)

**To Complete Full Verification:**
1. Start API server (`python functions/api_server.py`)
2. Run `python test_api_and_frontend.py`
3. Verify all 17 tests pass

**Everything is ready for thorough testing!** 🚀
