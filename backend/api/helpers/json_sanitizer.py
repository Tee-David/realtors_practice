"""
JSON Sanitizer Utility
Removes NaN, Infinity, and -Infinity values that break JSON serialization
Converts Firestore GeoPoint and DatetimeWithNanoseconds objects to JSON-safe types
"""
import math
from datetime import datetime
from typing import Any, Dict, List, Union


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize an object for JSON serialization.
    Replaces NaN, Infinity, -Infinity with None or appropriate values.
    Converts Firestore GeoPoint objects to {latitude: float, longitude: float}.

    Args:
        obj: Any Python object to sanitize

    Returns:
        Sanitized object safe for JSON serialization
    """
    if obj is None:
        return None

    # Handle Firestore DatetimeWithNanoseconds (MUST be before datetime check!)
    # Convert to ISO format string
    if hasattr(obj, 'isoformat') and hasattr(obj, 'timestamp') and not isinstance(obj, datetime):
        try:
            return obj.isoformat()
        except Exception:
            # Fallback to timestamp
            try:
                return obj.timestamp()
            except Exception:
                return None

    # Handle Python datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Handle Firestore GeoPoint objects (MUST be before dict check!)
    # Check for GeoPoint by duck typing (has latitude and longitude attributes)
    # This handles any object with these attributes, not just firebase GeoPoint
    if hasattr(obj, 'latitude') and hasattr(obj, 'longitude') and not isinstance(obj, dict):
        try:
            lat = float(obj.latitude) if not (isinstance(obj.latitude, float) and (math.isnan(obj.latitude) or math.isinf(obj.latitude))) else None
            lng = float(obj.longitude) if not (isinstance(obj.longitude, float) and (math.isnan(obj.longitude) or math.isinf(obj.longitude))) else None
            return {
                'latitude': lat,
                'longitude': lng
            }
        except Exception as e:
            # If conversion fails, return None
            print(f"Warning: Failed to convert GeoPoint-like object: {e}")
            return None

    # Handle floats - check for NaN and Infinity
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None  # Convert NaN/Infinity to None
        return obj

    # Handle dictionaries recursively
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    # Handle lists/tuples recursively
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]

    # Handle sets (convert to list)
    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]

    # Return other types as-is (str, int, bool, etc.)
    return obj


def sanitize_property_data(properties: List[Dict]) -> List[Dict]:
    """
    Sanitize a list of property dictionaries.

    Args:
        properties: List of property dictionaries from Firestore

    Returns:
        Sanitized list of properties
    """
    return [sanitize_for_json(prop) for prop in properties]
