# Frontend ↔ Backend Flow (Scraper Control & Data)

This document explains how the Next.js frontend talks to the Flask backend for the Real Estate Scraper, end to end. It covers configuration, key components, hooks, API contract, and troubleshooting.

## Overview

- Frontend: Next.js 15 (React 19), TypeScript, Tailwind, shadcn/ui, Sonner toasts
- Backend: Flask API on port 5000 with CORS enabled
- Data flow: UI components → hooks (`useApi`, `usePolling`) → client (`lib/api.ts`) → Flask routes → helpers → filesystem

## Configure the API Base URL

The frontend resolves the backend base URL in this order:

1. `process.env.NEXT_PUBLIC_API_URL` (build-time)
2. `window.ENV.NEXT_PUBLIC_API_URL` (runtime injection)
3. Fallback: `http://localhost:5000`

Set it during development by creating `.env.local` in `scrapper-ui`:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Or inject at runtime (optional):

```html
<script>
  window.ENV = { NEXT_PUBLIC_API_URL: "http://localhost:5000" };
</script>
```

## Core Client and Hooks

- `lib/api.ts`
  - Adds a 15s timeout (AbortController) to avoid indefinite loading
  - Exposes typed groups: `scrapeApi`, `sitesApi`, `dataApi`, `logsApi`, `statsApi`
- `lib/hooks/useApi.ts`
  - `useApi`: fetch once, with stable refs and `refetch()`
  - `usePolling`: periodic polling with mount/enable guards

## Key Screens and Components

- `app/page.tsx` – simple in-memory auth and navigation
- `components/scraper/scraper-control.tsx` – status banner + Run/Stop + sub-panels
- `components/scraper/site-configuration.tsx` – lists sites with enable/disable, edit, logs
- `components/scraper/run-console.tsx` – tabs: Current, Errors, History with polling

## Backend Endpoints (contract)

- Health: `GET /api/health` → `{ status, timestamp, version }`
- Sites: `GET /api/sites` → `{ total, enabled, disabled, sites: Site[] }`
- Site: `GET /api/sites/:site_key` → site config
- Toggle: `PATCH /api/sites/:site_key/toggle`
- Start: `POST /api/scrape/start` → `{ success, current_run }`
- Status: `GET /api/scrape/status` → `{ is_running, current_run, last_run, site_metadata }`
- Stop: `POST /api/scrape/stop`
- History: `GET /api/scrape/history?limit=N` → `{ history: [...] }`
- Logs: `GET /api/logs?limit=N` → `{ total, logs: LogEntry[] }`
- Errors: `GET /api/logs/errors?limit=N` → `{ total, logs: LogEntry[] }`
- Site Logs: `GET /api/logs/site/:site_key?limit=N`
- Data files: `GET /api/data/sites`
- Site data: `GET /api/data/sites/:site_key?limit&offset&source`
- Master data: `GET /api/data/master?limit&site`

## How the UI Works

1. Scraper status
   - `scraper-control.tsx` polls `GET /api/scrape/status` every 5s
   - Shows a blue banner when `is_running === true`
2. Site list
   - `site-configuration.tsx` calls `GET /api/sites` on mount
   - On error, shows retry actions; `Refresh` button calls `refetch()`
3. Run/Stop
   - Button posts to `POST /api/scrape/start` or `POST /api/scrape/stop`
   - Selected sites, max_pages, geocoding are sent only if provided
4. Logs console
   - `run-console.tsx` polls:
     - Current logs: `GET /api/logs?limit=50`
     - Error logs: `GET /api/logs/errors?limit=20`
   - Polls every 5–10s when running; 15–30s when idle so logs still appear
   - History tab uses `GET /api/scrape/history?limit=10` on demand via `refetch()`
5. Site logs modal
   - `GET /api/logs/site/:site_key?limit=200` while open

## Start Everything

- Backend (Flask):

```bash
# From realtors_practice
python api_server.py
```

- Frontend (Next.js):

```bash
# From scrapper-ui
npm install
npm run dev
```

Open http://localhost:3000, log in, go to Scraper Control.

## Typical Run Flow

- Select one or more sites in Site Configuration
- Click "Run Scraper Now"
- Watch status banner turn on and logs populate in Run Console
- Use Refresh if needed; History tab shows recent runs

## Troubleshooting

- Sites list stuck on "Loading sites..."
  - Ensure backend is running at `NEXT_PUBLIC_API_URL`
  - We added a 15s timeout to prevent indefinite waits; use Refresh/Retry
  - Check browser console for CORS or network errors
