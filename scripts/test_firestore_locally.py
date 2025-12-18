"""
Test Firestore connection and upload functionality locally.

This script helps debug Firebase/Firestore issues before deploying to GitHub Actions.
It performs a comprehensive test of the entire upload pipeline.

Usage:
    python scripts/test_firestore_locally.py

Requirements:
    - .env file with FIREBASE_SERVICE_ACCOUNT set
    OR
    - FIREBASE_CREDENTIALS environment variable
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase-admin not installed")
    print("Run: pip install firebase-admin")
    sys.exit(1)

from core.firestore_enterprise import (
    _get_firestore_client,
    transform_to_enterprise_schema,
    EnterpriseFirestoreUploader
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def test_environment():
    """Test 1: Check environment variables"""
    print_header("TEST 1: Environment Variables")

    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    cred_json = os.getenv('FIREBASE_CREDENTIALS')

    print(f"FIREBASE_SERVICE_ACCOUNT: {cred_path if cred_path else 'NOT SET'}")
    print(f"FIREBASE_CREDENTIALS: {'SET (length=' + str(len(cred_json)) + ')' if cred_json else 'NOT SET'}")
    print(f"FIRESTORE_ENABLED: {os.getenv('FIRESTORE_ENABLED', '1')}")
    print(f"Current directory: {os.getcwd()}")

    if not cred_path and not cred_json:
        print("\n[FAIL] No Firebase credentials found!")
        print("\nTo fix:")
        print("  1. Create .env file in project root")
        print("  2. Add: FIREBASE_SERVICE_ACCOUNT=path/to/credentials.json")
        print("  3. Or set FIREBASE_CREDENTIALS environment variable")
        return False

    if cred_path:
        if Path(cred_path).exists():
            print(f"\n[PASS] Credential file exists: {cred_path}")
        else:
            print(f"\n[FAIL] Credential file not found: {cred_path}")
            return False

    print("\n[PASS] Environment variables configured correctly")
    return True


def test_firebase_initialization():
    """Test 2: Firebase initialization"""
    print_header("TEST 2: Firebase Initialization")

    try:
        db = _get_firestore_client()

        if db is None:
            print("[FAIL] Firebase initialization returned None")
            print("Check logs above for error details")
            return False

        print("[PASS] Firebase initialized successfully")
        print(f"Firestore client type: {type(db)}")
        return True

    except Exception as e:
        print(f"[FAIL] Exception during initialization: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_firestore_connection():
    """Test 3: Firestore connection"""
    print_header("TEST 3: Firestore Connection")

    try:
        db = _get_firestore_client()
        if not db:
            print("[FAIL] Cannot test connection - Firebase not initialized")
            return False

        # Try to access properties collection
        collection_ref = db.collection('properties')
        print("Attempting to query properties collection...")

        # Get first document (if any)
        docs = list(collection_ref.limit(1).stream())

        if docs:
            print(f"[PASS] Successfully connected to Firestore")
            print(f"Found {len(docs)} document(s) in 'properties' collection")
            doc = docs[0]
            print(f"Sample document ID: {doc.id}")
        else:
            print("[PASS] Successfully connected to Firestore")
            print("NOTE: 'properties' collection is empty (no documents yet)")

        return True

    except Exception as e:
        print(f"[FAIL] Connection error: {type(e).__name__}: {e}")
        print("\nPossible causes:")
        print("  1. Invalid credentials")
        print("  2. Network connectivity issue")
        print("  3. Firestore API not enabled in Firebase project")
        print("  4. Service account lacks Firestore permissions")
        return False


def test_document_structure():
    """Test 4: Test enterprise schema transformation"""
    print_header("TEST 4: Enterprise Schema Transformation")

    try:
        # Create dummy property
        dummy_property = {
            'hash': 'test_property_12345',
            'title': '4 Bedroom Duplex in Lekki',
            'price': 75000000,
            'bedrooms': 4,
            'bathrooms': 3,
            'location': 'Lekki Phase 1, Lagos',
            'property_type': 'Duplex',
            'description': 'Newly built 4 bedroom duplex with BQ in a serene estate. Fully furnished with modern amenities.',
            'site_key': 'test_site',
            'source': 'Test',
            'listing_url': 'https://example.com/test',
            'scrape_timestamp': datetime.now().isoformat(),
            'quality_score': 0.85
        }

        print("Transforming dummy property to enterprise schema...")
        transformed = transform_to_enterprise_schema(dummy_property)

        # Check for required categories
        required_categories = ['basic_info', 'property_details', 'financial', 'location', 'metadata', 'tags']
        found_categories = [cat for cat in required_categories if cat in transformed]

        print(f"\nFound categories: {', '.join(found_categories)}")
        print(f"Categories found: {len(found_categories)}/{len(required_categories)}")

        # Print sample data
        print("\nSample transformed data:")
        if 'basic_info' in transformed:
            print(f"  basic_info.title: {transformed['basic_info'].get('title')}")
        if 'financial' in transformed:
            print(f"  financial.price: {transformed['financial'].get('price')}")
        if 'location' in transformed:
            print(f"  location.area: {transformed['location'].get('area')}")
        if 'tags' in transformed:
            print(f"  tags.premium: {transformed['tags'].get('premium')}")

        if len(found_categories) >= 4:
            print("\n[PASS] Schema transformation working correctly")
            return True
        else:
            print("\n[FAIL] Schema transformation incomplete")
            return False

    except Exception as e:
        print(f"[FAIL] Transformation error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_upload():
    """Test 5: Test actual upload"""
    print_header("TEST 5: Test Upload to Firestore")

    try:
        # Create test property
        test_property = {
            'hash': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'title': 'TEST PROPERTY - DELETE ME',
            'price': 1000000,
            'bedrooms': 3,
            'bathrooms': 2,
            'location': 'Test Location, Lagos',
            'property_type': 'Apartment',
            'description': 'This is a test property created by test_firestore_locally.py',
            'site_key': 'test_site',
            'source': 'Local Test',
            'listing_url': 'https://example.com/test',
            'scrape_timestamp': datetime.now().isoformat(),
            'quality_score': 1.0
        }

        print("Creating EnterpriseFirestoreUploader...")
        uploader = EnterpriseFirestoreUploader()

        if not uploader.enabled:
            print("[FAIL] Uploader is disabled")
            print("Check initialization logs above")
            return False

        print("Uploading test property...")
        result = uploader.upload_listings_batch('test_site', [test_property])

        uploaded = result.get('uploaded', 0)
        errors = result.get('errors', 0)
        status = result.get('status', 'unknown')

        print(f"\nUpload result:")
        print(f"  Uploaded: {uploaded}")
        print(f"  Errors: {errors}")
        print(f"  Status: {status}")

        if status == 'failed':
            print("\n[FAIL] Upload failed")
            print("Check error logs above")
            return False
        elif uploaded == 1:
            print(f"\n[PASS] Successfully uploaded test property")
            print(f"Document ID: {test_property['hash']}")
            print("\nNOTE: Remember to delete this test document from Firestore console")
            return True
        else:
            print(f"\n[FAIL] Upload completed but uploaded count is {uploaded} (expected 1)")
            return False

    except Exception as e:
        print(f"[FAIL] Upload error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_query():
    """Test 6: Query uploaded document"""
    print_header("TEST 6: Query Document")

    try:
        db = _get_firestore_client()
        if not db:
            print("[FAIL] Cannot test query - Firebase not initialized")
            return False

        # Query properties from test_site
        collection_ref = db.collection('properties')
        query = collection_ref.where('basic_info.site_key', '==', 'test_site').limit(1)

        print("Querying for test properties...")
        docs = list(query.stream())

        if docs:
            doc = docs[0]
            doc_data = doc.to_dict()
            print(f"\n[PASS] Successfully queried document")
            print(f"Document ID: {doc.id}")
            print(f"Title: {doc_data.get('basic_info', {}).get('title', 'N/A')}")
            print(f"Price: {doc_data.get('financial', {}).get('price', 'N/A')}")
            return True
        else:
            print("\n[FAIL] No documents found with site_key='test_site'")
            print("Upload may have failed, or query field path is incorrect")
            return False

    except Exception as e:
        print(f"[FAIL] Query error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FIRESTORE LOCAL TESTING SUITE")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Environment Variables", test_environment),
        ("Firebase Initialization", test_firebase_initialization),
        ("Firestore Connection", test_firestore_connection),
        ("Schema Transformation", test_document_structure),
        ("Upload Test", test_upload),
        ("Query Test", test_query)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\nUNEXPECTED ERROR in {test_name}: {e}")
            results.append((test_name, False))

        # Stop if critical tests fail
        if not passed and test_name in ["Environment Variables", "Firebase Initialization"]:
            print(f"\n[CRITICAL] {test_name} failed - stopping further tests")
            break

    # Summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n[SUCCESS] All tests passed! ✓")
        print("Firestore integration is working correctly")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] {total_count - passed_count} test(s) failed")
        print("\nRecommendations:")
        print("  1. Fix failed tests before deploying to GitHub Actions")
        print("  2. Check Firebase Console for permissions/setup issues")
        print("  3. Verify credentials are valid and not expired")
        sys.exit(1)


if __name__ == '__main__':
    main()
