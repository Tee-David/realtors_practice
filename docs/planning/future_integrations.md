# Future Integrations Plan

**Status**: Planning Phase
**Date**: 2025-10-05
**Priority**: High

---

## Overview

This document outlines planned integrations for connecting the scraper backend with a frontend interface and Firebase cloud storage. These integrations will transform the command-line scraper into a full-stack web application.

---

## Integration 1: Frontend Connection

### Objective
Connect existing frontend design to scraper backend, enabling UI-based scraping control and site management.

### Features

**1. Trigger Scraping Runs**
- Frontend button/form to initiate scraping
- Select specific sites to scrape via checkboxes/multi-select
- Real-time progress updates during scraping
- Display scraping results and statistics

**2. Site Management UI**
- View all configured sites (enabled/disabled status)
- Add new sites through web interface
- Edit existing site configurations
- Enable/disable sites without editing YAML manually

**3. Auto-Generate config.yaml**
- When user adds new site through frontend:
  - Collect site details: name, URL, parser type, selectors
  - Validate inputs (URL format, required fields)
  - Auto-generate config.yaml entry
  - Reload configuration without restarting application

**4. Dashboard & Monitoring**
- Display site health status (from `status.py` logic)
- Show last scrape times and record counts
- Top performers visualization
- Error logs and warnings

### Technical Approach

**Backend API Layer** (New):
- Create `api/` folder with Flask/FastAPI endpoints
- Endpoints:
  - `POST /api/scrape` - Trigger scraping run
  - `GET /api/sites` - List all sites
  - `POST /api/sites` - Add new site (generates config)
  - `PUT /api/sites/<site_key>` - Update site config
  - `DELETE /api/sites/<site_key>` - Remove site
  - `GET /api/status` - Get site health status
  - `GET /api/exports` - List available exports
  - `GET /api/scrape/progress` - Real-time scraping progress

**Config Generation Module** (New):
- Extract from `core/config_loader.py` validation logic
- `core/config_generator.py`:
  - `generate_site_config(name, url, parser, selectors)` → dict
  - `append_to_config_yaml(site_key, site_config)` → None
  - `validate_new_site(site_config)` → bool

**Job Queue** (New):
- Use Celery/RQ for async scraping jobs
- Avoid blocking frontend during long scrapes
- Store job status in Redis/database
- Allow cancellation of running jobs

**WebSocket Support** (Optional):
- Real-time progress updates during scraping
- Push notifications when scrape completes
- Live error reporting

### File Structure (Proposed)

```
realtors_practice/
├── api/                          # NEW
│   ├── __init__.py
│   ├── app.py                    # Flask/FastAPI application
│   ├── routes/
│   │   ├── scraper.py            # Scraping endpoints
│   │   ├── sites.py              # Site management endpoints
│   │   ├── exports.py            # Export download endpoints
│   │   └── status.py             # Status/monitoring endpoints
│   └── utils/
│       ├── config_generator.py   # Auto-generate config.yaml
│       └── job_manager.py        # Async job handling
├── frontend/                     # User's existing frontend
│   └── ...
├── main.py                       # Existing scraper (unchanged)
├── watcher.py                    # Existing watcher (unchanged)
└── core/                         # Existing modules (unchanged)
```

### Integration Points

**Without Modifying Existing Code**:
- API layer imports and calls `main.py` functions
- `config_generator.py` uses `config_loader.py` validation
- API reads `logs/site_metadata.json` for status
- API serves files from `exports/cleaned/` for downloads

**Migration Path**:
1. Create API layer in new `api/` folder
2. Frontend connects to API endpoints
3. Test with existing scraper (no changes)
4. Gradually refactor scraper for better API integration

---

## Integration 2: Firebase Backend Storage

### Objective
Store raw and cleaned scraper exports in Firebase Storage for cloud access, backup, and multi-device availability.

### Features

**1. Automatic Upload to Firebase**
- After each scrape, upload to Firebase Storage
- Upload both raw exports (`exports/sites/`) and cleaned data (`exports/cleaned/`)
- Maintain folder structure in cloud
- Automatic retry on upload failure

**2. Cloud Access**
- Download exports from Firebase through frontend
- Share export links with team members
- Access data from any device

**3. Backup & Versioning**
- Keep historical exports in cloud
- Configurable retention policy (e.g., keep last 30 days)
- Disaster recovery (restore from Firebase if local deleted)

### Technical Approach

**Firebase Uploader Module** (New):
- `core/firebase_uploader.py`:
  - `upload_export(local_path, firebase_path)` → str (download URL)
  - `upload_directory(local_dir, firebase_dir)` → List[str]
  - `list_firebase_exports()` → List[dict]
  - `download_from_firebase(firebase_path, local_path)` → bool

**Integration with Watcher**:
- After watcher processes files, trigger Firebase upload
- Upload master workbook and per-site CSVs
- Store metadata.json in Firebase Firestore

**Integration with Main Scraper**:
- After `exporter.py` creates files, upload to Firebase
- Optional: Skip local storage, write directly to Firebase
- Background upload to avoid blocking scraper

### Firebase Structure

