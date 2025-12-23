#!/usr/bin/env python3
"""
Test Parallel Scraping Module

Tests parallel site scraping with worker management, error handling, and performance.
"""

import sys
import os
import time
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parallel_scraper import (
    calculate_workers,
    scrape_sites_parallel,
    get_max_workers_from_env
)


def test_worker_calculation():
    """Test worker count calculation based on site count"""
    # Small site count
    assert calculate_workers(3) == 2
    assert calculate_workers(5) == 2

    # Medium site count
    assert calculate_workers(10) == 3
    assert calculate_workers(15) == 3

    # Large site count
    assert calculate_workers(20) == 4
    assert calculate_workers(50) == 4

    # Manual override
    assert calculate_workers(10, max_workers=5) == 5
    assert calculate_workers(3, max_workers=1) == 1

    print("[PASS] Worker calculation")


def test_env_variable_parsing():
    """Test RP_SITE_WORKERS environment variable parsing"""
    # Save original
    original = os.environ.get("RP_SITE_WORKERS")

    try:
        # Auto-detect
        os.environ["RP_SITE_WORKERS"] = "auto"
        assert get_max_workers_from_env() is None

        # Explicit values
        os.environ["RP_SITE_WORKERS"] = "2"
        assert get_max_workers_from_env() == 2

        os.environ["RP_SITE_WORKERS"] = "5"
        assert get_max_workers_from_env() == 5

        # Invalid values - should return None
        os.environ["RP_SITE_WORKERS"] = "invalid"
        assert get_max_workers_from_env() is None

        os.environ["RP_SITE_WORKERS"] = "-1"
        assert get_max_workers_from_env() is None

        # Very high value - should cap at 8
        os.environ["RP_SITE_WORKERS"] = "20"
        assert get_max_workers_from_env() == 8

        print("[PASS] Environment variable parsing")

    finally:
        # Restore original
        if original:
            os.environ["RP_SITE_WORKERS"] = original
        elif "RP_SITE_WORKERS" in os.environ:
            del os.environ["RP_SITE_WORKERS"]


def test_parallel_scraping_mock():
    """Test parallel scraping with mock scrape function"""

    # Mock scrape function that simulates work
    def mock_scrape(site_key: str, site_config: dict):
        time.sleep(0.1)  # Simulate scraping
        return (10, f"https://{site_key}.com")

    # Create mock sites
    sites = [
        ("site1", {"url": "https://site1.com"}),
        ("site2", {"url": "https://site2.com"}),
        ("site3", {"url": "https://site3.com"}),
    ]

    # Scrape in parallel
    results = scrape_sites_parallel(
        sites=sites,
        scrape_function=mock_scrape,
        max_workers=2,
        progress_bar=False
    )

    # Verify all sites were scraped
    assert len(results) == 3
    assert results["site1"] == (10, "https://site1.com")
    assert results["site2"] == (10, "https://site2.com")
    assert results["site3"] == (10, "https://site3.com")

    print("[PASS] Parallel scraping with mock function")


def test_error_handling():
    """Test that errors in one site don't stop others"""

    def scrape_with_errors(site_key: str, site_config: dict):
        if site_key == "failing_site":
            raise Exception("Simulated failure")
        return (5, f"https://{site_key}.com")

    sites = [
        ("good_site1", {}),
        ("failing_site", {}),
        ("good_site2", {}),
    ]

    results = scrape_sites_parallel(
        sites=sites,
        scrape_function=scrape_with_errors,
        max_workers=2,
        progress_bar=False
    )

    # Verify that good sites succeeded
    assert results["good_site1"] == (5, "https://good_site1.com")
    assert results["good_site2"] == (5, "https://good_site2.com")

    # Failing site should return (0, "")
    assert results["failing_site"] == (0, "")

    print("[PASS] Error isolation (one failure doesn't stop others)")


