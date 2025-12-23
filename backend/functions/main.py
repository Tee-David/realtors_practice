"""
Firebase Cloud Functions entry point for Nigerian Real Estate Scraper API.
Wraps the Flask API server for serverless deployment.
"""
from firebase_functions import https_fn
from firebase_admin import initialize_app

# Initialize Firebase Admin
initialize_app()

# Export the Flask app as a Firebase Function
@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Main API endpoint - routes all requests to the Flask app.

    URL: https://us-central1-realtor-s-practice.cloudfunctions.net/api/

    Examples:
      - GET  /api/health
      - GET  /api/sites
      - POST /api/scrape/start
      - GET  /api/properties
    """
    # Import Flask app lazily to avoid issues during deployment
    import sys
    from pathlib import Path

    # Add parent directory to path to import project modules
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Import Flask app from api_server.py
    from api_server import app

    with app.request_context(req.environ):
        return app.full_dispatch_request()
