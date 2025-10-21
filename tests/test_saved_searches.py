"""
Tests for Saved Searches & Alerts Module

Tests saved search creation, management, and matching.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.saved_searches import SavedSearchManager, get_saved_search_manager


class TestSavedSearchManager(unittest.TestCase):
    """Test SavedSearchManager functionality"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.manager = SavedSearchManager(storage_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test manager initializes correctly"""
        self.assertEqual(len(self.manager.searches), 0)
        self.assertTrue(self.manager.storage_dir.exists())

    def test_create_search(self):
        """Test creating a saved search"""
        criteria = {
            "filters": {
                "bedrooms": {"gte": 3},
                "location": {"contains": "Lekki"},
                "price": {"between": [5000000, 30000000]}
            }
        }

        search_id = self.manager.create_search(
            user_id="user123",
            name="3BR in Lekki under 30M",
            criteria=criteria,
            alert_frequency="daily"
        )

        self.assertIsNotNone(search_id)
        self.assertEqual(len(self.manager.searches), 1)

        # Verify search details
        search = self.manager.get_search(search_id)
        self.assertEqual(search['user_id'], "user123")
        self.assertEqual(search['name'], "3BR in Lekki under 30M")
        self.assertEqual(search['alert_frequency'], "daily")
        self.assertTrue(search['enabled'])

    def test_get_search(self):
        """Test retrieving a search by ID"""
        criteria = {"filters": {"bedrooms": {"gte": 3}}}
        search_id = self.manager.create_search(
            user_id="user123",
            name="Test Search",
            criteria=criteria
        )

        search = self.manager.get_search(search_id)

        self.assertIsNotNone(search)
        self.assertEqual(search['id'], search_id)
        self.assertEqual(search['name'], "Test Search")

        # Non-existent search
        none_search = self.manager.get_search("nonexistent-id")
        self.assertIsNone(none_search)

    def test_list_searches(self):
        """Test listing searches"""
        # Create searches for different users
        self.manager.create_search("user1", "Search 1", {"filters": {}})
        self.manager.create_search("user1", "Search 2", {"filters": {}})
        self.manager.create_search("user2", "Search 3", {"filters": {}})

        # List all searches
        all_searches = self.manager.list_searches()
        self.assertEqual(len(all_searches), 3)

        # List searches for user1
        user1_searches = self.manager.list_searches(user_id="user1")
        self.assertEqual(len(user1_searches), 2)

        # List searches for user2
        user2_searches = self.manager.list_searches(user_id="user2")
        self.assertEqual(len(user2_searches), 1)

    def test_update_search(self):
        """Test updating a saved search"""
        search_id = self.manager.create_search(
            user_id="user123",
            name="Original Name",
            criteria={"filters": {}},
            alert_frequency="daily"
        )

        # Update search
        success = self.manager.update_search(search_id, {
            'name': "Updated Name",
            'alert_frequency': "weekly"
        })

        self.assertTrue(success)

        # Verify updates
        search = self.manager.get_search(search_id)
        self.assertEqual(search['name'], "Updated Name")
        self.assertEqual(search['alert_frequency'], "weekly")

        # Update non-existent search
        success = self.manager.update_search("nonexistent-id", {'name': "Test"})
        self.assertFalse(success)

    def test_delete_search(self):
        """Test deleting a saved search"""
        search_id = self.manager.create_search(
            user_id="user123",
            name="To Delete",
            criteria={"filters": {}}
        )

        # Delete search
        success = self.manager.delete_search(search_id)
        self.assertTrue(success)
        self.assertEqual(len(self.manager.searches), 0)

        # Try to get deleted search
        search = self.manager.get_search(search_id)
        self.assertIsNone(search)

        # Delete non-existent search
        success = self.manager.delete_search("nonexistent-id")
        self.assertFalse(success)

    def test_listing_matches_criteria(self):
        """Test criteria matching logic"""
        listing = {
            'title': '3 Bedroom Flat in Lekki',
            'bedrooms': 3,
            'location': 'Lekki Phase 1',
            'price': 25000000
        }

        # Test gte operator
        filters = {"bedrooms": {"gte": 3}}
        self.assertTrue(self.manager._listing_matches_criteria(listing, filters))

        filters = {"bedrooms": {"gte": 4}}
        self.assertFalse(self.manager._listing_matches_criteria(listing, filters))

        # Test between operator
        filters = {"price": {"between": [20000000, 30000000]}}
        self.assertTrue(self.manager._listing_matches_criteria(listing, filters))

        filters = {"price": {"between": [30000000, 40000000]}}
        self.assertFalse(self.manager._listing_matches_criteria(listing, filters))

        # Test contains operator
        filters = {"location": {"contains": "Lekki"}}
        self.assertTrue(self.manager._listing_matches_criteria(listing, filters))

        filters = {"location": {"contains": "Ikoyi"}}
        self.assertFalse(self.manager._listing_matches_criteria(listing, filters))

        # Test multiple filters (AND logic)
        filters = {
            "bedrooms": {"gte": 3},
            "location": {"contains": "Lekki"},
            "price": {"lte": 30000000}
        }
        self.assertTrue(self.manager._listing_matches_criteria(listing, filters))

    def test_check_for_new_matches(self):
        """Test checking for new matches"""
        # Create a search
        criteria = {
            "filters": {
                "bedrooms": {"gte": 3},
                "location": {"contains": "Lekki"}
            }
        }

        search_id = self.manager.create_search(
            user_id="user123",
            name="3BR in Lekki",
            criteria=criteria
        )

        # Create test listings
        listings = [
            {
                'title': '3BR in Lekki',
                'bedrooms': 3,
                'location': 'Lekki',
                'price': 25000000
            },
            {
                'title': '4BR in Lekki',
                'bedrooms': 4,
                'location': 'Lekki Phase 1',
                'price': 35000000
            },
            {
                'title': '2BR in Ikoyi',
                'bedrooms': 2,
                'location': 'Ikoyi',
                'price': 40000000
            }
        ]

        # Check for matches
        matches = self.manager.check_for_new_matches(search_id, listings)

        # Should match first two listings (3BR and 4BR in Lekki)
        self.assertEqual(len(matches), 2)

        # Verify search metadata updated
        search = self.manager.get_search(search_id)
        self.assertIsNotNone(search['last_checked'])
        self.assertEqual(search['last_match_count'], 2)

    def test_persistence(self):
        """Test searches persist across instances"""
        # Create search in first manager
        search_id = self.manager.create_search(
            user_id="user123",
            name="Test Search",
            criteria={"filters": {}}
        )

        # Create new manager instance - should load searches
        manager2 = SavedSearchManager(storage_dir=self.test_dir)
        self.assertEqual(len(manager2.searches), 1)

        search = manager2.get_search(search_id)
        self.assertIsNotNone(search)
        self.assertEqual(search['name'], "Test Search")

    def test_get_search_stats(self):
        """Test getting search statistics"""
        search_id = self.manager.create_search(
            user_id="user123",
            name="Test Search",
            criteria={"filters": {}}
        )

        stats = self.manager.get_search_stats(search_id)

        self.assertIsNotNone(stats)
        self.assertEqual(stats['id'], search_id)
        self.assertEqual(stats['name'], "Test Search")
        self.assertEqual(stats['last_match_count'], 0)
        self.assertEqual(stats['total_matches_sent'], 0)

        # Non-existent search
        stats = self.manager.get_search_stats("nonexistent-id")
        self.assertIsNone(stats)

    def test_get_saved_search_manager(self):
        """Test factory function"""
        manager = get_saved_search_manager(storage_dir=self.test_dir)
        self.assertIsInstance(manager, SavedSearchManager)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSavedSearchManager)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("SAVED SEARCHES TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All saved searches tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
