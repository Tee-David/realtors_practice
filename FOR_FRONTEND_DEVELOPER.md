# For Frontend Developer - Start Here! 🎉

## Welcome!

Your backend API is **already deployed and ready to use**. This document will get you started in 5 minutes.

---

## 🚀 Your Live API

```
Base URL: https://us-central1-realtor-s-practice.cloudfunctions.net/api
Status: ✅ Live and Ready
Endpoints: 68 total
Authentication: None required (for now)
```

---

## ⚡ Quick Test (30 Seconds)

Open your browser console and paste this:

```javascript
// Test 1: Health Check
fetch('https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/health')
  .then(res => res.json())
  .then(data => console.log('API Health:', data));

// Test 2: Get All Sites
fetch('https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/sites')
  .then(res => res.json())
  .then(data => console.log('Total Sites:', data.total, 'Sites:', data.sites));
```

If you see data returned, **you're ready to go!** ✅

---

## 📚 Essential Documentation

Start with these files (in order):

### 1. **Quick Start** (5 minutes)
📄 [docs/FRONTEND_QUICKSTART.md](docs/FRONTEND_QUICKSTART.md)
- React/Next.js examples
- Common use cases
- TypeScript support
- All you need to get started

### 2. **Complete API Reference** (when you need details)
📄 [docs/FRONTEND_INTEGRATION_GUIDE.md](docs/FRONTEND_INTEGRATION_GUIDE.md)
- All 68 endpoints documented
- Request/response examples
- Error handling
- Advanced features

### 3. **Postman Testing** (optional but helpful)
📄 [docs/POSTMAN_GUIDE.md](docs/POSTMAN_GUIDE.md)
📦 [docs/Nigerian_Real_Estate_API.postman_collection.json](docs/Nigerian_Real_Estate_API.postman_collection.json)
- Import collection to Postman
- Test all endpoints
- See examples

### 4. **Firebase Deployment Info** (if you're curious)
📄 [FIREBASE_DEPLOYMENT_SUCCESS.md](FIREBASE_DEPLOYMENT_SUCCESS.md)
- Deployment details
- Cost information
- Monitoring and logs

---

## 🎯 Most Common Endpoints

### 1. Get All Sites
```javascript
GET /api/sites
Returns: { total: 51, enabled: 1, disabled: 50, sites: [...] }
```

### 2. Search Properties (Natural Language)
```javascript
POST /api/search/natural
Body: { "query": "3 bedroom flat in Lekki under 30 million" }
Returns: { results: [...], count: 25, query: "..." }
```

### 3. Get Properties
```javascript
GET /api/properties?limit=50&offset=0
Returns: { properties: [...], total: 1500, page: 1 }
```

### 4. Start Scraping
```javascript
POST /api/scrape/start
Body: { "sites": ["npc", "propertypro"], "max_pages": 10 }
Returns: { status: "started", sites: [...] }
```

### 5. Check Scrape Status
```javascript
GET /api/scrape/status
Returns: { running: true, progress: 50, current_site: "npc" }
```

---

## 💻 React/Next.js Integration Example

