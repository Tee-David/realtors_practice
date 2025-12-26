# Critical Issues Found - Playwright Testing Results
**Date:** 2025-12-25
**Status:** 🔴 Multiple Critical Issues

## Executive Summary

Comprehensive Playwright testing revealed **10 critical issues** that make the application largely non-functional for end users. The property listings are displayed, but:
- Search and filters don't work
- Property counts are incorrect
- Most property data is incomplete/unusable
- Dashboard monitoring sections are non-functional

---

## 🔴 CRITICAL ISSUES

### 1. **Property Count Completely Wrong**
- **Frontend Shows:** Total: 20, Showing: 20
- **Backend Actually Has:** 64+ properties for sale (366 total in Firestore)
- **Root Cause:** API endpoint returns `total: <limit>` instead of actual count
  - When requesting `limit=5`, API returns `total: 5`
  - When requesting `limit=20`, API returns `total: 20`
  - Backend query function correctly returns 64, but response is being corrupted
- **Impact:** Users think there are only 20 properties; pagination doesn't appear
- **Evidence:** Screenshots `properties-page-still-showing-20.png`

### 2. **Search Functionality Broken**
- **Test:** Searched for "Ikoyi"
- **Expected:** Should show only Ikoyi properties (3-4 properties)
- **Actual:** Shows "Active Filters: Search: 'Ikoyi'" but displays all 20 properties unchanged
- **Root Cause:** Search doesn't trigger API reload
- **Impact:** Users cannot find specific properties

### 3. **Filter Functionality Broken**
- **Status:** User confirmed "filters don't work"
- **Root Cause:** Not yet investigated
- **Impact:** Users cannot filter by price, bedrooms, property type, etc.

### 4. **Property Data Quality - Unusable**
**Screenshot Evidence:** `property-modal-poor-data-quality.png`

Out of 20 properties displayed:
- **12/20 (60%)** show "Price on Request" (price = 0)
- **15/20 (75%)** tagged as "Limited Info"
- **10/20 (50%)** have generic titles like "Property in Lagos", "Chevron", "Lekki"
- **8/20 (40%)** have no images ("No Image Available")

**Example property detail modal shows:**
```
Title: Property in Lagos
Price: 0
Bedrooms: (empty)
Bathrooms: (empty)
Property Type: (empty)
Location: (empty)
```

Only the listing URL is available. This is **not usable data** for users trying to find properties.

---

## 🟡 HIGH PRIORITY ISSUES

### 5. **No Pagination Controls**
- **Issue:** Pagination component exists but hidden because `totalCount <= itemsPerPage`
- **Root Cause:** Tied to Issue #1 (wrong total count)
- **Impact:** Users cannot browse beyond first 20 properties

### 6. **Scrape History Display Format**
- **Issue:** Shows "234 / 1 sites" which is confusing
- **Expected:** "234 properties from cwlagos" or similar
- **Impact:** User experience

### 7. **View Details Button Non-Functional**
- **Issue:** Button exists in Scrape History but doesn't do anything
- **Impact:** Cannot view scrape run details

### 8. **Scrape History Card Not Scrollable**
- **Issue:** Content overflow without scrolling
- **Impact:** Cannot see all history items

---

## 🟠 MEDIUM PRIORITY ISSUES

### 9. **Scheduled Runs Section**
- **Current:** Shows "No scheduled runs found"
- **Expected:** Should show GitHub Actions scheduled workflows
- **Requires:** GitHub Actions API integration

### 10. **Run Console Section**
- **Current:** Shows "No recent logs"
- **Expected:** Should display active logging from GitHub workflow progress
- **Requires:** Real-time GitHub Actions log streaming

### 11. **Data Explorer Page**
- **Status:** "Not working" per user
- **Investigation:** Not yet tested

---

## Root Cause Analysis

### Why Property Count is Wrong

1. **Backend Query Function (firestore_queries_enterprise.py)** ✅ CORRECT
   ```python
   total_count = len(all_results)  # Returns 64
   results = all_results[offset:offset + limit]
   return {
       'properties': results,  # 20 items
       'total': total_count    # 64
   }
   ```

2. **API Endpoint (api_server.py)** ✅ CORRECT
   ```python
   result = get_properties_by_listing_type('sale', limit=limit, offset=offset)
   return jsonify(result)  # Should return {properties: [...], total: 64}
   ```

