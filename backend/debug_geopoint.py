"""Debug script to find GeoPoint objects in Firestore properties"""
import os
import sys
import json

os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from core.firestore_queries_enterprise import get_properties_by_listing_type
from api.helpers.json_sanitizer import sanitize_for_json

def find_geopoints(obj, path=""):
    """Recursively find GeoPoint objects"""
    geopoints = []

    if hasattr(obj, 'latitude') and hasattr(obj, 'longitude') and not isinstance(obj, dict):
        geopoints.append(f"{path}: GeoPoint({obj.latitude}, {obj.longitude})")
        return geopoints

    if isinstance(obj, dict):
        for k, v in obj.items():
            geopoints.extend(find_geopoints(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            geopoints.extend(find_geopoints(item, f"{path}[{i}]"))

    return geopoints

print("Fetching first 200 for-sale properties...")
result = get_properties_by_listing_type('sale', limit=200, offset=0)

if 'properties' in result:
    properties = result['properties']
    print(f"Got {len(properties)} properties\n")

    for i, prop in enumerate(properties):
        geopoints = find_geopoints(prop)
        if geopoints:
            print(f"Property #{i+1} ({prop.get('basic_info', {}).get('title', 'Untitled')}):")
            for gp in geopoints:
                print(f"  - {gp}")
            print()

    # Try to JSON serialize
    print("Testing JSON serialization...")
    try:
        sanitized = sanitize_for_json(result)
        json_str = json.dumps(sanitized)
        print(f"[SUCCESS] Serialized {len(json_str)} bytes")
    except Exception as e:
        print(f"[FAILED] {e}")
else:
    print(f"Error: {result}")
