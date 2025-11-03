# 🚀 Quick Deploy Guide (3 Steps Only!)

**Your Task:** Deploy backend API so Hameedah can connect her frontend

**Time:** 20 minutes

---

## Step 1: Push Code to GitHub (2 min)

```bash
cd "C:\Users\DELL\Desktop\Dynamic realtors_practice"
git add .
git commit -m "Add backend deployment configuration"
git push origin main
```

---

## Step 2: Deploy to Render (15 min)

1. **Go to:** https://render.com
2. **Sign up** with GitHub (Tee-David account)
3. **Click:** "New +" → "Web Service"
4. **Select repo:** `Tee-David/realtors_practice`
5. **Configure:**
   - Name: `realtors-practice-api`
   - Build: `pip install -r requirements.txt && playwright install chromium`
   - Start: `gunicorn api_server:app --bind 0.0.0.0:$PORT --timeout 300`
   - Instance: **Free**

6. **Add Environment Variables** (click "Environment" tab):

   **FIREBASE_CREDENTIALS:**
   - Open: `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json`
   - Copy entire JSON content
   - Paste as value

   **GITHUB_TOKEN:**
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scopes: `repo` + `workflow`
   - Copy token and paste as value

   **GITHUB_OWNER:** `Tee-David`

   **GITHUB_REPO:** `realtors_practice`

7. **Click:** "Deploy"
8. **Wait:** 5-10 minutes

---

## Step 3: Test & Share URL (3 min)

1. **Copy your Render URL** (looks like: `https://realtors-practice-api.onrender.com`)

2. **Test it:**
   Open in browser: `https://your-url.onrender.com/api/health`

   Should see: `{"status": "ok", ...}`

3. **Send to Hameedah:**
   ```
   Hi Hameedah,

   Backend is live! 🚀

   API URL: https://your-url.onrender.com/api

   Test: https://your-url.onrender.com/api/health

   Update your frontend to use this URL.

   Note: First request takes 30 sec (free tier wakes up)
   ```

---

## ✅ Done!

- ✅ Backend deployed
- ✅ URL sent to Hameedah
- ✅ She updates her frontend
- ✅ Everything works!

---

**Need more details?** See `DEPLOY_BACKEND.md`

**Troubleshooting?** Check Render logs in dashboard
