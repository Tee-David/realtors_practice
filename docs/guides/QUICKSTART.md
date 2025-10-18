# Quick Start Guide

## Prerequisites

Make sure you have:
- Python 3.8+
- All dependencies installed: `pip install -r requirements.txt` (if exists)
- `config.yaml` file (copy from `config.example.yaml` if needed)

## 1. Test With a Single Site

The easiest way to test is to scrape just one site:

```bash
# List available sites
python enable_one_site.py --list

# Enable only one site for testing
python enable_one_site.py npc

# Run the scraper
python main.py
```

This will:
- ✓ Enable only the `npc` site
- ✓ Disable all other 49 sites
- ✓ Run the scraper for just that one site

## 2. Check Results

After running:

```bash
# Check if exports were created
dir exports\npc\*.csv         # Windows
ls exports/npc/*.csv          # Unix/Mac

# View the exported CSV
type exports\npc\*.csv         # Windows
cat exports/npc/*.csv          # Unix/Mac

# Check logs
type logs\scraper.log          # Windows
cat logs/scraper.log           # Unix/Mac
```

## 3. Validate Configuration

Before running the full scraper:

```bash
# Validate your config.yaml
python validate_config.py

# Check site health (after first run)
python status.py
```

## 4. Common Test Scenarios

### Test Scenario 1: Single Site (Quick Test)
```bash
# Test just one site
python enable_one_site.py npc
python main.py
```

### Test Scenario 2: Debug Mode
```bash
# Enable debug logging and visible browser
set RP_DEBUG=1              # Windows
set RP_HEADLESS=0           # See browser
python main.py

# Unix/Mac
export RP_DEBUG=1
export RP_HEADLESS=0
python main.py
```

### Test Scenario 3: Specific Settings
```bash
# Disable geocoding, limit to 5 pages
set RP_GEOCODE=0
set RP_PAGE_CAP=5
python main.py
```

### Test Scenario 4: All Enabled Sites
```bash
# First, re-enable all sites
# Edit config.yaml and set enabled: true for all sites
# OR restore from backup

python main.py
```

## 5. Understanding Output

### Console Output
```
2025-10-05 11:30:00 - INFO - Realtors Practice Scraper Entry

=== CONFIGURATION SUMMARY ===
Fallback order: requests -> playwright
Geocoding: enabled (max 120 per run)
Pagination: max 30 pages, 12 scroll steps
...

Scraping npc -> https://nigeriapropertycentre.com/
...
Exported 42 listings for npc

=== SCRAPE REPORT ===
Found 42 listings from npc
Successful sites: 1 / 1 | Total listings: 42
```

### Files Created

**Exports:**
```
exports/
  npc/
    2025-10-05_11-30-00_npc.csv
    2025-10-05_11-30-00_npc.xlsx
```

**Logs:**
```
logs/
  scraper.log          # Main log file
  geocache.json        # Geocoding cache
  site_metadata.json   # Site health tracking
```

**Metadata Example:**
```json
{
  "npc": {
    "last_scrape": "2025-10-05T11:30:00",
    "last_successful_scrape": "2025-10-05T11:30:00",
    "last_count": 42,
    "total_scrapes": 1
  }
}
```

## 6. Troubleshooting

### Problem: No results found

**Check 1: Is the site enabled?**
```bash
python validate_config.py
# Look for "Enabled sites: X"
```

**Check 2: Check logs**
```bash
type logs\scraper.log | findstr ERROR      # Windows
grep ERROR logs/scraper.log                # Unix/Mac
```

**Check 3: Try with debug mode**
```bash
set RP_DEBUG=1
set RP_HEADLESS=0
python main.py
# Watch the browser to see what's happening
```

### Problem: "Module not found" errors

Install dependencies:
```bash
pip install pyyaml beautifulsoup4 openpyxl playwright requests
playwright install chromium
```

### Problem: Config validation fails

```bash
python validate_config.py
# Will show specific errors like:
# "Site 'npc': Missing required field 'url'"
```

Fix in config.yaml and try again.

