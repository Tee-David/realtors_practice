# 🚀 Backend API Deployment Guide

**Problem:** Your frontend developer (Hameedah) can't access the API because it's only running on `localhost:5000`

**Solution:** Deploy the backend API to Render (FREE hosting)

---

## 📋 What You Have (Current Setup)

✅ **GitHub Repository:** `https://github.com/Tee-David/realtors_practice`
✅ **Branch:** `main`
✅ **API Server:** `api_server.py` (ready to deploy)
✅ **GitHub Actions:** Already configured with workflows
✅ **Firebase:** Already set up with credentials
✅ **Local Setup:** Working locally on `localhost:5000`

---

## 📋 What You Need

1. ✅ GitHub account (you have this - Tee-David)
2. ✅ Your GitHub repo: `https://github.com/Tee-David/realtors_practice` (confirmed working)
3. ✅ Firebase credentials file: `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json` (you have this locally)
4. ✅ GitHub Personal Access Token (you'll create this if you don't have one)

---

## 🚀 STEP 1: Commit and Push Your Code

**Note:** I've already added the necessary files (`render.yaml` and updated `requirements.txt`)

```bash
# Navigate to your project
cd "C:\Users\DELL\Desktop\Dynamic realtors_practice"

# Check what files changed
git status

# Add the deployment files
git add render.yaml requirements.txt DEPLOY_BACKEND.md

# Commit changes
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin main
```

**What we're pushing:**
- ✅ `render.yaml` - Render deployment configuration
- ✅ `requirements.txt` - Updated with `gunicorn` for production
- ✅ `DEPLOY_BACKEND.md` - This guide (for future reference)

---

## 🌐 STEP 2: Deploy to Render

### 2.1 Sign Up for Render

1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

### 2.2 Create New Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect account"** (if first time)
3. Find and select your repository: **`Tee-David/realtors_practice`**
4. Click **"Connect"**

**Note:** If you don't see your repo, click "Configure account" and grant Render access to it.

### 2.3 Configure Service

Fill in these settings:

**Basic Settings:**
- **Name:** `real-estate-api` (or any name you want)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** (leave blank)
- **Environment:** `Python 3`

**Build & Deploy:**
- **Build Command:**
  ```
  pip install -r requirements.txt && playwright install chromium
  ```

- **Start Command:**
  ```
  gunicorn api_server:app --bind 0.0.0.0:$PORT --timeout 300
  ```

**Instance Type:**
- Select: **"Free"** (this is important!)

Click **"Create Web Service"**

---

## 🔐 STEP 3: Add Environment Variables

After the service is created, you need to add environment variables:

### 3.1 Navigate to Environment Tab

1. In your Render service dashboard, click **"Environment"** in the left sidebar
2. Click **"Add Environment Variable"**

### 3.2 Add Required Variables

Add each of these one by one:

**1. FIREBASE_CREDENTIALS**
- Key: `FIREBASE_CREDENTIALS`
- Value: Open your `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json` file and copy ALL the contents (the entire JSON)
- Click **"Save Changes"**

