"""
Comprehensive test of batching system with 15 sites to verify multiple batch execution
This will force the system to create 2 batches (10 + 5 split)
"""
import sys
import io
import time
import requests
import json
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)

def test_multiple_batches():
    """Test batching with 15 sites to force 2 batches (10 + 5)"""

    print_section("COMPREHENSIVE BATCHING TEST: 15 Sites (2 Batches Expected)")

    # Select 15 fast sites for testing
    test_sites = [
        "cwlagos", "npc", "propertypro", "jiji", "lamudi",
        "buyletlive", "edenoasis", "privateproperty", "property24",
        "nigerianpropertymarket", "houseafrica", "naijahouses",
        "myproperty", "olist", "realestatenigeria"
    ]

    print(f"\nTest Configuration:")
    print(f"  Sites: {len(test_sites)}")
    print(f"  Expected Batches: 2 (Batch 1: 10 sites, Batch 2: 5 sites)")
    print(f"  Pages per site: 1 (for speed)")
    print(f"  Geocoding: Disabled (for speed)")
    print(f"  Sites list: {', '.join(test_sites[:5])}... (+{len(test_sites)-5} more)")

    # Start scraping
    print("\nStarting scraping job...")
    response = requests.post(
        f"{BASE_URL}/scrape/start",
        json={
            "sites": test_sites,
            "max_pages": 1,  # Just 1 page per site for speed
            "geocoding": False
        }
    )

    print(f"Status Code: {response.status_code}")
    result = response.json()

    if not result.get('success'):
        print(f"\n[ERROR] Failed to start scraping")
        print(f"Error: {result.get('error')}")
        return False

    run_id = result.get('run_id')
    print(f"\n[OK] Started scraping run: {run_id}")
    print(f"Message: {result.get('message')}")

    # Verify batch configuration
    current_run = result.get('current_run', {})
    batch_info = current_run.get('batch_info', {})
    total_batches = batch_info.get('total_batches', 0)

    print(f"\nBatch Configuration:")
    print(f"  Total Batches: {total_batches}")

    if total_batches != 2:
        print(f"  [WARNING] Expected 2 batches, got {total_batches}")
        print(f"  This may be due to batch size configuration")
    else:
        print(f"  [OK] Correctly configured for 2 batches")

    print_section("Monitoring Progress...")

    # Monitor progress
    check_count = 0
    max_checks = 240  # Check for up to 20 minutes (240 * 5 sec)

    last_batch_num = 0
    last_status_str = None
    batch_transitions = []

    while check_count < max_checks:
        time.sleep(5)  # Check every 5 seconds
        check_count += 1

        try:
            # Get status
            status_response = requests.get(f"{BASE_URL}/scrape/status")
            status = status_response.json()

            is_running = status.get('is_running', False)
            current_run = status.get('current_run')

            if not is_running:
                print("\n[OK] Scraping completed!")

                # Show final results
                last_run = status.get('last_run', {})
                if last_run:
                    print_section("Final Results")

                    print(f"Run ID: {last_run.get('run_id')}")
                    print(f"Success: {last_run.get('success')}")

                    # Timing
                    start_time = datetime.fromisoformat(last_run.get('started_at'))
                    end_time = datetime.fromisoformat(last_run.get('completed_at'))
                    duration = (end_time - start_time).total_seconds()

                    print(f"\nTiming:")
                    print(f"  Started: {start_time.strftime('%H:%M:%S')}")
                    print(f"  Completed: {end_time.strftime('%H:%M:%S')}")
                    print(f"  Duration: {int(duration)}s ({int(duration/60)}m {int(duration%60)}s)")

                    # Statistics
                    final_stats = last_run.get('final_stats', {})
                    if final_stats:
                        print(f"\nSite Statistics:")
                        print(f"  Total Sites: {final_stats.get('total_sites')}")
                        print(f"  Successful: {final_stats.get('successful_sites')}")
                        print(f"  Failed: {final_stats.get('failed_sites')}")
                        print(f"  Failed Batches: {final_stats.get('failed_batches')}")

                        success_rate = (final_stats.get('successful_sites', 0) /
                                      final_stats.get('total_sites', 1)) * 100
                        print(f"  Success Rate: {success_rate:.1f}%")

                    # Batch transitions
                    if batch_transitions:
                        print(f"\nBatch Transitions:")
                        for transition in batch_transitions:
                            print(f"  {transition}")

                    # Failed batches detail
                    failed_batches = last_run.get('failed_batches', [])
                    if failed_batches:
                        print(f"\nFailed Batches Details:")
                        for fb in failed_batches:
                            print(f"  Batch {fb.get('batch_num')}:")
                            print(f"    Sites: {', '.join(fb.get('sites', []))}")
                            print(f"    Error: {fb.get('error')}")

                    print_section("Test Result")

                    # Evaluate test success
                    test_success = True
                    issues = []

                    # Check if batches were correctly split
                    if total_batches < 2:
                        issues.append(f"Expected at least 2 batches, got {total_batches}")
                        test_success = False

                    # Check if all sites completed
                    if final_stats.get('total_sites') != len(test_sites):
                        issues.append(f"Site count mismatch: expected {len(test_sites)}, got {final_stats.get('total_sites')}")
                        test_success = False

                    # Check success rate
                    if final_stats.get('successful_sites', 0) < len(test_sites) * 0.8:
                        issues.append(f"Success rate too low: {success_rate:.1f}% (expected >80%)")
                        test_success = False

                    if test_success:
                        print("[OK] Test PASSED")
                        print("\nBatching system is working correctly:")
                        print("  [+] Multiple batches created")
                        print("  [+] All sites processed")
                        print("  [+] High success rate")
                        return True
                    else:
                        print("[FAIL] Test FAILED")
                        print("\nIssues found:")
                        for issue in issues:
                            print(f"  [-] {issue}")
                        return False

                break

            # Show progress updates
            if current_run:
                batch_info = current_run.get('batch_info', {})
                progress = current_run.get('progress', {})
                timing = current_run.get('timing', {})
                resources = current_run.get('resources', {})

                current_batch = batch_info.get('current_batch', 0)
                batch_status = batch_info.get('batch_status', 'unknown')

                # Detect batch transitions
                if current_batch != last_batch_num and current_batch > 0:
                    transition_msg = f"Batch {last_batch_num} → {current_batch} at {datetime.now().strftime('%H:%M:%S')}"
                    batch_transitions.append(transition_msg)
                    print(f"\n[BATCH TRANSITION] {transition_msg}")
                    last_batch_num = current_batch

                # Create status string
                status_str = f"{current_batch}/{batch_info.get('total_batches')}-{batch_status}"

                # Print updates periodically or on status change
                if status_str != last_status_str or check_count % 6 == 0:  # Every 30 seconds
                    print(f"\n[Check {check_count}] Scraping in progress...")
                    print(f"  Batch: {current_batch}/{batch_info.get('total_batches')} - {batch_status}")

                    current_sites = batch_info.get('current_batch_sites', [])
                    if current_sites:
                        sites_display = ', '.join(current_sites[:3])
                        if len(current_sites) > 3:
                            sites_display += f"... (+{len(current_sites)-3} more)"
                        print(f"  Current Sites: {sites_display}")

                    print(f"\n  Progress:")
                    print(f"    Completed: {progress.get('completed_sites')}/{progress.get('total_sites')}")
                    print(f"    In Progress: {progress.get('in_progress_sites')}")
                    print(f"    Failed: {progress.get('failed_sites')}")
                    print(f"    Pending: {progress.get('pending_sites')}")

                    # Progress bar
                    total = progress.get('total_sites', 1)
                    completed = progress.get('completed_sites', 0)
                    percent = (completed / total) * 100
                    bar_length = 40
                    filled = int((completed / total) * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"    [{bar}] {percent:.1f}%")

                    if timing and timing.get('elapsed_seconds'):
                        elapsed = timing.get('elapsed_seconds', 0)
                        remaining = timing.get('estimated_remaining_seconds')
                        avg_time = timing.get('average_seconds_per_site')

                        print(f"\n  Timing:")
                        mins, secs = divmod(elapsed, 60)
                        print(f"    Elapsed: {int(mins)}m {int(secs)}s")

                        if remaining:
                            mins, secs = divmod(remaining, 60)
                            print(f"    ETA: {int(mins)}m {int(secs)}s")

                        if avg_time:
                            print(f"    Avg/site: {avg_time:.1f}s")

                    if resources and resources.get('memory_percent'):
                        print(f"\n  Resources: Memory {resources.get('memory_percent')}% | CPU {resources.get('cpu_percent')}%")

                last_status_str = status_str

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] Could not connect to API: {e}")
            print("Is the API server running?")
            return False
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            return False

    if check_count >= max_checks:
        print("\n[TIMEOUT] Test timed out after 20 minutes")
        print("The scraping may still be running in the background")
        return False

if __name__ == "__main__":
    print_section("Comprehensive Batching System Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will test the batching system with 15 sites")
    print("Expected behavior: 2 batches (10 sites + 5 sites)")
    print("Each site limited to 1 page for faster testing")
    print("Estimated time: 10-15 minutes")
    print("\n[!] Make sure the API server is running: python api_server.py")

    # Quick API connection test
    print("\nTesting API connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] API server is running\n")

            # Run the test
            success = test_multiple_batches()

            print(f"\n{'='*80}")
            print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Result: {'PASSED [+]' if success else 'FAILED [-]'}")
            print('='*80)

            exit(0 if success else 1)
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            exit(1)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to API server: {e}")
        print("\n[!] Please start the API server first:")
        print("  python api_server.py")
        exit(1)
