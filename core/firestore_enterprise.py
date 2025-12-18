"""
Enterprise-grade Firestore schema for Nigerian Real Estate Scraper.

This module implements a highly structured, queryable Firestore data model
inspired by enterprise systems like Zillow, Realtor.com, and Trulia.

Schema Structure:
- basic_info: Core listing information
- property_details: Physical property attributes
- financial: Pricing and payment information
- location: Geographic and address data
- amenities: Property features and facilities
- media: Images, videos, virtual tours
- agent_info: Agent and agency details
- metadata: Quality scores, timestamps, engagement metrics
- audit_trail: Price history, status changes, update logs
- tags: Promotional and categorization tags
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

# Initialize Firebase (lazy loading)
_firebase_initialized = False
_firestore_client = None


def _get_firestore_client():
    """Get Firestore client with lazy initialization."""
    global _firebase_initialized, _firestore_client

    if _firebase_initialized:
        return _firestore_client

    # Check if credentials are available
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    credentials_json = os.getenv('FIREBASE_CREDENTIALS')

    if not service_account_path and not credentials_json:
        logger.error("Firebase credentials not found!")
        logger.error("Set FIREBASE_SERVICE_ACCOUNT (file path) or FIREBASE_CREDENTIALS (JSON string)")
        logger.error(f"Current working directory: {os.getcwd()}")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import json

        # Check if Firebase is already initialized (by another module)
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            if service_account_path:
                if not os.path.exists(service_account_path):
                    logger.error(f"Firebase credential file not found: {service_account_path}")
                    logger.error(f"Current working directory: {os.getcwd()}")
                    try:
                        logger.error(f"Files in current directory: {os.listdir('.')[:10]}")
                    except Exception:
                        pass
                    return None
                logger.info(f"Loading Firebase credentials from file: {service_account_path}")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"[SUCCESS] Firestore initialized from service account: {service_account_path}")
            elif credentials_json:
                logger.info(f"Loading Firebase credentials from env var (length: {len(credentials_json)} chars)")
                try:
                    cred_dict = json.loads(credentials_json)
                    project_id = cred_dict.get('project_id', 'unknown')
                    logger.info(f"Parsed credentials for project: {project_id}")
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info(f"[SUCCESS] Firestore initialized for project: {project_id}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in FIREBASE_CREDENTIALS: {e}")
                    logger.error(f"First 50 chars: {credentials_json[:50]}...")
                    return None
            else:
                logger.error("Firebase credentials configured but file not found")
                return None
        else:
            # Firebase already initialized, just log it
            logger.info("[SUCCESS] Firestore already initialized, reusing existing app")

        _firestore_client = firestore.client()
        _firebase_initialized = True
        logger.info("[SUCCESS] Firestore client created successfully")
        return _firestore_client

    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def _clean_value(value):
    """Clean value for Firestore (handle NaN, None, etc.)"""
    import pandas as pd

    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return int(value) if value == int(value) else float(value)
    if isinstance(value, str):
        return value.strip() if value else None
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return value
    return value


def _infer_listing_type(listing: Dict[str, Any]) -> str:
    """
    Infer listing type (sale/rent/lease/shortlet) from price and description.

    Args:
        listing: Raw listing dictionary

    Returns:
        Listing type: "sale" | "rent" | "lease" | "shortlet"
    """
    price = listing.get('price', 0)
    title = str(listing.get('title', '')).lower()
    desc = str(listing.get('description', '')).lower()
    property_type = str(listing.get('property_type', '')).lower()

    # Keywords for rent
    rent_keywords = ['rent', 'rental', 'let', 'lease', 'monthly', 'annually']
    shortlet_keywords = ['shortlet', 'short let', 'daily', 'weekly', 'vacation rental']

    # Check for shortlet first (more specific)
    if any(kw in title or kw in desc for kw in shortlet_keywords):
        return 'shortlet'

    # Check for rent/lease
    if any(kw in title or kw in desc for kw in rent_keywords):
        # Differentiate lease (usually commercial/land) from rent (residential)
        if 'land' in property_type or 'commercial' in property_type:
            return 'lease'
        return 'rent'

    # Default to sale
    return 'sale'


def _infer_furnishing(listing: Dict[str, Any]) -> Optional[str]:
    """
    Infer furnishing status from title and description.

    Returns:
        "furnished" | "semi-furnished" | "unfurnished" | None
    """
    title = str(listing.get('title', '')).lower()
    desc = str(listing.get('description', '')).lower()

    if 'furnished' in title or 'furnished' in desc:
        if 'semi' in title or 'semi' in desc or 'partially' in title or 'partially' in desc:
            return 'semi-furnished'
        if 'unfurnished' in title or 'unfurnished' in desc or 'not furnished' in title:
            return 'unfurnished'
        return 'furnished'

    if 'unfurnished' in title or 'unfurnished' in desc:
        return 'unfurnished'

    return None


def _infer_condition(listing: Dict[str, Any]) -> Optional[str]:
    """
    Infer property condition from title and description.

    Returns:
        "new" | "renovated" | "old" | None
    """
    title = str(listing.get('title', '')).lower()
    desc = str(listing.get('description', '')).lower()
    promo_tags = listing.get('promo_tags', [])

    new_keywords = ['new', 'newly built', 'brand new', 'new build', 'under construction']
    renovated_keywords = ['renovated', 'refurbished', 'remodeled', 'upgraded']

    # Handle promo_tags - might be string, list, or NaN from pandas
    if isinstance(promo_tags, str):
        promo_str = promo_tags.lower()
    elif isinstance(promo_tags, list):
        promo_str = ' '.join(str(tag) for tag in promo_tags).lower()
    else:
        promo_str = ''

    if any(kw in title or kw in desc or kw in promo_str for kw in new_keywords):
        return 'new'

    if any(kw in title or kw in desc or kw in promo_str for kw in renovated_keywords):
        return 'renovated'

    return None


def _extract_landmarks(location: str, description: str = '') -> List[str]:
    """
    Extract nearby landmarks from location and description text.

    Returns:
        List of landmark names
    """
    landmarks = []
    text = f"{location} {description}".lower()

    # Common Lagos landmarks
    landmark_keywords = [
        'lekki toll gate', 'chevron', 'ikota shopping complex', 'mega chicken',
        'novare mall', 'shoprite', 'palms mall', 'ikeja city mall',
        'murtala muhammed airport', 'lagos island', 'vi', 'third mainland bridge',
        'eko bridge', 'lagos lagoon', 'beach', 'expressway', 'lekki expressway'
    ]

    for landmark in landmark_keywords:
        if landmark in text:
            landmarks.append(landmark.title())

    return list(set(landmarks))[:5]  # Max 5 landmarks


def _extract_features(description: str, promo_tags: List[str] = None) -> List[str]:
    """
    Extract property features/amenities from description and promo tags.

    Returns:
        List of features
    """
    features = []
    text = description.lower() if description else ''

    feature_keywords = {
        'Swimming pool': ['swimming pool', 'pool'],
        'Gym': ['gym', 'fitness center', 'fitness centre'],
        '24hr power': ['24hr power', '24-hour power', '24hours power', '24 hour power'],
        'Solar power': ['solar', 'solar power', 'solar panel'],
        'Generator': ['generator', 'gen'],
        'Borehole': ['borehole', 'water supply'],
        'Parking': ['parking', 'garage', 'car park'],
        'Security': ['security', '24hr security', 'gated'],
        'CCTV': ['cctv', 'camera', 'surveillance'],
        'Elevator': ['elevator', 'lift'],
        'Balcony': ['balcony', 'terrace'],
        'Penthouse': ['penthouse'],
        'Garden': ['garden', 'green area'],
        'Playground': ['playground', 'play area'],
        'Clubhouse': ['clubhouse', 'club house'],
        'Study room': ['study', 'study room', 'home office'],
        'Ensuite': ['ensuite', 'en-suite', 'master bedroom'],
        'Walk-in closet': ['walk-in closet', 'wardrobe'],
        'Serviced': ['serviced', 'fully serviced'],
        'Gated estate': ['gated', 'gated estate', 'estate'],
        'C of O': ['c of o', 'certificate of occupancy'],
        'Governor consent': ['governor consent', 'governors consent'],
    }

    for feature, keywords in feature_keywords.items():
        if any(kw in text for kw in keywords):
            features.append(feature)

    # Add promo tags as features
    # Handle promo_tags - could be string, list, float/NaN, or None
    if promo_tags:
        if isinstance(promo_tags, str):
            # Split by comma if it's a string
            tags = [tag.strip() for tag in promo_tags.split(',') if tag.strip()]
            features.extend([tag for tag in tags if tag not in features])
        elif isinstance(promo_tags, list):
            features.extend([tag for tag in promo_tags if tag not in features])
        # If it's float/NaN or other type, skip it

    return list(set(features))[:20]  # Max 20 features


def _parse_location_hierarchy(location: str) -> Dict[str, Optional[str]]:
    """
    Parse location into hierarchical components: estate, area, LGA, state.

    Returns:
        Dict with estate_name, area, lga, state
    """
    location_lower = location.lower() if location else ''

    # Extract state (always Lagos for this scraper)
    state = 'Lagos'

    # Common LGAs in Lagos
    lgas = [
        'Alimosho', 'Ajeromi-Ifelodun', 'Kosofe', 'Mushin', 'Oshodi-Isolo',
        'Ojo', 'Ikorodu', 'Surulere', 'Agege', 'Ifako-Ijaiye',
        'Somolu', 'Amuwo-Odofin', 'Lagos Mainland', 'Ikeja', 'Eti-Osa',
        'Badagry', 'Apapa', 'Lagos Island', 'Epe', 'Ibeju-Lekki'
    ]

    lga = None
    for lga_name in lgas:
        if lga_name.lower() in location_lower:
            lga = lga_name
            break

    # Popular areas in Lagos
    areas = [
        'Lekki', 'Ajah', 'Ikoyi', 'Victoria Island', 'VI', 'Ikeja', 'Yaba',
        'Surulere', 'Gbagada', 'Maryland', 'Ogudu', 'Magodo', 'Ojodu',
        'Ikotun', 'Egbeda', 'Iyana Ipaja', 'Abule Egba', 'Ogba', 'Berger',
        'Sangotedo', 'Abraham Adesanya', 'Chevron', 'Ikota', 'VGC',
        'Banana Island', 'Parkview', 'Osapa London', 'Agungi', 'Badore'
    ]

    area = None
    for area_name in areas:
        if area_name.lower() in location_lower:
            area = area_name
            break

    # Estate name (if "Estate" is mentioned, extract preceding words)
    estate_name = None
    if 'estate' in location_lower:
        # Simple extraction: take up to 4 words before "estate"
        import re
        match = re.search(r'([\w\s]{1,40})\s+estate', location_lower, re.IGNORECASE)
        if match:
            estate_name = match.group(1).strip().title() + ' Estate'

    return {
        'estate_name': estate_name,
        'area': area,
        'lga': lga,
        'state': state
    }


def transform_to_enterprise_schema(listing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform flat listing dict to enterprise-grade structured schema.

    Args:
        listing: Flat listing dictionary from scraper

    Returns:
        Enterprise-structured document for Firestore
    """
    from google.cloud.firestore import SERVER_TIMESTAMP, GeoPoint

    # Basic info
    basic_info = {
        'title': _clean_value(listing.get('title')),
        'listing_url': _clean_value(listing.get('listing_url')),
        'source': _clean_value(listing.get('source')),
        'site_key': _clean_value(listing.get('site_key')),
        'status': 'available',  # Default status (can be updated via admin API)
        'verification_status': 'unverified',  # Manual verification required
        'listing_type': _infer_listing_type(listing),
    }

    # Property details
    property_details = {
        'property_type': _clean_value(listing.get('property_type')),
        'property_subtype': None,  # Can be extracted from title (e.g., "Detached Duplex")
        'bedrooms': _clean_value(listing.get('bedrooms')),
        'bathrooms': _clean_value(listing.get('bathrooms')),
        'toilets': _clean_value(listing.get('toilets')),
        'bq': _clean_value(listing.get('bq')),
        'land_size': _clean_value(listing.get('land_size')),
        'building_size': None,  # Extract if available
        'plot_dimensions': None,  # Extract if available
        'year_built': None,  # Extract if available
        'renovation_year': None,
        'furnishing': _infer_furnishing(listing),
        'condition': _infer_condition(listing),
        'floors': None,  # Extract if available
        'units_available': None,  # For multi-unit properties
    }

    # Financial
    financial = {
        'price': _clean_value(listing.get('price')),
        'price_currency': 'NGN',
        'price_per_sqm': _clean_value(listing.get('price_per_sqm')),
        'price_per_bedroom': _clean_value(listing.get('price_per_bedroom')),
        'initial_deposit': _clean_value(listing.get('initial_deposit')),
        'payment_plan': _clean_value(listing.get('payment_plan')),
        'service_charge': _clean_value(listing.get('service_charge')),
        'service_charge_frequency': 'annually' if listing.get('service_charge') else None,
        'legal_fees': None,
        'agent_commission': None,
        'price_negotiable': None,  # Can infer from description
        'rent_frequency': 'annually' if _infer_listing_type(listing) == 'rent' else None,
    }

    # Location
    location_text = _clean_value(listing.get('location'))
    location_hierarchy = _parse_location_hierarchy(location_text or '')
    description = _clean_value(listing.get('description')) or ''

    location = {
        'full_address': location_text,
        'location_text': location_text,
        'estate_name': location_hierarchy['estate_name'] or _clean_value(listing.get('estate_name')),
        'street_name': None,  # Extract if available
        'area': location_hierarchy['area'],
        'lga': location_hierarchy['lga'],
        'state': location_hierarchy['state'],
        'landmarks': _extract_landmarks(location_text or '', description),
        'accessibility_score': None,  # Can be calculated later
    }

    # Add coordinates if available
    coordinates = listing.get('coordinates')
    if coordinates and isinstance(coordinates, dict):
        lat = coordinates.get('lat')
        lng = coordinates.get('lng')
        if lat and lng:
            try:
                location['coordinates'] = GeoPoint(float(lat), float(lng))
            except:
                location['coordinates'] = None
        else:
            location['coordinates'] = None
    else:
        location['coordinates'] = None

    # Amenities
    promo_tags = listing.get('promo_tags', [])
    features = _extract_features(description, promo_tags)

    amenities = {
        'features': features,
        'security': [f for f in features if any(kw in f.lower() for kw in ['security', 'cctv', 'gated'])],
        'utilities': [f for f in features if any(kw in f.lower() for kw in ['power', 'generator', 'solar', 'borehole', 'water'])],
        'parking_spaces': None,  # Extract if available
    }

    # Media
    images = listing.get('images', [])
    if isinstance(images, list):
        media_images = [{'url': img, 'caption': None, 'order': i} for i, img in enumerate(images)]
    else:
        media_images = []

    media = {
        'images': media_images,
        'videos': [],
        'virtual_tour_url': None,
        'floor_plan_url': None,
    }

    # Agent info
    agent_info = {
        'agent_name': _clean_value(listing.get('agent_name')),
        'agent_phone': None,  # Extract from contact_info
        'agent_email': None,  # Extract from contact_info
        'contact_info': _clean_value(listing.get('contact_info')),
        'agency_name': None,
        'agency_logo': None,
        'agent_verified': False,
        'agent_rating': None,
    }

    # Metadata (without SERVER_TIMESTAMP - add at root level)
    scrape_timestamp = _clean_value(listing.get('scrape_timestamp'))
    days_on_market = None
    if scrape_timestamp:
        try:
            scrape_date = datetime.fromisoformat(scrape_timestamp.replace('Z', '+00:00'))
            days_on_market = (datetime.now() - scrape_date).days
        except:
            days_on_market = 0

    metadata = {
        'hash': _clean_value(listing.get('hash')),
        'quality_score': _clean_value(listing.get('quality_score')),
        'scrape_timestamp': scrape_timestamp,
        'last_verified_at': None,
        'view_count': 0,
        'inquiry_count': 0,
        'favorite_count': 0,
        'days_on_market': days_on_market,
        'search_keywords': _generate_search_keywords(listing),
    }

    # Audit trail (use timestamp strings instead of SERVER_TIMESTAMP)
    current_timestamp = datetime.now().isoformat()
    audit_trail = {
        'price_history': [{
            'price': financial['price'],
            'date': current_timestamp,
            'source': basic_info['site_key']
        }] if financial['price'] else [],
        'status_changes': [{
            'from': None,
            'to': 'available',
            'date': current_timestamp
        }],
        'update_log': []
    }

    # Tags
    tags = {
        'promo_tags': promo_tags if promo_tags else [],
        'title_tag': _clean_value(listing.get('title_tag')),
        'premium': False,  # Can set based on price or features
        'featured': False,
        'hot_deal': False,
    }

    # Determine premium status (top 10% by price or 4+ bedrooms with good features)
    if financial['price'] and financial['price'] > 100000000:  # 100M+
        tags['premium'] = True
    elif property_details['bedrooms'] and property_details['bedrooms'] >= 4 and len(features) >= 5:
        tags['premium'] = True

    # Hot deal (good price per sqm or price per bedroom)
    if financial['price_per_bedroom'] and financial['price_per_bedroom'] < 15000000:  # <15M per bedroom
        tags['hot_deal'] = True

    # Combine all categories
    doc_data = {
        'basic_info': basic_info,
        'property_details': property_details,
        'financial': financial,
        'location': location,
        'amenities': amenities,
        'media': media,
        'agent_info': agent_info,
        'metadata': metadata,
        'audit_trail': audit_trail,
        'tags': tags,
        # Timestamps at root level (required by Firestore)
        'uploaded_at': SERVER_TIMESTAMP,
        'updated_at': SERVER_TIMESTAMP,
    }

    return doc_data


