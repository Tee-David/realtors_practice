"""
Test scraper integration - verify API and scraping functionality
Tests both small and large batch scraping scenarios
"""
import requests
import time
import json
import sys
import io
from pathlib import Path

# Fix Windows Unicode issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API base URL
BASE_URL = "http://localhost:5000/api"


def test_health_check():
    """Test if API server is running"""
    print("\n=== Testing API Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API server is healthy")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server")
        print("  Please start the API server with: python api_server.py")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_get_sites():
    """Test getting list of sites"""
    print("\n=== Testing Get Sites ===")
    try:
        response = requests.get(f"{BASE_URL}/sites", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            enabled = data.get('enabled', 0)
            print(f"✓ Got sites list: {total} total, {enabled} enabled")

            # Show first few sites (sites is a list, not dict)
            sites = data.get('sites', [])
            for site in sites[:3]:
                status = "enabled" if site.get('enabled') else "disabled"
                print(f"  - {site.get('site_key')}: {site.get('name', 'N/A')} ({status})")

            return True, data
        else:
            print(f"✗ Failed to get sites: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Error getting sites: {e}")
        return False, None


def test_scrape_status():
    """Test getting scraper status"""
    print("\n=== Testing Scraper Status ===")
    try:
        response = requests.get(f"{BASE_URL}/scrape/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            is_running = data.get('is_running', False)
            print(f"✓ Scraper status: {'Running' if is_running else 'Idle'}")

            if is_running:
                current_run = data.get('current_run', {})
                batch_info = current_run.get('batch_info', {})
                print(f"  Current batch: {batch_info.get('current_batch')}/{batch_info.get('total_batches')}")
                print(f"  Sites in batch: {len(batch_info.get('current_batch_sites', []))}")

            return True, data
        else:
            print(f"✗ Failed to get status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Error getting status: {e}")
        return False, None


def test_small_batch_scrape():
    """Test small batch scrape (1-2 sites, few pages)"""
    print("\n=== Testing Small Batch Scrape ===")
    print("Starting scrape with 2 sites, 2 pages each...")

    try:
        # Use 2 known sites for testing
        payload = {
            "sites": ["cwlagos", "npc"],  # 2 sites
            "max_pages": 2,  # Only 2 pages per site
            "geocoding": False  # Disable geocoding for speed
        }

        response = requests.post(
            f"{BASE_URL}/scrape/start",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                run_id = data.get('run_id')
                print(f"✓ Scrape started successfully")
                print(f"  Run ID: {run_id}")
                print(f"  Message: {data.get('message')}")

                # Monitor progress for 2 minutes
                print("\n  Monitoring progress...")
                monitor_scrape_progress(max_duration=120)

                return True, data
            else:
                print(f"✗ Failed to start scrape: {data.get('error')}")
                return False, None
        else:
            print(f"✗ Request failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"✗ Error starting scrape: {e}")
        return False, None


def test_large_batch_scrape():
    """Test large batch scrape (all enabled sites)"""
    print("\n=== Testing Large Batch Scrape ===")
    print("Starting scrape with all enabled sites...")

    try:
        payload = {
            "sites": [],  # Empty = all enabled sites
            "max_pages": 5,  # Limit pages for testing
            "geocoding": False  # Disable geocoding for speed
        }

        response = requests.post(
            f"{BASE_URL}/scrape/start",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                run_id = data.get('run_id')
                print(f"✓ Scrape started successfully")
                print(f"  Run ID: {run_id}")
                print(f"  Message: {data.get('message')}")

                # Show batch info
                current_run = data.get('current_run', {})
                batch_info = current_run.get('batch_info', {})
                print(f"  Total batches: {batch_info.get('total_batches')}")
                print(f"  Total sites: {current_run.get('progress', {}).get('total_sites')}")

                # Monitor progress for 5 minutes
                print("\n  Monitoring progress...")
                monitor_scrape_progress(max_duration=300)

                return True, data
            else:
                error = data.get('error', 'Unknown error')
                print(f"✗ Failed to start scrape: {error}")

                # Check if already running
                if 'already running' in error.lower():
                    print("  Note: A scrape is already in progress")
                    return True, data  # Not a failure

                return False, None
        else:
            print(f"✗ Request failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"✗ Error starting scrape: {e}")
        return False, None


def monitor_scrape_progress(max_duration=300):
    """Monitor scrape progress in real-time"""
    start_time = time.time()
    last_completed = 0

    while time.time() - start_time < max_duration:
        try:
            response = requests.get(f"{BASE_URL}/scrape/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                is_running = data.get('is_running', False)

                if not is_running:
                    print("\n  ✓ Scrape completed!")
                    last_run = data.get('last_run', {})
                    if last_run:
                        final_stats = last_run.get('final_stats', {})
                        print(f"    Total sites: {final_stats.get('total_sites', 0)}")
                        print(f"    Successful: {final_stats.get('successful_sites', 0)}")
                        print(f"    Failed: {final_stats.get('failed_sites', 0)}")
                    break

                # Show progress
                current_run = data.get('current_run', {})
                progress = current_run.get('progress', {})
                batch_info = current_run.get('batch_info', {})
                timing = current_run.get('timing', {})

                completed = progress.get('completed_sites', 0)
                total = progress.get('total_sites', 0)
                in_progress = progress.get('in_progress_sites', 0)

                # Only print if progress changed
                if completed != last_completed:
                    percent = (completed / total * 100) if total > 0 else 0
                    eta = timing.get('estimated_remaining_seconds')
                    eta_str = f"{eta // 60}m {eta % 60}s" if eta else "calculating..."

                    print(f"  Progress: {completed}/{total} ({percent:.1f}%) | "
                          f"Batch: {batch_info.get('current_batch')}/{batch_info.get('total_batches')} | "
                          f"In progress: {in_progress} | "
                          f"ETA: {eta_str}")

                    last_completed = completed

            time.sleep(10)  # Check every 10 seconds

        except Exception as e:
            print(f"  Warning: Error monitoring progress: {e}")
            time.sleep(10)

    # Check if timed out
    if time.time() - start_time >= max_duration:
        print(f"\n  Note: Monitoring timed out after {max_duration}s")
        print("  Scrape may still be running. Check logs for details.")


def test_get_data():
    """Test getting scraped data"""
    print("\n=== Testing Get Data ===")
    try:
        # Get list of available data files
        response = requests.get(f"{BASE_URL}/data/sites", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sites = data.get('sites', [])
            print(f"✓ Found data for {len(sites)} sites")

            # Show first few
            for site in sites[:3]:
                print(f"  - {site.get('site_key')}: {site.get('record_count', 0)} records")

            # Try to get data from first site
            if sites:
                first_site = sites[0]['site_key']
                print(f"\n  Fetching data from {first_site}...")

                response = requests.get(
                    f"{BASE_URL}/data/sites/{first_site}",
                    params={'limit': 5},
                    timeout=10
                )

                if response.status_code == 200:
                    site_data = response.json()
                    records = site_data.get('data', [])
                    print(f"  ✓ Got {len(records)} sample records")

                    if records:
                        first_record = records[0]
                        print(f"    Sample: {first_record.get('title', 'N/A')[:50]}...")

            return True, data
        else:
            print(f"✗ Failed to get data: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Error getting data: {e}")
        return False, None


def main():
    """Run all integration tests"""
    import argparse

    parser = argparse.ArgumentParser(description='Test scraper integration')
    parser.add_argument('--skip-scrape', action='store_true', help='Skip scraping tests')
    parser.add_argument('--small-batch-only', action='store_true', help='Run only small batch test')
    parser.add_argument('--large-batch-only', action='store_true', help='Run only large batch test')
    args = parser.parse_args()

    print("=" * 60)
    print("SCRAPER INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {}

    # Test 1: Health check
    results['health'] = test_health_check()
    if not results['health']:
        print("\n✗ API server is not running. Cannot continue tests.")
        print("  Start the server with: python api_server.py")
        sys.exit(1)

    # Test 2: Get sites
    results['sites'], _ = test_get_sites()

    # Test 3: Get status
    results['status'], status_data = test_scrape_status()

    # Check if scraper is already running
    if status_data and status_data.get('is_running'):
        print("\n⚠ WARNING: Scraper is already running!")
        print("  Skipping scrape tests to avoid conflicts.")
        results['small_batch'] = None
        results['large_batch'] = None
    elif args.skip_scrape:
        print("\n  Skipping scrape tests (--skip-scrape flag)")
        results['small_batch'] = None
        results['large_batch'] = None
    else:
        # Test 4: Small batch scrape
        if not args.large_batch_only:
            print("\n" + "=" * 60)
            print("SMALL BATCH SCRAPE TEST")
            print("=" * 60)
            print("Running small batch test (2 sites, 2 pages each)...")
            results['small_batch'], _ = test_small_batch_scrape()

            # Wait before next test
            if not args.small_batch_only:
                time.sleep(5)

        # Test 5: Large batch scrape
        if not args.small_batch_only and not args.large_batch_only:
            print("\n" + "=" * 60)
            print("LARGE BATCH SCRAPE TEST")
            print("=" * 60)
            print("Skipping large batch test (use --large-batch-only to run)")
            results['large_batch'] = None
        elif args.large_batch_only:
            print("\n" + "=" * 60)
            print("LARGE BATCH SCRAPE TEST")
            print("=" * 60)
            print("Running large batch test (all enabled sites)...")
            results['large_batch'], _ = test_large_batch_scrape()

    # Test 6: Get data
    results['data'] = test_get_data()[0] if test_get_data() else False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
            symbol = "○"
        elif result:
            status = "PASSED"
            symbol = "✓"
        else:
            status = "FAILED"
            symbol = "✗"

        print(f"{symbol} {test_name.replace('_', ' ').title()}: {status}")

    # Overall result
    tested = [v for v in results.values() if v is not None]
    passed = [v for v in tested if v is True]

    print("\n" + "=" * 60)
    print(f"Overall: {len(passed)}/{len(tested)} tests passed")
    print("=" * 60)

    return len(passed) == len(tested)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
