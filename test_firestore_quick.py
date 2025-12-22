"""Quick test to verify Firestore integration works"""
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("Testing Firestore Integration...")
print(f"FIREBASE_SERVICE_ACCOUNT: {os.getenv('FIREBASE_SERVICE_ACCOUNT')}")

# Test the credential file resolution logic
cred_path_env = os.getenv('FIREBASE_SERVICE_ACCOUNT')
if cred_path_env:
    cred_path = Path(cred_path_env)
    if not cred_path.exists():
        cred_path = Path('..') / cred_path_env
    if not cred_path.exists():
        cred_path = Path(__file__).parent / cred_path_env

    print(f"Credential file path: {cred_path}")
    print(f"Exists: {cred_path.exists()}")

    if cred_path.exists():
        # Try Firebase connection
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            if not firebase_admin._apps:
                cred = credentials.Certificate(str(cred_path))
                firebase_admin.initialize_app(cred)

            db = firestore.client()
            docs = list(db.collection('properties').where('financial.price', '>=', 5000000).limit(3).stream())

            print(f"\n[SUCCESS] Connected to Firestore!")
            print(f"Found {len(docs)} properties with price >= N5M")

            if docs:
                prop = docs[0].to_dict()
                print(f"\nSample property:")
                print(f"  Title: {prop.get('basic_info', {}).get('title', 'N/A')}")
                print(f"  Price: N{prop.get('financial', {}).get('price', 0):,.0f}")
                print(f"  Bedrooms: {prop.get('property_details', {}).get('bedrooms', 'N/A')}")
                print(f"  Location: {prop.get('location', {}).get('area', 'N/A')}")

            print("\n[VERIFIED] Firestore nested path queries work!")
            sys.exit(0)

        except Exception as e:
            print(f"\n[ERROR] Firebase connection failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
else:
    print("[ERROR] FIREBASE_SERVICE_ACCOUNT not set")
    sys.exit(1)
