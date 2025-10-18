# Project Structure

## Directory Tree

```
realtors_practice/
│
├── 📄 main.py                      # Main scraper entry point
├── 📄 watcher.py                   # Export watcher service
├── 📄 config.yaml                  # Configuration file
├── 📄 CLAUDE.md                    # AI assistant context
├── 📄 README.md                    # Project overview
├── 📄 STRUCTURE.md                 # This file
├── 📄 COMPATIBILITY.md             # cPanel & Firebase guide
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 core/                        # Core application modules
│   ├── config_loader.py           # Configuration management
│   ├── scraper_engine.py          # Generic scraping engine
│   ├── dispatcher.py              # Parser dispatch system
│   ├── cleaner.py                 # Data normalization
│   ├── geo.py                     # Geocoding service
│   ├── exporter.py                # Export to CSV/XLSX
│   ├── utils.py                   # Utility functions
│   ├── captcha.py                 # Captcha handling
│   ├── data_cleaner.py            # Advanced data cleaning
│   └── master_workbook.py         # Master workbook management
│
├── 📁 parsers/                     # Site-specific parsers
│   ├── specials.py                # Config-driven parser (50+ sites)
│   ├── npc.py                     # Nigeria Property Centre
│   ├── propertypro.py             # PropertyPro
│   ├── jiji.py                    # Jiji
│   └── [site].py                  # Other site parsers
│
├── 📁 scripts/                     # Utility scripts
│   ├── enable_sites.py            # Enable multiple sites
│   ├── enable_one_site.py         # Enable single site
│   ├── validate_config.py         # Validate configuration
│   └── status.py                  # Site health dashboard
│
├── 📁 tests/                       # Test suite
│   ├── test_watcher_integration.py # Watcher integration tests
│   ├── test_milestone3.py         # Milestone 3 tests
│   ├── test_milestone4_5.py       # Milestone 4-5 tests
│   ├── test_site_specific.py      # Site configuration tests
│   ├── test_config_validation.py  # Config validation tests
│   └── test_main_integration.py   # Main scraper tests
│
├── 📁 docs/                        # Documentation
│   │
│   ├── 📁 guides/                 # User guides
│   │   ├── QUICKSTART.md          # Quick start guide
│   │   ├── WATCHER_QUICKSTART.md  # Watcher quick start
│   │   ├── WATCHER_COMPLETE.md    # Complete watcher docs
│   │   ├── MIGRATION_GUIDE.md     # Migration guide
│   │   └── HARD_CODED_CONFIGS_REMOVED.md
│   │
│   ├── 📁 milestones/             # Milestone completion docs
│   │   ├── MILESTONE_2_COMPLETE.md
│   │   ├── MILESTONE_3_COMPLETE.md
│   │   ├── MILESTONE_4_5_COMPLETE.md
│   │   ├── MILESTONE_9_10_11_COMPLETE.md
│   │   └── PROJECT_COMPLETE.md
│   │
│   └── 📁 planning/               # Planning documents
│       ├── planning.md            # Project planning
│       ├── tasks.md               # Task list
│       └── prompt.md              # Project prompt
│
├── 📁 exports/                     # Export data
│   │
│   ├── 📁 sites/                  # Raw scraper exports
│   │   ├── npc/
│   │   │   ├── 2025-10-05_11-49-27_npc.csv
│   │   │   └── 2025-10-05_11-49-27_npc.xlsx
│   │   ├── propertypro/
│   │   ├── jiji/
│   │   └── ... (50+ site folders)
│   │
│   └── 📁 cleaned/                # Cleaned & consolidated data
│       ├── MASTER_CLEANED_WORKBOOK.xlsx
│       ├── metadata.json
│       ├── .watcher_state.json
│       ├── watcher.log
│       ├── errors.log
│       ├── npc/
│       │   ├── npc_cleaned.csv
│       │   └── npc_cleaned.parquet
│       └── ... (per-site cleaned exports)
│
└── 📁 logs/                        # Application logs
    ├── scraper.log                # Main scraper log
    ├── geocache.json              # Geocoding cache
    └── site_metadata.json         # Site scraping metadata
```

---

## Module Descriptions

### Core Modules (`core/`)

