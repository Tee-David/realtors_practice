# 🎯 Frontend Setup Instructions - For Hameedah

**From:** Tee-David (Backend Developer)
**To:** Hameedah (Frontend Developer)

---

## 📨 Backend API is Now Live!

Great news! The backend API has been deployed and is now accessible from the internet.

**API Base URL:** `https://realtors-practice-api.onrender.com/api`

**Test it here:** `https://realtors-practice-api.onrender.com/api/health`

You should see: `{"status": "ok", "timestamp": "...", "version": "2.2"}`

---

## ✅ What You Need To Do

Follow these steps to connect your frontend to the deployed backend:

---

## STEP 1: Update Your Frontend Code

You have two options - **Option A is recommended** for production.

### Option A: Using Environment Variables (Recommended ⭐)

This is the best practice - keeps your code flexible.

**1. Create/Edit `.env.local` in your Next.js project root:**

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
- ✅ Production uses the deployed URL
- ✅ Local development still works with localhost
- ✅ You can change the URL without touching code

---

### Option B: Direct Update (Quick Test)

For quick testing only - not recommended for production.

**1. Find your API client file** (probably `lib/api.ts`)

**2. Change this line:**
```typescript
private baseURL = "http://localhost:5000/api";
```

**To:**
```typescript
private baseURL = "https://realtors-practice-api.onrender.com/api";
```

**Note:** This means you'll need to change it back to `localhost` when developing locally.

---

## STEP 2: Update Vercel Environment Variables

If your frontend is deployed on Vercel:

1. **Go to** your Vercel project dashboard: https://vercel.com/dashboard

2. **Click** on your project

3. **Click** "Settings" (in the top menu)

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

## STEP 3: Commit and Redeploy Your Frontend

**1. Commit your changes:**

```bash
# In your frontend project directory
git add .
git commit -m "Connect to deployed backend API"
git push origin main
```

**2. Vercel will automatically redeploy** (if you have auto-deploy enabled)

Or manually:
- Go to Vercel dashboard
- Click "Deployments"
- Click "Redeploy" on the latest deployment

**3. Wait 2-3 minutes** for deployment to complete

---

## STEP 4: Test Everything

### Test 1: Check API Connection

1. **Open your deployed frontend** (your Vercel URL)

2. **Open browser console** (F12 or right-click → Inspect → Console)

3. **Check for errors:**
   - ❌ If you see CORS errors → Tell Tee-David (CORS should already be enabled)
   - ❌ If you see 404 errors → Check your API URL is correct
   - ✅ If no errors → API is connected!

4. **Check if data loads:**
   - Does the dashboard show stats?
   - Does the sites list load?
   - Can you see property data?

---

### Test 2: Test API Endpoints Directly

Open these URLs in your browser (replace with actual URL):

**Health Check:**
```
https://realtors-practice-api.onrender.com/api/health
```
Should return: `{"status": "ok", ...}`

**List Sites:**
```
https://realtors-practice-api.onrender.com/api/sites
```
Should return: JSON array of 82+ sites

**Get Stats:**
```
https://realtors-practice-api.onrender.com/api/stats
```
Should return: Statistics about the scraper

---

### Test 3: Test Scraper Trigger (If You Have This Feature)

If your frontend has a "Start Scraping" button:

1. Click the button
2. Check if it successfully triggers
3. Check if you can see the GitHub Actions workflow running
4. Check if scraped data appears after completion

---

## 🚨 Important Notes

### 1. First Request Delay (Important!)

**The first API request after 15 minutes of inactivity will take 30-60 seconds.**

This is because Render's free tier "sleeps" the service after inactivity, and the first request "wakes it up."

**What to do:**
- Add a loading spinner for the initial data load
- Show a message like: "Waking up server... (this may take 30 seconds)"
- After the first request, all subsequent requests are fast!

**Example code:**
```typescript
const [isWakingUp, setIsWakingUp] = useState(false);

useEffect(() => {
  setIsWakingUp(true);
  fetch(baseURL + '/health')
    .then(() => {
      setIsWakingUp(false);
      // Now fetch your actual data
    });
}, []);
```

---

### 2. CORS (Cross-Origin Resource Sharing)

**Good news:** CORS is already enabled in the backend using `flask-cors`.

This means your frontend on Vercel can call the backend on Render without issues.

If you see CORS errors:
- Check that you're using the correct URL (with `/api` at the end)
- Make sure you're not using `localhost` in production
- Contact Tee-David if issues persist

---

### 3. Available Endpoints

All **68 API endpoints** are available at: `https://realtors-practice-api.onrender.com/api/...`

