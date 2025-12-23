"""
Test pause/resume functionality for scraping
"""
import time
import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)

def test_pause_resume():
    """Test pause and resume functionality"""

    print_section("Testing Pause/Resume Feature")

    # Check if there's a scraping job running
    print("\nStep 1: Checking current status...")
    status_response = requests.get(f"{BASE_URL}/scrape/status")
    status = status_response.json()

    if not status.get('is_running'):
        print("[INFO] No scraping job is currently running")
        print("\nTo test pause/resume, first start a scraping job:")
        print("  curl -X POST http://localhost:5000/api/scrape/start \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"sites\": [\"cwlagos\", \"npc\", \"propertypro\"], \"max_pages\": 2}'")
        return

    print(f"[OK] Scraping job is running")

    current_run = status.get('current_run', {})
    batch_info = current_run.get('batch_info', {})

    print(f"\nCurrent Status:")
    print(f"  Batch: {batch_info.get('current_batch')}/{batch_info.get('total_batches')}")
    print(f"  Paused: {current_run.get('paused', False)}")

    # Test 1: Pause
    if not current_run.get('paused', False):
        print("\n" + "="*80)
        print("Test 1: Pause Scraping")
        print("="*80)

        print("\nSending pause request...")
        pause_response = requests.post(f"{BASE_URL}/scrape/pause")
        pause_result = pause_response.json()

        if pause_result.get('success'):
            print(f"[OK] {pause_result.get('message')}")
            print(f"  Will pause after batch {pause_result.get('current_batch')}/{pause_result.get('total_batches')}")
        else:
            print(f"[ERROR] {pause_result.get('error')}")
            return

        # Wait for pause to take effect
        print("\nWaiting for pause to take effect...")
        time.sleep(10)

        # Check status
        status_response = requests.get(f"{BASE_URL}/scrape/status")
        status = status_response.json()
        current_run = status.get('current_run', {})

        if current_run.get('paused'):
            print("[OK] Scraper is now PAUSED")
            print(f"  Paused at: {current_run.get('paused_at')}")
        else:
            print("[INFO] Scraper is still completing current batch...")

    # Test 2: Resume
    if current_run.get('paused'):
        print("\n" + "="*80)
        print("Test 2: Resume Scraping")
        print("="*80)

        print("\nSending resume request...")
        resume_response = requests.post(f"{BASE_URL}/scrape/resume")
        resume_result = resume_response.json()

        if resume_result.get('success'):
            print(f"[OK] {resume_result.get('message')}")
            print(f"  Will continue from batch {resume_result.get('current_batch')}/{resume_result.get('total_batches')}")
        else:
            print(f"[ERROR] {resume_result.get('error')}")
            return

        # Check status
        time.sleep(3)
        status_response = requests.get(f"{BASE_URL}/scrape/status")
        status = status_response.json()
        current_run = status.get('current_run', {})

        if not current_run.get('paused'):
            print("[OK] Scraper is now RUNNING")
            print(f"  Resumed at: {current_run.get('resumed_at')}")
        else:
            print("[ERROR] Scraper is still paused")

    print("\n" + "="*80)
    print("Pause/Resume Test Complete")
    print("="*80)

def show_endpoints():
    """Show available pause/resume endpoints"""
    print_section("Pause/Resume API Endpoints")

    print("\n1. Pause Scraping:")
    print("   POST /api/scrape/pause")
    print("   - Pauses after current batch completes")
    print("   - Returns: current_batch, total_batches, message")
    print("\n   Example:")
    print("     curl -X POST http://localhost:5000/api/scrape/pause")

    print("\n2. Resume Scraping:")
    print("   POST /api/scrape/resume")
    print("   - Resumes from next batch")
    print("   - Returns: current_batch, total_batches, message")
    print("\n   Example:")
    print("     curl -X POST http://localhost:5000/api/scrape/resume")

    print("\n3. Check Status (includes pause status):")
    print("   GET /api/scrape/status")
    print("   - Returns: is_running, paused, batch_info, progress")
    print("\n   Example:")
    print("     curl http://localhost:5000/api/scrape/status")

    print("\n4. Stop Scraping:")
    print("   POST /api/scrape/stop")
    print("   - Stops scraping immediately")
    print("\n   Example:")
    print("     curl -X POST http://localhost:5000/api/scrape/stop")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_endpoints()
    else:
        try:
            # Test connection
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("[OK] API server is running")
                test_pause_resume()
            else:
                print(f"[ERROR] API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not connect to API: {e}")
            print("\nPlease start the API server first:")
            print("  python api_server.py")