def _generate_search_keywords(listing: Dict[str, Any]) -> List[str]:
    """Generate search keywords for full-text search optimization."""
    keywords = []

    # Add location keywords
    location = str(listing.get('location', '')).lower().split()
    keywords.extend(location)

    # Add property type
    prop_type = str(listing.get('property_type', '')).lower()
    if prop_type:
        keywords.append(prop_type)

    # Add bedroom count
    bedrooms = listing.get('bedrooms')
    if bedrooms:
        keywords.append(f"{bedrooms} bedroom")
        keywords.append(f"{bedrooms}br")

    # Add title words
    title = str(listing.get('title', '')).lower().split()
    keywords.extend([w for w in title if len(w) > 3])  # Only words > 3 chars

    # Remove duplicates and clean
    keywords = list(set([k.strip() for k in keywords if k.strip()]))

    return keywords[:50]  # Max 50 keywords


class EnterpriseFirestoreUploader:
    """
    Enterprise-grade Firestore uploader with structured schema.
    """

    def __init__(self, enabled: Optional[bool] = None):
        """
        Initialize enterprise uploader.

        AUTO-ENABLES when Firebase credentials are available.
        Set FIRESTORE_ENABLED=0 to explicitly disable.
        """
        if enabled is None:
            # Auto-enable if credentials are present (check env vars)
            firestore_explicit_disable = os.getenv('FIRESTORE_ENABLED', '1') == '0'
            self.enabled = not firestore_explicit_disable
        else:
            self.enabled = enabled

        self.db = None
        if self.enabled:
            self.db = _get_firestore_client()
            if self.db is None:
                self.enabled = False
                logger.warning("Enterprise Firestore upload disabled (initialization failed)")

    def _upload_single_property_with_retry(
        self,
        site_key: str,
        doc_ref,
        doc_data: Dict[str, Any],
        max_retries: int = 3
    ) -> bool:
        """
        Upload a single property with exponential backoff retry.

        Args:
            site_key: Site identifier
            doc_ref: Firestore document reference
            doc_data: Document data to upload
            max_retries: Maximum retry attempts

        Returns:
            True if successful, False otherwise
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                doc_ref.set(doc_data, merge=True)
                return True
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"{site_key}: Failed after {max_retries} retries: {e}")
                    return False

                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** (retry_count - 1)
                logger.warning(f"{site_key}: Upload failed (attempt {retry_count}/{max_retries}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        return False

    def _upload_with_batch_writes(
        self,
        site_key: str,
        listings: List[Dict[str, Any]],
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """
        Upload listings using Firestore batch writes (OPTIMIZED - 10x faster).

        **BATCH WRITE ARCHITECTURE:**
        - Groups up to 500 operations per batch
        - Single network roundtrip per batch (vs 500 individual calls)
        - Atomic commits per batch
        - 10x faster than individual uploads

        Args:
            site_key: Site identifier
            listings: List of cleaned listings
            batch_size: Operations per batch (max 500)

        Returns:
            Upload statistics dict
        """
        logger.info(f"{site_key}: Using BATCH WRITES (optimized) for {len(listings)} listings...")

        collection_ref = self.db.collection('properties')
        uploaded = 0
        errors = 0
        skipped = 0

        batch = self.db.batch()
        batch_count = 0

        for idx, listing in enumerate(listings, 1):
            try:
                # Get hash for document ID
                doc_hash = listing.get('hash')
                if not doc_hash:
                    logger.warning(f"{site_key}: Listing {idx}/{len(listings)} missing hash, skipping")
                    skipped += 1
                    continue

                # Add site_key to listing if not present
                if 'site_key' not in listing:
                    listing['site_key'] = site_key

                # Transform to enterprise schema
                doc_data = transform_to_enterprise_schema(listing)

                # Add to batch
                doc_ref = collection_ref.document(doc_hash)
                batch.set(doc_ref, doc_data, merge=True)
                batch_count += 1

                # Commit batch when it reaches batch_size or end of list
                if batch_count >= batch_size or idx == len(listings):
                    try:
                        batch.commit()
                        uploaded += batch_count
                        logger.info(f"{site_key}: Batch committed - {uploaded}/{idx} uploaded ({errors} errors, {skipped} skipped)")
                        # Start new batch
                        batch = self.db.batch()
                        batch_count = 0
                    except Exception as e:
                        logger.error(f"{site_key}: Batch commit failed: {e}")
                        errors += batch_count
                        batch = self.db.batch()
                        batch_count = 0

            except Exception as e:
                logger.error(f"{site_key}: Error processing listing {idx}: {e}")
                errors += 1

        total = len(listings)
        logger.info(f"{site_key}: Batch upload complete - {uploaded}/{total} uploaded, {errors} errors, {skipped} skipped")

        return {
            'uploaded': uploaded,
            'errors': errors,
            'skipped': skipped,
            'total': total
        }

    def upload_listings_batch(
        self,
        site_key: str,
        listings: List[Dict[str, Any]],
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """
        Upload listings to Firestore with enterprise schema.

        **AUTO-SELECTS UPLOAD STRATEGY:**
        - Batch writes (optimized, 10x faster) if RP_FIRESTORE_BATCH=1
        - Individual uploads (safer, default) if RP_FIRESTORE_BATCH=0

        Args:
            site_key: Site identifier
            listings: List of cleaned listings
            batch_size: Operations per batch (for batch write mode)

        Returns:
            Upload statistics dict
        """
        if not self.enabled or self.db is None:
            if self.db is None:
                logger.error(f"{site_key}: Firestore upload FAILED - Firebase not initialized (check credentials)")
                logger.error(f"{site_key}: Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS environment variable")
                return {'uploaded': 0, 'errors': len(listings), 'skipped': 0, 'total': len(listings), 'status': 'failed'}
            else:
                logger.info(f"{site_key}: Firestore upload disabled (FIRESTORE_ENABLED=0)")
                return {'uploaded': 0, 'errors': 0, 'skipped': 0, 'total': len(listings), 'status': 'disabled'}

        if not listings:
            logger.info(f"{site_key}: No listings to upload")
            return {'uploaded': 0, 'errors': 0, 'skipped': 0, 'total': 0}

        # Check if batch writes are enabled
        use_batch_writes = os.getenv('RP_FIRESTORE_BATCH', '0') == '1'

        if use_batch_writes:
            return self._upload_with_batch_writes(site_key, listings, batch_size)

        # Default: Individual uploads (safer, working method)
        logger.info(f"{site_key}: Using INDIVIDUAL UPLOADS (safe mode) for {len(listings)} listings...")
        logger.info(f"{site_key}: TIP: Set RP_FIRESTORE_BATCH=1 for 10x faster uploads")

        collection_ref = self.db.collection('properties')
        uploaded = 0
        errors = 0
        skipped = 0

        # Stream upload: process each property individually
        for idx, listing in enumerate(listings, 1):
            try:
                # Get hash for document ID
                doc_hash = listing.get('hash')
                if not doc_hash:
                    logger.warning(f"{site_key}: Listing {idx}/{len(listings)} missing hash, skipping")
                    skipped += 1
                    continue

                # Add site_key to listing if not present
                if 'site_key' not in listing:
                    listing['site_key'] = site_key

                # Transform to enterprise schema
                doc_data = transform_to_enterprise_schema(listing)

                # Upload with retry logic
                doc_ref = collection_ref.document(doc_hash)
                success = self._upload_single_property_with_retry(site_key, doc_ref, doc_data, max_retries=3)

                if success:
                    uploaded += 1
                    # Log progress every 10 properties
                    if idx % 10 == 0 or idx == len(listings):
                        logger.info(f"{site_key}: Progress: {uploaded}/{idx} uploaded ({errors} errors, {skipped} skipped)")
                else:
                    errors += 1

            except Exception as e:
                logger.error(f"{site_key}: Error processing listing {idx}: {e}")
                errors += 1

        total = len(listings)
        logger.info(f"{site_key}: Individual upload complete - {uploaded}/{total} uploaded, {errors} errors, {skipped} skipped")

        # Update site metadata
        try:
            self._update_site_metadata(site_key, uploaded)
        except Exception as e:
            logger.warning(f"{site_key}: Failed to update site metadata: {e}")

        return {
            'uploaded': uploaded,
            'errors': errors,
            'skipped': skipped,
            'total': total
        }

    def _update_site_metadata(self, site_key: str, count: int):
        """Update site metadata in Firestore."""
        from google.cloud.firestore import SERVER_TIMESTAMP

        metadata_ref = self.db.collection('site_metadata').document(site_key)
        metadata_ref.set({
            'site_key': site_key,
            'total_properties': count,
            'last_updated': SERVER_TIMESTAMP,
        }, merge=True)


# Convenience function for backward compatibility
def upload_listings_to_firestore(site_key: str, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Upload listings to Firestore with enterprise schema (convenience function).

    Args:
        site_key: Site identifier
        listings: List of cleaned listings

    Returns:
        Upload statistics dict
    """
    uploader = EnterpriseFirestoreUploader()
    return uploader.upload_listings_batch(site_key, listings)
