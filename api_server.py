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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

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
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

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
