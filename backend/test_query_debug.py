"""Debug script to test Firestore queries"""
import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from core.firestore_queries_enterprise import get_all_properties, get_properties_by_listing_type

print("Testing get_all_properties...")
results = get_all_properties(limit=5)
print(f"Results: {len(results)} properties")
if results:
    print(f"First property: {results[0].get('basic_info', {}).get('title', 'No title')}")
    print(f"Price: {results[0].get('financial', {}).get('price', 0)}")
else:
    print("No results returned!")

print("\n\nTesting get_properties_by_listing_type('sale')...")
results2 = get_properties_by_listing_type('sale', limit=5)
print(f"Results: {len(results2)} properties")
if results2:
    print(f"First property: {results2[0].get('basic_info', {}).get('title', 'No title')}")
    print(f"Price: {results2[0].get('financial', {}).get('price', 0)}")
else:
    print("No results returned!")
