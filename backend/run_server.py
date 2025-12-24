"""Launcher script for API server with environment setup"""
import os
import sys
import importlib

# Ensure we're in the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Set environment variable
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

# Clear any cached modules to force reload
modules_to_clear = [m for m in sys.modules.keys() if 'api_server' in m or 'firestore_queries' in m]
for mod in modules_to_clear:
    print(f"Clearing cached module: {mod}")
    del sys.modules[mod]

# Now import the app - this should load backend/api_server.py
import api_server
importlib.reload(api_server)

if __name__ == '__main__':
    print("="*50)
    print("STARTING FRESH API SERVER - VERSION 13:07")
    print("Firebase credentials:", os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
    print(f"api_server file: {api_server.__file__}")
    print("="*50)
    api_server.app.run(host='0.0.0.0', port=5000, debug=False)
