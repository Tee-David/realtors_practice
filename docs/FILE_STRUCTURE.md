# Project File Structure

Clean, organized file structure for the Nigerian Real Estate Scraper project.

**Last Updated:** 2025-10-13 (After cleanup and API integration)

---

## Root Directory

```
realtors_practice/
├── main.py                    # Main scraper entry point
├── watcher.py                 # Export watcher service
├── api_server.py              # Flask REST API server
├── config.yaml                # Active configuration (gitignored)
├── config.example.yaml        # Configuration template
├── requirements.txt           # Python dependencies
├── CLAUDE.md                  # AI assistant project context
├── README.md                  # Main project documentation
├── .gitignore                 # Git ignore rules
└── .git/                      # Git repository
```

**What belongs in root:**
- ✅ Main executable scripts (main.py, watcher.py, api_server.py)
- ✅ Configuration files (config.yaml, config.example.yaml)
- ✅ Essential documentation (README.md, CLAUDE.md)
- ✅ Project metadata (requirements.txt, .gitignore)

**What does NOT belong in root:**
- ❌ Detailed documentation (moved to docs/)
- ❌ Backup files (.backup)
- ❌ Temporary files (__pycache__)
- ❌ Test files (moved to tests/)
- ❌ Utility scripts (moved to scripts/)

---

## Core Modules (`core/`)

Application logic and business functionality.

```
core/
├── __init__.py
├── config_loader.py           # Configuration management
├── scraper_engine.py          # Generic web scraping engine
├── dispatcher.py              # Parser dispatch system
├── cleaner.py                 # Data normalization
├── geo.py                     # Geocoding service
├── exporter.py                # Export to CSV/XLSX
├── utils.py                   # Utility functions
├── captcha.py                 # Captcha handling (unused)
├── data_cleaner.py            # Advanced data cleaning (watcher)
└── master_workbook.py         # Master workbook management
```

**Purpose:** Core business logic, reusable across the application.

---

## API Modules (`api/`)

REST API server and helper modules for frontend integration.

```
api/
├── __init__.py
└── helpers/
    ├── __init__.py
    ├── data_reader.py         # Read and query Excel/CSV data
    ├── log_parser.py          # Parse and filter logs
    ├── config_manager.py      # Manage config.yaml programmatically
    ├── scraper_manager.py     # Manage scraping processes
    └── stats_generator.py     # Generate statistics
```

**Purpose:** API-specific logic for frontend integration.

---

## Parsers (`parsers/`)

Site-specific web scraping parsers.

```
parsers/
├── __init__.py
├── specials.py                # Config-driven generic parser (50+ sites)
├── npc.py                     # Nigeria Property Centre
├── propertypro.py             # PropertyPro
├── jiji.py                    # Jiji
├── property24.py              # Property24
├── lamudi.py                  # Lamudi
├── hutbay.py                  # Hutbay
└── [50+ site parsers].py      # Other site-specific parsers
```

**Purpose:** Site-specific scraping logic, mostly thin wrappers around specials.py.

---

## Scripts (`scripts/`)

Utility scripts for management and maintenance.

```
scripts/
├── enable_sites.py            # Enable multiple sites at once
├── enable_one_site.py         # Enable single site for testing
├── validate_config.py         # Validate configuration
└── status.py                  # Site health dashboard
```

**Purpose:** Command-line utilities for configuration and monitoring.

---

## Tests (`tests/`)

Test suite for integration and unit testing.

```
tests/
├── test_watcher_integration.py    # Watcher service integration tests
├── test_milestone3.py             # Parser integration tests
├── test_milestone4_5.py           # Config system tests
├── test_site_specific.py          # Site configuration tests
├── test_config_validation.py      # Config validation tests
└── test_main_integration.py       # Main scraper integration tests
```

**Purpose:** Automated testing for quality assurance.

**Test Results:** 57/58 tests passing (98.3%)

---

## Documentation (`docs/`)

Project documentation organized by category.

```
docs/
├── README.md                      # Documentation index
│
├── guides/                        # User guides and tutorials
│   ├── QUICKSTART.md             # Quick start guide
│   ├── WATCHER_QUICKSTART.md     # Watcher quick start
│   ├── WATCHER_COMPLETE.md       # Complete watcher docs
│   ├── MIGRATION_GUIDE.md        # Migration guide
│   ├── HARD_CODED_CONFIGS_REMOVED.md
│   ├── API_README.md             # API overview
│   ├── API_QUICKSTART.md         # API quick start
│   └── FRONTEND_INTEGRATION.md   # Complete frontend integration guide (1,100+ lines)
│
├── milestones/                    # Milestone completion docs
│   ├── MILESTONE_2_COMPLETE.md
│   ├── MILESTONE_3_COMPLETE.md
│   ├── MILESTONE_4_5_COMPLETE.md
│   ├── MILESTONE_9_10_11_COMPLETE.md
│   └── PROJECT_COMPLETE.md
│
├── planning/                      # Planning and design docs
│   ├── tasks.md                  # Task list and roadmap
│   ├── planning.md               # Project planning
│   ├── prompt.md                 # Original project prompt
│   ├── direction.txt             # Project direction notes
│   └── future_integrations.md   # Future integration plans
│
├── STRUCTURE.md                   # Project structure (this file's predecessor)
├── COMPATIBILITY.md               # cPanel & Firebase compatibility
├── REORGANIZATION_COMPLETE.md     # Reorganization summary
└── FILE_STRUCTURE.md              # This file
```

