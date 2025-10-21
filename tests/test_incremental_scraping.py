"""
Tests for Incremental Scraping Module

Tests the incremental scraper's ability to track seen URLs
and stop when encountering consecutive known listings.

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

from core.incremental_scraper import IncrementalScraper, get_incremental_scraper


class TestIncrementalScraper(unittest.TestCase):
    """Test IncrementalScraper functionality"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.scraper = IncrementalScraper('test_site', seen_urls_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test scraper initializes correctly"""
        self.assertEqual(self.scraper.site_key, 'test_site')
        self.assertEqual(len(self.scraper.seen_urls), 0)
        self.assertEqual(self.scraper.consecutive_seen, 0)
        self.assertEqual(self.scraper.stop_threshold, 10)

    def test_mark_url_seen(self):
        """Test marking URLs as seen"""
        url = "https://example.com/property1"

        # First time - should be new
        is_new = self.scraper.mark_url_seen(url)
        self.assertTrue(is_new)
        self.assertEqual(len(self.scraper.seen_urls), 1)

        # Second time - should not be new
        is_new = self.scraper.mark_url_seen(url)
        self.assertFalse(is_new)
        self.assertEqual(len(self.scraper.seen_urls), 1)

    def test_is_url_seen(self):
        """Test checking if URL is seen"""
        url = "https://example.com/property1"

        # Before marking
        self.assertFalse(self.scraper.is_url_seen(url))

        # After marking
        self.scraper.mark_url_seen(url)
        self.assertTrue(self.scraper.is_url_seen(url))

    def test_should_continue_with_new_urls(self):
        """Test scraper continues when encountering new URLs"""
        urls = [
            "https://example.com/property1",
            "https://example.com/property2",
            "https://example.com/property3"
        ]

        for url in urls:
            should_continue = self.scraper.should_continue_scraping(url)
            self.assertTrue(should_continue)
            self.assertEqual(self.scraper.consecutive_seen, 0)

        self.assertEqual(len(self.scraper.seen_urls), 3)

    def test_should_stop_after_threshold(self):
        """Test scraper stops after consecutive seen threshold"""
        # Mark 5 URLs as seen
        base_urls = [f"https://example.com/old{i}" for i in range(5)]
        for url in base_urls:
            self.scraper.mark_url_seen(url)

        # Now encounter them again - should stop after 10 consecutive
        for i, url in enumerate(base_urls * 3):  # 15 total
            should_continue = self.scraper.should_continue_scraping(url)

            if i < 9:  # First 10 should continue
                self.assertTrue(should_continue)
            else:  # After 10, should stop
                self.assertFalse(should_continue)
                break

    def test_consecutive_counter_resets(self):
        """Test consecutive counter resets when new URL found"""
        # Mark some URLs as seen
        old_urls = [f"https://example.com/old{i}" for i in range(5)]
        for url in old_urls:
            self.scraper.mark_url_seen(url)

        # Encounter 5 old URLs (consecutive = 5)
        for url in old_urls:
            self.scraper.should_continue_scraping(url)

        self.assertEqual(self.scraper.consecutive_seen, 5)

        # Encounter a new URL - should reset counter
        new_url = "https://example.com/new1"
        self.scraper.should_continue_scraping(new_url)

        self.assertEqual(self.scraper.consecutive_seen, 0)

    def test_mark_urls_seen_batch(self):
        """Test batch marking URLs as seen"""
        urls = [f"https://example.com/property{i}" for i in range(10)]

        self.scraper.mark_urls_seen_batch(urls)

        self.assertEqual(len(self.scraper.seen_urls), 10)
        self.assertEqual(self.scraper.new_urls_count, 10)

        # Mark same batch again - should not increase count
        self.scraper.mark_urls_seen_batch(urls)
        self.assertEqual(len(self.scraper.seen_urls), 10)
        self.assertEqual(self.scraper.new_urls_count, 10)

    def test_persistence(self):
        """Test seen URLs persist across instances"""
        # Mark URLs in first scraper
        urls = [f"https://example.com/property{i}" for i in range(5)]
        for url in urls:
            self.scraper.mark_url_seen(url)

        self.scraper.save()

        # Create new scraper instance - should load seen URLs
        scraper2 = IncrementalScraper('test_site', seen_urls_dir=self.test_dir)
        self.assertEqual(len(scraper2.seen_urls), 5)

        for url in urls:
            self.assertTrue(scraper2.is_url_seen(url))

    def test_get_stats(self):
        """Test getting scraper statistics"""
        # Add some URLs
        new_urls = [f"https://example.com/new{i}" for i in range(3)]
        for url in new_urls:
            self.scraper.should_continue_scraping(url)

        # Mark some as seen first, then encounter again
        old_urls = [f"https://example.com/old{i}" for i in range(2)]
        for url in old_urls:
            self.scraper.mark_url_seen(url)

        for url in old_urls:
            self.scraper.should_continue_scraping(url)

        stats = self.scraper.get_stats()

        self.assertEqual(stats['site_key'], 'test_site')
        self.assertEqual(stats['total_seen_urls'], 5)
        self.assertEqual(stats['new_urls_this_run'], 5)
        self.assertEqual(stats['consecutive_seen'], 2)
        self.assertTrue(stats['should_continue'])

    def test_clear_seen_urls(self):
        """Test clearing all seen URLs"""
        # Add some URLs
        urls = [f"https://example.com/property{i}" for i in range(5)]
        self.scraper.mark_urls_seen_batch(urls)

        self.assertEqual(len(self.scraper.seen_urls), 5)

        # Clear all
        self.scraper.clear_seen_urls()

        self.assertEqual(len(self.scraper.seen_urls), 0)
        self.assertEqual(self.scraper.consecutive_seen, 0)
        self.assertEqual(self.scraper.new_urls_count, 0)

    def test_singleton_pattern(self):
        """Test get_incremental_scraper singleton"""
        scraper1 = get_incremental_scraper('site1')
        scraper2 = get_incremental_scraper('site1')

        # Should be same instance
        self.assertIs(scraper1, scraper2)

        # Different site should be different instance
        scraper3 = get_incremental_scraper('site2')
        self.assertIsNot(scraper1, scraper3)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIncrementalScraper)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("INCREMENTAL SCRAPER TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All incremental scraper tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
