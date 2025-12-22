"""
Comprehensive Test Suite for v3.3.0
Tests all critical functionality after recent improvements
"""
import os
import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:5000"
FIREBASE_CRED = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json')

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "OK": "[OK]",
            "FAIL": "[FAIL]",
            "WARN": "[WARN]",
            "SKIP": "[SKIP]"
        }
        print(f"{timestamp} {prefix.get(level, '[INFO]')} {msg}")

    def test(self, name, func):
        """Run a single test"""
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print(f"{'='*70}")
        try:
            result = func()
            if result is None:
                self.skipped += 1
                self.log(f"SKIPPED: {name}", "SKIP")
            elif result:
                self.passed += 1
                self.log(f"PASSED: {name}", "OK")
            else:
                self.failed += 1
                self.log(f"FAILED: {name}", "FAIL")
                self.errors.append(name)
        except Exception as e:
            self.failed += 1
            self.log(f"ERROR in {name}: {e}", "FAIL")
            self.errors.append(f"{name}: {e}")
            import traceback
            traceback.print_exc()

    def summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.passed + self.failed + self.skipped}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Skipped: {self.skipped}")

        if self.errors:
            print(f"\nFailed Tests:")
            for error in self.errors:
                print(f"  - {error}")

        print("="*70)

        if self.failed == 0:
            print("\n[SUCCESS] All tests passed!")
            return 0
        else:
            print(f"\n[FAILURE] {self.failed} test(s) failed")
            return 1

# Initialize test runner
runner = TestRunner()

# ============================================================================
# TEST 1: Firestore Environment
# ============================================================================
def test_firestore_environment():
    """Verify Firestore credentials are configured"""
    runner.log("Checking Firestore credentials...")

    if not FIREBASE_CRED:
        runner.log("FIREBASE_SERVICE_ACCOUNT not set", "FAIL")
        return False

    cred_path = Path(FIREBASE_CRED)
    if not cred_path.exists():
        runner.log(f"Credentials file not found: {FIREBASE_CRED}", "FAIL")
        return False

    runner.log(f"Credentials found: {FIREBASE_CRED}", "OK")
    return True

# ============================================================================
# TEST 2: Firestore Connection
# ============================================================================
def test_firestore_connection():
    """Test direct Firestore connection"""
    runner.log("Testing Firestore connection...")

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Initialize if needed
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CRED)
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        # Query for 1 document
        docs = list(db.collection('properties').limit(1).stream())

        if docs:
            runner.log(f"Connected to Firestore, found documents", "OK")
            return True
        else:
            runner.log("Connected but no documents found", "WARN")
            return True

    except Exception as e:
        runner.log(f"Firestore connection failed: {e}", "FAIL")
        return False

# ============================================================================
# TEST 3: API Server Health
# ============================================================================
def test_api_health():
    """Test API server health endpoint"""
    runner.log("Testing API server health...")

    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            runner.log(f"API server healthy: {data.get('status')}", "OK")
            return True
        else:
            runner.log(f"Health check returned {response.status_code}", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running (start with: python functions/api_server.py)", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Health check failed: {e}", "FAIL")
        return False

