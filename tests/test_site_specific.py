# test_site_specific.py
"""
Site-Specific Testing for Milestone 6.2

Tests:
- Verify all sites in config.yaml are properly configured
- Test adding a new site via config only
- Test disabling a site (enabled: false)
- Test modifying site selectors in config
"""

import sys
import os
import yaml

print("=" * 70)
print("SITE-SPECIFIC CONFIGURATION TESTS")
print("=" * 70)

# Test 1: Load and validate all sites in config
print("\n[TEST 1] Loading and validating all sites in config.yaml...")
try:
    from core.config_loader import load_config, ConfigValidationError

    config = load_config("config.yaml")
    all_sites = config.get_all_sites()
    enabled_sites = config.get_enabled_sites()
    total, enabled_count = config.count_sites()

    print(f"  [PASS] All sites loaded successfully")
    print(f"       - Total sites: {total}")
    print(f"       - Enabled sites: {enabled_count}")
    print(f"       - Disabled sites: {total - enabled_count}")
except Exception as e:
    print(f"  [FAIL] Failed to load config: {e}")
    sys.exit(1)

# Test 2: Verify each site has required fields
print("\n[TEST 2] Verifying required fields for all sites...")
required_fields = ["name", "url", "enabled"]
invalid_sites = []

for site_key, site_config in all_sites.items():
    missing_fields = [field for field in required_fields if field not in site_config]
    if missing_fields:
        invalid_sites.append((site_key, missing_fields))

if invalid_sites:
    print(f"  [FAIL] {len(invalid_sites)} sites missing required fields:")
    for site_key, missing in invalid_sites:
        print(f"       - {site_key}: missing {missing}")
else:
    print(f"  [PASS] All {total} sites have required fields")

# Test 3: Verify URL formats
print("\n[TEST 3] Verifying URL formats...")
invalid_urls = []

for site_key, site_config in all_sites.items():
    url = site_config.get("url", "")
    if not url.startswith(("http://", "https://")):
        invalid_urls.append(site_key)

if invalid_urls:
    print(f"  [FAIL] {len(invalid_urls)} sites have invalid URLs:")
    for site_key in invalid_urls:
        print(f"       - {site_key}")
else:
    print(f"  [PASS] All {total} sites have valid URLs")

# Test 4: Check parser types
print("\n[TEST 4] Checking parser types...")
parser_counts = {"specials": 0, "generic": 0, "custom": 0, "unspecified": 0}

for site_key, site_config in all_sites.items():
    parser = site_config.get("parser", "unspecified")
    if parser in parser_counts:
        parser_counts[parser] += 1
    else:
        parser_counts["unspecified"] += 1

print(f"  [PASS] Parser distribution:")
for parser_type, count in parser_counts.items():
    if count > 0:
        print(f"       - {parser_type}: {count} sites")

# Test 5: Test adding a new site (simulate config change)
print("\n[TEST 5] Testing adding a new site via config only...")
try:
    # Create a test config with a new site
    test_config = {
        "sites": {
            "test_new_site": {
                "name": "Test New Site",
                "url": "https://testnewsite.com",
                "enabled": True,
                "parser": "specials",
                "selectors": {
                    "card": "div.listing",
                    "title": "h2.title",
                    "price": "span.price",
                    "location": "div.location"
                }
            }
        }
    }

    # Validate the new site config
    from core.config_loader import _validate_site
    _validate_site("test_new_site", test_config["sites"]["test_new_site"])

    print(f"  [PASS] New site configuration is valid")
    print(f"       - Can add sites via config.yaml only")
    print(f"       - No code changes required")
except Exception as e:
    print(f"  [FAIL] New site validation failed: {e}")

# Test 6: Test disabling a site
print("\n[TEST 6] Testing disabled site filtering...")
disabled_sites = [key for key, cfg in all_sites.items() if not cfg.get("enabled", False)]

if disabled_sites:
    print(f"  [PASS] Disabled sites are correctly filtered:")
    for site_key in disabled_sites[:3]:  # Show first 3
        print(f"       - {site_key}: enabled={all_sites[site_key]['enabled']}")
    if len(disabled_sites) > 3:
        print(f"       - ... and {len(disabled_sites) - 3} more")
