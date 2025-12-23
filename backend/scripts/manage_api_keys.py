"""
API Key Management Script
Generate, list, and manage API keys for frontend authentication
"""

import os
import secrets
import json
from datetime import datetime
from pathlib import Path

# File to store API keys (DO NOT commit to git!)
KEYS_FILE = Path("api_keys.json")


def load_keys():
    """Load existing API keys from file"""
    if KEYS_FILE.exists():
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return {"keys": []}


def save_keys(data):
    """Save API keys to file"""
    with open(KEYS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def generate_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def create_api_key(name: str, description: str = ""):
    """
    Create a new API key

    Args:
        name: Name/identifier for this key (e.g., "frontend-production")
        description: Optional description

    Returns:
        Generated API key
    """
    data = load_keys()

    # Generate new key
    api_key = generate_key()

    # Add to keys list
    key_info = {
        "key": api_key,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "active": True
    }

    data["keys"].append(key_info)
    save_keys(data)

    print("\n" + "="*70)
    print("✅ API KEY CREATED SUCCESSFULLY")
    print("="*70)
    print(f"\nKey Name: {name}")
    print(f"Description: {description or 'N/A'}")
    print(f"Created: {key_info['created_at']}")
    print(f"\n🔑 API Key: {api_key}")
    print("\n" + "="*70)
    print("IMPORTANT: Save this key securely!")
    print("You won't be able to see it again.")
    print("="*70)

    print("\n📋 Give this to your frontend developer:")
    print("-" * 70)
    print(f"API_KEY={api_key}")
    print(f"BASE_URL=http://localhost:5000")
    print("-" * 70)

    print("\n📝 For their .env file:")
    print("-" * 70)
    print(f"REACT_APP_API_KEY={api_key}")
    print(f"REACT_APP_API_URL=http://localhost:5000")
    print("-" * 70)

    return api_key


def list_keys():
    """List all API keys"""
    data = load_keys()

    if not data["keys"]:
        print("\n❌ No API keys found. Create one first!")
        return

    print("\n" + "="*70)
    print("API KEYS")
    print("="*70)

    for idx, key_info in enumerate(data["keys"], 1):
        status = "🟢 Active" if key_info.get("active", True) else "🔴 Disabled"

        print(f"\n{idx}. {key_info['name']}")
        print(f"   Status: {status}")
        print(f"   Created: {key_info['created_at']}")
        print(f"   Description: {key_info.get('description', 'N/A')}")
        print(f"   Key: {key_info['key'][:8]}...{key_info['key'][-8:]}")

    print("\n" + "="*70)


def disable_key(name: str):
    """Disable an API key"""
    data = load_keys()

    for key_info in data["keys"]:
        if key_info["name"] == name:
            key_info["active"] = False
            save_keys(data)
            print(f"\n✅ API key '{name}' has been disabled")
            return

    print(f"\n❌ API key '{name}' not found")


def enable_key(name: str):
    """Enable an API key"""
    data = load_keys()

    for key_info in data["keys"]:
        if key_info["name"] == name:
            key_info["active"] = True
            save_keys(data)
            print(f"\n✅ API key '{name}' has been enabled")
            return

    print(f"\n❌ API key '{name}' not found")


def delete_key(name: str):
    """Delete an API key"""
    data = load_keys()

    for idx, key_info in enumerate(data["keys"]):
        if key_info["name"] == name:
            data["keys"].pop(idx)
            save_keys(data)
            print(f"\n✅ API key '{name}' has been deleted")
            return

    print(f"\n❌ API key '{name}' not found")


def get_active_keys_for_env():
    """Get all active keys formatted for .env file"""
    data = load_keys()
    active_keys = [k["key"] for k in data["keys"] if k.get("active", True)]

    if not active_keys:
        print("\n❌ No active API keys found")
        return

    print("\n" + "="*70)
    print("ACTIVE API KEYS FOR .env FILE")
    print("="*70)
    print("\nCopy this line to your .env file:")
    print("-" * 70)
    print(f"API_KEYS={','.join(active_keys)}")
    print("-" * 70)


def main():
    """Main CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                     API KEY MANAGER                              ║
║              Nigerian Real Estate Scraper                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Usage:
    python manage_api_keys.py create <name> [description]
    python manage_api_keys.py list
    python manage_api_keys.py disable <name>
    python manage_api_keys.py enable <name>
    python manage_api_keys.py delete <name>
    python manage_api_keys.py env

Commands:
    create    - Create a new API key
    list      - List all API keys
    disable   - Disable an API key
    enable    - Enable an API key
    delete    - Delete an API key
    env       - Show active keys for .env file

Examples:
    # Create a key for frontend production
    python manage_api_keys.py create frontend-prod "Production frontend"

    # Create a key for testing
    python manage_api_keys.py create frontend-test "Testing environment"

    # List all keys
    python manage_api_keys.py list

    # Get keys for .env file
    python manage_api_keys.py env

    # Disable a key
    python manage_api_keys.py disable frontend-test
        """)
        return

    command = sys.argv[1].lower()

    if command == "create":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_api_keys.py create <name> [description]")
            return

        name = sys.argv[2]
        description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        create_api_key(name, description)

    elif command == "list":
        list_keys()

    elif command == "disable":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_api_keys.py disable <name>")
            return
        disable_key(sys.argv[2])

    elif command == "enable":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_api_keys.py enable <name>")
            return
        enable_key(sys.argv[2])

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_api_keys.py delete <name>")
            return
        delete_key(sys.argv[2])

    elif command == "env":
        get_active_keys_for_env()

    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see usage")


if __name__ == "__main__":
    main()
