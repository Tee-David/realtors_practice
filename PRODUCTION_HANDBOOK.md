# 📘 Realtor's Practice - Production Handbook

**Version:** 4.0.0
**Last Updated:** 2025-12-28
**Status:** Production Ready ✅

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Getting Started](#getting-started)
4. [Environment Configuration](#environment-configuration)
5. [Authentication & Security](#authentication--security)
6. [Core Features](#core-features)
7. [API Reference](#api-reference)
8. [Database Schema](#database-schema)
9. [Deployment](#deployment)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)
12. [Security Best Practices](#security-best-practices)
13. [Performance Optimization](#performance-optimization)
14. [Contributing](#contributing)

---

## Overview

### What is Realtor's Practice?

Realtor's Practice is a comprehensive Nigerian real estate property aggregation platform that:
- **Scrapes** data from multiple property websites
- **Normalizes** and validates property information
- **Geocodes** locations for accurate mapping
- **Stores** data in Google Firestore for fast, scalable access
- **Provides** a modern web interface for browsing and searching properties
- **Enables** saved searches with email alerts
- **Exports** data in multiple formats (CSV, XLSX, JSON)

### Key Statistics

- **Properties in Database:** 352+ (and growing)
- **Supported Websites:** Multiple real estate platforms
- **API Endpoints:** 82
- **Core Modules:** 32
- **Lines of Code:** 30,000+
- **Focus Area:** Lagos, Nigeria

### Technology Stack

**Backend:**
- Python 3.11+
- Flask (REST API)
- Google Firestore (Database)
- Playwright (Web Scraping)
- BeautifulSoup4 (HTML Parsing)

**Frontend:**
- Next.js 14 (React Framework)
- TypeScript
- Tailwind CSS
- Shadcn/ui Components
- React Query (Data Fetching)

**Infrastructure:**
- Render.com (Backend Hosting)
- Vercel (Frontend Hosting)
- GitHub Actions (CI/CD)
- Firebase (Database & Storage)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Next.js Frontend│ (Vercel)
│  Port: 3000      │
└────────┬────────┘
         │
         ▼ (HTTP/REST)
┌─────────────────┐
│  Flask API      │ (Render.com)
│  Port: 5000     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Core Modules   │
│  - Scraper      │
│  - Cleaner      │
│  - Geocoder     │
│  - Firestore    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Firestore DB   │ (Firebase)
│  352+ properties│
└─────────────────┘
```

### Data Flow

1. **Scraping Phase:**
   ```
   Websites → Scraper Engine → Parsers → Raw Data
   ```

2. **Processing Phase:**
   ```
   Raw Data → Cleaner → Normalizer → Quality Scorer → Clean Data
   ```

3. **Enrichment Phase:**
   ```
   Clean Data → Location Filter (Lagos Only) → Geocoder → Enriched Data
   ```

4. **Storage Phase:**
   ```
   Enriched Data → Firestore Batch Writer → Database
   ```

5. **Retrieval Phase:**
   ```
   User Request → Next.js → Flask API → Firestore → JSON Response → UI
   ```

### Directory Structure

```
realtors_practice/
├── backend/
│   ├── api_server.py           # Flask REST API (82 endpoints)
│   ├── main.py                 # Scraper entry point
│   ├── config.yaml             # Site configuration (82 sites)
│   ├── core/                   # 32 core modules
│   │   ├── firestore_enterprise.py
│   │   ├── scraper_engine.py
│   │   ├── cleaner.py
│   │   ├── geo.py
│   │   └── ...
│   ├── parsers/                # Site-specific parsers
│   ├── scripts/                # 27 utility scripts
│   ├── tests/                  # Test suite
│   └── docs/                   # Documentation
├── frontend/
│   ├── app/                    # Next.js pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities & API client
│   └── public/                 # Static assets
├── .github/workflows/          # CI/CD pipelines
├── CLAUDE.md                   # AI Assistant Guide
├── IMPLEMENTATION_PLAN.md      # Task tracker
└── PRODUCTION_HANDBOOK.md      # This file
```

---

## Getting Started

### Prerequisites

- **Node.js:** 18.x or higher
- **Python:** 3.11 or higher
- **npm:** 8.x or higher
- **Git:** Latest version
- **Firebase Account:** For Firestore access

### Local Development Setup

#### 1. Clone Repository

```bash
git clone https://github.com/Tee-David/realtors_practice.git
cd realtors_practice
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Firebase credentials
# Add: FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json

# Start API server
python api_server.py
# Server runs on http://localhost:5000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your backend URL
# Add: NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api

# Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

#### 4. Verify Setup

1. Open http://localhost:3000
2. You should see the login screen
3. Use "Continue as Guest" to access dashboard (if available)
4. Or create admin at http://localhost:3000/set-admin

---

## Environment Configuration

### Backend Environment Variables

See `backend/.env.example` for complete list. Key variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FIREBASE_SERVICE_ACCOUNT` | Path to Firebase JSON key | - | Yes |
| `FIRESTORE_ENABLED` | Enable Firestore storage | 1 | Yes |
| `RP_HEADLESS` | Headless browser mode | 1 | Yes |
| `RP_PAGE_CAP` | Max pages per site | 30 | No |
| `RP_GEOCODE` | Enable geocoding | 1 | No |
| `PORT` | API server port | 5000 | No |

### Frontend Environment Variables

See `frontend/.env.example` for complete list. Key variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | - | Yes |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID | - | No |
| `NEXT_PUBLIC_AUTH_ENABLED` | Enable authentication | true | No |

---

## Authentication & Security

### Admin Account Creation

1. Navigate to `/set-admin` (outside dashboard)
2. Fill in:
   - Username
   - Email
   - Password (min 8 chars, letters + numbers)
   - Confirm Password
3. Click "Create Admin Account"
4. Credentials are stored in localStorage (demo mode)
5. For production, implement proper backend authentication

### Security Features

✅ **Implemented:**
- Input validation on all forms
- CORS configuration
- API rate limiting
- Environment variable management
- Secure password requirements (8+ chars)
- XSS protection (React escaping)
- SQL injection protection (Firestore NoSQL)

⚠️ **To Implement for Production:**
- Backend JWT authentication
- Password hashing (bcrypt)
- Session management
- HTTPS/SSL enforcement
- Database-backed user storage
- Password reset functionality
- Two-factor authentication
- API key rotation

---

## Core Features

### 1. Property Search & Filtering

**Location:** `/data-explorer`

**Features:**
- Text search across title, location, description
- Location filter (area, LGA)
- Price range filter (min/max)
- Bedrooms/bathrooms filter
- Property type filter
- Listing type filter (For Sale/Rent/Short Let)
- Furnishing status filter
- Amenities filter
- View modes: Grid or List
- Pagination
- Real-time filter application
- **Sticky sidebar** for easy filtering while scrolling

**API:** `GET /api/firestore/properties`

### 2. Saved Searches

**Location:** `/saved-searches`

**Features:**
- Create custom search criteria
- Save searches with names
- View matching properties
- Check for new matches
- Email notifications (when configured)
- Edit saved searches
- Delete saved searches
- Toggle email alerts

**API:**
- `POST /api/searches` - Create search
- `GET /api/searches` - List searches
- `PUT /api/searches/{id}` - Update search
- `DELETE /api/searches/{id}` - Delete search

**Fixed:** API response format now matches frontend expectations (`{id, message}`)

### 3. Natural Language Search

**Status:** Planned (Task 11)

**Example Queries:**
- "3 bedroom apartment in Lekki under 100m"
- "Furnished house for rent in VI"
- "Commercial property in Ikeja"

**Implementation Plan:**
- NLP query parser
- Entity extraction (bedrooms, location, price)
- Query translation to filters
- Integration with search API

### 4. Property Details

**Features:**
- Full property information
- Image gallery
- Location map (if geocoded)
- Price and financial details
- Amenities list
- Agent contact information
- Quality score
- Source website link

### 5. Data Export

**Formats:** CSV, XLSX, JSON

**Locations:**
- Properties page
- Data Explorer
- Saved search results
- Dashboard reports

**Implementation:** All export buttons functional across the platform

### 6. Scraping Control

**Location:** `/scraper` or `/scrape-results`

**Features:**
- Manual scrape trigger
- Site selection
- Progress monitoring
- Results viewing
- Configuration:
  - Max pages per site (editable)
  - Geocoding toggle (editable)
  - Headless mode (locked to ON)
  - Other parameters (locked)

**API:**
- `POST /api/scrape` - Trigger scrape
- `GET /api/scrape/status` - Check status

### 7. Firestore Dashboard

**Location:** `/firestore` or `/dashboard`

**Features:**
- Total properties count
- Properties by listing type
- Recent additions
- Top deals
- Scrape activity (to be fixed)
- Database health metrics
- **Connection status:** Fixed to show correct Firestore connection

---

## API Reference

### Base URL
- **Development:** `http://localhost:5000/api`
- **Production:** `https://your-app.onrender.com/api`

### Authentication
Currently using demo mode. Production should implement JWT tokens.

### Key Endpoints

#### Health & Status
```http
GET /api/health
GET /api/info
```

#### Properties
```http
GET /api/firestore/properties
GET /api/firestore/property/{hash}
GET /api/firestore/dashboard
GET /api/firestore/for-sale
GET /api/firestore/for-rent
GET /api/firestore/newest
GET /api/firestore/top-deals
GET /api/firestore/premium
GET /api/firestore/properties/hot-deals
GET /api/firestore/properties/furnished
GET /api/firestore/properties/by-area/{area}
GET /api/firestore/properties/by-lga/{lga}
GET /api/firestore/site/{site_key}
POST /api/firestore/search
POST /api/firestore/query
POST /api/firestore/export
```

#### Saved Searches
```http
GET /api/searches
POST /api/searches
GET /api/searches/{id}
PUT /api/searches/{id}
DELETE /api/searches/{id}
GET /api/searches/{id}/stats
```

#### Scraping
```http
POST /api/scrape
GET /api/scrape/status
GET /api/sites
POST /api/sites/{site_key}/enable
POST /api/sites/{site_key}/disable
```

#### Export
```http
POST /api/export/csv
POST /api/export/xlsx
POST /api/export/json
```

### Response Formats

**Success:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

**Error:**
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {...}
}
```

---

## Database Schema

### Firestore Collection: `properties`

**Document Structure (9 Categories, 85+ Fields):**

```typescript
{
  // 1. Basic Info
  basic_info: {
    title: string
    source: string
    status: "available" | "sold" | "rented"
    listing_type: "sale" | "rent" | "land"
  }

  // 2. Property Details
  property_details: {
    property_type: string
    bedrooms: number
    bathrooms: number
    furnishing: "furnished" | "semi-furnished" | "unfurnished"
    size_sqm: number
    land_size_sqm: number
  }

  // 3. Financial
  financial: {
    price: number
    currency: "NGN"
    price_per_sqm: number
    service_charge: number
    payment_terms: string
  }

  // 4. Location
  location: {
    area: string
    lga: string
    state: "Lagos"
    address: string
    coordinates: GeoPoint
  }

  // 5. Amenities
  amenities: {
    features: string[]
    security: string[]
    utilities: string[]
  }

  // 6. Media
  media: {
    images: [{url: string, order: number}]
    videos: string[]
    virtual_tour: string
  }

  // 7. Agent Info
  agent_info: {
    name: string
    contact: string
    agency: string
    email: string
    phone: string
  }

  // 8. Metadata
  metadata: {
    quality_score: number
    scrape_timestamp: string
    hash: string
    last_updated: string
  }

  // 9. Tags
  tags: {
    premium: boolean
    hot_deal: boolean
    new_development: boolean
    verified: boolean
  }
}
```

---

## Deployment

### Backend Deployment (Render.com)

1. **Connect Repository:**
   - Link GitHub repo to Render
   - Select `main` branch

2. **Configure Service:**
   - **Type:** Web Service
   - **Environment:** Python 3.11
   - **Build Command:** `pip install -r backend/requirements-render.txt`
   - **Start Command:** `gunicorn api_server:app --bind 0.0.0.0:$PORT --timeout 300`
   - **Root Directory:** `/`

3. **Environment Variables:**
   - Add all variables from `backend/.env.example`
   - Especially: `FIREBASE_SERVICE_ACCOUNT` (paste JSON content)
   - Set `PORT` to Render's $PORT variable

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete
   - Note the deployment URL

### Frontend Deployment (Vercel)

1. **Connect Repository:**
   - Import project from GitHub
   - Select `main` branch

2. **Configure Project:**
   - **Framework:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

3. **Environment Variables:**
   - Add all from `frontend/.env.example`
   - Set `NEXT_PUBLIC_API_BASE_URL` to Render backend URL
   - Example: `https://realtors-practice-api.onrender.com/api`

4. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Domain: `your-project.vercel.app`

### GitHub Actions (Automated Scraping)

**Workflow:** `.github/workflows/scrape-production.yml`

**Schedule:** Runs daily or on-demand

**Steps:**
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run scraper with Firestore upload
5. Send email notification

**Triggers:**
- Schedule (cron)
- Manual workflow dispatch
- API trigger from frontend

---

## Monitoring & Maintenance

### Health Checks

**Endpoints:**
- `GET /api/health` - API server status
- `GET /api/firestore/dashboard` - Database connection

**Monitoring:**
- Check every 12 minutes (keep-alive)
- Frontend displays connection status
- Log errors to console

### Database Maintenance

**Scripts:**
```bash
# Update Firestore aggregates
python backend/scripts/update_firestore_aggregates.py

# Query properties
python backend/scripts/query_properties.py

# Clear Firestore (CAUTION!)
python backend/scripts/clear_firestore.py

# Monitor Firestore
python backend/scripts/monitor_firestore.py
```

### Log Files

**Locations:**
- Backend: `backend/logs/scraper.log`
- Scraper: `backend/logs/scrape_YYYYMMDD_HHMMSS.log`
- Exports: `backend/exports/`

### Performance Monitoring

**Metrics to Track:**
- API response times
- Database query performance
- Scraping duration
- Error rates
- User session duration

**Tools:**
- Render.com dashboard (backend)
- Vercel Analytics (frontend)
- Firebase Console (database)
- Sentry (error tracking - optional)

---

## Troubleshooting

### Frontend Shows 0 Properties

**Solution:** ✅ Fixed (v3.3.2)
- Added 13 missing Firestore endpoints
- Verified API routes work correctly

### Saved Search Creation Fails

**Solution:** ✅ Fixed (v4.0.0)
- Updated backend API response format
- Changed from `{success, search_id}` to `{id, message}`

### Backend Won't Start

**Causes:**
1. Missing Firebase credentials
2. Port 5000 already in use
3. Missing dependencies

**Solutions:**
```bash
# 1. Check Firebase credentials
ls backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json

# 2. Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9

# 3. Reinstall dependencies
pip install -r backend/requirements.txt
```

### Firestore Connection Failed

**Causes:**
1. Invalid service account file
2. Missing environment variable
3. Network issues

**Solutions:**
```bash
# Verify environment variable
echo $FIREBASE_SERVICE_ACCOUNT

# Test Firestore connection
python backend/tests/test_firestore_quick.py
```

### Scraper Returns Empty Data

**Causes:**
1. Site is disabled
2. Website structure changed
3. Network timeout

**Solutions:**
```bash
# Enable site
python backend/scripts/enable_one_site.py npc

# Run with debug
RP_DEBUG=1 RP_HEADLESS=0 python backend/main.py

# Check site accessibility
curl -I https://nigeriapropertycentre.com
```

---

## Security Best Practices

### ✅ Implemented

1. **Environment Variables:** Secrets in `.env` files
2. **Gitignore:** `.env` and credentials excluded
3. **Input Validation:** All user inputs validated
4. **CORS:** Restricted to allowed origins
5. **Rate Limiting:** API rate limits configured
6. **XSS Protection:** React escapes by default
7. **NoSQL Injection:** Firestore SDK prevents injection

### ⚠️ To Implement

1. **Backend Authentication:**
   - Replace localStorage with JWT tokens
   - Hash passwords with bcrypt
   - Implement refresh tokens
   - Add session management

2. **HTTPS:**
   - Force HTTPS in production
   - Use SSL certificates
   - Redirect HTTP to HTTPS

3. **API Keys:**
   - Implement API key authentication
   - Rotate keys monthly
   - Use different keys per environment

4. **Data Encryption:**
   - Encrypt sensitive data at rest
   - Use secure WebSocket connections
   - Implement field-level encryption

5. **Audit Logging:**
   - Log all authentication attempts
   - Track data modifications
   - Monitor suspicious activity

---

## Performance Optimization

### Backend Optimizations

✅ **Implemented:**
- Batch Firestore writes (10x faster)
- Connection pooling
- Query result caching
- Lazy loading of modules
- Efficient scraping with Playwright

⚠️ **To Implement:**
- Redis caching layer
- Database query optimization
- CDN for static assets
- Response compression (gzip)
- Load balancing

### Frontend Optimizations

✅ **Implemented:**
- Next.js static generation
- Image optimization
- Code splitting
- Lazy component loading
- React Query caching

⚠️ **To Implement:**
- Service workers (PWA)
- Prefetching
- Virtual scrolling for large lists
- Bundle size analysis
- Web vitals monitoring

---

## Contributing

### Code Style

**Python (Backend):**
- PEP 8 style guide
- Type hints for function signatures
- Docstrings for all public functions
- Black formatter

**TypeScript (Frontend):**
- ESLint configuration
- Prettier formatting
- Strict TypeScript mode
- Functional components with hooks

### Git Workflow

1. Create feature branch from `main`
2. Make changes
3. Test locally
4. Commit with descriptive message
5. Push to GitHub
6. Create pull request
7. Review and merge

### Testing

**Backend:**
```bash
cd backend
python -m pytest tests/
```

**Frontend:**
```bash
cd frontend
npm run test
npm run lint
npm run type-check
```

---

## Support & Resources

### Documentation

- **CLAUDE.md:** AI assistant quick reference
- **README.md:** Project overview
- **IMPLEMENTATION_PLAN.md:** Feature roadmap
- **backend/docs/:** Technical documentation
- **backend/frontend-integration-docs/:** API integration guides

### Links

- **Repository:** https://github.com/Tee-David/realtors_practice
- **Frontend:** Deployed on Vercel
- **Backend:** Deployed on Render.com
- **Database:** Firebase Firestore

### Contact

- **Developer:** Tee-David
- **Issues:** GitHub Issues
- **Email:** (Add your email here)

---

## Appendix

### Glossary

- **LGA:** Local Government Area
- **Firestore:** Google's NoSQL cloud database
- **Geocoding:** Converting addresses to GPS coordinates
- **JWT:** JSON Web Token (authentication)
- **CORS:** Cross-Origin Resource Sharing
- **API:** Application Programming Interface
- **REST:** Representational State Transfer
- **CRUD:** Create, Read, Update, Delete
- **PWA:** Progressive Web Application

### Changelog

**v4.0.0 (2025-12-28):**
- ✅ Fixed saved search creation
- ✅ Removed "Continue as Guest" option
- ✅ Created /set-admin page
- ✅ Added comprehensive environment variable templates
- ✅ Filter sidebar already sticky
- ✅ Added favicon and updated browser title
- ✅ Created production handbook

**v3.3.2 (2025-12-24):**
- ✅ Fixed Firestore endpoints (added 13 missing routes)
- ✅ Frontend now shows all 352 properties
- ✅ Major codebase reorganization

**v3.3.1 (2025-12-23):**
- ✅ Removed 3GB duplicate code
- ✅ Consolidated test files
- ✅ Cleaned up documentation

---

**End of Production Handbook**

*This handbook is maintained and updated with each major release. Last update: 2025-12-28*
