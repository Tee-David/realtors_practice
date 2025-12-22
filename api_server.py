"""
Shim module to maintain compatibility with Render's start command.
Imports the actual Flask app from functions/api_server.py
"""

from functions.api_server import app

__all__ = ['app']
