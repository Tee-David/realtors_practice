# Changelog

All notable changes to this project will be documented in this file.

## [2025-10-19 Later] - Intelligent Scraper Features

### Added
- **Intelligent Scraper Module** - 100% FREE heuristic-based enhancement
- `helpers/screenshot.py` - Screenshot utilities for debugging (NOT AI vision)
- `helpers/relevance.py` - Heuristic relevance detection system
- Auto-adaptive selector discovery when CSS selectors fail
- Screenshot capability for list pages and errors (opt-in via `RP_SCREENSHOT`)
- Comprehensive test suite (`tests/test_intelligent_scraper.py`)

### Features
- **Heuristic Scoring System**: 6-layer scoring (text patterns, structure, URLs, attributes, position, exclusions)
- **Auto-Discovery**: Automatically finds best CSS selector when configured ones fail
- **Relevance Filtering**: Filters out navigation/category elements using programmatic rules
- **Screenshot Support**: Visual debugging for troubleshooting (human review, not AI processing)

### Environment Variables
- `RP_INTELLIGENT_MODE` - Enable/disable intelligent features (default: 0)
- `RP_SCREENSHOT` - Enable/disable screenshots (default: 0)
- `RP_RELEVANCE_THRESHOLD` - Minimum score for relevance (default: 25)

### Test Results
✅ All 4 test suites passing (URL filtering, relevance scoring, auto-discovery, helpers)
✅ Backward compatible - zero impact when disabled
✅ Production ready

### Documentation
- Added `docs/INTELLIGENT_SCRAPER.md` - Complete feature documentation
- Updated `PROJECT_STRUCTURE.md` - Added helpers/ directory
- Updated `README.md` - Added intelligent scraper section

---

## [2025-10-19] - Critical Bug Fixes & Cleanup

### Fixed
- **URL Filter Bug**: Fixed parsers/npc.py missing `site_config` parameter causing fallback to generic scraper that extracted 630 category links instead of properties
- **Lagos Location Filter**: Now checks listing URLs in addition to location/title fields
- **Playwright Threading**: Added sequential mode (default) to avoid greenlet threading errors in parallel detail scraping
- **Indentation Error**: Fixed core/detail_scraper.py line 506 preventing module import

### Changed
- Lagos filter now checks `listing_url` field for location keywords (main.py:206)
- Detail scraper defaults to sequential mode; parallel mode available via `RP_DETAIL_PARALLEL=1`
- Removed file-based debug logging; now uses `RP_DEBUG` flag for logger output only

### Removed
- Temporary debug scripts (debug_scraper.py, test_*_fix.py, visual_debug_scraper.py, dump_*.py)
- File-based debug logging in parsers/specials.py

### Added
- `DETAIL_PARALLEL` environment variable to enable/disable parallel mode
- Sequential mode in detail scraper (safer, avoids threading issues)
- Comprehensive URL filtering in parsers/specials.py

### Documentation
- Moved session documentation to docs/sessions/
- Moved deployment docs to docs/deployment/
- Created archive/ folder for misc files
- Added CHANGELOG.md (this file)

### Test Results
**Before Fix**: 630 category links extracted
**After Fix**: 3 actual property listings with valid bedroom counts

Example URLs after fix:
- `.../lagos/lekki/3154197-4-bedrooms-semi-detached-duplex...`
- `.../lagos/ajah/ajiwe/3154196-brand-new-4-bedrooms-terraced-duplex`
- `.../lagos/lekki/ikota/3154194-3-bedrooms-duplex`

---

## [2025-10-13] - API Integration & File Structure

### Added
- Flask REST API server (api_server.py - 550 lines)
- API helper modules in api/helpers/ (5 modules, 1,270 lines)
- Frontend integration documentation (1,650+ lines)
- 25+ API endpoints across 6 categories

### Changed
- Reorganized project structure (root reduced from 30+ to 17 files)
- Created docs/ hierarchy (guides/, milestones/, planning/)

---

## [2025-10-05] - Export Watcher Service

### Added
- Export watcher service (watcher.py - 365 lines)
- Data cleaning module (core/data_cleaner.py - 430 lines)
- Master workbook management (core/master_workbook.py - 390 lines)
- Integration tests (test_watcher_integration.py)

### Features
- Fuzzy column name matching
- Price/location/type normalization
- Hash-based deduplication
- Master workbook consolidation
- Watch mode with configurable interval

---

## [2025-10-05 Earlier] - Config-Driven Architecture

### Added
- 100% config-driven architecture (config.yaml as single source of truth)
- Per-site overrides for retry, geocoding, export formats
- Automatic metadata tracking (last_scrape, total_scrapes)
- CLI tools: enable_sites.py, validate_config.py, status.py

### Changed
- Removed hard-coded CONFIGS dict from parsers/specials.py
- Made site_config parameter mandatory
- All 50 sites must be configured in config.yaml

### Test Results
- 57/58 tests passing (98.3%)
- Production test: 1,680 listings from 3/5 sites
- Graceful error handling verified

---

For detailed session notes, see docs/sessions/
