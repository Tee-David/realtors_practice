"""
Flask REST API Server for Real Estate Scraper
Provides endpoints for frontend to manage scraping, configure sites, and query data.
"""
import os
import sys
import json
import signal
import threading
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (override system env vars)
load_dotenv(override=True)

# Import core modules
from core.config_loader import load_config, ConfigValidationError
from core.url_validator import URLValidator
from core.location_filter import LocationFilter, get_location_filter
from core.query_engine import PropertyQuery
from core.rate_limiter import get_rate_limiter
from core.price_history import get_price_history_tracker
from core.natural_language_search import get_nl_search_parser
from core.duplicate_detector import get_duplicate_detector
from core.quality_scorer import get_quality_scorer
from core.saved_searches import get_saved_search_manager
from core.incremental_scraper import get_incremental_scraper
from core.email_notifier import EmailNotifier
from api.helpers.data_reader import DataReader
from api.helpers.log_parser import LogParser
from api.helpers.config_manager import ConfigManager
from api.helpers.scraper_manager import ScraperManager
from api.helpers.stats_generator import StatsGenerator
from api.helpers.health_monitor import get_health_monitor

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize helper instances
data_reader = DataReader()
log_parser = LogParser()
config_manager = ConfigManager()
scraper_manager = ScraperManager()
stats_generator = StatsGenerator()

# Initialize feature instances
url_validator = URLValidator()
location_filter = get_location_filter()  # Singleton instance
rate_limiter = get_rate_limiter()  # Singleton instance
price_tracker = get_price_history_tracker()
nl_parser = get_nl_search_parser()
duplicate_detector = get_duplicate_detector()
quality_scorer = get_quality_scorer()
saved_search_manager = get_saved_search_manager()
health_monitor = get_health_monitor()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/admin/reload-env', methods=['POST'])
def reload_env():
    """
    Reload environment variables from .env file without restarting server.

    This endpoint allows you to update credentials (GitHub token, Firebase credentials, etc.)
    by editing the .env file and then calling this endpoint to reload the values.

    **Why This is Important:**
    - No server downtime when updating credentials
    - GitHub tokens expire periodically and need rotation
    - Firebase credentials may need updates for security
    - Instant application of new environment values

    **Usage:**
    1. Edit .env file with new credentials
    2. POST to this endpoint
    3. New values are immediately active

    **Security:** Consider adding authentication to this endpoint in production.

    Returns:
        {
            "success": true,
            "message": "Environment variables reloaded successfully",
            "github_token_present": true,
            "firebase_account_present": true,
            "firestore_enabled": true,
            "timestamp": "2025-12-11T13:30:00Z"
        }
    """
    try:
        from dotenv import load_dotenv

        # Force reload environment variables from .env file
        load_dotenv(override=True)

        # Verify critical variables are loaded
        github_token = os.getenv('GITHUB_TOKEN')
        firebase_account = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
        firestore_enabled = os.getenv('FIRESTORE_ENABLED', '0')

        logger.info("Environment variables reloaded successfully")

        return jsonify({
            'success': True,
            'message': 'Environment variables reloaded successfully',
            'github_token_present': bool(github_token and len(github_token) > 0),
            'firebase_account_present': bool(firebase_account and len(firebase_account) > 0),
            'firebase_credentials_present': bool(firebase_credentials and len(firebase_credentials) > 0),
            'firestore_enabled': firestore_enabled == '1',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error reloading environment variables: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to reload environment variables'
        }), 500


# ============================================================================
# SCRAPING MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/scrape/start', methods=['POST'])
def start_scrape():
    """
    Start a scraping run
    Body: {
        "sites": ["npc", "propertypro"],  # Optional, if empty scrape all enabled
        "max_pages": 20,                   # Optional override
        "geocoding": true                  # Optional override
    }
    """
    try:
        data = request.get_json() or {}
        sites = data.get('sites', [])
        max_pages = data.get('max_pages')
        geocoding = data.get('geocoding')

        result = scraper_manager.start_scrape(
            sites=sites,
            max_pages=max_pages,
            geocoding=geocoding
        )

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error starting scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape/status', methods=['GET'])
def scrape_status():
    """Get current scraping status"""
    try:
        status = scraper_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting scrape status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape/stop', methods=['POST'])
def stop_scrape():
    """Stop current scraping run"""
    try:
        result = scraper_manager.stop_scrape()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error stopping scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape/pause', methods=['POST'])
def pause_scrape():
    """Pause current scraping run (pauses after current batch completes)"""
    try:
        result = scraper_manager.pause_scrape()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error pausing scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape/resume', methods=['POST'])
def resume_scrape():
    """Resume paused scraping run"""
    try:
        result = scraper_manager.resume_scrape()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error resuming scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape/history', methods=['GET'])
