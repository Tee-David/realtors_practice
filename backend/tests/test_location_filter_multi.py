#!/usr/bin/env python3
"""
Test Multi-Location Filter (Lagos + Ogun)

Tests the location filter's ability to handle multiple Nigerian cities.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.location_filter import LocationFilter


def test_lagos_location_matching():
    """Test Lagos location string matching"""
    filter = LocationFilter(target_locations=['Lagos'], strict_mode=True)

    # Test Lagos areas
    assert filter.is_target_location("Lekki, Lagos") == True
    assert filter.is_target_location("Victoria Island") == True
    assert filter.is_target_location("Ikoyi") == True
    assert filter.is_target_location("VI") == True

    # Test non-Lagos
    assert filter.is_target_location("Abuja") == False
    assert filter.is_target_location("Abeokuta") == False

    print("[PASS] Lagos location string matching")


def test_ogun_location_matching():
    """Test Ogun location string matching"""
    filter = LocationFilter(target_locations=['Ogun'], strict_mode=True)

    # Test Ogun areas
    assert filter.is_target_location("Abeokuta, Ogun State") == True
    assert filter.is_target_location("Mowe") == True
    assert filter.is_target_location("Ibafo") == True
    assert filter.is_target_location("Arepo") == True

    # Test non-Ogun
    assert filter.is_target_location("Lekki") == False
    assert filter.is_target_location("Victoria Island") == False

    print("[PASS] Ogun location string matching")


def test_multi_location_filter():
    """Test filtering with Lagos + Ogun"""
    filter = LocationFilter(target_locations=['Lagos', 'Ogun'], strict_mode=True)

    # Test Lagos locations
    assert filter.is_target_location("Lekki Phase 1") == True
    assert filter.is_target_location("Ajah, Lagos") == True

    # Test Ogun locations
    assert filter.is_target_location("Mowe, Ogun") == True
    assert filter.is_target_location("Abeokuta") == True

    # Test other locations (should fail)
    assert filter.is_target_location("Abuja") == False
    assert filter.is_target_location("Port Harcourt") == False

    print("[PASS] Multi-location (Lagos + Ogun) filtering")


def test_coordinate_bounds():
    """Test coordinate-based filtering"""
    filter = LocationFilter(target_locations=['Lagos', 'Ogun'], strict_mode=True)

    # Lagos coordinates (VI)
    lagos_coords = {'lat': 6.4281, 'lng': 3.4219}
    assert filter.is_target_location("Unknown Location", lagos_coords) == True

    # Ogun coordinates (Abeokuta)
    ogun_coords = {'lat': 7.1475, 'lng': 3.3619}
    assert filter.is_target_location("Unknown Location", ogun_coords) == True

    # Abuja coordinates (should fail)
    abuja_coords = {'lat': 9.0765, 'lng': 7.3986}
    assert filter.is_target_location("Unknown Location", abuja_coords) == False

    print("[PASS] Coordinate-based filtering")


def test_env_variable_parsing():
    """Test RP_TARGET_LOCATIONS environment variable"""
    import os

    # Set env variable
    os.environ['RP_TARGET_LOCATIONS'] = 'Lagos,Ogun,Abuja'

    filter = LocationFilter()

    # Should have 3 target locations
    assert len(filter.target_locations) == 3
    assert 'Lagos' in filter.target_locations
    assert 'Ogun' in filter.target_locations
    assert 'Abuja' in filter.target_locations

    # Clean up
    del os.environ['RP_TARGET_LOCATIONS']

    print("[PASS] Environment variable parsing")


def test_filter_statistics():
    """Test filtering statistics tracking"""
    filter = LocationFilter(target_locations=['Lagos'], strict_mode=True)

    listings = [
        {'location': 'Lekki, Lagos', 'title': 'Property 1'},
        {'location': 'Abeokuta, Ogun', 'title': 'Property 2'},
        {'location': 'Victoria Island', 'title': 'Property 3'},
        {'location': 'Abuja', 'title': 'Property 4'},
    ]

    # filter_listings_by_location returns (filtered_listings, num_filtered)
    filtered, num_filtered = filter.filter_listings_by_location(listings)

    # Should keep only Lagos properties
    assert len(filtered) == 2
    assert filtered[0]['location'] == 'Lekki, Lagos'
    assert filtered[1]['location'] == 'Victoria Island'
    assert num_filtered == 2

    # Check statistics
    stats = filter.get_stats()
    assert stats['matched'] == 2
    # 'filtered' is for coordinate-based filtering
    # 'unknown' is for non-matching locations without coordinates
    assert stats['unknown'] == 2  # Abeokuta and Abuja are unknown (no coords)
    assert stats['checked'] == 4   # All 4 listings were checked

    print("[PASS] Filtering statistics tracking")


def test_case_insensitivity():
    """Test case-insensitive matching"""
    filter = LocationFilter(target_locations=['Lagos', 'Ogun'])

    assert filter.is_target_location("LEKKI") == True
    assert filter.is_target_location("lekki") == True
    assert filter.is_target_location("LeKkI") == True

    assert filter.is_target_location("MOWE") == True
    assert filter.is_target_location("abeokuta") == True

    print("[PASS] Case-insensitive matching")


def run_all_tests():
    """Run all multi-location filter tests"""
    print("\n" + "="*60)
    print("MULTI-LOCATION FILTER TESTS (Lagos + Ogun)")
    print("="*60 + "\n")

    try:
        test_lagos_location_matching()
        test_ogun_location_matching()
        test_multi_location_filter()
        test_coordinate_bounds()
        test_env_variable_parsing()
        test_filter_statistics()
        test_case_insensitivity()

        print("\n" + "="*60)
        print("[PASS] ALL TESTS PASSED (7/7)")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
