"""
JSON Sanitizer Utility
Removes NaN, Infinity, and -Infinity values that break JSON serialization
"""
import math
from typing import Any, Dict, List, Union


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize an object for JSON serialization.
    Replaces NaN, Infinity, -Infinity with None or appropriate values.

    Args:
        obj: Any Python object to sanitize

    Returns:
        Sanitized object safe for JSON serialization
    """
    if obj is None:
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
