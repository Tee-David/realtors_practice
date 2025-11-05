# Hey! Ready to Build the Frontend? 👋

Everything you need is ready. This will take you **5 minutes to set up**.

---

## Quick Start (Copy-Paste These Commands)

### Step 1: Get the Latest Code (2 minutes)

```bash
cd "C:\Users\Amidat\Documents\Real Estate Scrapper\realtors_practice-main"
git pull origin main
```

### Step 2: Test Everything Works (1 minute)

```bash
python test_api_startup.py
```

You should see: **`[SUCCESS] ALL TESTS PASSED!`**

###  Step 3: Start the API Server (30 seconds)

```bash
python api_server.py
```

You should see: **`Running on http://127.0.0.1:5000`**

Leave this terminal open!

### Step 4: Test the API (30 seconds)

Open a **new terminal** and run:

```bash
curl http://localhost:5000/api/health
```

You should see: **`{"status":"healthy",...}`**

---

## Now Build Your Frontend! 🚀

### Create Your Own Branch

```bash
git checkout -b frontend-integration
```

Now you can make changes without affecting the main branch!

### Copy Files to Your Next.js Project

```bash
cd your-nextjs-project

# Install SWR (required)
npm install swr

# Copy the frontend integration files
cp -r ../realtors_practice-main/frontend ./lib/api
```

### Start Using It!

```typescript
// In any component - example: app/properties/page.tsx
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading } = useProperties();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{total} Properties Available</h1>
      {properties.map((property) => (
        <div key={property.hash}>
          <h3>{property.title}</h3>
          <p>Price: {property.price_formatted}</p>
          <p>Location: {property.location}</p>
        </div>
      ))}
    </div>
  );
}
```

**That's it! The hook handles everything - fetching, caching, loading states, errors.**

---

## 🆕 NEW: Pause/Resume Scraping (November 2025)

### What's New
The API now supports **pausing and resuming** scraping jobs! This gives users full control over long-running scraping operations.

### Key Features
- **Pause**: Stops scraping after the current batch completes
- **Resume**: Continues from where it left off
- **Status Tracking**: Know when scraping is paused
- **No Data Loss**: All progress is preserved

### New API Endpoints

```
POST /api/scrape/pause   - Pause after current batch
POST /api/scrape/resume  - Resume scraping
GET /api/scrape/status   - Now includes pause status
```

### How to Use in Your Frontend

```typescript
import { useState, useEffect } from 'react';

export default function ScraperControl() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch status periodically
  useEffect(() => {
    const fetchStatus = async () => {
      const res = await fetch('http://localhost:5000/api/scrape/status');
      const data = await res.json();
      setStatus(data);
    };

    const interval = setInterval(fetchStatus, 3000);
    fetchStatus();

    return () => clearInterval(interval);
  }, []);

  const handlePause = async () => {
    setLoading(true);
    await fetch('http://localhost:5000/api/scrape/pause', { method: 'POST' });
    setLoading(false);
  };

  const handleResume = async () => {
    setLoading(true);
    await fetch('http://localhost:5000/api/scrape/resume', { method: 'POST' });
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    await fetch('http://localhost:5000/api/scrape/stop', { method: 'POST' });
    setLoading(false);
  };

  if (!status?.is_running) {
    return <div>No scraping in progress</div>;
  }

  const { current_run } = status;
  const isPaused = current_run?.paused;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className={`px-2 py-1 rounded ${isPaused ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
          {isPaused ? '⏸ PAUSED' : '▶ RUNNING'}
        </span>
        <span>
          Batch {current_run?.batch_info?.current_batch}/{current_run?.batch_info?.total_batches}
        </span>
      </div>

      <div className="flex gap-2">
        {isPaused ? (
          <button
            onClick={handleResume}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded"
          >
            Resume
          </button>
        ) : (
          <button
            onClick={handlePause}
            disabled={loading}
            className="px-4 py-2 bg-yellow-600 text-white rounded"
          >
            Pause
          </button>
        )}

        <button
          onClick={handleStop}
          disabled={loading}
          className="px-4 py-2 bg-red-600 text-white rounded"
        >
          Stop
        </button>
      </div>

      {isPaused && (
        <p className="text-sm text-gray-600">
          Paused at: {new Date(current_run?.paused_at).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
```

### Status Response Example

```json
{
  "is_running": true,
  "current_run": {
    "paused": true,
    "paused_at": "2025-11-05T21:30:15.123456",
    "batch_info": {
      "current_batch": 1,
      "total_batches": 2,
      "batch_status": "completed"
    },
    "progress": {
      "completed_sites": 10,
      "total_sites": 15,
      "pending_sites": 5
    }
  }
}
```

---

## 🆕 Enhanced Progress Tracking

The `/api/scrape/status` endpoint now provides even more detailed information:

### Batch Progress
```json
{
  "batch_info": {
    "total_batches": 2,
    "current_batch": 1,
    "current_batch_sites": ["site1", "site2", ...],
    "batch_status": "in_progress"
  }
}
```

### Timing Estimates
```json
{
  "timing": {
    "elapsed_seconds": 120,
    "estimated_remaining_seconds": 180,
    "average_seconds_per_site": 24.5
  }
}
```

### Complete Progress UI Example

```typescript
export default function ScrapingProgress() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      const res = await fetch('http://localhost:5000/api/scrape/status');
      setStatus(await res.json());
    };

    const interval = setInterval(fetchStatus, 3000);
    fetchStatus();
    return () => clearInterval(interval);
  }, []);

  if (!status?.is_running) return null;

  const { batch_info, progress, timing } = status.current_run;

  return (
    <div className="space-y-4 p-4 border rounded">
      {/* Batch Info */}
      <div>
        <h3 className="font-bold">
          Batch {batch_info.current_batch} of {batch_info.total_batches}
        </h3>
        <p className="text-sm">Status: {batch_info.batch_status}</p>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{
              width: `${(progress.completed_sites / progress.total_sites) * 100}%`
            }}
          />
        </div>
        <p className="text-sm mt-1">
          {progress.completed_sites} of {progress.total_sites} sites completed
        </p>
      </div>

      {/* Time Estimates */}
      {timing?.estimated_remaining_seconds && (
        <p className="text-sm text-gray-600">
          About {Math.floor(timing.estimated_remaining_seconds / 60)} minutes remaining
        </p>
      )}

      {/* Site Details */}
      {batch_info.current_batch_sites && (
        <details className="text-sm">
          <summary className="cursor-pointer text-blue-600">
            Current batch sites ({batch_info.current_batch_sites.length})
          </summary>
          <ul className="mt-2 ml-4 list-disc">
            {batch_info.current_batch_sites.slice(0, 5).map(site => (
              <li key={site}>{site}</li>
            ))}
            {batch_info.current_batch_sites.length > 5 && (
              <li>+{batch_info.current_batch_sites.length - 5} more...</li>
            )}
          </ul>
        </details>
      )}
    </div>
  );
}
```

---

## More Examples

### Simple Scraper Control (Legacy)

```typescript
import { useScrapeStatus } from '@/lib/api/hooks';

