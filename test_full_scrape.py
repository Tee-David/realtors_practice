"""
Test full scrape with Firestore upload - Enterprise Schema Validation
"""
import subprocess
import sys

print("=" * 70)
print("FULL SCRAPE TEST - Enterprise Firestore v3.1.1")
print("=" * 70)
print()

# Step 1: Enable only 3 sites for quick test
print("Step 1: Enabling test sites...")
sites_to_enable = ['cwlagos', 'npc', 'jiji']
result = subprocess.run(
    ['python', 'scripts/enable_sites.py'] + sites_to_enable,
    capture_output=True,
    text=True
)
print(result.stdout)
if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
    sys.exit(1)

print()
print("=" * 70)
print("Step 2: Running scraper with Firestore upload...")
print("=" * 70)
print()

# Step 2: Run main.py with Firestore enabled
result = subprocess.run(
    ['python', 'main.py'],
    env={
        'FIREBASE_SERVICE_ACCOUNT': 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json',
        'FIRESTORE_ENABLED': '1',
        'RP_GEOCODE': '0',
        'RP_PAGE_CAP': '2',
        'RP_HEADLESS': '1',
        **dict(subprocess.os.environ)
    },
    capture_output=False,
    text=True
)

if result.returncode != 0:
    print(f"ERROR: Scraper failed with code {result.returncode}")
    sys.exit(1)

print()
print("=" * 70)
print("Step 3: Verifying Firestore data...")
print("=" * 70)
print()

# Step 3: Verify data in Firestore
verify_script = """
from core.firestore_enterprise import _get_firestore_client

db = _get_firestore_client()
if not db:
    print("ERROR: Could not connect to Firestore")
    exit(1)

# Get all properties
properties_ref = db.collection('properties')
docs = list(properties_ref.limit(10).stream())

print(f"✅ Found {len(docs)} properties in Firestore")
print()

if docs:
    # Check first document structure
    first_doc = docs[0]
    data = first_doc.to_dict()

    print("Checking enterprise schema structure...")
    required_categories = [
        'basic_info', 'property_details', 'financial',
        'location', 'amenities', 'media', 'agent_info',
        'metadata', 'tags'
    ]

    missing = []
    present = []
    for cat in required_categories:
        if cat in data:
            present.append(cat)
        else:
            missing.append(cat)

    print(f"✅ Categories present: {len(present)}/9")
    for cat in present:
        print(f"   - {cat}")

    if missing:
        print(f"⚠️ Missing categories: {missing}")

    print()
    print("Sample data from first property:")
    print(f"  Title: {data.get('basic_info', {}).get('title', 'N/A')}")
    print(f"  Price: ₦{data.get('financial', {}).get('price', 0):,}")
    print(f"  Location: {data.get('location', {}).get('location_text', 'N/A')}")
    print(f"  Bedrooms: {data.get('property_details', {}).get('bedrooms', 0)}")
    print(f"  Listing Type: {data.get('basic_info', {}).get('listing_type', 'N/A')}")
    print(f"  Furnishing: {data.get('property_details', {}).get('furnishing', 'N/A')}")
    print(f"  Premium: {data.get('tags', {}).get('premium', False)}")
    print(f"  Hot Deal: {data.get('tags', {}).get('hot_deal', False)}")

    print()
    print("✅ Enterprise schema validation PASSED!")
else:
    print("⚠️ No documents found in Firestore")
"""

result = subprocess.run(['python', '-c', verify_script], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
