# Project Structure (Clean Baseline - 2025-10-19)

## Root Directory
```
realtors_practice/
├── main.py                  # Main scraper entry point
├── watcher.py               # Export watcher service
├── api_server.py            # Flask REST API server
├── requirements.txt         # Python dependencies
├── config.yaml              # Site configurations (gitignored)
├── config.example.yaml      # Config template
├── README.md                # Project overview
├── CLAUDE.md                # AI assistant guidance
├── CHANGELOG.md             # Version history
└── PROJECT_STRUCTURE.md     # This file
```

## Core Modules (`core/`)
**10 essential modules for scraping logic**

| Module | Lines | Purpose |
|--------|-------|---------|
| `config_loader.py` | ~200 | YAML config loading + validation |
| `dispatcher.py` | ~120 | Parser resolution system |
| `scraper_engine.py` | ~350 | Playwright-based adaptive scraper |
| `cleaner.py` | ~250 | Normalize listings to schema |
| `geo.py` | ~150 | Nominatim geocoding w/ caching |
| `exporter.py` | ~180 | CSV/XLSX export generation |
| `utils.py` | ~145 | Lagos filter + utilities |
| `data_cleaner.py` | ~430 | Fuzzy matching + normalization |
| `master_workbook.py` | ~390 | Consolidated workbook management |
| `detail_scraper.py` | ~580 | Level 2 detail page scraping |

## Intelligent Scraper Helpers (`helpers/`) - NEW
**Modular helpers for intelligent scraping (100% FREE)**

| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | ~30 | Package exports |
| `screenshot.py` | ~210 | Screenshot utilities for debugging |
| `relevance.py` | ~390 | Heuristic relevance detection system |

**Features**:
- Screenshot capability (opt-in via `RP_SCREENSHOT`)
- Heuristic scoring: 6-layer analysis (text, structure, URL, attributes, position, exclusions)
- Auto-adaptive selector discovery when CSS selectors fail
- 100% FREE - No AI APIs, only programmatic rules
- See `docs/INTELLIGENT_SCRAPER.md` for complete documentation

## API Layer (`api/`)
**Flask REST API for frontend integration**

```
api/
├── __init__.py
└── helpers/
    ├── __init__.py
    ├── data_reader.py       # Read/query export data
    ├── log_parser.py        # Parse scraper logs
    ├── config_manager.py    # Manage config.yaml programmatically
    ├── scraper_manager.py   # Start/stop scraping processes
    └── stats_generator.py   # Generate statistics
```

## Parsers (`parsers/`)
**50+ site-specific parsers**

- `specials.py` - Config-driven generic parser (main logic)
- `npc.py`, `propertypro.py`, etc. - Thin wrappers for backward compatibility
- **Note**: Individual parsers to be deprecated in favor of `parser: specials` in config.yaml

## Scripts (`scripts/`)
**CLI utilities**

- `enable_sites.py` - Enable multiple sites at once
- `validate_config.py` - Pre-flight config validation
- `status.py` - Site health dashboard

## Tests (`tests/`)
**Regression and integration tests**

- `test_watcher_integration.py` - Watcher service tests
- `test_milestone*.py` - Feature milestone tests
- `test_url_filter.py` - URL filtering regression test

## Documentation (`docs/`)

```
docs/
├── deployment/              # Deployment guides
│   ├── FIREBASE_QUICKSTART.md
│   ├── FREE_DEPLOYMENT.md
│   └── GITHUB_ACTIONS_TESTING.md
├── guides/                  # User guides
│   ├── FRONTEND_INTEGRATION.md
│   ├── API_QUICKSTART.md
│   └── ...
├── sessions/                # Session notes
│   ├── SESSION_SUMMARY_2025-10-18.md
│   ├── SESSION_RESUME_2025-10-19.md
│   ├── BUG_FIX_COMPLETE_2025-10-19.md
│   └── ...
├── FINAL_DELIVERY.md
└── LAYMAN.md
```

## Data Directories (gitignored)

```
exports/
├── sites/                   # Per-site raw exports
│   ├── npc/
│   ├── propertypro/
│   └── ...
└── cleaned/                 # Cleaned data
    ├── MASTER_CLEANED_WORKBOOK.xlsx
    ├── npc_cleaned.csv
    └── metadata.json

logs/
├── scraper.log
├── geocache.json
└── site_metadata.json
```

## Archive (`archive/`)
**Misc files kept for reference**

- User notes, old instructions, etc.

## Configuration

### Environment Variables
```bash
# Scraping
RP_PAGE_CAP=30              # Max pages per site
RP_DEBUG=1                   # Enable debug logging
RP_HEADLESS=1                # Headless browser mode
RP_GEOCODE=1                 # Enable geocoding
RP_MAX_GEOCODES=120          # Geocoding limit

# Detail Scraping
RP_DETAIL_CAP=0              # Max detail pages (0=unlimited)
RP_DETAIL_WORKERS=5          # Parallel workers
RP_DETAIL_PARALLEL=0         # Enable parallel mode (0=sequential, safer)

# Network
RP_NET_RETRY_SECS=180        # Network timeout
RP_RETRY_ON_ZERO=0           # Retry if zero results
```

### config.yaml Structure
```yaml
global_settings:
  geocoding:
    enabled: true
    max_per_run: 120
  export_formats: [csv, xlsx]
  # ...

sites:
  npc:
    name: "Nigeria Property Centre"
    url: "https://nigeriapropertycentre.com"
    enabled: true
    parser: specials           # Use generic parser
    selectors:
      card: "li.property-list"
      title: "h2.title"
      # ...
    overrides:                 # Per-site settings
      geocoding:
        enabled: false
      # ...
```

## Data Flow

```
1. main.py
   ↓
2. config_loader.py → Load config.yaml
   ↓
3. dispatcher.py → Resolve parser (specials.py)
   ↓
4. scraper_engine.py → Fetch pages (Level 1)
   ↓
5. parsers/specials.py → Extract listings + URLs
   ↓
6. detail_scraper.py → Enrich with detail pages (Level 2)
   ↓
7. cleaner.py → Normalize to schema
   ↓
8. Lagos filter (utils.py) → Filter non-Lagos
   ↓
9. geo.py → Geocode (optional)
   ↓
10. exporter.py → Generate CSV/XLSX
    ↓
11. watcher.py → Clean + consolidate (background)
```

## Recent Changes (2025-10-19)

### Bug Fixes
✅ URL filter working (category links → actual properties)
✅ Lagos filter checks URLs
✅ Playwright threading fixed (sequential mode default)
✅ Code cleanup complete

### Files Cleaned
- Removed 6 debug scripts
- Moved 7 session docs to docs/sessions/
- Moved 3 deployment docs to docs/deployment/
- Removed debug folders

### Current Status
**Root Directory**: 9 essential files
**Code Quality**: All major bugs fixed
**Tests**: Passing
**Ready For**: Intelligent scraper development

## Next Steps

**Intelligent Scraper Features (Planned)**
- Screenshot capability for debugging
- Heuristic-based relevance detection (no AI APIs)
- Auto-adapt to different site structures
- Modular helper functions
- 100% FREE implementation

**Future Cleanup**
- Deprecate individual site parsers (use only `parser: specials`)
- Consolidate documentation further
- Add more integration tests