```
Firebase Storage:
├── raw_exports/
│   └── sites/
│       ├── npc/
│       │   ├── 2025-10-05_12-03-47_npc.csv
│       │   └── 2025-10-05_12-03-47_npc.xlsx
│       ├── propertypro/
│       │   └── ...
│       └── ...
└── cleaned_exports/
    ├── MASTER_CLEANED_WORKBOOK.xlsx
    ├── metadata.json
    └── sites/
        ├── npc_cleaned.csv
        ├── npc_cleaned.parquet
        └── ...

Firebase Firestore:
├── scraping_runs/
│   ├── run_20251005_120347/
│   │   ├── timestamp: "2025-10-05T12:03:47Z"
│   │   ├── sites_scraped: ["npc", "propertypro"]
│   │   ├── total_records: 1680
│   │   └── status: "completed"
│   └── ...
├── site_metadata/
│   ├── npc/
│   │   ├── last_scrape: timestamp
│   │   ├── last_count: 250
│   │   └── total_scrapes: 5
│   └── ...
└── exports_index/
    └── ... (searchable export metadata)
```

### Code Templates Ready

Implementation code already provided in `COMPATIBILITY.md`:
- Firebase Admin SDK initialization
- Upload script template
- Security rules
- Cost optimization tips

### File Structure (Proposed)

```
realtors_practice/
├── core/
│   ├── firebase_uploader.py      # NEW - Firebase upload logic
│   └── firebase_config.py        # NEW - Firebase credentials
├── scripts/
│   └── upload_to_firebase.py     # NEW - Manual upload tool
├── firebase_service_account.json # NEW - Firebase credentials (git-ignored)
└── .env                          # NEW - Firebase config (git-ignored)
```

### Integration Points

**Without Modifying Existing Code**:
- Create new `firebase_uploader.py` module
- Call uploader after scraping completes
- Wrapper script that runs scraper then uploads
- Watcher can optionally trigger upload after processing

**Configuration**:
- Add Firebase settings to `config.yaml`:
  ```yaml
  firebase:
    enabled: true
    auto_upload: true
    storage_bucket: "your-project.appspot.com"
    credential_path: "firebase_service_account.json"
    retention_days: 30
  ```

**Migration Path**:
1. Set up Firebase project and credentials
2. Create uploader module (standalone)
3. Test manual uploads with existing exports
4. Add automatic upload hooks
5. Implement Firestore metadata tracking

---

## Implementation Order

**Phase 1: Frontend Integration** (Next Session)
1. Create API layer (`api/` folder)
2. Implement scraping trigger endpoints
3. Build site management endpoints
4. Create config generator module
5. Connect frontend to API
6. Test end-to-end workflow

**Phase 2: Firebase Integration** (Future Session)
1. Set up Firebase project
2. Create Firebase uploader module
3. Test manual uploads
4. Add automatic upload triggers
5. Implement Firestore metadata
6. Connect frontend to Firebase data

**Phase 3: Polish & Optimization** (Future)
1. Add authentication/authorization
2. Implement job queue for async scraping
3. WebSocket for real-time updates
4. Advanced monitoring dashboard
5. Scheduled scraping (cron-like UI)
6. Export search and filtering

---

## Current Project Readiness

**✅ Ready for Integration**:
- Clean modular architecture
- Config-driven design (easy to extend)
- Comprehensive error handling
- Well-documented codebase
- Test coverage (7/7 integration tests passing)
- Firebase templates in COMPATIBILITY.md

**✅ No Code Changes Needed Yet**:
- Existing scraper works independently
- API can wrap existing functions
- Firebase uploader can be standalone module
- Frontend connects via new API layer

**✅ Backwards Compatible**:
- Command-line scraping still works
- Config.yaml remains source of truth
- No breaking changes to core modules

---

## Notes for Future Claude Sessions

**When Starting Frontend Integration**:
1. Read this document first
2. Review `COMPATIBILITY.md` for Firebase code templates
3. Examine `scripts/` folder for CLI patterns to replicate in API
4. Study `core/config_loader.py` for config generation logic
5. **Do not modify** `main.py`, `watcher.py`, or `core/` modules unless necessary

**Key Design Principles**:
- Keep API layer separate from core scraper
- Maintain backward compatibility with CLI usage
- Config.yaml remains single source of truth
- Firebase is optional enhancement (scraper works without it)
- Frontend is UI for existing functionality (not replacement)

**Testing Strategy**:
- Test API endpoints independently
- Verify scraper still works via CLI
- Test config generation with validation
- Integration tests for frontend → API → scraper flow

---

## Cost & Performance Estimates

**Firebase Costs** (see COMPATIBILITY.md):
- Storage: ~$0.026/GB/month
- Downloads: ~$0.12/GB
- **Estimated**: $0.26/month for typical usage (10GB storage, 100 downloads)

**API Performance**:
- Scraping unchanged (same performance)
- API adds <50ms overhead per request
- Async jobs prevent frontend blocking
- Firebase uploads happen in background

**Infrastructure**:
- Can run on same cPanel hosting
- Or deploy API separately (Heroku, Railway, etc.)
- Frontend can be static (Vercel, Netlify)
- Firebase handles scaling automatically

---

## Security Considerations

**API Security** (Future):
- Authentication (JWT tokens)
- Rate limiting per user
- Input validation on all endpoints
- CORS configuration for frontend origin

**Firebase Security**:
- Service account credentials in `.env` (git-ignored)
- Firebase Storage rules (authenticated users only)
- Firestore security rules
- No credentials in frontend code

**Config Management**:
- Validate user inputs before generating config
- Prevent malicious URLs or selectors
- Sanitize site names (prevent path traversal)
- Audit log for config changes

---

**Status**: Ready for implementation when frontend integration begins.