**Categories:**
1. Scraping Management (`/api/scrape/...`)
2. Site Configuration (`/api/sites/...`)
3. Data Access (`/api/data/...`)
4. Price Intelligence (`/api/prices/...`)
5. Saved Searches (`/api/searches/...`)
6. GitHub Actions (`/api/github/...`)
7. Firestore Integration (`/api/firestore/...`)
8. Email Notifications (`/api/email/...`)

Check the API documentation in the repo for full details.

---

### 4. GitHub Actions Integration

You can now trigger scraping from your frontend!

**Endpoint:**
```
POST https://realtors-practice-api.onrender.com/api/github/trigger-scrape
```

**Body:**
```json
{
  "page_cap": 20,
  "geocode": 1,
  "sites": ["npc", "jiji"]
}
```

This will trigger a GitHub Actions workflow that:
1. Runs the scraper
2. Processes the data
3. Uploads to Firestore
4. Returns results

---

## 🔧 Troubleshooting

### Issue: "Network Error" or "Failed to Fetch"

**Possible causes:**
1. Backend is sleeping (wait 30 seconds and try again)
2. Wrong API URL (check spelling and `/api` at the end)
3. Backend is down (check with Tee-David)

**Solution:**
- Open the API URL in browser to test: `https://realtors-practice-api.onrender.com/api/health`
- Check browser console for detailed error message
- Verify environment variables in Vercel

---

### Issue: "CORS Error"

**Symptoms:**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Solution:**
- CORS should already be enabled in backend
- Contact Tee-David - he may need to update CORS settings
- Make sure you're using the correct API URL

---

### Issue: Data Not Loading

**Check:**
1. API URL is correct (with `https://` and `/api`)
2. Environment variables are set in Vercel
3. You've redeployed after adding environment variables
4. Backend is responding (test `/api/health` in browser)

**Solution:**
- Check browser console for errors
- Test API endpoints directly in browser
- Verify environment variables: Vercel Settings → Environment Variables

---

### Issue: "401 Unauthorized" or "403 Forbidden"

**If authentication is enabled:**
- Some endpoints might require API keys
- Check with Tee-David if authentication is enabled
- You may need to add API key to your requests

**Currently:** Authentication is likely disabled, so this shouldn't happen.

---

## ✅ Success Checklist

Mark these off as you complete them:

- [ ] Updated `.env.local` with API URL
- [ ] Updated API client code to use environment variable
- [ ] Added environment variable in Vercel
- [ ] Committed and pushed changes
- [ ] Frontend redeployed successfully
- [ ] Opened deployed frontend - no console errors
- [ ] Data loads from backend
- [ ] Tested at least 2 different API endpoints
- [ ] First request delay handled (loading spinner)
- [ ] Everything works smoothly!

---

## 🎉 You're Done When...

1. ✅ Your deployed frontend loads without errors
2. ✅ Data displays correctly from the backend
3. ✅ No CORS errors in console
4. ✅ All features work as expected
5. ✅ You've tested triggering a scrape (if applicable)

**Congratulations! Your frontend is now connected to the live backend!** 🚀

---

## 📞 Need Help?

**If you get stuck:**
1. Check browser console for error messages
2. Test API endpoints directly in browser
3. Review the Troubleshooting section above
4. Contact Tee-David with:
   - What you tried
   - Error messages from console
   - Which step you're stuck on

**For API documentation:**
- See `frontend/API_ENDPOINTS_ACTUAL.md` in the repo
- All endpoints are documented with examples

---

## 📊 Understanding the Complete Flow

After setup, here's how everything works:

```
┌─────────────────────────────┐
│  USER                       │
│  Opens your frontend        │
│  (Vercel)                   │
└────────┬────────────────────┘
         │
         │ 1. User clicks button
         ↓
┌─────────────────────────────┐
│  YOUR FRONTEND              │
│  (Next.js on Vercel)        │
│  - Calls API                │
└────────┬────────────────────┘
         │
         │ 2. API request
         │ (e.g., GET /api/sites)
         ↓
┌─────────────────────────────┐
│  BACKEND API                │
│  (Tee-David's Render)       │
│  - Processes request        │
│  - Returns data OR          │
│  - Triggers GitHub Actions  │
└────────┬────────────────────┘
         │
         │ 3. If scraping triggered
         ↓
┌─────────────────────────────┐
│  GITHUB ACTIONS             │
│  - Runs scraper             │
│  - Uploads to Firestore     │
└─────────────────────────────┘
```

---

## 🎯 Quick Reference

**Backend API URL:** `https://realtors-practice-api.onrender.com/api`

**Environment Variable Name:** `NEXT_PUBLIC_API_URL`

**Health Check:** `https://realtors-practice-api.onrender.com/api/health`

**All Endpoints:** Start with `https://realtors-practice-api.onrender.com/api/...`

---

**Happy coding! Let Tee-David know when everything is working!** 💪
