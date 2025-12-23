"""
Quick test of Firestore API endpoints to verify data retrieval.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import query functions
from core.firestore_queries_enterprise import (
    get_dashboard_stats,
    get_cheapest_properties,
    get_properties_by_listing_type,
    get_premium_properties,
    get_hot_deals,
    get_properties_by_area,
    get_newest_listings,
    get_property_by_hash
)

def test_all_endpoints():
    """Test all major Firestore query endpoints."""

    print("=" * 60)
    print("FIRESTORE API ENDPOINTS TEST")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Dashboard Stats
    print("\n1. Testing /api/firestore/dashboard...")
    tests_total += 1
    stats = get_dashboard_stats()
    if stats and stats.get('total_properties', 0) > 0:
        print(f"   [OK] {stats['total_properties']} properties")
        print(f"   [OK] {stats.get('total_for_sale', 0)} for sale")
        print(f"   [OK] {stats.get('total_for_rent', 0)} for rent")
        tests_passed += 1
    else:
        print("   [FAIL] No stats returned")

    # Test 2: Cheapest Properties
    print("\n2. Testing /api/firestore/top-deals...")
    tests_total += 1
    cheap = get_cheapest_properties(limit=5)
    if cheap and len(cheap) > 0:
        print(f"   [OK] {len(cheap)} results")
        if cheap[0].get('financial', {}).get('price'):
            print(f"   [OK] Cheapest: {cheap[0]['financial']['price']:,.0f} NGN")
        tests_passed += 1
    else:
        print("   [FAIL] No results")

    # Test 3: For Sale Properties
    print("\n3. Testing /api/firestore/for-sale...")
    tests_total += 1
    for_sale = get_properties_by_listing_type('sale', limit=5)
    if for_sale and len(for_sale) > 0:
        print(f"   [OK] {len(for_sale)} results")
        tests_passed += 1
    else:
        print("   [FAIL] No results")

    # Test 4: For Rent Properties
    print("\n4. Testing /api/firestore/for-rent...")
    tests_total += 1
    for_rent = get_properties_by_listing_type('rent', limit=5)
    if for_rent is not None:  # Can be empty list
        print(f"   [OK] {len(for_rent)} results")
        tests_passed += 1
    else:
        print("   [FAIL] Query failed")

    # Test 5: Premium Properties
    print("\n5. Testing /api/firestore/premium...")
    tests_total += 1
    premium = get_premium_properties(limit=5)
    if premium is not None:
        print(f"   [OK] {len(premium)} results")
        tests_passed += 1
    else:
        print("   [FAIL] Query failed")

    # Test 6: Hot Deals
    print("\n6. Testing /api/firestore/properties/hot-deals...")
    tests_total += 1
    hot = get_hot_deals(limit=5)
    if hot is not None:
        print(f"   [OK] {len(hot)} results")
        tests_passed += 1
    else:
        print("   [FAIL] Query failed")

    # Test 7: By Area (Lekki)
    print("\n7. Testing /api/firestore/properties/by-area/Lekki...")
    tests_total += 1
    lekki = get_properties_by_area('Lekki', limit=5)
    if lekki is not None:
        print(f"   [OK] {len(lekki)} results")
        tests_passed += 1
    else:
        print("   [FAIL] Query failed")

    # Test 8: Newest Listings
    print("\n8. Testing /api/firestore/newest...")
    tests_total += 1
    newest = get_newest_listings(limit=5)
    if newest is not None:
        print(f"   [OK] {len(newest)} results")
        tests_passed += 1
    else:
        print("   [FAIL] Query failed")

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {tests_passed}/{tests_total} endpoints passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print("\n[SUCCESS] All Firestore endpoints working correctly!")
        print("Your frontend can now retrieve data from Firestore.")
        return True
    else:
        print(f"\n[WARNING] {tests_total - tests_passed} endpoints failed")
        return False


if __name__ == '__main__':
    import sys
    success = test_all_endpoints()
    sys.exit(0 if success else 1)
