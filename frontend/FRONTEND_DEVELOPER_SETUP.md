# Frontend Developer Setup Guide
## Nigerian Real Estate API Integration

**Last Updated:** 2025-11-03
**Status:** ✅ BACKEND DEPLOYED & LIVE

---

## 🎉 Backend API is Now Live!

The backend has been deployed to Render and is accessible from the internet!

**Backend URL:** `https://realtors-practice-api.onrender.com/api`

**Test it:** https://realtors-practice-api.onrender.com/api/health

---

## Quick Start (3 Steps)

### Step 1: Update Your Frontend Code

**Option A: Using Environment Variables (Recommended)**

Create/edit `.env.local` in your Next.js project:

```env
NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
```

Update your API client file (probably `lib/api.ts`):

```typescript
private baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
```

**Option B: Direct Update (Quick Test)**

In your API client file:

```typescript
// Change from:
private baseURL = "http://localhost:5000/api";

// To:
private baseURL = "https://realtors-practice-api.onrender.com/api";
```

---

### Step 2: Update Vercel Environment Variables

If deployed on Vercel:

1. Go to Vercel → Your project → **Settings** → **Environment Variables**
2. Add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://realtors-practice-api.onrender.com/api`
   - Environments: All (Production, Preview, Development)
3. Save

---

### Step 3: Deploy and Test

```bash
git add .
git commit -m "Connect to deployed backend API"
git push origin your-branch-name
```

Vercel will auto-deploy. Test on your preview deployment first!

---

## ⚠️ Important: First Request Delay

**The first API request after 15 minutes of inactivity takes 30-60 seconds** (Render free tier "wakes up")

Add a loading spinner:

```typescript
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  // First request may be slow
  fetch(baseURL + '/health')
    .then(() => {
      setIsLoading(false);
      // Now load your actual data
    });
}, []);
```

---

## Available API Endpoints

All **68 endpoints** are available at:

`https://realtors-practice-api.onrender.com/api/...`

### Main Endpoints:

**Health Check:**
```
https://realtors-practice-api.onrender.com/api/health
```

**List All Sites:**
```
https://realtors-practice-api.onrender.com/api/sites
```

**Get Statistics:**
```
https://realtors-practice-api.onrender.com/api/stats
```

**Search Properties:**
```
https://realtors-practice-api.onrender.com/api/data/search?location=Lekki
```

**Get Site Data:**
```
https://realtors-practice-api.onrender.com/api/data/sites/{site_key}
```

### Categories:

1. **Scraping Management** - `/api/scrape/...`
2. **Site Configuration** - `/api/sites/...`
3. **Data Access** - `/api/data/...`
4. **GitHub Actions** - `/api/github/...`
5. **Statistics** - `/api/stats/...`

See `API_ENDPOINTS_ACTUAL.md` in this folder for complete list.

---

## Integration Files

Everything you need is in this `frontend/` folder:

- ✅ `types.ts` - TypeScript definitions
- ✅ `api-client.ts` - Complete API client
- ✅ `hooks.tsx` - React hooks with SWR
- ✅ `API_ENDPOINTS_ACTUAL.md` - All 68 endpoints documented

---

## Local Development (Optional)

If you want to run the backend locally for development:

### Step 1: Start Local API Server

```bash
# In the backend repo
cd realtors_practice
pip install -r requirements.txt
python api_server.py
```

### Step 2: Use Local URL

Update your `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## Example Integration

### Basic Usage

```typescript
// Use the deployed backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

// Fetch sites
const response = await fetch(`${API_BASE_URL}/sites`);
const sites = await response.json();
```

### With React Hook

```typescript
import { useProperties } from './hooks';

export default function PropertiesPage() {
  const { properties, total, isLoading } = useProperties();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{total} Properties Available</h1>
      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}
```

---

## Troubleshooting

### Issue: "Network Error" or "Failed to Fetch"

**Solution:**
- Backend may be sleeping (wait 30-60 seconds and retry)
- Test URL directly: https://realtors-practice-api.onrender.com/api/health
- Check browser console for errors

### Issue: "CORS Error"

**Solution:**
- CORS is already enabled in backend
- Make sure you're using `https://` (not `http://`)
- Check that URL ends with `/api`

### Issue: Data Not Loading

**Check:**
1. API URL is correct in `.env.local`
2. Environment variables set in Vercel
3. Frontend redeployed after adding env vars
4. Backend is responding (test health endpoint)

---

## Success Checklist

- [ ] Updated `.env.local` with deployed API URL
- [ ] Updated API client to use environment variable
- [ ] Added environment variable in Vercel
- [ ] Committed and pushed changes
- [ ] Frontend redeployed successfully
- [ ] No console errors
- [ ] Data loads from backend
- [ ] Added loading spinner for first request
- [ ] Everything works!

---

## Next Steps

1. ✅ Backend is deployed and live
2. ✅ Update your frontend code (see Step 1 above)
3. ✅ Test on preview deployment
4. ✅ Merge to main when everything works

---

## Support

For complete API documentation, see:
- `API_ENDPOINTS_ACTUAL.md` - All endpoints
- `types.ts` - TypeScript types
- `api-client.ts` - API client implementation

---

**Backend URL:** https://realtors-practice-api.onrender.com/api

**Ready to integrate!** 🚀
