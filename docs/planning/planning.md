# Planning Document - Nigerian Real Estate Scraper

## Vision

Build a robust, scalable, and maintainable web scraping system for aggregating Nigerian real estate listings from multiple sources with minimal manual configuration. The system should be:

- **Dynamic**: Add/remove sites via configuration without code changes
- **Reliable**: Handle site failures gracefully with fallback mechanisms
- **Efficient**: Minimize redundant requests, cache geocoding results, respect rate limits
- **Maintainable**: Clear separation of concerns, standardized data schema
- **Focused**: Filter and enrich Lagos-area property data for market analysis

## Current State Analysis

### What Works Well
- ✅ Multi-site scraping infrastructure (50+ sites configured)
- ✅ Fallback scraping strategies (requests → playwright → scraperapi)
- ✅ Data normalization pipeline with comprehensive schema
- ✅ Geocoding with caching and rate limiting
- ✅ Dual export format (CSV + XLSX)
- ✅ Lagos-specific filtering
- ✅ Retry logic with configurable timeouts
- ✅ Config-driven parser (`parsers/specials.py`)

### Current Limitations
- ⚠️ Site list hard-coded in `main.py` (SITES dict, ENABLED_SITES list)
- ⚠️ Partial config.yaml exists but isn't fully utilized by main.py
- ⚠️ Enabling/disabling sites requires code changes
- ⚠️ Site-specific parameters scattered across multiple files
- ⚠️ No centralized site status tracking
- ⚠️ Missing validation for site configurations

## Architecture

### High-Level Data Flow

```
config.yaml (Sites + Settings)
    ↓
main.py (Orchestrator)
    ↓
core/dispatcher.py (Parser Resolution)
    ↓
parsers/* (Site-specific/Generic Scrapers)
    ↓
core/scraper_engine.py (Playwright/Requests)
    ↓
core/cleaner.py (Normalization)
    ↓
core/geo.py (Geocoding)
    ↓
core/exporter.py (CSV/XLSX Output)
```

### Key Components

#### 1. Configuration Layer (config.yaml)
**Current State**: Partially implemented, contains site list and some settings
**Target State**: Single source of truth for all sites and runtime parameters

```yaml
# Global settings
fallback_order: [requests, playwright, scraperapi]
geocoding:
  enabled: true
  max_per_run: 120
pagination:
  max_pages: 30
  scroll_steps: 12

# Per-site configurations
sites:
  npc:
    name: Nigeria Property Centre
    url: https://nigeriapropertycentre.com/
    enabled: true
    parser: specials
    selectors:
      card: "li.property-list"
      title: "h2"
      price: ".price"
      # ... etc
```

#### 2. Main Orchestrator (main.py)
- Read config.yaml dynamically
- Filter enabled sites
- Execute scraping pipeline per site
- Aggregate and report results

#### 3. Parser Layer
- **dispatcher.py**: Route to appropriate parser based on config
- **specials.py**: Generic config-driven parser (already exists)
- **Site-specific parsers**: Override for complex cases

#### 4. Data Processing
- **cleaner.py**: Normalize to standard schema
- **geo.py**: Geocode with caching
- **utils.py**: Common helpers (Lagos filter, price parsing)

#### 5. Output Layer
- **exporter.py**: CSV/XLSX generation
- **File structure**: `exports/<site>/<timestamp>_<site>.[csv|xlsx]`

## Technology Stack

### Core Languages & Frameworks
- **Python 3.9+**: Main runtime
- **BeautifulSoup4 + lxml**: HTML parsing
- **Playwright**: Browser automation for JavaScript-heavy sites
- **Requests**: HTTP client for simple sites

### Data Processing
- **PyYAML**: Configuration file parsing
- **openpyxl**: Excel file generation
- **csv**: CSV file handling (stdlib)

### External Services
- **OpenStreetMap Nominatim**: Geocoding API (free, rate-limited)
- **ScraperAPI** (optional): Fallback for difficult sites

### Development Tools
- **python-dotenv**: Environment variable management
- **logging**: Built-in Python logging
- **Git**: Version control

## Required Tools & Dependencies

### Python Packages (requirements.txt)
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
playwright>=1.40.0
pyyaml>=6.0.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

### System Requirements
- **Python 3.9+**
- **Git** for version control
- **Playwright browsers**: `playwright install chromium`
- **Disk space**: ~500MB for dependencies + browser binaries

### Optional Tools
- **ScraperAPI account**: For enhanced anti-bot bypass
- **Text editor**: VS Code, PyCharm, or similar

## Implementation Strategy

### Phase 1: Config-Driven Site Management ✅ (Partially Complete)
- [x] config.yaml with site definitions exists
- [ ] Migrate SITES dict from main.py to config.yaml exclusively
- [ ] Read enabled_sites from config dynamically
- [ ] Validate config on startup

### Phase 2: Enhanced Site Configuration
- [ ] Per-site retry settings
- [ ] Per-site timeout overrides
- [ ] Site-specific geocoding preferences
- [ ] Custom export formats per site

### Phase 3: Monitoring & Reliability
- [ ] Track success/failure rates per site
- [ ] Alert on consecutive failures
- [ ] Export metadata (scrape duration, item count)
- [ ] Health check endpoint/command

### Phase 4: Performance Optimization
- [ ] Parallel site scraping (threading/async)
- [ ] Smart pagination (stop on duplicate detection)
- [ ] Incremental exports (append mode)
- [ ] Database backend option (SQLite/PostgreSQL)

## Success Metrics

### Functional Requirements
- ✅ Add new site by editing config.yaml only (no code changes)
- ✅ Enable/disable sites via config flag
- ✅ All existing 50 sites work with new config system
- ✅ Backward compatible with existing exports

### Performance Requirements
- Scrape 50 sites in < 60 minutes (with current pagination limits)
- Geocoding cache hit rate > 80% on subsequent runs
- Zero data loss on partial failures

### Code Quality
- All configuration in config.yaml (no hard-coded URLs in .py files)
- Pass validation on startup (invalid configs rejected early)
- Clear error messages for configuration issues
- Comprehensive logging for debugging

## Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Sites change structure | Medium | Generic fallback scraper, per-site retries |
| Rate limiting/blocking | High | Multi-strategy fallback, respectful delays |
| Geocoding API limits | Medium | Persistent cache, configurable caps |
| Invalid config breaks all sites | High | Validation on startup, schema enforcement |

### Operational Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Config file corruption | Medium | Git version control, validation |
| Disk space exhaustion | Low | Rotate old exports, configurable retention |
| API key exposure | Medium | Environment variables, .gitignore |

## Future Enhancements

### Short-term (1-3 months)
- Web dashboard for monitoring scrape status
- Email/Slack notifications on failures
- Deduplication across sites (by listing URL/hash)
- Price trend tracking over time

### Long-term (6-12 months)
- Machine learning for property valuation
- Automated listing categorization (luxury, affordable, etc.)
- API for external consumption
- Multi-region support (beyond Lagos)
- Real-time scraping with webhooks
