# API Quick Start Guide

Quick reference for getting started with the Real Estate Scraper API.

## Prerequisites

- Python 3.8+
- Node.js 18+ (for Next.js frontend)
- Running backend scraper

## 1. Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server (default port 5000)
python api_server.py

# Verify it's running
curl http://localhost:5000/api/health
# Expected: {"status": "healthy", ...}
```

## 2. Test API Endpoints

### Health Check
```bash
curl http://localhost:5000/api/health
```

### List Sites
```bash
curl http://localhost:5000/api/sites
```

### Start Scraping
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 5}'
```

### Check Status
```bash
curl http://localhost:5000/api/scrape/status
```

### Get Data
```bash
curl "http://localhost:5000/api/data/sites/npc?limit=10"
```

### View Logs
```bash
curl "http://localhost:5000/api/logs?limit=20"
```

### Get Statistics
```bash
curl http://localhost:5000/api/stats/overview
```

## 3. Frontend Integration (Next.js)

### Install Dependencies

```bash
npm install axios swr
```

### Create API Client

```typescript
// lib/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Example Component

```tsx
// app/scraper/page.tsx
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

export default function ScraperPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const startScraping = async () => {
    setLoading(true);
    try {
      const response = await api.post('/scrape/start', {
        sites: ['npc'],
        max_pages: 10
      });
      alert('Started: ' + response.data.run_id);
      checkStatus();
    } catch (error: any) {
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    const response = await api.get('/scrape/status');
    setStatus(response.data);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Scraper Control</h1>

      <button
        onClick={startScraping}
        disabled={loading || status?.is_running}
        className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
      >
        Start Scraping
      </button>

      <button
        onClick={checkStatus}
        className="bg-gray-500 text-white px-4 py-2 rounded"
      >
        Check Status
      </button>

      {status && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <pre>{JSON.stringify(status, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## 4. Common Workflows

### Workflow 1: Start Scraping Specific Sites

```typescript
// 1. Get list of sites
const sitesResponse = await api.get('/sites');
const sites = sitesResponse.data.sites;

// 2. Enable specific sites
await api.patch('/sites/npc/toggle');
await api.patch('/sites/propertypro/toggle');

// 3. Start scraping
await api.post('/scrape/start', {
  sites: ['npc', 'propertypro'],
  max_pages: 20,
  geocoding: true
});

// 4. Monitor status
const interval = setInterval(async () => {
  const statusResponse = await api.get('/scrape/status');
  if (!statusResponse.data.is_running) {
    clearInterval(interval);
    console.log('Scraping complete!');
  }
}, 5000);
```

### Workflow 2: Add New Site

```typescript
// Add new site configuration
await api.post('/sites', {
  site_key: 'newsite',
  name: 'New Property Site',
  url: 'https://newsite.com',
  enabled: true,
  parser: 'specials',
  selectors: {
    card: '.property-card',
    title: '.title',
    price: '.price',
    location: '.location'
  }
});

// Verify it was added
const siteResponse = await api.get('/sites/newsite');
console.log(siteResponse.data);
```

### Workflow 3: Query and Display Data

```typescript
// Get available data
const dataResponse = await api.get('/data/sites');
const cleanedSites = dataResponse.data.cleaned_sites;

// Get data for specific site
const npcData = await api.get('/data/sites/npc', {
  params: {
    limit: 50,
    offset: 0,
    source: 'cleaned'
  }
});

// Display listings
npcData.data.data.forEach((listing: any) => {
  console.log(`${listing.title} - ₦${listing.price} in ${listing.location}`);
});

// Search across all sites
const searchResponse = await api.get('/data/search', {
  params: {
    query: 'lekki',
    fields: 'title,location',
    limit: 30
  }
});

console.log(`Found ${searchResponse.data.total_results} results`);
```

### Workflow 4: View Logs and Errors

```typescript
// Get recent logs
const logsResponse = await api.get('/logs', {
  params: {
    limit: 100,
    level: 'ERROR'  // Only errors
  }
});

// Get site-specific logs
const siteLogsResponse = await api.get('/logs/site/npc', {
  params: { limit: 50 }
});

// Display errors
logsResponse.data.logs.forEach((log: any) => {
  console.error(`[${log.timestamp}] ${log.message}`);
});
```

### Workflow 5: Display Statistics Dashboard

```typescript
// Get overview stats
const overviewResponse = await api.get('/stats/overview');
const overview = overviewResponse.data;

console.log(`Total Sites: ${overview.overview.total_sites}`);
console.log(`Total Listings: ${overview.overview.total_listings}`);

// Get site performance
const siteStatsResponse = await api.get('/stats/sites');
const topSites = siteStatsResponse.data.sites.slice(0, 10);

topSites.forEach((site: any) => {
  console.log(`${site.site_key}: ${site.last_count} listings (${site.health})`);
});

// Get trends
const trendsResponse = await api.get('/stats/trends', {
  params: { days: 7 }
});

trendsResponse.data.daily_trends.forEach((day: any) => {
  console.log(`${day.date}: ${day.total_listings} listings`);
});
```

## 5. Environment Configuration

### Backend (.env)

```env
# API Configuration
API_PORT=5000
API_DEBUG=false

# Scraper Settings
RP_PAGE_CAP=30
RP_GEOCODE=1
RP_HEADLESS=1
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## 6. Development Tips

### Enable Debug Logging

```bash
API_DEBUG=true python api_server.py
```

### Test with Postman/Insomnia

Import these endpoints:
- GET http://localhost:5000/api/health
- GET http://localhost:5000/api/sites
- POST http://localhost:5000/api/scrape/start
- GET http://localhost:5000/api/scrape/status
- GET http://localhost:5000/api/data/sites
- GET http://localhost:5000/api/stats/overview

### Monitor API Logs

```bash
# Watch API server output
python api_server.py

# Watch scraper logs
tail -f logs/scraper.log

# Watch watcher logs
tail -f exports/cleaned/watcher.log
```

### Validate Configuration

```bash
python scripts/validate_config.py
```

## 7. Production Deployment

### Run API Server as Service (Linux/cPanel)

```bash
# Create systemd service
sudo nano /etc/systemd/system/scraper-api.service

[Unit]
Description=Real Estate Scraper API
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/realtors_practice
Environment="API_PORT=5000"
ExecStart=/path/to/venv/bin/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# Start service
sudo systemctl start scraper-api
sudo systemctl enable scraper-api
```

### Use Gunicorn (Production)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 8. Troubleshooting

### API Not Starting

```bash
# Check if port is in use
lsof -i :5000

# Kill process using port
kill -9 <PID>

# Start with different port
API_PORT=8000 python api_server.py
```

### CORS Errors

Ensure `flask-cors` is installed:
```bash
pip install flask-cors
```

### Data Not Found

Run watcher to process exports:
```bash
python watcher.py --once
```

### Config Validation Errors

```bash
python scripts/validate_config.py
```

## Next Steps

1. Read full documentation: `docs/FRONTEND_INTEGRATION.md`
2. Explore API endpoints with Postman
3. Build your Next.js components
4. Implement real-time updates with SWR
5. Add authentication if needed
6. Deploy to production

---

**Quick Links:**
- Full API Docs: `docs/FRONTEND_INTEGRATION.md`
- Project Structure: `STRUCTURE.md`
- Backend README: `README.md`
- Config Guide: `config.example.yaml`