export default function SimpleScraperControl() {
  const { isRunning, progress, startScrape, stopScrape } = useScrapeStatus();

  return (
    <div>
      {isRunning ? (
        <>
          <p>Scraping... {progress}%</p>
          <button onClick={stopScrape}>Stop</button>
        </>
      ) : (
        <button onClick={() => startScrape()}>Start Scraping</button>
      )}
    </div>
  );
}
```

### Search Properties

```typescript
import { useState } from 'react';
import { useSearch } from '@/lib/api/hooks';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const { results, total } = useSearch(query, query.length > 2);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search properties..."
      />
      <p>{total} results</p>
      {results.map((p) => <PropertyCard key={p.hash} property={p} />)}
    </div>
  );
}
```

### View Statistics

```typescript
import { useOverviewStats } from '@/lib/api/hooks';

export default function Dashboard() {
  const { stats } = useOverviewStats();

  return (
    <div>
      <h2>Overview</h2>
      <p>Total Listings: {stats?.overview.total_listings}</p>
      <p>Active Sites: {stats?.overview.active_sites}</p>
    </div>
  );
}
```

---

## What You Get

✅ **Complete TypeScript types** - Full autocomplete in VS Code
✅ **67 API endpoints** - All documented and typed
✅ **React hooks** - No need to write fetch/axios code
✅ **Automatic caching** - Fast UI with SWR
✅ **Error handling** - Built-in
✅ **Real-time updates** - Automatic revalidation

---

## Full Documentation

- **`FRONTEND_DEVELOPER_SETUP.md`** - Complete guide with all examples
- **`API_ENDPOINTS_ACTUAL.md`** - All 67 endpoints reference
- **`frontend/types.ts`** - Browse all TypeScript types
- **`frontend/hooks.tsx`** - See all available hooks

---

## Troubleshooting

### Problem: Import error with URLValidator

**Solution:** You have old code. Run:
```bash
git pull origin main
python test_api_startup.py
```

### Problem: "Connection refused"

**Solution:** Start the API server:
```bash
python api_server.py
```

### Problem: No properties showing

**Solution:** Run a scrape first:
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d "{\"sites\":[\"cwlagos\"]}"
```

---

## Need Help?

1. Read `FRONTEND_DEVELOPER_SETUP.md` (has everything!)
2. Run `python test_api_startup.py` to verify setup
3. Check API is running: `curl http://localhost:5000/api/health`

---

## When You're Done

```bash
# Commit your work
git add .
git commit -m "feat: Add property listing page"

# Push your branch
git push origin frontend-integration

# Create a pull request on GitHub!
```

---

**That's it! Start building. Everything is tested and ready to go.** 🎉

Questions? Check `FRONTEND_DEVELOPER_SETUP.md` - it has detailed examples for every use case!
