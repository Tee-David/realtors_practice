# Nigerian Real Estate Scraper

> Comprehensive web scraper for aggregating property listings from 50+ Nigerian real estate websites, with intelligent data cleaning and export consolidation.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install pyyaml beautifulsoup4 openpyxl playwright requests pandas

# 2. Install browser for Playwright
playwright install chromium

# 3. Configure sites (optional)
cp config.example.yaml config.yaml

# 4. Run scraper
python main.py

# 5. Process exports
python watcher.py --once
```

## 📁 Project Structure

```
realtors_practice/
├── main.py                    # Main scraper entry point
├── watcher.py                # Export watcher service
├── config.yaml               # Configuration file
├── CLAUDE.md                 # AI assistant context
│
├── core/                     # Core modules
│   ├── config_loader.py     # Configuration management
│   ├── scraper_engine.py    # Generic scraping engine
│   ├── dispatcher.py        # Parser dispatch system
│   ├── cleaner.py          # Data normalization
│   ├── geo.py              # Geocoding service
│   ├── exporter.py         # Export to CSV/XLSX
│   ├── utils.py            # Utility functions
│   ├── data_cleaner.py     # Advanced data cleaning
│   └── master_workbook.py  # Master workbook management
│
├── parsers/                  # Site-specific parsers
│   ├── specials.py         # Config-driven parser (50+ sites)
│   └── [site].py           # Site-specific modules
│
├── scripts/                  # Utility scripts
│   ├── enable_sites.py     # Enable multiple sites
│   ├── enable_one_site.py  # Enable single site
│   ├── validate_config.py  # Validate configuration
│   └── status.py           # Site health dashboard
│
├── tests/                    # Test suite
│   ├── test_watcher_integration.py
│   ├── test_milestone*.py
│   └── test_*.py
│
├── docs/                     # Documentation
│   ├── guides/              # User guides
│   │   ├── QUICKSTART.md
│   │   ├── MIGRATION_GUIDE.md
│   │   ├── WATCHER_QUICKSTART.md
│   │   └── WATCHER_COMPLETE.md
│   ├── milestones/          # Milestone completion docs
│   │   └── MILESTONE_*.md
│   └── planning/            # Planning documents
│       ├── tasks.md
│       └── planning.md
│
├── exports/                  # Export data
│   ├── sites/               # Raw scraper exports
│   │   ├── npc/
│   │   ├── propertypro/
│   │   └── ...
│   └── cleaned/             # Cleaned & consolidated data
│       ├── MASTER_CLEANED_WORKBOOK.xlsx
│       ├── metadata.json
│       ├── [site]/
│       │   ├── [site]_cleaned.csv
│       │   └── [site]_cleaned.parquet
│       └── ...
│
└── logs/                     # Application logs
    ├── scraper.log
    ├── geocache.json
    └── site_metadata.json
```

## 🎯 Core Features

### 1. Web Scraping
- **50+ sites supported** (Nigeria Property Centre, PropertyPro, Jiji, etc.)
- **Config-driven architecture** - Add new sites via YAML
- **Adaptive fetching** - Requests → Playwright fallback
- **Lagos-focused** - Filters for Lagos area properties only
- **Pagination** - Automatic page traversal

### 2. Data Processing
- **Normalization** - Standardizes fields (price, location, property_type)
- **Geocoding** - OpenStreetMap Nominatim integration
- **Deduplication** - Hash-based duplicate removal
- **Validation** - Schema validation & data quality metrics

### 3. Export Watcher Service
- **Monitors** `exports/sites/` for new CSV/XLSX files
- **Cleans** data with intelligent fuzzy matching
- **Consolidates** into `MASTER_CLEANED_WORKBOOK.xlsx`
- **Exports** to CSV and Parquet formats
- **Idempotent** - Safe to run multiple times

### 4. Configuration Management
- **YAML-based** - All sites in `config.yaml`
- **Per-site overrides** - Custom settings per site
- **Environment variables** - Runtime configuration
- **Validation** - Pre-flight config checks

## 📖 Usage

### Basic Scraping

```bash
# Scrape all enabled sites
python main.py

# Enable specific sites only
python scripts/enable_sites.py npc propertypro jiji
python main.py

# Enable one site for testing
python scripts/enable_one_site.py npc
python main.py
```

### Environment Variables

```bash
# Windows
set RP_DEBUG=1              # Enable debug logging
set RP_HEADLESS=0           # Show browser window
set RP_GEOCODE=1            # Enable geocoding
set RP_PAGE_CAP=20          # Max pages per site
set RP_MAX_GEOCODES=200     # Max geocoding requests

# Linux/Mac
export RP_DEBUG=1
export RP_HEADLESS=0
# ... etc
```

### Export Processing

```bash
# Process all exports once
python watcher.py --once

# Continuous monitoring (daemon mode)
python watcher.py --watch

# Preview without writing
python watcher.py --dry-run --once

# Reset and reprocess all
python watcher.py --reset-state
python watcher.py --once
```

### Validation & Monitoring

```bash
# Validate configuration
python scripts/validate_config.py

