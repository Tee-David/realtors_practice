"""
Force restart API server - kills all Python processes and starts fresh
"""
import os
import subprocess
import sys
import time

print("=" * 70)
print("Force Restart API Server")
print("=" * 70)

# Step 1: Find and kill Python processes
print("\n[Step 1/3] Finding Python processes on port 5000...")

try:
    # Try to find processes using port 5000
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines:
            if ':5000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    print(f"Found process {pid} using port 5000")
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], timeout=5)
                        print(f"Killed process {pid}")
                    except:
                        print(f"Could not kill process {pid}")
except Exception as e:
    print(f"Could not check port 5000: {e}")
    print("Attempting to kill all python.exe processes...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], timeout=10)
        print("Killed all python.exe processes")
    except Exception as e2:
        print(f"Could not kill processes: {e2}")

print("\nWaiting 3 seconds for cleanup...")
time.sleep(3)

# Step 2: Start fresh server
print("\n[Step 2/3] Starting fresh API server...")
print(f"Working directory: {os.getcwd()}")

# Start server
try:
    process = subprocess.Popen(
        [sys.executable, 'api_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.getcwd(),
        text=True
    )

    print(f"Server started with PID: {process.pid}")
    print("\nWaiting 5 seconds for server to initialize...")
    time.sleep(5)

    # Check if process is still running
    if process.poll() is None:
        print("✅ Server process is running")
    else:
        print("❌ Server process terminated")
        print("\nServer output:")
        stdout, _ = process.communicate(timeout=1)
        print(stdout)
        sys.exit(1)

except Exception as e:
    print(f"❌ Failed to start server: {e}")
    sys.exit(1)

# Step 3: Test endpoints
print("\n[Step 3/3] Testing endpoints...")

import urllib.request
import json

# Test 1: Health check
try:
    print("\n1. Testing health endpoint...")
    response = urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)
    data = json.loads(response.read().decode())
    print(f"   ✅ Health: {data['status']}")
except Exception as e:
    print(f"   ❌ Health check failed: {e}")
    sys.exit(1)

# Test 2: Hot reload endpoint
try:
    print("\n2. Testing hot reload endpoint...")
    req = urllib.request.Request(
        'http://localhost:5000/api/admin/reload-env',
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    data = json.loads(response.read().decode())

    if data.get('success'):
        print(f"   ✅ Hot reload works!")
        print(f"      - GitHub token: {'✅' if data.get('github_token_present') else '❌'}")
        print(f"      - Firebase account: {'✅' if data.get('firebase_account_present') else '❌'}")
        print(f"      - Firestore enabled: {'✅' if data.get('firestore_enabled') else '❌'}")
    else:
        print(f"   ❌ Hot reload failed: {data}")

except urllib.error.HTTPError as e:
    if e.code == 404:
        print(f"   ❌ Hot reload endpoint not found (404)")
        print(f"      Server is still running OLD code!")
        print(f"      You may need to manually restart in a Windows terminal")
    else:
        print(f"   ❌ HTTP Error {e.code}")
except Exception as e:
    print(f"   ❌ Test failed: {e}")

# Test 3: Schedule endpoint
try:
    print("\n3. Testing schedule endpoint...")
    schedule_data = json.dumps({
        "sites": ["npc"],
        "max_pages": 2,
        "scheduled_time": "2025-12-11T20:00:00Z"
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:5000/api/schedule/scrape',
        data=schedule_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    data = json.loads(response.read().decode())

    if data.get('success'):
        print(f"   ✅ Scheduling works! (no timezone errors)")
        print(f"      - Job ID: {data.get('job_id')}")
    else:
        print(f"   ⚠️ Scheduling response: {data}")

except urllib.error.HTTPError as e:
    print(f"   ❌ HTTP Error {e.code}")
    if e.code == 500:
        print(f"      This might be a timezone error (old code)")
except Exception as e:
    print(f"   ⚠️ Test error: {e}")

print("\n" + "=" * 70)
print("Server Status:")
print("=" * 70)
print(f"Process ID: {process.pid}")
print(f"Server URL: http://localhost:5000")
print(f"\nServer is running in this terminal window.")
print(f"Press Ctrl+C to stop the server.")
print("=" * 70)

# Keep the server running
try:
    process.wait()
except KeyboardInterrupt:
    print("\n\nShutting down server...")
    process.terminate()
    process.wait(timeout=5)
    print("Server stopped.")
