"""
Test batching with 5 sites to verify multiple batch execution
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

print_section("Testing Batching with 5 Sites")
print("This will create 1 batch of 5 sites (since total < 10)")
print("Each site limited to 1 page for speed")
print(f"Started at: {datetime.now().strftime('%H:%M:%S')}\n")

# Test with 5 sites - should create 1 batch
response = requests.post(
    f"{BASE_URL}/scrape/start",
    json={
        "sites": ["cwlagos", "npc", "propertypro", "jiji", "lamudi"],
        "max_pages": 1,  # Just 1 page per site for speed
        "geocoding": False
    }
)

print(f"Start Response: {response.status_code}")
result = response.json()

if result.get('success'):
    print(f"[OK] {result.get('message')}")
    print(f"Run ID: {result.get('run_id')}")

    batch_info = result.get('current_run', {}).get('batch_info', {})
    print(f"\nBatch Configuration:")
    print(f"  Total Batches: {batch_info.get('total_batches')}")
    print(f"  Expected: 1 batch (5 sites)")

    print("\nMonitoring progress (checking every 10 seconds)...")

    # Monitor for up to 20 minutes
    for i in range(120):
        time.sleep(10)

        status = requests.get(f"{BASE_URL}/scrape/status").json()

        if not status.get('is_running'):
            print(f"\n[OK] Scraping completed!")

            last_run = status.get('last_run', {})
            final_stats = last_run.get('final_stats', {})

            print(f"\nFinal Results:")
            print(f"  Success: {last_run.get('success')}")
            print(f"  Total Sites: {final_stats.get('total_sites')}")
            print(f"  Successful: {final_stats.get('successful_sites')}")
            print(f"  Failed: {final_stats.get('failed_sites')}")
            print(f"  Failed Batches: {final_stats.get('failed_batches')}")

            start_time = datetime.fromisoformat(last_run.get('started_at'))
            end_time = datetime.fromisoformat(last_run.get('completed_at'))
            duration = (end_time - start_time).total_seconds()
            print(f"  Duration: {int(duration)}s ({int(duration/60)}m {int(duration%60)}s)")

            break

        current_run = status.get('current_run', {})
        batch_info = current_run.get('batch_info', {})
        progress = current_run.get('progress', {})
        timing = current_run.get('timing', {})

        if (i + 1) % 3 == 0:  # Print every 30 seconds
            print(f"\n[Check {i+1}] Batch {batch_info.get('current_batch')}/{batch_info.get('total_batches')} - {batch_info.get('batch_status')}")
            print(f"  Progress: {progress.get('completed_sites')}/{progress.get('total_sites')} completed, {progress.get('failed_sites')} failed")

            if timing.get('elapsed_seconds'):
                elapsed = timing.get('elapsed_seconds')
                remaining = timing.get('estimated_remaining_seconds', 0)
                print(f"  Time: {int(elapsed/60)}m {int(elapsed%60)}s elapsed, ~{int(remaining/60)}m {int(remaining%60)}s remaining")
else:
    print(f"[ERROR] Failed to start: {result.get('error')}")

print(f"\nTest completed at: {datetime.now().strftime('%H:%M:%S')}")
