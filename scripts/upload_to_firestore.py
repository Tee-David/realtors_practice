"""
Upload master workbook data to Firebase Firestore for queryable storage.

This script reads the master workbook and uploads each property as a Firestore document,
enabling fast queries without downloading the entire dataset.

Usage:
    python scripts/upload_to_firestore.py

Environment Variables:
    FIREBASE_SERVICE_ACCOUNT - Path to Firebase service account JSON file
    or FIREBASE_CREDENTIALS - JSON string of service account credentials
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
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
        # Already initialized
        return firestore.client()

    # Try to load credentials from environment
    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    cred_json = os.getenv('FIREBASE_CREDENTIALS')

    if cred_path and Path(cred_path).exists():
        cred = credentials.Certificate(cred_path)
        print(f"[SUCCESS] Loaded Firebase credentials from {cred_path}")
    elif cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        print("[SUCCESS] Loaded Firebase credentials from environment variable")
    else:
        print("ERROR: Firebase credentials not found!")
        print("Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS environment variable")
        sys.exit(1)

    firebase_admin.initialize_app(cred)
    return firestore.client()


def clean_value(value):
    """Clean value for Firestore (handle NaN, None, etc.)"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return int(value) if value == int(value) else float(value)
    if isinstance(value, str):
        return value.strip() if value else None
    return value


def cleanup_stale_listings(db, current_hashes, max_age_days=30):
    """
    Archive stale listings that haven't been seen in recent scrapes

    IMPORTANT: This ARCHIVES (not deletes) stale listings by moving them to
    'properties_archive' collection. This preserves historical data for:
    - Price prediction models
    - Market trend analysis
    - Historical property data

    Args:
        db: Firestore client
        current_hashes: Set of property hashes from current scrape
        max_age_days: Archive properties not updated in this many days (default: 30)

    Returns:
        Number of archived properties
    """
    from datetime import timedelta

    print(f"\n{'='*60}")
    print(f"Archiving stale listings (older than {max_age_days} days)")
    print(f"{'='*60}\n")

    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    collection_ref = db.collection('properties')
    archive_ref = db.collection('properties_archive')

    # Get all documents from active collection
    all_docs = collection_ref.stream()

    to_archive = []
    checked = 0

    for doc in all_docs:
        checked += 1
        doc_data = doc.to_dict()
        doc_hash = doc_data.get('hash')
        updated_at = doc_data.get('updated_at')

        # Archive if:
        # 1. Hash not in current scrape AND
        # 2. Not updated recently (older than max_age_days)
        if doc_hash not in current_hashes:
            if updated_at and updated_at.replace(tzinfo=None) < cutoff_date:
                to_archive.append((doc.id, doc_data))

    # Archive in batches (copy to archive, then delete from active)
    archived = 0
    if to_archive:
        print(f"Found {len(to_archive):,} stale listings to archive (out of {checked:,} total)")
        batch = db.batch()

        for idx, (doc_id, doc_data) in enumerate(to_archive):
            # Add archived_at timestamp
            doc_data['archived_at'] = firestore.SERVER_TIMESTAMP
            doc_data['status'] = 'archived'

            # Copy to archive collection
            batch.set(archive_ref.document(doc_id), doc_data)

            # Remove from active collection
            batch.delete(collection_ref.document(doc_id))

            archived += 1

            # Commit every 250 operations (500 operations = 250 sets + 250 deletes)
            if (idx + 1) % 250 == 0:
                batch.commit()
                print(f"  [PROGRESS] Archived {idx + 1:,}/{len(to_archive):,} stale listings")
                batch = db.batch()

        # Commit remaining
        if archived % 250 != 0:
            batch.commit()

        print(f"[SUCCESS] Archived {archived:,} stale listings to 'properties_archive'")
        print(f"          These are preserved for price prediction & historical analysis")
    else:
        print(f"[SUCCESS] No stale listings found (checked {checked:,} properties)")

    print(f"{'='*60}\n")
    return archived


