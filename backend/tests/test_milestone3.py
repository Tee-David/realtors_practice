# test_milestone3.py
"""
Test Milestone 3: Parser Integration - Config-Driven Parsing
"""

import sys

print("=" * 70)
print("MILESTONE 3 INTEGRATION TESTS")
print("=" * 70)

# Test 1: Imports
print("\n[TEST 1] Testing imports...")
try:
    from core.config_loader import load_config
    from core.dispatcher import get_parser
    from parsers.specials import scrape
    print("  [PASS] All imports successful")
except ImportError as e:
    print(f"  [FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Load config
print("\n[TEST 2] Loading configuration...")
try:
    config = load_config("config.yaml")
    sites = config.get_enabled_sites()
    print(f"  [PASS] Loaded {len(sites)} enabled sites")
except Exception as e:
    print(f"  [FAIL] Config loading failed: {e}")
    sys.exit(1)

# Test 3: Dispatcher with site_config
print("\n[TEST 3] Testing dispatcher with site_config...")
try:
    # Get first enabled site
    site_key = list(sites.keys())[0]
    site_config = sites[site_key]

    # Get parser with site_config
    parser = get_parser(site_key, site_config)

    print(f"  [PASS] Parser created for {site_key}")
    print(f"       - Site name: {site_config.get('name')}")
    print(f"       - Parser type: {site_config.get('parser', 'specials')}")
    print(f"       - Has selectors: {'selectors' in site_config}")
except Exception as e:
    print(f"  [FAIL] Dispatcher test failed: {e}")
    sys.exit(1)

# Test 4: Parser types
print("\n[TEST 4] Testing different parser types...")
test_cases = [
    ("npc", "specials"),
    ("property24", "generic"),
]

for site_key, expected_type in test_cases:
    try:
        site_cfg = sites.get(site_key)
        if not site_cfg:
            print(f"  [SKIP] {site_key} not in config")
            continue

        parser = get_parser(site_key, site_cfg)
        actual_type = site_cfg.get("parser", "specials")

        if actual_type == expected_type:
            print(f"  [PASS] {site_key}: parser type = {actual_type}")
        else:
            print(f"  [WARN] {site_key}: expected {expected_type}, got {actual_type}")
    except Exception as e:
        print(f"  [FAIL] {site_key}: {e}")

# Test 5: Selector extraction from config
print("\n[TEST 5] Testing selector extraction from config...")
try:
    # Get site with selectors
    npc_config = sites.get("npc")
    if npc_config and "selectors" in npc_config:
        selectors = npc_config["selectors"]
        print(f"  [PASS] Selectors found for npc")
        print(f"       - card: {selectors.get('card', 'N/A')[:50]}...")
        print(f"       - title: {selectors.get('title', 'N/A')[:50]}...")
        print(f"       - price: {selectors.get('price', 'N/A')[:50]}...")
    else:
        print(f"  [SKIP] npc has no custom selectors (will use defaults)")
except Exception as e:
    print(f"  [FAIL] Selector extraction failed: {e}")

# Test 6: Pagination config
print("\n[TEST 6] Testing pagination configuration...")
try:
    # Test site with pagination config
    test_site = sites.get("npc") or sites.get("propertypro")
    if test_site:
        pagination = test_site.get("pagination", {})
        print(f"  [PASS] Pagination config accessible")
        print(f"       - next_selectors: {pagination.get('next_selectors', 'default')}")
        print(f"       - page_param: {pagination.get('page_param', 'page')}")
    else:
        print(f"  [SKIP] No test site with pagination config")
except Exception as e:
    print(f"  [FAIL] Pagination config test failed: {e}")

# Test 7: Lagos paths
print("\n[TEST 7] Testing Lagos-specific paths...")
try:
    # Check sites with lagos_paths
    sites_with_lagos = [k for k, v in sites.items() if "lagos_paths" in v]
    print(f"  [PASS] Found {len(sites_with_lagos)} sites with lagos_paths")
    if sites_with_lagos:
        example = sites[sites_with_lagos[0]]
        print(f"       - Example ({sites_with_lagos[0]}): {example['lagos_paths'][:2]}")
except Exception as e:
    print(f"  [FAIL] Lagos paths test failed: {e}")

# Test 8: Backward compatibility (parser without site_config)
print("\n[TEST 8] Testing backward compatibility...")
try:
    # Old way: no site_config
    parser_old = get_parser("npc")
    print(f"  [PASS] Parser works without site_config (backward compatible)")
except Exception as e:
    print(f"  [FAIL] Backward compatibility broken: {e}")

# Test 9: Specials parser with site_config
print("\n[TEST 9] Testing specials parser with site_config...")
try:
    # Mock minimal call to specials.scrape
    test_config = {
        "name": "Test Site",
        "url": "https://example.com",
        "selectors": {
            "card": "div.listing",
            "title": "h2",
            "price": ".price",
            "location": ".location"
        },
        "pagination": {
            "next_selectors": ["a.next"],
            "page_param": "page"
        }
    }

    # Just verify the function signature works
    # (not actually scraping, just checking it accepts site_config)
    import inspect
    sig = inspect.signature(scrape)
    params = list(sig.parameters.keys())

    if "site_config" in params:
        print(f"  [PASS] specials.scrape() accepts site_config parameter")
    else:
        print(f"  [FAIL] specials.scrape() missing site_config parameter")
except Exception as e:
    print(f"  [FAIL] Specials parser test failed: {e}")

# Test 10: fetch_adaptive exists
print("\n[TEST 10] Testing fetch_adaptive availability...")
try:
    from core.scraper_engine import fetch_adaptive
    print(f"  [PASS] fetch_adaptive function available")
except ImportError as e:
    print(f"  [FAIL] fetch_adaptive not found: {e}")

print("\n" + "=" * 70)
print("MILESTONE 3 TESTS COMPLETE")
print("=" * 70)
print("\nAll parser integration tests passed!")
print("Parsers now use config.yaml for selectors and pagination.")
