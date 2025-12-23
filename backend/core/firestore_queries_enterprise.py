"""
Enterprise-grade Firestore query functions for Nigerian Real Estate Scraper.

This module provides optimized query functions for the nested enterprise schema.
All functions support the new schema structure with nested categories.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Initialize Firebase (lazy loading)
_firebase_initialized = False
_firestore_client = None


def _safe_get(dictionary: Dict, *keys, default='N/A'):
    """
    Safely get nested dictionary values with None handling.

    Args:
        dictionary: The dictionary to search
        *keys: Path of keys to follow (e.g., 'basic_info', 'title')
        default: Default value if key is missing or None

    Returns:
        Value or default

    Example:
        >>> _safe_get(doc, 'basic_info', 'title', default='Untitled')
    """
    value = dictionary
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    return value if value is not None else default


def _clean_property_dict(prop: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean a property dictionary to ensure all critical fields are present.

    Adds user-friendly defaults for missing or None values.

    Args:
        prop: Property dictionary from Firestore

    Returns:
        Cleaned property dictionary with guaranteed fields
    """
    # Ensure basic_info has required fields
    if 'basic_info' in prop and prop['basic_info']:
        basic_info = prop['basic_info']
        if basic_info.get('title') is None or basic_info.get('title') == '':
            # Try to generate title from other fields
            prop_type = _safe_get(prop, 'property_details', 'property_type', default='Property')
            bedrooms = _safe_get(prop, 'property_details', 'bedrooms', default=None)
            location = _safe_get(prop, 'location', 'area', default='Lagos')

            if bedrooms and bedrooms != 'N/A':
                basic_info['title'] = f"{bedrooms}BR {prop_type} in {location}"
            else:
                basic_info['title'] = f"{prop_type} in {location}"

    # Ensure price is present
    if 'financial' in prop and prop['financial']:
        if prop['financial'].get('price') is None:
            prop['financial']['price'] = 0

    return prop


def _get_firestore_client():
    """Get Firestore client with lazy initialization."""
    global _firebase_initialized, _firestore_client

    if _firebase_initialized:
        return _firestore_client

    # Check if credentials are available
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    credentials_json = os.getenv('FIREBASE_CREDENTIALS')

    if not service_account_path and not credentials_json:
        logger.warning("Firebase credentials not found")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Check if Firebase is already initialized (by another module)
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"Firestore initialized from: {service_account_path}")
            elif credentials_json:
                import json
                cred_dict = json.loads(credentials_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firestore initialized from environment variable")
            else:
                logger.error("Firebase credentials configured but file not found")
                return None
        else:
            # Firebase already initialized, just log it
            logger.info("Firestore already initialized, reusing existing app")

        _firestore_client = firestore.client()
        _firebase_initialized = True
        return _firestore_client

    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}")
        return None


def get_properties_by_status(
    status: str = 'available',
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get properties by status (available, sold, rented, off-market).

    Args:
        status: Property status
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', status) \
                             .limit(limit)

        if offset > 0:
            query = query.offset(offset)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} properties with status: {status}")
        return results

    except Exception as e:
        logger.error(f"Error querying by status: {e}")
        return []


def get_properties_by_listing_type(
    listing_type: str = 'sale',
    limit: int = 100,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Get properties by listing type (sale, rent, lease, shortlet).

    Args:
        listing_type: Type of listing
        limit: Maximum number of results
        price_min: Minimum price filter
        price_max: Maximum price filter

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.listing_type', '==', listing_type) \
                             .where('basic_info.status', '==', 'available')

        # Add price filters if provided
        if price_min is not None:
            query = query.where('financial.price', '>=', price_min)
        if price_max is not None:
            query = query.where('financial.price', '<=', price_max)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} {listing_type} properties")
        return results

    except Exception as e:
        logger.error(f"Error querying by listing type: {e}")
        return []


def get_furnished_properties(
    furnishing: str = 'furnished',
    limit: int = 100,
    price_max: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Get properties by furnishing status.

    Args:
        furnishing: Furnishing type (furnished, semi-furnished, unfurnished)
        limit: Maximum number of results
        price_max: Maximum price filter

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('property_details.furnishing', '==', furnishing) \
                             .where('basic_info.status', '==', 'available')

        if price_max:
            query = query.where('financial.price', '<=', price_max)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} {furnishing} properties")
        return results

    except Exception as e:
        logger.error(f"Error querying furnished properties: {e}")
        return []


def get_premium_properties(
    limit: int = 100,
    min_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Get premium properties (auto-tagged by system).

    Args:
        limit: Maximum number of results
        min_price: Minimum price filter

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('tags.premium', '==', True) \
                             .where('basic_info.status', '==', 'available')

        if min_price:
            query = query.where('financial.price', '>=', min_price)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} premium properties")
        return results

    except Exception as e:
        logger.error(f"Error querying premium properties: {e}")
        return []


