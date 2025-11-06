"""
core/firestore_queries.py

Optimized Firestore query helpers for common property search patterns.
Replaces Excel workbook summary sheets with query-time aggregation.

Features:
- Fast cross-site queries with composite indexes
- Flexible filtering (price, location, property type, bedrooms, etc.)
- Pagination support
- Aggregate statistics
- Cached results for expensive queries

Usage:
    from core.firestore_queries import (
        get_cheapest_properties,
        get_newest_listings,
        search_properties,
        get_dashboard_stats
    )

    # Get top 100 cheapest properties
    results = get_cheapest_properties(limit=100)

    # Search across all sites
    results = search_properties({
        'location': 'Lekki',
        'price_min': 5000000,
        'price_max': 50000000,
        'bedrooms_min': 3
    })
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# Lazy import Firestore
_firestore_client = None


def _get_firestore_client():
    """Get Firestore client (lazy initialization)"""
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    from core.firestore_direct import _get_firestore_client as get_client
    _firestore_client = get_client()
    return _firestore_client


def _doc_to_dict(doc) -> Dict[str, Any]:
    """Convert Firestore document to dict"""
    data = doc.to_dict()
    data['id'] = doc.id
    return data


# ============================================================================
# TOP DEALS & NEWEST LISTINGS
# ============================================================================

def get_cheapest_properties(
    limit: int = 100,
    min_quality_score: float = 0.0,
    property_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get cheapest properties across all sites (replaces _Top_100_Cheapest sheet).

    Args:
        limit: Number of properties to return
        min_quality_score: Minimum quality score filter (0.0-1.0)
        property_type: Filter by property type (e.g., 'Flat', 'Detached Duplex')

    Returns:
        List of property dicts sorted by price ascending
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        query = db.collection('properties')

        # Filter by quality score
        if min_quality_score > 0:
            query = query.where('quality_score', '>=', min_quality_score)

        # Filter by property type
        if property_type:
            query = query.where('property_type', '==', property_type)

        # Sort by price ascending, then quality score descending
        query = query.order_by('price', direction='ASCENDING')
        if min_quality_score > 0:
            query = query.order_by('quality_score', direction='DESCENDING')

        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} cheapest properties")
        return results

    except Exception as e:
        logger.error(f"Error getting cheapest properties: {e}")
        return []


def get_newest_listings(
    limit: int = 50,
    days_back: int = 7,
    site_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get newest listings (replaces _Newest_Listings sheet).

    Args:
        limit: Number of properties to return
        days_back: Only include listings from last N days
        site_key: Filter by specific site (optional)

    Returns:
        List of property dicts sorted by scrape_timestamp descending
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        query = db.collection('properties')

        # Filter by site if specified
        if site_key:
            query = query.where('site_key', '==', site_key)

        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        query = query.where('scrape_timestamp', '>=', cutoff_date.isoformat())

        # Sort by scrape timestamp descending
        query = query.order_by('scrape_timestamp', direction='DESCENDING')
        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} newest listings")
        return results

    except Exception as e:
        logger.error(f"Error getting newest listings: {e}")
        return []


# ============================================================================
# PROPERTY TYPE QUERIES
# ============================================================================

def get_for_sale_properties(
    limit: int = 100,
    price_max: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get properties for sale (replaces _For_Sale sheet).

    Uses heuristics: price > 10M or title contains "for sale"

    Args:
        limit: Number of properties to return
        price_max: Maximum price filter

    Returns:
        List of property dicts likely for sale
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        query = db.collection('properties')

        # Heuristic: properties over 10M are likely for sale
        query = query.where('price', '>=', 10000000)

        if price_max:
            query = query.where('price', '<=', price_max)

        query = query.order_by('price', direction='ASCENDING')
        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} for-sale properties")
        return results

    except Exception as e:
        logger.error(f"Error getting for-sale properties: {e}")
        return []


def get_for_rent_properties(
    limit: int = 100,
    price_max: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get properties for rent (replaces _For_Rent sheet).

    Uses heuristics: price < 10M (likely annual rent)

    Args:
        limit: Number of properties to return
        price_max: Maximum price filter

    Returns:
        List of property dicts likely for rent
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        query = db.collection('properties')

        # Heuristic: properties under 10M are likely for rent
        query = query.where('price', '<', 10000000)
        query = query.where('price', '>', 0)  # Exclude zero prices

        if price_max:
            query = query.where('price', '<=', price_max)

        query = query.order_by('price', direction='ASCENDING')
        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} for-rent properties")
        return results

    except Exception as e:
        logger.error(f"Error getting for-rent properties: {e}")
        return []


def get_land_only_properties(
    limit: int = 100,
    price_max: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get land-only properties (replaces _Land_Only sheet).

    Filters by property_type containing "land"

    Args:
        limit: Number of properties to return
        price_max: Maximum price filter

    Returns:
        List of land property dicts
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        # Note: Firestore doesn't support LIKE queries, so we need to
        # fetch and filter client-side or use specific property types
        query = db.collection('properties')

        # Common land property types
        land_types = ['Land', 'Residential Land', 'Commercial Land', 'Mixed Use Land']

        # Firestore 'in' query (max 10 values)
        query = query.where('property_type', 'in', land_types)

        if price_max:
            query = query.where('price', '<=', price_max)

        query = query.order_by('price', direction='ASCENDING')
        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} land-only properties")
        return results

    except Exception as e:
        logger.error(f"Error getting land-only properties: {e}")
        return []


def get_premium_properties(
    min_bedrooms: int = 4,
    limit: int = 100,
    price_max: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get premium properties (replaces _4BR_Plus sheet).

    Args:
        min_bedrooms: Minimum number of bedrooms (default 4)
        limit: Number of properties to return
        price_max: Maximum price filter

    Returns:
        List of premium property dicts
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return []

    try:
        query = db.collection('properties')

        # Filter by bedrooms
        query = query.where('bedrooms', '>=', min_bedrooms)

        if price_max:
            query = query.where('price', '<=', price_max)

        # Sort by bedrooms descending, then price ascending
        query = query.order_by('bedrooms', direction='DESCENDING')
        query = query.order_by('price', direction='ASCENDING')
        query = query.limit(limit)

        docs = query.stream()
        results = [_doc_to_dict(doc) for doc in docs]

        logger.info(f"Retrieved {len(results)} premium properties (>={min_bedrooms} BR)")
        return results

    except Exception as e:
        logger.error(f"Error getting premium properties: {e}")
        return []


# ============================================================================
# FLEXIBLE SEARCH
# ============================================================================

def search_properties(
    filters: Dict[str, Any],
    sort_by: str = 'price',
    sort_desc: bool = False,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Flexible property search with multiple filters (cross-site).

    Args:
        filters: Dict of filter criteria:
            - location: str (exact match)
            - price_min: int
            - price_max: int
            - bedrooms_min: int
            - bedrooms_max: int
            - property_type: str
            - site_key: str (specific site)
            - quality_score_min: float (0.0-1.0)
        sort_by: Field to sort by ('price', 'scrape_timestamp', 'quality_score', 'bedrooms')
        sort_desc: Sort descending if True
        limit: Number of results to return
        offset: Number of results to skip (pagination)

    Returns:
        Dict with:
            - results: List of property dicts
            - total: Total count (if available)
            - has_more: Boolean indicating more results available
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return {'results': [], 'total': 0, 'has_more': False}

    try:
        query = db.collection('properties')

        # Apply filters
        if 'site_key' in filters and filters['site_key']:
            query = query.where('site_key', '==', filters['site_key'])

        if 'location' in filters and filters['location']:
            query = query.where('location', '==', filters['location'])

        if 'property_type' in filters and filters['property_type']:
            query = query.where('property_type', '==', filters['property_type'])

        if 'price_min' in filters and filters['price_min']:
            query = query.where('price', '>=', filters['price_min'])

        if 'price_max' in filters and filters['price_max']:
            query = query.where('price', '<=', filters['price_max'])

        if 'bedrooms_min' in filters and filters['bedrooms_min']:
            query = query.where('bedrooms', '>=', filters['bedrooms_min'])

        if 'bedrooms_max' in filters and filters['bedrooms_max']:
            query = query.where('bedrooms', '<=', filters['bedrooms_max'])

        if 'quality_score_min' in filters and filters['quality_score_min']:
            query = query.where('quality_score', '>=', filters['quality_score_min'])

        # Sort
        direction = 'DESCENDING' if sort_desc else 'ASCENDING'
        query = query.order_by(sort_by, direction=direction)

        # Pagination
        if offset > 0:
            query = query.offset(offset)
        query = query.limit(limit + 1)  # Fetch one extra to check has_more

        docs = list(query.stream())
        has_more = len(docs) > limit
        results = [_doc_to_dict(doc) for doc in docs[:limit]]

        logger.info(f"Search returned {len(results)} properties")
        return {
            'results': results,
            'total': len(results),  # Firestore doesn't support COUNT in query
            'has_more': has_more
        }

    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return {'results': [], 'total': 0, 'has_more': False}


# ============================================================================
# SITE-SPECIFIC QUERIES
# ============================================================================

def get_site_properties(
    site_key: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = 'scrape_timestamp',
    sort_desc: bool = True
) -> Dict[str, Any]:
    """
    Get all properties from a specific site.

    Args:
        site_key: Site identifier (e.g., 'npc', 'cwlagos')
        limit: Number of results to return
        offset: Number of results to skip
        sort_by: Field to sort by
        sort_desc: Sort descending if True

    Returns:
        Dict with results, total, has_more
    """
    return search_properties(
        filters={'site_key': site_key},
        sort_by=sort_by,
        sort_desc=sort_desc,
        limit=limit,
        offset=offset
    )


# ============================================================================
# DASHBOARD STATISTICS
# ============================================================================

def get_dashboard_stats() -> Dict[str, Any]:
    """
    Get aggregate statistics for dashboard (replaces _Dashboard sheet).

    Returns:
        Dict with:
            - total_properties: int
            - total_sites: int
            - price_range: {min, max, avg}
            - property_type_breakdown: {type: count}
            - site_breakdown: {site: count}
            - quality_distribution: {high, medium, low}
            - newest_listing: dict
            - cheapest_listing: dict
    """
    db = _get_firestore_client()
    if db is None:
        logger.warning("Firestore not available")
        return {}

    try:
        # Check if cached aggregates exist
        aggregates_ref = db.collection('aggregates').document('dashboard')
        cached = aggregates_ref.get()

        if cached.exists:
            cached_data = cached.to_dict()
            # Check if cache is recent (less than 1 hour old)
            updated_at = cached_data.get('updated_at')
            if updated_at:
                age_hours = (datetime.now() - updated_at).total_seconds() / 3600
                if age_hours < 1:
                    logger.info("Using cached dashboard stats")
                    return cached_data.get('stats', {})

        # Calculate fresh stats (expensive operation)
        logger.info("Calculating fresh dashboard stats...")

        all_properties = db.collection('properties').stream()
        properties = [_doc_to_dict(doc) for doc in all_properties]

        if not properties:
            return {
                'total_properties': 0,
                'total_sites': 0,
                'message': 'No properties in database'
            }

        # Calculate statistics
        prices = [p.get('price') for p in properties if p.get('price') is not None and p.get('price') > 0]
        sites = set(p.get('site_key') for p in properties if p.get('site_key'))
        property_types = defaultdict(int)
        site_breakdown = defaultdict(int)
        quality_dist = {'high': 0, 'medium': 0, 'low': 0}

        for prop in properties:
            # Property type breakdown
            ptype = prop.get('property_type', 'Unknown')
            property_types[ptype] += 1

            # Site breakdown
            site = prop.get('site_key', 'unknown')
            site_breakdown[site] += 1

            # Quality distribution
            quality = prop.get('quality_score') or 0
            if quality >= 0.8:
                quality_dist['high'] += 1
            elif quality >= 0.5:
                quality_dist['medium'] += 1
            else:
                quality_dist['low'] += 1

        # Find newest and cheapest (filter out None values)
        valid_props_with_timestamp = [p for p in properties if p.get('scrape_timestamp')]
        valid_props_with_price = [p for p in properties if p.get('price') is not None and p.get('price') > 0]

        newest = max(valid_props_with_timestamp, key=lambda p: p.get('scrape_timestamp'), default=None) if valid_props_with_timestamp else None
        cheapest = min(valid_props_with_price, key=lambda p: p.get('price'), default=None) if valid_props_with_price else None

        stats = {
            'total_properties': len(properties),
            'total_sites': len(sites),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) // len(prices) if prices else 0
            },
            'property_type_breakdown': dict(property_types),
            'site_breakdown': dict(site_breakdown),
            'quality_distribution': quality_dist,
            'newest_listing': newest,
            'cheapest_listing': cheapest,
            'updated_at': datetime.now()
        }

        # Cache the results
        try:
            from google.cloud.firestore import SERVER_TIMESTAMP
            aggregates_ref.set({
                'stats': stats,
                'updated_at': SERVER_TIMESTAMP
            }, merge=True)
            logger.info("Cached dashboard stats")
        except Exception as e:
            logger.warning(f"Failed to cache dashboard stats: {e}")

        return stats

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_property_by_hash(property_hash: str) -> Optional[Dict[str, Any]]:
    """
    Get a single property by its hash (document ID).

    Args:
        property_hash: Property hash (SHA256)

    Returns:
        Property dict or None if not found
    """
    db = _get_firestore_client()
    if db is None:
        return None

    try:
        doc = db.collection('properties').document(property_hash).get()
        if doc.exists:
            return _doc_to_dict(doc)
        return None
    except Exception as e:
        logger.error(f"Error getting property by hash: {e}")
        return None


def get_site_statistics(site_key: str) -> Dict[str, Any]:
    """
    Get statistics for a specific site.

    Args:
        site_key: Site identifier

    Returns:
        Dict with site statistics
    """
    db = _get_firestore_client()
    if db is None:
        return {}

    try:
        # Try cache first
        metadata_ref = db.collection('site_metadata').document(site_key)
        cached = metadata_ref.get()

        if cached.exists:
            return cached.to_dict()

        # Calculate if not cached
        docs = db.collection('properties').where('site_key', '==', site_key).stream()
        properties = [_doc_to_dict(doc) for doc in docs]

        if not properties:
            return {'site_key': site_key, 'total_properties': 0}

        prices = [p.get('price') for p in properties if p.get('price') is not None and p.get('price') > 0]

        stats = {
            'site_key': site_key,
            'total_properties': len(properties),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) // len(prices) if prices else 0
            },
            'last_updated': datetime.now()
        }

        return stats

    except Exception as e:
        logger.error(f"Error getting site statistics for {site_key}: {e}")
        return {}
