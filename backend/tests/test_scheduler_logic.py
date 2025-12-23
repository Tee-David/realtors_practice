"""
Tests for Scheduler Module (Logic Tests)

Tests scheduler configuration and job management logic.
Does not test actual scheduling (requires APScheduler).

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if APScheduler is available
try:
    import apscheduler
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False


class TestSchedulerLogic(unittest.TestCase):
    """Test scheduler configuration logic"""

    def test_cron_parsing(self):
        """Test cron expression parsing"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            # Test valid cron expression
            cron_params = scheduler._parse_cron("0 8 * * *")

            self.assertEqual(cron_params['minute'], '0')
            self.assertEqual(cron_params['hour'], '8')
            self.assertEqual(cron_params['day'], '*')
            self.assertEqual(cron_params['month'], '*')
            self.assertEqual(cron_params['day_of_week'], '*')

            # Test another cron expression
            cron_params = scheduler._parse_cron("30 14 * * 1-5")

            self.assertEqual(cron_params['minute'], '30')
            self.assertEqual(cron_params['hour'], '14')
            self.assertEqual(cron_params['day_of_week'], '1-5')

    def test_invalid_cron(self):
        """Test invalid cron expression raises error"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            # Invalid - only 3 parts
            with self.assertRaises(ValueError):
                scheduler._parse_cron("0 8 *")

            # Invalid - 6 parts
            with self.assertRaises(ValueError):
                scheduler._parse_cron("0 0 8 * * *")

    def test_scheduler_initialization(self):
        """Test scheduler initializes correctly"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            self.assertIsNotNone(scheduler.scheduler)
            self.assertEqual(len(scheduler.jobs), 0)
            self.assertEqual(len(scheduler.history), 0)

    def test_add_job_cron(self):
        """Test adding a cron-style job"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            # Add cron job
            success = scheduler.add_job(
                job_id="daily_scrape",
                schedule="0 8 * * *",
                sites=["npc", "propertypro"],
                incremental=True,
                enabled=False  # Don't actually schedule it
            )

            self.assertTrue(success)
            self.assertEqual(len(scheduler.jobs), 1)

            job = scheduler.get_job("daily_scrape")
            self.assertIsNotNone(job)
            self.assertEqual(job['schedule'], "0 8 * * *")
            self.assertEqual(job['sites'], ["npc", "propertypro"])
            self.assertTrue(job['incremental'])
            self.assertFalse(job['enabled'])

    def test_add_job_interval(self):
        """Test adding an interval-style job"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            # Add interval job
            success = scheduler.add_job(
                job_id="hourly_scrape",
                schedule="interval:hours:6",
                incremental=True,
                enabled=False
            )

            self.assertTrue(success)

            job = scheduler.get_job("hourly_scrape")
            self.assertEqual(job['schedule'], "interval:hours:6")
            self.assertTrue(job['incremental'])

    def test_duplicate_job_id(self):
        """Test adding job with duplicate ID fails"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            scheduler.add_job("job1", "0 8 * * *", enabled=False)

            # Try to add same job ID again
            success = scheduler.add_job("job1", "0 9 * * *", enabled=False)

            self.assertFalse(success)
            self.assertEqual(len(scheduler.jobs), 1)

    def test_remove_job(self):
        """Test removing a job"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            scheduler.add_job("job1", "0 8 * * *", enabled=False)
            self.assertEqual(len(scheduler.jobs), 1)

            success = scheduler.remove_job("job1")

            self.assertTrue(success)
            self.assertEqual(len(scheduler.jobs), 0)

    def test_update_job(self):
        """Test updating a job"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            scheduler.add_job(
                "job1",
                "0 8 * * *",
                sites=["npc"],
                incremental=False,
                enabled=False
            )

            # Update job
            success = scheduler.update_job("job1", {
                'sites': ["npc", "propertypro"],
                'incremental': True
            })

            self.assertTrue(success)

            job = scheduler.get_job("job1")
            self.assertEqual(job['sites'], ["npc", "propertypro"])
            self.assertTrue(job['incremental'])

    def test_list_jobs(self):
        """Test listing all jobs"""
        if not APSCHEDULER_AVAILABLE:
            self.skipTest("APScheduler not installed")

        from core.scheduler import ScraperScheduler
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = ScraperScheduler(history_file=f"{tmpdir}/history.json")

            scheduler.add_job("job1", "0 8 * * *", enabled=False)
            scheduler.add_job("job2", "interval:hours:6", enabled=False)

            jobs = scheduler.list_jobs()

            self.assertEqual(len(jobs), 2)
            job_ids = [j['id'] for j in jobs]
            self.assertIn("job1", job_ids)
            self.assertIn("job2", job_ids)

    def test_factory_function(self):
        """Test get_scraper_scheduler factory"""
        from core.scheduler import get_scraper_scheduler

        if not APSCHEDULER_AVAILABLE:
            # Should return None if APScheduler not available
            scheduler = get_scraper_scheduler()
            self.assertIsNone(scheduler)
        else:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                scheduler = get_scraper_scheduler(history_file=f"{tmpdir}/history.json")
                self.assertIsNotNone(scheduler)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSchedulerLogic)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("SCHEDULER LOGIC TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n[PASS] All scheduler logic tests passed!")
    elif len(result.skipped) == result.testsRun:
        print("\n[SKIP] All tests skipped (APScheduler not installed)")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