#### `config_loader.py`
**Purpose**: Configuration management and validation
- Loads and validates `config.yaml`
- Provides `Config` class with type-safe access
- Validates site configurations
- Supports per-site overrides
- **Key Functions**:
  - `load_config()` - Load configuration
  - `get_site_setting()` - Get site-specific setting
  - `validate_site_config()` - Validate site configuration

#### `scraper_engine.py`
**Purpose**: Generic web scraping engine
- Adaptive fetching (requests → playwright fallback)
- Pagination strategies (next button, numeric, URL params)
- Lazy-load scrolling
- Generic card extraction
- **Key Functions**:
  - `fetch_adaptive()` - Adaptive fetch with fallback
  - `scrape_list_page()` - Scrape listing page
  - `generic_deep_crawl()` - Generic deep crawl

#### `dispatcher.py`
**Purpose**: Parser selection and dispatch
- Routes sites to appropriate parsers
- Supports 3 parser types: specials, generic, custom
- **Key Functions**:
  - `get_parser()` - Get parser for site
  - `ParserAdapter` - Parser adapter class

#### `cleaner.py`
**Purpose**: Data normalization and cleaning
- Extracts structured data from raw scraped content
- Normalizes prices, locations, property types
- Extracts bedrooms, bathrooms from text
- **Key Functions**:
  - `clean_listing()` - Clean single listing
  - `extract_bedrooms()` - Extract bedroom count

#### `geo.py`
**Purpose**: Geocoding service
- OpenStreetMap Nominatim integration
- Rate limiting (1 req/sec)
- Persistent cache (`logs/geocache.json`)
- **Key Functions**:
  - `geocode_location()` - Geocode location string

#### `exporter.py`
**Purpose**: Export listings to CSV/XLSX
- Exports to `exports/sites/<site>/`
- Supports multiple formats
- Handles complex data types (lists, dicts)
- **Key Functions**:
  - `export_listings()` - Export listings for a site

#### `data_cleaner.py`
**Purpose**: Advanced data cleaning for watcher service
- Multi-encoding CSV/XLSX parsing
- Fuzzy column name matching
- Price/location/type normalization
- Hash-based deduplication
- **Key Functions**:
  - `clean_and_normalize()` - Main cleaning pipeline
  - `normalize_price()` - Normalize price strings
  - `fuzzy_match_column()` - Fuzzy column matching

#### `master_workbook.py`
**Purpose**: Master workbook management
- Creates `MASTER_CLEANED_WORKBOOK.xlsx`
- Per-site sheets with formatting
- Append-only idempotent logic
- CSV/Parquet exports
- **Key Classes**:
  - `MasterWorkbookManager` - Workbook manager
- **Key Functions**:
  - `append_to_master()` - Append records to master

---

### Parsers (`parsers/`)

#### `specials.py`
**Purpose**: Config-driven parser for 50+ sites
- Reads selectors from `config.yaml`
- Supports custom pagination strategies
- Lagos-specific list paths
- Search query support
- **Key Functions**:
  - `scrape()` - Main scraping function

#### Site-specific parsers (`[site].py`)
**Purpose**: Thin wrappers for specific sites
- Delegate to `specials.scrape()` with site key
- Can override for custom logic
- **Examples**: `npc.py`, `propertypro.py`, `jiji.py`

---

### Scripts (`scripts/`)

#### `enable_sites.py`
**Usage**: `python scripts/enable_sites.py site1 site2 site3`
**Purpose**: Enable multiple sites at once
- Modifies `config.yaml`
- Disables all other sites

#### `enable_one_site.py`
**Usage**: `python scripts/enable_one_site.py <site>`
**Purpose**: Enable single site for testing
- Disables all other sites
- Lists all sites with `--list` flag

#### `validate_config.py`
**Usage**: `python scripts/validate_config.py`
**Purpose**: Validate configuration
- Checks required fields
- Validates URLs
- Verifies parser references

#### `status.py`
**Usage**: `python scripts/status.py`
**Purpose**: Site health dashboard
- Shows healthy/warning/critical sites
- Top performers by listing count
- Most active sites by scrape count

---

### Tests (`tests/`)

All test files follow pattern `test_*.py` and can be run with:
```bash
python tests/test_<name>.py
```

#### `test_watcher_integration.py`
**Tests**: Watcher service integration
- Folder structure
- Master workbook creation
- CSV exports
- Idempotency
- Data cleaning functions

