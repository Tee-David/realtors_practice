import subprocess
import time

print("Killing all Python processes...")
try:
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], timeout=10, capture_output=True)
except:
    pass

print("Waiting 3 seconds...")
time.sleep(3)

print("Starting API server...")
subprocess.Popen(['python', 'api_server.py'])

print("Waiting 5 seconds for server to start...")
time.sleep(5)

# Test endpoints
import urllib.request
import json

try:
    print("\nTesting hot reload endpoint...")
    req = urllib.request.Request('http://localhost:5000/api/admin/reload-env', method='POST')
    response = urllib.request.urlopen(req, timeout=5)
    data = json.loads(response.read().decode())
    print(f"SUCCESS: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

try:
    print("\nTesting schedule endpoint...")
    schedule_data = json.dumps({"sites": ["npc"], "max_pages": 2, "scheduled_time": "2025-12-11T20:00:00Z"}).encode('utf-8')
    req = urllib.request.Request('http://localhost:5000/api/schedule/scrape', data=schedule_data, headers={'Content-Type': 'application/json'}, method='POST')
    response = urllib.request.urlopen(req, timeout=5)
    data = json.loads(response.read().decode())
    print(f"SUCCESS: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

print("\nServer is running in background. PID should be visible in Task Manager.")
