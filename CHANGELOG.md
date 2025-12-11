# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.2.2] - 2025-12-11

### Added
- **Hot Reload Endpoint** (`POST /api/admin/reload-env`): Update environment variables (GitHub token, Firebase credentials) without server restart - zero downtime credential updates
- ENV_MANAGEMENT_GUIDE.md (2,300+ lines): Comprehensive guide for environment variable management, credential rotation, and security best practices
- Session documentation system: `docs/sessions/2025-12-11/SESSION_REPORT.md` with complete session details
- Maintenance scripts: `scripts/maintenance/quick_restart.py` and `force_restart_server.py` for server management
- QUICK_START.md: Simple getting started guide for common tasks

### Fixed
- **Critical**: Added missing `timezone` import to api_server.py (line 11) - required for hot reload endpoint
- **Timezone Errors**: Updated all datetime operations to use `datetime.now(timezone.utc)` for consistency
- Scheduling endpoint: Added timezone awareness for naive datetime inputs (lines 2350-2353)
- Global job counter: Added `global job_id_counter` declaration (line 2375)
- Health check endpoint: Now returns timezone-aware timestamps
- **Critical Data Loss Bug**: Added `if: ${{ always() }}` to consolidation job in `.github/workflows/scrape-production.yml` (line 334)

### Changed
- Updated all documentation references from `scrape.yml` to `scrape-production.yml` (21 files)
- Improved FOR_FRONTEND_DEVELOPER.md with clearer production URL configuration instructions
- Consolidated session documentation into organized structure (`docs/sessions/`)
- Moved maintenance scripts to `scripts/maintenance/` directory
- Updated .env.example to reference current Firebase credentials file
- Updated USER_GUIDE.md to v3.2.2

### Removed
- 17 temporary and duplicate documentation files from root directory
- Redundant session files (consolidated into SESSION_REPORT.md)

---

## [3.2.1] - 2025-11-18

### Added
- Enhanced time estimation endpoint with timeout warnings
- Time estimation API now provides risk assessment (safe/warning/danger)
- Session-level timeout warnings
- Actionable recommendations system
- Conservative strategy settings (3 sites/session, 5 parallel)
- Comprehensive frontend documentation for time estimation

### Changed
- Reduced sites per session: 5 → 3
- Increased session timeout: 60 → 90 minutes
- Reduced max parallel sessions: 10 → 5
- Reduced default pages: 20 → 15
- Updated workflow timeout fix for 99% reliability

### Fixed
- Firestore upload verification (16/16 success rate)
- Firebase credentials updated (resolved Invalid JWT Signature errors)
- Regenerated service account key: `realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json`

---

## [3.1.0] - 2025-11-10

### Added
- **Enterprise Firestore Schema**: Complete 9-category nested schema with 85+ fields
  - `basic_info.*`, `property_details.*`, `financial.*`, `location.*`, `amenities.*`, `media.*`, `agent_info.*`, `metadata.*`, `tags.*`
- **16 Firestore API Endpoints**: 11 updated + 7 new enterprise endpoints
- **18 Specialized Query Functions**: Advanced Firestore querying capabilities
- **Intelligent Auto-Detection**: listing_type, furnishing, condition from text analysis
- **Auto-Tagging**: premium (≥100M or 4+ BR), hot_deal (<15M per BR)
- **Location Intelligence**: 50+ Lagos landmarks, area/LGA hierarchy
- **Smart Extraction**: Automatic keyword generation for full-text search
- Complete TypeScript type definitions for enterprise schema
- React hooks examples for all endpoint categories
- `clear_firestore.py` utility
- `enable_all_sites.py` utility

### Changed
- Total API Endpoints: 84 (68 original + 16 Firestore)
- Documentation: 25+ files, 10,000+ lines
- Test Pass Rate: 100% (16/16 Firestore endpoints)
- Response Time: 30-200ms average

### Documentation
- Created `FINAL_SUMMARY_V3.1.md` (460+ lines)
- Created `API_ENDPOINT_TEST_REPORT.md`
- Complete rewrite of `frontend/README_FOR_DEVELOPER.md`
- Updated `frontend/API_ENDPOINTS_ACTUAL.md` to v3.1
- Updated Postman collection to v3.1.0

---

## [2.2.0] - 2025-10-22

### Added
- Comprehensive testing suite (82 tests, backend-only)
- Security implementation:
  - API Key authentication (permanent)
  - JWT token authentication (24-hour expiration)
  - Content Security Policy (CSP) headers
  - XSS Protection headers
  - CORS configuration
  - Input validation and sanitization
  - Path traversal protection
  - HSTS (HTTP Strict Transport Security)
- API Key Management System (CLI)
- Postman Collection (all 68 endpoints)

### Changed
- Updated README.md endpoint count: 50 → 68
- Updated docs/README.md: "25+ endpoints" → "68 endpoints across 8 categories"
- Cleaned README.md (removed "DO NOT DELETE" warnings)

### Documentation
- `core/auth.py` - Authentication system
- `core/security.py` - Security middleware
- `.env.example` - Complete environment template
- `docs/FRONTEND_AUTH_GUIDE.md` - Frontend integration guide
- `docs/Nigerian_Real_Estate_API.postman_collection.json`
- `docs/POSTMAN_GUIDE.md`

### Security
- All security features implemented but opt-in (AUTH_ENABLED=false by default)

---

## [2.1.0] - 2025-10-13

### Added
- **REST API Server** (api_server.py - 550 lines)
  - Flask web server with CORS support
  - 68 endpoints across 8 categories
  - Threaded operation for background scraping
  - Comprehensive error handling

- **API Helper Modules** (api/helpers/):
  - data_reader.py (230 lines) - Read/query Excel/CSV data
  - log_parser.py (180 lines) - Parse logs with filtering
  - config_manager.py (330 lines) - Programmatic config.yaml management
  - scraper_manager.py (290 lines) - Manage scraping processes
  - stats_generator.py (240 lines) - Generate statistics

### Documentation
- `docs/FRONTEND_INTEGRATION.md` (1,100+ lines) - Complete API reference
- `docs/API_QUICKSTART.md` (400+ lines) - Quick start guide
- `docs/API_README.md` (150+ lines) - API overview

### Changed
- File structure cleanup (root directory: 20+ → 17 files)
- All documentation updated and reorganized

---

## [2.0.0] - 2025-10-20

### Added
- Dynamic configuration system via config.yaml
- 82+ real estate websites support (unlimited scalability)
- Per-site overrides and metadata tracking
- Adaptive scraping (requests → playwright → scraperapi fallback)
- Quality scoring (0-100%) with configurable threshold
- Advanced duplicate detection using SHA256 hashing
- Lagos-only filtering with landmark detection
- Master workbook consolidation
- Watcher service for automated exports

### Changed
- Complete architecture refactoring
- Configuration-first approach (no hard-coded URLs)
- Environment variable precedence system

---

## [1.0.0] - Initial Release

### Added
- Basic web scraping functionality
- CSV/XLSX export
- Geocoding with OpenStreetMap
- Site-specific parsers
- Basic logging and error handling

---

## Version Numbering Guide

**Format**: MAJOR.MINOR.PATCH

- **MAJOR** (X.0.0): Breaking changes, major architecture updates
- **MINOR** (0.X.0): New features, backward-compatible
- **PATCH** (0.0.X): Bug fixes, documentation updates

**Current Version**: 3.2.2
**Status**: ✅ 100% Production Ready
