"""
Configuration Management Routes
Endpoints for managing environment variables and system configuration
"""

from flask import Blueprint, request, jsonify
import os
from pathlib import Path
from typing import Dict, Any

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# Path to .env file
ENV_FILE_PATH = Path(__file__).parent.parent.parent / '.env'

# Define which environment variables can be edited
EDITABLE_ENV_VARS = {
    # Application Settings
    'ENV': {'type': 'select', 'options': ['development', 'production'], 'description': 'Application environment'},
    'DEBUG': {'type': 'boolean', 'description': 'Enable debug mode'},
    'API_HOST': {'type': 'text', 'description': 'API host address'},
    'API_PORT': {'type': 'number', 'description': 'API port number'},

    # Security Settings
    'AUTH_ENABLED': {'type': 'boolean', 'description': 'Enable API authentication'},
    'API_KEYS': {'type': 'password', 'description': 'Comma-separated API keys'},
    'JWT_SECRET_KEY': {'type': 'password', 'description': 'JWT secret key'},
    'JWT_EXPIRATION_HOURS': {'type': 'number', 'description': 'JWT token expiration (hours)'},
    'ALLOWED_ORIGINS': {'type': 'text', 'description': 'Comma-separated CORS origins'},

    # Scraping Settings
    'RP_DEBUG': {'type': 'boolean', 'description': 'Enable scraper debug mode'},
    'RP_HEADLESS': {'type': 'boolean', 'description': 'Run browser in headless mode'},
    'RP_GEOCODE': {'type': 'boolean', 'description': 'Enable geocoding'},
    'RP_PAGE_CAP': {'type': 'number', 'description': 'Maximum pages to scrape per site'},
    'RP_MAX_GEOCODES': {'type': 'number', 'description': 'Maximum geocoding requests'},
    'RP_NO_IMAGES': {'type': 'boolean', 'description': 'Disable image downloads'},
    'RP_SITE_WORKERS': {'type': 'number', 'description': 'Number of parallel workers'},
    'RP_NO_AUTO_WATCHER': {'type': 'boolean', 'description': 'Disable auto file watcher'},

    # Firestore Settings
    'FIREBASE_SERVICE_ACCOUNT': {'type': 'text', 'description': 'Firebase service account JSON file'},
    'FIRESTORE_COLLECTION': {'type': 'text', 'description': 'Firestore collection name'},
    'FIRESTORE_ARCHIVE_COLLECTION': {'type': 'text', 'description': 'Archive collection name'},
    'FIRESTORE_ENABLED': {'type': 'boolean', 'description': 'Enable Firestore integration'},
    'FIRESTORE_AUTO_AGGREGATE': {'type': 'boolean', 'description': 'Auto-aggregate data'},

    # GitHub Settings
    'GITHUB_TOKEN': {'type': 'password', 'description': 'GitHub personal access token'},
    'GITHUB_REPOSITORY': {'type': 'text', 'description': 'GitHub repository (owner/repo)'},
    'GITHUB_OWNER': {'type': 'text', 'description': 'GitHub repository owner'},
    'GITHUB_REPO': {'type': 'text', 'description': 'GitHub repository name'},

    # Email Settings
    'SMTP_HOST': {'type': 'text', 'description': 'SMTP server host'},
    'SMTP_PORT': {'type': 'number', 'description': 'SMTP server port'},
    'SMTP_USERNAME': {'type': 'text', 'description': 'SMTP username'},
    'SMTP_PASSWORD': {'type': 'password', 'description': 'SMTP password'},
    'FROM_EMAIL': {'type': 'email', 'description': 'From email address'},
    'NOTIFICATION_RECIPIENTS': {'type': 'text', 'description': 'Comma-separated recipient emails'},

    # Rate Limiting
    'RATE_LIMIT_PER_HOUR': {'type': 'number', 'description': 'Rate limit per hour'},
    'RATE_LIMIT_PER_DAY': {'type': 'number', 'description': 'Rate limit per day'},

    # Logging
    'LOG_LEVEL': {'type': 'select', 'options': ['DEBUG', 'INFO', 'WARNING', 'ERROR'], 'description': 'Logging level'},
    'LOG_FILE': {'type': 'text', 'description': 'Log file path'},
    'SECURITY_AUDIT_LOG': {'type': 'boolean', 'description': 'Enable security audit logging'},
}

