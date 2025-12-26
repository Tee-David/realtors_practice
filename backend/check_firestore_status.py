#!/usr/bin/env python3
"""Quick script to check Firestore property counts by status"""

import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from core.firestore_enterprise import _get_firestore_client

def check_counts():
    db = _get_firestore_client()
    if not db:
        print("Failed to connect to Firestore")
        return

    properties_ref = db.collection('properties')
    all_docs = list(properties_ref.stream())

    print(f"Total documents in Firestore: {len(all_docs)}")

    # Count by listing_type
    by_type = {}
    by_status = {}
    for_sale_by_status = {}

    for doc in all_docs:
        data = doc.to_dict()
        listing_type = data.get('basic_info', {}).get('listing_type', 'unknown')
        status = data.get('basic_info', {}).get('status', 'unknown')

        # Count by type
        by_type[listing_type] = by_type.get(listing_type, 0) + 1

        # Count by status
        by_status[status] = by_status.get(status, 0) + 1

        # Count for-sale by status
        if listing_type == 'sale':
            for_sale_by_status[status] = for_sale_by_status.get(status, 0) + 1

    print("\nBy listing_type:")
    for type_name, count in sorted(by_type.items()):
        print(f"  {type_name}: {count}")

    print("\nBy status (all properties):")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")

    print("\nFor-sale properties by status:")
    for status, count in sorted(for_sale_by_status.items()):
        print(f"  {status}: {count}")

    # Calculate what we should see
    sale_available = sum(1 for doc in all_docs
                        if doc.to_dict().get('basic_info', {}).get('listing_type') == 'sale'
                        and doc.to_dict().get('basic_info', {}).get('status') == 'available')

    print(f"\nExpected count for listing_type='sale' AND status='available': {sale_available}")

if __name__ == '__main__':
    check_counts()