def upload_to_firestore(workbook_path='exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx',
                        batch_size=500,
                        cleanup_stale=False,
                        max_age_days=30):
    """
    Upload master workbook to Firestore

    Args:
        workbook_path: Path to master workbook Excel file
        batch_size: Number of documents to write per batch (Firestore limit: 500)
        cleanup_stale: If True, remove old listings not in current scrape (default: False)
        max_age_days: When cleanup_stale=True, remove listings older than this (default: 30)
    """
    if not Path(workbook_path).exists():
        print(f"ERROR: Master workbook not found at {workbook_path}")
        print("Run watcher.py first to create the master workbook")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Uploading to Firebase Firestore")
    print(f"{'='*60}\n")

    # Initialize Firebase
    db = initialize_firebase()

    # Load master workbook
    print(f"Loading master workbook: {workbook_path}")
    df = pd.read_excel(workbook_path)
    total_records = len(df)
    print(f"[SUCCESS] Loaded {total_records:,} properties\n")

    # Upload to Firestore in batches
    collection_ref = db.collection('properties')
    batch = db.batch()
    uploaded = 0
    errors = 0
    current_hashes = set()  # Track current scrape hashes for cleanup

    for idx, row in df.iterrows():
        try:
            # Use hash as document ID (prevents duplicates)
            doc_id = str(row.get('hash', f'property_{idx}'))
            doc_ref = collection_ref.document(doc_id)

            # Prepare document data
            doc_data = {
                'title': clean_value(row.get('title')),
                'price': clean_value(row.get('price')),
                'location': clean_value(row.get('location')),
                'bedrooms': clean_value(row.get('bedrooms')),
                'bathrooms': clean_value(row.get('bathrooms')),
                'property_type': clean_value(row.get('property_type')),
                'land_size': clean_value(row.get('land_size')),
                'description': clean_value(row.get('description')),
                'agent_name': clean_value(row.get('agent_name')),
                'agent_phone': clean_value(row.get('agent_phone')),
                'listing_url': clean_value(row.get('listing_url')),
                'images': clean_value(row.get('images')),
                'source': clean_value(row.get('source')),
                'scrape_timestamp': clean_value(row.get('scrape_timestamp')),
                'hash': clean_value(row.get('hash')),
                'quality_score': clean_value(row.get('quality_score')),

                # Metadata
                'uploaded_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
            }

            # Add coordinates if available
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                doc_data['coordinates'] = {
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude'])
                }

            # Set document in batch
            batch.set(doc_ref, doc_data, merge=True)
            uploaded += 1

            # Track hash for cleanup
            if doc_data.get('hash'):
                current_hashes.add(doc_data['hash'])

            # Commit batch every batch_size documents
            if uploaded % batch_size == 0:
                batch.commit()
                print(f"  [PROGRESS] Uploaded {uploaded:,}/{total_records:,} properties ({uploaded/total_records*100:.1f}%)")
                batch = db.batch()

        except Exception as e:
            errors += 1
            print(f"  [ERROR] Error uploading property {idx}: {e}")

    # Commit final batch
    if uploaded % batch_size != 0:
        batch.commit()

    print(f"\n{'='*60}")
    print(f"Upload Complete!")
    print(f"{'='*60}")
    print(f"[SUCCESS] Successfully uploaded: {uploaded:,} properties")
    if errors > 0:
        print(f"[ERROR] Errors: {errors}")
    print(f"\nFirestore collection: 'properties'")
    print(f"Total documents: {uploaded:,}")
    print(f"{'='*60}\n")

    # Run cleanup if enabled
    archived = 0
    if cleanup_stale:
        archived = cleanup_stale_listings(db, current_hashes, max_age_days)

    return {
        'uploaded': uploaded,
        'errors': errors,
        'total': total_records,
        'archived': archived
    }


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload master workbook to Firestore')
    parser.add_argument('--cleanup', action='store_true',
                        help='Archive stale listings (default: False)')
    parser.add_argument('--max-age-days', type=int, default=30,
                        help='Archive listings older than this many days (default: 30)')
    parser.add_argument('--workbook', type=str,
                        default='exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx',
                        help='Path to master workbook')

    args = parser.parse_args()

    upload_to_firestore(
        workbook_path=args.workbook,
        cleanup_stale=args.cleanup,
        max_age_days=args.max_age_days
    )
