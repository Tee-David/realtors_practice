"""
Universal Data Validator

Validates scraped property data using universal rules that apply to ANY site.
Calculates quality scores and identifies invalid data.

This module:
- Rejects properties with obviously bad data (phone numbers as counts, generic titles)
- Calculates quality scores (0-100)
- Provides detailed validation reasons
- Works without site-specific configuration

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

# Generic location names that shouldn't be property titles
GENERIC_LOCATION_NAMES = [
    'Chevron', 'Ikate', 'Lekki', 'Victoria Island', 'Ikoyi', 'Ajah',
    'Ikeja', 'Yaba', 'Surulere', 'Maryland', 'Magodo', 'Lagos',
    'Nigeria', 'VI', 'VGC', 'Osapa', 'Sangotedo'
]


def validate_property(property_dict: Dict) -> Tuple[bool, List[str]]:
    """
    Universal validation rules for ANY scraped property.

    Args:
        property_dict: Dictionary containing property data
            Expected keys: title, price, location, bedrooms, bathrooms, url

    Returns:
        Tuple of (is_valid: bool, reasons: List[str])
        - is_valid: True if property passes all validation rules
        - reasons: List of strings explaining why property is invalid (empty if valid)
    """
    reasons = []

    try:
        # Rule 1: Title must be meaningful (not generic location)
        title = property_dict.get('title', '')
        if not title or len(title) < 10:
            reasons.append(f"Title too short or missing: '{title}'")

        # Check if title is just a generic location name
        if title.strip() in GENERIC_LOCATION_NAMES:
            reasons.append(f"Title is generic location name: '{title}'")

        # Rule 2: Price validation
        price = property_dict.get('price', 0)
        if price is None or price == 0:
            reasons.append("Price missing or zero")
        elif price < 100_000:  # Below 100K NGN is suspicious for real estate
            reasons.append(f"Price suspiciously low: ₦{price:,.0f}")
        elif price > 10_000_000_000:  # Above 10B NGN is suspicious
            reasons.append(f"Price suspiciously high: ₦{price:,.0f}")

        # Rule 3: Bedroom/Bathroom validation (reject phone numbers)
        bedrooms = property_dict.get('bedrooms')
        bathrooms = property_dict.get('bathrooms')

        if bedrooms is not None and (bedrooms < 0 or bedrooms > 10):
            reasons.append(f"Bedrooms unrealistic (likely phone number): {bedrooms}")

        if bathrooms is not None and (bathrooms < 0 or bathrooms > 10):
            reasons.append(f"Bathrooms unrealistic (likely phone number): {bathrooms}")

        # Rule 4: Location must be present
        location = property_dict.get('location', '')
        if not location or len(location) < 3:
            reasons.append("Location missing or too short")

        # Rule 5: URL must not be category page
        url = property_dict.get('url', '')
        category_patterns = [
            '/property-location/', '/listings/', '/search/',
            '/category/', '/browse/', '/filter/', '/results/'
        ]

        for pattern in category_patterns:
            if pattern in url.lower():
                reasons.append(f"URL appears to be category page: {url}")
                break

        # Rule 6: Must have SOME useful data (not completely empty)
        has_any_data = any([
            title and len(title) >= 10,
            price and price > 0,
            location,
            bedrooms is not None,
            bathrooms is not None
        ])

        if not has_any_data:
            reasons.append("Property has no useful data")

        is_valid = len(reasons) == 0

        if not is_valid:
            logger.info(f"Property validation failed: {reasons}")

        return is_valid, reasons

    except Exception as e:
        logger.error(f"Error during property validation: {e}")
        return False, [f"Validation error: {str(e)}"]


def calculate_quality_score(property_dict: Dict) -> int:
    """
    Calculate quality score (0-100) for a property.

    Higher score = better data quality.
    Score breakdown:
    - Title: 15 points (10 if exists, +5 if detailed)
    - Price: 20 points (15 if exists, +5 if reasonable)
    - Location: 20 points
    - Bedrooms: 10 points
    - Bathrooms: 10 points
    - Description: 15 points (10 if exists, +5 if detailed)
    - Images: 10 points

    Args:
        property_dict: Dictionary containing property data

    Returns:
        Quality score (0-100)
    """
    try:
        score = 0

        # Title quality (15 points max)
        title = property_dict.get('title', '')
        if title:
            score += 10
            if len(title) > 30:  # Detailed title
                score += 5
            elif len(title) < 15:  # Too short, deduct points
                score -= 5

        # Check if title is generic
        if title.strip() in GENERIC_LOCATION_NAMES:
            score -= 10  # Penalty for generic title

        # Price quality (20 points max)
        price = property_dict.get('price', 0)
        if price and price > 0:
            score += 15
            # Bonus if price is in reasonable range
            if 500_000 <= price <= 1_000_000_000:
                score += 5

        # Location quality (20 points)
        location = property_dict.get('location', '')
        if location:
            score += 20

        # Bedrooms (10 points)
        bedrooms = property_dict.get('bedrooms')
        if bedrooms is not None and 0 <= bedrooms <= 10:
            score += 10

        # Bathrooms (10 points)
        bathrooms = property_dict.get('bathrooms')
        if bathrooms is not None and 0 <= bathrooms <= 10:
            score += 10

        # Description quality (15 points max)
        description = property_dict.get('description', '')
        if description:
            score += 10
            if len(description) > 100:  # Detailed description
                score += 5

        # Images (10 points)
        # Check for image_url, images list, or media.images
        has_images = False

        if property_dict.get('image_url'):
            has_images = True
        elif property_dict.get('images') and len(property_dict.get('images', [])) > 0:
            has_images = True
        elif property_dict.get('media', {}).get('images'):
            has_images = True

        if has_images:
            score += 10

        # Ensure score is within 0-100 range
        score = max(0, min(100, score))

        return score

    except Exception as e:
        logger.error(f"Error calculating quality score: {e}")
        return 0


def is_phone_number(number: int) -> bool:
    """
    Detect if a number is likely a phone number (not a room count).

    Nigerian phone numbers:
    - 11 digits (08012345678)
    - 10 digits (8012345678)
    - Or suspiciously large (> 20)

    Args:
        number: Integer to check

    Returns:
        True if likely a phone number, False otherwise
    """
    if number is None:
        return False

    # Nigerian phone numbers are 10-11 digits
    if number > 999_999_999:  # 9+ digits
        return True

    # Unrealistic room counts
    if number > 20:
        return True

    return False


def get_validation_summary(property_dict: Dict) -> Dict:
    """
    Get comprehensive validation summary for a property.

    Args:
        property_dict: Dictionary containing property data

    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'quality_score': int,
            'reasons': List[str],
            'warnings': List[str],
            'recommendations': List[str]
        }
    """
    is_valid, reasons = validate_property(property_dict)
    quality_score = calculate_quality_score(property_dict)

    warnings = []
    recommendations = []

    # Generate warnings
    if quality_score < 50:
        warnings.append(f"Low quality score: {quality_score}/100")

    if not property_dict.get('image_url') and not property_dict.get('images'):
        warnings.append("No images available")

    if not property_dict.get('description') or len(property_dict.get('description', '')) < 50:
        warnings.append("Missing or short description")

    # Generate recommendations
    if not property_dict.get('location'):
        recommendations.append("Add location information")

    if not property_dict.get('price') or property_dict.get('price', 0) == 0:
        recommendations.append("Add price information")

    if not property_dict.get('bedrooms'):
        recommendations.append("Add bedroom count")

    if not property_dict.get('bathrooms'):
        recommendations.append("Add bathroom count")

    return {
        'is_valid': is_valid,
        'quality_score': quality_score,
        'reasons': reasons,
        'warnings': warnings,
        'recommendations': recommendations
    }


def should_save_property(property_dict: Dict, min_quality_score: int = 40) -> Tuple[bool, str]:
    """
    Determine if a property should be saved to database.

    Args:
        property_dict: Dictionary containing property data
        min_quality_score: Minimum quality score required (default: 40)

    Returns:
        Tuple of (should_save: bool, reason: str)
    """
    try:
        # First check if valid
        is_valid, reasons = validate_property(property_dict)

        if not is_valid:
            reason = f"Failed validation: {'; '.join(reasons)}"
            return False, reason

        # Check quality score
        quality_score = calculate_quality_score(property_dict)

        if quality_score < min_quality_score:
            reason = f"Quality score too low: {quality_score}/{min_quality_score}"
            return False, reason

        # Passed all checks
        return True, f"Valid property with quality score {quality_score}/100"

    except Exception as e:
        logger.error(f"Error in should_save_property: {e}")
        return False, f"Error: {str(e)}"


# Example usage and testing
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    print("="*60)
    print("UNIVERSAL VALIDATOR TESTING")
    print("="*60)

    # Test 1: Good property
    print("\n\nTest 1: Good Property")
    good_property = {
        'title': 'Luxury 3 Bedroom Apartment in Lekki Phase 1, Victoria Island',
        'price': 35_000_000,
        'location': 'Lekki Phase 1, Victoria Island',
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'This beautiful 3 bedroom apartment is located in the heart of Lekki Phase 1. Features include modern kitchen, spacious living room, secure parking, 24hr power supply, swimming pool, and gym.',
        'image_url': 'https://example.com/images/property1.jpg',
        'url': 'https://example.com/property-details/12345'
    }

    summary = get_validation_summary(good_property)
    print(f"Valid: {summary['is_valid']}")
    print(f"Quality Score: {summary['quality_score']}/100")
    print(f"Warnings: {summary['warnings']}")
    print(f"Recommendations: {summary['recommendations']}")

    should_save, reason = should_save_property(good_property)
    print(f"Should Save: {should_save} ({reason})")

    # Test 2: Category page (bad)
    print("\n\nTest 2: Category Page (Invalid)")
    category_page = {
        'title': 'Lekki',
        'price': 0,
        'location': 'Lagos',
        'url': 'https://example.com/property-location/lekki'
    }

    summary = get_validation_summary(category_page)
    print(f"Valid: {summary['is_valid']}")
    print(f"Quality Score: {summary['quality_score']}/100")
    print(f"Reasons: {summary['reasons']}")

    should_save, reason = should_save_property(category_page)
    print(f"Should Save: {should_save} ({reason})")

    # Test 3: Phone number as bathroom count (bad)
    print("\n\nTest 3: Phone Number as Bathroom Count (Invalid)")
    phone_property = {
        'title': 'Nice apartment in Ikeja',
        'price': 25_000_000,
        'location': 'Ikeja',
        'bedrooms': 3,
        'bathrooms': 8012345678,  # Phone number!
        'url': 'https://example.com/property/456'
    }

    summary = get_validation_summary(phone_property)
    print(f"Valid: {summary['is_valid']}")
    print(f"Quality Score: {summary['quality_score']}/100")
    print(f"Reasons: {summary['reasons']}")

    should_save, reason = should_save_property(phone_property)
    print(f"Should Save: {should_save} ({reason})")

    # Test 4: Low quality but valid
    print("\n\nTest 4: Low Quality Property")
    low_quality = {
        'title': 'Apartment for sale',
        'price': 15_000_000,
        'location': 'Lagos',
        'url': 'https://example.com/property/789'
    }

    summary = get_validation_summary(low_quality)
    print(f"Valid: {summary['is_valid']}")
    print(f"Quality Score: {summary['quality_score']}/100")
    print(f"Warnings: {summary['warnings']}")
    print(f"Recommendations: {summary['recommendations']}")

    should_save, reason = should_save_property(low_quality, min_quality_score=40)
    print(f"Should Save (min 40): {should_save} ({reason})")

    should_save, reason = should_save_property(low_quality, min_quality_score=60)
    print(f"Should Save (min 60): {should_save} ({reason})")

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