**2. GITHUB_TOKEN** (for triggering GitHub Actions)
- Key: `GITHUB_TOKEN`
- Value: Your GitHub Personal Access Token
  - Don't have one? Create it here: https://github.com/settings/tokens
  - Click **"Generate new token (classic)"**
  - Name: `Scraper API Token`
  - Select scopes: `repo` and `workflow`
  - Click **"Generate token"**
  - Copy the token immediately (you won't see it again!)
- Click **"Save Changes"**

**3. GITHUB_OWNER**
- Key: `GITHUB_OWNER`
- Value: `Tee-David` (your GitHub username)
- Click **"Save Changes"**

**4. GITHUB_REPO**
- Key: `GITHUB_REPO`
- Value: `realtors_practice` (your repository name)
- Click **"Save Changes"**

**5. PYTHON_VERSION** (optional but recommended)
- Key: `PYTHON_VERSION`
- Value: `3.11.0`
- Click **"Save Changes"**

### 3.3 Restart Service

After adding all environment variables:
1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait 5-10 minutes for deployment to complete

---

## ✅ STEP 4: Get Your API URL

Once deployment is complete:

1. Look at the top of your Render dashboard
2. You'll see a URL like: `https://real-estate-api.onrender.com`
3. **Copy this URL** - you'll need to give it to your frontend developer!

### 4.1 Test Your Deployed API

Open in your browser:
```
https://real-estate-api.onrender.com/api/health
```

You should see something like:
```json
{
  "status": "ok",
  "timestamp": "2025-11-03T10:00:00",
  "version": "2.2"
}
```

If you see this, your API is live! 🎉

---

## 📨 STEP 5: Share URL with Frontend Developer (Hameedah)

Send Hameedah this message (update the URL with your actual Render URL):

```
Hi Hameedah,

The backend API is now deployed! 🚀

API Base URL: https://real-estate-api.onrender.com/api
(Replace with your actual Render URL)

You can test it by opening:
https://real-estate-api.onrender.com/api/health

Please update the frontend to use this URL instead of localhost:5000

Note: The first request might take 30 seconds (Render free tier sleeps after inactivity)

Let me know once you've updated the frontend!

Thanks!
```

**Copy your actual Render URL from Step 4 above!**

---

## 🔧 STEP 6: What Hameedah (Your Frontend Developer) Needs To Do

**Important:** Hameedah has the frontend code, not you. You just need to give her the deployed API URL.

After you deploy and get your Render URL, Hameedah will need to update HER frontend code:

### What Hameedah Needs to Update (She will do this, not you):

**Option A: Environment Variable (Recommended) - Hameedah does this in HER frontend code:**
```env
# In his Next.js project: .env.local
NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com/api
```

**Option B: Direct Update - David updates HIS `lib/api.ts`:**
```typescript
// Change from:
private baseURL = "http://localhost:5000/api";

// To:
private baseURL = "https://your-render-url.onrender.com/api";
```

### Hameedah's Vercel Deployment

**Hameedah** needs to update her Vercel environment variables:
1. Go to her Vercel project → **Settings** → **Environment Variables**
2. Add: `NEXT_PUBLIC_API_URL` = `https://your-render-url.onrender.com/api`
3. Redeploy her frontend

**You don't do any of this** - you just give Hameedah the URL!

---

## 🐛 Troubleshooting

### Issue: Service won't start

**Check logs:**
1. In Render dashboard, click **"Logs"** tab
2. Look for errors in the deployment logs

**Common fixes:**
- Make sure `requirements.txt` is in root directory
- Verify all environment variables are set correctly
- Check that Firebase credentials are valid JSON

### Issue: API returns 500 errors

**Solution:**
1. Check Render logs for Python errors
2. Verify `FIREBASE_CREDENTIALS` is valid JSON (not a file path)
3. Make sure all required environment variables are set

### Issue: "Service Unavailable" on first request

**This is normal!** Render free tier sleeps after 15 minutes of inactivity.
- First request takes 30-60 seconds to wake up
- Subsequent requests are fast
- Consider using a cron job to ping the API every 10 minutes to keep it awake

### Issue: GitHub Actions not triggering

**Check:**
1. `GITHUB_TOKEN` is set correctly in Render
2. Token has `workflow` scope
3. Verify `GITHUB_OWNER` and `GITHUB_REPO` match your repository

---

## 📊 Monitoring Your Deployment

### Check Service Status
- Render Dashboard → Your service → **"Metrics"** tab
- Shows CPU, Memory, Request count

### View Logs
- Render Dashboard → Your service → **"Logs"** tab
- Real-time logs of your API

### Set Up Notifications
- Render Dashboard → Your service → **"Settings"** → **"Notifications"**
- Get email alerts when deployment fails

---

## 💰 Cost Breakdown

**Render Free Tier:**
- ✅ FREE forever
- ✅ 750 hours/month (31 days = 744 hours)
- ⚠️ Service sleeps after 15 min inactivity
- ⚠️ First request after sleep takes 30 sec

**To avoid sleeping (optional, costs money):**
- Upgrade to paid plan ($7/month)
- OR use a cron job to ping every 10 minutes (still free!)

---

## 🎯 Complete Flow After Deployment

```
USER → Opens Vercel Frontend
  ↓
FRONTEND → Calls Render API
  https://real-estate-api.onrender.com/api/stats
  ↓
RENDER API → Returns data or triggers GitHub Actions
  ↓
GITHUB ACTIONS → Runs scraper, uploads to Firestore
  ↓
FRONTEND → Shows results from Firestore
```

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] All environment variables added
- [ ] Service deployed successfully
- [ ] `/api/health` endpoint responds
- [ ] Frontend developer has new API URL
- [ ] Frontend updated to use new URL
- [ ] Complete flow tested

---

## 🎉 You're Done!

Your backend API is now live and accessible to your frontend developer!

**Your API URL:** `https://real-estate-api.onrender.com/api`

**Next Steps:**
1. Share URL with frontend developer
2. Test a complete scrape from frontend
3. Monitor logs during testing
4. Celebrate! 🎊
