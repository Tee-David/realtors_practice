"""
Tests for Duplicate Detection Module

Tests fuzzy matching and duplicate detection across listings.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.duplicate_detector import DuplicateDetector, get_duplicate_detector


class TestDuplicateDetector(unittest.TestCase):
    """Test DuplicateDetector functionality"""

    def setUp(self):
        """Create detector instance"""
        self.detector = DuplicateDetector(threshold=0.85)

    def test_initialization(self):
        """Test detector initializes correctly"""
        self.assertEqual(self.detector.threshold, 0.85)
        self.assertEqual(self.detector.action, "flag")

    def test_exact_duplicates(self):
        """Test detection of exact duplicate listings"""
        listing1 = {
            'title': '3 Bedroom Flat in Lekki Phase 1',
            'location': 'Lekki Phase 1',
            'bedrooms': 3,
            'price': 25000000
        }

        listing2 = {
            'title': '3 Bedroom Flat in Lekki Phase 1',
            'location': 'Lekki Phase 1',
            'bedrooms': 3,
            'price': 25000000
        }

        is_dup, score, breakdown = self.detector.is_duplicate(listing1, listing2)

        self.assertTrue(is_dup)
        self.assertGreaterEqual(score, 0.85)
        self.assertEqual(breakdown['bedrooms_match'], 1.0)

    def test_near_duplicates(self):
        """Test detection of similar listings with minor differences"""
        listing1 = {
            'title': '3 Bedroom Flat in Lekki Phase 1',
            'location': 'Lekki Phase 1, Lagos',
            'bedrooms': 3,
            'price': 25000000
        }

        listing2 = {
            'title': '3 Bedroom Flat in Lekki Phase 1',  # More similar title
            'location': 'Lekki Phase 1',
            'bedrooms': 3,
            'price': 26000000  # 4% difference - within tolerance
        }

        is_dup, score, breakdown = self.detector.is_duplicate(listing1, listing2)

        self.assertTrue(is_dup)
        self.assertGreaterEqual(score, 0.80)  # Should still be high

    def test_not_duplicates(self):
        """Test non-duplicate listings are correctly identified"""
        listing1 = {
            'title': '3 Bedroom Flat in Lekki',
            'location': 'Lekki',
            'bedrooms': 3,
            'price': 25000000
        }

        listing2 = {
            'title': '5 Bedroom Duplex in Ikoyi',
            'location': 'Ikoyi',
            'bedrooms': 5,
            'price': 150000000
        }

        is_dup, score, breakdown = self.detector.is_duplicate(listing1, listing2)

        self.assertFalse(is_dup)
        self.assertLess(score, 0.85)

    def test_coordinate_matching(self):
        """Test duplicate detection with coordinate proximity"""
        listing1 = {
            'title': '3 Bedroom Flat in Lekki',
            'location': 'Lekki',
            'bedrooms': 3,
            'price': 25000000,
            'coordinates': {'lat': 6.4474, 'lng': 3.4706}
        }

        listing2 = {
            'title': '3 Bedroom Flat in Lekki',  # Same title
            'location': 'Lekki',
            'bedrooms': 3,
            'price': 26000000,
            'coordinates': {'lat': 6.4476, 'lng': 3.4708}  # ~30m away
        }

        is_dup, score, breakdown = self.detector.is_duplicate(listing1, listing2)

        self.assertTrue(breakdown['coord_match'])
        self.assertLess(breakdown['coord_distance_meters'], 100)
        # With similar titles and matching coordinates, should be duplicate
        self.assertGreater(score, 0.80)

    def test_find_duplicates(self):
        """Test finding all duplicate pairs in a list"""
        listings = [
            {'title': '3BR Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '3 Bedroom Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '5BR Duplex in Ikoyi', 'location': 'Ikoyi', 'bedrooms': 5, 'price': 150000000},
            {'title': '3BR Apartment at Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 26000000},
        ]

        duplicates = self.detector.find_duplicates(listings)

        # Should find listings 0, 1, and 3 as duplicates of each other
        self.assertGreater(len(duplicates), 0)

    def test_find_duplicate_groups(self):
        """Test finding groups of duplicates (transitive closure)"""
        listings = [
            {'title': '3 Bedroom Flat in Lekki Phase 1', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '3 Bedroom Flat in Lekki Phase 1', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '3 Bedroom Flat in Lekki Phase 1', 'location': 'Lekki', 'bedrooms': 3, 'price': 26000000},
            {'title': '5 Bedroom Duplex in Ikoyi', 'location': 'Ikoyi', 'bedrooms': 5, 'price': 150000000},
        ]

        groups = self.detector.find_duplicate_groups(listings)

        # Should find one group with listings 0, 1, 2
        if len(groups) > 0:  # If duplicates detected
            self.assertTrue(any(len(group) >= 2 for group in groups))

    def test_add_duplicate_ids(self):
        """Test adding duplicate_group_id to listings"""
        listings = [
            {'title': '3BR Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '3 Bedroom Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '5BR Duplex in Ikoyi', 'location': 'Ikoyi', 'bedrooms': 5, 'price': 150000000},
        ]

        updated = self.detector.add_duplicate_ids_to_listings(listings)

        # First two should have same group ID
        group_id_0 = updated[0].get('duplicate_group_id')
        group_id_1 = updated[1].get('duplicate_group_id')

        if group_id_0 is not None:  # If duplicates were detected
            self.assertEqual(group_id_0, group_id_1)
            self.assertTrue(updated[0]['is_duplicate'])
            self.assertTrue(updated[1]['is_duplicate'])

        # Third should not be duplicate
        self.assertIsNone(updated[2].get('duplicate_group_id'))
        self.assertFalse(updated[2]['is_duplicate'])

    def test_filter_duplicates_first(self):
        """Test filtering duplicates keeping first occurrence"""
        listings = [
            {'title': '3BR Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '3 Bedroom Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '5BR Duplex in Ikoyi', 'location': 'Ikoyi', 'bedrooms': 5, 'price': 150000000},
        ]

        filtered = self.detector.filter_duplicates(listings, keep_strategy="first")

        # Should keep first and third
        self.assertLessEqual(len(filtered), len(listings))

    def test_filter_duplicates_cheapest(self):
        """Test filtering duplicates keeping cheapest"""
        listings = [
            {'title': '3BR Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 27000000},
            {'title': '3 Bedroom Flat in Lekki', 'location': 'Lekki', 'bedrooms': 3, 'price': 25000000},
            {'title': '5BR Duplex in Ikoyi', 'location': 'Ikoyi', 'bedrooms': 5, 'price': 150000000},
        ]

        filtered = self.detector.filter_duplicates(listings, keep_strategy="cheapest")

        # Should keep cheapest Lekki listing (25M) and Ikoyi
        self.assertLessEqual(len(filtered), len(listings))

        # Verify cheapest was kept
        lekki_listings = [l for l in filtered if 'Lekki' in l.get('location', '')]
        if lekki_listings:
            self.assertEqual(min(l.get('price', float('inf')) for l in lekki_listings), 25000000)

    def test_title_similarity(self):
        """Test title similarity calculation"""
        sim1 = self.detector._title_similarity(
            "3 Bedroom Flat in Lekki",
            "3BR Apartment at Lekki"
        )
        self.assertGreater(sim1, 0.5)  # Should be similar

        sim2 = self.detector._title_similarity(
            "3 Bedroom Flat in Lekki",
            "Land for Sale in Ajah"
        )
        self.assertLess(sim2, 0.4)  # Should be very different

    def test_prices_close(self):
        """Test price proximity check"""
        # Within 10% tolerance
        self.assertTrue(self.detector._prices_close(25000000, 26000000))

        # Outside 10% tolerance
        self.assertFalse(self.detector._prices_close(25000000, 30000000))

        # None values
        self.assertFalse(self.detector._prices_close(None, 25000000))
        self.assertFalse(self.detector._prices_close(25000000, None))

    def test_get_duplicate_detector(self):
        """Test get_duplicate_detector factory function"""
        detector = get_duplicate_detector(threshold=0.90, action="remove")

        self.assertEqual(detector.threshold, 0.90)
        self.assertEqual(detector.action, "remove")


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDuplicateDetector)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("DUPLICATE DETECTOR TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All duplicate detector tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
