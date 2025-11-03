# 🚀 Frontend Setup - Connect to Deployed Backend

---

## ✅ Good News - Backend is Live!

The backend API has been successfully deployed and is now accessible from the internet!

**Backend URL:** `https://realtors-practice-api.onrender.com/api`

**Test it here:** https://realtors-practice-api.onrender.com/api/health
(You should see: `{"status": "ok", "timestamp": "...", "version": "2.2"}`)

---

## 🎯 What You Need To Do

You need to update your frontend to connect to the deployed backend instead of `localhost:5000`.

This is a **3-step process** that takes about 15 minutes.

---

## STEP 1: Update Your Frontend Code (5 min)

### Option A: Environment Variables (Recommended ⭐)

**1. Create or edit `.env.local` in your Next.js project root:**

```env
NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
```

**2. Update your API client file** (probably `lib/api.ts` or `lib/api-client.ts`):

Find this line:
```typescript
private baseURL = "http://localhost:5000/api";
```

Change it to:
```typescript
private baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
```

This way:
- ✅ Production uses the deployed backend
- ✅ Local development still works with localhost
- ✅ You can change the URL without modifying code

---

### Option B: Direct Update (Quick Test Only)

**Not recommended for production**, but good for quick testing:

In your API client file (probably `lib/api.ts`), change:

```typescript
// From:
private baseURL = "http://localhost:5000/api";

// To:
private baseURL = "https://realtors-practice-api.onrender.com/api";
```

**Note:** You'll need to change it back to `localhost` when developing locally.

---

## STEP 2: Update Vercel Environment Variables (5 min)

If your frontend is deployed on Vercel:

1. **Go to your Vercel project dashboard:** https://vercel.com/dashboard

2. **Click** on your project

3. **Click** "Settings" (top menu)

4. **Click** "Environment Variables" (left sidebar)

5. **Click** "Add New" button

6. **Fill in:**
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://realtors-practice-api.onrender.com/api`
   - **Environments:** Check all three:
     - ☑ Production
     - ☑ Preview
     - ☑ Development

7. **Click** "Save"

---

## STEP 3: Deploy Your Frontend (5 min)

**Commit and push your changes:**

```bash
# In your frontend project directory
git add .
git commit -m "Connect to deployed backend API"
git push origin main
```

**Vercel will automatically redeploy** (if auto-deploy is enabled)

Or manually redeploy:
- Go to Vercel dashboard
- Click "Deployments"
- Click "Redeploy" on the latest deployment

**Wait 2-3 minutes** for deployment to complete.

---

## ✅ Test Everything Works

### Test 1: Check Your Deployed Frontend

1. **Open your deployed frontend** (your Vercel URL)

2. **Open browser console** (Press F12 → Console tab)

3. **Check for errors:**
   - ❌ CORS errors? (Let me know - should be enabled)
   - ❌ 404 errors? (Check your API URL is correct)
   - ✅ No errors? Great! API is connected!

4. **Verify data loads:**
   - Dashboard shows stats? ✅
   - Sites list loads? ✅
   - Property data appears? ✅

---

### Test 2: Test API Endpoints Directly

Open these URLs in your browser to verify the backend is responding:

**Health Check:**
```
https://realtors-practice-api.onrender.com/api/health
```
Should return: `{"status": "ok", ...}`

**List All Sites:**
```
https://realtors-practice-api.onrender.com/api/sites
```
Should return: JSON array of 82+ configured sites

**Get Statistics:**
```
https://realtors-practice-api.onrender.com/api/stats
```
Should return: Scraper statistics

---

## ⚠️ Important: First Request Delay

**The first API request after 15 minutes of inactivity will take 30-60 seconds.**

This is because Render's free tier "sleeps" after inactivity to save resources. The first request "wakes it up."

**What to do:**
- Add a loading spinner for initial data load
- Show a message: "Loading... (This may take a moment)"
- After the first request, all subsequent requests are fast!

**Example code:**
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

## 📚 Available API Endpoints

All **68 endpoints** are now available at:

`https://realtors-practice-api.onrender.com/api/...`

**Main Categories:**

1. **Scraping Management**
   - `POST /api/scrape/start` - Start scraping
   - `GET /api/scrape/status` - Get status
   - `POST /api/scrape/stop` - Stop scraping