def scrape_history():
    """Get scraping history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = scraper_manager.get_history(limit=limit)
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"Error getting scrape history: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SITE CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/api/sites', methods=['GET'])
def list_sites():
    """List all sites with their configurations"""
    try:
        sites = config_manager.list_sites()
        return jsonify(sites), 200
    except Exception as e:
        logger.error(f"Error listing sites: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites/<site_key>', methods=['GET'])
def get_site(site_key):
    """Get configuration for specific site"""
    try:
        site = config_manager.get_site(site_key)
        if site is None:
            return jsonify({'error': 'Site not found'}), 404
        return jsonify(site), 200
    except Exception as e:
        logger.error(f"Error getting site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites', methods=['POST'])
def add_site():
    """
    Add new site
    Body: {
        "site_key": "newsite",
        "name": "New Site",
        "url": "https://newsite.com",
        "enabled": true,
        "parser": "specials",
        "selectors": {...}
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = config_manager.add_site(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding site: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites/<site_key>', methods=['PUT'])
def update_site(site_key):
    """
    Update site configuration
    Body: {
        "name": "Updated Name",
        "url": "https://updated-url.com",
        ...
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = config_manager.update_site(site_key, data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites/<site_key>', methods=['DELETE'])
def delete_site(site_key):
    """Delete site"""
    try:
        result = config_manager.delete_site(site_key)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites/<site_key>/toggle', methods=['PATCH'])
def toggle_site(site_key):
    """Enable or disable site"""
    try:
        result = config_manager.toggle_site(site_key)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error toggling site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LOGS & ERRORS ENDPOINTS
# ============================================================================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Get recent logs
    Query params:
        - limit: number of lines (default 100)
        - level: filter by level (INFO, WARNING, ERROR)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        level = request.args.get('level', type=str)

        logs = log_parser.get_logs(limit=limit, level=level)
        return jsonify(logs), 200
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/errors', methods=['GET'])
def get_errors():
    """Get error logs only"""
    try:
        limit = request.args.get('limit', 50, type=int)
        errors = log_parser.get_errors(limit=limit)
        return jsonify(errors), 200
    except Exception as e:
        logger.error(f"Error getting error logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/site/<site_key>', methods=['GET'])
def get_site_logs(site_key):
    """Get site-specific logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = log_parser.get_site_logs(site_key, limit=limit)
        return jsonify(logs), 200
    except Exception as e:
        logger.error(f"Error getting logs for site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DATA QUERY ENDPOINTS
# ============================================================================

@app.route('/api/data/sites', methods=['GET'])
def list_data_files():
    """List all available data files"""
    try:
        files = data_reader.list_available_data()
        return jsonify(files), 200
    except Exception as e:
        logger.error(f"Error listing data files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/sites/<site_key>', methods=['GET'])
def get_site_data(site_key):
    """
    Get data for specific site
    Query params:
        - limit: number of records (default 100)
        - offset: pagination offset (default 0)
        - source: 'raw' or 'cleaned' (default 'cleaned')
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        source = request.args.get('source', 'cleaned', type=str)

        data = data_reader.get_site_data(
            site_key,
            limit=limit,
            offset=offset,
            source=source
        )
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({'error': f'No data found for site {site_key}'}), 404
    except Exception as e:
        logger.error(f"Error getting data for site {site_key}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/master', methods=['GET'])
def get_master_data():
    """
    Get consolidated master workbook data
    Query params:
        - limit: number of records per site (default 100)
        - site: filter by specific site (optional)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        site_filter = request.args.get('site', type=str)

        data = data_reader.get_master_data(
            limit=limit,
            site_filter=site_filter
        )
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting master data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/search', methods=['GET'])
def search_data():
    """
    Search across all data
    Query params:
        - query: search term
        - fields: comma-separated fields to search (default: title,location)
        - limit: max results (default 50)
    """
    try:
        query = request.args.get('query', type=str)
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400

        fields = request.args.get('fields', 'title,location').split(',')
        limit = request.args.get('limit', 50, type=int)

        results = data_reader.search_data(
            query=query,
            fields=fields,
            limit=limit
        )
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error searching data: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/stats/overview', methods=['GET'])
def get_overview_stats():
    """Get overall statistics"""
    try:
        stats = stats_generator.get_overview()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/sites', methods=['GET'])
def get_site_stats():
    """Get per-site statistics"""
    try:
        stats = stats_generator.get_site_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting site stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/trends', methods=['GET'])
def get_trends():
    """
    Get historical trends
    Query params:
        - days: number of days (default 7)
    """
    try:
        days = request.args.get('days', 7, type=int)
        trends = stats_generator.get_trends(days=days)
        return jsonify(trends), 200
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# URL VALIDATION ENDPOINTS
# ============================================================================

@app.route('/api/validate/url', methods=['POST'])
def validate_url():
    """
    Validate a URL
    Body: {
        "url": "https://example.com/page"
    }
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'valid': False,
                'error': 'URL is required'
            }), 400

        url = data['url']
        is_valid = url_validator.is_valid(url)
        result = {
            'valid': is_valid,
            'url': url
        }

        if not is_valid:
            result['error'] = 'Invalid URL (blocked or non-HTTP protocol)'

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate/urls', methods=['POST'])
def validate_urls():
    """
    Validate multiple URLs
    Body: {
        "urls": ["url1", "url2", ...]
    }
    """
    try:
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({'error': 'URLs array is required'}), 400

        urls = data['urls']
        results = url_validator.validate_batch(urls)

        return jsonify({
            'results': results,
            'summary': {
                'total': len(results),
                'valid': sum(1 for r in results if r['valid']),
                'invalid': sum(1 for r in results if not r['valid'])
            }
        }), 200
    except Exception as e:
        logger.error(f"Error validating URLs: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LOCATION FILTER ENDPOINTS
# ============================================================================

@app.route('/api/filter/location', methods=['POST'])
def filter_location():
    """
    Check if a location matches target cities
    Body: {
        "location": "Lekki, Lagos",
        "coordinates": {"lat": 6.4281, "lng": 3.4219}  # Optional
    }
    """
    try:
        data = request.get_json()
        if not data or 'location' not in data:
            return jsonify({'error': 'Location is required'}), 400

        location = data['location']
        coordinates = data.get('coordinates')

        is_match = location_filter.is_target_location(location, coordinates)

        return jsonify({
            'location': location,
            'matches': is_match,
            'target_locations': location_filter.target_locations
        }), 200
    except Exception as e:
        logger.error(f"Error filtering location: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/filter/stats', methods=['GET'])
def get_filter_stats():
    """Get location filter statistics"""
    try:
        stats = location_filter.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting filter stats: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LOCATION CONFIG ENDPOINTS
# ============================================================================

@app.route('/api/config/locations', methods=['GET'])
def get_target_locations():
    """Get current target locations"""
    try:
        return jsonify({
            'target_locations': location_filter.target_locations,
            'strict_mode': location_filter.strict_mode,
            'available_cities': list(location_filter.CITY_DATA.keys())
        }), 200
    except Exception as e:
        logger.error(f"Error getting target locations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/locations', methods=['PUT'])
def update_target_locations():
    """
    Update target locations
    Body: {
        "target_locations": ["Lagos", "Ogun"],
        "strict_mode": true  # Optional
    }
    """
    try:
        data = request.get_json()
        if not data or 'target_locations' not in data:
            return jsonify({'error': 'target_locations array is required'}), 400

        target_locations = data['target_locations']
        strict_mode = data.get('strict_mode', False)

        # Create new filter instance with new locations
        global location_filter
        location_filter = LocationFilter(
            target_locations=target_locations,
            strict_mode=strict_mode
        )

        return jsonify({
            'success': True,
            'target_locations': location_filter.target_locations,
            'strict_mode': location_filter.strict_mode
        }), 200
    except Exception as e:
        logger.error(f"Error updating target locations: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# QUERY ENGINE ENDPOINTS
# ============================================================================

@app.route('/api/query', methods=['POST'])
def query_properties():
    """
    Query properties with filters
    Body: {
        "file": "exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx",  # Optional
        "filters": {
            "price_min": 5000000,
            "price_max": 50000000,
            "bedrooms": 3,
            "location": "Lekki",
            "property_type": "Flat"
        },
        "search": "luxury apartment",  # Optional text search
        "sort_by": "price",            # Optional
        "sort_desc": false,            # Optional
        "limit": 50,                   # Optional
        "offset": 0                    # Optional
    }
    """
    try:
        data = request.get_json() or {}
        file_path = data.get('file', 'exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx')

        # Check if file exists
        if not Path(file_path).exists():
            return jsonify({
                'error': f'File not found: {file_path}',
                'hint': 'Run scraper first to generate data'
            }), 404

        # Load data
        if file_path.endswith('.csv'):
            query = PropertyQuery.from_csv(file_path)
        else:
            query = PropertyQuery.from_excel(file_path)

        # Apply filters
        filters = data.get('filters', {})
        if filters:
            query.filter(**filters)

        # Apply search
        if 'search' in data:
            query.search(data['search'])

        # Apply sorting
        if 'sort_by' in data:
            query.sort_by(
                data['sort_by'],
                ascending=not data.get('sort_desc', False)
            )

        # Apply pagination
        if 'limit' in data:
            query.limit(data['limit'], offset=data.get('offset', 0))

        # Execute query
        results = query.execute()

        return jsonify({
            'results': results,
            'count': len(results),
            'filters_applied': filters,
            'file': file_path
        }), 200
    except Exception as e:
        logger.error(f"Error querying properties: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/summary', methods=['POST'])
def query_summary():
    """
    Get summary statistics for a query
    Body: same as /api/query but returns summary instead of results
    """
    try:
        data = request.get_json() or {}
        file_path = data.get('file', 'exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx')

        # Check if file exists
        if not Path(file_path).exists():
            return jsonify({
                'error': f'File not found: {file_path}'
            }), 404

        # Load data
        if file_path.endswith('.csv'):
            query = PropertyQuery.from_csv(file_path)
        else:
            query = PropertyQuery.from_excel(file_path)

        # Apply filters
        filters = data.get('filters', {})
        if filters:
            query.filter(**filters)

        # Apply search
        if 'search' in data:
            query.search(data['search'])

        # Get summary
        summary = query.get_summary()

        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error getting query summary: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# RATE LIMITER ENDPOINTS
# ============================================================================

@app.route('/api/rate-limit/status', methods=['GET'])
def get_rate_limit_status():
    """Get rate limiter statistics"""
    try:
        stats = rate_limiter.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate-limit/check', methods=['POST'])
def check_rate_limit():
    """
    Check if URL can be fetched (robots.txt check)
    Body: {
        "url": "https://example.com/page",
        "user_agent": "CustomBot/1.0"  # Optional
    }
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400

        url = data['url']
        user_agent = data.get('user_agent')

        can_fetch = rate_limiter.can_fetch(url, user_agent)
        domain = rate_limiter.get_domain(url)
        delay = rate_limiter.get_delay_for_domain(domain)

        return jsonify({
            'url': url,
            'can_fetch': can_fetch,
            'domain': domain,
            'delay_seconds': delay
        }), 200
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PRICE HISTORY ENDPOINTS
# ============================================================================

@app.route('/api/price-history/<property_id>', methods=['GET'])
def get_price_history(property_id):
    """Get price history for a specific property"""
    try:
        history = price_tracker.get_price_history(property_id)
        return jsonify({
            'property_id': property_id,
            'history': history,
            'total_entries': len(history)
        }), 200
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/price-drops', methods=['GET'])
def get_price_drops():
    """
    Get properties with recent price drops
    Query params: min_drop_pct (default: 5.0), days (default: 30)
    """
    try:
        min_drop_pct = float(request.args.get('min_drop_pct', 5.0))
        days = int(request.args.get('days', 30))

        drops = price_tracker.get_price_drops(min_drop_pct=min_drop_pct, days=days)

        return jsonify({
            'price_drops': drops,
            'total': len(drops),
            'min_drop_pct': min_drop_pct,
            'period_days': days
        }), 200
    except Exception as e:
        logger.error(f"Error getting price drops: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stale-listings', methods=['GET'])
def get_stale_listings():
    """
    Get stale listings (listed for long time without price change)
    Query params: min_days (default: 90)
    """
    try:
        min_days = int(request.args.get('min_days', 90))

        stale = price_tracker.get_stale_listings(min_days=min_days)

        return jsonify({
            'stale_listings': stale,
            'total': len(stale),
            'min_days': min_days
        }), 200
    except Exception as e:
        logger.error(f"Error getting stale listings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-trends', methods=['GET'])
def get_market_trends():
    """
    Get market price trends
    Query params: days (default: 30)
    """
    try:
        days = int(request.args.get('days', 30))

        trends = price_tracker.get_market_trends(days=days)

        return jsonify(trends), 200
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# NATURAL LANGUAGE SEARCH ENDPOINTS
# ============================================================================

@app.route('/api/search/natural', methods=['POST'])
def natural_language_search():
    """
    Natural language search
    Body: { "query": "3 bedroom flat in Lekki under 30 million" }
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data['query']

        # Parse query
        parsed = nl_parser.parse_query(query)

        # Get filters for query engine
        filters = nl_parser.generate_query_engine_filters(parsed)

        return jsonify({
            'original_query': query,
            'parsed': parsed,
            'filters': filters
        }), 200
    except Exception as e:
        logger.error(f"Error in natural language search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """
    Get search suggestions
    Query param: q (partial query)
    """
    try:
        partial_query = request.args.get('q', '')

        suggestions = nl_parser.get_suggestions(partial_query)

        return jsonify({
            'query': partial_query,
            'suggestions': suggestions
        }), 200
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SAVED SEARCHES ENDPOINTS
# ============================================================================

@app.route('/api/searches', methods=['GET', 'POST'])
def manage_searches():
    """
    GET: List all searches (optionally filter by user_id)
    POST: Create new saved search
    """
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            searches = saved_search_manager.list_searches(user_id=user_id)

            return jsonify({
                'searches': searches,
                'total': len(searches)
            }), 200

        elif request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body required'}), 400

            user_id = data.get('user_id')
            name = data.get('name')
            criteria = data.get('criteria')
            alert_frequency = data.get('alert_frequency', 'daily')

            if not all([user_id, name, criteria]):
                return jsonify({'error': 'user_id, name, and criteria are required'}), 400

            search_id = saved_search_manager.create_search(
                user_id=user_id,
                name=name,
                criteria=criteria,
                alert_frequency=alert_frequency
            )

            return jsonify({
                'success': True,
                'search_id': search_id
            }), 201

    except Exception as e:
        logger.error(f"Error managing searches: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<search_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_search(search_id):
    """
    GET: Get specific search
    PUT: Update search
    DELETE: Delete search
    """
    try:
        if request.method == 'GET':
            search = saved_search_manager.get_search(search_id)
            if not search:
                return jsonify({'error': 'Search not found'}), 404

            return jsonify(search), 200

        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body required'}), 400

            success = saved_search_manager.update_search(search_id, data)
            if not success:
                return jsonify({'error': 'Search not found'}), 404

            return jsonify({'success': True}), 200

        elif request.method == 'DELETE':
            success = saved_search_manager.delete_search(search_id)
            if not success:
                return jsonify({'error': 'Search not found'}), 404

            return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error managing search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<search_id>/stats', methods=['GET'])
def get_search_stats(search_id):
    """Get statistics for a saved search"""
    try:
        stats = saved_search_manager.get_search_stats(search_id)
        if not stats:
            return jsonify({'error': 'Search not found'}), 404

        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HEALTH MONITORING ENDPOINTS
# ============================================================================

@app.route('/api/health/overall', methods=['GET'])
def get_overall_health():
    """Get overall system health"""
    try:
        health = health_monitor.get_overall_health()
        return jsonify(health), 200
    except Exception as e:
        logger.error(f"Error getting overall health: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health/sites/<site_key>', methods=['GET'])
def get_site_health(site_key):
    """Get health for specific site"""
    try:
        days = int(request.args.get('days', 7))
        health = health_monitor.get_site_health(site_key, days=days)

        return jsonify(health), 200
    except Exception as e:
        logger.error(f"Error getting site health: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health/alerts', methods=['GET'])
def get_health_alerts():
    """Get active health alerts"""
    try:
        alerts = health_monitor.get_alerts()

        return jsonify({
            'alerts': alerts,
            'total': len(alerts)
        }), 200
    except Exception as e:
        logger.error(f"Error getting health alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing sites"""
    try:
        limit = int(request.args.get('limit', 10))
        performers = health_monitor.get_top_performers(limit=limit)

        return jsonify({
            'performers': performers,
            'total': len(performers)
        }), 200
    except Exception as e:
        logger.error(f"Error getting top performers: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DUPLICATE DETECTION ENDPOINTS
# ============================================================================

@app.route('/api/duplicates/detect', methods=['POST'])
def detect_duplicates():
    """
    Detect duplicates in provided listings
    Body: { "listings": [...], "threshold": 0.85 }
    """
    try:
        data = request.get_json()
        if not data or 'listings' not in data:
            return jsonify({'error': 'Listings array is required'}), 400

        listings = data['listings']
        threshold = data.get('threshold', 0.85)

        detector = get_duplicate_detector(threshold=threshold)
        duplicates = detector.find_duplicates(listings)

        return jsonify({
            'duplicates': duplicates,
            'total_duplicates': len(duplicates),
            'threshold': threshold
        }), 200
    except Exception as e:
        logger.error(f"Error detecting duplicates: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# QUALITY SCORING ENDPOINTS
# ============================================================================

@app.route('/api/quality/score', methods=['POST'])
def score_quality():
    """
    Score quality of provided listings
    Body: { "listings": [...] }
    """
    try:
        data = request.get_json()
        if not data or 'listings' not in data:
            return jsonify({'error': 'Listings array is required'}), 400

        listings = data['listings']
        scored = quality_scorer.score_listings_batch(listings)

        summary = quality_scorer.get_quality_summary(scored)

        return jsonify({
            'scored_listings': scored,
            'summary': summary
        }), 200
    except Exception as e:
        logger.error(f"Error scoring quality: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# FIRESTORE QUERY ENDPOINTS
# ============================================================================

@app.route('/api/firestore/query', methods=['POST'])
def query_firestore():
    """
    Query properties from Firestore with advanced filtering

    Body: {
        "filters": {
            "location": "Lekki",
            "price_min": 5000000,
            "price_max": 50000000,
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "property_type": "Flat",
            "source": "npc",
            "quality_score_min": 0.7
        },
        "sort_by": "price",          # price, bedrooms, quality_score, scrape_timestamp
        "sort_desc": true,
        "limit": 50,
        "offset": 0
    }
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred_json = os.getenv('FIREBASE_CREDENTIALS')
            cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')

            if cred_json:
                cred = credentials.Certificate(json.loads(cred_json))
            elif cred_path and Path(cred_path).exists():
                cred = credentials.Certificate(cred_path)
            else:
                return jsonify({
                    'error': 'Firebase not configured',
                    'details': 'Set FIREBASE_CREDENTIALS or FIREBASE_SERVICE_ACCOUNT environment variable'
                }), 500

            firebase_admin.initialize_app(cred)

        db = firestore.client()
        data = request.get_json() or {}
        filters = data.get('filters', {})

        # Build query
        query = db.collection('properties')

        # Apply filters
        if 'location' in filters:
            query = query.where('location', '==', filters['location'])
        if 'price_min' in filters:
            query = query.where('price', '>=', filters['price_min'])
        if 'price_max' in filters:
            query = query.where('price', '<=', filters['price_max'])
        if 'bedrooms_min' in filters:
            query = query.where('bedrooms', '>=', filters['bedrooms_min'])
        if 'bathrooms_min' in filters:
            query = query.where('bathrooms', '>=', filters['bathrooms_min'])
        if 'property_type' in filters:
            query = query.where('property_type', '==', filters['property_type'])
        if 'source' in filters:
            query = query.where('source', '==', filters['source'])
        if 'quality_score_min' in filters:
            query = query.where('quality_score', '>=', filters['quality_score_min'])

        # Apply sorting
        sort_by = data.get('sort_by', 'scrape_timestamp')
        sort_desc = data.get('sort_desc', True)
        direction = firestore.Query.DESCENDING if sort_desc else firestore.Query.ASCENDING
        query = query.order_by(sort_by, direction=direction)

        # Apply pagination
        limit = min(data.get('limit', 50), 1000)  # Max 1000 results
        query = query.limit(limit)

        if data.get('offset', 0) > 0:
            query = query.offset(data['offset'])

        # Execute query
        results = query.stream()
        properties = [doc.to_dict() for doc in results]

        return jsonify({
            'results': properties,
            'count': len(properties),
            'filters_applied': filters,
            'sort_by': sort_by,
            'sort_desc': sort_desc
        }), 200

    except ImportError:
        return jsonify({
            'error': 'Firebase Admin SDK not installed',
            'details': 'Run: pip install firebase-admin'
        }), 500
    except Exception as e:
        logger.error(f"Error querying Firestore: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/query-archive', methods=['POST'])
def query_firestore_archive():
    """
    Query ARCHIVED properties from Firestore (for price prediction & historical analysis)

    Archived properties are those that haven't been seen in recent scrapes (>30 days old).
    This is useful for:
    - Price prediction models (historical data)
    - Market trend analysis
    - Tracking price changes over time

    Body: Same as /api/firestore/query
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred_json = os.getenv('FIREBASE_CREDENTIALS')
            cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')

            if cred_json:
                cred = credentials.Certificate(json.loads(cred_json))
            elif cred_path and Path(cred_path).exists():
                cred = credentials.Certificate(cred_path)
            else:
                return jsonify({
                    'error': 'Firebase not configured',
                    'details': 'Set FIREBASE_CREDENTIALS or FIREBASE_SERVICE_ACCOUNT environment variable'
                }), 500

            firebase_admin.initialize_app(cred)

        db = firestore.client()
        data = request.get_json() or {}
        filters = data.get('filters', {})

        # Build query on ARCHIVE collection
        query = db.collection('properties_archive')

        # Apply filters (same as active properties)
        if 'location' in filters:
            query = query.where('location', '==', filters['location'])
        if 'price_min' in filters:
            query = query.where('price', '>=', filters['price_min'])
        if 'price_max' in filters:
            query = query.where('price', '<=', filters['price_max'])
        if 'bedrooms_min' in filters:
            query = query.where('bedrooms', '>=', filters['bedrooms_min'])
        if 'bathrooms_min' in filters:
            query = query.where('bathrooms', '>=', filters['bathrooms_min'])
        if 'property_type' in filters:
            query = query.where('property_type', '==', filters['property_type'])
        if 'source' in filters:
            query = query.where('source', '==', filters['source'])

        # Apply sorting
        sort_by = data.get('sort_by', 'archived_at')
        sort_desc = data.get('sort_desc', True)
        direction = firestore.Query.DESCENDING if sort_desc else firestore.Query.ASCENDING
        query = query.order_by(sort_by, direction=direction)

        # Apply pagination
        limit = min(data.get('limit', 50), 1000)  # Max 1000 results
        query = query.limit(limit)

        if data.get('offset', 0) > 0:
            query = query.offset(data['offset'])

        # Execute query
        results = query.stream()
        properties = [doc.to_dict() for doc in results]

        return jsonify({
            'results': properties,
            'count': len(properties),
            'collection': 'properties_archive',
            'filters_applied': filters,
            'sort_by': sort_by,
            'sort_desc': sort_desc,
            'note': 'These are archived (stale) properties for historical analysis'
        }), 200

    except ImportError:
        return jsonify({
            'error': 'Firebase Admin SDK not installed',
            'details': 'Run: pip install firebase-admin'
        }), 500
    except Exception as e:
        logger.error(f"Error querying Firestore archive: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/export', methods=['POST'])
def export_firestore_data():
    """
    Export data directly from Firestore to various formats

    Body: {
        "format": "excel",      # excel, csv, json
        "collection": "properties",  # properties or properties_archive
        "filters": {...},       # Same filters as query endpoint
        "limit": 1000          # Max records to export
    }

    Returns: File download or download URL
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import pandas as pd
        import io

        data = request.get_json() or {}
        export_format = data.get('format', 'excel').lower()
        collection_name = data.get('collection', 'properties')
        filters = data.get('filters', {})
        limit = min(data.get('limit', 1000), 10000)  # Max 10k records

        # Validate format
        valid_formats = ['excel', 'csv', 'json']
        if export_format not in valid_formats:
            return jsonify({
                'error': f'Invalid format. Valid: {valid_formats}'
            }), 400

        # Initialize Firebase
        if not firebase_admin._apps:
            cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        query = db.collection(collection_name)

        # Apply filters (same logic as query endpoint)
        if filters.get('location'):
            query = query.where('location', '==', filters['location'])
        if filters.get('property_type'):
            query = query.where('property_type', '==', filters['property_type'])
        if filters.get('price_min'):
            query = query.where('price', '>=', filters['price_min'])
        if filters.get('price_max'):
            query = query.where('price', '<=', filters['price_max'])

        # Execute query
        query = query.limit(limit)
        docs = query.stream()

        # Convert to list
        properties = []
        for doc in docs:
            prop = doc.to_dict()
            prop['id'] = doc.id
            properties.append(prop)

        if not properties:
            return jsonify({
                'error': 'No data found matching filters'
            }), 404

        # Convert to DataFrame
        df = pd.DataFrame(properties)

        # Remove Firebase internal fields
        internal_fields = ['_firestore_id', '_timestamp']
        df = df.drop(columns=[col for col in internal_fields if col in df.columns], errors='ignore')

        # Generate file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if export_format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Properties')
            output.seek(0)

            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'firestore_export_{timestamp}.xlsx'
            )

        elif export_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)

            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=firestore_export_{timestamp}.csv'}
            )

        elif export_format == 'json':
            return jsonify({
                'count': len(properties),
                'properties': properties,
                'exported_at': timestamp
            }), 200

    except ModuleNotFoundError:
        return jsonify({
            'error': 'Firebase Admin SDK not installed',
            'details': 'Run: pip install firebase-admin'
        }), 500
    except Exception as e:
        logger.error(f"Error exporting from Firestore: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADVANCED EXPORT ENDPOINTS (Multiple Formats & Filters)
# ============================================================================

@app.route('/api/export/generate', methods=['POST'])
def generate_export():
    """
    Generate export file with advanced filtering and format options

    Body: {
        "format": "excel",           # excel, csv, json, parquet
        "filters": {                 # Same as Firestore query filters
            "location": "Lekki",
            "price_min": 5000000,
            "price_max": 50000000,
            "bedrooms_min": 3,
            "property_type": "Flat",
            "date_from": "2025-01-01",
            "date_to": "2025-10-21"
        },
        "columns": ["title", "price", "location", "bedrooms"],  # Optional: select specific columns
        "sort_by": "price",
        "sort_desc": true,
        "include_images": false,     # Exclude images column for smaller file
        "filename": "my_export"      # Optional custom filename
    }
    """
    try:
        data = request.get_json() or {}
        export_format = data.get('format', 'excel').lower()
        filters = data.get('filters', {})
        columns = data.get('columns')
        sort_by = data.get('sort_by', 'scrape_timestamp')
        sort_desc = data.get('sort_desc', True)
        include_images = data.get('include_images', True)
        custom_filename = data.get('filename')

        # Validate format
        valid_formats = ['excel', 'csv', 'json', 'parquet']
        if export_format not in valid_formats:
            return jsonify({
                'error': f'Invalid format: {export_format}',
                'valid_formats': valid_formats
            }), 400

        # Query Firestore with filters using enterprise schema
        try:
            from core.firestore_queries_enterprise import search_properties_advanced

            # Convert filters to enterprise format (nested schema fields)
            enterprise_filters = {}

            if 'location' in filters:
                enterprise_filters['location'] = filters['location']
            if 'price_min' in filters:
                enterprise_filters['price_min'] = filters['price_min']
            if 'price_max' in filters:
                enterprise_filters['price_max'] = filters['price_max']
            if 'bedrooms_min' in filters:
                enterprise_filters['bedrooms_min'] = filters['bedrooms_min']
            if 'bathrooms_min' in filters:
                enterprise_filters['bathrooms_min'] = filters['bathrooms_min']
            if 'property_type' in filters:
                enterprise_filters['property_type'] = filters['property_type']
            if 'source' in filters:
                # Note: 'source' in frontend maps to 'site_key' in enterprise schema
                enterprise_filters['site_key'] = filters['source']

            # Use enterprise query function (handles nested schema correctly)
            # This returns unlimited results for export purposes
            properties = search_properties_advanced(enterprise_filters)

            # Flatten enterprise schema for export (CSV/Excel need flat structure)
            flattened_properties = []
            for prop in properties:
                flat = {}
                # Flatten basic_info
                if 'basic_info' in prop:
                    for k, v in prop['basic_info'].items():
                        flat[f'basic_{k}'] = v
                # Flatten property_details
                if 'property_details' in prop:
                    for k, v in prop['property_details'].items():
                        flat[f'property_{k}'] = v
                # Flatten financial
                if 'financial' in prop:
                    for k, v in prop['financial'].items():
                        flat[f'financial_{k}'] = v
                # Flatten location
                if 'location' in prop:
                    for k, v in prop['location'].items():
                        if k != 'coordinates':  # Skip GeoPoint (not exportable)
                            flat[f'location_{k}'] = v
                # Flatten amenities (convert arrays to comma-separated)
                if 'amenities' in prop:
                    for k, v in prop['amenities'].items():
                        if isinstance(v, list):
                            flat[f'amenities_{k}'] = ', '.join(str(x) for x in v)
                        else:
                            flat[f'amenities_{k}'] = v
                # Flatten agent_info
                if 'agent_info' in prop:
                    for k, v in prop['agent_info'].items():
                        flat[f'agent_{k}'] = v
                # Flatten metadata
                if 'metadata' in prop:
                    for k, v in prop['metadata'].items():
                        if k not in ['search_keywords']:  # Skip arrays
                            flat[f'metadata_{k}'] = v
                # Flatten tags
                if 'tags' in prop:
                    for k, v in prop['tags'].items():
                        if not isinstance(v, list):
                            flat[f'tags_{k}'] = v
                        else:
                            flat[f'tags_{k}'] = ', '.join(str(x) for x in v)
                # Handle media (just URLs, not full arrays)
                if 'media' in prop:
                    flat['media_image_count'] = len(prop['media'].get('images', []))
                    flat['media_virtual_tour'] = prop['media'].get('virtual_tour_url')

                flattened_properties.append(flat)

            properties = flattened_properties

        except ImportError as e:
            # Firestore is required - no fallback to local files
            return jsonify({
                'error': 'Firestore not available',
                'details': 'Export requires Firestore. Ensure FIRESTORE_ENABLED=1 and credentials are configured.',
                'import_error': str(e)
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Export query failed',
                'details': str(e)
            }), 500

        if not properties:
            return jsonify({
                'error': 'No properties match the filters',
                'filters': filters
            }), 404

        # Convert to DataFrame for export
        df = pd.DataFrame(properties)

        # Select specific columns if requested
        if columns:
            available_cols = [col for col in columns if col in df.columns]
            df = df[available_cols]

        # Remove images column if requested
        if not include_images and 'images' in df.columns:
            df = df.drop('images', axis=1)

        # Sort data
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=not sort_desc)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_filename:
            base_filename = f"{custom_filename}_{timestamp}"
        else:
            base_filename = f"properties_export_{timestamp}"

        # Create exports/temp directory if it doesn't exist
        temp_dir = Path('exports/temp')
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Generate file based on format
        if export_format == 'excel':
            filename = f"{base_filename}.xlsx"
            filepath = temp_dir / filename
            df.to_excel(filepath, index=False, engine='openpyxl')

        elif export_format == 'csv':
            filename = f"{base_filename}.csv"
            filepath = temp_dir / filename
            df.to_csv(filepath, index=False)

        elif export_format == 'json':
            filename = f"{base_filename}.json"
            filepath = temp_dir / filename
            df.to_json(filepath, orient='records', indent=2)

        elif export_format == 'parquet':
            filename = f"{base_filename}.parquet"
            filepath = temp_dir / filename
            df.to_parquet(filepath, index=False)

        file_size = filepath.stat().st_size

        return jsonify({
            'success': True,
            'download_url': f'/api/export/download/{filename}',
            'filename': filename,
            'format': export_format,
            'record_count': len(df),
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / 1024 / 1024, 2),
            'filters_applied': filters,
            'columns': list(df.columns)
        }), 200

    except Exception as e:
        logger.error(f"Error generating export: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/download/<filename>', methods=['GET'])
def download_export_file(filename):
    """Download generated export file"""
    try:
        filepath = Path('exports/temp') / filename

        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        # Determine mimetype based on extension
        extension = filepath.suffix.lower()
        mimetypes = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.parquet': 'application/octet-stream'
        }

        mimetype = mimetypes.get(extension, 'application/octet-stream')

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/formats', methods=['GET'])
def get_export_formats():
    """Get list of available export formats and their descriptions"""
    return jsonify({
        'formats': [
            {
                'format': 'excel',
                'extension': '.xlsx',
                'description': 'Microsoft Excel format - Best for manual analysis and sharing',
                'supports_formulas': True,
                'file_size': 'Medium',
                'recommended_for': 'General use, business reports, manual analysis'
            },
            {
                'format': 'csv',
                'extension': '.csv',
                'description': 'Comma-Separated Values - Universal compatibility',
                'supports_formulas': False,
                'file_size': 'Small',
                'recommended_for': 'Import into other tools, lightweight storage'
            },
            {
                'format': 'json',
                'extension': '.json',
                'description': 'JSON format - Best for programmatic access and APIs',
                'supports_formulas': False,
                'file_size': 'Medium',
                'recommended_for': 'Web applications, API integration'
            },
            {
                'format': 'parquet',
                'extension': '.parquet',
                'description': 'Apache Parquet - Optimized columnar format',
                'supports_formulas': False,
                'file_size': 'Very Small (compressed)',
                'recommended_for': 'Data analysis, analytics, big data processing'
            }
        ],
        'available_filters': {
            'location': 'Filter by location (exact match)',
            'price_min': 'Minimum price',
            'price_max': 'Maximum price',
            'bedrooms_min': 'Minimum bedrooms',
            'bathrooms_min': 'Minimum bathrooms',
            'property_type': 'Property type (Flat, House, Land, etc.)',
            'source': 'Data source (npc, propertypro, jiji, etc.)',
            'quality_score_min': 'Minimum quality score (0.0 - 1.0)',
            'date_from': 'Start date (YYYY-MM-DD)',
            'date_to': 'End date (YYYY-MM-DD)'
        }
    }), 200


# ============================================================================
# GITHUB ACTIONS INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/github/trigger-scrape', methods=['POST'])
def trigger_github_scrape():
    """
    Trigger GitHub Actions workflow via repository_dispatch
    Body: {
        "page_cap": 20,         # Optional: pages per site
        "geocode": 1,           # Optional: enable geocoding (0 or 1)
        "sites": ["npc", ...]   # Optional: specific sites
    }

    Requires environment variables:
    - GITHUB_TOKEN: Personal Access Token with 'repo' scope
    - GITHUB_OWNER: Repository owner (e.g., 'Tee-David')
    - GITHUB_REPO: Repository name (e.g., 'realtors_practice')
    """
    try:
        import requests

        # Get GitHub credentials from environment
        github_token = os.getenv('GITHUB_TOKEN')
        github_owner = os.getenv('GITHUB_OWNER')
        github_repo = os.getenv('GITHUB_REPO')

        # Debug logging
        logger.info(f"GitHub Token loaded: {github_token[:10] if github_token else 'NONE'}... (length: {len(github_token) if github_token else 0})")

        if not all([github_token, github_owner, github_repo]):
            return jsonify({
                'error': 'Missing GitHub configuration',
                'details': 'Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables'
            }), 500

        # Get request body
        data = request.get_json() or {}
        max_pages = data.get('max_pages', 15)  # Matches workflow parameter name
        geocode = data.get('geocode', 1)
        sites = data.get('sites', [])  # Can be empty list for all sites

        # Prepare GitHub API request
        url = f'https://api.github.com/repos/{github_owner}/{github_repo}/dispatches'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        payload = {
            'event_type': 'trigger-scrape',
            'client_payload': {
                'max_pages': str(max_pages),  # Convert to string for GitHub Actions
                'geocode': str(geocode),      # Convert to string to avoid falsy 0 bug
                'sites': sites,
                'triggered_by': 'api',
                'timestamp': datetime.now().isoformat()
            }
        }

        # Make request to GitHub API
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 204:
            return jsonify({
                'success': True,
                'message': 'Scraper workflow triggered successfully',
                'run_url': f'https://github.com/{github_owner}/{github_repo}/actions',
                'parameters': {
                    'max_pages': max_pages,
                    'geocode': geocode,
                    'sites': sites if sites else 'all enabled sites'
                }
            }), 200
        else:
            return jsonify({
                'error': f'GitHub API error: {response.status_code}',
                'details': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out")
        return jsonify({'error': 'Request to GitHub API timed out'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        return jsonify({'error': f'GitHub API request failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error triggering GitHub workflow: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/estimate-scrape-time', methods=['POST'])
def estimate_scrape_time():
    """
    Estimate time required for a scrape session with timeout warnings

    Body: {
        "page_cap": 15,          # Pages per site (default: 15)
        "geocode": 1,            # 0 or 1
        "sites": ["npc", ...]    # Optional: specific sites (empty = all enabled)
    }

    Returns: {
        "estimated_duration_minutes": 180,
        "estimated_duration_hours": 3.0,
        "estimated_duration_text": "~3h 0m",
        "site_count": 51,
        "batch_type": "multi-session",
        "sessions": 17,
        "sites_per_session": 3,
        "max_parallel_sessions": 5,
        "timeout_risk": "safe",  # "safe", "warning", "danger"
        "timeout_message": null,
        "breakdown": {...},
        "recommendations": [...]
    }
    """
    try:
        import yaml
        import math

        # Get request body
        data = request.get_json() or {}
        page_cap = data.get('page_cap', 15)  # Updated default to match workflow
        geocode = data.get('geocode', 1)
        sites_param = data.get('sites', [])

        # Load config to count sites
        with open('config.yaml') as f:
            config = yaml.safe_load(f)

        if sites_param:
            site_count = len(sites_param)
        else:
            site_count = sum(1 for site_config in config.get('sites', {}).values() if site_config.get('enabled', False))

        # UPDATED ESTIMATION FORMULA (matches workflow constants)
        # Based on actual workflow time estimation (lines 72-78 in scrape-production.yml)
        TIME_PER_PAGE = 8  # seconds
        TIME_PER_SITE_OVERHEAD = 45  # seconds
        GEOCODE_TIME_PER_PROPERTY = 1.2  # seconds
        FIRESTORE_UPLOAD_TIME = 0.3  # seconds
        WATCHER_OVERHEAD = 120  # seconds
        BUFFER_MULTIPLIER = 1.3  # 30% safety buffer

        # Workflow settings (conservative strategy)
        SITES_PER_SESSION = 3
        MAX_PARALLEL_SESSIONS = 5
        SESSION_TIMEOUT_MINUTES = 90
        GITHUB_TIMEOUT_MINUTES = 350  # 6 hours minus 10 min buffer

        # Estimate properties per page
        estimated_properties_per_page = 15
        estimated_properties = page_cap * estimated_properties_per_page

        # Calculate time per site (in seconds)
        scrape_time = (page_cap * TIME_PER_PAGE) + TIME_PER_SITE_OVERHEAD
        geocode_time = (estimated_properties * GEOCODE_TIME_PER_PROPERTY) if geocode == 1 else 0
        upload_time = estimated_properties * FIRESTORE_UPLOAD_TIME
        time_per_site = scrape_time + geocode_time + upload_time

        # Calculate session time (in minutes)
        sites_in_session = min(site_count, SITES_PER_SESSION)
        session_time_seconds = (time_per_site * sites_in_session + WATCHER_OVERHEAD) * BUFFER_MULTIPLIER
        session_time_minutes = session_time_seconds / 60

        # Calculate total sessions
        total_sessions = math.ceil(site_count / SITES_PER_SESSION)

        # Calculate total time (accounting for parallel execution)
        parallel_batches = math.ceil(total_sessions / MAX_PARALLEL_SESSIONS)
        total_minutes = parallel_batches * session_time_minutes

        # Determine timeout risk
        timeout_risk = "safe"
        timeout_message = None
        recommendations = []

        if total_minutes > GITHUB_TIMEOUT_MINUTES:
            timeout_risk = "danger"
            timeout_message = f"⛔ CRITICAL: Estimated time ({total_minutes:.0f} min) exceeds GitHub Actions limit ({GITHUB_TIMEOUT_MINUTES} min). Scrape WILL timeout!"
            recommendations.append(f"Reduce sites or pages. Try max {int(GITHUB_TIMEOUT_MINUTES / session_time_minutes * SITES_PER_SESSION)} sites or {int(page_cap * 0.5)} pages.")
        elif total_minutes > 240:  # 4 hours
            timeout_risk = "warning"
            timeout_message = f"⚠️ WARNING: Estimated time ({total_minutes:.0f} min / {total_minutes/60:.1f}h) is high. Risk of timeout."
            recommendations.append("Consider reducing pages or running in smaller batches.")
        elif session_time_minutes > SESSION_TIMEOUT_MINUTES:
            timeout_risk = "warning"
            timeout_message = f"⚠️ WARNING: Session time ({session_time_minutes:.0f} min) exceeds session timeout ({SESSION_TIMEOUT_MINUTES} min)."
            recommendations.append(f"Reduce pages to {int(page_cap * SESSION_TIMEOUT_MINUTES / session_time_minutes)} or fewer per site.")
        else:
            recommendations.append("✅ Estimated time is within safe limits.")

        # Format duration text
        if total_minutes < 60:
            duration_text = f"~{int(total_minutes)} minutes"
        else:
            hours = int(total_minutes // 60)
            mins = int(total_minutes % 60)
            duration_text = f"~{hours}h {mins}m" if mins > 0 else f"~{hours}h"

        # Determine batch type
        if site_count <= SITES_PER_SESSION:
            batch_type = "single-session"
        else:
            batch_type = "multi-session"

        return jsonify({
            'estimated_duration_minutes': round(total_minutes, 1),
            'estimated_duration_hours': round(total_minutes / 60, 2),
            'estimated_duration_text': duration_text,
            'site_count': site_count,
            'batch_type': batch_type,
            'sessions': total_sessions,
            'sites_per_session': SITES_PER_SESSION,
            'max_parallel_sessions': MAX_PARALLEL_SESSIONS,
            'session_time_minutes': round(session_time_minutes, 1),
            'session_timeout_limit': SESSION_TIMEOUT_MINUTES,
            'total_timeout_limit': GITHUB_TIMEOUT_MINUTES,
            'timeout_risk': timeout_risk,
            'timeout_message': timeout_message,
            'breakdown': {
                'scraping_per_site': round(scrape_time / 60, 1),
                'geocoding_per_site': round(geocode_time / 60, 1),
                'upload_per_site': round(upload_time / 60, 1),
                'watcher_overhead': round(WATCHER_OVERHEAD / 60, 1),
                'buffer_multiplier': BUFFER_MULTIPLIER
            },
            'recommendations': recommendations,
            'configuration': {
                'page_cap': page_cap,
                'geocode_enabled': geocode == 1,
                'estimated_properties_per_site': estimated_properties
            },
            'note': 'Estimates based on workflow time constants. Actual time may vary by ±20%.'
        }), 200

    except Exception as e:
        logger.error(f"Error estimating scrape time: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/subscribe', methods=['POST'])
def subscribe_notifications():
    """
    Subscribe to workflow notifications (for push notifications)

    Body: {
        "subscription": {
            "endpoint": "https://fcm.googleapis.com/...",  # Push notification endpoint
            "keys": {...}  # Push notification keys
        },
        "user_id": "optional_user_id"
    }

    Note: This stores the subscription in memory. For production, use a database.
    """
    try:
        data = request.get_json()
        if not data or 'subscription' not in data:
            return jsonify({'error': 'Subscription data is required'}), 400

        # In production, store this in a database
        # For now, we'll just acknowledge it
        subscription = data['subscription']
        user_id = data.get('user_id', 'anonymous')

        logger.info(f"Notification subscription registered for user: {user_id}")

        return jsonify({
            'success': True,
            'message': 'Subscribed to workflow notifications',
            'note': 'You will receive notifications when scrapes start, progress, and complete'
        }), 200

    except Exception as e:
        logger.error(f"Error subscribing to notifications: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/workflow-status/<run_id>', methods=['GET'])
def get_workflow_status(run_id):
    """
    Get real-time status of a workflow run (for live updates on frontend)

    Returns: {
        "run_id": 123456,
        "status": "in_progress",  # queued, in_progress, completed, failed
        "conclusion": null,        # success, failure, cancelled (when completed)
        "progress": {
            "current_step": "Processing exports",
            "percent_complete": 65,
            "estimated_time_remaining": "15 minutes"
        },
        "started_at": "2025-10-21T10:00:00Z",
        "completed_at": null
    }
    """
    try:
        import requests

        # Get GitHub credentials
        github_token = os.getenv('GITHUB_TOKEN')
        github_owner = os.getenv('GITHUB_OWNER')
        github_repo = os.getenv('GITHUB_REPO')

        if not all([github_token, github_owner, github_repo]):
            return jsonify({'error': 'GitHub configuration missing'}), 500

        # Get workflow run details from GitHub API
        url = f'https://api.github.com/repos/{github_owner}/{github_repo}/actions/runs/{run_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            run_data = response.json()

            # Calculate progress based on current step
            status = run_data.get('status')  # queued, in_progress, completed
            conclusion = run_data.get('conclusion')  # success, failure, cancelled
            started_at = run_data.get('run_started_at')
            completed_at = run_data.get('updated_at')

            # Estimate progress (rough estimation)
            progress = {
                'current_step': 'Unknown',
                'percent_complete': 0,
                'estimated_time_remaining': 'Calculating...'
            }

            if status == 'completed':
                progress['current_step'] = 'Complete'
                progress['percent_complete'] = 100
                progress['estimated_time_remaining'] = '0 minutes'
            elif status == 'in_progress':
                # Rough estimation based on elapsed time
                from datetime import datetime, timezone
                if started_at:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    elapsed_minutes = (datetime.now(timezone.utc) - start_time).total_seconds() / 60

                    # Assume typical scrape is 45-60 minutes
                    estimated_total = 50
                    percent = min(95, (elapsed_minutes / estimated_total) * 100)

                    progress['percent_complete'] = int(percent)
                    progress['estimated_time_remaining'] = f"~{int(estimated_total - elapsed_minutes)} minutes"

                    # Guess current step based on progress
                    if percent < 20:
                        progress['current_step'] = 'Setting up environment'
                    elif percent < 60:
                        progress['current_step'] = 'Scraping websites'
                    elif percent < 80:
                        progress['current_step'] = 'Processing data'
                    elif percent < 95:
                        progress['current_step'] = 'Uploading to Firestore'
                    else:
                        progress['current_step'] = 'Finalizing...'

            return jsonify({
                'run_id': run_data.get('id'),
                'status': status,
                'conclusion': conclusion,
                'progress': progress,
                'started_at': started_at,
                'completed_at': completed_at,
                'html_url': run_data.get('html_url')
            }), 200
        else:
            return jsonify({'error': f'GitHub API error: {response.status_code}'}), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request to GitHub API timed out'}), 504
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/workflow-runs', methods=['GET'])
def get_workflow_runs():
    """
    Get recent GitHub Actions workflow runs
    Query params:
        - per_page: Number of runs to return (default: 5, max: 100)
        - workflow_id: Filter by specific workflow file (optional)
    """
    try:
        import requests

        # Get GitHub credentials from environment
        github_token = os.getenv('GITHUB_TOKEN')
        github_owner = os.getenv('GITHUB_OWNER')
        github_repo = os.getenv('GITHUB_REPO')

        if not all([github_token, github_owner, github_repo]):
            return jsonify({
                'error': 'Missing GitHub configuration',
                'details': 'Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables'
            }), 500

        # Get query parameters
        per_page = min(int(request.args.get('per_page', 5)), 100)
        workflow_id = request.args.get('workflow_id')

        # Prepare GitHub API request
        url = f'https://api.github.com/repos/{github_owner}/{github_repo}/actions/runs'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}'
        }
        params = {'per_page': per_page}
        if workflow_id:
            params['workflow_id'] = workflow_id

        # Make request to GitHub API
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])

            # Simplify run data for frontend
            simplified_runs = []
            for run in runs:
                simplified_runs.append({
                    'id': run['id'],
                    'name': run['name'],
                    'status': run['status'],
                    'conclusion': run['conclusion'],
                    'created_at': run['created_at'],
                    'updated_at': run['updated_at'],
                    'html_url': run['html_url'],
                    'run_number': run['run_number']
                })

            return jsonify({
                'workflow_runs': simplified_runs,
                'total_count': data.get('total_count', len(runs))
            }), 200
        else:
            return jsonify({
                'error': f'GitHub API error: {response.status_code}',
                'details': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out")
        return jsonify({'error': 'Request to GitHub API timed out'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        return jsonify({'error': f'GitHub API request failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error getting workflow runs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/artifacts', methods=['GET'])
def get_artifacts():
    """
    Get GitHub Actions artifacts (scraped data exports)
    Query params:
        - per_page: Number of artifacts to return (default: 10, max: 100)
    """
    try:
        import requests

        # Get GitHub credentials from environment
        github_token = os.getenv('GITHUB_TOKEN')
        github_owner = os.getenv('GITHUB_OWNER')
        github_repo = os.getenv('GITHUB_REPO')

        if not all([github_token, github_owner, github_repo]):
            return jsonify({
                'error': 'Missing GitHub configuration',
                'details': 'Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables'
            }), 500

        # Get query parameters
        per_page = min(int(request.args.get('per_page', 10)), 100)

        # Prepare GitHub API request
        url = f'https://api.github.com/repos/{github_owner}/{github_repo}/actions/artifacts'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}'
        }
        params = {'per_page': per_page}

        # Make request to GitHub API
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            artifacts = data.get('artifacts', [])

            # Simplify artifact data for frontend
            simplified_artifacts = []
            for artifact in artifacts:
                simplified_artifacts.append({
                    'id': artifact['id'],
                    'name': artifact['name'],
                    'size_in_bytes': artifact['size_in_bytes'],
                    'size_mb': round(artifact['size_in_bytes'] / 1024 / 1024, 2),
                    'created_at': artifact['created_at'],
                    'expired': artifact['expired'],
                    'archive_download_url': artifact['archive_download_url']
                })

            return jsonify({
                'artifacts': simplified_artifacts,
                'total_count': data.get('total_count', len(artifacts))
            }), 200
        else:
            return jsonify({
                'error': f'GitHub API error: {response.status_code}',
                'details': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out")
        return jsonify({'error': 'Request to GitHub API timed out'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        return jsonify({'error': f'GitHub API request failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error getting artifacts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/artifact/<int:artifact_id>/download', methods=['GET'])
def download_artifact(artifact_id):
    """
    Download a specific GitHub artifact
    Returns the download URL (frontend must download with Authorization header)
    """
    try:
        import requests

        # Get GitHub credentials from environment
        github_token = os.getenv('GITHUB_TOKEN')
        github_owner = os.getenv('GITHUB_OWNER')
        github_repo = os.getenv('GITHUB_REPO')

        if not all([github_token, github_owner, github_repo]):
            return jsonify({
                'error': 'Missing GitHub configuration',
                'details': 'Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables'
            }), 500

        # Get artifact details first
        url = f'https://api.github.com/repos/{github_owner}/{github_repo}/actions/artifacts/{artifact_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            artifact = response.json()
            return jsonify({
                'artifact_id': artifact_id,
                'name': artifact['name'],
                'download_url': artifact['archive_download_url'],
                'size_mb': round(artifact['size_in_bytes'] / 1024 / 1024, 2),
                'note': 'Use this URL with Authorization header to download'
            }), 200
        else:
            return jsonify({
                'error': f'Artifact not found or GitHub API error: {response.status_code}',
                'details': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out")
        return jsonify({'error': 'Request to GitHub API timed out'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        return jsonify({'error': f'GitHub API request failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error getting artifact download URL: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SCHEDULED SCRAPING ENDPOINTS
# ============================================================================

# In-memory storage for scheduled jobs (use Redis/database in production)
scheduled_jobs = {}
job_id_counter = 1

@app.route('/api/schedule/scrape', methods=['POST'])
def schedule_scrape():
    """
    Schedule a scrape to run at a specific time
    Body: {
        "scheduled_time": "2025-10-22T15:00:00",  # ISO format or Unix timestamp
        "page_cap": 20,                            # Optional
        "geocode": 1,                              # Optional
        "sites": ["npc", "jiji"]                   # Optional
    }

    Returns: {
        "job_id": 1,
        "scheduled_time": "2025-10-22T15:00:00",
        "status": "scheduled",
        "trigger_url": "/api/schedule/jobs/1/cancel"
    }
    """
    global job_id_counter

    try:
        from datetime import datetime, timezone
        import threading
        import time

        data = request.get_json() or {}
        scheduled_time_str = data.get('scheduled_time')

        if not scheduled_time_str:
            return jsonify({'error': 'scheduled_time is required'}), 400

        # Parse scheduled time
        try:
            # Try ISO format first
            if isinstance(scheduled_time_str, str):
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                # Ensure timezone-aware (assume UTC if naive)
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            else:
                # Unix timestamp
                scheduled_time = datetime.fromtimestamp(scheduled_time_str, tz=timezone.utc)
        except Exception as e:
            return jsonify({
                'error': 'Invalid scheduled_time format',
                'details': 'Use ISO format (2025-10-22T15:00:00) or Unix timestamp'
            }), 400

        # Check if time is in the future
        now = datetime.now(timezone.utc)
        if scheduled_time <= now:
            return jsonify({
                'error': 'scheduled_time must be in the future',
                'current_time': now.isoformat()
            }), 400

        # Calculate delay in seconds
        delay_seconds = (scheduled_time - now).total_seconds()

        # Create job
        global job_id_counter
        job_id = job_id_counter
        job_id_counter += 1

        job = {
            'job_id': job_id,
            'scheduled_time': scheduled_time.isoformat(),
            'page_cap': data.get('page_cap', 20),
            'geocode': data.get('geocode', 1),
            'sites': data.get('sites', []),
            'status': 'scheduled',
            'created_at': now.isoformat()
        }

        # Define the job execution function
        def execute_scheduled_job(job_id):
            time.sleep(delay_seconds)

            # Check if job was cancelled
            if job_id not in scheduled_jobs or scheduled_jobs[job_id]['status'] == 'cancelled':
                return

            # Update status
            scheduled_jobs[job_id]['status'] = 'running'

            # Trigger GitHub Actions workflow
            try:
                import requests

                github_token = os.getenv('GITHUB_TOKEN')
                github_owner = os.getenv('GITHUB_OWNER')
                github_repo = os.getenv('GITHUB_REPO')

                if all([github_token, github_owner, github_repo]):
                    url = f'https://api.github.com/repos/{github_owner}/{github_repo}/dispatches'
                    headers = {
                        'Accept': 'application/vnd.github+json',
                        'Authorization': f'Bearer {github_token}',
                        'X-GitHub-Api-Version': '2022-11-28'
                    }
                    payload = {
                        'event_type': 'trigger-scrape',
                        'client_payload': {
                            'max_pages': str(scheduled_jobs[job_id]['page_cap']),  # Convert to string
                            'geocode': str(scheduled_jobs[job_id]['geocode']),     # Convert to string
                            'sites': scheduled_jobs[job_id]['sites']
                        }
                    }

                    response = requests.post(url, json=payload, headers=headers, timeout=30)

                    if response.status_code == 204:
                        scheduled_jobs[job_id]['status'] = 'completed'
                        scheduled_jobs[job_id]['completed_at'] = datetime.now(timezone.utc).isoformat()
                    else:
                        scheduled_jobs[job_id]['status'] = 'failed'
                        scheduled_jobs[job_id]['error'] = f'GitHub API returned {response.status_code}'
                else:
                    scheduled_jobs[job_id]['status'] = 'failed'
                    scheduled_jobs[job_id]['error'] = 'Missing GitHub configuration'

            except Exception as e:
                scheduled_jobs[job_id]['status'] = 'failed'
                scheduled_jobs[job_id]['error'] = str(e)

        # Start background thread
        thread = threading.Thread(target=execute_scheduled_job, args=(job_id,), daemon=True)
        thread.start()

        # Store job
        scheduled_jobs[job_id] = job

        return jsonify({
            'success': True,
            'job_id': job_id,
            'scheduled_time': scheduled_time.isoformat(),
            'delay_seconds': int(delay_seconds),
            'status': 'scheduled',
            'cancel_url': f'/api/schedule/jobs/{job_id}/cancel',
            'check_status_url': f'/api/schedule/jobs/{job_id}'
        }), 201

    except Exception as e:
        logger.error(f"Error scheduling scrape: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/jobs', methods=['GET'])
def get_scheduled_jobs():
    """
    Get all scheduled jobs

    Returns: {
        "jobs": [...],
        "count": 5
    }
    """
    try:
        jobs_list = list(scheduled_jobs.values())

        # Sort by scheduled time (most recent first)
        jobs_list.sort(key=lambda x: x['scheduled_time'], reverse=True)

        return jsonify({
            'jobs': jobs_list,
            'count': len(jobs_list)
        }), 200

    except Exception as e:
        logger.error(f"Error getting scheduled jobs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/jobs/<int:job_id>', methods=['GET'])
def get_scheduled_job(job_id):
    """
    Get details of a specific scheduled job

    Returns job details including status
    """
    try:
        if job_id not in scheduled_jobs:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify(scheduled_jobs[job_id]), 200

    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/jobs/<int:job_id>/cancel', methods=['POST', 'DELETE'])
def cancel_scheduled_job(job_id):
    """
    Cancel a scheduled job

    Returns confirmation of cancellation
    """
    try:
        if job_id not in scheduled_jobs:
            return jsonify({'error': 'Job not found'}), 404

        job = scheduled_jobs[job_id]

        if job['status'] in ['completed', 'failed']:
            return jsonify({
                'error': f'Cannot cancel job with status: {job["status"]}'
            }), 400

        # Mark as cancelled
        job['status'] = 'cancelled'
        from datetime import datetime, timezone
        job['cancelled_at'] = datetime.now(timezone.utc).isoformat()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'cancelled',
            'message': 'Job cancelled successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# EMAIL NOTIFICATION ENDPOINTS
# ============================================================================

# Global email notifier instance (will be configured via API)
email_notifier = None
email_config = {}
email_recipients = []

@app.route('/api/email/configure', methods=['POST'])
def configure_email():
    """
    Configure SMTP settings for email notifications

    Body: {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "your-email@gmail.com",
        "smtp_password": "app-password-here",
        "smtp_use_tls": true,
        "smtp_use_ssl": false,
        "from_email": "notifications@example.com",
        "from_name": "Realtors Practice Scraper"
    }

    Returns: {
        "success": true,
        "message": "SMTP configuration saved successfully"
    }
    """
    global email_notifier, email_config

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Store configuration (in production, encrypt smtp_password!)
        email_config = {
            'smtp_host': data['smtp_host'],
            'smtp_port': int(data['smtp_port']),
            'smtp_user': data['smtp_user'],
            'smtp_password': data['smtp_password'],
            'smtp_use_tls': data.get('smtp_use_tls', data['smtp_port'] == 587),
            'smtp_use_ssl': data.get('smtp_use_ssl', data['smtp_port'] == 465),
            'from_email': data.get('from_email', data['smtp_user']),
            'from_name': data.get('from_name', 'Realtors Practice Scraper')
        }

        # Initialize email notifier
        email_notifier = EmailNotifier(email_config)

        logger.info(f"SMTP configuration updated: {email_config['smtp_host']}:{email_config['smtp_port']}")

        return jsonify({
            'success': True,
            'message': 'SMTP configuration saved successfully',
            'config': {
                'smtp_host': email_config['smtp_host'],
                'smtp_port': email_config['smtp_port'],
                'smtp_user': email_config['smtp_user'],
                'from_email': email_config['from_email'],
                'from_name': email_config['from_name']
                # Note: password is intentionally omitted from response
            }
        }), 200

    except Exception as e:
        logger.error(f"Error configuring SMTP: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/test-connection', methods=['POST'])
def test_email_connection():
    """
    Test SMTP connection with current configuration

    Returns: {
        "success": true/false,
        "message": "Connection successful" or error message,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "authenticated": true
    }
    """
    global email_notifier

    try:
        if not email_notifier:
            return jsonify({
                'error': 'SMTP not configured',
                'message': 'Please configure SMTP settings first using POST /api/email/configure'
            }), 400

        # Test connection
        result = email_notifier.test_connection()

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error testing SMTP connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/email/config', methods=['GET'])
def get_email_config():
    """
    Get current SMTP configuration (sanitized - no password)

    Returns: {
        "configured": true/false,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "your-email@gmail.com",
        "from_email": "notifications@example.com",
        "from_name": "Realtors Practice Scraper",
        "recipients_count": 3
    }
    """
    global email_config, email_recipients

    try:
        if not email_config:
            return jsonify({
                'configured': False,
                'message': 'SMTP not configured yet'
            }), 200

        return jsonify({
            'configured': True,
            'smtp_host': email_config.get('smtp_host'),
            'smtp_port': email_config.get('smtp_port'),
            'smtp_user': email_config.get('smtp_user'),
            'from_email': email_config.get('from_email'),
            'from_name': email_config.get('from_name'),
            'recipients_count': len(email_recipients)
        }), 200

    except Exception as e:
        logger.error(f"Error getting email config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/recipients', methods=['GET'])
def get_email_recipients():
    """
    Get list of notification recipients

    Returns: {
        "recipients": ["email1@example.com", "email2@example.com"],
        "count": 2
    }
    """
    global email_recipients

    try:
        return jsonify({
            'recipients': email_recipients,
            'count': len(email_recipients)
        }), 200

    except Exception as e:
        logger.error(f"Error getting email recipients: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/recipients', methods=['POST'])
def add_email_recipient():
    """
    Add email to notification list

    Body: {
        "email": "user@example.com"
    }

    Returns: {
        "success": true,
        "message": "Recipient added",
        "recipients": ["email1@example.com", "email2@example.com"],
        "count": 2
    }
    """
    global email_recipients

    try:
        data = request.get_json()

        if 'email' not in data:
            return jsonify({'error': 'Missing email field'}), 400

        email = data['email'].strip()

        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if already exists
        if email in email_recipients:
            return jsonify({
                'error': 'Email already exists',
                'recipients': email_recipients,
                'count': len(email_recipients)
            }), 400

        # Add recipient
        email_recipients.append(email)
        logger.info(f"Added email recipient: {email}")

        return jsonify({
            'success': True,
            'message': 'Recipient added successfully',
            'recipients': email_recipients,
            'count': len(email_recipients)
        }), 200

    except Exception as e:
        logger.error(f"Error adding email recipient: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/recipients/<email>', methods=['DELETE'])
def remove_email_recipient(email):
    """
    Remove email from notification list

    Returns: {
        "success": true,
        "message": "Recipient removed",
        "recipients": [...],
        "count": 1
    }
    """
    global email_recipients

    try:
        if email not in email_recipients:
            return jsonify({
                'error': 'Email not found in recipients list'
            }), 404

        email_recipients.remove(email)
        logger.info(f"Removed email recipient: {email}")

        return jsonify({
            'success': True,
            'message': 'Recipient removed successfully',
            'recipients': email_recipients,
            'count': len(email_recipients)
        }), 200

    except Exception as e:
        logger.error(f"Error removing email recipient: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/send-test', methods=['POST'])
def send_test_email():
    """
    Send a test email to verify configuration

    Body: {
        "recipient": "test@example.com"  (optional, uses configured recipients if not provided)
    }

    Returns: {
        "success": true,
        "message": "Test email sent successfully"
    }
    """
    global email_notifier, email_recipients

    try:
        if not email_notifier:
            return jsonify({
                'error': 'SMTP not configured',
                'message': 'Please configure SMTP settings first'
            }), 400

        data = request.get_json() or {}

        # Determine recipients
        if 'recipient' in data:
            recipients = [data['recipient']]
        elif email_recipients:
            recipients = email_recipients
        else:
            return jsonify({
                'error': 'No recipients specified',
                'message': 'Either provide a recipient email or add recipients to the list first'
            }), 400

        # Send test email
        test_stats = {
            'site_count': 3,
            'properties_found': 42,
            'duration': '~15 minutes'
        }

        result = email_notifier.send_scrape_completion(
            recipients=recipients,
            scrape_stats=test_stats,
            workflow_url='https://github.com/example/test'
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'results': result.get('results', [])
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to send email')
            }), 500

    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FIRESTORE OPTIMIZED QUERY ENDPOINTS (NEW)
# ============================================================================

@app.route('/api/firestore/dashboard', methods=['GET'])
def get_firestore_dashboard():
    """
    Get dashboard statistics (replaces _Dashboard sheet).

    Returns aggregated stats: total properties, price ranges, breakdowns, etc.
    Uses cached aggregates when available (updated hourly).
    """
    try:
        from core.firestore_queries_enterprise import get_dashboard_stats

        stats = get_dashboard_stats()

        if not stats:
            return jsonify({'error': 'No statistics available'}), 404

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/top-deals', methods=['GET'])
def get_firestore_top_deals():
    """
    Get cheapest properties across all sites (replaces _Top_100_Cheapest sheet).

    Query params:
        - limit: Number of results (default 100)
        - min_quality: Minimum quality score 0.0-1.0 (default 0.0)
        - property_type: Filter by property type (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_cheapest_properties

        limit = int(request.args.get('limit', 100))
        min_quality = float(request.args.get('min_quality', 0.0))
        property_type = request.args.get('property_type')

        properties = get_cheapest_properties(
            limit=limit,
            min_quality_score=min_quality,
            property_type=property_type
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting top deals: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/newest', methods=['GET'])
def get_firestore_newest():
    """
    Get newest listings (replaces _Newest_Listings sheet).

    Query params:
        - limit: Number of results (default 50)
        - days_back: Days to look back (default 7)
        - site_key: Filter by site (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_newest_listings

        limit = int(request.args.get('limit', 50))
        days_back = int(request.args.get('days_back', 7))
        site_key = request.args.get('site_key')

        properties = get_newest_listings(
            limit=limit,
            days_back=days_back,
            site_key=site_key
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting newest listings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/for-sale', methods=['GET'])
def get_firestore_for_sale():
    """
    Get properties for sale (replaces _For_Sale sheet).

    Query params:
        - limit: Number of results (default 100)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_properties_by_listing_type

        limit = int(request.args.get('limit', 100))
        price_max = request.args.get('price_max')
        price_max = int(price_max) if price_max else None

        properties = get_properties_by_listing_type(
            listing_type='sale',
            limit=limit,
            price_max=price_max
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting for-sale properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/for-rent', methods=['GET'])
def get_firestore_for_rent():
    """
    Get properties for rent (replaces _For_Rent sheet).

    Query params:
        - limit: Number of results (default 100)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_properties_by_listing_type

        limit = int(request.args.get('limit', 100))
        price_max = request.args.get('price_max')
        price_max = int(price_max) if price_max else None

        properties = get_properties_by_listing_type(
            listing_type='rent',
            limit=limit,
            price_max=price_max
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting for-rent properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/land', methods=['GET'])
def get_firestore_land():
    """
    Get land-only properties (replaces _Land_Only sheet).

    Query params:
        - limit: Number of results (default 100)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import search_properties_advanced

        limit = int(request.args.get('limit', 100))
        price_max = request.args.get('price_max')
        price_max = int(price_max) if price_max else None

        # Filter for land only
        filters = {'property_type': 'Land'}
        if price_max:
            filters['price_max'] = price_max

        properties = search_properties_advanced(
            filters=filters,
            limit=limit
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting land properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/premium', methods=['GET'])
def get_firestore_premium():
    """
    Get premium properties (replaces _4BR_Plus sheet).

    Query params:
        - min_bedrooms: Minimum bedrooms (default 4)
        - limit: Number of results (default 100)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_premium_properties

        limit = int(request.args.get('limit', 100))
        min_price = request.args.get('min_price')
        min_price = int(min_price) if min_price else None

        properties = get_premium_properties(
            limit=limit,
            min_price=min_price
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting premium properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/search', methods=['POST'])
def search_firestore_properties():
    """
    Advanced cross-site property search with multiple filters.

    JSON body:
        - filters: Dict of filters (location, price_min/max, bedrooms_min/max, property_type, site_key, quality_score_min)
        - sort_by: Field to sort by (default 'price')
        - sort_desc: Sort descending (default false)
        - limit: Number of results (default 50)
        - offset: Pagination offset (default 0)

    Example:
        {
            "filters": {
                "location": "Lekki",
                "price_min": 5000000,
                "price_max": 50000000,
                "bedrooms_min": 3,
                "property_type": "Flat",
                "quality_score_min": 0.7
            },
            "sort_by": "price",
            "limit": 50
        }
    """
    try:
        from core.firestore_queries_enterprise import search_properties_advanced

        data = request.get_json() or {}

        filters = data.get('filters', {})
        limit = data.get('limit', 50)

        properties = search_properties_advanced(
            filters=filters,
            limit=limit
        )

        result = {
            'count': len(properties),
            'data': properties
        }

        return jsonify({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/site/<site_key>', methods=['GET'])
def get_firestore_site_properties(site_key):
    """
    Get all properties from a specific site.

    Query params:
        - limit: Number of results (default 100)
        - offset: Pagination offset (default 0)
        - sort_by: Field to sort by (default 'scrape_timestamp')
        - sort_desc: Sort descending (default true)
    """
    try:
        from core.firestore_queries_enterprise import get_site_properties

        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        properties = get_site_properties(
            site_key=site_key,
            limit=limit,
            offset=offset
        )

        result = {
            'count': len(properties),
            'data': properties
        }

        return jsonify({
            'success': True,
            'site_key': site_key,
            **result
        })

    except Exception as e:
        logger.error(f"Error getting site properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/property/<property_hash>', methods=['GET'])
def get_firestore_property_by_hash(property_hash):
    """
    Get a single property by its hash (document ID).
    """
    try:
        from core.firestore_queries_enterprise import get_property_by_hash

        property_data = get_property_by_hash(property_hash)

        if not property_data:
            return jsonify({'error': 'Property not found'}), 404

        return jsonify({
            'success': True,
            'data': property_data
        })

    except Exception as e:
        logger.error(f"Error getting property by hash: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/site-stats/<site_key>', methods=['GET'])
def get_firestore_site_stats(site_key):
    """
    Get statistics for a specific site.
    """
    try:
        from core.firestore_queries_enterprise import get_site_properties

        # Get all properties for this site
        properties = get_site_properties(site_key=site_key, limit=1000)

        if not properties:
            return jsonify({'error': 'No properties found for this site'}), 404

        # Calculate statistics
        total = len(properties)
        prices = [p.get('financial', {}).get('price', 0) for p in properties if p.get('financial', {}).get('price')]

        stats = {
            'site_key': site_key,
            'total_properties': total,
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'property_types': {},
            'listing_types': {}
        }

        # Count property types and listing types
        for prop in properties:
            pt = prop.get('property_details', {}).get('property_type', 'Unknown')
            stats['property_types'][pt] = stats['property_types'].get(pt, 0) + 1

            lt = prop.get('basic_info', {}).get('listing_type', 'Unknown')
            stats['listing_types'][lt] = stats['listing_types'].get(lt, 0) + 1

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Error getting site statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/furnished', methods=['GET'])
def get_firestore_furnished():
    """
    Get furnished properties.

    Query params:
        - furnishing: Furnishing type (furnished, semi-furnished, unfurnished) - default: furnished
        - limit: Number of results (default 100)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_furnished_properties

        furnishing = request.args.get('furnishing', 'furnished')
        limit = int(request.args.get('limit', 100))
        price_max = request.args.get('price_max')
        price_max = int(price_max) if price_max else None

        properties = get_furnished_properties(
            furnishing=furnishing,
            limit=limit,
            price_max=price_max
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting furnished properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/verified', methods=['GET'])
def get_firestore_verified():
    """
    Get verified properties.

    Query params:
        - limit: Number of results (default 100)
        - price_min: Minimum price filter (optional)
        - price_max: Maximum price filter (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_verified_properties

        limit = int(request.args.get('limit', 100))
        price_min = request.args.get('price_min')
        price_max = request.args.get('price_max')
        price_min = int(price_min) if price_min else None
        price_max = int(price_max) if price_max else None

        properties = get_verified_properties(
            limit=limit,
            price_min=price_min,
            price_max=price_max
        )

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting verified properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/trending', methods=['GET'])
def get_firestore_trending():
    """
    Get trending properties (highest view count).

    Query params:
        - limit: Number of results (default 50)
    """
    try:
        from core.firestore_queries_enterprise import get_trending_properties

        limit = int(request.args.get('limit', 50))

        properties = get_trending_properties(limit=limit)

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting trending properties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/hot-deals', methods=['GET'])
def get_firestore_hot_deals():
    """
    Get hot deal properties (auto-tagged as hot_deal).

    Query params:
        - limit: Number of results (default 50)
    """
    try:
        from core.firestore_queries_enterprise import get_hot_deals

        limit = int(request.args.get('limit', 50))

        properties = get_hot_deals(limit=limit)

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting hot deals: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/by-lga/<lga>', methods=['GET'])
def get_firestore_by_lga(lga):
    """
    Get properties by LGA (Local Government Area).

    Query params:
        - limit: Number of results (default 100)
        - bedrooms_min: Minimum bedrooms (optional)
        - price_max: Maximum price (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_properties_by_lga

        limit = int(request.args.get('limit', 100))
        bedrooms_min = request.args.get('bedrooms_min')
        price_max = request.args.get('price_max')
        bedrooms_min = int(bedrooms_min) if bedrooms_min else None
        price_max = int(price_max) if price_max else None

        properties = get_properties_by_lga(
            lga=lga,
            limit=limit,
            bedrooms_min=bedrooms_min,
            price_max=price_max
        )

        return jsonify({
            'success': True,
            'lga': lga,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting properties by LGA: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/by-area/<area>', methods=['GET'])
def get_firestore_by_area(area):
    """
    Get properties by area.

    Query params:
        - limit: Number of results (default 100)
        - listing_type: Filter by listing type (optional)
    """
    try:
        from core.firestore_queries_enterprise import get_properties_by_area

        limit = int(request.args.get('limit', 100))
        listing_type = request.args.get('listing_type')

        properties = get_properties_by_area(
            area=area,
            limit=limit,
            listing_type=listing_type
        )

        return jsonify({
            'success': True,
            'area': area,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting properties by area: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/firestore/properties/new-on-market', methods=['GET'])
def get_firestore_new_on_market():
    """
    Get newly listed properties.

    Query params:
        - days: Days on market (default 7)
        - limit: Number of results (default 100)
    """
    try:
        from core.firestore_queries_enterprise import get_new_on_market

        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 100))

        properties = get_new_on_market(days=days, limit=limit)

        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties
        })

    except Exception as e:
        logger.error(f"Error getting new properties: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'

    logger.info(f"Starting API server on port {port}")
    logger.info(f"Debug mode: {debug}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
