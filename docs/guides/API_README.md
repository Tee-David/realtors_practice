# Real Estate Scraper API

REST API for managing scraping operations, configuring sites, and querying scraped data.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies for API:
- `flask` - Web framework
- `flask-cors` - CORS support
- `pandas` - Data manipulation

### 2. Start API Server

```bash
python api_server.py
```

Server starts on `http://localhost:5000`

### 3. Test API

```bash
curl http://localhost:5000/api/health
```

## Documentation

- **[Frontend Integration Guide](FRONTEND_INTEGRATION.md)** - Complete guide for Next.js integration (150+ KB)
- **[API Quick Start](API_QUICKSTART.md)** - Quick reference and examples

## API Overview

### Endpoints

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Health** | `/api/health` | GET | Health check |
| **Scraping** | `/api/scrape/start` | POST | Start scraping |
| | `/api/scrape/status` | GET | Get status |
| | `/api/scrape/stop` | POST | Stop scraping |
| | `/api/scrape/history` | GET | Get history |
| **Sites** | `/api/sites` | GET | List all sites |
| | `/api/sites/<key>` | GET | Get site config |
| | `/api/sites` | POST | Add site |
| | `/api/sites/<key>` | PUT | Update site |
| | `/api/sites/<key>` | DELETE | Delete site |
| | `/api/sites/<key>/toggle` | PATCH | Toggle enabled |
| **Logs** | `/api/logs` | GET | Get logs |
| | `/api/logs/errors` | GET | Get errors |
| | `/api/logs/site/<key>` | GET | Get site logs |
| **Data** | `/api/data/sites` | GET | List data files |
| | `/api/data/sites/<key>` | GET | Get site data |
| | `/api/data/master` | GET | Get master data |
| | `/api/data/search` | GET | Search data |
| **Stats** | `/api/stats/overview` | GET | Overview stats |
| | `/api/stats/sites` | GET | Site stats |
| | `/api/stats/trends` | GET | Trends |

## Architecture

```
┌─────────────────┐         HTTP/REST         ┌─────────────────┐
│  Next.js        │ ◄────────────────────────► │  Flask API      │
│  Frontend       │      (Port 5000)           │  Server         │
└─────────────────┘                            └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Python         │
                                               │  Scraper        │
                                               │  (main.py)      │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │  Data Storage    │
                                              │  - config.yaml   │
                                              │  - exports/      │
                                              │  - logs/         │
                                              └──────────────────┘
```

## API Helper Modules

Located in `api/helpers/`:

- **`data_reader.py`** - Read and query Excel/CSV data
- **`log_parser.py`** - Parse and filter log files
- **`config_manager.py`** - Manage config.yaml programmatically
- **`scraper_manager.py`** - Manage scraping processes
- **`stats_generator.py`** - Generate statistics

## Example Usage

### Start Scraping

```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 10}'
```

### Check Status

```bash
curl http://localhost:5000/api/scrape/status
```

### Get Data

```bash
curl "http://localhost:5000/api/data/sites/npc?limit=50"
```

### Add New Site

```bash
curl -X POST http://localhost:5000/api/sites \
  -H "Content-Type: application/json" \
  -d '{
    "site_key": "newsite",
    "name": "New Site",
    "url": "https://newsite.com",
    "enabled": true,
    "parser": "specials"
  }'
```

## Configuration

### Environment Variables

```bash
# API settings
API_PORT=5000        # API server port
API_DEBUG=false      # Debug mode

# Scraper settings
RP_PAGE_CAP=30       # Max pages per site
RP_GEOCODE=1         # Enable geocoding
RP_HEADLESS=1        # Headless browser
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Systemd Service (Linux)

```bash
sudo nano /etc/systemd/system/scraper-api.service
```

```ini
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
```

```bash
sudo systemctl start scraper-api
sudo systemctl enable scraper-api
```

## Frontend Integration

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
});
```

### Example Hook

```typescript
// hooks/useScraper.ts
import { api } from '@/lib/api';

export function useScraper() {
  const startScrape = async (options) => {
    const response = await api.post('/scrape/start', options);
    return response.data;
  };

  return { startScrape };
}
```

See **[Frontend Integration Guide](FRONTEND_INTEGRATION.md)** for complete examples.

## Development

### Run API in Debug Mode

```bash
API_DEBUG=true python api_server.py
```

### Test Endpoints

Use Postman, Insomnia, or curl to test endpoints.

### Monitor Logs

```bash
tail -f logs/scraper.log
```

## Troubleshooting

### API Not Starting

Check if port is in use:
```bash
lsof -i :5000
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

## Resources

- **Full API Documentation:** [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **Quick Start Guide:** [API_QUICKSTART.md](API_QUICKSTART.md)
- **Project Structure:** [../../STRUCTURE.md](../STRUCTURE.md)
- **Backend README:** [../../README.md](../../README.md)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-13
