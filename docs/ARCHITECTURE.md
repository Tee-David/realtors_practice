# 🏗️ Complete System Architecture & Workflow

> **Last Updated:** October 21, 2025
> **Version:** 2.0 (with Firestore integration)

---

## Table of Contents
1. [GitHub Actions Scraping Workflow](#1-github-actions-scraping-workflow)
2. [Data Storage Locations](#2-data-storage-locations)
3. [Complete System Architecture](#3-complete-system-architecture)
4. [Frontend Application Structure](#4-frontend-application-structure)
5. [Typical User Journey](#5-typical-user-journey)
6. [Data Flow Diagram](#6-data-flow-diagram)
7. [Key Advantages](#7-key-advantages)
8. [Production Roadmap](#8-production-roadmap)

---

## 1. GitHub Actions Scraping Workflow

When you trigger a scrape from GitHub Actions (either manually or via API):

### **Step-by-Step Process**

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: TRIGGER (3 Ways)                                    │
├─────────────────────────────────────────────────────────────┤
│ A. Manual: GitHub UI → Actions → "Run workflow"             │
│ B. API: Your frontend calls POST /api/github/trigger-scrape │
│ C. Scheduled: POST /api/schedule/scrape (you set the time)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: GITHUB ACTIONS CLOUD RUNNER                         │
├─────────────────────────────────────────────────────────────┤
│ • Ubuntu server spins up in GitHub's cloud                  │
│ • Installs Python 3.11                                      │
│ • Installs dependencies (requests, playwright, etc.)        │
│ • Installs Chromium browser                                 │
│ • Duration: ~60 minutes max                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: SCRAPING PHASE (main.py)                            │
├─────────────────────────────────────────────────────────────┤
│ • Reads config.yaml (which sites to scrape)                 │
│ • Scrapes 5 sites in parallel (2 workers)                   │
│ • For each property:                                        │
│   - Fetches listing page                                    │
│   - Extracts details (price, location, bedrooms, etc.)      │
│   - Visits detail page for more info                        │
│   - Downloads images (optional)                             │
│   - Geocodes addresses → lat/lng coordinates                │
│ • Output: Raw CSV & XLSX files in exports/sites/           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: CLEANING PHASE (watcher.py --once)                  │
├─────────────────────────────────────────────────────────────┤
│ • Loads all raw exports from exports/sites/                │
│ • For each property:                                        │
│   - Normalizes data (price formats, locations, etc.)        │
│   - Removes duplicates (using hash of key fields)           │
│   - Quality scoring (0-100% based on completeness)          │
│   - Filters out low-quality listings (<30% score)           │
│ • Generates:                                                │
│   ✓ MASTER_CLEANED_WORKBOOK.xlsx (all sites combined)      │
│   ✓ Individual cleaned CSVs per site                        │
│   ✓ Parquet files (fast columnar format)                    │
│   ✓ metadata.json (stats, counts, timestamps)               │
│ • Output: exports/cleaned/                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: FIRESTORE UPLOAD (NEW - Automatic)                  │
├─────────────────────────────────────────────────────────────┤
│ • Reads MASTER_CLEANED_WORKBOOK.xlsx                        │
│ • Uploads each property to Firebase Firestore               │
│ • Uses property hash as document ID (prevents duplicates)   │
│ • Batch uploads (500 documents at a time)                   │
│ • Updates existing records (merge=True)                     │
│ • Result: Data instantly queryable via API                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: ARTIFACT UPLOAD (GitHub Storage - Backup)           │
├─────────────────────────────────────────────────────────────┤
│ • GitHub Actions uploads:                                   │
│   - exports/sites/ → "scraper-exports-raw-{run#}"          │
│   - exports/cleaned/ → "scraper-exports-cleaned-{run#}"     │
│   - logs/ → "scraper-logs-{run#}"                          │
│ • Storage: 30 days for exports, 7 days for logs            │
│ • Download: Via GitHub UI or /api/github/artifact/{id}     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Storage Locations

You have **TWO** data storage systems working together:

### **Primary: Firebase Firestore (Production Database)**
```
Location: Google Cloud (Firebase)
Retention: Permanent until you delete
Access: Instant query via API (no download needed!)
Cost: FREE tier = 50K reads/day, 20K writes/day
Best For: Production, real-time queries, frontend access
Advantage: Query-in-place, no file downloads, always up-to-date
```

**Auto-upload:** After every GitHub Actions scrape run
**Query endpoint:** `POST /api/firestore/query`

**Example Query:**
```javascript
const response = await fetch('/api/firestore/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filters: {
      location: 'Lekki',
      price_max: 50000000,
      bedrooms_min: 3
    },
    limit: 50,
    sort_by: 'price',
    sort_desc: false
  })
});

const data = await response.json();
// Returns: { results: [...], count: 142, filters_applied: {...} }
```

### **Backup: GitHub Artifacts (Temporary Storage)**
```
Location: GitHub Cloud Storage
Retention: 30 days
Access: Download ZIP files via GitHub UI or API
Cost: FREE (included with GitHub)
Best For: Backup, manual downloads, data audits
Limitation: Must download entire file, not queryable
```

**Files stored:**
- `scraper-exports-raw-{run#}.zip` - Raw CSVs/XLSX from each site
- `scraper-exports-cleaned-{run#}.zip` - Cleaned data + master workbook
- `scraper-logs-{run#}.zip` - Debug logs

**Local Backup (Optional):**
- `exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx` - Download from artifacts for local backup

---

## 3. Complete System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │  END USERS       │
                         │  (Property       │
                         │   seekers)       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  FRONTEND APP    │
                         │  (React/Next.js) │
                         │                  │
                         │  • Search UI     │
                         │  • Property cards│
                         │  • Detail pages  │
                         │  • Admin panel   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  API SERVER      │
                         │  (Flask)         │
                         │  api_server.py   │
                         │                  │
                         │  58 Endpoints    │
                         └────────┬─────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
       ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
       │  FIRESTORE   │  │ GITHUB       │  │ SCHEDULED    │
       │  (Primary DB)│  │ ACTIONS      │  │ JOBS         │
       │              │  │              │  │              │
       │ • Properties │  │ • Scraping   │  │ • Manual     │
       │ • Fast query │  │ • Auto upload│  │   scheduling │
       │ • Real-time  │  │ • Artifacts  │  │ • No cron    │
       └──────┬───────┘  └──────┬───────┘  └──────────────┘
              │                 │
              │                 ▼
              │        ┌──────────────────┐
              │        │  SCRAPER ENGINE  │
              │        │  (main.py)       │
              │        │                  │
              │        │  • 82+ sites     │
              │        │  • Parallel      │
              │        │  • Intelligent   │
              │        └────────┬─────────┘
              │                 │
              │                 ▼
              │        ┌──────────────────┐
              │        │  WATCHER         │
              │        │  (watcher.py)    │
              │        │                  │
              │        │  • Cleaning      │
              │        │  • Deduplication │
              │        │  • Quality score │
              └────────┴────────┬─────────┘
                                │
                      Auto-upload to Firestore
```

---

## 4. Frontend Application Structure

Your developer will build this using React/Next.js:

### **Page Structure**

```
┌──────────────────────────────────────────────────────────────┐
│ A. HOME PAGE (/)                                              │
├──────────────────────────────────────────────────────────────┤
│ • Hero section with search bar                               │
│ • Featured properties (latest listings)                      │
│ • Popular locations (Lekki, Ikoyi, VI, etc.)                │
│ • Market insights (total properties, avg price)              │
│                                                              │
│ API Calls:                                                   │
│ • GET /api/properties/recent - Latest 20 listings            │
│ • GET /api/analytics/summary - Market stats                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ B. SEARCH PAGE (/search)                                     │
├──────────────────────────────────────────────────────────────┤
│ • Search bar (natural language)                              │
│ • Filter sidebar:                                            │
│   - Location dropdown                                        │
│   - Price range slider (₦5M - ₦100M)                        │
│   - Bedrooms (1-6+)                                          │
│   - Bathrooms (1-5+)                                         │
│   - Property type (Flat, House, Land, etc.)                  │
│   - Quality filter (High/Medium/Low)                         │
│ • Results grid (property cards)                              │
│ • Pagination (50 per page)                                   │
│ • Sort options (price, date, relevance)                      │
│                                                              │
│ API Calls:                                                   │
│ • POST /api/firestore/query - Main search                   │
│ • POST /api/search/natural - Natural language search        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ C. PROPERTY DETAIL PAGE (/property/:id)                      │
├──────────────────────────────────────────────────────────────┤
│ • Image gallery (lightbox carousel)                          │
│ • Property specs:                                            │
│   - Price (large, prominent)                                 │
│   - Location with map                                        │
│   - Bedrooms, Bathrooms                                      │
│   - Land size, Property type                                 │
│   - Quality score badge                                      │
│ • Description (full text)                                    │
│ • Google Map (with coordinates)                              │
│ • Agent contact:                                             │
│   - Phone number (click to call)                             │
│   - WhatsApp button                                          │
│   - Email inquiry form                                       │
│ • Price history chart (if available)                         │
│ • Similar properties section                                 │
│                                                              │
│ API Calls:                                                   │
│ • GET /api/properties/{id} - Property details               │
│ • GET /api/price-history/{id} - Price tracking              │
│ • POST /api/firestore/query - Similar properties            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ D. ADMIN DASHBOARD (/admin) - Protected Route               │
├──────────────────────────────────────────────────────────────┤
│ • Scraper Control Panel:                                     │
│   - "Run Scraper Now" button                                 │
│   - Site selection (checkboxes)                              │
│   - Pages per site slider                                    │
│   - Enable/disable geocoding                                 │
│ • Schedule Scraper:                                          │
│   - Date/time picker                                         │
│   - "Schedule Scrape" button                                 │
│   - List of scheduled jobs (with cancel buttons)             │
│ • Recent Scrapes:                                            │
│   - Workflow runs table (status, time, results)              │
│   - Download artifacts button                                │
│ • Export Tools:                                              │
│   - Format dropdown (Excel/CSV/JSON)                         │
│   - Filter selection                                         │
│   - "Generate Export" button                                 │
│ • Site Health Dashboard:                                     │
│   - Sites table (name, status, last scrape, listings)        │
│   - Health indicators (green/yellow/red)                     │
│                                                              │
│ API Calls:                                                   │
│ • POST /api/github/trigger-scrape - Run scraper             │
│ • GET /api/github/workflow-runs - Scrape history            │
│ • POST /api/schedule/scrape - Schedule future scrape        │
│ • GET /api/schedule/jobs - List scheduled jobs              │
│ • POST /api/export/generate - Create export                 │
│ • GET /api/sites - Site health                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ E. USER DASHBOARD (/dashboard) - Optional Future Feature    │
├──────────────────────────────────────────────────────────────┤
│ • Saved searches (with email alerts)                         │
│ • Favorite properties (wishlist)                             │
│ • Price drop alerts                                          │
│ • Market insights (trends for saved locations)               │
│                                                              │
│ API Calls:                                                   │
│ • GET /api/searches - User's saved searches                 │
│ • POST /api/searches - Save new search                      │
│ • GET /api/price-drops - Recent price drops                 │
│ • GET /api/market-trends - Market insights                  │
└──────────────────────────────────────────────────────────────┘
```

### **Technical Stack (Recommended)**

```javascript
// Frontend Framework
- Next.js 14+ (React framework with SSR)
- TypeScript (type safety)

// UI Components
- Tailwind CSS (styling)
- shadcn/ui or Chakra UI (component library)
- React Query (API state management)

// Maps & Visualizations
- Google Maps API (property locations)
- Recharts or Chart.js (price history charts)

// State Management
- Zustand or React Context (global state)
- React Query (server state)

// Forms
- React Hook Form (search filters)
- Zod (validation)
```

---

## 5. Typical User Journey

### **Scenario: User searching for property**

```
┌─────────────────────────────────────────────────────────────┐
│ USER JOURNEY: Finding a Property in Lekki                   │
└─────────────────────────────────────────────────────────────┘

STEP 1: User arrives on homepage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User action: Opens www.yoursite.com
Frontend: Loads homepage with featured properties
API call: GET /api/properties/recent
Response: { properties: [...20 recent listings...] }

STEP 2: User searches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User action: Types "3 bedroom flat in Lekki under 30 million"
Frontend: Sends query to API
API call: POST /api/search/natural
Request: { query: "3 bedroom flat in Lekki under 30 million" }

Backend: Parses query → Converts to structured filters
Internal: POST /api/firestore/query
Request: {
  filters: {
    location: "Lekki",
    bedrooms_min: 3,
    property_type: "Flat",
    price_max: 30000000
  },
  limit: 50
}

Firestore: Queries properties collection
Response: {
  results: [
    {
      id: "abc123",
      title: "Luxury 3BR Flat Lekki Phase 1",
      price: 25000000,
      location: "Lekki Phase 1",
      bedrooms: 3,
      bathrooms: 3,
      images: ["url1", "url2"],
      quality_score: 0.85
    },
    ... 141 more properties
  ],
  count: 142,
  filters_applied: {...}
}

STEP 3: User browses results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend: Displays 142 results in grid (50 per page)
User action: Applies additional filter (4 bedrooms minimum)
API call: POST /api/firestore/query (with updated filters)
Response: { results: [...], count: 87 }

STEP 4: User clicks on property
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User action: Clicks on "Luxury 3BR Flat Lekki Phase 1"
Frontend: Navigates to /property/abc123
API call: GET /api/properties/abc123
Response: {
  // Full property details
  title: "Luxury 3BR Flat Lekki Phase 1",
  price: 25000000,
  location: "Lekki Phase 1, Lagos",
  coordinates: { lat: 6.4474, lng: 3.4701 },
  bedrooms: 3,
  bathrooms: 3,
  description: "Fully furnished...",
  images: ["url1", "url2", "url3"],
  agent_name: "John Doe",
  agent_phone: "+234 801 234 5678",
  listing_url: "https://...",
  quality_score: 0.85
}

STEP 5: User views property details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend: Shows image gallery, map, specs, contact info
User action: Clicks "WhatsApp Agent" button
Frontend: Opens WhatsApp with pre-filled message:
  "Hi, I'm interested in the 3BR Flat in Lekki Phase 1 (₦25M)"
```

---

## 6. Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                         │
└──────────────────────────────────────────────────────────────┘

STAGE 1: SCRAPING (GitHub Actions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You → Trigger → GitHub Actions → Scraper runs
                                      ↓
                            ┌─────────────────┐
                            │ exports/sites/  │
                            │                 │
                            │ npc/            │
                            │ ├── 2025-10-21.csv
                            │ └── 2025-10-21.xlsx
                            │                 │
                            │ jiji/           │
                            │ ├── 2025-10-21.csv
                            │ └── 2025-10-21.xlsx
                            │                 │
                            │ propertypro/    │
                            │ ├── 2025-10-21.csv
                            │ └── 2025-10-21.xlsx
                            └─────────────────┘

STAGE 2: CLEANING (Watcher)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                      ↓
                       Watcher.py reads all files
                                      ↓
                  Deduplicates → Normalizes → Scores
                                      ↓
                            ┌─────────────────┐
                            │ exports/cleaned/│
                            │                 │
                            │ MASTER_CLEANED_WORKBOOK.xlsx
                            │ npc_cleaned.csv │
                            │ jiji_cleaned.csv│
                            │ propertypro_cleaned.csv
                            │ metadata.json   │
                            └─────────────────┘

STAGE 3: FIRESTORE UPLOAD (Automatic)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                      ↓
                  upload_to_firestore.py runs
                                      ↓
                  Reads MASTER_CLEANED_WORKBOOK.xlsx
                                      ↓
                  Batch uploads (500 at a time)
                                      ↓
                            ┌─────────────────┐
                            │ FIRESTORE DB    │
                            │                 │
                            │ Collection:     │
                            │ "properties"    │
                            │                 │
                            │ 474 documents   │
                            │ (auto-updated)  │
                            └─────────────────┘

STAGE 4: BACKUP TO GITHUB (Artifacts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                      ↓
                  GitHub Actions uploads files
                                      ↓
                            ┌─────────────────┐
                            │ GITHUB ARTIFACTS│
                            │                 │
                            │ scraper-exports-raw-{run#}.zip
                            │ scraper-exports-cleaned-{run#}.zip
                            │ scraper-logs-{run#}.zip
                            │                 │
                            │ (30 day retention)
                            └─────────────────┘

STAGE 5: FRONTEND ACCESS (Real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User → Frontend → API Server → Firestore
                                    ↓
                          Query results in <1s
                                    ↓
                          JSON response to frontend
                                    ↓
                          Display to user
```

---

## 7. Key Advantages

### **For You (Business Owner)**
✅ **Zero server maintenance** - GitHub Actions handles scraping infrastructure
✅ **Unlimited scalability** - Add new sites via config.yaml (no code changes)
✅ **Cost-effective** - GitHub Actions FREE (2000 min/month), Firestore FREE tier
✅ **Fully automated** - Schedule scrapes, auto-upload to Firestore, no manual work
✅ **Multiple backups** - Firestore (permanent) + GitHub Artifacts (30 days)
✅ **Quality controlled** - Automatic deduplication and quality filtering

### **For Your Developer**
✅ **Simple REST API** - 58 well-documented endpoints
✅ **No database setup** - Firestore handles everything
✅ **Lightning fast** - Firestore queries return in milliseconds
✅ **Flexible filtering** - Location, price, beds, type, quality score, etc.
✅ **Real-time data** - Auto-updated after every scrape
✅ **Type safety** - TypeScript types provided in documentation

### **For End Users**
✅ **Fast search** - Results in <1 second
✅ **Accurate data** - Deduplicated and quality-filtered
✅ **Rich details** - Images, maps, agent contact
✅ **Price tracking** - Historical price data for properties
✅ **Always fresh** - Data updated automatically

---

## 8. Production Roadmap

### **Phase 1: Foundation (COMPLETED ✅)**
- [x] Scraper engine with 82+ sites
- [x] Automatic cleaning and deduplication
- [x] REST API with 58 endpoints
- [x] Firestore integration
- [x] GitHub Actions automation
- [x] Scheduled scraping capability
- [x] Advanced export system

### **Phase 2: Frontend Development (CURRENT 🔄)**
- [ ] Homepage with search bar
- [ ] Search results page with filters
- [ ] Property detail pages
- [ ] Admin dashboard for scraping control
- [ ] Responsive design (mobile-friendly)

### **Phase 3: Enhanced Features (NEXT 📅)**
- [ ] User authentication (login/signup)
- [ ] Saved searches with email alerts
- [ ] Favorite properties (wishlist)
- [ ] Price drop notifications
- [ ] Market insights and trends

### **Phase 4: Advanced Features (FUTURE 🚀)**
- [ ] Machine learning price predictions
- [ ] Image recognition for property features
- [ ] Mobile app (React Native)
- [ ] Agent portal
- [ ] Payment integration (premium features)

---

## 9. Configuration Files

### **GitHub Actions Workflow**
File: `.github/workflows/scrape.yml`
- Triggers: Manual, API, Scheduled
- Runs: Scraper → Watcher → Firestore Upload → Artifact Upload
- Duration: ~60 minutes max
- Cost: FREE

### **Firestore Credentials**
File: `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json`
- Location: Project root (gitignored)
- Used by: upload_to_firestore.py
- Required: Set in GitHub Secrets for Actions

### **API Server**
File: `api_server.py`
- Port: 5000 (default)
- Endpoints: 58 total
- CORS: Enabled for frontend
- Documentation: `docs/FRONTEND_INTEGRATION_GUIDE.md`

---

## 10. Performance Metrics

### **Scraping Performance**
- Sites scraped: 5 in parallel (82+ configured)
- Listings per run: ~500 properties
- Success rate: 80% (4/5 sites typically successful)
- Duration: 60-90 minutes per run
- Frequency: As often as you trigger (no automatic cron)

### **Firestore Performance**
- Query speed: <100ms average
- Storage: ~1KB per property document
- Current data: 474 properties
- Free tier limits: 50K reads/day, 20K writes/day
- Cost at 10K users/day: Still FREE

### **API Performance**
- Response time: <200ms average
- Concurrent requests: Unlimited (Flask + Firestore)
- Uptime: 99.9% (Firestore SLA)

---

## 11. Security & Privacy

### **Data Protection**
- Firebase credentials: Gitignored, stored in GitHub Secrets
- API server: No authentication required (read-only public data)
- Admin endpoints: Add authentication before production
- User data: No PII stored (only property data)

### **Compliance**
- Robots.txt: Respected by all scrapers
- Rate limiting: Built-in per-site delays
- User-agent: Identifies scraper clearly
- Terms of service: Review target sites' ToS

---

## 12. Monitoring & Debugging

### **GitHub Actions Logs**
- View: GitHub → Actions → Select workflow run
- Contains: Scraping logs, error messages, summaries
- Retention: 90 days

### **Local Logs**
- File: `logs/scraper.log`
- Contains: Detailed scraping activity
- Downloaded: Via GitHub Artifacts

### **Error Tracking**
- File: `exports/cleaned/errors.log`
- Contains: Cleaning errors, failed files
- Review: After each scrape run

---

## 13. Cost Breakdown (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| GitHub Actions | Free | $0 (2000 min/month) |
| Firebase Firestore | Free | $0 (within limits) |
| Google Maps API | Free | $0 ($200 credit/month) |
| Domain Name | Varies | ~$12/year |
| Hosting (Vercel) | Free | $0 (for frontend) |
| VPS (for API) | Optional | $5-10/month |
| **Total** | | **~$0-10/month** |

---

## 14. Support & Documentation

- **Architecture:** This file (`docs/ARCHITECTURE.md`)
- **API Reference:** `docs/FRONTEND_INTEGRATION_GUIDE.md`
- **Quick Start:** `README.md`
- **Postman Collection:** `docs/POSTMAN_COLLECTION.json`
- **Branch Protection:** `docs/BRANCH_PROTECTION.md`

---

**Questions?** Review the documentation files or check GitHub Issues for troubleshooting.

**Happy Building! 🚀**