#### `test_milestone3.py`
**Tests**: Parser integration (Milestone 3)
- Config-driven parsing
- Parser dispatch
- Site configuration

#### `test_milestone4_5.py`
**Tests**: Enhanced config system (Milestones 4-5)
- Per-site overrides
- Metadata tracking
- Error handling

#### `test_site_specific.py`
**Tests**: Site configuration
- All sites have required fields
- URL validation
- Parser type distribution

---

## Data Flow

### Scraping Flow

```
┌─────────────┐
│   main.py   │  (Entry point)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ config_loader   │  (Load config.yaml)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   dispatcher    │  (Get parser for site)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ parsers/special │  (Scrape site)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    cleaner      │  (Normalize data)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│      geo        │  (Geocode locations)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│    exporter     │  (Export to CSV/XLSX)
└──────┬──────────┘
       │
       ▼
    exports/sites/
```

### Watcher Flow

```
┌─────────────┐
│ watcher.py  │  (Monitor exports/sites/)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ ExportScanner   │  (Find new/changed files)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ data_cleaner    │  (Clean & normalize)
└──────┬──────────┘
       │
       ▼
┌─────────────────────┐
│ master_workbook     │  (Append to master)
└──────┬──────────────┘
       │
       ▼
    exports/cleaned/
```

---

## Configuration

### `config.yaml` Structure

```yaml
global_settings:
  geocoding: { ... }
  pagination: { ... }
  retry: { ... }
  export: { ... }
  browser: { ... }

sites:
  site_key:
    name: "Site Name"
    url: "https://example.com"
    enabled: true|false
    parser: specials|generic|custom
    selectors: { ... }
    pagination: { ... }
    overrides: { ... }
```

---

## File Paths (Relative)

All file paths in code are **relative to project root**:

```python
Path("config.yaml")              # Config file
Path("exports/sites/")           # Site exports
Path("exports/cleaned/")         # Cleaned exports
Path("logs/scraper.log")         # Main log
Path("core/config_loader.py")    # Core module
```

This ensures portability across different environments (local, cPanel, etc.)

---

## Import Structure

### Import Conventions

```python
# Core modules
from core.config_loader import load_config
from core.scraper_engine import fetch_adaptive
from core.dispatcher import get_parser

# Parsers
from parsers.specials import scrape

# Standard library
from pathlib import Path
import logging
```

### No Circular Imports

Module dependencies are unidirectional:
- `main.py` → imports `core/*`, `parsers/*`
- `core/*` → imports only standard library and other `core/*`
- `parsers/*` → imports `core/*`

---

## Git Structure

### `.gitignore` (Recommended)

```
# Environment
venv/
.env
*.pyc
__pycache__/

# Data
exports/
logs/
*.log

# Config (use example)
config.yaml

# Credentials
firebase-credentials.json
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### Tracked Files

- Source code (`*.py`)
- Documentation (`*.md`)
- Example config (`config.example.yaml`)
- Requirements (`requirements.txt`)

---

## Best Practices

### File Organization

1. **Keep main executables in root** (`main.py`, `watcher.py`)
2. **Group related modules** (`core/`, `parsers/`, etc.)
3. **Separate concerns** (utilities, tests, docs)
4. **Use clear names** (descriptive, not abbreviated)

### Code Organization

1. **One module per file** (except small helpers)
2. **Module docstrings** (explain purpose)
3. **Function docstrings** (args, returns, purpose)
4. **Type hints** (where appropriate)

### Documentation Organization

1. **README.md** - Project overview (root)
2. **STRUCTURE.md** - Project structure (this file)
3. **COMPATIBILITY.md** - Platform compatibility
4. **docs/guides/** - User guides
5. **docs/milestones/** - Milestone completions
6. **docs/planning/** - Planning documents

---

## Quick Reference

### Run Scraper
```bash
python main.py
```

### Run Watcher
```bash
python watcher.py --once
```

### Enable Sites
```bash
python scripts/enable_sites.py npc propertypro jiji
```

### Validate Config
```bash
python scripts/validate_config.py
```

### Check Health
```bash
python scripts/status.py
```

### Run Tests
```bash
python tests/test_watcher_integration.py
```

---

**Last Updated**: 2025-10-05
**Total Files**: 100+
**Total Lines**: ~10,000+
**Languages**: Python, YAML, Markdown
