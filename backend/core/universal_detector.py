"""
Universal Category Page Detector

Detects if a scraped page is a category/listing page vs an actual property page.
Works on ANY real estate website without site-specific configuration.

This module uses multiple signals to make intelligent decisions:
- URL pattern analysis
- Content analysis (text patterns)
- Link density
- Pagination indicators
- Data quality signals
- Schema.org markup

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import re
from typing import Dict, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def is_category_page(url: str, html_content: str, extracted_data: Dict) -> Tuple[bool, Dict[str, int]]:
    """
    Detect if a page is a category/listing page vs actual property page.
    Works on ANY real estate site without site-specific rules.

    Args:
        url: The page URL
        html_content: Raw HTML content of the page
        extracted_data: Dictionary of data already extracted (title, price, etc.)

    Returns:
        Tuple of (is_category: bool, signals: Dict[str, int])
        - is_category: True if category page, False if property page
        - signals: Dictionary showing category_signals and property_signals scores
    """
    signals = {
        'category_signals': 0,
        'property_signals': 0
    }

    try:
        # Signal 1: URL Pattern Analysis
        _analyze_url_patterns(url, signals)

        # Signal 2: Content Analysis (text patterns)
        _analyze_content_patterns(html_content, signals)

        # Signal 3: Link Density
        _analyze_link_density(html_content, signals)

        # Signal 4: Pagination Elements
        _analyze_pagination(html_content, signals)

        # Signal 5: Extracted Data Quality
        _analyze_data_quality(extracted_data, signals)

        # Signal 6: Schema.org Markup
        _analyze_schema_markup(html_content, signals)

        # Decision: Category if category signals > property signals
        is_category = signals['category_signals'] > signals['property_signals']

        logger.debug(
            f"Category detection for {url[:50]}...: "
            f"Category={signals['category_signals']}, "
            f"Property={signals['property_signals']}, "
            f"Result={'CATEGORY' if is_category else 'PROPERTY'}"
        )

        return is_category, signals

    except Exception as e:
        logger.error(f"Error in category detection: {e}")
        # On error, default to assuming it's a property page (conservative)
        return False, signals


def _analyze_url_patterns(url: str, signals: Dict[str, int]) -> None:
    """
    Analyze URL for category vs property patterns.
    Category pages often have: /listings/, /search/, /location/
    Property pages often have: /property/, /detail/, /id/
    """
    url_lower = url.lower()

    # Category URL patterns
    category_url_patterns = [
        '/property-location/', '/listings/', '/search/', '/properties/',
        '/category/', '/location/', '/area/', '/city/', '/state/',
        '/for-sale/', '/for-rent/', '/property-type/', '/browse/',
        '/filter/', '/results/', '/find/'
    ]

    # Property URL patterns
    property_url_patterns = [
        '/property-details/', '/listing/', '/property/', '/detail/',
        '/view/', '/show/', '/id/', '/ref/', '/p/', '/pid/',
        '/property-id/', '/listing-id/'
    ]

    # Check for category patterns
    for pattern in category_url_patterns:
        if pattern in url_lower:
            signals['category_signals'] += 2
            break  # Only count once

    # Check for property patterns
    for pattern in property_url_patterns:
        if pattern in url_lower:
            signals['property_signals'] += 2
            break  # Only count once

    # Additional heuristic: URLs with /property/ followed by a number are likely property pages
    if re.search(r'/property/\d+', url_lower) or re.search(r'/id/\d+', url_lower):
        signals['property_signals'] += 3


def _analyze_content_patterns(html_content: str, signals: Dict[str, int]) -> None:
    """
    Analyze page content for category vs property indicators.
    Category pages mention "X Properties", "X Listings", "X Results"
    """
    # Patterns that indicate category pages
    property_count_patterns = [
        r'\d+\s+(?:properties|listings|results|homes|apartments|houses)',
        r'(?:showing|found|available):\s*\d+',
        r'\d+\s+properties?\s+(?:found|available|for\s+(?:sale|rent))',
        r'Showing\s+\d+\s*-\s*\d+\s+of\s+\d+',
        r'\d+\s+search\s+results?'
    ]

    for pattern in property_count_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            signals['category_signals'] += 3
            break  # Only count once

    # Patterns that indicate property pages
    property_detail_patterns = [
        r'Property\s+(?:Description|Details|Features|Information)',
        r'About\s+this\s+property',
        r'Property\s+ID:\s*\w+',
        r'Listed\s+(?:on|by)',
        r'Contact\s+(?:Agent|Owner|Seller)'
    ]

    for pattern in property_detail_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            signals['property_signals'] += 2
            break  # Only count once


def _analyze_link_density(html_content: str, signals: Dict[str, int]) -> None:
    """
    Analyze density of property links.
    Category pages have MANY property links (10+)
    Property pages have few property links (<5)
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Count links that look like property links
        property_link_patterns = [
            r'/property/', r'/listing/', r'/detail/', r'/view/',
            r'/for-sale/', r'/for-rent/', r'/apartment/', r'/house/',
            r'/p/', r'/id/'
        ]

        property_links = 0
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for pattern in property_link_patterns:
                if pattern in href:
                    property_links += 1
                    break  # Count each link only once

        # High link density = category page
        if property_links > 10:
            signals['category_signals'] += 5
        elif property_links > 5:
            signals['category_signals'] += 2
        # Low link density = property page
        elif property_links < 5:
            signals['property_signals'] += 3
        elif property_links < 2:
            signals['property_signals'] += 5

    except Exception as e:
        logger.debug(f"Error analyzing link density: {e}")


