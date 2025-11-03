# 🎯 Deploy Backend API - Complete Walkthrough

**Your Goal:** Deploy your backend API to Render so Hameedah can connect her frontend to it

**Time Required:** 30 minutes (first time), 10 minutes (if you've done it before)

**Cost:** $0.00 (100% FREE)

---

## 📋 Understanding the Situation

### What You Currently Have:
- ✅ Backend API running on your computer (`localhost:5000`)
- ✅ GitHub repo: `https://github.com/Tee-David/realtors_practice`
- ✅ All backend code working locally
- ✅ Firebase credentials on your machine

### The Problem:
- ❌ Hameedah's frontend (on Vercel) can't reach `localhost:5000`
- ❌ `localhost` only works on YOUR computer
- ❌ You need the backend accessible from the internet

### The Solution:
- ✅ Deploy backend to Render (cloud hosting)
- ✅ Get a public URL like: `https://your-api.onrender.com`
- ✅ Hameedah updates her frontend to use that URL
- ✅ Everything works live!

---

## 🚀 PART 1: Deploy Backend to Render (Detailed Walkthrough)

### Step 1.1: Push Your Code to GitHub (Already Done!)

Your code is already on GitHub. If you've made any changes, push them:

```bash
cd "C:\Users\DELL\Desktop\Dynamic realtors_practice"
git add .
git commit -m "Prepare for deployment"
git push origin main
```

---

### Step 1.2: Sign Up for Render

1. **Open your browser** and go to: https://render.com

2. **Click "Get Started for Free"** (big button in the middle)

3. **Sign up with GitHub:**
   - Click the **"GitHub"** button (don't use email)
   - You'll be redirected to GitHub
   - Click **"Authorize Render"**
   - You might need to enter your GitHub password

4. **You're now on the Render dashboard!**
   - It should say "Welcome" at the top
   - You'll see a mostly empty page with a big "New +" button

---

### Step 1.3: Create a New Web Service

1. **Click the "New +" button** (top right of the dashboard)

2. **Select "Web Service"** from the dropdown menu

3. **Connect Your Repository:**

   **First time?** You'll see "Connect account" button:
   - Click **"Connect account"**
   - A popup will appear
   - Click **"Install Render"** on GitHub
   - Select: **"Only select repositories"**
   - Choose: **`Tee-David/realtors_practice`**
   - Click **"Install"**
   - Wait a few seconds...

   **Now you'll see a list of repositories:**
   - Find: **`Tee-David/realtors_practice`**
   - Click the **"Connect"** button next to it

---

### Step 1.4: Configure Your Service (IMPORTANT!)

You'll now see a form with many fields. Fill them in **EXACTLY** as shown:

**Name:**
```
realtors-practice-api
```
(You can choose any name, but use lowercase with hyphens)

**Region:**
- Select **"Oregon (US West)"** or **"Frankfurt (EU Central)"** (whichever is closer to you)

**Branch:**
```
main
```

**Root Directory:**
- **Leave this BLANK** (empty)

**Runtime:**
- Should automatically detect **"Python 3"**
- If not, select it from dropdown

**Build Command:**
```
pip install -r requirements.txt && playwright install chromium
```
(Copy this EXACTLY - it installs your Python packages and Playwright browser)

**Start Command:**
```
gunicorn api_server:app --bind 0.0.0.0:$PORT --timeout 300
```
(Copy this EXACTLY - it starts your Flask API)

**Instance Type:**
- Select **"Free"** (very important!)
- Should show: "$0/month"

---

### Step 1.5: Add Environment Variables (CRITICAL!)

**Scroll down** to the "Environment Variables" section. You'll see "Add Environment Variable" button.

#### Variable 1: FIREBASE_CREDENTIALS

1. **Click "Add Environment Variable"**

2. **Key:** (type this)
   ```
   FIREBASE_CREDENTIALS
   ```

3. **Value:** (follow these steps carefully)
   - On your computer, find this file:
     ```
     C:\Users\DELL\Desktop\Dynamic realtors_practice\realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
     ```
   - **Right-click** the file → **Open with** → **Notepad**
   - **Select ALL** the text (Ctrl+A)
   - **Copy** it (Ctrl+C)
   - **Go back to Render** in your browser
   - **Click in the "Value" field**
   - **Paste** (Ctrl+V)
   - You should see a big blob of JSON text starting with `{"type": "service_account",...`

4. **Don't click anything yet!** Keep adding more variables.

---

#### Variable 2: GITHUB_TOKEN

This allows your API to trigger GitHub Actions workflows.

**First, create the token:**

1. **Open a new tab** and go to: https://github.com/settings/tokens

2. **Click "Generate new token"** → **"Generate new token (classic)"**

3. **Fill in:**
   - **Note:** `Scraper API Token`
   - **Expiration:** `No expiration` (select from dropdown)
   - **Select scopes:** Check these two boxes:
     - ☑ **repo** (Full control of private repositories)
     - ☑ **workflow** (Update GitHub Action workflows)

4. **Scroll down** and click **"Generate token"**

5. **COPY THE TOKEN IMMEDIATELY!**
   - It will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **You'll never see it again!** Copy it now!
   - Paste it in Notepad temporarily

**Now add it to Render:**

1. **Go back to Render tab**

2. **Click "Add Environment Variable"** again

3. **Key:**
   ```
   GITHUB_TOKEN
   ```

4. **Value:**
   - Paste the token you just created (from Notepad)

---

#### Variable 3: GITHUB_OWNER

1. **Click "Add Environment Variable"** again

2. **Key:**
   ```
   GITHUB_OWNER
   ```

3. **Value:**
   ```
   Tee-David
   ```
   (This is your GitHub username)

---

#### Variable 4: GITHUB_REPO

1. **Click "Add Environment Variable"** again

2. **Key:**
   ```
   GITHUB_REPO
   ```

3. **Value:**
   ```
   realtors_practice
   ```
   (This is your repository name)

---

### Step 1.6: Create the Service!

1. **Scroll to the bottom** of the page

2. **Click "Create Web Service"** (big button)

3. **Wait for deployment:**
   - You'll see a black box with scrolling logs
   - This is Render installing Python, packages, and deploying your API
   - **This will take 5-10 minutes** (be patient!)
   - Watch the logs scroll by (it's installing everything)

4. **Look for these signs of success:**
   - Logs will show: `Starting Gunicorn...`
   - At the top, status will change from "Building" → "Live" (with green dot)
   - You'll see: `Your service is live 🎉`

---

### Step 1.7: Get Your API URL

Once deployment is complete:

1. **Look at the top** of the page

2. You'll see your service URL, something like:
   ```
   https://realtors-practice-api.onrender.com
   ```

3. **Copy this URL** (click the copy icon next to it, or select and copy)

4. **Save it somewhere!** You'll need it in the next step.

---

## ✅ PART 2: Test Your Deployed API

### Step 2.1: Test the Health Endpoint

1. **Open a new browser tab**

2. **Type your URL** + `/api/health`:
   ```
   https://your-actual-url.onrender.com/api/health
   ```
   (Replace `your-actual-url` with your real Render URL)

3. **Press Enter**

4. **You should see:**
   ```json
   {
     "status": "ok",
     "timestamp": "2025-11-03T16:30:00",
     "version": "2.2"
   }
   ```

5. **If you see this:** ✅ **SUCCESS! Your API is live!**

6. **If you see an error:**
   - Wait 30 seconds and try again (Render free tier "wakes up" slowly)
   - If still error, go to Render dashboard → Click "Logs" tab → Check for errors

---

### Step 2.2: Test Another Endpoint (Optional)

Try listing all sites:

```
https://your-actual-url.onrender.com/api/sites
```

You should see a JSON list of all 82+ configured sites.

---

## 📨 PART 3: Send URL to Hameedah

Now that your backend is live, Hameedah needs to know the URL.

### Step 3.1: Compose Message

Send Hameedah this message (copy and customize):

```
Hi Hameedah,

Great news! The backend API is now deployed and live! 🚀

Here's what you need:

API Base URL: https://[YOUR-ACTUAL-URL].onrender.com/api

Test it here to confirm it works:
https://[YOUR-ACTUAL-URL].onrender.com/api/health

You should see: {"status": "ok", ...}

Now you can update your frontend code to use this URL instead of localhost:5000

Important Notes:
1. The first request after 15 minutes of inactivity takes 30-60 seconds (Render free tier "wakes up")
2. After that, all requests are fast
3. All 68 API endpoints are available
4. GitHub Actions can now be triggered from your frontend

Let me know if you have any issues connecting!
```

**Replace `[YOUR-ACTUAL-URL]` with your real Render URL!**

---

## 📋 PART 4: What Hameedah Needs To Do

Here's what you can tell Hameedah to do on her end:

---

### **Instructions for Hameedah** (Send her this)

```
Hi Hameedah,

The backend is now live! Here's what you need to do to connect your frontend:

---

STEP 1: Update Your Frontend Code

Option A: Using Environment Variables (Recommended)

1. In your Next.js project, create/edit `.env.local`:

   NEXT_PUBLIC_API_URL=https://[THE-URL-I-SENT-YOU]/api

2. In your API client file (probably `lib/api.ts` or similar), update:

   const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

Option B: Direct Update (Quick Test)

1. Find your API client file (probably `lib/api.ts`)

2. Change this line:
   private baseURL = "http://localhost:5000/api";

   To:
   private baseURL = "https://[THE-URL-I-SENT-YOU]/api";

---

STEP 2: Update Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Click "Settings" → "Environment Variables"
3. Click "Add New"
4. Key: NEXT_PUBLIC_API_URL
5. Value: https://[THE-URL-I-SENT-YOU]/api
6. Environment: Select "Production", "Preview", "Development"
7. Click "Save"

---

STEP 3: Redeploy Your Frontend

1. Commit your changes:
   git add .
   git commit -m "Update API URL to deployed backend"
   git push origin main

2. Vercel will automatically redeploy (or click "Redeploy" in Vercel dashboard)

3. Wait 2-3 minutes for deployment

---

STEP 4: Test

1. Open your deployed frontend URL
2. Check if data loads from the backend
3. Try triggering a scrape (if you have that feature)
4. Check browser console for any errors

---

IMPORTANT NOTES:

1. First Request Delay: The first API request after 15 min of inactivity will take 30-60 seconds. This is normal for Render's free tier. Show a loading spinner!

2. CORS: Already enabled in the backend (flask-cors), so no CORS errors

3. All 68 endpoints are available at: https://[THE-URL-I-SENT-YOU]/api/...

4. GitHub Actions: You can now trigger scraping from your frontend using the /api/github/trigger-scrape endpoint

Let me know if you hit any issues!
```

---

## 🔧 Troubleshooting

### Issue: Render deployment fails

**Check the logs:**
1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for red error messages

**Common fixes:**
- Make sure all 4 environment variables are set correctly
- Check that `FIREBASE_CREDENTIALS` is valid JSON (not a file path)
- Verify Build Command is correct

---

### Issue: API returns 500 errors

**Check:**
1. Render logs for Python errors
2. Verify `FIREBASE_CREDENTIALS` is complete JSON
3. Make sure you didn't accidentally include extra spaces in environment variables

---

### Issue: First request takes forever

**This is normal!**
- Render free tier "sleeps" after 15 minutes of inactivity
- First request "wakes it up" - takes 30-60 seconds
- After that, requests are fast
- Tell Hameedah to add a loading spinner for the first request

---

### Issue: Can't find my Render URL

1. Go to https://dashboard.render.com
2. Click on your service name
3. Look at the top - URL is displayed there
4. Format: `https://your-service-name.onrender.com`

---

## 📊 Understanding the Complete Flow

After you're both done:

```
┌─────────────────────────────────┐
│  USER'S BROWSER                 │
│  Opens Hameedah's Frontend      │
│  https://her-app.vercel.app     │
└──────────┬──────────────────────┘
           │
           │ Makes API Call
           │ (e.g., GET /api/sites)
           ↓
┌─────────────────────────────────┐
│  YOUR BACKEND (Render)          │
│  https://your.onrender.com/api  │  ← You deployed this!
│  - Handles the request          │
│  - Returns data OR              │
│  - Triggers GitHub Actions      │
└──────────┬──────────────────────┘
           │
           │ If scraping triggered
           │ Calls GitHub API
           ↓
┌─────────────────────────────────┐
│  GITHUB ACTIONS                 │
│  Your repo workflows            │
│  - Runs scraper                 │
│  - Uploads to Firestore         │
└─────────────────────────────────┘
```

---

## 🔐 Security Notes

### What's Safe:
- ✅ All secrets are in Render environment variables (not in code)
- ✅ Firebase credentials never committed to GitHub
- ✅ GitHub tokens are hidden
- ✅ Hameedah can't see your environment variables (even as collaborator)

### What Hameedah Can See:
- ✅ Your code (she's a collaborator)
- ✅ Config files
- ✅ API endpoints
- ❌ Environment variables (hidden)
- ❌ Firebase credentials (hidden)
- ❌ Secrets (hidden)

This is correct and secure! ✅

---

## 💰 Cost Breakdown

**Render Free Tier:**
- FREE forever
- 750 hours/month (31 days × 24 hours = 744 hours)
- Sleeps after 15 min inactivity
- 512 MB RAM
- Shared CPU

**GitHub Actions:**
- 2000 minutes/month FREE
- More than enough for your scraping needs

**Total Cost: $0.00/month** 🎉

---

## ✅ Success Checklist

Mark these off as you complete them:

- [ ] Signed up for Render with GitHub
- [ ] Created Web Service
- [ ] Connected `Tee-David/realtors_practice` repository
- [ ] Configured Build and Start commands correctly
- [ ] Added all 4 environment variables
- [ ] Deployment completed successfully (shows "Live")
- [ ] Tested `/api/health` endpoint - returns JSON
- [ ] Copied Render URL
- [ ] Sent URL and instructions to Hameedah
- [ ] Hameedah confirmed she can connect

---

## 🎉 You're Done When...

1. ✅ Render dashboard shows green "Live" status
2. ✅ `/api/health` returns: `{"status": "ok", ...}`
3. ✅ Hameedah says: "Frontend connected successfully!"

**Congratulations! Your backend is live!** 🚀

---

## 📞 Need Help?

If you get stuck at any step:
1. Check the Troubleshooting section above
2. Look at Render logs (Logs tab in dashboard)
3. Test locally first: `python api_server.py`
4. Check that all environment variables are set correctly

---

**Ready?** Start with Part 1, Step 1.2 above! Take your time, follow each step carefully, and you'll have it deployed in 30 minutes! 💪