### Problem: Site returns 0 listings

**Option 1: Increase retry time**
```yaml
# config.yaml
sites:
  npc:
    overrides:
      network_retry_seconds: 300  # 5 minutes
      max_pages: 50
```

**Option 2: Check if Lagos paths work**
```yaml
sites:
  npc:
    lagos_paths:
      - "/property-for-sale/in/lagos"
```

**Option 3: Try generic parser**
```yaml
sites:
  npc:
    parser: generic  # Instead of specials
```

## 7. Advanced Usage

### Custom Selectors

If a site's structure changed:

```yaml
# config.yaml
sites:
  mysite:
    selectors:
      card: "div.new-listing-class"      # Updated
      title: "h2.new-title-class"         # Updated
      price: "span.new-price-class"       # Updated
```

### Per-Site Overrides

```yaml
sites:
  slow_site:
    overrides:
      network_retry_seconds: 300   # Longer timeout
      max_pages: 50                # More pages
      formats: ["csv"]             # CSV only, skip XLSX
```

### Disable Geocoding for One Site

```yaml
sites:
  problematic_site:
    overrides:
      enabled: false  # Disable geocoding
```

## 8. Monitoring

### Check Site Health
```bash
python status.py
```

Shows:
- ✅ Healthy sites (working)
- ⚠️ Warning sites (recent failures)
- ❌ Critical sites (need attention)
- 🏆 Top performers
- 📈 Most active sites

### View Metadata
```bash
# All sites
type logs\site_metadata.json              # Windows
cat logs/site_metadata.json | jq          # Unix/Mac with jq

# Specific site
type logs\site_metadata.json | findstr npc         # Windows
cat logs/site_metadata.json | jq '.npc'            # Unix/Mac
```

## 9. Testing Checklist

Before considering the test successful:

- [ ] Config validation passes: `python validate_config.py`
- [ ] Single site scrape works: `python main.py` (with one site enabled)
- [ ] Results exported to CSV/XLSX
- [ ] Metadata tracking works: `logs/site_metadata.json` updated
- [ ] Status tool works: `python status.py`
- [ ] No errors in logs: `logs/scraper.log`

## 10. Next Steps

Once basic testing works:

1. **Enable more sites**: Edit `config.yaml` and set `enabled: true`
2. **Customize selectors**: Add `selectors:` section for sites needing it
3. **Set up monitoring**: Run `python status.py` regularly
4. **Optimize settings**: Adjust `max_pages`, `retry_seconds` per site
5. **Schedule scraping**: Set up cron job or task scheduler

## Common Commands Reference

```bash
# Configuration
python validate_config.py                    # Validate config
python enable_one_site.py npc               # Enable one site
python enable_one_site.py --list            # List all sites

# Running
python main.py                               # Run scraper

# Monitoring
python status.py                             # Site health dashboard
type logs\site_metadata.json                # View metadata

# Testing
python test_milestone4_5.py                 # Run integration tests
python test_site_specific.py                # Run site tests
```

## Environment Variables Quick Reference

```bash
# Debug
set RP_DEBUG=1                    # Enable debug logging
set RP_HEADLESS=0                 # Show browser window

# Geocoding
set RP_GEOCODE=1                  # Enable geocoding
set RP_MAX_GEOCODES=200           # Max geocoding requests

# Pagination
set RP_PAGE_CAP=50                # Max pages per site
set RP_SCROLL_STEPS=15            # Scroll steps for lazy load

# Retry
set RP_NET_RETRY_SECS=300         # Network timeout (seconds)
set RP_RETRY_ON_ZERO=1            # Retry if 0 results

# Fallback
set RP_FALLBACK=requests,playwright   # Fetch strategy order
```

## Success!

If you see this:

```
=== SCRAPE REPORT ===
Found 42 listings from npc (https://nigeriapropertycentre.com/)
Successful sites: 1 / 1 | Total listings: 42
```

**Congratulations! The scraper is working. 🎉**

Check `exports/npc/` for your CSV and XLSX files.