def _analyze_pagination(html_content: str, signals: Dict[str, int]) -> None:
    """
    Detect pagination elements (indicate category pages).
    Category pages have: "Next", "Page 2", "Showing 1-20 of 100"
    """
    pagination_patterns = [
        r'(?:page\s+\d+|next\s+page|previous\s+page)',
        r'(?:showing\s+\d+\s*-\s*\d+\s+of\s+\d+)',
        r'pagination',
        r'(?:next|prev)\s*(?:&raquo;|&laquo;|›|‹)',
        r'page\s+\d+\s+of\s+\d+'
    ]

    for pattern in pagination_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            signals['category_signals'] += 2
            break  # Only count once


def _analyze_data_quality(extracted_data: Dict, signals: Dict[str, int]) -> None:
    """
    Analyze quality of extracted data.
    Property pages have DETAILED data (long title, price, amenities)
    Category pages have minimal/no data
    """
    title = extracted_data.get('title', '')
    price = extracted_data.get('price', 0)
    description = extracted_data.get('description', '')
    bedrooms = extracted_data.get('bedrooms')

    # Long detailed title suggests property page
    if len(title) > 50:
        signals['property_signals'] += 3
    elif len(title) > 30:
        signals['property_signals'] += 1
    # Short generic title suggests category page
    elif len(title) < 20 and title:
        signals['category_signals'] += 2

    # Has price = likely property page
    if price and price > 1_000_000:
        signals['property_signals'] += 2
    elif price and price > 0:
        signals['property_signals'] += 1

    # Has description = likely property page
    if len(description) > 100:
        signals['property_signals'] += 2

    # Has bedroom count = likely property page
    if bedrooms is not None:
        signals['property_signals'] += 1


def _analyze_schema_markup(html_content: str, signals: Dict[str, int]) -> None:
    """
    Analyze Schema.org structured data markup.
    Property pages often have RealEstate, Offer, Product schemas
    """
    schema_patterns = [
        r'itemtype="http://schema\.org/RealEstateAgent"',
        r'itemtype="http://schema\.org/Offer"',
        r'itemtype="http://schema\.org/Product"',
        r'itemtype="http://schema\.org/Apartment"',
        r'itemtype="http://schema\.org/House"',
        r'@type":\s*"(?:RealEstateListing|Apartment|House|Product)"'
    ]

    for pattern in schema_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            signals['property_signals'] += 3
            break  # Only count once


def get_detection_confidence(signals: Dict[str, int]) -> str:
    """
    Get confidence level of the detection.

    Args:
        signals: Dictionary with category_signals and property_signals

    Returns:
        Confidence level: 'high', 'medium', 'low'
    """
    total = signals['category_signals'] + signals['property_signals']

    if total == 0:
        return 'low'

    diff = abs(signals['category_signals'] - signals['property_signals'])
    confidence_ratio = diff / total

    if confidence_ratio >= 0.5:
        return 'high'
    elif confidence_ratio >= 0.25:
        return 'medium'
    else:
        return 'low'


# Example usage and testing
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    # Test with a category page URL
    test_url_category = "https://example.com/property-location/lekki/for-sale"
    test_html_category = """
    <html>
        <body>
            <h1>Properties in Lekki</h1>
            <p>Showing 1-20 of 150 properties for sale</p>
            <div class="property-list">
                <a href="/property/123">3 bedroom apartment</a>
                <a href="/property/124">4 bedroom house</a>
                <a href="/property/125">2 bedroom flat</a>
                <!-- ... more links ... -->
            </div>
            <div class="pagination">Page 1 of 8</div>
        </body>
    </html>
    """
    test_data_category = {'title': 'Lekki', 'price': 0}

    is_cat, sigs = is_category_page(test_url_category, test_html_category, test_data_category)
    print(f"\nCategory Page Test:")
    print(f"Result: {'CATEGORY' if is_cat else 'PROPERTY'}")
    print(f"Signals: {sigs}")
    print(f"Confidence: {get_detection_confidence(sigs)}")

    # Test with a property page URL
    test_url_property = "https://example.com/property-details/12345"
    test_html_property = """
    <html itemtype="http://schema.org/Apartment">
        <body>
            <h1>Luxury 3 Bedroom Apartment in Lekki Phase 1, Victoria Island</h1>
            <p class="price">₦35,000,000</p>
            <div class="property-description">
                This beautiful 3 bedroom apartment is located in the heart of Lekki...
                (300+ words description)
            </div>
            <div class="property-details">
                <span>3 Bedrooms</span>
                <span>2 Bathrooms</span>
                <span>Property ID: ABC12345</span>
            </div>
            <div class="contact">Contact Agent</div>
        </body>
    </html>
    """
    test_data_property = {
        'title': 'Luxury 3 Bedroom Apartment in Lekki Phase 1, Victoria Island',
        'price': 35000000,
        'bedrooms': 3,
        'description': 'This beautiful 3 bedroom apartment...' * 10
    }

    is_cat2, sigs2 = is_category_page(test_url_property, test_html_property, test_data_property)
    print(f"\nProperty Page Test:")
    print(f"Result: {'CATEGORY' if is_cat2 else 'PROPERTY'}")
    print(f"Signals: {sigs2}")
    print(f"Confidence: {get_detection_confidence(sigs2)}")