- No logs visible while running
  - Logs appear when `logs/scraper.log` updates; some scrapers may be quiet at first
  - The console now polls even when idle (slower) so you still see recent logs
- Start button says already running
  - Status shows running; use Stop to abort, then Start again
- Data not found for a site
  - The backend returns an empty dataset with a helpful message until data exists

## Types Used in Frontend

See `lib/types.ts` for `Site`, `ScrapeStatus`, `LogEntry`, and API response shapes.

## Where to Change Things

- Base URL: `.env.local` or `window.ENV`
- Timeouts: `lib/api.ts` (default 15s)
- Poll intervals: `run-console.tsx` and `usePolling`
- Enable/disable sites, edit configs: buttons in Site Configuration call `/api/sites` endpoints

## Postman

Use the collection in `realtors_practice/docs/POSTMAN_COLLECTION.json` and the guide in `realtors_practice/docs/API_TESTING_GUIDE.md` to test every endpoint outside the UI.

## Browser Console Debugging

The frontend now includes comprehensive console logging at every layer. Open browser DevTools (F12) and watch the Console tab to track:

### Low-Level API Logs

Every network request logs:

- `[API] GET/POST/PUT/PATCH/DELETE <url>` with request body (if any)
- Success: `[API] ... succeeded:` with response data
- Errors: `[API] ... failed:` with status/error details
- Timeouts: `[API] ... timed out after 15000ms`

### Hook-Level Logs

- `[useApi] Starting request...` → `[useApi] Request succeeded:` or `[useApi] Request failed:`
- `[useApiMutation] Starting mutation with params:` → success or failure
- `[usePolling] Starting polling (interval: Xms, enabled: true)` → per-poll logs with count → `[usePolling] Stopping polling (total polls: N)`

### Component Logs

Each component logs mount/update and key operations:

- **ScraperControl**: mount, scraper status, run/stop actions
- **SiteConfiguration**: mount, sites data (count, loading, error), toggle/selection changes
- **RunConsole**: mount, active tab, logs data (current/error/history counts), refresh
- **DashboardOverview**: mount, stats/sites/status data, refresh
- **SiteStatistics**: mount, stats count
- **TrendsChart**: mount, data points count
- **DataExplorer**: mount, state (data source, site, search term, properties count), loadData calls, search/site/master data results

### How to Use Console Logs

1. **Tracking a failed request:**

   - Look for `[API] ... failed:` to see the exact endpoint and error.
   - Check `[useApi] Request failed:` for hook-level context.
   - Component logs show which screen triggered the request.

2. **Debugging infinite loading:**

   - Search for `[usePolling] Starting polling` to confirm polling is active.
   - Count poll logs (`[usePolling] Poll #N`) to see if requests are repeating endlessly.
   - Check if `[API] ... succeeded:` confirms data is arriving.

3. **Verifying data flow:**

   - Watch component mount logs (e.g., `[SiteConfiguration] Component mounted/updated`).
   - Follow state logs (e.g., `[SiteConfiguration] Sites data: { loading, error, sitesCount }`).
   - Confirm `[API]` logs show the expected endpoint was called.

4. **Checking scraper status:**

   - `[ScraperControl] Scraper status: { isRunning, scrapeStatus }` shows current state.
   - `[RunConsole] Logs data:` shows log counts (current, error, history).

5. **Filtering logs:**
   - Use DevTools Console filter: type `[API]` to see only network calls, `[usePolling]` for polling, or component names like `[DataExplorer]`.

### Example Console Output

```
[DataExplorer] Component mounted/updated
[DataExplorer] State: { dataSource: "master", currentSite: "", searchTerm: "", propertiesCount: 0, totalRecords: 0, loading: false }
[useApi] Starting request...
[API] GET http://localhost:5000/api/data/sites
[API] GET http://localhost:5000/api/data/sites succeeded: { raw_sites: [...], cleaned_sites: [...] }
[useApi] Request succeeded: { raw_sites: [...], cleaned_sites: [...] }
[DataExplorer] loadData called, dataSource: master, currentSite: , searchTerm:
[DataExplorer] Loading master data
[API] GET http://localhost:5000/api/data/master?limit=100
[API] GET http://localhost:5000/api/data/master?limit=100 succeeded: { total_sheets: 2, sheets: [...] }
[DataExplorer] Master data: { total_sheets: 2, sheets: [...] }
```

This makes it easy to trace exactly what's happening at every step!
