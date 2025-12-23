"""
Security Middleware and Utilities
Provides security headers, input validation, and protection mechanisms
"""

import re
import os
from pathlib import Path
from flask import Flask, request, jsonify
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def add_security_headers(app: Flask):
    """
    Add security headers to all responses

    Headers added:
    - Content-Security-Policy
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    """
    @app.after_request
    def set_security_headers(response):
        # Content Security Policy - restrict resources
        response.headers['Content-Security-Policy'] = "default-src 'self'"

        # Prevent MIME-sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HSTS - Force HTTPS (only if using HTTPS)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response


def configure_cors(app: Flask):
    """
    Configure CORS with proper restrictions

    In production, set ALLOWED_ORIGINS environment variable
    """
    from flask_cors import CORS

    # Get allowed origins from environment
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    origins_list = [origin.strip() for origin in allowed_origins.split(',')]

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": origins_list,
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
            "expose_headers": ["Content-Range", "X-Total-Count"],
            "max_age": 3600,
            "supports_credentials": True
        }
    })

    logger.info(f"CORS configured for origins: {origins_list}")


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate to max length
    text = str(text)[:max_length]

    # Remove potentially dangerous characters
    # Allow alphanumeric, spaces, and common punctuation
    text = re.sub(r'[<>"\';()]', '', text)

    return text.strip()


def validate_filename(filename: str) -> bool:
    """
    Validate filename to prevent path traversal

    Args:
        filename: Filename to validate

    Returns:
        True if safe, False otherwise
    """
    if not filename:
        return False

    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        logger.warning(f"Path traversal attempt detected: {filename}")
        return False

    # Check for valid characters only
    if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
        logger.warning(f"Invalid filename characters: {filename}")
        return False

    return True


def safe_file_path(base_dir: Path, filename: str) -> Path:
    """
    Safely construct file path preventing path traversal

    Args:
        base_dir: Base directory
        filename: Filename (will be validated)

    Returns:
        Safe absolute path

    Raises:
        ValueError: If path is unsafe
    """
    if not validate_filename(filename):
        raise ValueError(f"Invalid filename: {filename}")

    # Construct path
    file_path = (base_dir / filename).resolve()

    # Ensure it's within base_dir
    if not str(file_path).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal attempt: {filename}")

    return file_path


def validate_json_input(required_fields: list = None) -> Dict[str, Any]:
    """
    Validate and parse JSON input from request

    Args:
        required_fields: List of required field names

    Returns:
        Parsed JSON data

    Raises:
        ValueError: If validation fails
    """
    if not request.is_json:
        raise ValueError("Content-Type must be application/json")

    try:
        data = request.get_json()
    except Exception as e:
        raise ValueError(f"Invalid JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object")

    # Check required fields
    if required_fields:
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return data


def sanitize_url(url: str) -> str:
    """
    Sanitize URL to prevent SSRF and other attacks

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL
    """
    if not url:
        return ""

    # Basic URL validation
    if not re.match(r'^https?://', url):
        raise ValueError("URL must start with http:// or https://")

    # Block localhost/private IPs in production
    if os.getenv('ENV') == 'production':
        if any(pattern in url.lower() for pattern in ['localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.', '172.']):
            raise ValueError("Private/local URLs not allowed in production")

    return url


def rate_limit_check(identifier: str, max_requests: int = 100, window_seconds: int = 3600) -> bool:
    """
    Simple in-memory rate limiting check

    Args:
        identifier: User/IP identifier
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds

    Returns:
        True if within limit, False if exceeded
    """
    # This is a simple implementation
    # For production, use Redis or similar
    from datetime import datetime, timedelta

    # Store in app context (simple implementation)
    if not hasattr(rate_limit_check, 'requests'):
        rate_limit_check.requests = {}

    now = datetime.now()
    cutoff = now - timedelta(seconds=window_seconds)

    # Get requests for this identifier
    if identifier not in rate_limit_check.requests:
        rate_limit_check.requests[identifier] = []

    # Clean old requests
    rate_limit_check.requests[identifier] = [
        req_time for req_time in rate_limit_check.requests[identifier]
        if req_time > cutoff
    ]

    # Check limit
    if len(rate_limit_check.requests[identifier]) >= max_requests:
        logger.warning(f"Rate limit exceeded for {identifier}")
        return False

    # Add current request
    rate_limit_check.requests[identifier].append(now)
    return True


def add_error_handlers(app: Flask):
    """
    Add secure error handlers that don't leak information

    Args:
        app: Flask application
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request format'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        # Log the actual error
        logger.error(f"Internal server error: {error}")

        # Don't expose error details to client
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def setup_security(app: Flask):
    """
    Set up all security features for the Flask app

    Call this function after creating your Flask app:

    ```python
    from core.security import setup_security

    app = Flask(__name__)
    setup_security(app)
    ```

    Args:
        app: Flask application
    """
    # Add security headers
    add_security_headers(app)

    # Configure CORS
    configure_cors(app)

    # Add error handlers
    add_error_handlers(app)

    logger.info("Security features enabled")
