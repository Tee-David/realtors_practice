"""
Test script for intelligent batching system
"""
import time
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)

def test_batch_scraping():
    """Test the batching system with a small batch"""

    print_section("TEST 1: Start Scraping with Batching (5 sites)")

    # Start a scrape with 5 sites (should create 1 batch)
    response = requests.post(
        f"{BASE_URL}/scrape/start",
        json={
            "sites": ["cwlagos", "npc", "propertypro", "jiji", "lamudi"],
            "max_pages": 3,  # Only 3 pages per site for quick test
            "geocoding": False  # Disable geocoding for faster test
        }
    )

    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    if not result.get('success'):
        print("[ERROR] Failed to start scraping")
        return

    run_id = result.get('run_id')
    print(f"\n[OK] Started scraping run: {run_id}")
    print(f"Message: {result.get('message')}")

    print_section("TEST 2: Monitor Progress in Real-Time")

    # Monitor progress
    check_count = 0
    max_checks = 60  # Check for up to 5 minutes (60 * 5 seconds)

    while check_count < max_checks:
        time.sleep(5)  # Check every 5 seconds
        check_count += 1

        # Get status
        status_response = requests.get(f"{BASE_URL}/scrape/status")
        status = status_response.json()

        is_running = status.get('is_running', False)
        current_run = status.get('current_run')

        if not is_running:
            print("\n[OK] Scraping completed!")

            # Show last run details
            last_run = status.get('last_run', {})
            if last_run:
                print(f"\nFinal Statistics:")
                print(f"  Run ID: {last_run.get('run_id')}")
                print(f"  Started: {last_run.get('started_at')}")
                print(f"  Completed: {last_run.get('completed_at')}")
                print(f"  Success: {last_run.get('success')}")

                final_stats = last_run.get('final_stats', {})
                if final_stats:
                    print(f"\n  Total Sites: {final_stats.get('total_sites')}")
                    print(f"  Successful: {final_stats.get('successful_sites')}")
                    print(f"  Failed: {final_stats.get('failed_sites')}")
                    print(f"  Failed Batches: {final_stats.get('failed_batches')}")

                failed_batches = last_run.get('failed_batches', [])
                if failed_batches:
                    print(f"\n  Failed Batches Details:")
                    for fb in failed_batches:
                        print(f"    Batch {fb.get('batch_num')}: {fb.get('sites')}")
                        print(f"      Error: {fb.get('error')}")

            break

        # Show current progress
        if current_run:
            batch_info = current_run.get('batch_info', {})
            progress = current_run.get('progress', {})
            timing = current_run.get('timing', {})
            resources = current_run.get('resources', {})

            print(f"\n[Check {check_count}] Scraping in progress...")
            print(f"  Batch: {batch_info.get('current_batch')}/{batch_info.get('total_batches')}")
            print(f"  Batch Status: {batch_info.get('batch_status')}")
            print(f"  Current Sites: {batch_info.get('current_batch_sites', [])}")

            print(f"\n  Progress:")
            print(f"    Total: {progress.get('total_sites')}")
            print(f"    Completed: {progress.get('completed_sites')}")
            print(f"    In Progress: {progress.get('in_progress_sites')}")
            print(f"    Failed: {progress.get('failed_sites')}")
            print(f"    Pending: {progress.get('pending_sites')}")

            if timing:
                elapsed = timing.get('elapsed_seconds', 0)
                remaining = timing.get('estimated_remaining_seconds')
                avg_time = timing.get('average_seconds_per_site')
                completion = timing.get('estimated_completion')

                print(f"\n  Timing:")
                print(f"    Elapsed: {elapsed}s ({elapsed // 60}m {elapsed % 60}s)")
                if remaining:
                    print(f"    Remaining: {remaining}s ({remaining // 60}m {remaining % 60}s)")
                if avg_time:
                    print(f"    Avg per site: {avg_time}s")
                if completion:
                    print(f"    Est. completion: {completion}")

            if resources:
                print(f"\n  Resources:")
                print(f"    Memory: {resources.get('memory_percent')}%")
                print(f"    CPU: {resources.get('cpu_percent')}%")

    if check_count >= max_checks:
        print("\n[WARN] Timeout waiting for scraping to complete")
        print("The scraping may still be running in the background")

def test_batch_splitting():
    """Test the batch splitting logic without actually running"""

    print_section("TEST 3: Batch Splitting Logic")

    # Import the scraper manager
    import sys
    sys.path.insert(0, 'api/helpers')
    from scraper_manager import ScraperManager

    manager = ScraperManager()

    # Test with different site counts
    test_cases = [
        (5, "Small job (5 sites)"),
        (15, "Medium job (15 sites)"),
        (30, "Large job (30 sites)"),
        (51, "Extra large job (51 sites)")
    ]

    for site_count, description in test_cases:
        sites = [f"site{i}" for i in range(site_count)]
        batches = manager._split_into_batches(sites)

        print(f"\n{description}:")
        print(f"  Total sites: {site_count}")
        print(f"  Batches created: {len(batches)}")
        print(f"  Sites per batch: {[len(b) for b in batches]}")

        if len(batches) <= 5:
            for i, batch in enumerate(batches, 1):
                print(f"    Batch {i}: {len(batch)} sites")

if __name__ == "__main__":
    print(f"\nBatching System Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Test 1: Batch splitting logic (no API calls)
        test_batch_splitting()

        # Test 2: Actual scraping with batching (requires API server)
        print("\n\nNow testing actual scraping with API...")
        print("Make sure the API server is running!")

        user_input = input("\nProceed with live scraping test? (yes/no): ")
        if user_input.lower() in ['yes', 'y']:
            test_batch_scraping()
        else:
            print("\n[SKIP] Skipped live scraping test")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
