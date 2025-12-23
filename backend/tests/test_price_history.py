"""
Tests for Price History Tracking Module

Tests price tracking, change detection, and trend analysis.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import tempfile
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.price_history import PriceHistoryTracker, get_price_history_tracker


class TestPriceHistoryTracker(unittest.TestCase):
    """Test PriceHistoryTracker functionality"""

    def setUp(self):
        """Create temporary history file"""
        self.test_dir = tempfile.mkdtemp()
        self.history_file = Path(self.test_dir) / "price_history.json"
        self.tracker = PriceHistoryTracker(history_file=str(self.history_file))

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test tracker initializes correctly"""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(len(self.tracker.history), 0)

    def test_track_new_listing(self):
        """Test tracking a new listing"""
        listing = {
            'hash': 'abc123',
            'title': '3 Bedroom Flat',
            'location': 'Lekki',
            'price': 25000000,
            'source': 'npc'
        }

        result = self.tracker.track_listing(listing)

        self.assertIsNotNone(result)
        self.assertTrue(result['is_new'])
        self.assertFalse(result['price_changed'])
        self.assertEqual(result['current_price'], 25000000)

    def test_track_price_change(self):
        """Test detecting price changes"""
        listing = {
            'hash': 'abc123',
            'title': '3 Bedroom Flat',
            'location': 'Lekki',
            'price': 25000000,
            'source': 'npc'
        }

        # First tracking
        self.tracker.track_listing(listing)

        # Update price
        listing['price'] = 22000000
        result = self.tracker.track_listing(listing)

        self.assertTrue(result['price_changed'])
        self.assertFalse(result['is_new'])
        self.assertEqual(result['old_price'], 25000000)
        self.assertEqual(result['new_price'], 22000000)
        self.assertEqual(result['price_diff'], -3000000)
        self.assertTrue(result['is_drop'])
        self.assertLess(result['price_diff_pct'], 0)

    def test_track_unchanged_price(self):
        """Test tracking listing with unchanged price"""
        listing = {
            'hash': 'abc123',
            'title': '3 Bedroom Flat',
            'location': 'Lekki',
            'price': 25000000,
            'source': 'npc'
        }

        # Track twice with same price
        self.tracker.track_listing(listing)
        result = self.tracker.track_listing(listing)

        self.assertFalse(result['price_changed'])
        self.assertFalse(result['is_new'])
        self.assertEqual(result['current_price'], 25000000)

    def test_get_price_history(self):
        """Test retrieving price history"""
        listing = {
            'hash': 'abc123',
            'title': '3 Bedroom Flat',
            'location': 'Lekki',
            'price': 25000000,
            'source': 'npc'
        }

        # Track with different prices
        self.tracker.track_listing(listing)

        listing['price'] = 23000000
        self.tracker.track_listing(listing)

        listing['price'] = 22000000
        result = self.tracker.track_listing(listing)

        # Get history
        property_id = result['property_id']
        history = self.tracker.get_price_history(property_id)

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['price'], 25000000)
        self.assertEqual(history[1]['price'], 23000000)
        self.assertEqual(history[2]['price'], 22000000)

    def test_get_price_drops(self):
        """Test finding price drops"""
        # Create listings with price drops
        listing1 = {
            'hash': 'abc123',
            'title': 'Property 1',
            'location': 'Lekki',
            'price': 30000000,
            'source': 'npc'
        }

        listing2 = {
            'hash': 'def456',
            'title': 'Property 2',
            'location': 'Ikoyi',
            'price': 50000000,
            'source': 'propertypro'
        }

        # Track initial prices
        self.tracker.track_listing(listing1)
        self.tracker.track_listing(listing2)

        # Drop prices
        listing1['price'] = 25000000  # 16.7% drop
        listing2['price'] = 42000000  # 16% drop

        self.tracker.track_listing(listing1)
        self.tracker.track_listing(listing2)

        # Get price drops
        drops = self.tracker.get_price_drops(min_drop_pct=15.0)

        self.assertEqual(len(drops), 2)
        self.assertGreater(drops[0]['price_drop_pct'], 15.0)

    def test_get_stale_listings(self):
        """Test finding stale listings (mocked with manual history)"""
        # Manually create old entry
        old_timestamp = (datetime.now() - timedelta(days=100)).isoformat()

        self.tracker.history['stale_property'] = [{
            'price': 25000000,
            'timestamp': old_timestamp,
            'title': 'Old Listing',
            'location': 'Lekki'
        }]

        stale = self.tracker.get_stale_listings(min_days=90)

        self.assertEqual(len(stale), 1)
        self.assertGreater(stale[0]['days_listed'], 90)

    def test_get_market_trends(self):
        """Test market trend analysis"""
        # Create some price changes
        for i in range(5):
            listing = {
                'hash': f'prop{i}',
                'title': f'Property {i}',
                'location': 'Lekki',
                'price': 25000000,
                'source': 'npc'
            }
            self.tracker.track_listing(listing)

            # Change price (some up, some down)
            if i % 2 == 0:
                listing['price'] = 27000000  # Increase
            else:
                listing['price'] = 23000000  # Decrease

            self.tracker.track_listing(listing)

        trends = self.tracker.get_market_trends(days=30)

        self.assertIn('trend', trends)
        self.assertIn('total_price_changes', trends)
        self.assertIn('price_increases', trends)
        self.assertIn('price_decreases', trends)

    def test_track_batch(self):
        """Test batch tracking"""
        listings = [
            {'hash': 'prop1', 'title': 'P1', 'price': 25000000, 'location': 'Lekki'},
            {'hash': 'prop2', 'title': 'P2', 'price': 30000000, 'location': 'Ikoyi'},
            {'hash': 'prop3', 'title': 'P3', 'price': 35000000, 'location': 'VI'}
        ]

        result = self.tracker.track_batch(listings)

        self.assertEqual(result['total_tracked'], 3)
        self.assertEqual(result['new_properties'], 3)
        self.assertEqual(result['price_changed'], 0)

    def test_property_id_generation(self):
        """Test property ID generation from different sources"""
        # Hash-based
        listing1 = {'hash': 'abc123', 'title': 'Test', 'price': 25000000}
        id1 = self.tracker._get_property_id(listing1)
        self.assertTrue(id1.startswith('hash_'))

        # URL-based
        listing2 = {'listing_url': 'https://example.com/prop1', 'title': 'Test', 'price': 25000000}
        id2 = self.tracker._get_property_id(listing2)
        self.assertTrue(id2.startswith('url_'))

        # Title-based fallback
        listing3 = {'title': 'Test Property', 'location': 'Lekki', 'price': 25000000}
        id3 = self.tracker._get_property_id(listing3)
        self.assertTrue(id3.startswith('title_'))

    def test_factory_function(self):
        """Test get_price_history_tracker factory"""
        tracker = get_price_history_tracker(history_file=str(self.history_file))
        self.assertIsInstance(tracker, PriceHistoryTracker)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPriceHistoryTracker)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("PRICE HISTORY TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All price history tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
