import requests
import json
import sys
import io
import time
from datetime import datetime

# Fix Windows Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# GitHub details - prioritize environment variables, fallback to defaults for local use
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', "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")
GITHUB_OWNER = os.getenv('GITHUB_OWNER', "Tee-David")
GITHUB_REPO = os.getenv('GITHUB_REPO', "realtors_practice")

def get_latest_workflow_run():
    """Get the most recent workflow run"""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/scrape-production.yml/runs"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }
    
    response = requests.get(url, headers=headers, params={"per_page": 1})
    
    if response.status_code == 200:
        data = response.json()
        runs = data.get('workflow_runs', [])
        if runs:
            return runs[0]
    return None

def get_workflow_jobs(run_id):
    """Get jobs for a workflow run"""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}/jobs"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('jobs', [])
    return []

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def monitor_workflow():
    """Monitor the latest workflow run"""
    print("=" * 60)
    print("WORKFLOW MONITOR - Production Scraper")
    print("=" * 60)
    print()
    
    run = get_latest_workflow_run()
    
    if not run:
        print("No workflow runs found")
        return
    
    run_id = run['id']
    run_number = run['run_number']
    status = run['status']
    conclusion = run.get('conclusion')
    
    print(f"Run #{run_number} (ID: {run_id})")
    print(f"Status: {status.upper()}")
    if conclusion:
        print(f"Conclusion: {conclusion.upper()}")
    print()
    
    # Calculate timing
    created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
    updated_at = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
    
    if status == 'completed':
        duration = (updated_at - created_at).total_seconds()
        print(f"Duration: {format_duration(duration)}")
    else:
        elapsed = (datetime.now().astimezone() - created_at).total_seconds()
        print(f"Elapsed: {format_duration(elapsed)}")
    
    print()
    print("=" * 60)
    print("JOB STATUS")
    print("=" * 60)
    print()
    
    # Get jobs
    jobs = get_workflow_jobs(run_id)
    
    for job in jobs:
        job_name = job['name']
        job_status = job['status']
        job_conclusion = job.get('conclusion', 'N/A')
        
        # Job timing
        if job.get('started_at'):
            started = datetime.fromisoformat(job['started_at'].replace('Z', '+00:00'))
            if job.get('completed_at'):
                completed = datetime.fromisoformat(job['completed_at'].replace('Z', '+00:00'))
                job_duration = (completed - started).total_seconds()
                timing = f"Duration: {format_duration(job_duration)}"
            else:
                job_elapsed = (datetime.now().astimezone() - started).total_seconds()
                timing = f"Elapsed: {format_duration(job_elapsed)}"
        else:
            timing = "Not started"
        
        # Status symbol
        if job_status == 'completed':
            if job_conclusion == 'success':
                symbol = "[SUCCESS]"
            elif job_conclusion == 'failure':
                symbol = "[FAILED]"
            else:
                symbol = f"[{job_conclusion.upper()}]"
        elif job_status == 'in_progress':
            symbol = "[RUNNING]"
        else:
            symbol = "[QUEUED]"
        
        print(f"{symbol} {job_name}")
        print(f"  Status: {job_status} | {timing}")
        print()
    
    # Overall summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    if status == 'completed':
        if conclusion == 'success':
            print("STATUS: Workflow completed successfully!")
            print()
            print("Next steps:")
            print("  1. Check Firestore for uploaded data")
            print("  2. Download artifacts from GitHub Actions")
            print(f"  3. View results: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}")
        else:
            print(f"STATUS: Workflow completed with {conclusion}")
            print(f"  View logs: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}")
    else:
        print(f"STATUS: Workflow is {status}")
        print(f"  View live: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}")
        print()
        print("  Expected workflow:")
        print("    1. Prepare job (1-2 minutes)")
        print("    2. Scrape jobs - 3 sessions in parallel (60-90 minutes)")
        print("    3. Consolidate job (5-10 minutes)")
        print()
        print("  Total estimated time: 1-2 hours")

if __name__ == "__main__":
    try:
        monitor_workflow()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")
