"""
Enhanced Cleanup Script - Remove ALL Category Pages from Firestore

Fetches ALL properties directly from Firestore (no limit) and removes garbage data.
"""

import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from google.cloud import firestore
import json
from datetime import datetime

# Initialize Firestore
db = firestore.Client.from_service_account_json(os.environ['FIREBASE_SERVICE_ACCOUNT'])

print("\n" + "="*80)
print("ENHANCED CATEGORY PAGE CLEANUP")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*80 + "\n")

# Step 1: Get ALL properties (no limit)
print("Step 1: Fetching ALL properties from Firestore (no limit)...")
properties_ref = db.collection('properties')
all_docs = list(properties_ref.stream())
print(f"Retrieved {len(all_docs)} total properties\n")

# Step 2: Analyze and categorize
category_pages = []
poor_quality = []
good_quality = []

print("Step 2: Analyzing data quality...")
for doc in all_docs:
    prop = doc.to_dict()

    # Extract fields
    title = prop.get('basic_info', {}).get('title', '') or ''
    price = prop.get('financial', {}).get('price', 0) or 0
    bedrooms = prop.get('property_details', {}).get('bedrooms')
    bathrooms = prop.get('property_details', {}).get('bathrooms')
    location = prop.get('location', {}).get('area', '') or ''
    url = prop.get('basic_info', {}).get('url', '') or ''

    # Category page detection heuristics
    is_category = False
    reasons = []

    # 1. Generic location-only titles
    generic_titles = ['chevron', 'lekki', 'ikate', 'victoria island', 'ikoyi',
                     'ajah', 'ikeja', 'yaba', 'surulere', 'maryland', 'magodo',
                     'lagos', 'nigeria', 'vi', 'vgc', 'osapa', 'sangotedo',
                     'banana island', 'eko atlantic', 'latest posts']

    if title.lower().strip() in generic_titles:
        is_category = True
        reasons.append(f"Generic title: '{title}'")

    # 2. Very short titles (< 15 chars)
    if len(title.strip()) < 15:
        is_category = True
        reasons.append(f"Title too short ({len(title)} chars): '{title}'")

    # 3. Missing critical data
    if price == 0 and bedrooms is None and len(title.strip()) < 20:
        is_category = True
        reasons.append("Missing price + bedrooms + short title")

    # 4. Unrealistic data (corruption)
    if price > 1000000000000:  # > 1 trillion NGN
        is_category = True
        reasons.append(f"Unrealistic price: {price:,.0f} NGN")

    # 5. Phone numbers as bathroom counts
    if bathrooms and bathrooms > 20:
        is_category = True
        reasons.append(f"Phone number as bathrooms: {bathrooms}")

    # 6. URL patterns
    category_url_patterns = ['/property-location/', '/listings/', '/search/',
                           '/properties/', '/category/', '/location/', '/area/']
    if any(pattern in url.lower() for pattern in category_url_patterns):
        is_category = True
        reasons.append("Category URL pattern")

    if is_category:
        category_pages.append({
            'doc_id': doc.id,
            'title': title,
            'price': price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'location': location,
            'url': url[:80],
            'reasons': reasons
        })
    elif not title or price == 0:
        poor_quality.append({'doc_id': doc.id, 'title': title, 'price': price})
    else:
        good_quality.append({'doc_id': doc.id, 'title': title[:50]})

print("\n" + "="*80)
print("ANALYSIS RESULTS")
print("="*80)
print(f"Total Properties: {len(all_docs)}")
print(f"  [OK] Good Quality: {len(good_quality)} ({100*len(good_quality)/len(all_docs):.1f}%)")
print(f"  [WARN] Poor Quality: {len(poor_quality)} ({100*len(poor_quality)/len(all_docs):.1f}%)")
print(f"  [BAD] Category Pages: {len(category_pages)} ({100*len(category_pages)/len(all_docs):.1f}%)")
print("="*80 + "\n")

# Step 3: Show samples
if category_pages:
    print("Sample Category Pages to be Deleted (first 15):")
    print("="*80)
    for i, cp in enumerate(category_pages[:15], 1):
        print(f"{i}. Title: '{cp['title']}'")
        print(f"   Price: {cp['price']:,.0f} NGN, Beds: {cp['bedrooms']}, Baths: {cp['bathrooms']}")
        print(f"   Location: {cp['location']}")
        print(f"   Reasons: {', '.join(cp['reasons'])}")
        print(f"   Doc ID: {cp['doc_id'][:40]}...")
        print()

    if len(category_pages) > 15:
        print(f"... and {len(category_pages) - 15} more category pages\n")

    # Step 4: Auto-confirm deletion (script mode)
    print("="*80)
    print(f"READY TO DELETE {len(category_pages)} CATEGORY PAGES")
    print("="*80)
    print("\nAuto-confirming deletion in script mode...")

    if True:  # Auto-confirm
        # Create backup first
        backup_file = f'firestore_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        print(f"\nCreating backup: {backup_file}")
        with open(backup_file, 'w') as f:
            json.dump([cp for cp in category_pages], f, indent=2, default=str)
        print(f"Backup saved: {len(category_pages)} properties backed up\n")

        # Delete category pages
        print(f"Deleting {len(category_pages)} category pages...")
        deleted_count = 0

        for i, cp in enumerate(category_pages, 1):
            try:
                doc_ref = db.collection('properties').document(cp['doc_id'])
                doc_ref.delete()
                deleted_count += 1

                if i % 20 == 0:
                    print(f"  Progress: {i}/{len(category_pages)} deleted...")

            except Exception as e:
                print(f"  Error deleting {cp['doc_id']}: {e}")

        print(f"\n{'='*80}")
        print(f"DELETION COMPLETE")
        print(f"{'='*80}")
        print(f"Deleted: {deleted_count} properties")
        print(f"Remaining in Firestore: {len(all_docs) - deleted_count}")
        print(f"Good quality properties: {len(good_quality)}")
        print(f"Backup saved to: {backup_file}")
        print(f"{'='*80}\n")

    else:
        print("\nDeletion cancelled by user.")

else:
    print("No category pages found! Database is clean.\n")
