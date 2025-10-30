# Frontend Integration Package

Complete TypeScript/React integration for Nigerian Real Estate API

---

## 🚀 Quick Start

**New to this project? Start here:** → [**README_FOR_DEVELOPER.md**](./README_FOR_DEVELOPER.md)

This is a **5-minute quick start guide** that gets you up and running immediately.

---

## 📁 Files in This Folder

### Integration Files (Copy these to your project)

| File | Description | Lines |
|------|-------------|-------|
| **`types.ts`** | Complete TypeScript type definitions for all API responses | 400+ |
| **`api-client.ts`** | Fully typed API client with all 67 endpoints | 550+ |
| **`hooks.tsx`** | Ready-to-use React hooks with SWR integration | 400+ |

### Documentation Files

| File | Purpose |
|------|---------|
| **`README_FOR_DEVELOPER.md`** | ⭐ **START HERE** - 5-minute quick start guide |
| **`FRONTEND_DEVELOPER_SETUP.md`** | Complete setup guide with detailed examples |
| **`API_ENDPOINTS_ACTUAL.md`** | Reference for all 67 API endpoints |
| **`SEND_TO_DEVELOPER.md`** | Quick troubleshooting guide |

---

## 📦 What You Get

✅ **Zero Configuration** - Just copy and use
✅ **Full TypeScript Support** - Autocomplete everywhere
✅ **React Hooks** - No need to write fetch/axios code
✅ **Automatic Caching** - SWR handles everything
✅ **67 API Endpoints** - All typed and documented
✅ **Real Examples** - Every use case covered
✅ **Error Handling** - Built-in

---

## 🎯 Usage

### 1. Copy Files to Your Next.js Project

```bash
# In your Next.js project
cd your-nextjs-project

# Install SWR (required dependency)
npm install swr

# Copy the integration files
cp types.ts api-client.ts hooks.tsx ./lib/api/
```

### 2. Start Using Immediately

```typescript
// app/properties/page.tsx
import { useProperties } from '@/lib/api/hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading } = useProperties();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{total} Properties</h1>
      {properties.map(p => (
        <div key={p.hash}>
          <h3>{p.title}</h3>
          <p>{p.price_formatted}</p>
          <p>{p.location}</p>
        </div>
      ))}
    </div>
  );
}
```

That's it! The hook handles fetching, caching, loading states, and errors automatically.

---

## 📚 Documentation

Read in this order:

1. **`README_FOR_DEVELOPER.md`** ← START HERE (5-minute setup)
2. **`FRONTEND_DEVELOPER_SETUP.md`** ← Complete guide with all examples
3. **`API_ENDPOINTS_ACTUAL.md`** ← All endpoints reference

---

## 🔥 Common Examples

### Control Scraping

```typescript
import { useScrapeStatus } from '@/lib/api/hooks';

const { isRunning, progress, startScrape, stopScrape } = useScrapeStatus();

// Start scraping
await startScrape({ sites: ['npc'], max_pages: 10 });

// Monitor progress
{isRunning && <ProgressBar value={progress} />}
```

### Search Properties

```typescript
import { useSearch } from '@/lib/api/hooks';

const [query, setQuery] = useState('');
const { results, total } = useSearch(query, query.length > 2);
```

### View Statistics

```typescript
import { useOverviewStats } from '@/lib/api/hooks';

const { stats } = useOverviewStats();
// stats.overview.total_listings
// stats.overview.active_sites
```

### Manage Sites

```typescript
import { useSites } from '@/lib/api/hooks';

const { sites, toggleSite } = useSites();
await toggleSite('npc', true); // Enable site
```

---

## 🧪 Backend Requirements

The backend API server must be running:

```bash
# In the realtors_practice directory
python api_server.py
```

Expected output:
```
INFO - Starting API server on port 5000
Running on http://127.0.0.1:5000
```

---

## ✅ Verification

To verify everything is set up correctly:

```bash
# In the realtors_practice directory
python test_api_startup.py
```

You should see: `[SUCCESS] ALL TESTS PASSED!`

---

## 🆘 Troubleshooting

### Issue: Import errors

**Solution:** Pull latest code
```bash
git pull origin main
```

### Issue: "Connection refused"

**Solution:** Start the API server
```bash
python api_server.py
```

### Issue: Empty data

**Solution:** Run a scrape first
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites":["cwlagos"]}'
```

---

## 📖 Full API Reference

All 67 endpoints organized by category:

- Health & Monitoring (5 endpoints)
- Scraping Operations (4 endpoints)
- Sites Management (6 endpoints)
- Data Access (4 endpoints)
- Statistics (3 endpoints)
- Logs (3 endpoints)
- URL Validation (2 endpoints)
- Location Filtering (3 endpoints)
- Property Queries (2 endpoints)
- Rate Limiting (2 endpoints)
- Price Intelligence (4 endpoints)
- Natural Language Search (2 endpoints)
- Saved Searches (5 endpoints)
- Duplicate Detection (1 endpoint)
- Quality Scoring (1 endpoint)
- Firestore Integration (3 endpoints)
- Export Management (3 endpoints)
- GitHub Actions (7 endpoints)
- Scheduling (4 endpoints)
- Email Notifications (7 endpoints)

See `API_ENDPOINTS_ACTUAL.md` for complete details.

---

## 🚦 Getting Started Checklist

- [ ] Read `README_FOR_DEVELOPER.md`
- [ ] Start API server: `python api_server.py`
- [ ] Test API: `curl http://localhost:5000/api/health`
- [ ] Install SWR: `npm install swr`
- [ ] Copy files: `cp types.ts api-client.ts hooks.tsx your-project/lib/api/`
- [ ] Create first component with `useProperties()`
- [ ] Start building!

---

**Everything is tested and ready. Start with `README_FOR_DEVELOPER.md` and you'll be building in 5 minutes!** 🎉
