"""
Tests for Health Monitoring Dashboard Module

Tests health metrics calculation and monitoring.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'api'))

from helpers.health_monitor import HealthMonitor, get_health_monitor


class TestHealthMonitor(unittest.TestCase):
    """Test HealthMonitor functionality"""

    def setUp(self):
        """Create temporary metadata file"""
        self.test_dir = tempfile.mkdtemp()
        self.metadata_file = Path(self.test_dir) / "site_metadata.json"

        # Create mock metadata
        now = datetime.now()
        recent = (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        warning_time = (now - timedelta(hours=30)).strftime('%Y-%m-%d %H:%M:%S')  # 30 hours ago (warning)
        critical_time = (now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')  # 5 days ago (critical)

        self.mock_metadata = {
            'healthy_site': {
                'last_scrape': recent,
                'last_successful_scrape': recent,
                'last_count': 500,
                'total_scrapes': 10
            },
            'warning_site': {
                'last_scrape': warning_time,
                'last_successful_scrape': warning_time,
                'last_count': 100,
                'total_scrapes': 5
            },
            'critical_site': {
                'last_scrape': critical_time,
                'last_successful_scrape': None,
                'last_count': 0,
                'total_scrapes': 3
            }
        }

        # Write metadata to file
        with open(self.metadata_file, 'w') as f:
            json.dump(self.mock_metadata, f)

        self.monitor = HealthMonitor(metadata_file=str(self.metadata_file))

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test monitor initializes correctly"""
        self.assertIsNotNone(self.monitor)
        self.assertTrue(self.monitor.metadata_file.exists())

    def test_get_site_health_healthy(self):
        """Test health check for healthy site"""
        health = self.monitor.get_site_health('healthy_site')

        self.assertEqual(health['site'], 'healthy_site')
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['last_listing_count'], 500)
        self.assertEqual(health['total_scrapes'], 10)
        self.assertEqual(len(health['issues']), 0)
        self.assertGreater(health['health_score'], 0.8)

    def test_get_site_health_warning(self):
        """Test health check for warning site"""
        health = self.monitor.get_site_health('warning_site')

        self.assertEqual(health['site'], 'warning_site')
        self.assertEqual(health['status'], 'warning')
        self.assertGreater(len(health['issues']), 0)
        self.assertLess(health['health_score'], 0.8)

    def test_get_site_health_critical(self):
        """Test health check for critical site"""
        health = self.monitor.get_site_health('critical_site')

        self.assertEqual(health['site'], 'critical_site')
        self.assertEqual(health['status'], 'critical')
        self.assertGreater(len(health['issues']), 0)
        self.assertLess(health['health_score'], 0.5)

    def test_get_site_health_unknown(self):
        """Test health check for non-existent site"""
        health = self.monitor.get_site_health('nonexistent_site')

        self.assertEqual(health['site'], 'nonexistent_site')
        self.assertEqual(health['status'], 'unknown')

    def test_get_overall_health(self):
        """Test overall health summary"""
        overall = self.monitor.get_overall_health()

        self.assertEqual(overall['total_sites'], 3)
        self.assertEqual(overall['healthy_sites'], 1)
        self.assertEqual(overall['warning_sites'], 1)
        self.assertEqual(overall['critical_sites'], 1)

        # Check percentages
        self.assertAlmostEqual(overall['health_percentages']['healthy'], 33.3, places=1)
        self.assertAlmostEqual(overall['health_percentages']['warning'], 33.3, places=1)
        self.assertAlmostEqual(overall['health_percentages']['critical'], 33.3, places=1)

        # Check listings
        self.assertEqual(overall['total_listings'], 600)  # 500 + 100 + 0
        self.assertEqual(overall['avg_listings_per_site'], 200.0)

    def test_get_sites_by_status(self):
        """Test filtering sites by status"""
        healthy = self.monitor.get_sites_by_status('healthy')
        warning = self.monitor.get_sites_by_status('warning')
        critical = self.monitor.get_sites_by_status('critical')

        self.assertEqual(len(healthy), 1)
        self.assertEqual(len(warning), 1)
        self.assertEqual(len(critical), 1)

        self.assertEqual(healthy[0]['site'], 'healthy_site')
        self.assertEqual(warning[0]['site'], 'warning_site')
        self.assertEqual(critical[0]['site'], 'critical_site')

    def test_get_top_performers(self):
        """Test getting top performing sites"""
        top = self.monitor.get_top_performers(limit=2)

        self.assertEqual(len(top), 2)

        # Should be sorted by last_count (descending)
        self.assertEqual(top[0]['site'], 'healthy_site')
        self.assertEqual(top[0]['last_count'], 500)

        self.assertEqual(top[1]['site'], 'warning_site')
        self.assertEqual(top[1]['last_count'], 100)

    def test_get_alerts(self):
        """Test getting active alerts"""
        alerts = self.monitor.get_alerts()

        # Should have alerts for warning_site and critical_site
        self.assertGreaterEqual(len(alerts), 2)

        # Check alert structure
        self.assertIn('site', alerts[0])
        self.assertIn('severity', alerts[0])
        self.assertIn('message', alerts[0])
        self.assertIn('health_score', alerts[0])

        # Critical alerts should be first
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        self.assertGreater(len(critical_alerts), 0)

    def test_get_trend_analysis(self):
        """Test trend analysis"""
        trends = self.monitor.get_trend_analysis(days=7)

        self.assertEqual(trends['period_days'], 7)
        self.assertEqual(trends['total_listings_current'], 600)
        self.assertGreater(trends['avg_listings_per_day'], 0)

    def test_health_score_calculation(self):
        """Test health score calculation"""
        # Healthy with no issues
        score1 = self.monitor._calculate_health_score('healthy', [])
        self.assertEqual(score1, 1.0)

        # Warning with 1 issue
        score2 = self.monitor._calculate_health_score('warning', ['Issue 1'])
        self.assertLess(score2, 1.0)
        self.assertGreater(score2, 0.0)

        # Critical with multiple issues
        score3 = self.monitor._calculate_health_score('critical', ['Issue 1', 'Issue 2'])
        self.assertLess(score3, score2)

    def test_factory_function(self):
        """Test get_health_monitor factory"""
        monitor = get_health_monitor(metadata_file=str(self.metadata_file))

        self.assertIsInstance(monitor, HealthMonitor)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHealthMonitor)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("HEALTH MONITOR TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All health monitor tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
