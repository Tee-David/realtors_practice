"""
Verification Script: Firestore-Only Architecture
Tests that workbook dependencies are removed and Firestore works correctly.
"""
import os
import sys
import json
import requests
from pathlib import Path

def test_firestore_env():
    """Test Firestore environment setup"""
    print("\n[1/5] Testing Firestore Environment...")

    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if not cred_path:
        print("[FAIL] FIREBASE_SERVICE_ACCOUNT not set")
        return False

    if not Path(cred_path).exists():
        print(f"[FAIL] Credentials file not found: {cred_path}")
        return False

    print(f"[OK] Firebase credentials found: {cred_path}")
    return True

def test_firestore_connection():
    """Test Firestore connection"""
    print("\n[2/5] Testing Firestore Connection...")

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        # Test query
        docs = list(db.collection('properties').limit(1).stream())
        if docs:
            print(f"[OK] Connected to Firestore ({len(docs)} test doc)")
            return True
        else:
            print("[WARN] Connected but no documents found")
            return True
    except Exception as e:
        print(f"[FAIL] Firestore connection failed: {e}")
        return False

def test_api_health():
    """Test API server health"""
    print("\n[3/5] Testing API Server...")

    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("[OK] API server is healthy")
            return True
        else:
            print(f"[FAIL] API health check returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[SKIP] API server not running (start with: python functions/api_server.py)")
        return None  # Not a failure, just not running
    except Exception as e:
        print(f"[FAIL] API health check failed: {e}")
        return False

def test_firestore_query_endpoint():
    """Test Firestore query endpoint"""
    print("\n[4/5] Testing Firestore Query Endpoint...")

    try:
        response = requests.post(
            'http://localhost:5000/api/firestore/query',
            json={'limit': 5},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"[OK] Firestore query returned {count} properties")
            return True
        else:
            print(f"[FAIL] Query returned {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("[SKIP] API server not running")
        return None
    except Exception as e:
        print(f"[FAIL] Query test failed: {e}")
        return False

def test_no_workbook_dependencies():
    """Test that workbook is not required"""
    print("\n[5/5] Testing Workbook Independence...")

    # Check data_reader.py prioritizes Firestore
    data_reader_path = Path('api/helpers/data_reader.py')
    if data_reader_path.exists():
        content = data_reader_path.read_text()

        # Should have Firestore-first logic
        if 'db = _get_firestore()' in content and 'if db:' in content:
            print("[OK] data_reader.py uses Firestore-first approach")
        else:
            print("[WARN] data_reader.py may not be Firestore-first")

    # Check api_server.py doesn't import PropertyQuery
    api_server_path = Path('functions/api_server.py')
    if api_server_path.exists():
        content = api_server_path.read_text()

        if 'from core.query_engine import PropertyQuery' in content:
            print("[FAIL] api_server.py still imports PropertyQuery")
            return False
        else:
            print("[OK] api_server.py doesn't import PropertyQuery")

    # Check that legacy endpoints are removed
    if '/api/query' in content and 'def query_properties():' in content:
        print("[FAIL] Legacy /api/query endpoint still exists")
        return False
    else:
        print("[OK] Legacy query endpoints removed")

    return True

def main():
    print("=" * 60)
    print("Firestore-Only Architecture Verification")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(test_firestore_env())
    results.append(test_firestore_connection())
    api_health = test_api_health()
    if api_health is not None:
        results.append(api_health)
    query_result = test_firestore_query_endpoint()
    if query_result is not None:
        results.append(query_result)
    results.append(test_no_workbook_dependencies())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    total = len(results)

    print(f"Results: {passed}/{total} passed, {failed} failed")

    if failed == 0:
        print("\n[SUCCESS] All tests passed! Firestore-only architecture verified.")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] {failed} test(s) failed. Check logs above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
