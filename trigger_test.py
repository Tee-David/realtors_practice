"""
Trigger GitHub Actions workflow for testing Firestore upload.

This script will trigger the test-quick-scrape workflow via GitHub API.
"""

import os
import sys
import requests
import json

# GitHub credentials (set these as environment variables)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_OWNER = 'Tee-David'
GITHUB_REPO = 'realtors_practice'

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable not set")
    print("Set it with: set GITHUB_TOKEN=your_personal_access_token")
    sys.exit(1)

# Trigger workflow
url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/test-quick-scrape.yml/dispatches'

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}

payload = {
    'ref': 'main',
    'inputs': {
        'site': 'npc',
        'pages': '5'
    }
}

print("Triggering test-quick-scrape workflow...")
print(f"Site: npc")
print(f"Pages: 5")
print()

response = requests.post(url, headers=headers, json=payload, timeout=10)

if response.status_code == 204:
    print("✓ Workflow triggered successfully!")
    print()
    print("Check status at:")
    print(f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions")
    print()
    print("Wait 3-5 minutes, then check:")
    print("1. Workflow logs for: '[SUCCESS] Uploaded X listings to Firestore'")
    print("2. Firestore console: https://console.firebase.google.com/project/realtor-s-practice/firestore")
else:
    print(f"✗ Failed to trigger workflow: {response.status_code}")
    print(f"Response: {response.text}")
    sys.exit(1)
