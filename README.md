# Nigerian Real Estate Scraper

Enterprise-grade property aggregation platform that scrapes 51 real estate websites, enriches data with enterprise schema (9 categories, 85+ fields), and provides 84 REST API endpoints for frontend integration. Fully production-ready with GitHub Actions automation and Firestore integration.

## 🎯 Current Status

✅ **PRODUCTION READY** - All systems tested and verified (2025-11-16)

**Key Metrics**:
- **Sites Configured**: 51 active real estate websites
- **API Endpoints**: 84 total (68 core + 16 Firestore)
- **Data Storage**: Firestore (enterprise schema)
- **Automation**: GitHub Actions (auto-scaling multi-session)
- **Frontend Ready**: Complete TypeScript integration

**Latest Achievement**: Successfully running large-scale scrape of all 51 sites via GitHub Actions (Run #19408262700)

---

## 🚀 Quick Start

### For Frontend Developers (START HERE)

**📖 Complete Setup Guide**: [frontend/README.md](frontend/README.md)

```typescript
// Install and start using in 3 lines
import { useProperties } from '@/hooks/useProperties';

export default function PropertiesPage() {
  const { properties, loading } = useProperties();
  return <PropertyList properties={properties} />;
}
```

**What's Included**:
- ✅ TypeScript types for all 84 endpoints
- ✅ React hooks with SWR
- ✅ API client with error handling
- ✅ Complete documentation
- ✅ Integration examples

**Frontend Developer Resources**:
- 📚 [Complete Setup Guide](frontend/README.md) - Step-by-step integration
- 📋 [All 84 API Endpoints](frontend/API_ENDPOINTS_ACTUAL.md) - Full reference
- 🔧 [TypeScript Types](frontend/types.ts) - Type definitions
- 🌐 [API Client](frontend/api-client.ts) - HTTP client
- ⚛️ [React Hooks](frontend/hooks.tsx) - Data fetching hooks

---

### For Backend Developers

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Start API server
python api_server.py

# 3. Test scraper (small batch)
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 2, "geocoding": false}'

# 4. Monitor progress
curl http://localhost:5000/api/scrape/status