3. **API Response** ❌ WRONG
   ```bash
   curl "http://localhost:5000/api/firestore/for-sale?limit=20"
   # Returns: {"properties": [...], "total": 20}  <-- WRONG!
   ```

4. **Direct Function Call** ✅ RETURNS CORRECT VALUE
   ```python
   python -c "from core.firestore_queries_enterprise import get_properties_by_listing_type; print(get_properties_by_listing_type('sale', limit=20)['total'])"
   # Output: 64  <-- CORRECT!
   ```

**Hypothesis:** Python module caching issue OR there's middleware/decorator modifying the response

---

## Why Data Quality is Poor

The cwlagos scraper is extracting category pages instead of property detail pages:

**Bad Property Examples:**
```json
{
  "title": "Chevron",
  "url": "https://cwlagos.com/property-location/chevron/",
  "price": 0,
  "location": {
    "full_address": "Chevron 36 Properties"
  }
}
```

This is a **category listing page**, not a property. The scraper is treating area pages as properties.

**Good Property Example:**
```json
{
  "title": "Maisonette in Ikoyi",
  "price": 35000000,
  "bedrooms": 1,
  "location": {
    "area": "Ikoyi"
  },
  "property_type": "Maisonette"
}
```

**Recommendation:**
- Filter out properties with quality_score < 40%
- Fix cwlagos parser to skip category pages
- Add detail page scraping for cwlagos

---

## Testing Evidence

**Screenshots Captured:**
1. `dashboard-property-count-issue.png` - Dashboard showing 366 total
2. `properties-page-still-showing-20.png` - Properties page showing wrong count
3. `property-modal-poor-data-quality.png` - Unusable property detail

**API Tests:**
```bash
# Test 1: Limit=5 returns total=5 (WRONG)
curl "localhost:5000/api/firestore/for-sale?limit=5" | grep total
# Output: "total":5

# Test 2: Limit=20 returns total=20 (WRONG)
curl "localhost:5000/api/firestore/for-sale?limit=20" | grep total
# Output: "total":20

# Test 3: Direct function call returns 64 (CORRECT)
python -c "..."
# Output: 64
```

---

## Recommended Fix Priority

### Phase 1: Core Functionality (CRITICAL)
1. ✅ Fix property count API response issue
2. ✅ Fix search functionality
3. ✅ Fix filter functionality
4. ✅ Make pagination buttons appear

### Phase 2: Data Quality (HIGH)
5. ⚠️ Improve property data quality (parser fixes)
6. ⚠️ Add quality filter to hide bad listings by default

### Phase 3: Dashboard (MEDIUM)
7. 🔧 Fix Scrape History display format
8. 🔧 Make View Details button functional
9. 🔧 Make Scrape History scrollable
10. 🔧 Integrate GitHub Actions for Scheduled Runs
11. 🔧 Integrate GitHub Actions for Run Console

### Phase 4: Additional Pages (LOW)
12. 🔧 Fix Data Explorer page

---

## Impact Assessment

**User Perspective:**
- ❌ Cannot search properties
- ❌ Cannot filter properties
- ❌ Cannot browse beyond 20 properties
- ❌ 75% of property data is incomplete
- ❌ Cannot monitor scraping operations

**Business Impact:**
- Application appears to have only 20 properties (actually has 366)
- Users will assume the app has very limited inventory
- Data quality issues make properties unsearchable/unbookmarkable
- Monitoring tools don't work for operational visibility

**Conclusion:** The application is technically working at the infrastructure level (API runs, database connected, frontend renders) but is **not functionally useful** for end users in its current state.

---

## Next Steps

1. **Immediate:** Debug why API returns wrong total (module caching? Flask issue?)
2. **Quick Win:** Enable Quality Filter by default to hide bad listings
3. **Short Term:** Fix search/filter API integration
4. **Medium Term:** Improve cwlagos parser to extract real property details
5. **Long Term:** Add GitHub Actions integration for monitoring

---

**Report Generated:** 2025-12-25 10:20 AM
**Tested By:** Claude Code (Playwright Automation)
**Application:** Nigerian Real Estate Scraper v3.3.2
