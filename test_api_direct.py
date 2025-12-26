"""Test API endpoint directly bypassing Flask"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from core.firestore_queries_enterprise import get_properties_by_listing_type
from api.helpers.json_sanitizer import sanitize_for_json
import json

print("Fetching 200 properties...")
result = get_properties_by_listing_type('sale', limit=200, offset=0)

print(f"Got {len(result.get('properties', []))} properties")

print("Sanitizing...")
sanitized = sanitize_for_json(result)

print("Converting to JSON...")
try:
    json_str = json.dumps(sanitized)
    print(f"[SUCCESS] Created {len(json_str)} bytes of JSON")
    print("API serialization WORKS correctly!")
except Exception as e:
    print(f"[FAILED] {e}")
