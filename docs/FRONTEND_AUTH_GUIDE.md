# Frontend Authentication Integration Guide

**For Frontend Developers**

Complete guide to integrating with the Nigerian Real Estate Scraper API with authentication.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your API Key

Contact the backend team to get your API key. They will provide:
- API Key (string)
- Base URL (e.g., `https://api.yourdomain.com` or `http://localhost:5000`)

### Step 2: Test the API

```bash
# Test with cURL
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00"
}
```

### Step 3: Use in Your Frontend

```javascript
// config.js
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  apiKey: process.env.REACT_APP_API_KEY
};
```

```javascript
// api.js
import { API_CONFIG } from './config';

export async function fetchProperties() {
  const response = await fetch(`${API_CONFIG.baseURL}/api/data/master`, {
    headers: {
      'X-API-Key': API_CONFIG.apiKey,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

---

## 🔐 Authentication Methods

The API supports **two authentication methods**. Choose the one that fits your needs:

### Method 1: API Key (Simpler, Recommended for Most Cases)

**Use this if:**
- You're building a client application
- You don't need user-specific permissions
- You want simple, straightforward authentication

**How it works:**
- Include `X-API-Key` header in every request
- Backend validates the key
- All requests with valid key are allowed

### Method 2: JWT Tokens (For User-Based Apps)

**Use this if:**
- You have user accounts
- Different users need different permissions
- You need session management

**How it works:**
1. User logs in → receive JWT token
2. Include token in `Authorization: Bearer <token>` header
3. Token expires after 24 hours (configurable)
4. Refresh token when needed

---

## 📦 Complete React/TypeScript Integration

### 1. Installation

```bash
npm install axios
# or
yarn add axios
```

### 2. API Client Setup

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const API_KEY = process.env.REACT_APP_API_KEY;

// Create axios instance
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Authentication failed. Check your API key.');
    }
    return Promise.reject(error);
  }
);
```

### 3. TypeScript Types

```typescript
// src/types/property.ts
export interface Property {
  title: string;
  price: string;
  location: string;
  property_type: string;
  bedrooms: number;
  bathrooms: number;
  land_size?: string;
  description: string;
  agent_name?: string;
  images: string[];
  listing_url: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  source: string;
  scrape_timestamp: string;
  hash: string;
}

export interface ApiResponse<T> {
  data?: T;
  properties?: T[];
  total?: number;
  page?: number;
  limit?: number;
  error?: string;
  message?: string;
}
```

### 4. API Service Functions

```typescript
// src/api/properties.ts
import { apiClient } from './client';
import { Property, ApiResponse } from '../types/property';

export const propertyAPI = {
  // Get all properties (with pagination)
  async getAll(page = 1, limit = 20): Promise<ApiResponse<Property>> {
    const response = await apiClient.get('/data/master', {
      params: { page, limit }
    });
    return response.data;
  },

  // Search properties
  async search(query: string): Promise<ApiResponse<Property>> {
    const response = await apiClient.get('/data/search', {
      params: { q: query, limit: 50 }
    });
    return response.data;
  },

  // Natural language search
  async naturalSearch(query: string): Promise<ApiResponse<Property>> {
    const response = await apiClient.post('/search/natural', {
      query
    });
    return response.data;
  },

  // Advanced query
  async advancedQuery(filters: any): Promise<ApiResponse<Property>> {
    const response = await apiClient.post('/query', {
      filters,
      limit: 100
    });
    return response.data;
  },

  // Get property by ID
  async getById(id: string): Promise<Property> {
    const response = await apiClient.get(`/data/property/${id}`);
    return response.data;
  },

  // Get price history
  async getPriceHistory(propertyId: string) {
    const response = await apiClient.get(`/price-history/${propertyId}`);
    return response.data;
  },

  // Get price drops
  async getPriceDrops(minDropPct = 10, days = 30) {
    const response = await apiClient.get('/price-drops', {
      params: { min_drop_pct: minDropPct, days }
    });
    return response.data;
  },

  // Get market trends
  async getMarketTrends() {
    const response = await apiClient.get('/market-trends');
    return response.data;
  }
};
```

### 5. React Hooks (Custom Hooks for Easy Use)