def test_performance_improvement():
    """Test that parallel is faster than sequential for multiple sites"""

    def slow_scrape(site_key: str, site_config: dict):
        time.sleep(0.3)  # Simulate slow scraping
        return (1, f"https://{site_key}.com")

    sites = [
        (f"site{i}", {}) for i in range(4)
    ]

    # Sequential (1 worker) - should take ~1.2s (4 × 0.3s)
    start = time.time()
    results_sequential = scrape_sites_parallel(
        sites=sites,
        scrape_function=slow_scrape,
        max_workers=1,
        progress_bar=False
    )
    sequential_time = time.time() - start

    # Parallel (2 workers) - should take ~0.6s (2 batches × 0.3s)
    start = time.time()
    results_parallel = scrape_sites_parallel(
        sites=sites,
        scrape_function=slow_scrape,
        max_workers=2,
        progress_bar=False
    )
    parallel_time = time.time() - start

    # Verify both produced same results
    assert results_sequential == results_parallel

    # Parallel should be significantly faster (at least 1.5x)
    speedup = sequential_time / parallel_time
    assert speedup >= 1.5, f"Speedup {speedup:.2f}x is too low"

    print(f"[PASS] Performance improvement: {speedup:.2f}x faster with 2 workers")
    print(f"       Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s")


def test_single_site_optimization():
    """Test that single site doesn't use parallel execution"""

    def mock_scrape(site_key: str, site_config: dict):
        return (1, "https://site.com")

    # Single site
    sites = [("only_site", {})]

    # Should work even with max_workers > 1
    results = scrape_sites_parallel(
        sites=sites,
        scrape_function=mock_scrape,
        max_workers=5,
        progress_bar=False
    )

    assert len(results) == 1
    assert results["only_site"] == (1, "https://site.com")

    print("[PASS] Single site optimization")


def test_empty_sites_list():
    """Test handling of empty sites list"""

    def mock_scrape(site_key: str, site_config: dict):
        return (1, "https://site.com")

    results = scrape_sites_parallel(
        sites=[],
        scrape_function=mock_scrape,
        max_workers=2,
        progress_bar=False
    )

    assert results == {}

    print("[PASS] Empty sites list handling")


def test_worker_capping():
    """Test that workers are capped appropriately"""
    cpu_count = os.cpu_count() or 2

    # Test automatic worker calculation (should never exceed 4 for GitHub Actions safety)
    workers_auto = calculate_workers(100)  # Large site count
    assert workers_auto <= 4, f"Auto workers {workers_auto} exceeds GitHub Actions safety cap of 4"
    assert workers_auto <= cpu_count or workers_auto <= 4  # Either CPU or safety cap

    # Test manual override is respected
    workers_manual = calculate_workers(10, max_workers=7)
    assert workers_manual == 7, f"Manual override not respected: {workers_manual} != 7"

    print(f"[PASS] Worker capping (CPU count: {cpu_count}, auto: {workers_auto}, manual: {workers_manual})")


def test_concurrent_execution():
    """Test that sites actually run concurrently"""

    execution_times = {}

    def track_execution(site_key: str, site_config: dict):
        start = time.time()
        time.sleep(0.2)
        execution_times[site_key] = time.time()
        return (1, "https://site.com")

    sites = [
        ("site1", {}),
        ("site2", {}),
    ]

    overall_start = time.time()
    scrape_sites_parallel(
        sites=sites,
        scrape_function=track_execution,
        max_workers=2,
        progress_bar=False
    )
    overall_elapsed = time.time() - overall_start

    # Both sites should finish within ~0.3s (concurrent)
    # If sequential, would take ~0.4s
    assert overall_elapsed < 0.35, f"Took {overall_elapsed:.2f}s - not concurrent!"

    # Both should have executed (timestamps recorded)
    assert len(execution_times) == 2

    print(f"[PASS] Concurrent execution (completed in {overall_elapsed:.2f}s)")


def run_all_tests():
    """Run all parallel scraping tests"""
    print("\n" + "="*60)
    print("PARALLEL SCRAPING TESTS")
    print("="*60 + "\n")

    try:
        test_worker_calculation()
        test_env_variable_parsing()
        test_parallel_scraping_mock()
        test_error_handling()
        test_performance_improvement()
        test_single_site_optimization()
        test_empty_sites_list()
        test_worker_capping()
        test_concurrent_execution()

        print("\n" + "="*60)
        print("[PASS] ALL TESTS PASSED (9/9)")
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
