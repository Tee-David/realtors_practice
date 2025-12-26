"""
Data Quality Enhancer - Integrates NLP and Enhanced Dictionaries

Uses existing NLP module and enhanced dictionaries to:
1. Detect category pages vs real properties
2. Enhance generic titles with better descriptions
3. Validate and fix bedroom/bathroom counts (reject phone numbers)
4. Extract amenities from descriptions
5. Improve property type classification
6. Add quality scores

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import existing NLP capabilities
try:
    from core.universal_nlp import (
        classify_property_type,
        extract_amenities,
        enhance_title_with_nlp,
        analyze_text_quality,
        extract_contact_info,
        NLP_AVAILABLE
    )
    NLP_IMPORTED = True
except ImportError:
    logging.warning("Could not import universal_nlp module")
    NLP_IMPORTED = False

# Import data cleaner utilities
try:
    from core.data_cleaner import (
        normalize_price,
        normalize_location,
        normalize_property_type
    )
    DATA_CLEANER_IMPORTED = True
except ImportError:
    logging.warning("Could not import data_cleaner module")
    DATA_CLEANER_IMPORTED = False

logger = logging.getLogger(__name__)


# ============================================================================
# CATEGORY PAGE DETECTION
# ============================================================================

CATEGORY_URL_PATTERNS = [
    r'/property-location/',
    r'/category/',
    r'/area/',
    r'/location/',
    r'maps\.google\.com',
    r'goo\.gl/maps',
    r'/search\?',
    r'/browse/',
    r'/listings/$',  # Just the listings page, not a specific property
]

CATEGORY_TITLE_PATTERNS = [
    # Just location names without property details
    r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # "Ikoyi", "Victoria Island"
    r'^Properties? (?:in|for Sale|for Rent)',  # "Properties in Lagos"
    r'^(?:Lagos|Abuja|Port Harcourt)\s*$',  # Just city names
]

GENERIC_TITLES = [
    'property in lagos',
    'house for sale',
    'apartment for rent',
    'land for sale',
    'properties',
    'listing',
]


def is_category_page(property_data: Dict) -> Tuple[bool, str]:
    """
    Detect if a property listing is actually a category/landing page.

    Args:
        property_data: Property dictionary from Firestore

    Returns:
        Tuple of (is_category, reason)
    """
    reasons = []

    # Check 1: URL patterns
    url = property_data.get('basic_info', {}).get('url', '')
    for pattern in CATEGORY_URL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            reasons.append(f"URL matches category pattern: {pattern}")

    # Check 2: Generic title patterns
    title = property_data.get('basic_info', {}).get('title', '')
    if title:
        title_lower = title.lower().strip()

        # Check against generic titles
        if title_lower in GENERIC_TITLES:
            reasons.append(f"Generic title: '{title}'")

        # Check against patterns
        for pattern in CATEGORY_TITLE_PATTERNS:
            if re.match(pattern, title):
                reasons.append(f"Title matches category pattern: {pattern}")

    # Check 3: Unrealistic property data (likely aggregated category stats)
    bedrooms = property_data.get('property_details', {}).get('bedrooms')
    bathrooms = property_data.get('property_details', {}).get('bathrooms')

    if bedrooms and bedrooms > 10:
        reasons.append(f"Unrealistic bedrooms: {bedrooms} (likely phone number)")

    if bathrooms and bathrooms > 10:
        reasons.append(f"Unrealistic bathrooms: {bathrooms} (likely phone number)")

    # Check 4: Missing critical fields
    price = property_data.get('financial', {}).get('price')
    location = property_data.get('location', {}).get('area')

    critical_missing = []
    if not price or price == 0:
        critical_missing.append('price')
    if not location or len(location) < 3:
        critical_missing.append('location')
    if not title or len(title) < 10:
        critical_missing.append('title')

    if len(critical_missing) >= 2:
        reasons.append(f"Missing critical fields: {', '.join(critical_missing)}")

    # Check 5: Description is just location info
    description = property_data.get('basic_info', {}).get('description', '')
    if description:
        desc_lower = description.lower()
        location_keywords = ['view properties in', 'browse properties', 'search properties',
                            'all properties in', 'listings in']
        if any(keyword in desc_lower for keyword in location_keywords):
            reasons.append("Description contains category page keywords")

    is_category = len(reasons) >= 2  # At least 2 red flags = category page
    reason_text = "; ".join(reasons) if reasons else "None"

    return is_category, reason_text


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_bedroom_count(bedrooms: Any) -> Optional[int]:
    """
    Validate bedroom count is realistic (not a phone number).

    Args:
        bedrooms: Raw bedroom value

    Returns:
        Validated bedroom count or None
    """
    if bedrooms is None:
        return None

    try:
        count = int(bedrooms)

        # Reasonable range: 0-10 bedrooms
        # Anything above 10 is likely a phone number (08012345678 → 8)
        if 0 <= count <= 10:
            return count
        else:
            logger.debug(f"Rejecting unrealistic bedroom count: {count}")
            return None
    except (ValueError, TypeError):
        return None


def validate_bathroom_count(bathrooms: Any) -> Optional[int]:
    """
    Validate bathroom count is realistic (not a phone number).

    Args:
        bathrooms: Raw bathroom value

    Returns:
        Validated bathroom count or None
    """
    if bathrooms is None:
        return None

    try:
        count = int(bathrooms)

        # Reasonable range: 0-10 bathrooms
        if 0 <= count <= 10:
            return count
        else:
            logger.debug(f"Rejecting unrealistic bathroom count: {count}")
            return None
    except (ValueError, TypeError):
        return None


def validate_price(price: Any) -> Optional[int]:
    """
    Validate price is in reasonable range for Nigerian properties.

    Args:
        price: Raw price value

    Returns:
        Validated price or None
    """
    if price is None:
        return None

    try:
        amount = int(price)

        # Reasonable range: 100K - 10B NGN
        MIN_PRICE = 100_000  # 100K NGN
        MAX_PRICE = 10_000_000_000  # 10B NGN

        if MIN_PRICE <= amount <= MAX_PRICE:
            return amount
        else:
            logger.debug(f"Price outside reasonable range: {amount:,} NGN")
            return None
    except (ValueError, TypeError):
        return None


# ============================================================================
# DATA ENHANCEMENT
# ============================================================================

def enhance_title(property_data: Dict) -> str:
    """
    Enhance generic property titles using NLP.

    Args:
        property_data: Property dictionary

    Returns:
        Enhanced title
    """
    if not NLP_IMPORTED:
        return property_data.get('basic_info', {}).get('title', '')

    title = property_data.get('basic_info', {}).get('title', '')
    description = property_data.get('basic_info', {}).get('description', '')
    location = property_data.get('location', {}).get('area', '')

    # Use NLP to enhance
    enhanced = enhance_title_with_nlp(title, description, location)

    return enhanced


def extract_amenities_from_property(property_data: Dict) -> List[str]:
    """
    Extract amenities from property description using NLP.

    Args:
        property_data: Property dictionary

    Returns:
        List of amenities
    """
    if not NLP_IMPORTED:
        return property_data.get('amenities', {}).get('features', [])

    # Get existing amenities
    existing = property_data.get('amenities', {}).get('features', []) or []

    # Extract from description
    description = property_data.get('basic_info', {}).get('description', '')
    title = property_data.get('basic_info', {}).get('title', '')

    combined_text = f"{title} {description}"
    extracted = extract_amenities(combined_text)

    # Merge and deduplicate
    all_amenities = list(set(existing + extracted))

    return all_amenities


def improve_property_type(property_data: Dict) -> Optional[str]:
    """
    Improve property type classification using NLP.

    Args:
        property_data: Property dictionary

    Returns:
        Improved property type
    """
    if not NLP_IMPORTED:
        return property_data.get('property_details', {}).get('property_type')

    existing_type = property_data.get('property_details', {}).get('property_type')

    # If we already have a good type, keep it
    if existing_type and len(existing_type) > 5:
        return existing_type

    # Try to classify from title and description
    title = property_data.get('basic_info', {}).get('title', '')
    description = property_data.get('basic_info', {}).get('description', '')

    combined_text = f"{title} {description}"
    classified = classify_property_type(combined_text)

    # Return classified type or keep existing
    return classified or existing_type


def calculate_quality_score(property_data: Dict) -> int:
    """
    Calculate overall quality score (0-100) for a property.

    Higher score = more complete and reliable data.

    Args:
        property_data: Property dictionary

    Returns:
        Quality score (0-100)
    """
    score = 0

    # Basic info (40 points max)
    if property_data.get('basic_info', {}).get('title'):
        title_len = len(property_data['basic_info']['title'])
        if title_len > 30:
            score += 15
        elif title_len > 15:
            score += 10
        elif title_len > 5:
            score += 5

    if property_data.get('basic_info', {}).get('description'):
        desc_len = len(property_data['basic_info']['description'])
        if desc_len > 200:
            score += 15
        elif desc_len > 50:
            score += 10
        elif desc_len > 10:
            score += 5

    if property_data.get('basic_info', {}).get('url'):
        score += 10

    # Financial (20 points max)
    price = property_data.get('financial', {}).get('price')
    if price and validate_price(price):
        score += 20

    # Location (15 points max)
    if property_data.get('location', {}).get('area'):
        score += 10
    if property_data.get('location', {}).get('coordinates'):
        score += 5

    # Property details (15 points max)
    if property_data.get('property_details', {}).get('property_type'):
        score += 5

    bedrooms = property_data.get('property_details', {}).get('bedrooms')
    if bedrooms and validate_bedroom_count(bedrooms):
        score += 5

    bathrooms = property_data.get('property_details', {}).get('bathrooms')
    if bathrooms and validate_bathroom_count(bathrooms):
        score += 5

    # Media (5 points max)
    images = property_data.get('media', {}).get('images', [])
    if images and len(images) > 0:
        score += 5

    # Agent info (5 points max)
    if property_data.get('agent_info', {}).get('contact'):
        score += 5

    return min(100, score)


# ============================================================================
# MAIN ENHANCEMENT FUNCTION
# ============================================================================

def enhance_property_data(property_data: Dict,
                         validate_only: bool = False) -> Dict[str, Any]:
    """
    Enhance a single property's data quality using NLP and validation.

    Args:
        property_data: Property dictionary from Firestore
        validate_only: If True, only validate without enhancing

    Returns:
        Dictionary with enhanced property and metadata:
        {
            'enhanced_property': Dict,
            'is_category_page': bool,
            'category_reason': str,
            'quality_score': int,
            'changes_made': List[str]
        }
    """
    changes = []

    # Step 1: Check if category page
    is_category, category_reason = is_category_page(property_data)

    if is_category:
        logger.info(f"Category page detected: {category_reason}")
        return {
            'enhanced_property': property_data,
            'is_category_page': True,
            'category_reason': category_reason,
            'quality_score': 0,
            'changes_made': []
        }

    # Make a copy for enhancement
    enhanced = dict(property_data)

    if not validate_only:
        # Step 2: Enhance title
        original_title = enhanced.get('basic_info', {}).get('title', '')
        enhanced_title = enhance_title(enhanced)
        if enhanced_title != original_title:
            if 'basic_info' not in enhanced:
                enhanced['basic_info'] = {}
            enhanced['basic_info']['title'] = enhanced_title
            changes.append(f"Enhanced title: '{original_title}' → '{enhanced_title}'")

        # Step 3: Extract and add amenities
        if NLP_IMPORTED:
            amenities = extract_amenities_from_property(enhanced)
            original_amenities = enhanced.get('amenities', {}).get('features', [])
            if amenities and amenities != original_amenities:
                if 'amenities' not in enhanced:
                    enhanced['amenities'] = {}
                enhanced['amenities']['features'] = amenities
                changes.append(f"Added {len(amenities)} amenities")

        # Step 4: Improve property type
        if NLP_IMPORTED:
            improved_type = improve_property_type(enhanced)
            original_type = enhanced.get('property_details', {}).get('property_type')
            if improved_type and improved_type != original_type:
                if 'property_details' not in enhanced:
                    enhanced['property_details'] = {}
                enhanced['property_details']['property_type'] = improved_type
                changes.append(f"Improved property type: '{original_type}' → '{improved_type}'")

    # Step 5: Validate bedroom count
    bedrooms = enhanced.get('property_details', {}).get('bedrooms')
    validated_bedrooms = validate_bedroom_count(bedrooms)
    if bedrooms != validated_bedrooms:
        if 'property_details' not in enhanced:
            enhanced['property_details'] = {}
        enhanced['property_details']['bedrooms'] = validated_bedrooms
        changes.append(f"Fixed bedrooms: {bedrooms} → {validated_bedrooms}")

    # Step 6: Validate bathroom count
    bathrooms = enhanced.get('property_details', {}).get('bathrooms')
    validated_bathrooms = validate_bathroom_count(bathrooms)
    if bathrooms != validated_bathrooms:
        if 'property_details' not in enhanced:
            enhanced['property_details'] = {}
        enhanced['property_details']['bathrooms'] = validated_bathrooms
        changes.append(f"Fixed bathrooms: {bathrooms} → {validated_bathrooms}")

    # Step 7: Validate price
    price = enhanced.get('financial', {}).get('price')
    validated_price = validate_price(price)
    if price != validated_price:
        if 'financial' not in enhanced:
            enhanced['financial'] = {}
        enhanced['financial']['price'] = validated_price
        changes.append(f"Fixed price: {price:,} → {validated_price:,}" if validated_price else f"Removed invalid price: {price}")

    # Step 8: Calculate quality score
    quality_score = calculate_quality_score(enhanced)

    # Add metadata
    if 'metadata' not in enhanced:
        enhanced['metadata'] = {}
    enhanced['metadata']['quality_score'] = quality_score
    enhanced['metadata']['last_enhanced'] = datetime.now().isoformat()

    return {
        'enhanced_property': enhanced,
        'is_category_page': False,
        'category_reason': None,
        'quality_score': quality_score,
        'changes_made': changes
    }


def batch_enhance_properties(properties: List[Dict],
                             validate_only: bool = False) -> Dict[str, Any]:
    """
    Enhance multiple properties in batch.

    Args:
        properties: List of property dictionaries
        validate_only: If True, only validate without enhancing

    Returns:
        Dictionary with results:
        {
            'enhanced_properties': List[Dict],
            'category_pages': List[Dict],
            'total_processed': int,
            'total_enhanced': int,
            'total_category_pages': int,
            'average_quality_score': float
        }
    """
    enhanced_properties = []
    category_pages = []
    total_changes = 0
    total_quality = 0

    for prop in properties:
        result = enhance_property_data(prop, validate_only=validate_only)

        if result['is_category_page']:
            category_pages.append({
                'property': prop,
                'reason': result['category_reason']
            })
        else:
            enhanced_properties.append(result['enhanced_property'])
            total_changes += len(result['changes_made'])
            total_quality += result['quality_score']

    avg_quality = total_quality / len(enhanced_properties) if enhanced_properties else 0

    return {
        'enhanced_properties': enhanced_properties,
        'category_pages': category_pages,
        'total_processed': len(properties),
        'total_enhanced': len(enhanced_properties),
        'total_category_pages': len(category_pages),
        'total_changes': total_changes,
        'average_quality_score': round(avg_quality, 2)
    }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("DATA QUALITY ENHANCER TEST")
    print("=" * 80)
    print(f"NLP Module Available: {NLP_AVAILABLE}")
    print(f"NLP Module Imported: {NLP_IMPORTED}")
    print(f"Data Cleaner Imported: {DATA_CLEANER_IMPORTED}")
    print()

    # Test property 1: Good property
    test_property_good = {
        'basic_info': {
            'title': '3 Bedroom Flat in Lekki Phase 1',
            'description': 'Beautiful apartment with modern kitchen, swimming pool, gym, and 24hr power',
            'url': 'https://example.com/properties/12345',
            'status': 'available',
            'listing_type': 'sale'
        },
        'financial': {
            'price': 45000000,
            'currency': 'NGN'
        },
        'location': {
            'area': 'Lekki Phase 1',
            'lga': 'Eti-Osa',
            'state': 'Lagos'
        },
        'property_details': {
            'bedrooms': 3,
            'bathrooms': 2,
            'property_type': 'Flat'
        },
        'amenities': {
            'features': ['parking']
        }
    }

    # Test property 2: Category page
    test_property_category = {
        'basic_info': {
            'title': 'Ikoyi',
            'description': 'View all properties in Ikoyi',
            'url': 'https://example.com/property-location/ikoyi',
            'status': 'available',
            'listing_type': 'sale'
        },
        'financial': {
            'price': 0
        },
        'location': {
            'area': 'Ikoyi'
        },
        'property_details': {
            'bedrooms': 35,  # Phone number!
            'bathrooms': 100  # Phone number!
        }
    }

    # Test property 3: Needs enhancement
    test_property_needs_enhancement = {
        'basic_info': {
            'title': 'Lekki',
            'description': 'Nice 4 bedroom duplex with swimming pool, gym, and fitted kitchen in Lekki Phase 1',
            'url': 'https://example.com/properties/67890',
            'status': 'available',
            'listing_type': 'sale'
        },
        'financial': {
            'price': 75000000
        },
        'location': {
            'area': 'Lekki Phase 1'
        },
        'property_details': {
            'bedrooms': 4,
            'bathrooms': 3
        }
    }

    print("\nTest 1: Good Property")
    print("-" * 80)
    result1 = enhance_property_data(test_property_good)
    print(f"Is Category Page: {result1['is_category_page']}")
    print(f"Quality Score: {result1['quality_score']}/100")
    print(f"Changes Made: {len(result1['changes_made'])}")
    for change in result1['changes_made']:
        print(f"  - {change}")

    print("\nTest 2: Category Page Detection")
    print("-" * 80)
    result2 = enhance_property_data(test_property_category)
    print(f"Is Category Page: {result2['is_category_page']}")
    print(f"Reason: {result2['category_reason']}")
    print(f"Quality Score: {result2['quality_score']}/100")

    print("\nTest 3: Property Needs Enhancement")
    print("-" * 80)
    result3 = enhance_property_data(test_property_needs_enhancement)
    print(f"Is Category Page: {result3['is_category_page']}")
    print(f"Quality Score: {result3['quality_score']}/100")
    print(f"Changes Made: {len(result3['changes_made'])}")
    for change in result3['changes_made']:
        print(f"  - {change}")
    print(f"\nEnhanced Title: {result3['enhanced_property']['basic_info']['title']}")
    if 'amenities' in result3['enhanced_property']:
        print(f"Extracted Amenities: {result3['enhanced_property']['amenities'].get('features', [])}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