# Check site health
python scripts/status.py

# Run tests
python tests/test_watcher_integration.py
```

## 🔧 Configuration

### config.yaml Structure

```yaml
global_settings:
  geocoding:
    enabled: true
    max_per_run: 120
  pagination:
    max_pages: 30
    scroll_steps: 12
  retry:
    network_retry_seconds: 180
    retry_on_zero_results: true
  export:
    formats: ["csv", "xlsx"]
  browser:
    headless: true
    block_images: true

sites:
  npc:
    name: "Nigeria Property Centre"
    url: "https://nigeriapropertycentre.com"
    enabled: true
    parser: specials
    selectors:
      card: "div.listing"
      title: "h2.title"
      price: ".price"
      location: ".location"
    pagination:
      next_selectors: ["a.next", "a[rel='next']"]
      page_param: "page"
    overrides:
      network_retry_seconds: 300
      max_pages: 50
```

## 📊 Data Schema

All listings normalized to canonical schema:

```python
{
  'title': str,
  'price': str,
  'location': str,
  'property_type': str,
  'bedrooms': int,
  'bathrooms': int,
  'land_size': str,
  'description': str,
  'agent_name': str,
  'images': List[str],
  'listing_url': str,
  'coordinates': Dict[str, float],
  'source': str,
  'scrape_timestamp': str,
  'hash': str,
  # ... 27 total fields
}
```

## 🧪 Testing

```bash
# Run all integration tests
cd tests
python test_watcher_integration.py      # Watcher service tests
python test_milestone4_5.py             # Config system tests
python test_site_specific.py            # Site config tests

# Test results: 57/58 tests passing (98.3%)
```

## 📚 Documentation

**Getting Started:**
- **[QUICKSTART.md](docs/guides/QUICKSTART.md)** - Quick start guide for scraper
- **[WATCHER_QUICKSTART.md](docs/guides/WATCHER_QUICKSTART.md)** - Quick start for watcher service
- **[API_QUICKSTART.md](docs/guides/API_QUICKSTART.md)** - API quick start

**Integration Guides:**
- **[FRONTEND_INTEGRATION.md](docs/guides/FRONTEND_INTEGRATION.md)** - Complete Next.js integration guide
- **[MIGRATION_GUIDE.md](docs/guides/MIGRATION_GUIDE.md)** - Migration to config-driven system

**Architecture:**
- **[CLAUDE.md](CLAUDE.md)** - AI assistant context & project overview
- **[STRUCTURE.md](docs/STRUCTURE.md)** - Detailed project architecture
- **[FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md)** - Clean file organization reference
- **[COMPATIBILITY.md](docs/COMPATIBILITY.md)** - Firebase deployment compatibility

## 🚀 Deployment

### FREE Deployment Options (No Cost!) 💰

**🏆 RECOMMENDED**: See **[FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md)** - Complete guide to FREE deployment

**Top FREE Options**:

1. **⭐ GitHub Actions** (Best for most users)
   - ✅ $0/month - Completely FREE
   - ✅ 2000 minutes/month free
   - ✅ No credit card required
   - ✅ Scheduled scraping (cron)
   - ✅ 15-minute setup
   - **Perfect for**: Daily/weekly scraping

2. **🌐 Oracle Cloud Always Free**
   - ✅ $0/month - FREE forever
   - ✅ 1-4 CPUs, 6-24GB RAM free
   - ✅ Can run 24/7
   - ⚠️ Requires credit card verification (never charges)
   - **Perfect for**: 24/7 availability or API hosting

3. **💻 Local Machine**
   - ✅ $0/month - Completely FREE
   - ✅ Full control
   - ✅ 5-minute setup
   - ❌ Computer must stay on
   - **Perfect for**: Testing and development

**See [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) for complete setup guides for all FREE options!**

---

### Firebase Deployment (Paid, ~$1-5/month)

**Quick Start**: See **[FIREBASE_QUICKSTART.md](FIREBASE_QUICKSTART.md)** - Fast setup guide

**Complete Guide**: See **[docs/FIREBASE_DEPLOYMENT.md](docs/FIREBASE_DEPLOYMENT.md)** - Step-by-step deployment walkthrough

**What you get**:
- ✅ **Serverless** - No server management required
- ✅ **Cloud Functions** - Automated scheduled scraping
- ✅ **Cloud Storage** - Unlimited data storage with CDN
- ✅ **Scalable** - Auto-scales based on demand
- ✅ **Cost**: ~$1-5/month (pay-as-you-go)

**When to use Firebase**:
- Need enterprise-grade reliability
- Want global CDN for data access
- Integrating with Firebase-based frontend
- Need more than 2000 minutes/month

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_*.py`
5. Update documentation
6. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with: Python 3.8+, Playwright, BeautifulSoup4, Pandas, OpenPyXL
- Geocoding: OpenStreetMap Nominatim
- AI Assistance: Claude Code (Anthropic)

## 🔗 Links

- **GitHub**: [Repository Link]
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues]

---

**Status**: ✅ Production Ready | **Version**: 1.0 | **Last Updated**: 2025-10-05
