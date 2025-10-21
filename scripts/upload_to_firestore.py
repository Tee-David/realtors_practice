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
        print(f"✓ Loaded Firebase credentials from {cred_path}")
    elif cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        print("✓ Loaded Firebase credentials from environment variable")
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


def upload_to_firestore(workbook_path='exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx', batch_size=500):
    """
    Upload master workbook to Firestore

    Args:
        workbook_path: Path to master workbook Excel file
        batch_size: Number of documents to write per batch (Firestore limit: 500)
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
    print(f"✓ Loaded {total_records:,} properties\n")

    # Upload to Firestore in batches
    collection_ref = db.collection('properties')
    batch = db.batch()
    uploaded = 0
    errors = 0

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

            # Commit batch every batch_size documents
            if uploaded % batch_size == 0:
                batch.commit()
                print(f"  ✓ Uploaded {uploaded:,}/{total_records:,} properties ({uploaded/total_records*100:.1f}%)")
                batch = db.batch()

        except Exception as e:
            errors += 1
            print(f"  ✗ Error uploading property {idx}: {e}")

    # Commit final batch
    if uploaded % batch_size != 0:
        batch.commit()

    print(f"\n{'='*60}")
    print(f"Upload Complete!")
    print(f"{'='*60}")
    print(f"✓ Successfully uploaded: {uploaded:,} properties")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print(f"\nFirestore collection: 'properties'")
    print(f"Total documents: {uploaded:,}")
    print(f"{'='*60}\n")

    return {
        'uploaded': uploaded,
        'errors': errors,
        'total': total_records
    }


if __name__ == '__main__':
    upload_to_firestore()