# 5. Run integration tests
python test_scraper_integration.py --skip-scrape
```

---

## 📊 Features

### Core Functionality

**✅ Web Scraping**
- 51 real estate websites supported
- Adaptive scraping (requests → playwright → scraperapi fallback)
- Detail page enrichment (parallel & sequential modes)
- Auto-retry on failures with exponential backoff

**✅ Data Processing**
- Enterprise schema with 9 categories, 85+ fields
- Quality scoring (0-100%) with configurable threshold
- Duplicate detection using SHA256 hashing
- Lagos-only filtering with landmark detection

**✅ Data Storage**
- **Primary**: Firestore (enterprise schema)
- **Backup**: CSV/XLSX exports (master workbook)
- Auto-deduplication across all sources
- Historical data tracking

**✅ REST API** (84 Endpoints)
- Scraping Management (5 endpoints)
- Site Configuration (6 endpoints)
- Data Access (4 endpoints)
- Firestore Queries (16 endpoints)
- GitHub Actions Integration (4 endpoints)
- Price Intelligence (4 endpoints)
- Saved Searches (5 endpoints)
- Email Notifications (5 endpoints)
- Additional Features (35 endpoints)

**✅ Automation**
- GitHub Actions workflows (auto-scaling)
- Scheduled scraping (cron support)
- Email notifications on completion
- Artifact management (30-day retention)

---

## 🏗️ Architecture

### Enterprise Data Schema

**9 Categories, 85+ Fields**:

```typescript
interface Property {
  basic_info: {
    title: string;
    source: string;
    status: 'for_sale' | 'for_rent' | 'sold';
    listing_type: 'sale' | 'rent' | 'land';
  };
  property_details: {
    property_type: string;
    bedrooms: number;
    bathrooms: number;
    furnishing: 'furnished' | 'semi-furnished' | 'unfurnished';
  };
  financial: {
    price: number;
    currency: string;
    price_per_sqm: number;
    price_per_bedroom: number;
  };
  location: {
    address: string;
    area: string;
    lga: string;
    state: string;
    coordinates: GeoPoint;
    landmarks: string[];
  };
  amenities: {
    features: string[];
    security: string[];
    utilities: string[];
  };
  media: {
    images: Image[];
    videos: string[];
    virtual_tour: string;
  };
  agent_info: {
    name: string;
    contact: string;
    agency: string;
  };
  metadata: {
    quality_score: number;
    view_count: number;
    search_keywords: string[];
  };
  tags: {
    premium: boolean;
    hot_deal: boolean;
    featured: boolean;
  };
}
```

### API Architecture

**84 Endpoints Organized by Category**:

1. **Scraping Management** (5 endpoints)
   - Start, stop, pause, resume, status

2. **Site Configuration** (6 endpoints)
   - List, get, add, update, delete, toggle sites

3. **Data Access** (4 endpoints)
   - List files, get site data, master data, search

4. **Firestore Integration** (16 endpoints)
   - Dashboard, filters, search, site queries

5. **GitHub Actions** (4 endpoints)
   - Trigger workflows, get runs, artifacts

6. **Price Intelligence** (4 endpoints)
   - Price trends, history, alerts

7. **Saved Searches** (5 endpoints)
   - Create, list, execute, update, delete

8. **Email Notifications** (5 endpoints)
   - Configure, send, subscriptions

**Full API Documentation**: [frontend/API_ENDPOINTS_ACTUAL.md](frontend/API_ENDPOINTS_ACTUAL.md)

---

## 📁 Project Structure

```
realtors_practice/
├── main.py                      # Scraper entry point
├── api_server.py                # REST API server (84 endpoints)
├── watcher.py                   # Export watcher service
├── config.yaml                  # Site configuration (51 sites)
│
├── core/                        # Core scraping modules
│   ├── scraper_engine.py        # Adaptive fetching (requests/playwright)
│   ├── cleaner.py               # Data normalization
│   ├── geo.py                   # Geocoding with OpenStreetMap
│   ├── firestore_enterprise.py  # Enterprise schema upload
│   └── [15+ other modules]
│
├── parsers/                     # Site-specific parsers
│   └── specials.py              # Generic config-driven parser
│
├── api/helpers/                 # API helper modules
│   ├── scraper_manager.py       # Intelligent batch management
│   ├── data_reader.py           # Data access layer
│   ├── config_manager.py        # Config manipulation
│   └── stats_generator.py       # Statistics generation
│
├── frontend/                    # Frontend integration files
│   ├── README.md                # Frontend developer guide
│   ├── API_ENDPOINTS_ACTUAL.md  # Complete API reference
│   ├── types.ts                 # TypeScript definitions
│   ├── api-client.ts            # HTTP client
│   └── hooks.tsx                # React hooks
│
├── docs/                        # Documentation
│   ├── README.md                # Documentation index
│   ├── FINAL_SUMMARY_V3.1.md    # Complete project summary
│   ├── setup-guides/            # Setup and workflow guides
│   ├── reports/                 # Verification and test reports
│   └── [architecture, backend-only, frontend folders]
│
├── .github/workflows/           # GitHub Actions
│   ├── scrape-production.yml    # Auto-scaling multi-session
│   └── test-quick-scrape.yml    # Quick testing workflow
│
├── scripts/                     # Utility scripts
│   ├── enable_sites.py          # Enable multiple sites
│   ├── enable_one_site.py       # Enable single site
│   └── validate_config.py       # Config validation
│
├── tests/                       # Test suites
│   └── [20+ test files]
│
├── exports/                     # Scraped data (gitignored)
│   ├── sites/                   # Per-site exports
│   └── cleaned/                 # Master workbook
│
└── logs/                        # Logs (gitignored)
    ├── scraper.log              # Main log file
    ├── geocache.json            # Geocoding cache
    └── site_metadata.json       # Site statistics
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Scraping
RP_PAGE_CAP=20              # Max pages per site
RP_GEOCODE=1                # Enable geocoding (1=yes, 0=no)
RP_HEADLESS=1               # Headless browser mode
RP_DEBUG=0                  # Debug logging

# Firestore
FIREBASE_SERVICE_ACCOUNT=path/to/credentials.json
FIRESTORE_ENABLED=1

# GitHub Actions
GITHUB_TOKEN=ghp_xxx        # For API integration
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo
```

### Site Configuration (config.yaml)

```yaml
sites:
  npc:
    name: "Nigeria Property Centre"
    url: "https://nigeriapropertycentre.com"
    enabled: true
    parser: specials
    overrides:
      max_pages: 30  # Site-specific override
      geocoding: true
```

**Adding New Sites**: Just add to config.yaml - no code changes needed!

---

## 🚀 Deployment

### GitHub Actions (Recommended for Large Scrapes)

**Trigger Production Scrape**:
```bash
# Via GitHub UI
Go to: Actions → Production Scraper → Run workflow

# Via API
curl -X POST http://localhost:5000/api/github/trigger-scrape \
  -H "Content-Type: application/json" \
  -d '{"sites_per_session": 20, "page_cap": 20}'
```

**Features**:
- Auto-scaling: 3 parallel sessions for 51 sites
- Estimated time: 1-2 hours (vs 3-4 hours sequential)
- Automatic Firestore upload
- Artifact retention: 30 days

**Setup Guide**: [docs/setup-guides/GITHUB_ACTIONS_SETUP.md](docs/setup-guides/GITHUB_ACTIONS_SETUP.md)

### Local Deployment

```bash
# Start API server
python api_server.py

