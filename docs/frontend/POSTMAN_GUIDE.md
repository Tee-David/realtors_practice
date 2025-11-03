# Postman Testing Guide

Complete guide for testing all 68 API endpoints using Postman with the live Firebase backend or local server.

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Import Collection

1. Download: `Nigerian_Real_Estate_API.postman_collection.json` (in `docs/` folder)
2. Open Postman
3. Click **Import** button (top left)
4. Drag the JSON file or click "Upload Files"
5. Click **Import**

### Step 2: Choose Your Environment

**Option A: Firebase (Recommended) - Already Configured!**
- ✅ The collection is pre-configured with Firebase URL
- ✅ No setup needed - just start testing!
- ✅ BASE_URL: `https://us-central1-realtor-s-practice.cloudfunctions.net/api`

**Option B: Local Server**
1. Start local API server: `python api_server.py`
2. In Postman, click the **eye icon** (👁️) in top right
3. Change `BASE_URL` to `{{LOCAL_URL}}` or `http://localhost:5000`
4. Click **Save**

### Step 3: Test!

1. Select any request from the collection
2. Click **Send**
3. View response in the bottom panel

**Quick Test:** Open "1. Core Operations" → "Health Check" → Click **Send**

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T...",
  "version": "1.0.0"
}
```

---

## 📋 68 Endpoints Included

### 1. Core Operations (5)
- Health Check, Start/Stop Scraping, Status, History

### 2. Site Management (6)
- List, Get, Create, Update, Delete, Toggle Sites

### 3. Data Access (4)
- Get Properties, Search, Natural Language, Advanced Query

### 4. Price Intelligence (4)
- Price History, Drops, Stale Listings, Market Trends

### 5. Saved Searches (5)
- CRUD operations for saved searches

### 6. GitHub Actions (4)
- Trigger, Estimate, Workflow Runs, Artifacts

### 7. Firestore (3)
- Query, Archive, Export

### 8. Email (5)
- Configure, Test, Recipients, Send

---

## 🔐 Authentication

Already configured in collection!

**Header:** `X-API-Key: {{API_KEY}}`

Just set the `API_KEY` variable.

---

## 🧪 Example Tests

### Test 1: Health Check
```
GET {{BASE_URL}}/api/health
```

### Test 2: Search Properties
```http
POST {{BASE_URL}}/api/search/natural
{
  "query": "3 bedroom flat in Lekki under 30 million"
}
```

### Test 3: Get Price Drops
```
GET {{BASE_URL}}/api/price-drops?min_drop_pct=10
```

---

## 🐛 Troubleshooting

**401 Unauthorized?**
- Check API_KEY is set
- Verify `X-API-Key` header exists

**Connection refused?**
- Start server: `python api_server.py`

**No data?**
- Run scraper first: `python main.py`

---

## 📚 More Info

- **Frontend Integration:** `FRONTEND_AUTH_GUIDE.md`
- **All Endpoints:** `FRONTEND_INTEGRATION_GUIDE.md`
- **Testing Guide:** `TESTING_GUIDE.md`

---

**Collection:** `Nigerian_Real_Estate_API.postman_collection.json`
**Total Endpoints:** 68
**Status:** ✅ Complete
