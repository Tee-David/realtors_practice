"""
Firebase Authentication Manager
Handles user authentication, registration, and management using Firebase Auth
"""

import os
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, auth
from pathlib import Path

logger = logging.getLogger(__name__)


class FirebaseAuthManager:
    """
    Manages Firebase Authentication operations

    Features:
    - User registration with email/password
    - User login and token verification
    - Password reset and email verification
    - User management (list, update, delete)
    - Custom claims for role-based access
    - Session management with custom tokens
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase Auth Manager

        Args:
            credentials_path: Path to Firebase service account JSON file
        """
        import json

        self.initialized = False

        # Initialize Firebase Admin SDK if not already initialized
        try:
            if not firebase_admin._apps:
                # Try FIREBASE_CREDENTIALS environment variable first (JSON string)
                cred_json = os.getenv('FIREBASE_CREDENTIALS')
                if cred_json:
                    cred = credentials.Certificate(json.loads(cred_json))
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK initialized from FIREBASE_CREDENTIALS environment variable")
                else:
                    # Fall back to file path from parameter or environment
                    if not credentials_path:
                        credentials_path = os.getenv(
                            'FIREBASE_SERVICE_ACCOUNT',
                            'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'
                        )

                    # Convert to absolute path if needed
                    if not os.path.isabs(credentials_path):
                        # Look in backend directory
                        backend_dir = Path(__file__).parent.parent
                        credentials_path = str(backend_dir / credentials_path)

                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred)
                    logger.info(f"Firebase Admin SDK initialized with credentials: {credentials_path}")
            else:
                logger.info("Firebase Admin SDK already initialized")

            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise

    def create_user(self, email: str, password: str, display_name: Optional[str] = None,
                   additional_claims: Optional[Dict] = None) -> Dict:
        """
        Create a new user with email and password

        Args:
            email: User email address
            password: User password (min 6 characters)
            display_name: Optional display name
            additional_claims: Optional custom claims (roles, permissions)

        Returns:
            Dict with user information

        Raises:
            ValueError: If user creation fails
        """
        try:
            # Validate password
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters")

            # Create user
            user_params = {
                'email': email,
                'password': password,
                'email_verified': False,
                'disabled': False
            }

            if display_name:
                user_params['display_name'] = display_name

            user = auth.create_user(**user_params)

            # Set custom claims if provided
            if additional_claims:
                auth.set_custom_user_claims(user.uid, additional_claims)

            logger.info(f"Created user: {email} (uid: {user.uid})")

            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'email_verified': user.email_verified,
                'created_at': datetime.now().isoformat()
            }

        except auth.EmailAlreadyExistsError:
            raise ValueError(f"User with email {email} already exists")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise ValueError(f"Failed to create user: {str(e)}")

    def verify_id_token(self, id_token: str) -> Dict:
        """
        Verify Firebase ID token

        Args:
            id_token: Firebase ID token from client

        Returns:
            Decoded token with user information

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.InvalidIdTokenError:
            raise ValueError("Invalid ID token")
        except auth.ExpiredIdTokenError:
            raise ValueError("Token has expired")
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise ValueError(f"Token verification failed: {str(e)}")

    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> str:
        """
        Create a custom token for a user

        Args:
            uid: User ID
            additional_claims: Optional additional claims

        Returns:
            Custom token string
        """
        try:
            token = auth.create_custom_token(uid, additional_claims)
            return token.decode('utf-8') if isinstance(token, bytes) else token
        except Exception as e:
            logger.error(f"Error creating custom token: {e}")
            raise ValueError(f"Failed to create custom token: {str(e)}")

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user information by email

        Args:
            email: User email address

        Returns:
            User information or None if not found
        """
        try:
            user = auth.get_user_by_email(email)
            return self._user_to_dict(user)
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict]:
        """
        Get user information by UID

        Args:
            uid: User ID

        Returns:
            User information or None if not found
        """
        try:
            user = auth.get_user(uid)
            return self._user_to_dict(user)
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting user by UID: {e}")
            return None

    def update_user(self, uid: str, **kwargs) -> Dict:
        """
        Update user information

        Args:
            uid: User ID
            **kwargs: Fields to update (email, display_name, password, etc.)

        Returns:
            Updated user information
        """
        try:
            user = auth.update_user(uid, **kwargs)
            logger.info(f"Updated user: {uid}")
            return self._user_to_dict(user)
        except auth.UserNotFoundError:
            raise ValueError(f"User not found: {uid}")
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise ValueError(f"Failed to update user: {str(e)}")

    def delete_user(self, uid: str) -> bool:
        """
        Delete a user

        Args:
            uid: User ID

        Returns:
            True if successful
        """
        try:
            auth.delete_user(uid)
            logger.info(f"Deleted user: {uid}")
            return True
        except auth.UserNotFoundError:
            raise ValueError(f"User not found: {uid}")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise ValueError(f"Failed to delete user: {str(e)}")

    def list_users(self, max_results: int = 100) -> List[Dict]:
        """
        List all users

        Args:
            max_results: Maximum number of users to return

        Returns:
            List of user dictionaries
        """
        try:
            users = []
            page = auth.list_users(max_results=max_results)

            for user in page.users:
                users.append(self._user_to_dict(user))

            return users
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def set_custom_claims(self, uid: str, claims: Dict) -> bool:
        """
        Set custom claims for a user (roles, permissions)

        Args:
            uid: User ID
            claims: Dictionary of custom claims

        Returns:
            True if successful
        """
        try:
            auth.set_custom_user_claims(uid, claims)
            logger.info(f"Set custom claims for user {uid}: {claims}")
            return True
        except Exception as e:
            logger.error(f"Error setting custom claims: {e}")
            raise ValueError(f"Failed to set custom claims: {str(e)}")

    def generate_password_reset_link(self, email: str) -> str:
        """
        Generate password reset link

        Args:
            email: User email address

        Returns:
            Password reset link
        """
        try:
            link = auth.generate_password_reset_link(email)
            logger.info(f"Generated password reset link for {email}")
            return link
        except Exception as e:
            logger.error(f"Error generating password reset link: {e}")
            raise ValueError(f"Failed to generate password reset link: {str(e)}")

    def generate_email_verification_link(self, email: str) -> str:
        """
        Generate email verification link

        Args:
            email: User email address

        Returns:
            Email verification link
        """
        try:
            link = auth.generate_email_verification_link(email)
            logger.info(f"Generated email verification link for {email}")
            return link
        except Exception as e:
            logger.error(f"Error generating email verification link: {e}")
            raise ValueError(f"Failed to generate email verification link: {str(e)}")

    def revoke_refresh_tokens(self, uid: str) -> bool:
        """
        Revoke all refresh tokens for a user (force logout)

        Args:
            uid: User ID

        Returns:
            True if successful
        """
        try:
            auth.revoke_refresh_tokens(uid)
            logger.info(f"Revoked refresh tokens for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error revoking refresh tokens: {e}")
            return False

    def _user_to_dict(self, user) -> Dict:
        """
        Convert Firebase UserRecord to dictionary

        Args:
            user: Firebase UserRecord object

        Returns:
            User dictionary
        """
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url,
            'email_verified': user.email_verified,
            'disabled': user.disabled,
            'created_at': datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000).isoformat() if user.user_metadata.creation_timestamp else None,
            'last_sign_in': datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000).isoformat() if user.user_metadata.last_sign_in_timestamp else None,
            'custom_claims': user.custom_claims or {}
        }


# Singleton instance
_auth_manager = None


def get_firebase_auth_manager(credentials_path: Optional[str] = None) -> FirebaseAuthManager:
    """
    Get singleton instance of FirebaseAuthManager

    Args:
        credentials_path: Optional path to credentials file

    Returns:
        FirebaseAuthManager instance
    """
    global _auth_manager

    if _auth_manager is None:
        _auth_manager = FirebaseAuthManager(credentials_path)

    return _auth_manager