2. **Site Configuration**
   - `GET /api/sites` - List all sites
   - `GET /api/sites/{site_key}` - Get site details
   - `PUT /api/sites/{site_key}` - Update site config

3. **Data Access**
   - `GET /api/data/sites/{site_key}` - Get scraped data
   - `GET /api/data/search` - Search properties
   - `GET /api/data/latest` - Get latest data

4. **GitHub Actions**
   - `POST /api/github/trigger-scrape` - Trigger scraping workflow
   - `GET /api/github/status` - Check workflow status

5. **Statistics**
   - `GET /api/stats` - Get overview statistics
   - `GET /api/stats/sites/{site_key}` - Site-specific stats

See the repo documentation for complete API reference.

---

## 🔧 Troubleshooting

### Issue: "Network Error" or "Failed to Fetch"

**Possible causes:**
1. Backend is sleeping (wait 30-60 seconds and retry)
2. Wrong API URL (check spelling)
3. CORS issue (should be pre-configured)

**Solution:**
- Test the URL directly in browser: https://realtors-practice-api.onrender.com/api/health
- Check browser console for detailed error messages
- Verify environment variables in Vercel

---

### Issue: "CORS Error"

**Symptoms:**
```
Access to fetch has been blocked by CORS policy
```

**Solution:**
- CORS is already enabled in the backend
- Make sure you're using the correct URL with `https://` (not `http://`)
- Let me know if issue persists

---

### Issue: Data Not Loading

**Check:**
1. API URL is correct (includes `https://` and ends with `/api`)
2. Environment variables set correctly in Vercel
3. Frontend redeployed after adding environment variables
4. Backend is responding (test health endpoint in browser)

**Solution:**
- Check browser console for errors
- Test API endpoints directly in browser
- Verify Vercel environment variables: Settings → Environment Variables

---

## 📊 How It All Works Together

After setup, here's the complete flow:

```
┌─────────────────────────────┐
│  USER                       │
│  Opens your frontend        │
│  (Vercel)                   │
└────────┬────────────────────┘
         │
         │ 1. Clicks button/loads page
         ↓
┌─────────────────────────────┐
│  YOUR FRONTEND              │
│  (Next.js on Vercel)        │
│  Makes API calls            │
└────────┬────────────────────┘
         │
         │ 2. API request
         │ (e.g., GET /api/sites)
         ↓
┌─────────────────────────────┐
│  BACKEND API                │
│  (Deployed on Render)       │
│  https://realtors-practice  │
│  -api.onrender.com/api      │
│  Processes & returns data   │
└────────┬────────────────────┘
         │
         │ 3. If scraping triggered
         ↓
┌─────────────────────────────┐
│  GITHUB ACTIONS             │
│  Runs scraper workflow      │
│  Uploads to Firestore       │
└─────────────────────────────┘
```

---

## ✅ Success Checklist

Mark these off as you complete them:

- [ ] Updated `.env.local` with API URL
- [ ] Updated API client code to use environment variable
- [ ] Added environment variable in Vercel
- [ ] Committed and pushed changes
- [ ] Frontend redeployed successfully
- [ ] Opened deployed frontend - no console errors
- [ ] Data loads from backend correctly
- [ ] Tested at least 2-3 API endpoints
- [ ] Loading spinner added for first request
- [ ] Everything works smoothly!

---

## 🎯 Quick Reference

**Backend API Base URL:**
```
https://realtors-practice-api.onrender.com/api
```

**Environment Variable Name:**
```
NEXT_PUBLIC_API_URL
```

**Health Check URL:**
```
https://realtors-practice-api.onrender.com/api/health
```

**All Endpoints Start With:**
```
https://realtors-practice-api.onrender.com/api/...
```

---

## 📞 Need Help?

If you get stuck:

1. Check browser console for error messages
2. Test API endpoints directly in browser
3. Review the troubleshooting section above
4. Let me know if you get stuck - send me:
   - What you tried
   - Error messages from console
   - Which step you're stuck on

---

## 🎉 You're Done When...

1. ✅ Your deployed frontend loads without errors
2. ✅ Data displays correctly from the backend
3. ✅ No CORS errors in browser console
4. ✅ All features work as expected
5. ✅ You can trigger scraping (if that feature exists)

**Let me know when everything is working!** 🚀

---

**For more detailed information, see:** `FOR_HAMEEDAH_FRONTEND_SETUP.md` in the repo.

**Happy coding!** 💪
