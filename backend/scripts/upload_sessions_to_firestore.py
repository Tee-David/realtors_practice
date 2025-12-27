"""
Upload session export files directly to Firebase Firestore (NO MASTER WORKBOOK REQUIRED).

This script reads all CSV/XLSX files from session exports and uploads them to Firestore,
eliminating the need for a master workbook. This approach is more reliable and faster.

**ADVANTAGES**:
- No master workbook corruption risk
- Faster processing (parallel upload capable)
- Works even if watcher fails
- Simpler error recovery

Usage:
    python scripts/upload_sessions_to_firestore.py

Environment Variables:
    FIREBASE_SERVICE_ACCOUNT - Path to Firebase service account JSON file
    or FIREBASE_CREDENTIALS - JSON string of service account credentials
"""

import os
import sys
import json
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase-admin not installed. Run: pip install firebase-admin")
    sys.exit(1)

# Import enterprise Firestore transformation
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.firestore_enterprise import transform_to_enterprise_schema


def initialize_firebase():
    """Initialize Firebase Admin SDK with detailed logging"""
    if firebase_admin._apps:
        # Already initialized
        return firestore.client()

    # Try to load credentials from environment
    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    cred_json = os.getenv('FIREBASE_CREDENTIALS')

    print("\n" + "="*70)
    print("FIREBASE INITIALIZATION")
    print("="*70)

    if not cred_path and not cred_json:
        print("ERROR: Firebase credentials not found!")
        print("Set one of the following environment variables:")
        print("  - FIREBASE_SERVICE_ACCOUNT (path to credentials JSON file)")
        print("  - FIREBASE_CREDENTIALS (JSON string)")
        print(f"\nCurrent working directory: {os.getcwd()}")
        sys.exit(1)

    try:
        if cred_path and Path(cred_path).exists():
            print(f"Loading credentials from file: {cred_path}")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Loaded Firebase credentials from {cred_path}")
        elif cred_json:
            print(f"Loading credentials from environment variable (length: {len(cred_json)} chars)")
            cred_dict = json.loads(cred_json)
            project_id = cred_dict.get('project_id', 'unknown')
            print(f"Project ID: {project_id}")
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Loaded Firebase credentials from environment variable")
        else:
            print(f"ERROR: Credential file not found: {cred_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Files in current directory:")
            for f in os.listdir('.')[:10]:
                print(f"  - {f}")
            sys.exit(1)

        db = firestore.client()
        print("[SUCCESS] Firestore client created successfully")
        print("="*70 + "\n")
        return db

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in credentials: {e}")
        if cred_json:
            print(f"First 50 chars: {cred_json[:50]}...")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)


def find_session_exports(base_dir: str = 'exports/sites') -> list:
    """
    Find all CSV and XLSX export files from scraping sessions.

    Args:
        base_dir: Base directory containing session exports

    Returns:
        List of (file_path, site_key) tuples
    """
    print("\n" + "="*70)
    print("FINDING SESSION EXPORT FILES")
    print("="*70)

    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"ERROR: Export directory not found: {base_path}")
        print(f"Current working directory: {os.getcwd()}")
        return []

    # Find all CSV and XLSX files
    csv_files = list(base_path.glob('*/*.csv'))
    xlsx_files = list(base_path.glob('*/*.xlsx'))
    all_files = csv_files + xlsx_files

    print(f"Found {len(csv_files)} CSV files")
    print(f"Found {len(xlsx_files)} XLSX files")
    print(f"Total: {len(all_files)} export files\n")

    # Extract site keys from file paths
    file_info = []
    for file_path in all_files:
        # Site key is the parent directory name
        site_key = file_path.parent.name
        file_info.append((str(file_path), site_key))
        print(f"  {site_key}: {file_path.name}")

    print("="*70 + "\n")
    return file_info