# Access at: http://localhost:5000
```

---

## 📚 Documentation

### For Frontend Developers
- 📖 [Frontend Setup Guide](frontend/README.md) - Complete integration guide
- 📋 [API Endpoints Reference](frontend/API_ENDPOINTS_ACTUAL.md) - All 84 endpoints
- 🎯 [Quick Integration Examples](frontend/README.md#quick-start)

### For Backend Developers
- 📖 [Complete Project Summary](docs/FINAL_SUMMARY_V3.1.md) - V3.1 overview
- 🏗️ [Architecture Documentation](docs/README.md) - System architecture
- 🔧 [GitHub Actions Setup](docs/setup-guides/GITHUB_ACTIONS_SETUP.md) - Workflow automation
- 📊 [Enterprise Schema Guide](docs/ENTERPRISE_SCHEMA_EXPLAINED.md) - Data structure

### Verification Reports
- ✅ [Integration Verification](docs/reports/SCRAPER_INTEGRATION_VERIFIED.md) - Full test report
- ✅ [Verification Complete](docs/reports/VERIFICATION_COMPLETE.md) - Production readiness
- ✅ [API Test Report](docs/reports/API_ENDPOINT_TEST_REPORT.md) - Endpoint testing

---

## 🧪 Testing

### Quick API Test
```bash
# Health check
curl http://localhost:5000/api/health

# List sites
curl http://localhost:5000/api/sites

# Small batch scrape
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 2, "geocoding": false}'
```

### Automated Tests
```bash
# Run integration tests (API only)
python test_scraper_integration.py --skip-scrape

# Run small batch test
python test_scraper_integration.py --small-batch-only

# Run all tests
pytest tests/
```

---

## 🔍 Monitoring

### Real-time Progress
```bash
# Via API
curl http://localhost:5000/api/scrape/status

# Via monitoring script
python monitor_workflow.py
```

### GitHub Actions Workflow
- Live logs: https://github.com/Tee-David/realtors_practice/actions
- Current run: #19408262700 (IN PROGRESS)
- Expected completion: 1-2 hours

---

## 🎓 Key Features Explained

### Intelligent Batching
Automatically splits sites into optimal batches based on count:
- ≤10 sites: No batching
- 11-30 sites: 10 per batch
- 31-50 sites: 15 per batch
- 51+ sites: 20 per batch

### Quality Filtering
Scores listings 0-100% based on:
- Completeness (has price, location, images)
- Validity (realistic price ranges)
- Detail richness (description length, features)

Default threshold: 40% (configurable)

### Auto-detection
Automatically infers from listing text:
- `listing_type`: sale, rent, or land
- `furnishing`: furnished, semi-furnished, unfurnished
- `condition`: new, renovated, or existing

### Firestore Integration
- **Primary storage**: All scraped data uploaded
- **Enterprise schema**: 9 categories, 85+ fields
- **16 query endpoints**: Optimized for frontend
- **Real-time**: Data available immediately

---

## 🤝 Contributing

### Adding New Sites
1. Add to `config.yaml`:
   ```yaml
   newsite:
     name: "New Site"
     url: "https://example.com"
     enabled: true
     parser: specials
   ```
2. No code changes needed!
3. Test: `python scripts/enable_one_site.py newsite && python main.py`

### Reporting Issues
- GitHub Issues: https://github.com/Tee-David/realtors_practice/issues
- Include: Site name, error logs, config used

---

## 📄 License

This project is private and proprietary.

---

## 📞 Support

**Documentation**: See `docs/` folder for complete guides
**API Reference**: See `frontend/API_ENDPOINTS_ACTUAL.md`
**Setup Help**: See `docs/setup-guides/GITHUB_ACTIONS_SETUP.md`

---

## 🎯 Quick Links

- 🏠 [Frontend Setup](frontend/README.md) - For developers integrating the API
- 📚 [Complete API Reference](frontend/API_ENDPOINTS_ACTUAL.md) - All 84 endpoints
- 🔧 [GitHub Actions Guide](docs/setup-guides/GITHUB_ACTIONS_SETUP.md) - Automation setup
- ✅ [Verification Report](docs/reports/VERIFICATION_COMPLETE.md) - Production readiness
- 📊 [Project Summary](docs/FINAL_SUMMARY_V3.1.md) - V3.1 overview

---

**Version**: 3.1.0 (Enterprise Firestore)
**Status**: ✅ Production Ready
**Last Updated**: 2025-11-16
**Last Verified**: 2025-11-16 (All systems tested and working)
