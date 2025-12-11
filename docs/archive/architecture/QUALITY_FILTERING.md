# Quality Filtering System

**Date**: 2025-10-21
**Status**: ✅ Implemented and Active

## Overview

Automatic quality filtering ensures only high-quality property listings are exported, protecting against incomplete or malformed data from scrapers.

## How It Works

### Quality Scoring (0-100%)

Each listing is scored based on field completeness:

**Required Fields (40 points)**:
- `title`, `price`, `location`, `listing_url`

**Recommended Fields (30 points)**:
- `bedrooms`, `bathrooms`, `property_type`, `images`

**Bonus Fields (30 points)**:
- `coordinates`, `land_size`, `description`, `contact_info`

### Quality Tiers

- **High Quality** (≥70%): Has required + most recommended fields
- **Medium Quality** (30-69%): Has required + some recommended fields
- **Low Quality** (<30%): Missing critical fields (REJECTED)

## Configuration

### Global Setting (config.yaml)

```yaml
quality:
  enabled: true
  min_quality_score: 30  # Reject listings below 30%
  export_quality_report: true
```

### Per-Site Overrides

```yaml
sites:
  propertypro:
    overrides:
      min_quality_score: 60  # Stricter for high-value site

  npc:
    overrides:
      min_quality_score: 30  # More lenient (or disable detail scraping)
```

### Environment Variable

```bash
set RP_MIN_QUALITY=50  # Override via environment
python main.py
```

## Real-World Test Results

### NPC (Nigeria Property Centre)
- **Scraped**: 3 listings
- **Average Quality**: 17.5%
- **Exported**: 0 listings (all rejected)
- **Reason**: Detail scraping failed - no data extracted

### CWLagos
- **Scraped**: 44 listings
- **Average Quality**: 76.9%
- **High Quality**: 34 listings (77%)
- **Medium Quality**: 9 listings (20%)
- **Low Quality**: 1 listing (2%)
- **Exported**: 43 listings (1 rejected)

### PropertyPro
- **Scraped**: 566 listings
- **Quality**: Mixed (detail scraping partial)
- **Action Needed**: Add site-specific selectors

## Benefits

### 1. Data Integrity
- ✅ No more NaN-filled exports
- ✅ Listings must have minimum required fields
- ✅ Protects master workbook from junk data

### 2. Visibility
- ✅ Identifies problematic sites automatically
- ✅ Shows which sites need selector improvements
- ✅ Quality stats in logs

### 3. Dynamic & Maintainable
- ✅ No hard-coding - configuration-driven
- ✅ Per-site flexibility
- ✅ Easy to adjust thresholds

## Handling Low-Quality Sites

### Option 1: Fix Detail Selectors (Recommended)

Add site-specific selectors to `config.yaml`:

```yaml
sites:
  npc:
    detail_selectors:
      price: [".price", ".listing-price"]
      location: [".location", ".address"]
      bedrooms: [".bedrooms", "[class*='bedroom']"]
      bathrooms: [".bathrooms"]
      description: [".description"]
```

### Option 2: Disable Detail Scraping

Use list page data only:

```yaml
sites:
  npc:
    overrides:
      enable_detail_scraping: false
```

### Option 3: Lower Quality Threshold

Accept partial data:

```yaml
sites:
  npc:
    overrides:
      min_quality_score: 20  # Very lenient
```

### Option 4: Temporarily Disable Site

```yaml
sites:
  npc:
    enabled: false
```

## Monitoring Quality

### In Logs

```
INFO - npc: Quality filter rejected 3/3 listings (below 30% threshold). Avg quality: 17.5%
INFO - cwlagos: All 44 listings passed quality filter (>= 30%). Avg quality: 76.9%
INFO - Exported 43 listings for cwlagos (avg quality: 77.2%)
```

### Future: Quality Reports

Planned feature - generate weekly quality reports:

```
WEEKLY QUALITY REPORT
=====================
High Quality Sites (>70% avg):
  - cwlagos: 76.9%
  - propertypro: 65.0%

Sites Needing Attention (<30% avg):
  - npc: 17.5% ⚠️ (0 exports)
  - buyletlive: 0% ⚠️ (0 exports)
```

## Implementation Details

**Modified Files**:
- `core/exporter.py` - Added `_filter_by_quality()` function
- `core/exporter.py` - Updated `export_listings()` to apply quality filter
- `config.yaml` - Added `quality` section

**Dependencies**:
- Uses existing `core/quality_scorer.py` (already implemented)
- No new dependencies required

**Backward Compatibility**:
- ✅ Default threshold: 30% (keeps most good listings)
- ✅ Can be disabled by setting `min_quality_score: 0`
- ✅ Returns stats for reporting

## Recommendations

### For New Sites
1. Start with generic selectors (dynamic)
2. Monitor quality scores
3. If avg < 50%, add site-specific selectors
4. Iterate until quality > 70%

### For Existing Sites
1. Review current quality scores
2. Top priority: Sites with <30% avg quality
3. Add custom `detail_selectors` to config
4. Re-test and verify improvement

### Quality Targets
- **Minimum Acceptable**: 30% (required fields)
- **Good**: 70% (required + recommended)
- **Excellent**: 85%+ (nearly complete data)

## Next Steps

1. ✅ **Implemented**: Quality filtering active
2. ✅ **Configured**: 30% global threshold set
3. 🔄 **In Progress**: Fix NPC detail selectors
4. ⏳ **Planned**: Auto-generate weekly quality reports
5. ⏳ **Planned**: Alert system for failing sites

---

**Author**: Tee-David
**Last Updated**: 2025-10-21