```typescript
// src/hooks/useProperties.ts
import { useState, useEffect } from 'react';
import { propertyAPI } from '../api/properties';
import { Property } from '../types/property';

export function useProperties(page = 1, limit = 20) {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function fetchProperties() {
      try {
        setLoading(true);
        const response = await propertyAPI.getAll(page, limit);
        setProperties(response.properties || []);
        setTotal(response.total || 0);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch properties');
      } finally {
        setLoading(false);
      }
    }

    fetchProperties();
  }, [page, limit]);

  return { properties, loading, error, total };
}

export function usePropertySearch(query: string) {
  const [results, setResults] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query || query.length < 3) {
      setResults([]);
      return;
    }

    async function search() {
      try {
        setLoading(true);
        const response = await propertyAPI.naturalSearch(query);
        setResults(response.properties || []);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    // Debounce search
    const timeout = setTimeout(search, 500);
    return () => clearTimeout(timeout);
  }, [query]);

  return { results, loading, error };
}
```

### 6. React Component Example

```typescript
// src/components/PropertyList.tsx
import React from 'react';
import { useProperties } from '../hooks/useProperties';

export function PropertyList() {
  const { properties, loading, error, total } = useProperties(1, 20);

  if (loading) {
    return <div>Loading properties...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h2>Properties ({total} total)</h2>
      <div className="grid">
        {properties.map((property) => (
          <div key={property.hash} className="property-card">
            <img src={property.images[0]} alt={property.title} />
            <h3>{property.title}</h3>
            <p>{property.location}</p>
            <p><strong>{property.price}</strong></p>
            <p>{property.bedrooms} beds • {property.bathrooms} baths</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔍 Advanced Features

### Saved Searches

```typescript
// src/api/savedSearches.ts
export const savedSearchAPI = {
  // List all saved searches
  async list() {
    const response = await apiClient.get('/searches');
    return response.data;
  },

  // Create saved search
  async create(name: string, criteria: any) {
    const response = await apiClient.post('/searches', {
      name,
      criteria
    });
    return response.data;
  },

  // Get search results
  async getResults(searchId: string) {
    const response = await apiClient.get(`/searches/${searchId}`);
    return response.data;
  },

  // Delete search
  async delete(searchId: string) {
    await apiClient.delete(`/searches/${searchId}`);
  }
};
```

### Price Alerts

```typescript
// src/api/alerts.ts
export const alertAPI = {
  // Get price drops
  async getPriceDrops(minDropPct = 10) {
    const response = await apiClient.get('/price-drops', {
      params: { min_drop_pct: minDropPct }
    });
    return response.data;
  },

  // Subscribe to email notifications
  async subscribe(email: string, events: string[]) {
    const response = await apiClient.post('/notifications/subscribe', {
      email,
      events
    });
    return response.data;
  }
};
```

---

## 🎨 Vue.js Integration

```typescript
// src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL + '/api',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY
  }
});

// src/composables/useProperties.ts
import { ref, watchEffect } from 'vue';
import { apiClient } from '../api/client';

