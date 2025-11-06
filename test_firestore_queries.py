"""Test Firestore query functions"""
import os
import sys

# Set environment variables
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json'
os.environ['FIRESTORE_ENABLED'] = '1'

from core.firestore_queries import (
    get_cheapest_properties,
    get_newest_listings,
    get_dashboard_stats,
    search_properties,
    get_site_properties,
    get_property_by_hash
)

print("="*60)
print("Testing Firestore Query Functions")
print("="*60)

# Test 1: Get cheapest properties
print("\n1. Testing get_cheapest_properties()...")
cheapest = get_cheapest_properties(limit=5)
print(f"   Found {len(cheapest)} properties")
if cheapest:
    price = cheapest[0].get('price', 0) or 0
    print(f"   Cheapest: {cheapest[0].get('title')} - N{price:,}")

# Test 2: Get newest listings
print("\n2. Testing get_newest_listings()...")
newest = get_newest_listings(limit=5, days_back=30)
print(f"   Found {len(newest)} recent listings")
if newest:
    print(f"   Newest: {newest[0].get('title')} - {newest[0].get('scrape_timestamp')}")

# Test 3: Get site properties
print("\n3. Testing get_site_properties()...")
npc_props = get_site_properties('npc', limit=5)
print(f"   Found {npc_props.get('total', 0)} properties from NPC")
print(f"   Has more: {npc_props.get('has_more', False)}")

# Test 4: Search properties
print("\n4. Testing search_properties()...")
search_result = search_properties(
    filters={'price_max': 100000000},
    sort_by='price',
    limit=5
)
print(f"   Found {len(search_result.get('results', []))} properties under 100M")

# Test 5: Get dashboard stats
print("\n5. Testing get_dashboard_stats()...")
stats = get_dashboard_stats()
if stats:
    print(f"   Total properties: {stats.get('total_properties', 0)}")
    print(f"   Total sites: {stats.get('total_sites', 0)}")
    price_range = stats.get('price_range', {})
    if price_range:
        print(f"   Price range: N{price_range.get('min', 0):,} - N{price_range.get('max', 0):,}")

# Test 6: Get property by hash
print("\n6. Testing get_property_by_hash()...")
if cheapest:
    test_hash = cheapest[0].get('id')
    prop = get_property_by_hash(test_hash)
    if prop:
        print(f"   Retrieved: {prop.get('title')}")
    else:
        print("   Property not found")

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