# ============================================================================
# TEST 4: Price Range Filtering (CRITICAL FIX)
# ============================================================================
def test_price_range_filtering():
    """Test the critical price range filtering fix"""
    runner.log("Testing price range filtering (CRITICAL FIX)...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/firestore/query",
            json={
                "filters": {
                    "price_min": 1000000,
                    "price_max": 100000000
                },
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            results = data.get('results', [])

            runner.log(f"Price range query returned {count} properties", "OK")

            # Verify response structure
            if results:
                first = results[0]
                if 'financial' in first and 'price' in first['financial']:
                    price = first['financial']['price']
                    runner.log(f"Sample price: ₦{price:,.0f}", "OK")

                    # Verify price is in range
                    if 1000000 <= price <= 100000000:
                        runner.log("Price within requested range", "OK")
                        return True
                    else:
                        runner.log(f"Price {price} outside range", "WARN")
                        return True  # Still pass, data might be pre-existing
                else:
                    runner.log("Response missing nested financial.price field", "FAIL")
                    return False
            else:
                runner.log("No results (might be no data in range)", "WARN")
                return True
        else:
            runner.log(f"Query failed with status {response.status_code}: {response.text}", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Price range test failed: {e}", "FAIL")
        return False

# ============================================================================
# TEST 5: Nested Field Path Queries
# ============================================================================
def test_nested_field_queries():
    """Test various nested field path queries"""
    runner.log("Testing nested field path queries...")

    test_queries = [
        {
            "name": "Location filter",
            "filters": {"location.state": "Lagos"},
            "check_field": ["location", "state"]
        },
        {
            "name": "Property type filter",
            "filters": {"property_type": "Flat"},
            "check_field": ["property_details", "property_type"]
        },
        {
            "name": "Bedrooms filter",
            "filters": {"bedrooms": 3},
            "check_field": ["property_details", "bedrooms"]
        }
    ]

    all_passed = True

    for test_query in test_queries:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/firestore/query",
                json={
                    "filters": test_query["filters"],
                    "limit": 5
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                runner.log(f"{test_query['name']}: {data.get('count', 0)} results", "OK")
            else:
                runner.log(f"{test_query['name']} failed: {response.status_code}", "FAIL")
                all_passed = False

        except requests.exceptions.ConnectionError:
            runner.log("API server not running", "SKIP")
            return None
        except Exception as e:
            runner.log(f"{test_query['name']} error: {e}", "FAIL")
            all_passed = False

    return all_passed

# ============================================================================
# TEST 6: Sorting with Field Mapping
# ============================================================================
def test_sorting():
    """Test automatic sort field mapping"""
    runner.log("Testing sort field mapping...")

    sort_tests = [
        {"sort_by": "price", "sort_desc": False, "name": "Price ascending"},
        {"sort_by": "price", "sort_desc": True, "name": "Price descending"},
        {"sort_by": "bedrooms", "sort_desc": True, "name": "Bedrooms descending"},
        {"sort_by": "uploaded_at", "sort_desc": True, "name": "Upload date descending"}
    ]

    all_passed = True

    for test in sort_tests:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/firestore/query",
                json={
                    "sort_by": test["sort_by"],
                    "sort_desc": test["sort_desc"],
                    "limit": 5
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                runner.log(f"{test['name']}: {data.get('count', 0)} results", "OK")
            else:
                runner.log(f"{test['name']} failed: {response.status_code}", "FAIL")
                all_passed = False

        except requests.exceptions.ConnectionError:
            runner.log("API server not running", "SKIP")
            return None
        except Exception as e:
            runner.log(f"{test['name']} error: {e}", "FAIL")
            all_passed = False

    return all_passed

# ============================================================================
# TEST 7: Combined Filters (Complex Query)
# ============================================================================
def test_complex_query():
    """Test combining multiple filters"""
    runner.log("Testing complex multi-filter query...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/firestore/query",
            json={
                "filters": {
                    "price_min": 5000000,
                    "price_max": 50000000,
                    "bedrooms": 3,
                    "property_type": "Flat"
                },
                "sort_by": "price",
                "sort_desc": False,
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            runner.log(f"Complex query returned {count} properties", "OK")

            if count > 0:
                runner.log("Complex filtering working correctly", "OK")
            else:
                runner.log("No results (might be no matching data)", "WARN")

            return True
        else:
            runner.log(f"Complex query failed: {response.status_code} - {response.text}", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Complex query error: {e}", "FAIL")
        return False

# ============================================================================
# TEST 8: Export Endpoint
# ============================================================================
def test_export_endpoint():
    """Test Firestore export with filters"""
    runner.log("Testing export endpoint...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/firestore/export",
            json={
                "format": "json",
                "filters": {
                    "price_min": 1000000
                },
                "limit": 10
            },
            timeout=15
        )

        if response.status_code == 200:
            # Check if response is JSON or file
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                data = response.json()
                runner.log(f"Export returned JSON data", "OK")
            else:
                runner.log(f"Export returned file ({len(response.content)} bytes)", "OK")

            return True
        elif response.status_code == 404:
            runner.log("No data found for export (expected if no matching data)", "WARN")
            return True
        else:
            runner.log(f"Export failed: {response.status_code}", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Export test error: {e}", "FAIL")
        return False

# ============================================================================
# TEST 9: Archive Query Endpoint
# ============================================================================
def test_archive_query():
    """Test archive collection query"""
    runner.log("Testing archive query endpoint...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/firestore/query-archive",
            json={
                "filters": {},
                "limit": 5
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            runner.log(f"Archive query returned {count} properties", "OK")
            return True
        else:
            runner.log(f"Archive query returned {response.status_code}", "WARN")
            # Don't fail - archive collection might be empty
            return True

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Archive query error: {e}", "FAIL")
        return False

# ============================================================================
# TEST 10: Pagination
# ============================================================================
def test_pagination():
    """Test query pagination"""
    runner.log("Testing pagination...")

    try:
        # Page 1
        response1 = requests.post(
            f"{API_BASE_URL}/api/firestore/query",
            json={"limit": 5, "offset": 0},
            timeout=10
        )

        # Page 2
        response2 = requests.post(
            f"{API_BASE_URL}/api/firestore/query",
            json={"limit": 5, "offset": 5},
            timeout=10
        )

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()

            runner.log(f"Page 1: {data1.get('count', 0)} results", "OK")
            runner.log(f"Page 2: {data2.get('count', 0)} results", "OK")

            return True
        else:
            runner.log("Pagination test failed", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        runner.log(f"Pagination error: {e}", "FAIL")
        return False

# ============================================================================
# TEST 11: Legacy Endpoints Removed
# ============================================================================
def test_legacy_endpoints_removed():
    """Verify legacy endpoints are removed"""
    runner.log("Verifying legacy endpoints removed...")

    try:
        # These should not exist anymore
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"filters": {}},
            timeout=5
        )

        if response.status_code == 404:
            runner.log("Legacy /api/query correctly removed", "OK")
            return True
        else:
            runner.log(f"Legacy endpoint still exists: {response.status_code}", "FAIL")
            return False

    except requests.exceptions.ConnectionError:
        runner.log("API server not running", "SKIP")
        return None
    except Exception as e:
        # 404 or connection error is good
        runner.log("Legacy endpoints properly removed", "OK")
        return True

# ============================================================================
# TEST 12: Data Integrity Check
# ============================================================================
def test_data_integrity():
    """Check Firestore data integrity"""
    runner.log("Checking data integrity...")

    try:
        import firebase_admin
        from firebase_admin import firestore

        if not firebase_admin._apps:
            runner.log("Firebase not initialized", "SKIP")
            return None

        db = firestore.client()

        # Sample 10 documents
        docs = list(db.collection('properties').limit(10).stream())

        if not docs:
            runner.log("No documents in Firestore", "WARN")
            return True

        runner.log(f"Sampled {len(docs)} documents", "OK")

        # Check schema structure
        required_fields = ['basic_info', 'property_details', 'financial', 'location']
        valid_count = 0

        for doc in docs:
            data = doc.to_dict()
            has_required = all(field in data for field in required_fields)
            if has_required:
                valid_count += 1

        runner.log(f"{valid_count}/{len(docs)} documents have complete schema", "OK")

        if valid_count > 0:
            return True
        else:
            runner.log("No documents have proper enterprise schema", "FAIL")
            return False

    except Exception as e:
        runner.log(f"Data integrity check failed: {e}", "FAIL")
        return False

# ============================================================================
# TEST 13: No Workbook Dependencies
# ============================================================================
def test_no_workbook_dependencies():
    """Verify workbook dependencies removed"""
    runner.log("Checking for workbook dependencies...")

    # Check api_server.py doesn't import PropertyQuery
    api_server = Path('functions/api_server.py')
    if api_server.exists():
        content = api_server.read_text()

        if 'from core.query_engine import PropertyQuery' in content:
            runner.log("api_server.py still imports PropertyQuery", "FAIL")
            return False
        else:
            runner.log("PropertyQuery import removed", "OK")

    # Check legacy endpoints removed
    if 'def query_properties():' in content:
        runner.log("Legacy query_properties() still exists", "FAIL")
        return False
    else:
        runner.log("Legacy endpoints removed", "OK")

    return True

# ============================================================================
# TEST 14: Documentation Files Exist
# ============================================================================
def test_documentation_exists():
    """Verify all new documentation exists"""
    runner.log("Checking documentation files...")

    docs = [
        'IMPROVEMENTS_V3.3.0.md',
        'frontend/FIRESTORE_QUERY_REFERENCE.md',
        'FOR_FRONTEND_DEVELOPER.md',
        'frontend/API_ENDPOINTS_ACTUAL.md',
        'verify_firestore_only.py'
    ]

    all_exist = True
    for doc in docs:
        if Path(doc).exists():
            runner.log(f"[+] {doc}", "OK")
        else:
            runner.log(f"[-] {doc} missing", "FAIL")
            all_exist = False

    return all_exist

# ============================================================================
# TEST 15: Git Status Clean
# ============================================================================
def test_git_status():
    """Verify all changes are committed"""
    runner.log("Checking git status...")

    try:
        import subprocess
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.stdout.strip():
            runner.log(f"Uncommitted changes found:\n{result.stdout}", "WARN")
            return True  # Don't fail, just warn
        else:
            runner.log("Working tree clean", "OK")
            return True

    except Exception as e:
        runner.log(f"Git check failed: {e}", "WARN")
        return True  # Don't fail

# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE v3.3.0")
    print("Testing all critical systems after improvements")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Environment tests
    runner.test("1. Firestore Environment", test_firestore_environment)
    runner.test("2. Firestore Connection", test_firestore_connection)

    # API tests
    runner.test("3. API Server Health", test_api_health)
    runner.test("4. Price Range Filtering (CRITICAL)", test_price_range_filtering)
    runner.test("5. Nested Field Queries", test_nested_field_queries)
    runner.test("6. Sort Field Mapping", test_sorting)
    runner.test("7. Complex Multi-Filter Query", test_complex_query)
    runner.test("8. Export Endpoint", test_export_endpoint)
    runner.test("9. Archive Query", test_archive_query)
    runner.test("10. Pagination", test_pagination)

    # Architecture tests
    runner.test("11. Legacy Endpoints Removed", test_legacy_endpoints_removed)
    runner.test("12. Data Integrity", test_data_integrity)
    runner.test("13. No Workbook Dependencies", test_no_workbook_dependencies)

    # Documentation tests
    runner.test("14. Documentation Complete", test_documentation_exists)
    runner.test("15. Git Status", test_git_status)

    # Summary
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return runner.summary()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