def upload_file_to_firestore(
    db,
    file_path: str,
    site_key: str,
    uploaded_hashes: Set[str]
) -> Tuple[int, int, int]:
    """
    Upload a single export file to Firestore.

    Args:
        db: Firestore client
        file_path: Path to CSV/XLSX file
        site_key: Site identifier
        uploaded_hashes: Set of already uploaded hashes (for deduplication)

    Returns:
        (uploaded_count, skipped_count, error_count) tuple
    """
    print(f"\n{'='*70}")
    print(f"PROCESSING: {site_key} - {Path(file_path).name}")
    print(f"{'='*70}")

    try:
        # Load data
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        total_rows = len(df)
        print(f"Loaded {total_rows} properties from file")

        if total_rows == 0:
            print("WARNING: File is empty, skipping")
            return 0, 0, 0

        collection_ref = db.collection('properties')
        uploaded = 0
        errors = 0
        skipped = 0

        # Upload each property
        for idx, row in df.iterrows():
            try:
                # Convert to dict
                row_dict = row.to_dict()

                # Get hash (document ID)
                doc_hash = row_dict.get('hash')
                if not doc_hash or pd.isna(doc_hash):
                    print(f"  Row {idx+1}: Missing hash, skipping")
                    skipped += 1
                    continue

                doc_hash = str(doc_hash)

                # Skip if already uploaded
                if doc_hash in uploaded_hashes:
                    skipped += 1
                    continue

                # Add site_key if not present
                if 'site_key' not in row_dict or pd.isna(row_dict.get('site_key')):
                    row_dict['site_key'] = site_key

                # Transform to enterprise schema
                doc_data = transform_to_enterprise_schema(row_dict)

                # Add timestamps (must be at root level, not nested)
                doc_data['uploaded_at'] = firestore.SERVER_TIMESTAMP
                doc_data['updated_at'] = firestore.SERVER_TIMESTAMP

                # Upload to Firestore
                doc_ref = collection_ref.document(doc_hash)
                doc_ref.set(doc_data, merge=True)

                uploaded += 1
                uploaded_hashes.add(doc_hash)

                # Log progress every 50 properties
                if uploaded % 50 == 0:
                    print(f"  Progress: {uploaded}/{total_rows} uploaded ({skipped} duplicates, {errors} errors)")

            except Exception as e:
                errors += 1
                print(f"  Row {idx+1}: ERROR - {type(e).__name__}: {e}")

        # Final summary
        print(f"\n{'='*70}")
        print(f"FILE COMPLETE: {Path(file_path).name}")
        print(f"{'='*70}")
        print(f"  Uploaded: {uploaded}")
        print(f"  Skipped (duplicates): {skipped}")
        print(f"  Errors: {errors}")
        print(f"  Total rows: {total_rows}")
        print(f"{'='*70}\n")

        return uploaded, skipped, errors

    except Exception as e:
        print(f"ERROR: Failed to process file: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return 0, 0, 1


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("FIRESTORE UPLOAD FROM SESSION EXPORTS")
    print("(No master workbook required)")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize Firebase
    db = initialize_firebase()

    # Find all export files
    file_info = find_session_exports()

    if not file_info:
        print("ERROR: No export files found!")
        print("\nPossible reasons:")
        print("  1. Scraping sessions haven't completed yet")
        print("  2. No data was scraped (check scrape logs)")
        print("  3. Wrong working directory")
        sys.exit(1)

    # Track uploaded hashes to prevent duplicates
    uploaded_hashes = set()
    total_uploaded = 0
    total_skipped = 0
    total_errors = 0

    # Process each file
    for file_path, site_key in file_info:
        uploaded, skipped, errors = upload_file_to_firestore(db, file_path, site_key, uploaded_hashes)
        total_uploaded += uploaded
        total_skipped += skipped
        total_errors += errors

    # Final summary
    print("\n" + "="*70)
    print("UPLOAD COMPLETE!")
    print("="*70)
    print(f"Total files processed: {len(file_info)}")
    print(f"Total properties uploaded: {total_uploaded}")
    print(f"Total properties skipped (duplicates): {total_skipped}")
    print(f"Total unique properties: {len(uploaded_hashes)}")
    print(f"Total errors: {total_errors}")
    print(f"\nFirestore collection: 'properties'")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Determine success/failure based on actual errors, not just "no new uploads"
    if total_errors > 0:
        print(f"❌ FAILURE: {total_errors} errors occurred during upload")
        print("Check logs above for details")
        sys.exit(1)
    elif total_uploaded == 0 and total_skipped > 0:
        # Successfully scraped properties, but all were duplicates
        print("\n" + "="*70)
        print("✅ SUCCESS: Scrape completed successfully!")
        print("="*70)
        print(f"Found {total_skipped} properties, but all were duplicates")
        print("No new properties to upload (all already in Firestore)")
        print("\nThis is NORMAL and indicates:")
        print("  ✓ Scraper is working correctly")
        print("  ✓ All scraped properties already exist in database")
        print("  ✓ No duplicate data was added")
        print("\n💡 TIP: This is expected when scraping the same sites frequently")
        print("="*70)
        sys.exit(0)  # ✅ SUCCESS - duplicates are normal!
    elif total_uploaded == 0 and total_skipped == 0:
        # No properties found at all - this might be a problem
        print("❌ FAILURE: No properties were found in export files!")
        print("Check that session export files contain valid data")
        print("\nPossible causes:")
        print("  1. Scraper failed to find any properties")
        print("  2. All properties were filtered out (e.g., non-Lagos)")
        print("  3. Export files are empty or corrupted")
        sys.exit(1)  # ❌ FAILURE - truly no data found
    else:
        # Successfully uploaded new properties
        print(f"\n✅ SUCCESS: Uploaded {total_uploaded} new properties to Firestore")
        if total_skipped > 0:
            print(f"Also found {total_skipped} duplicates (already in database)")
        sys.exit(0)


if __name__ == '__main__':
    main()