export function useProperties(page: Ref<number> = ref(1)) {
  const properties = ref([]);
  const loading = ref(false);
  const error = ref(null);

  watchEffect(async () => {
    try {
      loading.value = true;
      const response = await apiClient.get('/data/master', {
        params: { page: page.value, limit: 20 }
      });
      properties.value = response.data.properties;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  });

  return { properties, loading, error };
}
```

---

## 📱 Angular Integration

```typescript
// src/app/services/property.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PropertyService {
  private apiUrl = environment.apiUrl + '/api';
  private headers = new HttpHeaders({
    'X-API-Key': environment.apiKey
  });

  constructor(private http: HttpClient) {}

  getProperties(page = 1, limit = 20): Observable<any> {
    return this.http.get(`${this.apiUrl}/data/master`, {
      params: { page, limit },
      headers: this.headers
    });
  }

  searchProperties(query: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/search/natural`,
      { query },
      { headers: this.headers }
    );
  }
}
```

---

## 🛡️ Security Best Practices for Frontend

### 1. Store API Key Securely

**✅ DO:**
```javascript
// .env.local (NOT committed to git)
REACT_APP_API_KEY=your-api-key-here
REACT_APP_API_URL=https://api.yourdomain.com
```

**❌ DON'T:**
```javascript
// NEVER hardcode in source code
const API_KEY = "sk-1234567890abcdef"; // BAD!
```

### 2. Add .gitignore Rules

```
# .gitignore
.env
.env.local
.env.*.local
```

### 3. Handle Errors Gracefully

```typescript
async function fetchData() {
  try {
    const response = await propertyAPI.getAll();
    return response.properties;
  } catch (error) {
    if (error.response?.status === 401) {
      // API key invalid - show error to user
      showNotification('Authentication failed. Please contact support.');
    } else if (error.response?.status === 429) {
      // Rate limit exceeded
      showNotification('Too many requests. Please try again later.');
    } else {
      // Generic error
      showNotification('Failed to load properties. Please try again.');
    }
    console.error('API Error:', error);
    return [];
  }
}
```

### 4. Implement Request Retry

```typescript
import axios from 'axios';
import axiosRetry from 'axios-retry';

// Retry failed requests
axiosRetry(apiClient, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return error.response?.status >= 500;
  }
});
```

---

## 📊 Complete API Reference (Frontend Friendly)

### Properties

| Method | Endpoint | Purpose | Example |
|--------|----------|---------|---------|
| GET | `/api/data/master` | Get all properties | `propertyAPI.getAll(1, 20)` |
| GET | `/api/data/search` | Search properties | `propertyAPI.search('lekki')` |
| POST | `/api/search/natural` | Natural language search | `propertyAPI.naturalSearch('3BR flat under 30M')` |
| POST | `/api/query` | Advanced filtering | `propertyAPI.advancedQuery(filters)` |
| GET | `/api/price-history/:id` | Price history | `propertyAPI.getPriceHistory(id)` |
| GET | `/api/price-drops` | Recent price drops | `propertyAPI.getPriceDrops()` |
| GET | `/api/market-trends` | Market trends | `propertyAPI.getMarketTrends()` |

### Searches

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/searches` | List saved searches |
| POST | `/api/searches` | Create saved search |
| GET | `/api/searches/:id` | Get search results |
| PUT | `/api/searches/:id` | Update search |
| DELETE | `/api/searches/:id` | Delete search |

### Alerts & Notifications

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/notifications/subscribe` | Subscribe to alerts |
| GET | `/api/price-drops` | Get price drop alerts |

---

## 🚨 Troubleshooting

### Error: "API key required"

**Problem:** Missing or invalid API key

**Solution:**
```javascript
// Check your .env file
REACT_APP_API_KEY=your-api-key-here

// Verify it's being used
console.log(process.env.REACT_APP_API_KEY); // Should print your key
```

### Error: "CORS policy blocked"

**Problem:** Backend CORS not configured for your domain

**Solution:** Contact backend team to add your domain to `ALLOWED_ORIGINS`

### Error: 429 Too Many Requests

**Problem:** Rate limit exceeded

**Solution:** Implement request throttling or caching
```typescript
// Cache API responses
const cache = new Map();

async function fetchWithCache(key: string, fetcher: () => Promise<any>) {
  if (cache.has(key)) {
    return cache.get(key);
  }

  const data = await fetcher();
  cache.set(key, data);

  // Expire after 5 minutes
  setTimeout(() => cache.delete(key), 5 * 60 * 1000);

  return data;
}
```

---

## 📞 Support

**Need Help?**
- Check the [API Documentation](FRONTEND_INTEGRATION_GUIDE.md)
- Review [Testing Guide](TESTING_GUIDE.md)
- Contact backend team with:
  - Your API key
  - Error message
  - Request/response details

---

## ✅ Checklist for Frontend Integration

- [ ] Get API key from backend team
- [ ] Add API key to `.env.local`
- [ ] Add `.env.local` to `.gitignore`
- [ ] Install axios or fetch library
- [ ] Create API client with headers
- [ ] Add error handling
- [ ] Test basic endpoints (health, properties)
- [ ] Implement property listing
- [ ] Implement search functionality
- [ ] Add loading states
- [ ] Add error messages
- [ ] Test rate limiting
- [ ] Deploy to production

---

**Last Updated:** 2025-10-22
**API Version:** 2.2
**Status:** ✅ Production Ready
