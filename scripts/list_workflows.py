#!/usr/bin/env python3
"""
List recent GitHub Actions workflow runs
"""
import requests
import json
from datetime import datetime

# GitHub API details
REPO_OWNER = "Tee-David"
REPO_NAME = "realtors_practice"

def list_recent_workflows():
    """List recent workflow runs"""

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"

    try:
        response = requests.get(url, params={"per_page": 10}, timeout=30)
        response.raise_for_status()

        data = response.json()

        print("=" * 100)
        print("RECENT WORKFLOW RUNS")
        print("=" * 100)

        if not data.get('workflow_runs'):
            print("No workflow runs found")
            return

        for run in data['workflow_runs']:
            created = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            updated = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))

            status_emoji = {
                'completed': '✓' if run.get('conclusion') == 'success' else '✗',
                'in_progress': '○',
                'queued': '⋯'
            }.get(run['status'], '?')

            print(f"\n{status_emoji} Run #{run['run_number']}: {run['name']}")
            print(f"   ID: {run['id']}")
            print(f"   Status: {run['status']} - {run.get('conclusion', 'N/A')}")
            print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Branch: {run['head_branch']}")
            print(f"   Event: {run['event']}")
            print(f"   URL: {run['html_url']}")

        print("\n" + "=" * 100)

    except requests.exceptions.RequestException as e:
        print(f"Error listing workflows: {e}")

if __name__ == "__main__":
    list_recent_workflows()
