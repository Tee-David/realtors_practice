#!/usr/bin/env python3
"""
Trigger GitHub Actions workflow via API
"""
import requests
import sys
import os

REPO_OWNER = "Tee-David"
REPO_NAME = "realtors_practice"
WORKFLOW_FILE = "scrape-production.yml"

# Get GitHub token from git config or environment
def get_github_token():
    """Get GitHub Personal Access Token"""
    # Try environment variable
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    if token:
        return token

    # Try git config
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'config', '--get', 'github.token'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass

    return None

def trigger_workflow(max_pages=20, geocode=1):
    """Trigger the production scrape workflow"""

    token = get_github_token()
    if not token:
        print("ERROR: GitHub token not found!")
        print("\nPlease set token via:")
        print("  export GITHUB_TOKEN=your_token")
        print("  or")
        print("  git config --global github.token your_token")
        sys.exit(1)

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    data = {
        "ref": "main",
        "inputs": {
            "max_pages": str(max_pages),
            "geocode": str(geocode)
        }
    }

    print(f"Triggering workflow: {WORKFLOW_FILE}")
    print(f"  Max pages: {max_pages}")
    print(f"  Geocoding: {'enabled' if geocode else 'disabled'}")
    print(f"  Repository: {REPO_OWNER}/{REPO_NAME}")
    print()

    response = requests.post(url, headers=headers, json=data, timeout=30)

    if response.status_code == 204:
        print("SUCCESS: Workflow triggered!")
        print(f"\nView progress at:")
        print(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
        print()
        print("The workflow will:")
        print("  1. Calculate intelligent batching strategy")
        print("  2. Scrape all 51 enabled sites")
        print("  3. Upload to Firestore in real-time")
        print("  4. Create master workbook")
        print()
        return True
    else:
        print(f"ERROR: Failed to trigger workflow")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Trigger GitHub Actions scrape workflow')
    parser.add_argument('--max-pages', type=int, default=20, help='Max pages per site')
    parser.add_argument('--no-geocode', action='store_true', help='Disable geocoding')

    args = parser.parse_args()

    success = trigger_workflow(
        max_pages=args.max_pages,
        geocode=0 if args.no_geocode else 1
    )

    sys.exit(0 if success else 1)
