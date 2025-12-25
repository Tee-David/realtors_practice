"""
Universal Scraper Integration Layer

Ties together all universal intelligence modules:
- universal_detector (category detection)
- universal_extractor (field extraction)
- universal_validator (data validation)
- universal_nlp (NLP enhancements)

This module provides simple wrapper functions that can be called from
existing code (scraper_engine.py, cleaner.py, etc.) without breaking changes.

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import logging
from typing import Dict, Optional, Tuple, List
from bs4 import BeautifulSoup

# Import universal modules
from core.universal_detector import is_category_page, get_detection_confidence
from core.universal_extractor import (
    extract_price_universal,
    extract_location_universal,
    extract_bedrooms_universal,
    extract_bathrooms_universal,
    extract_title_universal,
    extract_description_universal,
    extract_all_universal
)
from core.universal_validator import (
    validate_property,
    calculate_quality_score,
    should_save_property,
    get_validation_summary
)

# Try to import NLP (optional)
try:
    from core.universal_nlp import (
        extract_location_with_nlp,
        classify_property_type,
        extract_amenities,
        enhance_title_with_nlp,
        analyze_text_quality,
        NLP_AVAILABLE
    )
except ImportError:
    NLP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("universal_nlp not available, NLP features disabled")

logger = logging.getLogger(__name__)


def should_skip_url(url: str, html: str, extracted_data: Optional[Dict] = None) -> Tuple[bool, str]:
    """
    Determine if a URL should be skipped (because it's a category page).

    Args:
        url: Page URL
        html: Page HTML content
        extracted_data: Optional dict of already-extracted data

    Returns:
        Tuple of (should_skip: bool, reason: str)
        - should_skip: True if should skip, False if should scrape
        - reason: Explanation why
    """
    try:
        if extracted_data is None:
            extracted_data = {}

        is_cat, signals = is_category_page(url, html, extracted_data)
        confidence = get_detection_confidence(signals)

        if is_cat:
            reason = f"Category page detected (confidence: {confidence}, signals: {signals})"
            logger.info(f"Skipping {url[:60]}... - {reason}")
            return True, reason
        else:
            reason = f"Property page (confidence: {confidence}, signals: {signals})"
            logger.debug(f"Processing {url[:60]}... - {reason}")
            return False, reason

    except Exception as e:
        logger.error(f"Error in category detection for {url[:60]}...: {e}")
        # On error, default to NOT skipping (conservative approach)
        return False, f"Error in detection: {e}"


def enhance_extraction(url: str, html: str, existing_data: Optional[Dict] = None) -> Dict:
    """
    Enhance data extraction using universal intelligence.

    Uses pattern matching and NLP to extract fields that traditional
    CSS selectors might miss.

    Args:
        url: Page URL
        html: Page HTML content
        existing_data: Optional dict of data already extracted by parsers

    Returns:
        Dictionary with enhanced/additional fields
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()

        # Start with existing data or empty dict
        enhanced = existing_data.copy() if existing_data else {}

        # Extract all fields using universal extractor
        universal_data = extract_all_universal(soup, url, text)

        # Merge: prefer existing_data, use universal as fallback
        for key, value in universal_data.items():
            if value is not None:
                # If existing data doesn't have this field or it's empty, use universal
                if key not in enhanced or enhanced.get(key) is None or enhanced.get(key) == "":
                    enhanced[key] = value
                    logger.debug(f"Enhanced {key} using universal extraction: {value}")

        # NLP enhancements (if available)
        if NLP_AVAILABLE:
            # Classify property type if missing
            if not enhanced.get('property_type'):
                prop_type = classify_property_type(text)
                if prop_type:
                    enhanced['property_type'] = prop_type
                    logger.debug(f"Classified property type using NLP: {prop_type}")

            # Extract amenities
            amenities = extract_amenities(text)
            if amenities:
                enhanced['amenities'] = amenities
                logger.debug(f"Extracted {len(amenities)} amenities using NLP")

            # Enhance title if generic
            title = enhanced.get('title', '')
            if title and len(title) < 20:
                enhanced_title = enhance_title_with_nlp(
                    title,
                    enhanced.get('description', ''),
                    enhanced.get('location', '')
                )
                if enhanced_title != title:
                    logger.debug(f"Enhanced title: '{title}' → '{enhanced_title}'")
                    enhanced['title_enhanced'] = enhanced_title
                    # Keep original title, add enhanced version

        return enhanced

    except Exception as e:
        logger.error(f"Error in enhance_extraction for {url[:60]}...: {e}")
        return existing_data if existing_data else {}


def validate_and_score(property_dict: Dict, min_quality: int = 40) -> Tuple[bool, Dict]:
    """
    Validate property data and calculate quality score.

    Args:
        property_dict: Property data dictionary
        min_quality: Minimum quality score to pass (0-100)

    Returns:
        Tuple of (is_valid: bool, validation_summary: Dict)
        - is_valid: True if property should be saved
        - validation_summary: Detailed validation results
    """
    try:
        # Get comprehensive validation summary
        summary = get_validation_summary(property_dict)

        # Add quality score to property dict
        property_dict['quality_score'] = summary['quality_score']

        # Determine if should save
        should_save, reason = should_save_property(property_dict, min_quality_score=min_quality)

        # Add validation metadata
        property_dict['validation_passed'] = should_save
        property_dict['validation_reason'] = reason

        if not should_save:
            logger.info(f"Property validation failed: {reason}")
            logger.debug(f"Validation summary: {summary}")

        return should_save, summary

    except Exception as e:
        logger.error(f"Error in validate_and_score: {e}")
        # On error, be conservative: allow property but with low quality score
        return True, {
            'is_valid': True,
            'quality_score': 30,
            'warnings': [f"Validation error: {e}"],
            'reasons': [],
            'recommendations': []
        }


def process_property_with_universal_intelligence(
    url: str,
    html: str,
    existing_data: Optional[Dict] = None,
    min_quality: int = 40
) -> Tuple[bool, Optional[Dict], str]:
    """
    Complete universal intelligence pipeline for a property.

    This is the main integration function that should be called from
    existing scraper code.

    Steps:
    1. Check if category page (skip if yes)
    2. Enhance extraction (fill missing fields)
    3. Validate and score (reject if quality too low)

    Args:
        url: Property page URL
        html: Page HTML content
        existing_data: Optional data already extracted by parsers
        min_quality: Minimum quality score (0-100)

    Returns:
        Tuple of (should_process: bool, enhanced_data: Dict or None, reason: str)
        - should_process: True if property is valid and should be saved
        - enhanced_data: Enhanced property dict, or None if skipped
        - reason: Explanation of decision
    """
    try:
        # Step 1: Check if category page
        should_skip, skip_reason = should_skip_url(url, html, existing_data)
        if should_skip:
            return False, None, f"Skipped: {skip_reason}"

        # Step 2: Enhance extraction
        enhanced_data = enhance_extraction(url, html, existing_data)

        # Ensure required fields
        if 'url' not in enhanced_data:
            enhanced_data['url'] = url

        # Step 3: Validate and score
        is_valid, validation_summary = validate_and_score(enhanced_data, min_quality)

        if not is_valid:
            reason = f"Validation failed: {validation_summary.get('reasons', ['Unknown'])}"
            return False, None, reason

        # Success!
        reason = f"Valid property (quality: {enhanced_data.get('quality_score', 0)}/100)"
        return True, enhanced_data, reason

    except Exception as e:
        logger.error(f"Error in process_property_with_universal_intelligence: {e}")
        # On error, allow property through (conservative)
        return True, existing_data, f"Error in processing: {e}"


# Convenience functions for specific use cases

def is_url_category_page(url: str, html: str) -> bool:
    """Simple check: is this URL a category page?"""
    try:
        is_cat, _ = is_category_page(url, html, {})
        return is_cat
    except:
        return False


def extract_with_universal(url: str, html: str) -> Dict:
    """Extract all fields using universal intelligence."""
    try:
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()
        return extract_all_universal(soup, url, text)
    except Exception as e:
        logger.error(f"Error in extract_with_universal: {e}")
        return {}


def get_property_quality_score(property_dict: Dict) -> int:
    """Get quality score (0-100) for a property."""
    try:
        return calculate_quality_score(property_dict)
    except:
        return 0


# Example usage
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    print("="*60)
    print("UNIVERSAL INTEGRATION TESTING")
    print("="*60)

    # Test HTML - category page
    category_html = """
    <html>
        <body>
            <h1>Properties in Lekki</h1>
            <p>Showing 1-20 of 150 properties</p>
            <div class="property-list">
                <a href="/property/123">3 bedroom apartment</a>
                <a href="/property/124">4 bedroom house</a>
                <a href="/property/125">2 bedroom flat</a>
            </div>
            <div class="pagination">Page 1 of 8</div>
        </body>
    </html>
    """

    print("\n\nTest 1: Category Page Detection")
    should_skip, reason = should_skip_url(
        "https://example.com/property-location/lekki",
        category_html
    )
    print(f"Should Skip: {should_skip}")
    print(f"Reason: {reason}")

    # Test HTML - property page
    property_html = """
    <html>
        <head>
            <title>3 Bedroom Apartment in Lekki - PropertySite</title>
        </head>
        <body>
            <h1>Luxury 3 Bedroom Apartment in Lekki Phase 1</h1>
            <div class="price">₦35,000,000</div>
            <div class="details">
                <span>3 Bedrooms</span>
                <span>2 Bathrooms</span>
                <span>Location: Lekki Phase 1, Victoria Island</span>
            </div>
            <div class="description">
                This beautiful apartment features modern kitchen, swimming pool, and 24hr power.
            </div>
        </body>
    </html>
    """

    print("\n\nTest 2: Property Page Processing")
    should_process, enhanced, reason = process_property_with_universal_intelligence(
        "https://example.com/property-details/12345",
        property_html,
        existing_data={'source': 'example.com'},
        min_quality=40
    )
    print(f"Should Process: {should_process}")
    print(f"Reason: {reason}")
    if enhanced:
        print(f"Title: {enhanced.get('title')}")
        print(f"Price: {enhanced.get('price')}")
        print(f"Location: {enhanced.get('location')}")
        print(f"Quality Score: {enhanced.get('quality_score')}/100")

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