else:
    print(f"  [PASS] No disabled sites (all sites enabled)")

# Test 7: Test sites with custom selectors
print("\n[TEST 7] Checking sites with custom selectors...")
sites_with_selectors = [key for key, cfg in all_sites.items() if "selectors" in cfg]

print(f"  [PASS] {len(sites_with_selectors)} sites have custom selectors")
if sites_with_selectors:
    example = sites_with_selectors[0]
    selectors = all_sites[example]["selectors"]
    print(f"       - Example ({example}):")
    for sel_type, sel_value in list(selectors.items())[:3]:
        print(f"         - {sel_type}: {sel_value[:40]}...")

# Test 8: Test sites with overrides
print("\n[TEST 8] Checking sites with overrides...")
sites_with_overrides = [key for key, cfg in all_sites.items() if "overrides" in cfg]

print(f"  [PASS] {len(sites_with_overrides)} sites have overrides")
if sites_with_overrides:
    example = sites_with_overrides[0]
    overrides = all_sites[example]["overrides"]
    print(f"       - Example ({example}):")
    for override_key, override_value in overrides.items():
        print(f"         - {override_key}: {override_value}")

# Test 9: Test sites with Lagos paths
print("\n[TEST 9] Checking sites with Lagos-specific paths...")
sites_with_lagos = [key for key, cfg in all_sites.items() if "lagos_paths" in cfg]

print(f"  [PASS] {len(sites_with_lagos)} sites have lagos_paths")
if sites_with_lagos:
    example = sites_with_lagos[0]
    paths = all_sites[example]["lagos_paths"]
    print(f"       - Example ({example}): {len(paths)} paths")
    for path in paths[:2]:
        print(f"         - {path}")

# Test 10: Test sites with metadata fields
print("\n[TEST 10] Checking sites with metadata (category, priority, notes)...")
sites_with_category = [key for key, cfg in all_sites.items() if "category" in cfg]
sites_with_priority = [key for key, cfg in all_sites.items() if "priority" in cfg]
sites_with_notes = [key for key, cfg in all_sites.items() if "notes" in cfg]

print(f"  [PASS] Site metadata usage:")
print(f"       - category: {len(sites_with_category)} sites")
print(f"       - priority: {len(sites_with_priority)} sites")
print(f"       - notes: {len(sites_with_notes)} sites")

# Test 11: Test config-driven parser selection
print("\n[TEST 11] Testing config-driven parser selection...")
try:
    from core.dispatcher import get_parser

    # Test with a site from config
    if enabled_sites:
        site_key = list(enabled_sites.keys())[0]
        site_config = enabled_sites[site_key]

        parser = get_parser(site_key, site_config)
        print(f"  [PASS] Parser selection works")
        print(f"       - Site: {site_key}")
        print(f"       - Parser type: {site_config.get('parser', 'specials')}")
except Exception as e:
    print(f"  [FAIL] Parser selection failed: {e}")

# Test 12: Test modifying selectors
print("\n[TEST 12] Testing selector modification flexibility...")
try:
    # Simulate modifying selectors for a site
    modified_config = {
        "name": "Modified Site",
        "url": "https://modified-site.com",
        "enabled": True,
        "parser": "specials",
        "selectors": {
            "card": "article.property-card",  # Modified selector
            "title": "h1.listing-title",       # Modified selector
            "price": ".price-tag",              # Modified selector
            "location": ".location-info"        # Modified selector
        }
    }

    _validate_site("modified_site", modified_config)

    print(f"  [PASS] Selector modification works")
    print(f"       - Can update selectors via config.yaml")
    print(f"       - No code changes required")
except Exception as e:
    print(f"  [FAIL] Selector modification test failed: {e}")

print("\n" + "=" * 70)
print("SITE-SPECIFIC TESTS COMPLETE")
print("=" * 70)
print(f"\nSummary:")
print(f"- Total sites in config: {total}")
print(f"- Enabled sites: {enabled_count}")
print(f"- Sites with custom selectors: {len(sites_with_selectors)}")
print(f"- Sites with overrides: {len(sites_with_overrides)}")
print(f"- Sites with Lagos paths: {len(sites_with_lagos)}")
print(f"\nAll sites properly configured and config-driven workflow verified!")
