# test_config_validation.py
"""
Validation tests for config_loader.py

Tests various edge cases and error conditions to ensure robust validation.
"""

import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config_loader import load_config, ConfigValidationError


def write_temp_config(content: str) -> str:
    """Write temporary config file and return path."""
    fd, path = tempfile.mkstemp(suffix='.yaml', text=True)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


def test_valid_config():
    """Test: Valid complete configuration loads successfully."""
    print("\n[TEST] Valid config with all fields...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "https://example.com"
    enabled: true
    parser: specials
    """
    path = write_temp_config(config_content)
    try:
        config = load_config(path)
        assert len(config.get_all_sites()) == 1
        print("  [PASS]")
    finally:
        os.unlink(path)


def test_missing_required_field_name():
    """Test: Missing 'name' field raises validation error."""
    print("\n[TEST] Missing required field 'name'...")
    config_content = """
sites:
  testsite:
    url: "https://example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Missing required field 'name'" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_missing_required_field_url():
    """Test: Missing 'url' field raises validation error."""
    print("\n[TEST] Missing required field 'url'...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Missing required field 'url'" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_missing_required_field_enabled():
    """Test: Missing 'enabled' field raises validation error."""
    print("\n[TEST] Missing required field 'enabled'...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "https://example.com"
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Missing required field 'enabled'" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_invalid_url_no_scheme():
    """Test: URL without http/https scheme raises error."""
    print("\n[TEST] Invalid URL (no scheme)...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Invalid URL scheme" in str(e) or "URL missing domain" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_invalid_url_empty():
    """Test: Empty URL raises error."""
    print("\n[TEST] Invalid URL (empty)...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: ""
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "URL is empty" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_invalid_url_ftp():
    """Test: FTP URL scheme raises error."""
    print("\n[TEST] Invalid URL (ftp scheme)...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "ftp://example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Invalid URL scheme 'ftp'" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_malformed_yaml():
    """Test: Malformed YAML syntax raises error."""
    print("\n[TEST] Malformed YAML...")
    config_content = """
sites:
  testsite:
    name: "Test Site
    url: "https://example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except (ConfigValidationError, Exception) as e:
        print(f"  ✓ PASS - {type(e).__name__}: {e}")
    finally:
        os.unlink(path)


def test_empty_config_file():
    """Test: Empty config file raises error."""
    print("\n[TEST] Empty config file...")
    path = write_temp_config("")
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "empty" in str(e).lower()
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_missing_sites_section():
    """Test: Missing 'sites' section raises error."""
    print("\n[TEST] Missing 'sites' section...")
    config_content = """
geocoding:
  enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "missing 'sites' section" in str(e).lower()
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_enabled_not_boolean():
    """Test: 'enabled' field with non-boolean value raises error."""
    print("\n[TEST] Enabled field not boolean...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "https://example.com"
    enabled: "yes"
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "'enabled' must be true or false" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_invalid_fallback_order():
    """Test: Invalid fallback option raises error."""
    print("\n[TEST] Invalid fallback order...")
    config_content = """
fallback_order:
  - requests
  - invalid_option
sites:
  testsite:
    name: "Test Site"
    url: "https://example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        load_config(path)
        print("  [FAIL] - Should have raised ConfigValidationError")
    except ConfigValidationError as e:
        assert "Invalid fallback option" in str(e)
        print(f"  [PASS] - {e}")
    finally:
        os.unlink(path)


def test_file_not_found():
    """Test: Non-existent config file raises FileNotFoundError."""
    print("\n[TEST] Config file not found...")
    try:
        load_config("nonexistent_config_12345.yaml")
        print("  [FAIL] - Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()
        print(f"  [PASS] - {e}")


def test_disabled_sites_filtered():
    """Test: Disabled sites are filtered out correctly."""
    print("\n[TEST] Disabled sites filtered...")
    config_content = """
sites:
  enabled_site:
    name: "Enabled Site"
    url: "https://enabled.com"
    enabled: true
  disabled_site:
    name: "Disabled Site"
    url: "https://disabled.com"
    enabled: false
    """
    path = write_temp_config(config_content)
    try:
        config = load_config(path)
        all_sites = config.get_all_sites()
        enabled_sites = config.get_enabled_sites()
        assert len(all_sites) == 2
        assert len(enabled_sites) == 1
        assert "enabled_site" in enabled_sites
        assert "disabled_site" not in enabled_sites
        print("  [PASS]")
    finally:
        os.unlink(path)


def test_global_settings_defaults():
    """Test: Global settings use defaults when not specified."""
    print("\n[TEST] Global settings defaults...")
    config_content = """
sites:
  testsite:
    name: "Test Site"
    url: "https://example.com"
    enabled: true
    """
    path = write_temp_config(config_content)
    try:
        config = load_config(path)
        settings = config.get_global_settings()
        assert settings["geocoding"]["enabled"] == True
        assert settings["pagination"]["max_pages"] == 30
        assert settings["fallback_order"] == ["requests", "playwright"]
        print("  [PASS]")
    finally:
        os.unlink(path)


def run_all_tests():
    """Run all validation tests."""
    print("=" * 70)
    print("CONFIG VALIDATION TESTS")
    print("=" * 70)

    tests = [
        test_valid_config,
        test_missing_required_field_name,
        test_missing_required_field_url,
        test_missing_required_field_enabled,
        test_invalid_url_no_scheme,
        test_invalid_url_empty,
        test_invalid_url_ftp,
        test_malformed_yaml,
        test_empty_config_file,
        test_missing_sites_section,
        test_enabled_not_boolean,
        test_invalid_fallback_order,
        test_file_not_found,
        test_disabled_sites_filtered,
        test_global_settings_defaults,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [ASSERTION FAILED]: {e}")
            failed += 1
        except Exception as e:
            print(f"  [UNEXPECTED ERROR]: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
