#!/usr/bin/env python3
"""
Check GitHub Actions workflow status
"""
import requests
import json
import sys

# GitHub API details
REPO_OWNER = "Tee-David"
REPO_NAME = "realtors_practice"
RUN_ID = "19408262700"

def check_workflow_status():
    """Check the status of a specific workflow run"""

    # API endpoint
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{RUN_ID}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        print("=" * 80)
        print(f"WORKFLOW RUN #{data.get('run_number', 'N/A')}")
        print("=" * 80)
        print(f"Run ID: {data.get('id')}")
        print(f"Name: {data.get('name')}")
        print(f"Status: {data.get('status')}")
        print(f"Conclusion: {data.get('conclusion')}")
        print(f"Created: {data.get('created_at')}")
        print(f"Updated: {data.get('updated_at')}")
        print(f"URL: {data.get('html_url')}")
        print()

        # Get jobs
        jobs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{RUN_ID}/jobs"
        jobs_response = requests.get(jobs_url, timeout=30)
        jobs_data = jobs_response.json()

        print("=" * 80)
        print("JOBS")
        print("=" * 80)

        for job in jobs_data.get('jobs', []):
            print(f"\nJob: {job.get('name')}")
            print(f"  Status: {job.get('status')}")
            print(f"  Conclusion: {job.get('conclusion')}")
            print(f"  Started: {job.get('started_at')}")
            print(f"  Completed: {job.get('completed_at')}")

            # Check steps
            for step in job.get('steps', []):
                status_icon = "✓" if step.get('conclusion') == 'success' else "✗" if step.get('conclusion') == 'failure' else "○"
                print(f"    {status_icon} {step.get('name')}: {step.get('conclusion', 'in_progress')}")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        if data.get('status') == 'completed':
            if data.get('conclusion') == 'success':
                print("Status: SUCCESS - Workflow completed successfully")
            elif data.get('conclusion') == 'failure':
                print("Status: FAILED - Workflow failed")
            elif data.get('conclusion') == 'cancelled':
                print("Status: CANCELLED - Workflow was cancelled")
            elif data.get('conclusion') == 'timed_out':
                print("Status: TIMED OUT - Workflow exceeded time limit")
            else:
                print(f"Status: {data.get('conclusion')}")
        elif data.get('status') == 'in_progress':
            print("Status: IN PROGRESS - Workflow is still running")
        else:
            print(f"Status: {data.get('status')}")

    except requests.exceptions.RequestException as e:
        print(f"Error checking workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_workflow_status()
