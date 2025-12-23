"""
Live test of batching system with actual scraping
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

def test_live_scraping():
    """Test the batching system with a small live scrape"""

    print_section("LIVE TEST: Batching with 3 Sites (Quick Test)")

    # Start a scrape with just 3 sites for quick testing
    # This should complete in about 2-3 minutes
    response = requests.post(
        f"{BASE_URL}/scrape/start",
        json={
            "sites": ["cwlagos"],  # Just 1 site for very quick test
            "max_pages": 2,  # Only 2 pages for speed
            "geocoding": False  # Disable for speed
        }
    )

    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    if not result.get('success'):
        print("[ERROR] Failed to start scraping")
        print(f"Error: {result.get('error')}")
        return

    run_id = result.get('run_id')
    print(f"\n[OK] Started scraping run: {run_id}")
    print(f"Message: {result.get('message')}")

    print_section("Monitoring Progress...")

    # Monitor progress
    check_count = 0
    max_checks = 120  # Check for up to 10 minutes

    last_status = None

    while check_count < max_checks:
        time.sleep(3)  # Check every 3 seconds
        check_count += 1

        try:
            # Get status
            status_response = requests.get(f"{BASE_URL}/scrape/status")
            status = status_response.json()

            is_running = status.get('is_running', False)
            current_run = status.get('current_run')

            # Only print if status changed
            current_status = json.dumps(current_run, sort_keys=True) if current_run else None

            if current_status != last_status or check_count % 10 == 0:  # Print every 10 checks even if no change
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
                    current_sites = batch_info.get('current_batch_sites', [])
                    if current_sites:
                        print(f"  Current Sites: {', '.join(current_sites[:3])}{'...' if len(current_sites) > 3 else ''}")

                    print(f"\n  Progress:")
                    print(f"    Total: {progress.get('total_sites')} | " +
                          f"Completed: {progress.get('completed_sites')} | " +
                          f"In Progress: {progress.get('in_progress_sites')} | " +
                          f"Failed: {progress.get('failed_sites')} | " +
                          f"Pending: {progress.get('pending_sites')}")

                    if timing and timing.get('elapsed_seconds'):
                        elapsed = timing.get('elapsed_seconds', 0)
                        remaining = timing.get('estimated_remaining_seconds')
                        avg_time = timing.get('average_seconds_per_site')

                        print(f"\n  Timing:")
                        mins, secs = divmod(elapsed, 60)
                        print(f"    Elapsed: {int(mins)}m {int(secs)}s")

                        if remaining:
                            mins, secs = divmod(remaining, 60)
                            print(f"    Remaining: {int(mins)}m {int(secs)}s")

                        if avg_time:
                            print(f"    Avg per site: {avg_time}s")

                    if resources and resources.get('memory_percent'):
                        print(f"\n  Resources: Memory {resources.get('memory_percent')}% | CPU {resources.get('cpu_percent')}%")

                last_status = current_status

        except requests.exceptions.RequestException as e:
            print(f"\n[WARN] Could not connect to API: {e}")
            print("Is the API server running?")
            break

    if check_count >= max_checks:
        print("\n[WARN] Timeout waiting for scraping to complete")
        print("The scraping may still be running in the background")

if __name__ == "__main__":
    print(f"\nLive Batching System Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will start a real scraping job with 1 site (2 pages each)")
    print("Estimated time: 1-2 minutes")
    print("\nMake sure the API server is running (python api_server.py)")

    try:
        # Quick connection test
        print("\nTesting API connection...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] API server is running")
            test_live_scraping()
        else:
            print(f"[ERROR] API returned status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to API server: {e}")
        print("\nPlease start the API server first:")
        print("  python api_server.py")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
