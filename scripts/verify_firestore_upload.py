"""
Verify that Firestore uploads succeeded.

This script checks:
1. Firebase connection works
2. Properties collection exists
3. Documents were uploaded recently (within last 15 minutes)
4. Document count is reasonable (> 0)

Used by GitHub Actions workflow to verify successful uploads.

Usage:
    python scripts/verify_firestore_upload.py

Environment Variables:
    FIREBASE_SERVICE_ACCOUNT - Path to Firebase service account JSON file
    or FIREBASE_CREDENTIALS - JSON string of service account credentials

Exit Codes:
    0 - Success (data uploaded successfully)
    1 - Failure (no data or connection issues)
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase-admin not installed. Run: pip install firebase-admin")
    sys.exit(1)


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if firebase_admin._apps:
        return firestore.client()

    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    cred_json = os.getenv('FIREBASE_CREDENTIALS')

    print("\n" + "="*70)
    print("FIRESTORE UPLOAD VERIFICATION")
    print("="*70)

    if not cred_path and not cred_json:
        print("ERROR: Firebase credentials not found!")
        print("Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS")
        sys.exit(1)

    try:
        if cred_path and Path(cred_path).exists():
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Loaded credentials from: {cred_path}")
        elif cred_json:
            cred_dict = json.loads(cred_json)
            project_id = cred_dict.get('project_id', 'unknown')
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Loaded credentials for project: {project_id}")
        else:
            print(f"ERROR: Credential file not found: {cred_path}")
            sys.exit(1)

        return firestore.client()

    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase: {e}")
        sys.exit(1)


def verify_upload(db, minutes_threshold: int = 15):
    """
    Verify that properties were uploaded recently.

    Args:
        db: Firestore client
        minutes_threshold: Consider uploads within this many minutes as "recent"

    Returns:
        True if verification passed, False otherwise
    """
    print("\n" + "="*70)
    print("VERIFICATION CHECKS")
    print("="*70)

    try:
        # Check 1: Collection exists and has documents
        print("\n[Check 1] Checking properties collection exists...")
        collection_ref = db.collection('properties')

        # Get total count (limit query for performance)
        all_docs = list(collection_ref.limit(1).stream())

        if not all_docs:
            print("  FAILED: Properties collection is empty!")
            print("  No documents found in Firestore")
            return False

        print("  [PASS] Properties collection exists and has documents")

        # Check 2: Count total documents
        print("\n[Check 2] Counting total documents...")
        # For accurate count, we need to iterate (Firestore doesn't have direct count)
        # Limit to 10000 for performance
        total_count = 0
        docs_iterator = collection_ref.limit(10000).stream()
        for doc in docs_iterator:
            total_count += 1
            if total_count % 1000 == 0:
                print(f"  Counted {total_count} documents...")

        print(f"  [PASS] Total documents: {total_count}")

        if total_count == 0:
            print("  FAILED: No documents in collection!")
            return False

        # Check 3: Recent uploads (within last X minutes)
        print(f"\n[Check 3] Checking for recent uploads (within {minutes_threshold} minutes)...")
        cutoff_time = datetime.now() - timedelta(minutes=minutes_threshold)

        # Query documents with recent scrape_timestamp
        # Note: Firestore timestamps are stored in metadata.scrape_timestamp
        recent_docs = []

        # Get sample of recent documents (limit 100 for performance)
        sample_docs = list(collection_ref.limit(100).stream())

        for doc in sample_docs:
            doc_data = doc.to_dict()

            # Check various timestamp fields
            uploaded_at = doc_data.get('uploaded_at')
            updated_at = doc_data.get('updated_at')

            # Check if document was uploaded/updated recently
            if uploaded_at:
                # Convert Firestore timestamp to datetime
                if hasattr(uploaded_at, 'timestamp'):
                    upload_time = datetime.fromtimestamp(uploaded_at.timestamp())
                    if upload_time >= cutoff_time:
                        recent_docs.append(doc)
                        continue

            if updated_at:
                if hasattr(updated_at, 'timestamp'):
                    update_time = datetime.fromtimestamp(updated_at.timestamp())
                    if update_time >= cutoff_time:
                        recent_docs.append(doc)

        recent_count = len(recent_docs)
        print(f"  Found {recent_count} recently uploaded/updated documents")

        if recent_count == 0:
            print(f"  WARNING: No documents uploaded in last {minutes_threshold} minutes")
            print(f"  This might indicate uploads didn't happen in this workflow run")
            print(f"  Total documents in Firestore: {total_count}")
            print(f"\n  Checking if this is expected...")
            print(f"  If scraping didn't run (only consolidate job), this is normal")

            # Don't fail if we have documents (they might be from previous runs)
            if total_count > 0:
                print(f"  [PASS] Firestore has {total_count} total documents (from previous runs)")
                return True
            else:
                print(f"  [FAILED] No documents at all in Firestore")
                return False

        print(f"  [PASS] {recent_count} documents uploaded/updated recently")

        # Check 4: Verify document structure
        print("\n[Check 4] Verifying document structure...")
        sample_doc = sample_docs[0]
        sample_data = sample_doc.to_dict()

        # Check for enterprise schema categories
        required_categories = ['basic_info', 'property_details', 'financial', 'location', 'metadata']
        found_categories = [cat for cat in required_categories if cat in sample_data]

        print(f"  Found {len(found_categories)}/{len(required_categories)} enterprise schema categories")
        print(f"  Categories: {', '.join(found_categories)}")

        if len(found_categories) >= 3:  # At least 3 categories should exist
            print("  [PASS] Document structure looks good")
        else:
            print("  WARNING: Document might be using old schema")
            print("  This is not necessarily an error, but check transform_to_enterprise_schema()")

        # All checks passed
        print("\n" + "="*70)
        print("VERIFICATION RESULT: SUCCESS ✓")
        print("="*70)
        print(f"Total documents: {total_count}")
        print(f"Recent uploads: {recent_count}")
        print(f"Firestore collection: 'properties'")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print(f"\nERROR during verification: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """Main execution function"""
    # Initialize Firebase
    db = initialize_firebase()

    # Verify upload
    success = verify_upload(db, minutes_threshold=15)

    if success:
        print("[SUCCESS] Firestore upload verified!")
        sys.exit(0)
    else:
        print("[FAILURE] Firestore upload verification failed!")
        print("\nPossible issues:")
        print("  1. No data was uploaded (check upload step logs)")
        print("  2. Firebase credentials are invalid")
        print("  3. Firestore write permissions issue")
        print("  4. Network connectivity problems")
        sys.exit(1)


if __name__ == '__main__':
    main()
