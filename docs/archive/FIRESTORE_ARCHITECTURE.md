# Firestore Architecture Guide

Complete guide to the optimized Firestore data architecture for the Nigerian Real Estate Scraper.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Structure](#data-structure)
3. [Index Configuration](#index-configuration)
4. [Query Patterns](#query-patterns)
5. [API Endpoints](#api-endpoints)
6. [Setup & Deployment](#setup--deployment)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)

---

## Overview

### Design Philosophy

The Firestore architecture is optimized for **cross-site aggregate queries** with:
- **Flat collection structure** - All properties in one `properties` collection
- **Smart composite indexes** - Fast multi-field queries
- **Query-time aggregation** - Calculate summaries on-demand
- **Cached aggregates** - Store expensive calculations for reuse

### Key Features

- Fast cross-site searches (< 100ms)
- Flexible filtering (price, location, type, bedrooms, etc.)
- Pagination support
- Dashboard statistics
- Replaces Excel workbook summary sheets
- Backward compatible with existing API

---

## Data Structure

### Collections

#### 1. `properties` Collection

Primary data store for all property listings.

**Document Structure:**
```javascript
properties/{hash}
{
  // Core fields
  "title": "3 Bedroom Flat in Lekki",
  "price": 45000000,
  "location": "Lekki Phase 1, Lagos",
  "property_type": "Flat",
  "bedrooms": 3,
  "bathrooms": 3,
  "toilets": 3,
  "bq": 0,

  // Additional details
  "estate_name": "Richmond Estate",
  "land_size": "450sqm",
  "description": "Modern 3BR flat with...",
  "promo_tags": ["New Listing", "Hot Deal"],

  // Financial
  "price_per_sqm": 100000,
  "price_per_bedroom": 15000000,
  "initial_deposit": 5000000,
  "payment_plan": "12 months",
  "service_charge": 250000,

  // Legal/timeline
  "title_tag": "Governor's Consent",
  "launch_timeline": "Q1 2025",

  // Contact
  "agent_name": "John Doe Properties",
  "contact_info": "+234-xxx-xxx-xxxx",

  // Media
  "images": ["https://...", "https://..."],
  "listing_url": "https://nigeriapropertycentre.com/...",

  // Location
  "coordinates": {
    "latitude": 6.4474,
    "longitude": 3.5638
  },

  // Metadata
  "source": "npc",
  "site_key": "npc",
  "scrape_timestamp": "2025-11-06T08:00:00",
  "hash": "a1b2c3d4e5f6...",
  "quality_score": 0.85,

  // Firestore timestamps
  "uploaded_at": Timestamp,
  "updated_at": Timestamp
}
```

**Document ID:** Property hash (SHA256 of title+price+location)

#### 2. `site_metadata` Collection

Per-site statistics and metadata.

```javascript
site_metadata/{site_key}
{
  "site_key": "npc",
  "total_properties": 1234,
  "price_range": {
    "min": 2000000,
    "max": 500000000,
    "avg": 35000000
  },
  "last_updated": Timestamp,
  "updated_at": Timestamp
}
```

#### 3. `aggregates` Collection

Cached aggregate statistics for expensive queries.

```javascript
aggregates/dashboard
{
  "stats": {
    "total_properties": 5000,
    "total_sites": 50,
    "price_range": {...},
    "property_type_breakdown": {...},
    "site_breakdown": {...},
    "quality_distribution": {...},
    "newest_listing": {...},
    "cheapest_listing": {...}
  },
  "updated_at": Timestamp
}

aggregates/top_deals
{
  "properties": [...],  // Top 100 cheapest
  "count": 100,
  "updated_at": Timestamp
}

aggregates/newest_listings
{
  "properties": [...],  // Last 50 listings
  "count": 50,
  "days_back": 7,
  "updated_at": Timestamp
}

aggregates/_stale_marker
{
  "dashboard": true,  // Needs refresh
  "top_deals": true,
  "newest_listings": true,
  "last_upload_site": "npc",
  "updated_at": Timestamp
}
```

#### 4. `properties_archive` Collection

Historical property data (price changes, status updates).

```javascript
properties_archive/{archive_id}
{
  "property_hash": "a1b2c3d4...",
  "change_type": "price_update",
  "old_value": 45000000,
  "new_value": 42000000,
  "changed_at": Timestamp
}
```

---

## Index Configuration

### Composite Indexes

Located in `firestore.indexes.json`:

```json
{
  "indexes": [
    // Site + timestamp (newest per site)
    {
      "fields": [
        {"fieldPath": "site_key", "order": "ASCENDING"},
        {"fieldPath": "scrape_timestamp", "order": "DESCENDING"}
      ]
    },

    // Price + quality (best value)
    {
      "fields": [
        {"fieldPath": "price", "order": "ASCENDING"},
        {"fieldPath": "quality_score", "order": "DESCENDING"}
      ]
    },

    // Property type + bedrooms + price (filtered search)
    {
      "fields": [
        {"fieldPath": "property_type", "order": "ASCENDING"},
        {"fieldPath": "bedrooms", "order": "ASCENDING"},
        {"fieldPath": "price", "order": "ASCENDING"}
      ]
    },

    // Location + price (location-based deals)
    {
      "fields": [
        {"fieldPath": "location", "order": "ASCENDING"},
        {"fieldPath": "price", "order": "ASCENDING"}
      ]
    },

    // Quality + price (premium listings)
    {
      "fields": [
        {"fieldPath": "quality_score", "order": "DESCENDING"},
        {"fieldPath": "price", "order": "ASCENDING"}
      ]
    }
  ]
}
```

### Deployment

Deploy indexes to Firebase:

```bash
# Using Firebase CLI
firebase deploy --only firestore:indexes

# Or manually via Firebase Console:
# 1. Go to Firebase Console > Firestore Database > Indexes
# 2. Import firestore.indexes.json
```

---

## Query Patterns

### Common Query Examples

#### 1. Cheapest Properties (Top 100)

```javascript
db.collection('properties')
  .orderBy('price', 'asc')
  .orderBy('quality_score', 'desc')
  .limit(100)
  .get()
```

**Performance:** ~50-100ms
**Index:** `price ASC + quality_score DESC`

#### 2. Newest Listings (Last 7 Days)

```javascript
const cutoff = new Date(Date.now() - 7*24*60*60*1000);

db.collection('properties')
  .where('scrape_timestamp', '>=', cutoff.toISOString())
  .orderBy('scrape_timestamp', 'desc')
  .limit(50)
  .get()
```

**Performance:** ~50-100ms
**Index:** `scrape_timestamp DESC`

#### 3. Cross-Site Search (Filtered)

```javascript
db.collection('properties')
  .where('location', '==', 'Lekki')
  .where('price', '>=', 5000000)
  .where('price', '<=', 50000000)
  .where('bedrooms', '>=', 3)
  .orderBy('price', 'asc')
  .limit(50)
  .get()
```

**Performance:** ~100-200ms
**Index:** `location ASC + price ASC`

#### 4. Site-Specific Properties

```javascript
db.collection('properties')
  .where('site_key', '==', 'npc')
  .orderBy('scrape_timestamp', 'desc')
  .limit(100)
  .get()
```

**Performance:** ~50-100ms
**Index:** `site_key ASC + scrape_timestamp DESC`

#### 5. Premium Properties (4+ Bedrooms)

```javascript
db.collection('properties')
  .where('bedrooms', '>=', 4)
  .orderBy('bedrooms', 'desc')
  .orderBy('price', 'asc')
  .limit(100)
  .get()
```

**Performance:** ~50-100ms
**Index:** `bedrooms ASC + price ASC`

---

## API Endpoints

### New Firestore-Optimized Endpoints

All endpoints are **backward compatible** - existing endpoints remain unchanged.

#### Dashboard & Statistics

```bash
# Get dashboard statistics
GET /api/firestore/dashboard

Response:
{
  "success": true,
  "data": {
    "total_properties": 5000,
    "total_sites": 50,
    "price_range": {"min": 2M, "max": 500M, "avg": 35M},
    "property_type_breakdown": {...},
    "site_breakdown": {...},
    "quality_distribution": {"high": 100, "medium": 200, "low": 50}
  }
}
```

#### Top Deals

```bash
# Get top 100 cheapest properties
GET /api/firestore/top-deals?limit=100&min_quality=0.7

Response:
{
  "success": true,
  "count": 100,
  "data": [...]
}
```

#### Newest Listings

```bash
# Get newest listings (last 7 days)
GET /api/firestore/newest?limit=50&days_back=7&site_key=npc

Response:
{
  "success": true,
  "count": 50,
  "data": [...]
}
```

#### Property Type Queries

```bash
# For sale properties
GET /api/firestore/for-sale?limit=100&price_max=100000000

# For rent properties
GET /api/firestore/for-rent?limit=100&price_max=5000000

# Land only
GET /api/firestore/land?limit=100&price_max=50000000

# Premium (4+ bedrooms)
GET /api/firestore/premium?min_bedrooms=4&limit=100
```

#### Advanced Search

```bash
POST /api/firestore/search

Body:
{
  "filters": {
    "location": "Lekki",
    "price_min": 5000000,
    "price_max": 50000000,
    "bedrooms_min": 3,
    "property_type": "Flat",
    "quality_score_min": 0.7
  },
  "sort_by": "price",
  "sort_desc": false,
  "limit": 50,
  "offset": 0
}

Response:
{
  "success": true,
  "results": [...],
  "total": 45,
  "has_more": false
}
```

#### Site-Specific Queries

```bash
# Get all properties from a site
GET /api/firestore/site/npc?limit=100&offset=0&sort_by=price

# Get site statistics
GET /api/firestore/site-stats/npc

Response:
{
  "success": true,
  "data": {
    "site_key": "npc",
    "total_properties": 1234,
    "price_range": {...}
  }
}
```

#### Individual Property

```bash
# Get property by hash
GET /api/firestore/property/{hash}

Response:
{
  "success": true,
  "data": {
    "id": "a1b2c3d4...",
    "title": "...",
    "price": 45000000,
    ...
  }
}
```

---

## Setup & Deployment

### 1. Firebase Project Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firestore
firebase init firestore
# Select your project
# Use default firestore.rules and firestore.indexes.json
```

### 2. Deploy Indexes

```bash
# Deploy composite indexes
firebase deploy --only firestore:indexes

# This will create all composite indexes defined in firestore.indexes.json
# Index creation takes 5-15 minutes
```

### 3. Deploy Security Rules

```bash
# Deploy Firestore security rules
firebase deploy --only firestore:rules

# This will apply the rules from firestore.rules
```

### 4. Environment Configuration

Update `.env`:

```bash
# Firebase credentials
FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json

# Enable Firestore uploads
FIRESTORE_ENABLED=1

# Auto-update aggregates (optional, recommended: 0)
FIRESTORE_AUTO_AGGREGATE=0

# Collections
FIRESTORE_COLLECTION=properties
FIRESTORE_ARCHIVE_COLLECTION=properties_archive
```

### 5. Run Initial Scrape

```bash
# Scrape and upload to Firestore
python main.py

# Update aggregates after scrape
python scripts/update_firestore_aggregates.py
```

### 6. Start API Server

```bash
# Start Flask API with Firestore endpoints
python api_server.py

# Test new endpoints
curl http://localhost:5000/api/firestore/dashboard
curl http://localhost:5000/api/firestore/top-deals?limit=10
```

---

## Performance Optimization

### Query Performance Tips

1. **Use Composite Indexes**
   - Always query indexed fields
   - Check index usage in Firebase Console

2. **Limit Results**
   - Use `.limit(N)` on all queries
   - Default: 50-100 results per query

3. **Pagination**
   - Use `offset` for pagination
   - Better: Use cursor-based pagination with `.startAfter()`

4. **Cache Aggregates**
   - Use `aggregates` collection for expensive queries
   - Update aggregates after scrapes, not on every query

5. **Monitor Costs**
   - 1 read = 1 document fetch
   - Aggregate queries can be expensive
   - Cache results when possible

### Cost Estimates

**Free Tier:**
- 50K reads/day
- 20K writes/day
- 1GB storage

**Typical Usage:**
- 10K properties = ~10MB storage
- 100 API requests/day = ~500 reads/day
- Well within free tier

**Scaling:**
- 1M properties = ~1GB storage
- 10K API requests/day = ~50K reads/day
- Cost: ~$0.06/day (~$2/month)

---

## Best Practices

### 1. Querying

```javascript
// GOOD: Use indexed fields
db.collection('properties')
  .where('site_key', '==', 'npc')
  .orderBy('price', 'asc')
  .limit(50)

// BAD: Full collection scan
db.collection('properties')
  .get()
  .then(docs => docs.filter(d => d.data().title.includes('luxury')))
```

### 2. Aggregates

```javascript
// GOOD: Use cached aggregates
const cached = await db.collection('aggregates').doc('dashboard').get();
if (cached.exists && isRecent(cached.data().updated_at)) {
  return cached.data().stats;
}

// BAD: Calculate on every request
const allDocs = await db.collection('properties').get();
// Calculate stats from allDocs...
```

### 3. Pagination

```javascript
// GOOD: Cursor-based pagination
const first = await db.collection('properties')
  .orderBy('price')
  .limit(25)
  .get();

const last = first.docs[first.docs.length - 1];
const next = await db.collection('properties')
  .orderBy('price')
  .startAfter(last)
  .limit(25)
  .get();

// OK: Offset pagination (simpler, less efficient)
const page2 = await db.collection('properties')
  .orderBy('price')
  .offset(25)
  .limit(25)
  .get();
```

### 4. Error Handling

```javascript
// GOOD: Handle errors gracefully
try {
  const result = await db.collection('properties')
    .where('price', '>=', minPrice)
    .get();

  if (result.empty) {
    return { results: [], total: 0 };
  }

  return { results: result.docs.map(d => d.data()) };
} catch (error) {
  logger.error('Query failed:', error);
  return { error: 'Database query failed', results: [] };
}
```

### 5. Security

```javascript
// firestore.rules

// GOOD: Validate data on write
match /properties/{id} {
  allow read: if true;
  allow write: if request.auth != null
    && request.resource.data.price > 0
    && request.resource.data.title.size() > 0;
}

// BAD: Allow unrestricted writes
match /properties/{id} {
  allow read, write: if true;
}
```

---

## Maintenance

### Regular Tasks

1. **Update Aggregates (After Each Scrape)**
   ```bash
   python scripts/update_firestore_aggregates.py
   ```

2. **Monitor Index Usage (Weekly)**
   - Check Firebase Console > Firestore > Indexes
   - Look for "Suggested Indexes"
   - Add any recommended indexes

3. **Review Costs (Monthly)**
   - Firebase Console > Usage
   - Check read/write counts
   - Optimize expensive queries

4. **Backup Data (Monthly)**
   - Firebase automatically backs up daily
   - Export to Cloud Storage for long-term archival:
   ```bash
   gcloud firestore export gs://your-bucket/backups/$(date +%Y%m%d)
   ```

---

## Troubleshooting

### Slow Queries

**Problem:** Queries taking > 1 second

**Solutions:**
1. Check if composite index exists
2. Add missing indexes via Firebase Console
3. Reduce result limit
4. Use cached aggregates

### High Costs

**Problem:** Exceeding free tier

**Solutions:**
1. Reduce query frequency
2. Increase cache TTL
3. Use pagination (smaller page sizes)
4. Batch reads instead of individual fetches

### Missing Data

**Problem:** Properties not appearing in Firestore

**Solutions:**
1. Check `FIRESTORE_ENABLED=1` in `.env`
2. Verify Firebase credentials
3. Check upload logs for errors
4. Verify security rules allow writes

---

## Migration Guide

### From Excel Workbook to Firestore

If migrating from Excel-only to Firestore:

1. **Run Initial Upload**
   ```bash
   # Enable Firestore
   export FIRESTORE_ENABLED=1

   # Run scraper (will upload existing + new data)
   python main.py
   ```

2. **Verify Data**
   ```bash
   # Check Firestore has data
   curl http://localhost:5000/api/firestore/dashboard
   ```

3. **Update Aggregates**
   ```bash
   python scripts/update_firestore_aggregates.py
   ```

4. **Switch Frontend**
   - Update API calls from `/api/data/*` to `/api/firestore/*`
   - Test all queries
   - Monitor performance

5. **Disable Excel (Optional)**
   ```bash
   # Stop generating master workbook
   export MASTER_WORKBOOK_ENABLED=0
   ```

---

## Support

For questions or issues:
- Check Firebase Console > Firestore > Logs
- Review `logs/scraper.log`
- See `docs/FRONTEND_INTEGRATION_GUIDE.md` for API details

---

**Last Updated:** 2025-11-06
**Version:** 1.0