```javascript
// lib/api.js
const API_BASE_URL = 'https://us-central1-realtor-s-practice.cloudfunctions.net/api';

export async function fetchSites() {
  const response = await fetch(`${API_BASE_URL}/api/sites`);
  if (!response.ok) throw new Error('Failed to fetch sites');
  return response.json();
}

export async function searchProperties(query) {
  const response = await fetch(`${API_BASE_URL}/api/search/natural`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!response.ok) throw new Error('Search failed');
  return response.json();
}

// Usage in component
import { useState, useEffect } from 'react';

function Properties() {
  const [properties, setProperties] = useState([]);

  useEffect(() => {
    fetch('https://us-central1-realtor-s-practice.cloudfunctions.net/api/api/properties?limit=50')
      .then(res => res.json())
      .then(data => setProperties(data.properties));
  }, []);

  return (
    <div>
      {properties.map(property => (
        <div key={property.listing_url}>
          <h3>{property.title}</h3>
          <p>{property.price} - {property.location}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 Environment Variables

Create `.env.local` in your project:

```env
NEXT_PUBLIC_API_URL=https://us-central1-realtor-s-practice.cloudfunctions.net/api
```

Then use it:

```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
fetch(`${API_URL}/api/sites`)...
```

---

## 📋 All 68 Endpoints (8 Categories)

1. **Scraping Management** (5 endpoints)
   - Health check, start/stop scraping, status, history

2. **Site Configuration** (6 endpoints)
   - List, add, update, delete, toggle sites

3. **Data Access** (4 endpoints)
   - Get properties, search, natural language search, advanced query

4. **Price Intelligence** (4 endpoints)
   - Price history, price drops, stale listings, market trends

5. **Saved Searches** (5 endpoints)
   - CRUD operations for saved searches

6. **GitHub Actions** (4 endpoints)
   - Trigger workflows, estimate time, view runs, get artifacts

7. **Firestore Integration** (3 endpoints)
   - Query, archive, export from Firestore

8. **Email Notifications** (5 endpoints)
   - Configure SMTP, test connection, manage recipients

9. **Additional** (32 endpoints)
   - Health monitoring, duplicates, quality scoring, logs, stats, etc.

**See [docs/FRONTEND_INTEGRATION_GUIDE.md](docs/FRONTEND_INTEGRATION_GUIDE.md) for complete details.**

---

## 🎨 Property Data Schema

Every property has these fields:

```javascript
{
  title: "3 Bedroom Flat in Lekki",
  price: "₦30,000,000",
  location: "Lekki Phase 1, Lagos",
  property_type: "Flat / Apartment",
  bedrooms: 3,
  bathrooms: 2,
  listing_url: "https://...",
  images: ["url1", "url2", ...],
  source: "Nigeria Property Centre",
  scrape_timestamp: "2025-10-27T10:00:00",
  // ... and 20+ more optional fields
}
```

---

## 🐛 Troubleshooting

### API Not Responding?
1. Check your internet connection
2. Verify the URL is correct
3. View Firebase logs: https://console.firebase.google.com/project/realtor-s-practice/logs

### CORS Issues?
- The API has CORS enabled for all origins
- If you still face issues, check browser console for specific errors

### Need More Data?
- API returns 50 items by default
- Use pagination: `?limit=100&offset=0`

---

## 🆘 Need Help?

1. **Start here**: [docs/FRONTEND_QUICKSTART.md](docs/FRONTEND_QUICKSTART.md)
2. **Full API docs**: [docs/FRONTEND_INTEGRATION_GUIDE.md](docs/FRONTEND_INTEGRATION_GUIDE.md)
3. **Test with Postman**: Import [docs/Nigerian_Real_Estate_API.postman_collection.json](docs/Nigerian_Real_Estate_API.postman_collection.json)
4. **View logs**: https://console.firebase.google.com/project/realtor-s-practice/functions

---

## ✅ Checklist for Getting Started

- [ ] Test API in browser console (see "Quick Test" above)
- [ ] Read [docs/FRONTEND_QUICKSTART.md](docs/FRONTEND_QUICKSTART.md)
- [ ] Import Postman collection (optional but helpful)
- [ ] Set up environment variables
- [ ] Create your first API call
- [ ] Build your first component
- [ ] Review complete API docs when needed

---

## 🎉 You're Ready!

The backend is deployed, tested, and ready for integration. All documentation is updated and complete.

**Your API Base URL**:
```
https://us-central1-realtor-s-practice.cloudfunctions.net/api
```

**Next Step**: Open [docs/FRONTEND_QUICKSTART.md](docs/FRONTEND_QUICKSTART.md) and start building! 🚀

---

**Questions?** All documentation is in the `docs/` folder. Start with FRONTEND_QUICKSTART.md!

Good luck! 💪
