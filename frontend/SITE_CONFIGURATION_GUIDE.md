# Site Configuration Management Guide

## Overview

Sites in the Real Estate Scraper are disabled by default for safety and to give you control over which sources to scrape. You can now view all sites (enabled and disabled) and toggle them individually through the UI.

## Frontend Changes (Site Configuration Component)

### New Features

1. **Show All Sites Toggle**

   - Checkbox to show/hide disabled sites
   - Default: Shows all sites (enabled + disabled)
   - Uncheck to see only enabled sites

2. **Site Statistics Display**

   - Total sites count
   - Enabled sites count (green)
   - Disabled sites count (gray)

3. **Empty State Handling**

   - Clear message when no sites match filter
   - Quick button to show all sites if filtered

4. **Console Logging**
   - Tracks site counts and filter state
   - Helps debug any loading issues

### UI Layout

```
┌─────────────────────────────────────────────┐
│  Site Configuration              [+Add Site] │
├─────────────────────────────────────────────┤
│  Total: 50  Enabled: 1  Disabled: 49       │
│  ☑ Show disabled sites                      │
├─────────────────────────────────────────────┤
│  [Site List with Enable/Disable buttons]   │
└─────────────────────────────────────────────┘
```

## Backend: Enable Sites

### Option 1: Enable All Sites (Quick)

Run this script from the `realtors_practice` directory:

```bash
python scripts/enable_all_sites.py
```

This will:

- Enable all 50 sites in config.yaml
- Show progress for each site
- Restart the API server to apply changes

### Option 2: Enable Specific Sites (Selective)

Use the existing script:

```bash
python scripts/enable_sites.py npc propertypro privateproperty
```

Replace site keys with the ones you want to enable.

### Option 3: Enable via UI

1. Go to Scraper Control & Configuration page
2. Check "Show disabled sites" (if unchecked)
3. Find the site you want
4. Click the "Enable" button in the Actions column
5. The site will be enabled immediately

### Option 4: Manual Edit

Edit `config.yaml` directly:

```yaml
sites:
  propertypro:
    name: PropertyPro
    url: https://propertypro.ng/
    enabled: true # Change from false to true
    parser: specials
```

Restart the API server after editing.

## Why Sites Are Disabled by Default

1. **Controlled scraping**: Start with a few sites, expand gradually
2. **Resource management**: 50 sites running at once may be too much
3. **Testing**: Test individual parsers before enabling all
4. **Rate limiting**: Avoid overwhelming targets

## Common Workflows

### Start Small, Scale Up

```bash
# Enable just a few high-quality sites
python scripts/enable_sites.py propertypro npc privateproperty

# Test them
# Run scraper with selected sites in UI

# Enable more as needed
python scripts/enable_sites.py lamudi jiji property24
```

### Enable Everything

```bash
# Enable all sites
python scripts/enable_all_sites.py

# Restart API server
python api_server.py

# In UI: Select which sites to scrape this run
```

### Enable One at a Time (UI)

1. Check "Show disabled sites"
2. Browse through the 50 sites
3. Click "Enable" on sites you want
4. Select them for your scrape run

## Site Configuration Component Improvements

- ✅ Shows all 50 sites by default
- ✅ Filter to show only enabled sites
- ✅ Statistics display (Total/Enabled/Disabled)
- ✅ Empty state with helpful message
- ✅ Console logging for debugging
- ✅ Works on mobile and desktop

## Troubleshooting

### Sites not showing in UI

Check browser console for:

```
[SiteConfiguration] Sites data: {sitesCount: 50, allSitesCount: 50, ...}
```

If `sitesCount` is 0 but `allSitesCount` is 50, check the "Show disabled sites" toggle.

### Sites enabled but not scraping

1. Verify enabled in UI (green "Enabled" badge)
2. Select the sites before clicking "Run Scraper Now"
3. Check Run Console for logs

### Can't enable a site in UI

1. Refresh the page
2. Try the backend script: `python scripts/enable_sites.py <site_key>`
3. Check API server logs for errors

## Next Steps

1. Run `python scripts/enable_all_sites.py` to enable all sites
2. Restart the API server
3. Refresh the frontend
4. You should see all 50 sites in the list
5. Select which ones to scrape and click "Run Scraper Now"
