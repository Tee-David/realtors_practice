# Postman Testing Guide

> **⚠️ DO NOT DELETE THIS FILE!** Essential guide for API testing with Postman.

Complete guide for testing all 68 API endpoints using Postman.

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Import Collection

1. Download: `Nigerian_Real_Estate_API.postman_collection.json` (in project root)
2. Open Postman
3. Click **Import** button (top left)
4. Drag the JSON file or click "Upload Files"
5. Click **Import**

### Step 2: Set Variables

1. Click the **eye icon** (👁️) in top right
2. Add these variables:

| Variable | Value |
|----------|-------|
| `BASE_URL` | `http://localhost:5000` |
| `API_KEY` | `your-api-key-here` |

3. Click **Save**

### Step 3: Test!

1. Start API server: `python api_server.py`
2. In Postman, select any request
3. Click **Send**

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