def parse_env_file() -> Dict[str, str]:
    """Parse .env file and return key-value pairs"""
    env_vars = {}

    if not ENV_FILE_PATH.exists():
        return env_vars

    with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars

def write_env_file(env_vars: Dict[str, str]) -> None:
    """Write environment variables back to .env file"""
    lines = []
    lines.append("# Environment Configuration")
    lines.append("# Auto-generated - Do not edit manually")
    lines.append("")

    # Group by category
    categories = {
        'APPLICATION SETTINGS': ['ENV', 'DEBUG', 'API_HOST', 'API_PORT'],
        'SECURITY SETTINGS': ['AUTH_ENABLED', 'API_KEYS', 'JWT_SECRET_KEY', 'JWT_EXPIRATION_HOURS', 'ALLOWED_ORIGINS'],
        'SCRAPING SETTINGS': ['RP_DEBUG', 'RP_HEADLESS', 'RP_GEOCODE', 'RP_PAGE_CAP', 'RP_MAX_GEOCODES', 'RP_NO_IMAGES', 'RP_SITE_WORKERS', 'RP_NO_AUTO_WATCHER'],
        'FIREBASE / FIRESTORE': ['FIREBASE_SERVICE_ACCOUNT', 'FIRESTORE_COLLECTION', 'FIRESTORE_ARCHIVE_COLLECTION', 'FIRESTORE_ENABLED', 'FIRESTORE_AUTO_AGGREGATE'],
        'GITHUB ACTIONS': ['GITHUB_TOKEN', 'GITHUB_REPOSITORY', 'GITHUB_OWNER', 'GITHUB_REPO'],
        'EMAIL NOTIFICATIONS': ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'FROM_EMAIL', 'NOTIFICATION_RECIPIENTS'],
        'RATE LIMITING': ['RATE_LIMIT_PER_HOUR', 'RATE_LIMIT_PER_DAY'],
        'LOGGING': ['LOG_LEVEL', 'LOG_FILE', 'SECURITY_AUDIT_LOG'],
    }

    for category, keys in categories.items():
        lines.append("# " + "=" * 76)
        lines.append(f"# {category}")
        lines.append("# " + "=" * 76)
        lines.append("")

        for key in keys:
            if key in env_vars:
                lines.append(f"{key}={env_vars[key]}")

        lines.append("")

    with open(ENV_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

@config_bp.route('/env', methods=['GET'])
def get_env_vars():
    """Get all editable environment variables"""
    try:
        env_vars = parse_env_file()

        # Format for frontend
        formatted = []
        for key, config in EDITABLE_ENV_VARS.items():
            value = env_vars.get(key, '')

            # Convert boolean strings
            if config['type'] == 'boolean':
                value = value.lower() in ['true', '1', 'yes']
            # Convert number strings
            elif config['type'] == 'number':
                try:
                    value = int(value) if value else 0
                except ValueError:
                    value = 0

            formatted.append({
                'key': key,
                'value': value,
                'type': config['type'],
                'description': config['description'],
                'options': config.get('options', [])
            })

        return jsonify({
            'success': True,
            'variables': formatted,
            'total': len(formatted)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_bp.route('/env', methods=['POST'])
def update_env_vars():
    """Update environment variables"""
    try:
        data = request.get_json()
        updates = data.get('variables', {})

        # Read current env
        env_vars = parse_env_file()

        # Validate and update
        for key, value in updates.items():
            if key not in EDITABLE_ENV_VARS:
                return jsonify({
                    'success': False,
                    'error': f'Variable {key} is not editable'
                }), 400

            # Convert booleans to strings
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                value = str(value)

            env_vars[key] = value

        # Write back to file
        write_env_file(env_vars)

        # Also update os.environ for immediate effect
        for key, value in updates.items():
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                value = str(value)
            os.environ[key] = value

        return jsonify({
            'success': True,
            'message': f'Updated {len(updates)} environment variable(s)',
            'updated_count': len(updates)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_bp.route('/env/test', methods=['POST'])
def test_env_change():
    """Test if environment variable changes take effect"""
    try:
        data = request.get_json()
        key = data.get('key')

        if not key:
            return jsonify({'success': False, 'error': 'No key provided'}), 400

        # Check current value in os.environ
        current_value = os.environ.get(key)
        file_value = parse_env_file().get(key)

        return jsonify({
            'success': True,
            'key': key,
            'current_value': current_value,
            'file_value': file_value,
            'in_sync': current_value == file_value
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_bp.route('/env/categories', methods=['GET'])
def get_env_categories():
    """Get environment variables grouped by category"""
    try:
        env_vars = parse_env_file()

        categories = {
            'Application Settings': [],
            'Security Settings': [],
            'Scraping Settings': [],
            'Firestore Settings': [],
            'GitHub Settings': [],
            'Email Settings': [],
            'Rate Limiting': [],
            'Logging': [],
        }

        category_mapping = {
            'ENV': 'Application Settings',
            'DEBUG': 'Application Settings',
            'API_HOST': 'Application Settings',
            'API_PORT': 'Application Settings',
            'AUTH_ENABLED': 'Security Settings',
            'API_KEYS': 'Security Settings',
            'JWT_SECRET_KEY': 'Security Settings',
            'JWT_EXPIRATION_HOURS': 'Security Settings',
            'ALLOWED_ORIGINS': 'Security Settings',
            'RP_DEBUG': 'Scraping Settings',
            'RP_HEADLESS': 'Scraping Settings',
            'RP_GEOCODE': 'Scraping Settings',
            'RP_PAGE_CAP': 'Scraping Settings',
            'RP_MAX_GEOCODES': 'Scraping Settings',
            'RP_NO_IMAGES': 'Scraping Settings',
            'RP_SITE_WORKERS': 'Scraping Settings',
            'RP_NO_AUTO_WATCHER': 'Scraping Settings',
            'FIREBASE_SERVICE_ACCOUNT': 'Firestore Settings',
            'FIRESTORE_COLLECTION': 'Firestore Settings',
            'FIRESTORE_ARCHIVE_COLLECTION': 'Firestore Settings',
            'FIRESTORE_ENABLED': 'Firestore Settings',
            'FIRESTORE_AUTO_AGGREGATE': 'Firestore Settings',
            'GITHUB_TOKEN': 'GitHub Settings',
            'GITHUB_REPOSITORY': 'GitHub Settings',
            'GITHUB_OWNER': 'GitHub Settings',
            'GITHUB_REPO': 'GitHub Settings',
            'SMTP_HOST': 'Email Settings',
            'SMTP_PORT': 'Email Settings',
            'SMTP_USERNAME': 'Email Settings',
            'SMTP_PASSWORD': 'Email Settings',
            'FROM_EMAIL': 'Email Settings',
            'NOTIFICATION_RECIPIENTS': 'Email Settings',
            'RATE_LIMIT_PER_HOUR': 'Rate Limiting',
            'RATE_LIMIT_PER_DAY': 'Rate Limiting',
            'LOG_LEVEL': 'Logging',
            'LOG_FILE': 'Logging',
            'SECURITY_AUDIT_LOG': 'Logging',
        }

        for key, config in EDITABLE_ENV_VARS.items():
            value = env_vars.get(key, '')
            category = category_mapping.get(key, 'Other')

            # Convert boolean strings
            if config['type'] == 'boolean':
                value = value.lower() in ['true', '1', 'yes']
            # Convert number strings
            elif config['type'] == 'number':
                try:
                    value = int(value) if value else 0
                except ValueError:
                    value = 0

            if category in categories:
                categories[category].append({
                    'key': key,
                    'value': value,
                    'type': config['type'],
                    'description': config['description'],
                    'options': config.get('options', [])
                })

        return jsonify({
            'success': True,
            'categories': categories
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
