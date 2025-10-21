#!/usr/bin/env python3
"""
Performance Test: Sequential vs Parallel Scraping

Compares scraping time with 1 worker (sequential) vs 2 workers (parallel).
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_scraper_with_workers(workers, test_name):
    """Run scraper with specified number of workers and measure time."""
    print(f"\n{'='*60}")
    print(f"{test_name}")
    print(f"{'='*60}")
    print(f"Workers: {workers}")
    print(f"Start time: {time.strftime('%H:%M:%S')}")

    # Set environment variables
    env = os.environ.copy()
    env['RP_SITE_WORKERS'] = str(workers)
    env['RP_PAGE_CAP'] = '1'
    env['RP_GEOCODE'] = '0'
    env['RP_DETAIL_CAP'] = '0'
    env['RP_NO_AUTO_WATCHER'] = '1'

    # Run scraper
    start = time.time()

    try:
        result = subprocess.run(
            [sys.executable, 'main.py'],
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        elapsed = time.time() - start

        # Parse output for results
        output = result.stdout

        # Count successful sites
        successful = output.count("Exported")
        total_listings = 0

        # Extract listing counts
        for line in output.split('\n'):
            if 'Exported' in line and 'listings' in line:
                try:
                    count = int(line.split('Exported')[1].split('listings')[0].strip())
                    total_listings += count
                except:
                    pass

        print(f"\nResults:")
        print(f"  Time elapsed: {elapsed:.1f}s")
        print(f"  Successful sites: {successful}/3")
        print(f"  Total listings: {total_listings}")
        print(f"  Avg time/site: {elapsed/3:.1f}s")

        return {
            'workers': workers,
            'elapsed': elapsed,
            'successful': successful,
            'listings': total_listings
        }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"\n[TIMEOUT] Test exceeded 5 minutes ({elapsed:.1f}s)")
        return None
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("PARALLEL SCRAPING PERFORMANCE TEST")
    print("="*60)
    print("\nTesting with 3 sites (cwlagos, buyletlive, edenoasis)")
    print("Configuration: 1 page, no geocoding, no detail scraping")

    # Run sequential test
    sequential = run_scraper_with_workers(1, "TEST 1: SEQUENTIAL (1 worker)")

    time.sleep(5)  # Brief pause between tests

    # Run parallel test
    parallel = run_scraper_with_workers(2, "TEST 2: PARALLEL (2 workers)")

    # Compare results
    if sequential and parallel:
        print("\n" + "="*60)
        print("PERFORMANCE COMPARISON")
        print("="*60)

        speedup = sequential['elapsed'] / parallel['elapsed']
        time_saved = sequential['elapsed'] - parallel['elapsed']

        print(f"\nSequential (1 worker):")
        print(f"  Time: {sequential['elapsed']:.1f}s")
        print(f"  Listings: {sequential['listings']}")

        print(f"\nParallel (2 workers):")
        print(f"  Time: {parallel['elapsed']:.1f}s")
        print(f"  Listings: {parallel['listings']}")

        print(f"\nPerformance Improvement:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Time saved: {time_saved:.1f}s")
        print(f"  Efficiency: {(speedup-1)*100:.0f}% improvement")

        if speedup >= 1.5:
            print(f"\n[SUCCESS] Parallel scraping is {speedup:.1f}x faster!")
        else:
            print(f"\n[WARNING] Speedup {speedup:.1f}x is lower than expected (target: 1.5x+)")

        print("\n" + "="*60)

        return speedup >= 1.3  # At least 30% improvement
    else:
        print("\n[FAIL] Could not complete performance comparison")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
