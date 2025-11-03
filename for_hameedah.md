# 🚀 Complete Deployment Guide: Frontend (Vercel) + Backend (GitHub Actions)

## 🎯 What Your Client Wants

Your client wants to see the **full system working**:

- ✅ Frontend deployed on Vercel (accessible via URL)
- ✅ Backend API running (to handle requests from frontend)
- ✅ GitHub Actions scraping (triggered from frontend)
- ✅ Everything connected and working together

---

## 📋 Current Setup Overview

```
┌─────────────────────────────────────────────────────────┐
│  USER'S BROWSER                                         │
│  https://your-app.vercel.app                           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ API Calls
                  ↓
┌─────────────────────────────────────────────────────────┐
│  BACKEND API (Need to Deploy!)                         │
│  Flask API Server (api_server.py)                      │
│  - Handles requests from frontend                       │
│  - Triggers GitHub Actions                              │
│  - Queries Firestore                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Triggers
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS (Already Set Up!)                      │
│  - Runs scraper                                         │
│  - Collects property data                               │
│  - Uploads to Firestore                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔴 THE MISSING PIECE: Backend API Deployment

**Problem:** Your frontend is on Vercel, but your backend (Flask API) is still only on your local machine!

**Solution:** You need to deploy the backend API server so the frontend can talk to it.

---

## 🚀 Step-by-Step Setup Guide

## STEP 1: Deploy Backend API (Choose One Option)

### Option A: Deploy Backend to Render (Recommended - FREE)

Render is perfect for Flask APIs and has a generous free tier.

#### 1.1 Prepare Your Backend for Deployment

Create a `render.yaml` file in your backend folder:

```bash
cd "C:\Users\Uche\Documents\Real Estate Scrapper\realtors_practice-main"
```

Create `render.yaml`:

```yaml
services:
  - type: web
    name: real-estate-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn api_server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FIREBASE_CREDENTIALS
        sync: false
      - key: GITHUB_TOKEN
        sync: false
      - key: GITHUB_OWNER
        sync: false
      - key: GITHUB_REPO
        sync: false
```

#### 1.2 Add Gunicorn to Requirements

Add to your `requirements.txt`:

```bash
echo gunicorn >> requirements.txt
```

#### 1.3 Deploy to Render

1. Go to https://render.com
2. Sign up/login with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name:** `real-estate-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api_server:app --bind 0.0.0.0:$PORT`
   - **Instance Type:** `Free`
6. Click **"Create Web Service"**
7. Wait for deployment (5-10 minutes)
8. You'll get a URL like: `https://real-estate-api.onrender.com`

#### 1.4 Add Environment Variables in Render

In Render dashboard:

1. Go to your service → **Environment**
2. Add these variables:
   - `FIREBASE_CREDENTIALS` - Your Firebase JSON (from local file)
   - `GITHUB_TOKEN` - Your GitHub Personal Access Token
   - `GITHUB_OWNER` - Your GitHub username
   - `GITHUB_REPO` - Your repo name (e.g., `Scrap`)

---

### Option B: Deploy Backend to Railway (Alternative - FREE)

Railway is another great option similar to Render.

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys
6. Add environment variables in **Variables** tab
7. You'll get a URL like: `https://real-estate-api.up.railway.app`

---

### Option C: Keep Backend Local (For Testing Only)

**Only use this for initial testing!** You'll need to:

1. Run backend locally:

   ```bash
   cd "C:\Users\Uche\Documents\Real Estate Scrapper\realtors_practice-main"
   python api_server.py
   ```

2. Expose it to the internet using ngrok:

   ```bash
   # Install ngrok: https://ngrok.com/download
   ngrok http 5000
   ```

3. You'll get a URL like: `https://abc123.ngrok.io`

**⚠️ Limitation:** This only works while your computer is on and ngrok is running.

---

## STEP 2: Update Frontend to Use Deployed Backend

### 2.1 Update API Base URL in Frontend

Edit `scrapper-ui/lib/api.ts`:

```typescript
// Find this line:
private baseURL = "http://localhost:5000/api";

// Change to your deployed backend URL:
private baseURL = "https://real-estate-api.onrender.com/api"; // Or your Railway/ngrok URL
```

**BETTER APPROACH:** Use environment variables:

Create `scrapper-ui/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://real-estate-api.onrender.com/api
```

Update `scrapper-ui/lib/api.ts`:

```typescript
private baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
```

