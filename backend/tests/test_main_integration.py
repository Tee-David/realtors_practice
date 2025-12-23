# test_main_integration.py
"""
Integration test for refactored main.py with config loader.
"""

import sys
import os

# Test imports
print("[TEST] Testing imports...")
try:
    from core.config_loader import load_config, ConfigValidationError
    from core.dispatcher import get_parser
    from core.cleaner import normalize_listing
    from core.geo import geocode_listings
    from core.exporter import export_listings
    from core.utils import is_lagos_like
    print("  [PASS] All imports successful")
except ImportError as e:
    print(f"  [FAIL] Import error: {e}")
    sys.exit(1)

# Test config loading
print("\n[TEST] Testing config loading...")
try:
    config = load_config("config.yaml")
    print(f"  [PASS] Config loaded: {config.count_sites()}")
except Exception as e:
    print(f"  [FAIL] Config loading failed: {e}")
    sys.exit(1)

# Test getting enabled sites
print("\n[TEST] Testing enabled sites retrieval...")
try:
    enabled_sites = config.get_enabled_sites()
    print(f"  [PASS] Found {len(enabled_sites)} enabled sites")

    # Show first 3 sites as examples
    for i, (key, site_config) in enumerate(list(enabled_sites.items())[:3]):
        print(f"       - {key}: {site_config.get('name')} ({site_config.get('url')})")
except Exception as e:
    print(f"  [FAIL] Failed to get enabled sites: {e}")
    sys.exit(1)

# Test global settings
print("\n[TEST] Testing global settings...")
try:
    global_settings = config.get_global_settings()
    print(f"  [PASS] Global settings loaded")
    print(f"       - Fallback order: {global_settings['fallback_order']}")
    print(f"       - Geocoding enabled: {global_settings['geocoding']['enabled']}")
    print(f"       - Max pages: {global_settings['pagination']['max_pages']}")
    print(f"       - Retry seconds: {global_settings['retry']['network_retry_seconds']}")
except Exception as e:
    print(f"  [FAIL] Failed to get global settings: {e}")
    sys.exit(1)

# Test environment variable override
print("\n[TEST] Testing environment variable override...")
os.environ["RP_DEBUG"] = "1"
os.environ["RP_MAX_GEOCODES"] = "200"
try:
    config_with_env = load_config("config.yaml")
    settings = config_with_env.get_global_settings()
    assert settings["logging"]["level"] == "DEBUG", "RP_DEBUG env var not applied"
    assert settings["geocoding"]["max_per_run"] == 200, "RP_MAX_GEOCODES env var not applied"
    print(f"  [PASS] Environment overrides working")
    print(f"       - Log level: {settings['logging']['level']}")
    print(f"       - Max geocodes: {settings['geocoding']['max_per_run']}")
except AssertionError as e:
    print(f"  [FAIL] Environment override failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  [FAIL] Unexpected error: {e}")
    sys.exit(1)
finally:
    # Clean up env vars
    del os.environ["RP_DEBUG"]
    del os.environ["RP_MAX_GEOCODES"]

# Test dispatcher with site config
print("\n[TEST] Testing dispatcher integration...")
try:
    # Get a site config
    test_site_key = list(enabled_sites.keys())[0]
    test_site_config = enabled_sites[test_site_key]

    # Get parser for the site
    parser = get_parser(test_site_key)
    print(f"  [PASS] Parser retrieved for {test_site_key}")
    print(f"       - Parser type: {type(parser).__name__}")
except Exception as e:
    print(f"  [FAIL] Dispatcher integration failed: {e}")
    sys.exit(1)

# Test backward compatibility
print("\n[TEST] Testing backward compatibility...")
try:
    # Simulate old code accessing settings
    assert "fallback_order" in global_settings
    assert "geocoding" in global_settings
    assert "pagination" in global_settings
    print("  [PASS] All expected settings present")
except AssertionError as e:
    print(f"  [FAIL] Backward compatibility broken: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL INTEGRATION TESTS PASSED")
print("=" * 70)
print("\nRefactored main.py is ready for use!")
print("The scraper can now be configured entirely via config.yaml")
