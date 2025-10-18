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
from api.helpers.data_reader import DataReader
from api.helpers.log_parser import LogParser
from api.helpers.config_manager import ConfigManager
from api.helpers.scraper_manager import ScraperManager
from api.helpers.stats_generator import StatsGenerator

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