### 2.2 Add Environment Variable in Vercel

1. Go to your Vercel project dashboard
2. Click **Settings** → **Environment Variables**
3. Add:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://real-estate-api.onrender.com/api` (your backend URL)
   - **Environment:** All (Production, Preview, Development)
4. Click **Save**

### 2.3 Redeploy Frontend

```bash
cd "C:\Users\Uche\Documents\Real Estate Scrapper\scrapper-ui"

# Commit changes
git add .
git commit -m "Update API URL for production"
git push origin main
```

Vercel will automatically redeploy with the new environment variable.

---

## STEP 3: Set Up GitHub Actions Secrets

Your GitHub Actions workflows need secrets to work:

1. Go to your GitHub repository: `https://github.com/UchennaAustine-dev/Scrap`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add each of these:

### Required Secrets:

**1. FIREBASE_CREDENTIALS**

- Click **"New repository secret"**
- Name: `FIREBASE_CREDENTIALS`
- Value: Copy entire content of `realtor-s-practice-firebase-adminsdk-*.json`
- Click **"Add secret"**

**2. GITHUB_TOKEN (for API triggering)**

- Go to: https://github.com/settings/tokens
- Click **"Generate new token (classic)"**
- Name: `Scraper API Token`
- Expiration: `No expiration`
- Scopes: Check `repo` and `workflow`
- Click **"Generate token"**
- Copy the token (you won't see it again!)
- Add as secret:
  - Name: `GH_PAT`
  - Value: Your token

---

## STEP 4: Update Backend Environment Variables

Your backend needs GitHub credentials to trigger workflows.

### For Render:

1. Go to Render dashboard → Your service
2. Click **Environment**
3. Add these variables:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_OWNER=UchennaAustine-dev
   GITHUB_REPO=Scrap
   ```
4. Click **Save**

### For Railway:

1. Go to Railway project → **Variables** tab
2. Add the same variables
3. Railway will auto-restart

---

## STEP 5: Test the Complete Flow

Now test everything working together!

### Test 1: Check Backend API is Live

Open in browser:

```
https://your-backend-url.onrender.com/api/health
```

You should see:

```json
{
  "status": "ok",
  "timestamp": "2025-11-01T10:00:00",
  "version": "1.0.0"
}
```

### Test 2: Test from Frontend (Deployed)

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Go to **Dashboard** page
3. You should see:
   - ✅ Stats loading (proves frontend → backend connection works)
   - ✅ Sites list
   - ✅ Scraper controls

### Test 3: Trigger GitHub Actions from Frontend

1. On your deployed frontend, go to **Dashboard**
2. Find the **Scraper Control** panel
3. Configure:
   - **Max Pages:** 2
   - **Geocoding:** Off
   - **Sites:** Select 1-2 sites
4. Click **"Start Scraping"**
5. You should see:
   - Success message
   - Link to GitHub Actions run
6. Click the link → Opens GitHub Actions workflow running!

### Test 4: View Results

After workflow completes (5-10 minutes):

1. **In GitHub:**

   - Go to Actions tab
   - See completed workflow with green checkmark
   - Download artifacts (cleaned Excel file)

2. **In Frontend:**

   - Go to **Data Explorer** page
   - Search for properties
   - Should show newly scraped data (if Firestore upload enabled)

3. **In Firestore (Optional):**
   - Go to Firebase Console
   - Check `properties` collection
   - Should have new documents

---

## 🎯 Complete Testing Checklist

### ✅ Backend Deployed

- [ ] Backend API deployed (Render/Railway/ngrok)
- [ ] Backend URL is accessible (test /api/health)
- [ ] Environment variables set (GITHUB_TOKEN, FIREBASE_CREDENTIALS)

### ✅ Frontend Updated

- [ ] API base URL updated to deployed backend
- [ ] Environment variable added in Vercel
- [ ] Frontend redeployed to Vercel

### ✅ GitHub Actions Configured

- [ ] FIREBASE_CREDENTIALS secret added
- [ ] GH_PAT secret added (for triggering)
- [ ] Workflow files exist in .github/workflows/

### ✅ Testing Complete

- [ ] Health endpoint responds
- [ ] Frontend loads without errors
- [ ] Can trigger scrape from frontend
- [ ] GitHub Actions workflow runs successfully
- [ ] Can see results in Data Explorer

---

## 🐛 Common Issues & Solutions

### Issue: Frontend can't connect to backend

**Symptoms:** Network errors, CORS errors in console

**Solutions:**

1. Check backend URL in frontend is correct
2. Check backend API is running (visit health endpoint)
3. Check CORS is enabled in backend:
   ```python
   # In api_server.py, should have:
   from flask_cors import CORS
   CORS(app)
   ```

### Issue: "GITHUB_TOKEN not found" when triggering

**Solution:**

1. Check environment variable in Render/Railway
2. Make sure it's named exactly: `GITHUB_TOKEN`
3. Restart backend service after adding

### Issue: GitHub Actions not triggering

**Solutions:**

1. Check GH_PAT secret exists in GitHub repo
2. Verify token has `workflow` scope
3. Check backend logs for API errors

### Issue: Firestore upload fails

**Solutions:**

1. Check FIREBASE_CREDENTIALS secret in GitHub
2. Verify Firebase project ID matches
3. Check Firestore rules allow writes

---

## 📊 Architecture Flow

Here's how everything works together:

```
1. USER → Opens Vercel URL
   https://your-app.vercel.app
   ↓

2. FRONTEND → Calls Backend API
   GET https://backend.onrender.com/api/stats
   ↓

3. BACKEND → Returns data
   { sites: [...], stats: {...} }
   ↓

4. USER → Clicks "Start Scraping"
   ↓

5. FRONTEND → Calls Backend API
   POST https://backend.onrender.com/api/github/trigger-scrape
   { page_cap: 10, sites: ['npc', 'jiji'] }
   ↓

6. BACKEND → Calls GitHub API
   POST https://api.github.com/repos/{owner}/{repo}/dispatches
   { event_type: 'trigger-scrape', client_payload: {...} }
   ↓

7. GITHUB ACTIONS → Starts workflow
   - Install Python
   - Run scraper
   - Upload to Firestore
   ↓

8. FRONTEND → Shows results
   - Query Firestore
   - Display properties
```

---

## 🎉 Final Deployment URLs

After setup, you'll have:

1. **Frontend (Vercel):**

   - `https://your-app.vercel.app`
   - Users access this

2. **Backend API (Render/Railway):**

   - `https://real-estate-api.onrender.com`
   - Frontend calls this

3. **GitHub Actions:**

   - `https://github.com/UchennaAustine-dev/Scrap/actions`
   - Scraper runs here

4. **Firebase/Firestore:**
   - `https://console.firebase.google.com`
   - Data stored here

---

## 📝 Quick Start Commands

```bash
# 1. Deploy Backend to Render (via GitHub)
# - Connect repo to Render
# - Add environment variables
# - Deploy automatically

# 2. Update Frontend
cd "C:\Users\Uche\Documents\Real Estate Scrapper\scrapper-ui"

# Create .env.local
echo "NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api" > .env.local

# Update API client
# Edit lib/api.ts to use environment variable

# Commit and push
git add .
git commit -m "Connect to deployed backend"
git push origin main

# 3. Add environment variable in Vercel dashboard

# 4. Test on deployed URL!
```

---

## 🎯 What Your Client Will See

When you demo to your client:

1. **Open deployed URL:** `https://your-app.vercel.app`
2. **Show Dashboard:** Real-time stats, sites, scraper status
3. **Trigger Scrape:** Click button → Starts GitHub Actions
4. **Show Progress:** Open GitHub Actions tab → See workflow running
5. **Show Results:** After 10 min → Data appears in frontend
6. **Demo Search:** Search properties by location, price, bedrooms

**Client will be impressed by:**

- ✅ Professional deployed application
- ✅ Automated cloud scraping
- ✅ Real-time data updates
- ✅ Full-stack integration

---

## 💡 Pro Tips

1. **Use Render Free Tier:**

   - Perfect for demos
   - Sleeps after 15 min inactivity
   - First request wakes it up (30 sec delay)

2. **Add Loading States:**

   - Show "Waking up server..." if first request is slow
   - Improves user experience

3. **Monitor Logs:**

   - Render: Check logs tab
   - Vercel: Check Functions logs
   - GitHub Actions: Check workflow logs

4. **Set Realistic Expectations:**
   - First scrape takes 10-30 minutes
   - Subsequent scrapes are faster
   - Free tier has some limitations

---

## ✅ You're Ready!

Follow the steps above, and you'll have a fully deployed, production-ready application that impresses your client! 🚀

**Next:** Deploy backend to Render → Update frontend environment variable → Test complete flow → Show client! 🎯
