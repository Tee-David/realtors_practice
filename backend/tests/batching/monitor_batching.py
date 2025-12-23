"""
Simple monitoring script for batching progress
"""
import time
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def monitor_progress():
    """Monitor the current scraping progress"""

    print("="*80)
    print("Batching System Monitor")
    print("="*80)
    print(f"Started monitoring at: {datetime.now().strftime('%H:%M:%S')}\n")

    last_batch = 0
    check_count = 0

    while True:
        time.sleep(10)  # Check every 10 seconds
        check_count += 1

        try:
            response = requests.get(f"{BASE_URL}/scrape/status")
            status = response.json()

            if not status.get('is_running'):
                print("\n[DONE] Scraping completed!")

                last_run = status.get('last_run', {})
                if last_run:
                    print("\nFinal Results:")
                    print(f"  Run ID: {last_run.get('run_id')}")
                    print(f"  Success: {last_run.get('success')}")

                    final_stats = last_run.get('final_stats', {})
                    print(f"  Total Sites: {final_stats.get('total_sites')}")
                    print(f"  Successful: {final_stats.get('successful_sites')}")
                    print(f"  Failed: {final_stats.get('failed_sites')}")
                    print(f"  Failed Batches: {final_stats.get('failed_batches')}")

                    if final_stats.get('total_sites'):
                        success_rate = (final_stats.get('successful_sites', 0) /
                                      final_stats.get('total_sites')) * 100
                        print(f"  Success Rate: {success_rate:.1f}%")

                    start_time = datetime.fromisoformat(last_run.get('started_at'))
                    end_time = datetime.fromisoformat(last_run.get('completed_at'))
                    duration = (end_time - start_time).total_seconds()
                    print(f"  Duration: {int(duration/60)}m {int(duration%60)}s")

                break

            current_run = status.get('current_run', {})
            batch_info = current_run.get('batch_info', {})
            progress = current_run.get('progress', {})
            timing = current_run.get('timing', {})

            current_batch = batch_info.get('current_batch', 0)

            # Detect batch transitions
            if current_batch != last_batch and current_batch > 0:
                print(f"\n>>> BATCH TRANSITION: {last_batch} -> {current_batch} <<<")
                last_batch = current_batch

            # Print status every check
            print(f"\n[{check_count}] {datetime.now().strftime('%H:%M:%S')}")
            print(f"  Batch: {current_batch}/{batch_info.get('total_batches')} ({batch_info.get('batch_status')})")
            print(f"  Progress: {progress.get('completed_sites')}/{progress.get('total_sites')} completed, " +
                  f"{progress.get('in_progress_sites')} in progress, " +
                  f"{progress.get('pending_sites')} pending")

            # Progress bar
            if progress.get('total_sites'):
                completed = progress.get('completed_sites', 0)
                total = progress.get('total_sites')
                percent = (completed / total) * 100
                bar_length = 40
                filled = int((completed / total) * bar_length)
                bar = '#' * filled + '-' * (bar_length - filled)
                print(f"  [{bar}] {percent:.0f}%")

            if timing.get('elapsed_seconds'):
                elapsed = timing.get('elapsed_seconds')
                remaining = timing.get('estimated_remaining_seconds', 0)
                print(f"  Time: {int(elapsed/60)}m {int(elapsed%60)}s elapsed, " +
                      f"~{int(remaining/60)}m {int(remaining%60)}s remaining")

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            break

if __name__ == "__main__":
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            monitor_progress()
        else:
            print(f"[ERROR] API returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to API: {e}")
        print("\nPlease start the API server first: python api_server.py")
