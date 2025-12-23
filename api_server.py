"""
Root-level shim to maintain compatibility with Render deployment.
Imports the Flask app from backend/functions/api_server.py
"""

import sys
import os

# Add backend directory to Python path so imports work correctly
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Change to backend directory for file operations
os.chdir(backend_path)

# Now import the app (using the backend's import structure)
from functions.api_server import app

__all__ = ['app']
