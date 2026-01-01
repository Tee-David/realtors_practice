#!/usr/bin/env python3
"""
Script to set a user as admin
Usage: python scripts/set_admin.py <user_uid>
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.firebase_auth import get_firebase_auth_manager

def set_admin(uid: str):
    """Set a user as admin"""
    try:
        auth_manager = get_firebase_auth_manager()

        # Set custom claims
        auth_manager.set_custom_claims(uid, {'role': 'admin'})

        # Revoke refresh tokens to force re-authentication
        auth_manager.revoke_refresh_tokens(uid)

        print(f"[SUCCESS] User {uid} is now an admin")
        print("[WARNING] User must log out and log in again for changes to take effect")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/set_admin.py <user_uid>")
        sys.exit(1)

    uid = sys.argv[1]
    set_admin(uid)
