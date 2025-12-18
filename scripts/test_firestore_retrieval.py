"""
Test script to diagnose Firestore data retrieval issues.
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firestore_connection():
    """Test Firestore connection and data retrieval."""

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    credentials_json = os.getenv('FIREBASE_CREDENTIALS')

    print("=" * 60)
    print("FIRESTORE DIAGNOSTIC TEST")
    print("=" * 60)

    # Check credentials
    print("\n1. Checking Firebase Credentials...")
    if service_account_path:
        print(f"   [OK] FIREBASE_SERVICE_ACCOUNT: {service_account_path}")
        if os.path.exists(service_account_path):
            print(f"   [OK] File exists: {service_account_path}")
        else:
            print(f"   [FAIL] File NOT found: {service_account_path}")
            return False
    elif credentials_json:
        print(f"   [OK] FIREBASE_CREDENTIALS: Set ({len(credentials_json)} chars)")
    else:
        print("   [FAIL] No Firebase credentials found!")
        print("   Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS in .env")
        return False

    # Initialize Firebase
    print("\n2. Initializing Firebase Admin SDK...")
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import json

        if service_account_path:
            cred = credentials.Certificate(service_account_path)
        else:
            cred_dict = json.loads(credentials_json)
            cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred)
        print("   [OK] Firebase Admin SDK initialized")

        db = firestore.client()
        print("   [OK] Firestore client created")

    except Exception as e:
        print(f"   [FAIL] Failed to initialize: {e}")
        return False

    # Test collection access
    print("\n3. Testing 'properties' collection access...")
    try:
        collection_ref = db.collection('properties')
        print("   [OK] Collection reference created")

        # Try to get a count (with limit to avoid timeout)
        docs = list(collection_ref.limit(1).stream())
        if docs:
            print(f"   [OK] Collection is accessible and has data!")
            print(f"   Sample document ID: {docs[0].id}")
        else:
            print("   [WARN] Collection exists but is EMPTY")
            return True  # Connection works, just no data

    except Exception as e:
        print(f"   [FAIL] Failed to access collection: {e}")
        return False

    # Test nested field queries
    print("\n4. Testing nested field queries (enterprise schema)...")
    try:
        # Query with nested field path
        query = collection_ref.where('basic_info.status', '==', 'available').limit(5)
        results = list(query.stream())

        print(f"   [OK] Nested field query successful!")
        print(f"   Found {len(results)} properties with status='available'")

        if results:
            # Display first property structure
            sample_doc = results[0].to_dict()
            print(f"\n   Sample property structure:")
            print(f"   - basic_info: {'[OK]' if 'basic_info' in sample_doc else '[FAIL]'}")
            print(f"   - financial: {'[OK]' if 'financial' in sample_doc else '[FAIL]'}")
            print(f"   - location: {'[OK]' if 'location' in sample_doc else '[FAIL]'}")
            print(f"   - property_details: {'[OK]' if 'property_details' in sample_doc else '[FAIL]'}")

            if 'basic_info' in sample_doc:
                print(f"\n   basic_info fields:")
                for key in sample_doc.get('basic_info', {}).keys():
                    print(f"     - {key}")

    except Exception as e:
        print(f"   [FAIL] Nested field query failed: {e}")
        print(f"\n   POSSIBLE CAUSE: Composite index missing!")
        print(f"   You may need to create indexes in Firebase Console")
        print(f"   Check firestore.indexes.json and deploy indexes")
        return False

    # Test query functions
    print("\n5. Testing query functions...")
    try:
        from core.firestore_queries_enterprise import (
            get_dashboard_stats,
            get_cheapest_properties,
            get_properties_by_listing_type
        )

        print("   Testing get_dashboard_stats()...")
        stats = get_dashboard_stats()
        if stats:
            print(f"   [OK] Dashboard stats: {stats.get('total_properties', 0)} properties")
        else:
            print("   [WARN] Dashboard stats returned empty")

        print("   Testing get_cheapest_properties()...")
        cheap = get_cheapest_properties(limit=5)
        print(f"   [OK] Cheapest properties: {len(cheap)} results")

        print("   Testing get_properties_by_listing_type()...")
        for_sale = get_properties_by_listing_type('sale', limit=5)
        print(f"   [OK] For sale properties: {len(for_sale)} results")

    except Exception as e:
        print(f"   [FAIL] Query function failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nFirestore is working correctly.")
    print("If Postman shows no data, check:")
    print("1. API server is running (python api_server.py)")
    print("2. Environment variables are set in API server process")
    print("3. You're calling the correct endpoint URL")
    print("=" * 60)

    return True


if __name__ == '__main__':
    success = test_firestore_connection()
    sys.exit(0 if success else 1)
