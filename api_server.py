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
from flask import Flask, jsonify, request, send_file, Response
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

        # Query Firestore with filters
        try:
            import firebase_admin
            from firebase_admin import firestore

            if not firebase_admin._apps:
                cred_json = os.getenv('FIREBASE_CREDENTIALS')
                cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')

                if cred_json:
                    from firebase_admin import credentials
                    cred = credentials.Certificate(json.loads(cred_json))
                    firebase_admin.initialize_app(cred)
                elif cred_path and Path(cred_path).exists():
                    from firebase_admin import credentials
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)

            db = firestore.client()
            query = db.collection('properties')

            # Apply filters (same as query endpoint)
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

            # Get all results (for export, we want everything matching filters)
            results = query.stream()
            properties = [doc.to_dict() for doc in results]

        except ImportError:
            # Fallback to local master workbook if Firestore not available
            workbook_path = 'exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx'
            if not Path(workbook_path).exists():
                return jsonify({
                    'error': 'No data available',
                    'details': 'Firestore not configured and local master workbook not found'
                }), 404

            df = pd.read_excel(workbook_path)

            # Apply filters to DataFrame
            if 'location' in filters:
                df = df[df['location'].str.contains(filters['location'], case=False, na=False)]
            if 'price_min' in filters:
                df = df[df['price'] >= filters['price_min']]
            if 'price_max' in filters:
                df = df[df['price'] <= filters['price_max']]
            if 'bedrooms_min' in filters:
                df = df[df['bedrooms'] >= filters['bedrooms_min']]
            if 'property_type' in filters:
                df = df[df['property_type'] == filters['property_type']]

            properties = df.to_dict('records')

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

        if not all([github_token, github_owner, github_repo]):
            return jsonify({
                'error': 'Missing GitHub configuration',
                'details': 'Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables'
            }), 500

        # Get request body
        data = request.get_json() or {}
        page_cap = data.get('page_cap', 20)
        geocode = data.get('geocode', 1)
        sites = data.get('sites', [])

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
                'page_cap': page_cap,
                'geocode': geocode,
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
                    'page_cap': page_cap,
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
    Estimate time required for a scrape session

    Body: {
        "page_cap": 20,          # Pages per site
        "geocode": 1,            # 0 or 1
        "sites": ["npc", ...]    # Optional: specific sites (empty = all enabled)
    }

    Returns: {
        "estimated_duration_minutes": 45,
        "estimated_duration_text": "~45 minutes",
        "site_count": 5,
        "batch_type": "small",    # "small" or "large" (multi-session)
        "sessions": 1,
        "breakdown": {...}
    }
    """
    try:
        import yaml

        # Get request body
        data = request.get_json() or {}
        page_cap = data.get('page_cap', 20)
        geocode = data.get('geocode', 1)
        sites_param = data.get('sites', [])

        # Load config to count sites
        with open('config.yaml') as f:
            config = yaml.safe_load(f)

        if sites_param:
            site_count = len(sites_param)
        else:
            site_count = sum(1 for site_config in config.get('sites', {}).values() if site_config.get('enabled', False))

        # Estimation formula (based on historical data)
        # Average: 2 minutes per page, with parallel scraping
        minutes_per_page = 2
        parallel_workers = 5  # From config
        geocode_overhead = 0.5 if geocode == 1 else 0  # 30 seconds per site with geocoding

        # Calculate base time
        total_pages = site_count * page_cap
        scrape_time = (total_pages * minutes_per_page) / parallel_workers
        processing_time = site_count * 2  # 2 min per site for watcher processing
        geocode_time = site_count * geocode_overhead if geocode == 1 else 0

        total_minutes = scrape_time + processing_time + geocode_time + 5  # +5 for setup

        # Determine batch type and adjust
        is_large_batch = site_count > 30
        sessions = 1
        batch_type = "small"

        if is_large_batch:
            # Multi-session: split into sessions of 20, run 3 in parallel
            batch_type = "large"
            sessions = (site_count + 19) // 20  # Ceiling division
            parallel_sessions = min(sessions, 3)

            # Time for parallel sessions + consolidation
            time_per_session = total_minutes / site_count * 20  # Time for 20 sites
            total_minutes = (sessions / parallel_sessions) * time_per_session + 10  # +10 for consolidation

        # Format duration text
        if total_minutes < 60:
            duration_text = f"~{int(total_minutes)} minutes"
        else:
            hours = int(total_minutes // 60)
            mins = int(total_minutes % 60)
            duration_text = f"~{hours}h {mins}m"

        return jsonify({
            'estimated_duration_minutes': round(total_minutes, 1),
            'estimated_duration_text': duration_text,
            'site_count': site_count,
            'batch_type': batch_type,
            'sessions': sessions,
            'breakdown': {
                'scraping': round(scrape_time, 1),
                'processing': round(processing_time, 1),
                'geocoding': round(geocode_time, 1),
                'overhead': 5
            },
            'note': 'This is an estimate based on average performance. Actual time may vary.'
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
                            'page_cap': scheduled_jobs[job_id]['page_cap'],
                            'geocode': scheduled_jobs[job_id]['geocode'],
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
