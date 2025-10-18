# Frontend Integration Guide

Complete guide for integrating Next.js frontend with the Real Estate Scraper Backend.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [API Reference](#api-reference)
5. [Next.js Integration Examples](#nextjs-integration-examples)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Real Estate Scraper provides a REST API that allows your Next.js frontend to:

- **Manage Scraping Runs**: Start, stop, and monitor scraping operations
- **Configure Sites**: Add, update, delete, and toggle site configurations
- **View Logs**: Access scraper logs and error messages
- **Query Data**: Search and retrieve scraped property listings
- **Display Statistics**: Show overview stats, site performance, and trends

### Technology Stack

**Backend:**
- Python 3.8+
- Flask (REST API)
- Pandas (Data processing)
- PyYAML (Configuration)

**Frontend:**
- Next.js (React framework)
- TypeScript (recommended)
- Axios or Fetch API (HTTP client)

---

## Architecture

### System Overview

```
┌─────────────────┐         HTTP/REST API          ┌─────────────────┐
│                 │ ◄────────────────────────────► │                 │
│  Next.js        │         (Port 5000)            │  Flask API      │
│  Frontend       │                                │  Server         │
│                 │                                │                 │
└─────────────────┘                                └────────┬────────┘
                                                            │
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  Python         │
                                                   │  Scraper        │
                                                   │  (main.py)      │
                                                   └────────┬────────┘
                                                            │
                                                            ▼
                                              ┌─────────────────────────┐
                                              │  Data Storage           │
                                              │  - config.yaml          │
                                              │  - exports/sites/       │
                                              │  - exports/cleaned/     │
                                              │  - logs/                │
                                              └─────────────────────────┘
```

### API Endpoints Overview

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| **Health** | `/api/health` | API health check |
| **Scraping** | `/api/scrape/*` | Manage scraping operations |
| **Sites** | `/api/sites/*` | Configure and manage sites |
| **Logs** | `/api/logs/*` | Access logs and errors |
| **Data** | `/api/data/*` | Query scraped data |
| **Stats** | `/api/stats/*` | View statistics and trends |

---

## Setup Instructions

### Backend Setup

#### 1. Install Dependencies

```bash
cd path/to/realtors_practice
pip install -r requirements.txt
```

**New dependencies added for API:**
- `flask` - Web framework
- `flask-cors` - CORS support for frontend
- `pandas` - Data manipulation

#### 2. Start API Server

```bash
# Default port 5000
python api_server.py

# Custom port
API_PORT=8000 python api_server.py

# Debug mode
API_DEBUG=true python api_server.py
```

The API server will start on `http://localhost:5000` by default.

#### 3. Verify API is Running

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T10:30:00",
  "version": "1.0.0"
}
```

### Frontend Setup

#### 1. Install HTTP Client

```bash
npm install axios
# or
npm install swr  # For data fetching with caching
```

#### 2. Create API Client

Create `lib/api.ts` in your Next.js project:

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

#### 3. Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## API Reference

### Health Check

#### `GET /api/health`

Check if API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T10:30:00",
  "version": "1.0.0"
}
```

---

### Scraping Management

#### `POST /api/scrape/start`

Start a scraping run.

**Request Body:**
```json
{
  "sites": ["npc", "propertypro"],  // Optional: specific sites, empty = all enabled
  "max_pages": 20,                   // Optional: override max pages
  "geocoding": true                  // Optional: enable/disable geocoding
}
```

**Response:**
```json
{
  "success": true,
  "run_id": "20251013_103000",
  "message": "Scraping started successfully",
  "current_run": {
    "run_id": "20251013_103000",
    "started_at": "2025-10-13T10:30:00",
    "sites": ["npc", "propertypro"],
    "max_pages": 20,
    "geocoding": true,
    "pid": 12345
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Scraper is already running"
}
```

---

#### `GET /api/scrape/status`

Get current scraping status.

**Response:**
```json
{
  "is_running": true,
  "current_run": {
    "run_id": "20251013_103000",
    "started_at": "2025-10-13T10:30:00",
    "sites": ["npc", "propertypro"],
    "pid": 12345
  },
  "last_run": {
    "run_id": "20251013_093000",
    "started_at": "2025-10-13T09:30:00",
    "completed_at": "2025-10-13T10:15:00",
    "return_code": 0,
    "success": true
  },
  "site_metadata": {
    "npc": {
      "last_scrape": "2025-10-13T10:15:00",
      "last_successful_scrape": "2025-10-13T10:15:00",
      "last_count": 750,
      "total_scrapes": 15
    }
  }
}
```

---

#### `POST /api/scrape/stop`

Stop current scraping run.

**Response:**
```json
{
  "success": true,
  "message": "Scraper stopped successfully"
}
```

---

#### `GET /api/scrape/history`

Get scraping history.

**Query Parameters:**
- `limit` (optional): Number of records (default: 20)

**Response:**
```json
{
  "total": 15,
  "limit": 20,
  "history": [
    {
      "run_id": "20251013_093000",
      "started_at": "2025-10-13T09:30:00",
      "completed_at": "2025-10-13T10:15:00",
      "success": true
    }
  ]
}
```

---

### Site Configuration

#### `GET /api/sites`

List all sites with configurations.

**Response:**
```json
{
  "total": 50,
  "enabled": 5,
  "disabled": 45,
  "sites": [
    {
      "site_key": "npc",
      "name": "Nigeria Property Centre",
      "url": "https://nigeriapropertycentre.com/",
      "enabled": true,
      "parser": "specials"
    }
  ]
}
```

---

#### `GET /api/sites/<site_key>`

Get configuration for specific site.

**Response:**
```json
{
  "site_key": "npc",
  "name": "Nigeria Property Centre",
  "url": "https://nigeriapropertycentre.com/",
  "enabled": true,
  "parser": "specials",
  "selectors": {
    "card": "li.property-list",
    "title": "h2",
    "price": ".price",
    "location": ".location"
  },
  "pagination": {
    "next_selectors": ["a[rel='next']"],
    "page_param": "page"
  }
}
```

**Error Response (404):**
```json
{
  "error": "Site not found"
}
```

---

#### `POST /api/sites`

Add new site.

**Request Body:**
```json
{
  "site_key": "newsite",
  "name": "New Site",
  "url": "https://newsite.com",
  "enabled": true,
  "parser": "specials",
  "selectors": {
    "card": ".property-card",
    "title": ".title",
    "price": ".price",
    "location": ".location"
  }
}
```

**Required Fields:**
- `site_key` - Unique identifier (lowercase, no spaces)
- `name` - Display name
- `url` - Site URL

**Optional Fields:**
- `enabled` - Enable/disable site (default: false)
- `parser` - Parser type: specials, generic, custom (default: specials)
- `selectors` - CSS selectors for scraping
- `pagination` - Pagination configuration
- `lagos_paths` - Lagos-specific URL paths
- `overrides` - Per-site setting overrides

**Response:**
```json
{
  "success": true,
  "site_key": "newsite",
  "message": "Site newsite added successfully"
}
```

**Error Response (400):**
```json
{
  "error": "site_key is required"
}
```

---

#### `PUT /api/sites/<site_key>`

Update site configuration.

**Request Body:**
```json
{
  "name": "Updated Name",
  "url": "https://updated-url.com",
  "enabled": false
}
```

**Response:**
```json
{
  "success": true,
  "site_key": "newsite",
  "message": "Site newsite updated successfully"
}
```

---

#### `DELETE /api/sites/<site_key>`

Delete site.

**Response:**
```json
{
  "success": true,
  "site_key": "newsite",
  "message": "Site newsite deleted successfully"
}
```

---

#### `PATCH /api/sites/<site_key>/toggle`

Toggle site enabled/disabled.

**Response:**
```json
{
  "success": true,
  "site_key": "npc",
  "enabled": false,
  "message": "Site npc disabled"
}
```

---

### Logs & Errors

#### `GET /api/logs`

Get recent logs.

**Query Parameters:**
- `limit` (optional): Number of lines (default: 100)
- `level` (optional): Filter by level (INFO, WARNING, ERROR)

**Response:**
```json
{
  "total": 100,
  "filter": {"level": "ERROR"},
  "logs": [
    {
      "timestamp": "2025-10-13T10:30:00",
      "level": "ERROR",
      "message": "Failed to scrape site xyz: Connection timeout"
    }
  ]
}
```

---

#### `GET /api/logs/errors`

Get error logs only.

**Query Parameters:**
- `limit` (optional): Number of lines (default: 50)

**Response:** Same as `/api/logs` with `level=ERROR`

---

#### `GET /api/logs/site/<site_key>`

Get site-specific logs.

**Query Parameters:**
- `limit` (optional): Number of lines (default: 100)

**Response:**
```json
{
  "site_key": "npc",
  "total": 25,
  "logs": [
    {
      "timestamp": "2025-10-13T10:30:00",
      "level": "INFO",
      "message": "Scraping npc: found 750 listings"
    }
  ]
}
```

---

### Data Query

#### `GET /api/data/sites`

List all available data files.

**Response:**
```json
{
  "raw_sites": [
    {
      "site_key": "npc",
      "latest_file": "sites/npc/2025-10-13_10-30-00_npc.csv",
      "file_count": 15,
      "last_updated": 1697194200.0
    }
  ],
  "cleaned_sites": [
    {
      "site_key": "npc",
      "file": "cleaned/npc/npc_cleaned.csv",
      "last_updated": 1697194500.0
    }
  ],
  "master_workbook_exists": true,
  "master_workbook_path": "cleaned/MASTER_CLEANED_WORKBOOK.xlsx",
  "master_workbook_updated": 1697194500.0
}
```

---

#### `GET /api/data/sites/<site_key>`

Get data for specific site.

**Query Parameters:**
- `limit` (optional): Number of records (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `source` (optional): 'raw' or 'cleaned' (default: 'cleaned')

**Response:**
```json
{
  "site_key": "npc",
  "source": "cleaned",
  "total_records": 750,
  "returned_records": 100,
  "offset": 0,
  "limit": 100,
  "data": [
    {
      "title": "5 Bedroom Duplex in Lekki",
      "price": 50000000,
      "location": "Lekki Phase 1",
      "property_type": "House",
      "bedrooms": 5,
      "bathrooms": 6,
      "listing_url": "https://...",
      "source": "npc"
    }
  ]
}
```

---

#### `GET /api/data/master`

Get consolidated master workbook data.

**Query Parameters:**
- `limit` (optional): Number of records per site (default: 100)
- `site` (optional): Filter by specific site

**Response:**
```json
{
  "total_sheets": 25,
  "sheets": [
    {
      "site_key": "npc",
      "total_records": 750,
      "returned_records": 100,
      "data": [...]
    }
  ]
}
```

---

#### `GET /api/data/search`

Search across all data.

**Query Parameters:**
- `query` (required): Search term
- `fields` (optional): Comma-separated fields (default: "title,location")
- `limit` (optional): Max results (default: 50)

**Response:**
```json
{
  "query": "lekki",
  "fields": ["title", "location"],
  "total_results": 45,
  "results": [
    {
      "site_key": "npc",
      "data": {
        "title": "5 Bedroom in Lekki",
        "location": "Lekki Phase 1",
        "price": 50000000
      }
    }
  ]
}
```

---

### Statistics

#### `GET /api/stats/overview`

Get overall statistics.

**Response:**
```json
{
  "overview": {
    "total_sites": 50,
    "active_sites": 25,
    "total_listings": 15000,
    "latest_scrape": "2025-10-13T10:30:00"
  },
  "files": {
    "raw_files": 150,
    "cleaned_files": 75,
    "master_workbook_exists": true,
    "master_workbook_size_mb": 12.5
  }
}
```

---

#### `GET /api/stats/sites`

Get per-site statistics.

**Response:**
```json
{
  "total": 50,
  "sites": [
    {
      "site_key": "npc",
      "last_scrape": "2025-10-13T10:30:00",
      "last_successful_scrape": "2025-10-13T10:30:00",
      "last_count": 750,
      "total_scrapes": 15,
      "status": "active",
      "health": "healthy"
    }
  ]
}
```

**Health Status:**
- `healthy`: last_count >= 100
- `warning`: last_count >= 10
- `critical`: last_count < 10
- `inactive`: last_count = 0

---

#### `GET /api/stats/trends`

Get historical trends.

**Query Parameters:**
- `days` (optional): Number of days (default: 7)

**Response:**
```json
{
  "period_days": 7,
  "total_scrapes": 45,
  "daily_trends": [
    {
      "date": "2025-10-07",
      "total_listings": 1200,
      "total_scrapes": 5
    }
  ]
}
```

---

## Next.js Integration Examples

### API Hooks

Create reusable hooks for API calls:

#### `hooks/useScraper.ts`

```typescript
import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

interface ScrapeOptions {
  sites?: string[];
  max_pages?: number;
  geocoding?: boolean;
}

export function useScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startScrape = useCallback(async (options: ScrapeOptions = {}) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/scrape/start', options);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Failed to start scraping';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const stopScrape = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/scrape/stop');
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Failed to stop scraping';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { startScrape, stopScrape, isLoading, error };
}
```

#### `hooks/useScrapeStatus.ts`

```typescript
import useSWR from 'swr';
import { api } from '@/lib/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export function useScrapeStatus(refreshInterval: number = 5000) {
  const { data, error, mutate } = useSWR('/scrape/status', fetcher, {
    refreshInterval,
    revalidateOnFocus: true
  });

  return {
    status: data,
    isLoading: !error && !data,
    isError: error,
    refresh: mutate
  };
}
```

#### `hooks/useSites.ts`

```typescript
import useSWR from 'swr';
import { api } from '@/lib/api';
import { useCallback } from 'react';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export function useSites() {
  const { data, error, mutate } = useSWR('/sites', fetcher);

  const addSite = useCallback(async (siteData: any) => {
    const response = await api.post('/sites', siteData);
    mutate(); // Refresh sites list
    return response.data;
  }, [mutate]);

  const updateSite = useCallback(async (siteKey: string, updates: any) => {
    const response = await api.put(`/sites/${siteKey}`, updates);
    mutate();
    return response.data;
  }, [mutate]);

  const deleteSite = useCallback(async (siteKey: string) => {
    const response = await api.delete(`/sites/${siteKey}`);
    mutate();
    return response.data;
  }, [mutate]);

  const toggleSite = useCallback(async (siteKey: string) => {
    const response = await api.patch(`/sites/${siteKey}/toggle`);
    mutate();
    return response.data;
  }, [mutate]);

  return {
    sites: data,
    isLoading: !error && !data,
    isError: error,
    addSite,
    updateSite,
    deleteSite,
    toggleSite,
    refresh: mutate
  };
}
```

---

### Page Components

#### Scraper Control Panel

```tsx
// app/scraper/page.tsx
'use client';

import { useState } from 'react';
import { useScraper } from '@/hooks/useScraper';
import { useScrapeStatus } from '@/hooks/useScrapeStatus';

export default function ScraperControlPanel() {
  const { startScrape, stopScrape, isLoading } = useScraper();
  const { status, refresh } = useScrapeStatus();

  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const [maxPages, setMaxPages] = useState(20);

  const handleStart = async () => {
    try {
      await startScrape({
        sites: selectedSites.length > 0 ? selectedSites : undefined,
        max_pages: maxPages,
        geocoding: true
      });

      alert('Scraping started successfully!');
      refresh();
    } catch (error) {
      console.error('Failed to start scraping:', error);
    }
  };

  const handleStop = async () => {
    try {
      await stopScrape();
      alert('Scraping stopped');
      refresh();
    } catch (error) {
      console.error('Failed to stop scraping:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Scraper Control</h1>

      {/* Status Display */}
      <div className="bg-gray-100 p-4 rounded mb-4">
        <h2 className="font-semibold">Status:</h2>
        {status?.is_running ? (
          <div className="text-green-600">
            ✓ Running - Run ID: {status.current_run?.run_id}
          </div>
        ) : (
          <div className="text-gray-600">Idle</div>
        )}
      </div>

      {/* Controls */}
      <div className="space-y-4">
        <div>
          <label className="block mb-2">Max Pages:</label>
          <input
            type="number"
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            className="border p-2 rounded"
          />
        </div>

        <div className="space-x-2">
          <button
            onClick={handleStart}
            disabled={isLoading || status?.is_running}
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            Start Scraping
          </button>

          <button
            onClick={handleStop}
            disabled={isLoading || !status?.is_running}
            className="bg-red-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            Stop Scraping
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

#### Sites Management

```tsx
// app/sites/page.tsx
'use client';

import { useSites } from '@/hooks/useSites';

export default function SitesManagement() {
  const { sites, toggleSite, isLoading } = useSites();

  const handleToggle = async (siteKey: string) => {
    try {
      await toggleSite(siteKey);
    } catch (error) {
      console.error('Failed to toggle site:', error);
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Sites Configuration</h1>

      <div className="space-y-2">
        {sites?.sites?.map((site: any) => (
          <div key={site.site_key} className="flex items-center justify-between border p-3 rounded">
            <div>
              <div className="font-semibold">{site.name}</div>
              <div className="text-sm text-gray-600">{site.url}</div>
            </div>

            <button
              onClick={() => handleToggle(site.site_key)}
              className={`px-4 py-2 rounded ${
                site.enabled
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-700'
              }`}
            >
              {site.enabled ? 'Enabled' : 'Disabled'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

#### Data Viewer

```tsx
// app/data/page.tsx
'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function DataViewer() {
  const [selectedSite, setSelectedSite] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: availableData } = useSWR('/data/sites', fetcher);
  const { data: siteData } = useSWR(
    selectedSite ? `/data/sites/${selectedSite}?limit=50` : null,
    fetcher
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Data Viewer</h1>

      {/* Site Selector */}
      <div className="mb-4">
        <select
          value={selectedSite}
          onChange={(e) => setSelectedSite(e.target.value)}
          className="border p-2 rounded w-full"
        >
          <option value="">Select a site...</option>
          {availableData?.cleaned_sites?.map((site: any) => (
            <option key={site.site_key} value={site.site_key}>
              {site.site_key}
            </option>
          ))}
        </select>
      </div>

      {/* Data Table */}
      {siteData && (
        <div>
          <div className="mb-2 text-sm text-gray-600">
            Showing {siteData.returned_records} of {siteData.total_records} records
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border p-2">Title</th>
                  <th className="border p-2">Price</th>
                  <th className="border p-2">Location</th>
                  <th className="border p-2">Type</th>
                </tr>
              </thead>
              <tbody>
                {siteData.data.map((item: any, idx: number) => (
                  <tr key={idx}>
                    <td className="border p-2">{item.title}</td>
                    <td className="border p-2">₦{item.price?.toLocaleString()}</td>
                    <td className="border p-2">{item.location}</td>
                    <td className="border p-2">{item.property_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

#### Statistics Dashboard

```tsx
// app/dashboard/page.tsx
'use client';

import useSWR from 'swr';
import { api } from '@/lib/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function Dashboard() {
  const { data: overview } = useSWR('/stats/overview', fetcher);
  const { data: siteStats } = useSWR('/stats/sites', fetcher);
  const { data: trends } = useSWR('/stats/trends?days=7', fetcher);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {/* Overview Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-100 p-4 rounded">
          <div className="text-3xl font-bold">{overview?.overview?.total_sites}</div>
          <div className="text-sm">Total Sites</div>
        </div>

        <div className="bg-green-100 p-4 rounded">
          <div className="text-3xl font-bold">{overview?.overview?.active_sites}</div>
          <div className="text-sm">Active Sites</div>
        </div>

        <div className="bg-purple-100 p-4 rounded">
          <div className="text-3xl font-bold">{overview?.overview?.total_listings?.toLocaleString()}</div>
          <div className="text-sm">Total Listings</div>
        </div>

        <div className="bg-yellow-100 p-4 rounded">
          <div className="text-3xl font-bold">{overview?.files?.master_workbook_size_mb} MB</div>
          <div className="text-sm">Master Workbook</div>
        </div>
      </div>

      {/* Site Performance Table */}
      <div className="bg-white border rounded p-4 mb-6">
        <h2 className="text-xl font-semibold mb-3">Site Performance</h2>
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 text-left">Site</th>
              <th className="p-2 text-left">Status</th>
              <th className="p-2 text-left">Health</th>
              <th className="p-2 text-right">Last Count</th>
              <th className="p-2 text-right">Total Scrapes</th>
            </tr>
          </thead>
          <tbody>
            {siteStats?.sites?.slice(0, 10).map((site: any) => (
              <tr key={site.site_key} className="border-t">
                <td className="p-2">{site.site_key}</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    site.status === 'active' ? 'bg-green-200' : 'bg-gray-200'
                  }`}>
                    {site.status}
                  </span>
                </td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    site.health === 'healthy' ? 'bg-green-200' :
                    site.health === 'warning' ? 'bg-yellow-200' :
                    'bg-red-200'
                  }`}>
                    {site.health}
                  </span>
                </td>
                <td className="p-2 text-right">{site.last_count.toLocaleString()}</td>
                <td className="p-2 text-right">{site.total_scrapes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Trends Chart (simplified) */}
      <div className="bg-white border rounded p-4">
        <h2 className="text-xl font-semibold mb-3">7-Day Trends</h2>
        <div className="space-y-2">
          {trends?.daily_trends?.map((day: any) => (
            <div key={day.date} className="flex items-center">
              <div className="w-24 text-sm">{day.date}</div>
              <div className="flex-1">
                <div
                  className="bg-blue-500 h-6 rounded"
                  style={{ width: `${(day.total_listings / 2000) * 100}%` }}
                />
              </div>
              <div className="w-24 text-right text-sm">{day.total_listings} listings</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Error Handling

### API Error Types

```typescript
interface ApiError {
  error: string;
  details?: any;
}
```

### Error Handler Utility

```typescript
// lib/errorHandler.ts
export function handleApiError(error: any): string {
  if (error.response) {
    // Server responded with error
    return error.response.data.error || 'Server error occurred';
  } else if (error.request) {
    // No response received
    return 'Unable to reach server. Please check your connection.';
  } else {
    // Request setup error
    return error.message || 'An unexpected error occurred';
  }
}
```

### Usage in Components

```typescript
try {
  await api.post('/scrape/start', options);
} catch (error) {
  const errorMessage = handleApiError(error);
  toast.error(errorMessage);
  console.error('API Error:', error);
}
```

---

## Best Practices

### 1. Use SWR for Data Fetching

SWR provides automatic caching, revalidation, and error handling:

```typescript
import useSWR from 'swr';

const { data, error, mutate } = useSWR('/api/endpoint', fetcher, {
  refreshInterval: 5000,  // Auto-refresh every 5 seconds
  revalidateOnFocus: true,
  revalidateOnReconnect: true
});
```

### 2. Handle Loading States

Always provide feedback for async operations:

```tsx
{isLoading && <LoadingSpinner />}
{error && <ErrorMessage error={error} />}
{data && <DataDisplay data={data} />}
```

### 3. Implement Pagination

For large datasets, use pagination:

```typescript
const [page, setPage] = useState(0);
const limit = 50;
const offset = page * limit;

const { data } = useSWR(
  `/data/sites/${siteKey}?limit=${limit}&offset=${offset}`,
  fetcher
);
```

### 4. Debounce Search Input

Prevent excessive API calls:

```typescript
import { useDebouncedValue } from '@/hooks/useDebounce';

const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebouncedValue(searchTerm, 500);

const { data } = useSWR(
  debouncedSearch ? `/data/search?query=${debouncedSearch}` : null,
  fetcher
);
```

### 5. Real-time Updates

Poll scraping status while running:

```typescript
const { data: status } = useSWR('/scrape/status', fetcher, {
  refreshInterval: status?.is_running ? 3000 : 0,
  // Only poll when scraping is running
});
```

### 6. Optimistic UI Updates

Update UI before API response:

```typescript
const toggleSite = async (siteKey: string) => {
  // Optimistically update UI
  mutate(
    (current) => ({
      ...current,
      sites: current.sites.map((s) =>
        s.site_key === siteKey ? { ...s, enabled: !s.enabled } : s
      )
    }),
    false
  );

  // Make API call
  try {
    await api.patch(`/sites/${siteKey}/toggle`);
  } catch (error) {
    // Revert on error
    mutate();
  }
};
```

---

## GitHub Actions Integration (For Serverless Deployment)

### Overview

When deployed using GitHub Actions (instead of Flask API), your frontend can trigger scraper runs via GitHub's API using **repository_dispatch** events.

**Use Case**: Serverless scraping without running a local Flask API server.

### Architecture

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │
│                 │
└────────┬────────┘
         │
         │ GitHub API
         │ (repository_dispatch)
         ▼
┌─────────────────────┐
│  GitHub Actions     │
│  Workflow           │
│  (.github/workflows)│
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│  Python         │
│  Scraper Runs   │
│  (main.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub         │
│  Artifacts      │
│  (Exports)      │
└─────────────────┘
```

### Prerequisites

1. **GitHub Personal Access Token (PAT)**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy token (save securely)

2. **Repository Details**
   - Owner: Your GitHub username (e.g., `Tee-David`)
   - Repo: Your repository name (e.g., `realtors_practice`)

### Backend Setup (GitHub Actions Workflow)

The workflow must include `repository_dispatch` as a trigger:

```yaml
# .github/workflows/scrape.yml
name: Scraper Workflow

on:
  # Trigger via frontend
  repository_dispatch:
    types: [trigger-scrape]

  # Scheduled runs
  schedule:
    - cron: '0 3 * * *'

  # Manual trigger
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Run scraper
        env:
          # Use inputs from repository_dispatch
          RP_PAGE_CAP: ${{ github.event.client_payload.page_cap || '20' }}
          RP_GEOCODE: ${{ github.event.client_payload.geocode || '1' }}
          RP_HEADLESS: 1
        run: |
          python main.py

      - name: Process exports
        run: |
          python watcher.py --once

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: scraper-exports-${{ github.run_number }}
          path: exports/cleaned/
          retention-days: 30
```

### Frontend Implementation

#### 1. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_GITHUB_TOKEN=ghp_your_token_here
NEXT_PUBLIC_GITHUB_OWNER=Tee-David
NEXT_PUBLIC_GITHUB_REPO=realtors_practice
```

#### 2. API Route for GitHub Actions Trigger

Create `app/api/trigger-scrape/route.ts`:

```typescript
// app/api/trigger-scrape/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { page_cap, geocode } = body;

    const GITHUB_TOKEN = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
    const GITHUB_OWNER = process.env.NEXT_PUBLIC_GITHUB_OWNER;
    const GITHUB_REPO = process.env.NEXT_PUBLIC_GITHUB_REPO;

    if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
      return NextResponse.json(
        { error: 'Missing GitHub configuration' },
        { status: 500 }
      );
    }

    // Trigger GitHub Actions workflow
    const response = await fetch(
      `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github+json',
          'Authorization': `Bearer ${GITHUB_TOKEN}`,
          'X-GitHub-Api-Version': '2022-11-28',
        },
        body: JSON.stringify({
          event_type: 'trigger-scrape',
          client_payload: {
            page_cap: page_cap || 20,
            geocode: geocode !== undefined ? geocode : 1,
            triggered_by: 'frontend',
            timestamp: new Date().toISOString(),
          },
        }),
      }
    );

    if (response.status === 204) {
      return NextResponse.json({
        success: true,
        message: 'Scraper workflow triggered successfully',
        run_url: `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/actions`,
      });
    } else {
      const error = await response.text();
      return NextResponse.json(
        { error: `GitHub API error: ${error}` },
        { status: response.status }
      );
    }
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
```

#### 3. Frontend Component

```tsx
// components/ScraperControl.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';

export default function ScraperControl() {
  const [isTriggering, setIsTriggering] = useState(false);
  const [message, setMessage] = useState('');
  const [pageCap, setPageCap] = useState(20);
  const [geocode, setGeocode] = useState(true);

  const handleTriggerScrape = async () => {
    setIsTriggering(true);
    setMessage('');

    try {
      const response = await axios.post('/api/trigger-scrape', {
        page_cap: pageCap,
        geocode: geocode ? 1 : 0,
      });

      setMessage(response.data.message);

      // Optionally open GitHub Actions page
      if (response.data.run_url) {
        window.open(response.data.run_url, '_blank');
      }
    } catch (error: any) {
      setMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Trigger Scraper</h2>

      <div className="space-y-4">
        {/* Page Cap */}
        <div>
          <label className="block text-sm font-medium mb-1">
            Pages per Site
          </label>
          <input
            type="number"
            value={pageCap}
            onChange={(e) => setPageCap(Number(e.target.value))}
            className="border p-2 rounded w-full"
            min="1"
            max="50"
          />
        </div>

        {/* Geocoding */}
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={geocode}
            onChange={(e) => setGeocode(e.target.checked)}
            className="mr-2"
          />
          <label className="text-sm font-medium">
            Enable Geocoding
          </label>
        </div>

        {/* Trigger Button */}
        <button
          onClick={handleTriggerScrape}
          disabled={isTriggering}
          className={`w-full py-2 px-4 rounded font-semibold ${
            isTriggering
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {isTriggering ? 'Triggering...' : 'Trigger Scraper Run'}
        </button>

        {/* Message */}
        {message && (
          <div
            className={`p-3 rounded ${
              message.includes('Error')
                ? 'bg-red-100 text-red-700'
                : 'bg-green-100 text-green-700'
            }`}
          >
            {message}
          </div>
        )}

        {/* Info */}
        <div className="text-sm text-gray-600 mt-4">
          <p>✨ This will trigger a GitHub Actions workflow</p>
          <p>⏱️ Scraping runs in the cloud (no local server needed)</p>
          <p>📦 Results available as GitHub artifacts (30-day retention)</p>
        </div>
      </div>
    </div>
  );
}
```

#### 4. Check Workflow Status

```tsx
// components/WorkflowStatus.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface WorkflowRun {
  id: number;
  status: string;
  conclusion: string | null;
  created_at: string;
  html_url: string;
}

export default function WorkflowStatus() {
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);

  const GITHUB_TOKEN = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
  const GITHUB_OWNER = process.env.NEXT_PUBLIC_GITHUB_OWNER;
  const GITHUB_REPO = process.env.NEXT_PUBLIC_GITHUB_REPO;

  useEffect(() => {
    fetchWorkflowRuns();
    const interval = setInterval(fetchWorkflowRuns, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflowRuns = async () => {
    try {
      const response = await axios.get(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs`,
        {
          headers: {
            'Accept': 'application/vnd.github+json',
            'Authorization': `Bearer ${GITHUB_TOKEN}`,
          },
          params: {
            per_page: 5, // Get last 5 runs
          },
        }
      );

      setRuns(response.data.workflow_runs);
    } catch (error) {
      console.error('Failed to fetch workflow runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (run: WorkflowRun) => {
    if (run.status === 'in_progress' || run.status === 'queued') {
      return (
        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
          🔄 Running
        </span>
      );
    }

    if (run.conclusion === 'success') {
      return (
        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
          ✅ Success
        </span>
      );
    }

    if (run.conclusion === 'failure') {
      return (
        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
          ❌ Failed
        </span>
      );
    }

    return (
      <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">
        ⏸️ {run.conclusion}
      </span>
    );
  };

  if (loading) {
    return <div className="p-6">Loading workflow status...</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Recent Workflow Runs</h2>

      <div className="space-y-3">
        {runs.map((run) => (
          <div
            key={run.id}
            className="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
          >
            <div>
              <div className="font-medium">Run #{run.id}</div>
              <div className="text-sm text-gray-600">
                {new Date(run.created_at).toLocaleString()}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {getStatusBadge(run)}
              <a
                href={run.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline text-sm"
              >
                View →
              </a>
            </div>
          </div>
        ))}
      </div>

      {runs.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No workflow runs found
        </div>
      )}
    </div>
  );
}
```

#### 5. Download Artifacts

```tsx
// components/ArtifactDownloader.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Artifact {
  id: number;
  name: string;
  size_in_bytes: number;
  created_at: string;
  archive_download_url: string;
}

export default function ArtifactDownloader() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(true);

  const GITHUB_TOKEN = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
  const GITHUB_OWNER = process.env.NEXT_PUBLIC_GITHUB_OWNER;
  const GITHUB_REPO = process.env.NEXT_PUBLIC_GITHUB_REPO;

  useEffect(() => {
    fetchArtifacts();
  }, []);

  const fetchArtifacts = async () => {
    try {
      const response = await axios.get(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/artifacts`,
        {
          headers: {
            'Accept': 'application/vnd.github+json',
            'Authorization': `Bearer ${GITHUB_TOKEN}`,
          },
        }
      );

      setArtifacts(response.data.artifacts);
    } catch (error) {
      console.error('Failed to fetch artifacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadArtifact = async (artifact: Artifact) => {
    try {
      const response = await axios.get(artifact.archive_download_url, {
        headers: {
          'Authorization': `Bearer ${GITHUB_TOKEN}`,
        },
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${artifact.name}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download artifact:', error);
    }
  };

  if (loading) {
    return <div className="p-6">Loading artifacts...</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Download Scraped Data</h2>

      <div className="space-y-3">
        {artifacts.map((artifact) => (
          <div
            key={artifact.id}
            className="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
          >
            <div>
              <div className="font-medium">{artifact.name}</div>
              <div className="text-sm text-gray-600">
                {(artifact.size_in_bytes / 1024 / 1024).toFixed(2)} MB
                {' • '}
                {new Date(artifact.created_at).toLocaleDateString()}
              </div>
            </div>

            <button
              onClick={() => downloadArtifact(artifact)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Download
            </button>
          </div>
        ))}
      </div>

      {artifacts.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No artifacts available
        </div>
      )}
    </div>
  );
}
```

### Security Considerations

1. **Never expose GitHub PAT in client-side code**
   - Store token in environment variables
   - Use API routes (server-side) for GitHub API calls
   - For production, use GitHub Apps instead of PATs

2. **Rate Limiting**
   - GitHub API: 5000 requests/hour for authenticated requests
   - Implement client-side throttling

3. **Token Permissions**
   - Use minimal required scopes
   - Consider fine-grained tokens (beta)
   - Rotate tokens regularly

### Deployment Options Comparison

| Feature | Flask API (Local) | GitHub Actions (Serverless) |
|---------|-------------------|----------------------------|
| **Cost** | Free (local) | Free (2000 min/month) |
| **Setup** | Run `python api_server.py` | GitHub workflow file |
| **Always On** | Requires server running | No server needed |
| **Trigger** | HTTP REST API | GitHub repository_dispatch |
| **Real-time Status** | Yes (polling) | Yes (via GitHub API) |
| **Data Access** | Direct file access | GitHub artifacts (download) |
| **Best For** | Development, local testing | Production, serverless deployment |

### Complete Example Page

```tsx
// app/scraper/page.tsx
'use client';

import ScraperControl from '@/components/ScraperControl';
import WorkflowStatus from '@/components/WorkflowStatus';
import ArtifactDownloader from '@/components/ArtifactDownloader';

export default function ScraperPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Scraper Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trigger Control */}
        <div>
          <ScraperControl />
        </div>

        {/* Workflow Status */}
        <div>
          <WorkflowStatus />
        </div>

        {/* Artifact Downloader */}
        <div className="lg:col-span-2">
          <ArtifactDownloader />
        </div>
      </div>
    </div>
  );
}
```

### Testing

1. **Test repository_dispatch trigger**:
   ```bash
   curl -X POST \
     -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.github.com/repos/OWNER/REPO/dispatches \
     -d '{"event_type":"trigger-scrape","client_payload":{"page_cap":10}}'
   ```

2. **Check workflow runs**:
   - Go to `https://github.com/OWNER/REPO/actions`
   - Verify workflow was triggered
   - Check logs

3. **Download artifacts**:
   - Click on completed workflow run
   - Download artifacts from bottom of page

---

## Troubleshooting

### API Not Responding

**Check if API server is running:**
```bash
curl http://localhost:5000/api/health
```

**Start API server:**
```bash
python api_server.py
```

---

### CORS Errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** API server has `flask-cors` enabled by default. Verify:
- API server is running
- Frontend is making requests to correct URL
- Check browser console for exact error

---

### Site Configuration Not Saving

**Check config.yaml permissions:**
```bash
# Ensure config.yaml is writable
ls -l config.yaml
```

**Verify config syntax:**
```bash
python scripts/validate_config.py
```

---

### Data Not Loading

**Check data files exist:**
```bash
ls exports/cleaned/
ls exports/sites/
```

**Run watcher to process exports:**
```bash
python watcher.py --once
```

---

### Scraper Not Starting

**Check if already running:**
```bash
GET http://localhost:5000/api/scrape/status
```

**Check logs:**
```bash
tail -f logs/scraper.log
```

**Verify sites are enabled:**
```bash
python scripts/status.py
```

---

## Additional Resources

- **Backend Documentation:** `README.md`, `STRUCTURE.md`
- **API Testing:** Use tools like Postman or Insomnia
- **Logs Location:** `logs/scraper.log`
- **Data Location:** `exports/cleaned/`

---

**Last Updated:** 2025-10-13
**API Version:** 1.0.0
