# Quick Start Guide - Local Services
**Purpose**: Start all services locally for development/testing
**Time**: 2 minutes

---

## 🚀 Start All Services (2 Terminals Required)

### Terminal 1: Backend API Server

```bash
cd C:\Users\DELL\Desktop\Dynamic realtors_practice\backend
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
python api_server.py
```

**Expected Output**:
```
 * Serving Flask app 'api_server'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Verify**: Open browser → http://localhost:5000/api/health
Should see: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

---

### Terminal 2: Frontend (Next.js)

```bash
cd C:\Users\DELL\Desktop\Dynamic realtors_practice\frontend
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 16.0.10
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 2.3s
```

**Verify**: Open browser → http://localhost:3000
Should see: Login page with "Continue as Guest" button

---

## ✅ Quick Health Check

Once both services are running:

1. **Frontend**: http://localhost:3000
   - Click "Continue as Guest"
   - Should see API Integration Test page
   - All 4 tests should show green ✅

2. **Backend API**: http://localhost:5000/api/health
   - Should return JSON: `{"status":"healthy",...}`

3. **Firestore Data**: http://localhost:5000/api/firestore/dashboard
   - Should return: `{"data":{"by_listing_type":{"rent":42,"sale":294,...}}}`

---

## 🛑 Stop All Services

**Terminal 1 (Backend)**: Press `CTRL+C`
**Terminal 2 (Frontend)**: Press `CTRL+C`

---

## 🔧 Troubleshooting

### Error: "Python not found"
```bash
# Install Python 3.11+
# Download from: https://www.python.org/downloads/
```

### Error: "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### Error: "npm not found"
```bash
# Install Node.js 18+
# Download from: https://nodejs.org/
```

### Error: "FIREBASE_SERVICE_ACCOUNT not found"
```bash
# Make sure file exists:
dir backend\realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json

# If missing, check backend/ directory
```

### Frontend shows "ERR_CONNECTION_REFUSED"
```
Cause: Backend not running
Fix: Start Terminal 1 (Backend API Server)
```

### Frontend stuck on "Loading..."
```
Cause: Backend is slow to start (first time)
Fix: Wait 30 seconds, then refresh browser
```

---

## 📝 One-Line Startup (PowerShell)

Create `start_services.ps1`:

```powershell
# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\DELL\Desktop\Dynamic realtors_practice\backend; `$env:FIREBASE_SERVICE_ACCOUNT='realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'; python api_server.py"

# Wait 5 seconds for backend to start
Start-Sleep -Seconds 5

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\DELL\Desktop\Dynamic realtors_practice\frontend; npm run dev"

# Open browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
```

**Usage**:
```powershell
.\start_services.ps1
```

---

## 🎯 What You Should See

### Backend Terminal:
```
[2025-12-25 09:40:15] INFO - Firestore initialized from: realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
[2025-12-25 09:40:15] INFO - Connected to Firebase project: realtor-s-practice
[2025-12-25 09:40:15] INFO - Firestore collection: properties
 * Serving Flask app 'api_server'
 * Running on http://127.0.0.1:5000
```

### Frontend Terminal:
```
  ▲ Next.js 16.0.10
  - Local:        http://localhost:3000

 ✓ Ready in 2.3s
 ○ Compiling / ...
 ✓ Compiled / in 800ms
```

### Browser (http://localhost:3000):
- Login page loads ✅
- Click "Continue as Guest" ✅
- API tests all green ✅
- Dashboard shows 366 properties ✅

---

## 💡 Production vs Development

### Development (Current Setup):
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000/api`
- Database: Firestore (production data)

### Production (When Ready):
- Frontend: https://your-frontend.vercel.app (deploy Next.js to Vercel)
- Backend: https://realtors-practice-api.onrender.com/api (already deployed ✅)
- Database: Firestore (same)

**To switch to production API**:
Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
```

---

**That's it!** Both services should be running now. 🎉

**Need help?** See `FINAL_SUMMARY.md` for comprehensive documentation.