**Documentation Categories:**
- **guides/** - User-facing how-to guides
- **milestones/** - Historical milestone completion records
- **planning/** - Internal planning and design documents
- **Root docs/** - Major architectural documentation

---

## Exports (`exports/`)

Scraped data storage (gitignored).

```
exports/
├── sites/                     # Raw scraper exports
│   ├── npc/
│   │   ├── 2025-10-13_10-30-00_npc.csv
│   │   └── 2025-10-13_10-30-00_npc.xlsx
│   ├── propertypro/
│   ├── jiji/
│   └── ... (50+ site folders)
│
└── cleaned/                   # Cleaned & consolidated data
    ├── MASTER_CLEANED_WORKBOOK.xlsx
    ├── metadata.json
    ├── .watcher_state.json
    ├── watcher.log
    ├── errors.log
    ├── npc/
    │   ├── npc_cleaned.csv
    │   └── npc_cleaned.parquet
    └── ... (per-site cleaned exports)
```

**Purpose:** Data storage for raw and processed scraping results.

**Note:** This directory is gitignored and created automatically.

---

## Logs (`logs/`)

Application logs and caches (gitignored).

```
logs/
├── scraper.log                # Main scraper log
├── geocache.json              # Geocoding cache
├── site_metadata.json         # Site scraping metadata
└── scraper_state.json         # Scraper state tracking
```

**Purpose:** Runtime logs and persistent caches.

**Note:** This directory is gitignored and created automatically.

---

## Virtual Environment (`venv/`)

Python virtual environment (gitignored).

```
venv/
├── Scripts/                   # (Windows) or bin/ (Linux/Mac)
├── Lib/                       # Python packages
└── pyvenv.cfg                 # Virtual environment config
```

**Purpose:** Isolated Python environment for dependencies.

**Note:** Created with `python -m venv venv`, always gitignored.

---

## Hidden Directories

### `.git/`
Git version control repository. Standard git structure.

### `.claude/`
Claude Code IDE configuration (if using Claude Code).

---

## File Naming Conventions

### Python Files
- **Lowercase with underscores:** `config_loader.py`, `scraper_engine.py`
- **Descriptive names:** Name reflects purpose/functionality
- **No abbreviations:** Use full words for clarity

### Documentation Files
- **UPPERCASE for major docs:** `README.md`, `STRUCTURE.md`, `COMPATIBILITY.md`
- **Descriptive titles:** `FRONTEND_INTEGRATION.md`, `API_QUICKSTART.md`
- **Category prefixes:** `MILESTONE_*.md`, `test_*.py`

### Configuration Files
- **Lowercase:** `config.yaml`, `requirements.txt`
- **Standard names:** Follow community conventions (.gitignore, pyproject.toml)

---

## Ignored Files (.gitignore)

Files and directories that should NOT be committed:

```
# Python
__pycache__/
*.pyc
*.pyo
venv/

# Project Data
logs/
exports/
config.yaml
*.backup

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

Full `.gitignore` in project root.

---

## Import Path Rules

### Absolute Imports (Preferred)
```python
from core.config_loader import load_config
from api.helpers.data_reader import DataReader
from parsers.specials import scrape
```

### Relative Imports (Within Package)
```python
# Inside core/
from .utils import is_lagos_like
from .config_loader import get_site_setting
```

### Path Additions (scripts/ and tests/)
Scripts and tests add parent directory to path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## Size Guidelines

### Total Project Size
- **Code:** ~10,000 lines of Python
- **Documentation:** ~5,000 lines of Markdown
- **Dependencies:** ~300 MB (venv)
- **Exports:** Variable (user data)

### File Size Limits
- **Python files:** < 1,000 lines (refactor if larger)
- **Documentation:** < 2,000 lines per file (split if larger)
- **Configuration:** < 500 lines (keep readable)

---

## Quick Reference

### Where to Find Things

| What | Where |
|------|-------|
| Main scraper | `main.py` |
| API server | `api_server.py` |
| Watcher service | `watcher.py` |
| Configuration | `config.yaml` |
| Core logic | `core/` |
| Site parsers | `parsers/` |
| API helpers | `api/helpers/` |
| Utility scripts | `scripts/` |
| Tests | `tests/` |
| Documentation | `docs/` |
| Scraped data | `exports/` |
| Logs | `logs/` |

### Key Commands

```bash
# Run scraper
python main.py

# Run watcher
python watcher.py --once

# Run API server
python api_server.py

# Enable sites
python scripts/enable_sites.py npc propertypro

# Validate config
python scripts/validate_config.py

# Check site health
python scripts/status.py
```

---

## Best Practices

### File Organization
1. ✅ Keep root directory clean (< 20 files)
2. ✅ Group related files in folders
3. ✅ Use descriptive names
4. ✅ Follow naming conventions
5. ✅ Document directory purposes

### Module Structure
1. ✅ One module per file
2. ✅ Clear separation of concerns
3. ✅ Reusable components in core/
4. ✅ Site-specific logic in parsers/
5. ✅ No circular dependencies

### Documentation
1. ✅ README.md for project overview
2. ✅ Detailed docs in docs/
3. ✅ Code comments for complex logic
4. ✅ Docstrings for all functions
5. ✅ Keep docs up-to-date

---

**Status:** ✅ Clean and Organized | **Last Cleanup:** 2025-10-13