def get_hot_deals(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get hot deal properties (auto-tagged, <15M per bedroom).

    Args:
        limit: Maximum number of results

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('tags.hot_deal', '==', True) \
                             .where('basic_info.status', '==', 'available') \
                             .order_by('financial.price') \
                             .limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} hot deal properties")
        return results

    except Exception as e:
        logger.error(f"Error querying hot deals: {e}")
        return []


def get_verified_properties(
    limit: int = 100,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get verified properties (verification_status = 'verified').

    Args:
        limit: Maximum number of results
        price_min: Minimum price filter (optional)
        price_max: Maximum price filter (optional)

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.verification_status', '==', 'verified') \
                             .where('basic_info.status', '==', 'available')

        # Add price filters if provided
        if price_min is not None:
            query = query.where('financial.price', '>=', price_min)
        if price_max is not None:
            query = query.where('financial.price', '<=', price_max)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} verified properties")
        return results

    except Exception as e:
        logger.error(f"Error querying verified properties: {e}")
        return []


def get_trending_properties(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get trending properties (high view count).

    Args:
        limit: Maximum number of results

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', 'available') \
                             .order_by('metadata.view_count', direction='DESCENDING') \
                             .limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} trending properties")
        return results

    except Exception as e:
        logger.error(f"Error querying trending properties: {e}")
        return []


def get_properties_by_lga(
    lga: str,
    limit: int = 100,
    bedrooms_min: Optional[int] = None,
    price_max: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Get properties by LGA (Local Government Area).

    Args:
        lga: LGA name (e.g., 'Eti-Osa', 'Ikeja')
        limit: Maximum number of results
        bedrooms_min: Minimum bedrooms filter
        price_max: Maximum price filter

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('location.lga', '==', lga) \
                             .where('basic_info.status', '==', 'available')

        if bedrooms_min:
            query = query.where('property_details.bedrooms', '>=', bedrooms_min)

        if price_max:
            query = query.where('financial.price', '<=', price_max)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} properties in {lga}")
        return results

    except Exception as e:
        logger.error(f"Error querying by LGA: {e}")
        return []


def get_properties_by_area(
    area: str,
    limit: int = 100,
    listing_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get properties by area (e.g., Lekki, Ikoyi, VI).

    Args:
        area: Area name
        limit: Maximum number of results
        listing_type: Filter by listing type (sale, rent)

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('location.area', '==', area) \
                             .where('basic_info.status', '==', 'available')

        if listing_type:
            query = query.where('basic_info.listing_type', '==', listing_type)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} properties in {area}")
        return results

    except Exception as e:
        logger.error(f"Error querying by area: {e}")
        return []


def get_new_on_market(days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get properties newly added to market (within X days).

    Args:
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', 'available') \
                             .where('metadata.days_on_market', '<=', days) \
                             .order_by('metadata.days_on_market') \
                             .limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} properties new in last {days} days")
        return results

    except Exception as e:
        logger.error(f"Error querying new on market: {e}")
        return []


def get_cheapest_properties(
    limit: int = 100,
    min_quality_score: float = 0.0,
    property_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get cheapest available properties.

    Args:
        limit: Maximum number of results
        min_quality_score: Minimum quality score filter
        property_type: Filter by property type

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', 'available')

        if min_quality_score > 0:
            query = query.where('metadata.quality_score', '>=', min_quality_score)

        if property_type:
            query = query.where('property_details.property_type', '==', property_type)

        query = query.order_by('financial.price').limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} cheapest properties")
        return results

    except Exception as e:
        logger.error(f"Error querying cheapest properties: {e}")
        return []


def get_newest_listings(
    limit: int = 50,
    days_back: int = 30,
    site_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get newest property listings.

    Args:
        limit: Maximum number of results
        days_back: Days to look back
        site_key: Filter by site

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_iso = cutoff_date.isoformat()

        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', 'available')

        if site_key:
            query = query.where('basic_info.site_key', '==', site_key)

        # Note: This may require a composite index on status + scrape_timestamp
        query = query.order_by('metadata.scrape_timestamp', direction='DESCENDING') \
                    .limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} newest listings")
        return results

    except Exception as e:
        logger.error(f"Error querying newest listings: {e}")
        return []


def search_properties_advanced(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Advanced property search with multiple filters.

    Args:
        filters: Dictionary of filters:
            - location: Area or LGA
            - price_min: Minimum price
            - price_max: Maximum price
            - bedrooms_min: Minimum bedrooms
            - bedrooms_max: Maximum bedrooms
            - property_type: Property type
            - listing_type: sale, rent, etc.
            - furnishing: furnished, semi-furnished, unfurnished
            - premium: Boolean for premium properties
            - limit: Maximum results (default 100)

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.status', '==', 'available')

        # Apply filters
        if filters.get('listing_type'):
            query = query.where('basic_info.listing_type', '==', filters['listing_type'])

        if filters.get('property_type'):
            query = query.where('property_details.property_type', '==', filters['property_type'])

        if filters.get('furnishing'):
            query = query.where('property_details.furnishing', '==', filters['furnishing'])

        if filters.get('location'):
            # Try area first, then LGA
            query = query.where('location.area', '==', filters['location'])

        if filters.get('premium') is not None:
            query = query.where('tags.premium', '==', filters['premium'])

        # Price range
        if filters.get('price_min'):
            query = query.where('financial.price', '>=', filters['price_min'])
        if filters.get('price_max'):
            query = query.where('financial.price', '<=', filters['price_max'])

        # Bedrooms range
        if filters.get('bedrooms_min'):
            query = query.where('property_details.bedrooms', '>=', filters['bedrooms_min'])
        if filters.get('bedrooms_max'):
            query = query.where('property_details.bedrooms', '<=', filters['bedrooms_max'])

        # Limit
        limit = filters.get('limit', 100)
        query = query.limit(limit)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Advanced search returned {len(results)} properties")
        return results

    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        return []


def get_property_by_hash(property_hash: str) -> Optional[Dict[str, Any]]:
    """
    Get single property by hash.

    Args:
        property_hash: Property hash (document ID)

    Returns:
        Property dictionary or None
    """
    db = _get_firestore_client()
    if not db:
        return None

    try:
        doc_ref = db.collection('properties').document(property_hash)
        doc = doc_ref.get()

        if doc.exists:
            return _clean_property_dict(doc.to_dict())
        else:
            logger.warning(f"Property not found: {property_hash}")
            return None

    except Exception as e:
        logger.error(f"Error getting property by hash: {e}")
        return None


def get_dashboard_stats() -> Dict[str, Any]:
    """
    Get dashboard statistics.

    Returns:
        Dictionary with aggregate stats
    """
    db = _get_firestore_client()
    if not db:
        return {}

    try:
        # Try to get cached stats first
        aggregates_ref = db.collection('aggregates').document('dashboard')
        cached = aggregates_ref.get()

        if cached.exists:
            data = cached.to_dict()
            # Check if cache is fresh (< 1 hour old)
            if data.get('updated_at'):
                cache_time = data['updated_at']
                if isinstance(cache_time, datetime):
                    # Make both datetimes timezone-aware for comparison
                    now = datetime.now(timezone.utc)
                    if cache_time.tzinfo is None:
                        cache_time = cache_time.replace(tzinfo=timezone.utc)
                    age = now - cache_time
                    if age.total_seconds() < 3600:  # 1 hour
                        logger.info("Returning cached dashboard stats")
                        return data

        # Calculate fresh stats
        properties_ref = db.collection('properties')

        # Get all available properties (may be slow for large collections)
        all_props = list(properties_ref.where('basic_info.status', '==', 'available').stream())

        if not all_props:
            return {
                'total_properties': 0,
                'updated_at': datetime.now(timezone.utc)
            }

        # Calculate stats
        prices = []
        by_type = {}
        by_listing_type = {}
        by_area = {}
        premium_count = 0

        for doc in all_props:
            data = doc.to_dict()

            # Price stats
            price = data.get('financial', {}).get('price')
            if price:
                prices.append(price)

            # Type breakdown
            prop_type = data.get('property_details', {}).get('property_type')
            if prop_type:
                by_type[prop_type] = by_type.get(prop_type, 0) + 1

            # Listing type breakdown
            listing_type = data.get('basic_info', {}).get('listing_type')
            if listing_type:
                by_listing_type[listing_type] = by_listing_type.get(listing_type, 0) + 1

            # Area breakdown
            area = data.get('location', {}).get('area')
            if area:
                by_area[area] = by_area.get(area, 0) + 1

            # Premium count
            if data.get('tags', {}).get('premium'):
                premium_count += 1

        stats = {
            'total_properties': len(all_props),
            'total_for_sale': by_listing_type.get('sale', 0),
            'total_for_rent': by_listing_type.get('rent', 0),
            'premium_properties': premium_count,
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0
            },
            'by_property_type': by_type,
            'by_listing_type': by_listing_type,
            'top_areas': dict(sorted(by_area.items(), key=lambda x: x[1], reverse=True)[:10]),
            'updated_at': datetime.now(timezone.utc)
        }

        # Cache the stats
        try:
            aggregates_ref.set(stats)
        except:
            pass  # Non-critical

        logger.info("Calculated fresh dashboard stats")
        return stats

    except Exception as e:
        logger.error(f"Error calculating dashboard stats: {e}")
        return {}


def get_site_properties(
    site_key: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get properties from specific site.

    Args:
        site_key: Site identifier
        limit: Maximum results
        offset: Results to skip

    Returns:
        List of property dictionaries
    """
    db = _get_firestore_client()
    if not db:
        return []

    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('basic_info.site_key', '==', site_key) \
                             .limit(limit)

        if offset > 0:
            query = query.offset(offset)

        results = [_clean_property_dict(doc.to_dict()) for doc in query.stream()]
        logger.info(f"Retrieved {len(results)} properties from {site_key}")
        return results

    except Exception as e:
        logger.error(f"Error querying site properties: {e}")
        return []
