"""
Authentication Routes for Flask API
Provides endpoints for user registration, login, and management
"""

import logging
from flask import Blueprint, request, jsonify, make_response
from functools import wraps
from typing import Dict, Optional
from datetime import datetime, timedelta

from core.firebase_auth import get_firebase_auth_manager
from core.auth import create_jwt_token, decode_jwt_token
from core.security import validate_json_input, sanitize_input

logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize Firebase Auth Manager
auth_manager = get_firebase_auth_manager()


def require_firebase_auth(f):
    """
    Decorator to require Firebase authentication
    Validates Firebase ID token from Authorization header
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authentication required',
                'message': 'Provide Firebase ID token in Authorization header as: Bearer <token>'
            }), 401

        token = auth_header.replace('Bearer ', '', 1)

        try:
            # Verify Firebase token
            decoded_token = auth_manager.verify_id_token(token)

            # Attach user info to request
            request.user_uid = decoded_token.get('uid')
            request.user_email = decoded_token.get('email')
            request.token_payload = decoded_token

            return f(*args, **kwargs)

        except ValueError as e:
            return jsonify({
                'error': 'Invalid token',
                'message': str(e)
            }), 401
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid or expired token'
            }), 401

    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user

    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "displayName": "John Doe" (optional)
    }

    Returns:
    {
        "success": true,
        "user": {...},
        "customToken": "..." (for immediate login)
    }
    """
    try:
        # Validate input
        data = validate_json_input(['email', 'password'])

        email = sanitize_input(data.get('email'), max_length=255)
        password = data.get('password')  # Don't sanitize passwords
        display_name = sanitize_input(data.get('displayName', ''), max_length=255) or None

        # Validate email format
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400

        # Create user in Firebase
        user = auth_manager.create_user(
            email=email,
            password=password,
            display_name=display_name,
            additional_claims={'role': 'user'}  # Default role
        )

        # Create custom token for immediate login
        custom_token = auth_manager.create_custom_token(user['uid'])

        logger.info(f"User registered successfully: {email}")

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user,
            'customToken': custom_token
        }), 201

    except ValueError as e:
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'error': 'Registration failed',
            'message': 'An error occurred during registration'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verify Firebase ID token

    Request body:
    {
        "idToken": "firebase-id-token"
    }

    Returns:
    {
        "valid": true,
        "user": {...}
    }
    """
    try:
        data = validate_json_input(['idToken'])
        id_token = data.get('idToken')

        # Verify token
        decoded_token = auth_manager.verify_id_token(id_token)

        # Get full user information
        user = auth_manager.get_user_by_uid(decoded_token['uid'])

        return jsonify({
            'valid': True,
            'user': user,
            'claims': decoded_token
        }), 200

    except ValueError as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 401
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({
            'valid': False,
            'error': 'Token verification failed'
        }), 500


@auth_bp.route('/user/me', methods=['GET'])
@require_firebase_auth
def get_current_user():
    """
    Get current user information

    Requires: Authorization: Bearer <firebase-id-token>

    Returns:
    {
        "user": {...}
    }
    """
    try:
        user = auth_manager.get_user_by_uid(request.user_uid)

        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404

        return jsonify({
            'user': user
        }), 200

    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return jsonify({
            'error': 'Failed to get user information'
        }), 500


@auth_bp.route('/user/me', methods=['PUT'])
@require_firebase_auth
def update_current_user():
    """
    Update current user information

    Request body:
    {
        "displayName": "New Name",
        "photoURL": "https://..."
    }

    Returns:
    {
        "success": true,
        "user": {...}
    }
    """
    try:
        data = request.get_json() or {}

        # Build update parameters
        update_params = {}

        if 'displayName' in data:
            update_params['display_name'] = sanitize_input(data['displayName'], max_length=255)

        if 'photoURL' in data:
            update_params['photo_url'] = data['photoURL']

        # Update user
        user = auth_manager.update_user(request.user_uid, **update_params)

        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user
        }), 200

    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return jsonify({
            'error': 'Failed to update user'
        }), 500


@auth_bp.route('/user/<uid>', methods=['GET'])
@require_firebase_auth
def get_user_by_id(uid: str):
    """
    Get user information by UID

    Requires: Authorization: Bearer <firebase-id-token>

    Returns:
    {
        "user": {...}
    }
    """
    try:
        # Check if user has permission (admin or self)
        is_admin = request.token_payload.get('role') == 'admin'
        is_self = request.user_uid == uid

        if not (is_admin or is_self):
            return jsonify({
                'error': 'Permission denied',
                'message': 'You can only view your own profile'
            }), 403

        user = auth_manager.get_user_by_uid(uid)

        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404

        return jsonify({
            'user': user
        }), 200

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return jsonify({
            'error': 'Failed to get user information'
        }), 500


@auth_bp.route('/users', methods=['GET'])
@require_firebase_auth
def list_users():
    """
    List all users (admin only)

    Query parameters:
    - limit: Maximum number of users to return (default: 100)

    Returns:
    {
        "users": [...],
        "total": 100
    }
    """
    try:
        # Check if user is admin
        is_admin = request.token_payload.get('role') == 'admin'

        if not is_admin:
            return jsonify({
                'error': 'Permission denied',
                'message': 'Only administrators can list users'
            }), 403

        # Get limit from query parameters
        limit = min(int(request.args.get('limit', 100)), 1000)

        # List users
        users = auth_manager.list_users(max_results=limit)

        return jsonify({
            'users': users,
            'total': len(users)
        }), 200

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return jsonify({
            'error': 'Failed to list users'
        }), 500


@auth_bp.route('/user/<uid>', methods=['DELETE'])
@require_firebase_auth
def delete_user(uid: str):
    """
    Delete user (admin only or self)

    Returns:
    {
        "success": true,
        "message": "User deleted successfully"
    }
    """
    try:
        # Check if user has permission (admin or self)
        is_admin = request.token_payload.get('role') == 'admin'
        is_self = request.user_uid == uid

        if not (is_admin or is_self):
            return jsonify({
                'error': 'Permission denied',
                'message': 'You can only delete your own account'
            }), 403

        # Delete user
        auth_manager.delete_user(uid)

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({
            'error': 'Failed to delete user',
            'message': str(e)
        }), 500


@auth_bp.route('/user/<uid>/role', methods=['PUT'])
@require_firebase_auth
def update_user_role(uid: str):
    """
    Update user role (admin only)

    Request body:
    {
        "role": "admin" | "user"
    }

    Returns:
    {
        "success": true,
        "message": "Role updated successfully"
    }
    """
    try:
        # Check if user is admin
        is_admin = request.token_payload.get('role') == 'admin'

        if not is_admin:
            return jsonify({
                'error': 'Permission denied',
                'message': 'Only administrators can update user roles'
            }), 403

        data = validate_json_input(['role'])
        role = data.get('role')

        # Validate role
        if role not in ['admin', 'user']:
            return jsonify({
                'error': 'Invalid role',
                'message': 'Role must be either "admin" or "user"'
            }), 400

        # Set custom claims
        auth_manager.set_custom_claims(uid, {'role': role})

        # Revoke refresh tokens to force re-authentication with new claims
        auth_manager.revoke_refresh_tokens(uid)

        return jsonify({
            'success': True,
            'message': 'Role updated successfully. User must re-authenticate.'
        }), 200

    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        return jsonify({
            'error': 'Failed to update user role',
            'message': str(e)
        }), 500


@auth_bp.route('/password-reset', methods=['POST'])
def request_password_reset():
    """
    Request password reset link

    Request body:
    {
        "email": "user@example.com"
    }

    Returns:
    {
        "success": true,
        "message": "Password reset link sent",
        "resetLink": "..." (in development only)
    }
    """
    try:
        data = validate_json_input(['email'])
        email = sanitize_input(data.get('email'), max_length=255)

        # Generate password reset link
        reset_link = auth_manager.generate_password_reset_link(email)

        # In production, send email instead of returning link
        # For development, return the link
        import os
        is_dev = os.getenv('ENV', 'development') == 'development'

        response = {
            'success': True,
            'message': 'Password reset link generated'
        }

        if is_dev:
            response['resetLink'] = reset_link
            response['message'] = 'Password reset link generated (development mode)'

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating password reset link: {e}")
        return jsonify({
            'error': 'Failed to generate password reset link',
            'message': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@require_firebase_auth
def logout():
    """
    Logout user (revoke all refresh tokens)

    Returns:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    try:
        # Revoke all refresh tokens for the user
        auth_manager.revoke_refresh_tokens(request.user_uid)

        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error logging out: {e}")
        return jsonify({
            'error': 'Failed to logout',
            'message': str(e)
        }), 500


@auth_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for authentication service

    Returns:
    {
        "status": "healthy",
        "firebase_initialized": true
    }
    """
    return jsonify({
        'status': 'healthy',
        'service': 'authentication',
        'firebase_initialized': auth_manager.initialized,
        'timestamp': datetime.now().isoformat()
    }), 200
