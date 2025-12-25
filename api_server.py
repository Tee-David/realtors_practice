"""
Root-level shim to maintain compatibility with Render deployment.
Imports the Flask app from backend/api_server.py
"""

import sys
import os

# Add backend directory to Python path so imports work correctly
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Change to backend directory for file operations
os.chdir(backend_path)

# Now import the app from backend/api_server.py
# Import as a module to avoid circular import
import importlib.util
spec = importlib.util.spec_from_file_location("backend_api_server", os.path.join(backend_path, "api_server.py"))
backend_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_module)
app = backend_module.app

__all__ = ['app']
