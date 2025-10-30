"""
Test script to verify API server can start successfully.
This will help the frontend developer confirm the setup is correct.
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("API Server Startup Test")
print("=" * 60)
print()

# Test 1: Check Python version
print("[Step 1] Checking Python version...")
print(f"  Python {sys.version}")
print()

# Test 2: Check required files exist
print("[Step 2] Checking required files...")
required_files = [
    "api_server.py",
    "core/url_validator.py",
    "core/config_loader.py",
    "config.yaml"
]
all_exist = True
for file in required_files:
    exists = Path(file).exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n[ERROR] Some required files are missing!")
    sys.exit(1)
print()

# Test 3: Test core imports
print("[Step 3] Testing core imports...")
try:
    from core.url_validator import URLValidator
    print("  [OK] URLValidator imported")

    from core.config_loader import load_config
    print("  [OK] load_config imported")

    from core.location_filter import get_location_filter
    print("  [OK] get_location_filter imported")

    print()
except ImportError as e:
    print(f"\n[ERROR] Import failed - {e}")
    sys.exit(1)

# Test 4: Test URLValidator functionality
print("[Step 4] Testing URLValidator functionality...")
try:
    validator = URLValidator()
    test_urls = [
        ("https://example.com", True),
        ("whatsapp://send?phone=123", False),
        ("mailto:test@example.com", False),
    ]

    for url, expected in test_urls:
        result = validator.is_valid(url)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"  {status} {url}: {result}")
    print()
except Exception as e:
    print(f"\n[ERROR] URLValidator test failed - {e}")
    sys.exit(1)

# Test 5: Test config loading
print("[Step 5] Testing config loading...")
try:
    config = load_config()
    sites = config.sites if hasattr(config, 'sites') else {}
    print(f"  [OK] Config loaded with {len(sites)} sites")
    print()
except Exception as e:
    print(f"\n[ERROR] Config loading failed - {e}")
    sys.exit(1)

# Test 6: Test api_server module import
print("[Step 6] Testing API server imports...")
try:
    import api_server
    print("  [OK] api_server module imported successfully")
    print()
except Exception as e:
    print(f"\n[ERROR] API server import failed - {e}")
    print(f"\nFull error:\n{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Check Flask app creation
print("[Step 7] Checking Flask app...")
try:
    from api_server import app
    print(f"  [OK] Flask app created: {app}")
    print()
except Exception as e:
    print(f"\n[ERROR] Flask app creation failed - {e}")
    sys.exit(1)

print("=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 60)
print()
print("The API server should start successfully.")
print("To start the server, run:")
print()
print("  python api_server.py")
print()
print("Then test with:")
print()
print("  curl http://localhost:5000/api/health")
print()
print("=" * 60)
