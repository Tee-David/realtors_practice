# Quick Start Guide - Nigerian Real Estate Scraper

**Version:** 3.2.2
**Last Updated:** December 11, 2025

---

## 🚀 Get Started in 3 Minutes

### 1. Start the API Server

```bash
cd "C:\Users\DELL\Desktop\Dynamic realtors_practice"
python api_server.py
```

Server starts on: `http://localhost:5000`

### 2. Verify It's Working

```bash
curl http://localhost:5000/api/health
```

Expected: `{"status": "healthy", ...}`

### 3. Run a Quick Scrape

```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 2}'
```

---

## 📚 Documentation

### For Developers:
- **README.md** - Project overview and features
- **USER_GUIDE.md** - Complete user guide
- **CHANGELOG.md** - Version history
- **docs/FOR_FRONTEND_DEVELOPER.md** - API integration guide (90 endpoints)

### For System Management:
- **docs/ENV_MANAGEMENT_GUIDE.md** - Environment variables and credential management
- **docs/sessions/2025-12-11/SESSION_REPORT.md** - Latest session details

---

## 🔧 Common Tasks

### Update Credentials (Zero Downtime)

**When GitHub token expires:**
```bash
# 1. Edit .env file
nano .env  # Change GITHUB_TOKEN=new_token

# 2. Reload without restart
curl -X POST http://localhost:5000/api/admin/reload-env

# 3. Verify
curl http://localhost:5000/api/github/workflows
```

### Restart Server

```bash
# Windows Command Prompt:
taskkill /F /IM python.exe
timeout /t 3
cd "C:\Users\DELL\Desktop\Dynamic realtors_practice"
python api_server.py
```

### Run Full Scrape

```bash
# 1. Enable sites (edit config.yaml or use endpoint)
curl -X POST http://localhost:5000/api/sites/npc/enable

# 2. Trigger scrape
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 10}'

# 3. Check status
curl http://localhost:5000/api/scrape/status
```

---

## 🎯 Key Features (v3.2.2)

### API Endpoints: 91 Total
- **Scraping Management** - Start, stop, status, history
- **Site Configuration** - 51 sites, enable/disable, update settings
- **Data Access** - Query properties from Firestore or exports
- **GitHub Actions** - Trigger workflows remotely, get status
- **Firestore Queries** - Dashboard stats, search, filters
- **Hot Reload** - Update credentials without downtime ⭐ NEW

### Core Systems:
- ✅ **Scraping:** 51 Nigerian real estate sites supported
- ✅ **Firestore:** Enterprise schema with 9 categories, 85+ fields
- ✅ **GitHub Actions:** Automated scraping via scrape-production.yml
- ✅ **API Server:** Flask REST API for frontend integration
- ✅ **Hot Reload:** Zero-downtime credential updates

---

## ⚠️ Current Status

**Version:** 3.2.2
**API Server:** ✅ Ready to start
**Firestore:** ✅ Connected and configured
**GitHub Actions:** ✅ Working (scrape-production.yml)
**Documentation:** ✅ Complete and up-to-date

**Action Required:** Restart API server to load latest timezone import fix (commit 8f96712)

---

## 🆘 Troubleshooting

### Server Won't Start

**Check if port 5000 is in use:**
```bash
netstat -ano | findstr :5000
```

**Kill processes using port:**
```bash
taskkill /F /PID <PID_NUMBER>
```

### Credentials Not Loading

**Use hot reload endpoint:**
```bash
curl -X POST http://localhost:5000/api/admin/reload-env
```

### Need Help?

- See **docs/sessions/2025-12-11/SESSION_REPORT.md** for latest changes
- See **docs/ENV_MANAGEMENT_GUIDE.md** for credential management
- See **docs/FOR_FRONTEND_DEVELOPER.md** for API integration

---

## 📞 Support

**Documentation:** See `docs/` directory
**GitHub:** https://github.com/Tee-David/realtors_practice
**Latest Session:** `docs/sessions/2025-12-11/SESSION_REPORT.md`
