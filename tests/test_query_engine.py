#!/usr/bin/env python3
"""
Test Query Engine

Tests the advanced property query engine's filtering, sorting, and search capabilities.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query_engine import PropertyQuery


def create_test_data():
    """Create sample property data for testing"""
    data = {
        'title': [
            'Luxury 4 Bedroom Duplex',
            '3 Bedroom Flat',
            '5 Bedroom Detached House',
            '2 Bedroom Apartment',
            'Land for Sale',
        ],
        'price': [50000000, 25000000, 100000000, 15000000, 30000000],
        'location': ['Lekki', 'Ikoyi', 'Victoria Island', 'Ajah', 'Lekki'],
        'bedrooms': [4, 3, 5, 2, 0],
        'bathrooms': [4, 3, 6, 2, 0],
        'property_type': ['Duplex', 'Flat', 'Detached', 'Flat', 'Land'],
        'source': ['npc', 'propertypro', 'npc', 'jiji', 'npc'],
    }
    return pd.DataFrame(data)


def test_price_filtering():
    """Test price range filtering"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Filter by price range
    results = query.filter(price_min=20000000, price_max=60000000).execute()

    assert len(results) == 3  # Should get 3 properties in this range
    for prop in results:
        assert 20000000 <= prop['price'] <= 60000000

    print("[PASS] Price range filtering")


def test_bedroom_filtering():
    """Test bedroom filtering"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Exact bedrooms
    results = query.filter(bedrooms=3).execute()
    assert len(results) == 1
    assert results[0]['bedrooms'] == 3

    print("[PASS] Exact bedroom filtering")


def test_bedroom_range_filtering():
    """Test bedroom range filtering"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Bedroom range
    results = query.filter(bedrooms_min=3, bedrooms_max=4).execute()
    assert len(results) == 2  # 3 bed and 4 bed properties

    print("[PASS] Bedroom range filtering")


def test_location_filtering():
    """Test location filtering"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Location search (partial match)
    results = query.filter(location='Lekki').execute()
    assert len(results) == 2  # 2 properties in Lekki

    print("[PASS] Location filtering")


def test_property_type_filtering():
    """Test property type filtering"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Property type search
    results = query.filter(property_type='Flat').execute()
    assert len(results) == 2  # 2 flats

    print("[PASS] Property type filtering")


def test_text_search():
    """Test text search across multiple fields"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Search for "Bedroom"
    results = query.search('Luxury').execute()
    assert len(results) == 1
    assert 'Luxury' in results[0]['title']

    print("[PASS] Text search")


def test_sorting():
    """Test sorting by price"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Sort by price ascending
    results = query.sort_by('price', ascending=True).execute()
    assert results[0]['price'] == 15000000  # Cheapest first
    assert results[-1]['price'] == 100000000  # Most expensive last

    print("[PASS] Sorting (ascending)")


def test_sorting_descending():
    """Test sorting descending"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Sort by price descending
    results = query.sort_by('price', ascending=False).execute()
    assert results[0]['price'] == 100000000  # Most expensive first
    assert results[-1]['price'] == 15000000  # Cheapest last

    print("[PASS] Sorting (descending)")


def test_pagination():
    """Test limit and offset"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Limit results
    results = query.limit(2).execute()
    assert len(results) == 2

    # Limit with offset
    query2 = PropertyQuery(df)
    results2 = query2.limit(2, offset=2).execute()
    assert len(results2) == 2
    # Results should be different
    assert results[0]['title'] != results2[0]['title']

    print("[PASS] Pagination (limit + offset)")


def test_combined_filters():
    """Test multiple filters combined"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Price + bedrooms + location
    results = query.filter(
        price_max=60000000,
        bedrooms_min=3,
        location='Lekki'
    ).execute()

    # Should only get 1 property: 4 bed in Lekki
    assert len(results) == 1
    assert results[0]['location'] == 'Lekki'
    assert results[0]['bedrooms'] >= 3

    print("[PASS] Combined filters")


def test_count():
    """Test count without executing"""
    df = create_test_data()
    query = PropertyQuery(df)

    count = query.filter(price_max=50000000).count()
    assert count == 4  # 4 properties under 50M

    print("[PASS] Count without execute")


def test_summary_statistics():
    """Test summary statistics"""
    df = create_test_data()
    query = PropertyQuery(df)

    summary = query.get_summary()

    assert summary['total_results'] == 5
    assert 'price_stats' in summary
    assert summary['price_stats']['min'] == 15000000
    assert summary['price_stats']['max'] == 100000000

    print("[PASS] Summary statistics")


def test_reset():
    """Test query reset"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Apply filter
    query.filter(price_max=30000000)
    assert query.count() < 5

    # Reset
    query.reset()
    assert query.count() == 5  # Back to original

    print("[PASS] Query reset")


def test_chaining():
    """Test method chaining"""
    df = create_test_data()
    query = PropertyQuery(df)

    # Chain multiple operations
    results = (query
               .filter(price_max=60000000)
               .filter(bedrooms_min=2)
               .sort_by('price')
               .limit(3)
               .execute())

    assert len(results) <= 3
    # Should be sorted by price
    if len(results) > 1:
        assert results[0]['price'] <= results[1]['price']

    print("[PASS] Method chaining")


def run_all_tests():
    """Run all query engine tests"""
    print("\n" + "="*60)
    print("QUERY ENGINE TESTS")
    print("="*60 + "\n")

    try:
        test_price_filtering()
        test_bedroom_filtering()
        test_bedroom_range_filtering()
        test_location_filtering()
        test_property_type_filtering()
        test_text_search()
        test_sorting()
        test_sorting_descending()
        test_pagination()
        test_combined_filters()
        test_count()
        test_summary_statistics()
        test_reset()
        test_chaining()

        print("\n" + "="*60)
        print("[PASS] ALL TESTS PASSED (14/14)")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
