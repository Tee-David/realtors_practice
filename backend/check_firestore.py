import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from google.cloud import firestore

# Initialize Firestore
db = firestore.Client.from_service_account_json(os.environ['FIREBASE_SERVICE_ACCOUNT'])

# Get all properties
properties_ref = db.collection('properties')
all_properties = list(properties_ref.stream())

print("\n" + "="*80)
print("FIRESTORE DATABASE STATUS")
print("="*80)
print(f"Total Properties: {len(all_properties)}\n")

# Analyze data quality
category_pages = []
poor_quality = []
good_quality = []

for prop_doc in all_properties:
    prop = prop_doc.to_dict()
    
    # Check if it's a category page
    title = prop.get('basic_info', {}).get('title', '') or ''
    price = prop.get('financial', {}).get('price', 0) or 0
    bedrooms = prop.get('property_details', {}).get('bedrooms')
    location = prop.get('location', {}).get('area', '') or ''
    
    # Category page detection
    is_category = (
        len(title) < 15 or
        title.lower() in ['chevron', 'lekki', 'ikate', 'victoria island', 'ikoyi', 'ajah'] or
        (price == 0 and bedrooms is None and len(title) < 20)
    )
    
    if is_category:
        category_pages.append({
            'id': prop_doc.id,
            'title': title,
            'price': price,
            'bedrooms': bedrooms,
            'location': location
        })
    elif not title or price == 0:
        poor_quality.append(prop_doc.id)
    else:
        good_quality.append(prop_doc.id)

print("Data Quality Breakdown:")
print(f"  [OK] Good Quality: {len(good_quality)} properties")
print(f"  [WARN] Poor Quality: {len(poor_quality)} properties")
print(f"  [BAD] Category Pages (garbage): {len(category_pages)} properties")
print("\n" + "="*80)

if category_pages:
    print(f"\nCategory Pages Detected ({len(category_pages)}):")
    print("="*80)
    for i, cp in enumerate(category_pages[:10], 1):
        print(f"{i}. Title: '{cp['title']}'")
        print(f"   Price: {cp['price']}, Bedrooms: {cp['bedrooms']}, Location: {cp['location']}")
        print(f"   ID: {cp['id'][:30]}...")
        print()
    
    if len(category_pages) > 10:
        print(f"... and {len(category_pages) - 10} more category pages")

