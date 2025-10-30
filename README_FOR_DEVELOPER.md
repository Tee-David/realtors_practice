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

## More Examples

### Control Scraping

```typescript
import { useScrapeStatus } from '@/lib/api/hooks';

export default function ScraperControl() {
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
