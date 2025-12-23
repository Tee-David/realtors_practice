"""
Authentication and Authorization Module
Provides API key and JWT-based authentication for the API server
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Callable
import logging

logger = logging.getLogger(__name__)

# Load configuration from environment
API_KEYS = set(os.getenv('API_KEYS', '').split(',')) if os.getenv('API_KEYS') else set()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
AUTH_ENABLED = os.getenv('AUTH_ENABLED', 'false').lower() == 'true'


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication

    Usage:
        @app.route('/api/endpoint')
        @require_api_key
        def my_endpoint():
            return jsonify({'data': 'protected'})

    API key should be provided in header: X-API-Key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if disabled (for development)
        if not AUTH_ENABLED:
            return f(*args, **kwargs)

        # Check for API key in header
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            logger.warning(f"API key missing for {request.endpoint}")
            return jsonify({
                'error': 'API key required',
                'message': 'Provide API key in X-API-Key header'
            }), 401

        if api_key not in API_KEYS:
            logger.warning(f"Invalid API key attempt for {request.endpoint}")
            return jsonify({
                'error': 'Invalid API key'
            }), 401

        # API key is valid
        return f(*args, **kwargs)

    return decorated_function


def create_jwt_token(user_id: str, additional_claims: Optional[Dict] = None) -> str:
    """
    Create a JWT token for a user

    Args:
        user_id: User identifier
        additional_claims: Additional claims to include in token

    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def require_jwt(f: Callable) -> Callable:
    """
    Decorator to require JWT authentication

    Usage:
        @app.route('/api/endpoint')
        @require_jwt
        def my_endpoint():
            user_id = request.user_id
            return jsonify({'data': f'Hello {user_id}'})

    JWT should be provided in header: Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if disabled (for development)
        if not AUTH_ENABLED:
            request.user_id = 'dev-user'
            return f(*args, **kwargs)

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            logger.warning(f"Missing Bearer token for {request.endpoint}")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Provide JWT token in Authorization header as: Bearer <token>'
            }), 401

        token = auth_header.replace('Bearer ', '', 1)

        # Decode and validate token
        payload = decode_jwt_token(token)

        if not payload:
            return jsonify({
                'error': 'Invalid or expired token'
            }), 401

        # Attach user info to request
        request.user_id = payload.get('user_id')
        request.token_payload = payload

        return f(*args, **kwargs)

    return decorated_function


def require_auth(f: Callable) -> Callable:
    """
    Decorator that accepts either API key OR JWT

    Usage:
        @app.route('/api/endpoint')
        @require_auth
        def my_endpoint():
            return jsonify({'data': 'protected'})

    Accepts either:
    - X-API-Key header with API key
    - Authorization: Bearer <jwt> header
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if disabled (for development)
        if not AUTH_ENABLED:
            request.user_id = 'dev-user'
            return f(*args, **kwargs)

        # Try API key first
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key in API_KEYS:
            request.user_id = 'api-key-user'
            return f(*args, **kwargs)

        # Try JWT
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '', 1)
            payload = decode_jwt_token(token)

            if payload:
                request.user_id = payload.get('user_id')
                request.token_payload = payload
                return f(*args, **kwargs)

        # No valid authentication
        logger.warning(f"Authentication failed for {request.endpoint}")
        return jsonify({
            'error': 'Authentication required',
            'message': 'Provide either X-API-Key or Authorization: Bearer <token> header'
        }), 401

    return decorated_function


# Optional: Rate limiting per user
def get_user_identifier() -> str:
    """
    Get user identifier for rate limiting
    Returns user_id from JWT or 'anonymous' for API keys
    """
    if hasattr(request, 'user_id'):
        return request.user_id
    return request.remote_addr  # Fall back to IP address
