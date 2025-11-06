"""Test Firestore upload with dummy data"""
import os
import sys

# Set environment variables
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json'
os.environ['FIRESTORE_ENABLED'] = '1'

from core.firestore_direct import FirestoreUploader

# Test initialization
print("="*60)
print("Testing Firestore Initialization")
print("="*60)

uploader = FirestoreUploader()
print(f"Firestore enabled: {uploader.enabled}")
print(f"DB client exists: {uploader.db is not None}")

if not uploader.enabled or uploader.db is None:
    print("\n[FAILED] Firestore initialization FAILED!")
    print("Please check:")
    print("1. Firebase service account file exists")
    print("2. File path is correct")
    print("3. firebase-admin is installed: pip install firebase-admin")
    sys.exit(1)

print("\n[SUCCESS] Firestore initialization SUCCESS!")

# Create test listing
print("\n" + "="*60)
print("Uploading Test Listing to Firestore")
print("="*60)

test_listing = {
    'title': 'Test Property - Lagos Island',
    'price': 45000000,
    'location': 'Victoria Island, Lagos',
    'property_type': '3 Bedroom Flat',
    'bedrooms': 3,
    'bathrooms': 3,
    'listing_url': 'https://test.com/property/123',
    'source': 'test_site',
    'scrape_timestamp': '2025-11-06T08:00:00',
    'hash': 'test_hash_12345',
    'description': 'This is a test property to verify Firestore upload is working correctly.'
}

result = uploader.upload_listings_batch('test_site', [test_listing])

print(f"\nUpload Results:")
print(f"  Total: {result['total']}")
print(f"  Uploaded: {result['uploaded']}")
print(f"  Errors: {result['errors']}")
print(f"  Skipped: {result['skipped']}")

if result['uploaded'] > 0:
    print("\n[SUCCESS] Test listing uploaded to Firestore")
    print("   Check your Firebase Console: https://console.firebase.google.com/")
    print("   -> Firestore Database -> properties collection")
else:
    print("\n[FAILED] No listings uploaded")
    print("   Check logs above for errors")
