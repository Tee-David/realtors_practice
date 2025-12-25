"""
Universal Field Extractor

Extracts property data using pattern matching and heuristics instead of CSS selectors.
Works on ANY real estate website without site-specific configuration.

This module uses multiple strategies:
- Regular expression patterns for prices, numbers, etc.
- Domain knowledge (Lagos areas, Nigerian currency)
- Schema.org and meta tag fallbacks
- Built-in validation (reject phone numbers as room counts)

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import re
from typing import Optional, Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Lagos areas and LGAs (domain knowledge - not site-specific)
LAGOS_AREAS = [
    'Victoria Island', 'Ikoyi', 'Lekki', 'Ajah', 'Ikeja', 'Yaba',
    'Surulere', 'Maryland', 'Magodo', 'Gbagada', 'Ikotun', 'Egbeda',
    'Festac', 'Isolo', 'Oshodi', 'Mushin', 'Somolu', 'Kosofe',
    'Alimosho', 'Ajeromi-Ifelodun', 'Amuwo-Odofin', 'Apapa', 'Eti-Osa',
    'Ifako-Ijaiye', 'Ikeja', 'Lagos Island', 'Lagos Mainland',
    'Ojo', 'Shomolu', 'Badagry', 'Epe', 'Ibeju-Lekki', 'Ikorodu',
    'VI', 'Lekki Phase 1', 'Lekki Phase 2', 'Banana Island',
    'Parkview', 'Old Ikoyi', 'Dolphin Estate', 'Osapa London',
    'Chevron', 'Ikate', 'Oniru', 'Sangotedo', 'Awoyaya'
]


def extract_price_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[float]:
    """
    Extract price using pattern matching, not CSS selectors.
    Works on ANY site worldwide (focuses on Nigerian Naira).

    Args:
        soup: BeautifulSoup object of the page
        url: Page URL (for logging)
        text_content: Plain text content of the page

    Returns:
        Price as float (in Naira), or None if not found
    """
    try:
        # Nigerian Naira patterns
        naira_patterns = [
            r'₦\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|m|billion|b|thousand|k))?',
            r'NGN\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|m|billion|b|thousand|k))?',
            r'Naira\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|m|billion|b|thousand|k))?',
            r'Price:\s*₦?\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|m|billion|b|thousand|k))?',
            r'Amount:\s*₦?\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|m|billion|b|thousand|k))?',
            r'\bN?\s*[\d,]+\s*(?:million|m|billion|b)\b'  # Catches "25 million", "N25M"
        ]

        # Try all patterns
        for pattern in naira_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                # Parse the first match
                price_str = matches[0]
                price = _parse_nigerian_price(price_str)
                if price and price > 0:
                    return price

        # Fallback 1: Look for price in meta tags
        price_meta = soup.find('meta', {'property': 'product:price:amount'})
        if price_meta:
            try:
                return float(price_meta.get('content', 0))
            except (ValueError, TypeError):
                pass

        # Fallback 2: Look for price in schema.org markup
        price_schema = soup.find('span', {'itemprop': 'price'})
        if price_schema:
            price_text = price_schema.get_text(strip=True)
            price = _parse_nigerian_price(price_text)
            if price and price > 0:
                return price

        # Fallback 3: Look for og:price meta tag
        og_price = soup.find('meta', {'property': 'og:price:amount'})
        if og_price:
            try:
                return float(og_price.get('content', 0))
            except (ValueError, TypeError):
                pass

        return None

    except Exception as e:
        logger.error(f"Error extracting price from {url[:50]}...: {e}")
        return None


def _parse_nigerian_price(price_str: str) -> Optional[float]:
    """
    Parse Nigerian price string to float.
    Handles: ₦25,000,000 or NGN 25M or N25 million
    """
    try:
        # Remove currency symbols and clean
        price_str = price_str.replace('₦', '').replace('NGN', '').replace('Naira', '')
        price_str = price_str.replace('Price:', '').replace('Amount:', '').strip()

        # Extract number and multiplier
        # Match patterns like "25,000,000" or "25 million" or "25M"
        match = re.search(r'([\d,\.]+)\s*(?:(million|m|billion|b|thousand|k))?', price_str, re.IGNORECASE)

        if not match:
            return None

        number_str = match.group(1).replace(',', '')
        multiplier_str = match.group(2)

        # Parse base number
        base_number = float(number_str)

        # Apply multiplier
        if multiplier_str:
            mult_lower = multiplier_str.lower()
            if mult_lower in ['billion', 'b']:
                base_number *= 1_000_000_000
            elif mult_lower in ['million', 'm']:
                base_number *= 1_000_000
            elif mult_lower in ['thousand', 'k']:
                base_number *= 1_000

        return base_number

    except (ValueError, AttributeError) as e:
        logger.debug(f"Error parsing price '{price_str}': {e}")
        return None


def extract_location_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[str]:
    """
    Extract location using:
    1. Common Lagos areas/LGAs (domain knowledge)
    2. Address patterns
    3. Schema.org markup

    Args:
        soup: BeautifulSoup object of the page
        url: Page URL (for logging)
        text_content: Plain text content of the page

    Returns:
        Location string, or None if not found
    """
    try:
        # Pattern 1: Look for "Location: X" or "Address: X" patterns
        location_patterns = [
            r'Location:\s*([^<\n]+)',
            r'Address:\s*([^<\n]+)',
            r'Area:\s*([^<\n]+)',
            r'(?:Located in|Found in|Situated in)\s+([^<\n]+)',
            r'Property\s+location:\s*([^<\n]+)'
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                # Validate it contains a real Lagos area
                if _contains_lagos_area(location):
                    return location

        # Pattern 2: Find Lagos area names anywhere in text
        # Look for the most specific (longest) match first
        sorted_areas = sorted(LAGOS_AREAS, key=len, reverse=True)
        for area in sorted_areas:
            if area.lower() in text_content.lower():
                # Try to extract surrounding context for better location string
                pattern = rf'(?:in|at|located|,)\s+({re.escape(area)}[^<\n.,]*)'
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
                return area

        # Fallback 1: Schema.org addressLocality
        address = soup.find('span', {'itemprop': 'addressLocality'})
        if address:
            location = address.get_text(strip=True)
            if location:
                return location

        # Fallback 2: Meta tags
        og_locality = soup.find('meta', {'property': 'og:locality'})
        if og_locality:
            location = og_locality.get('content', '').strip()
            if location:
                return location

        return None

    except Exception as e:
        logger.error(f"Error extracting location from {url[:50]}...: {e}")
        return None


def _contains_lagos_area(text: str) -> bool:
    """Check if text contains any Lagos area name."""
    text_lower = text.lower()
    for area in LAGOS_AREAS:
        if area.lower() in text_lower:
            return True
    return False


def extract_bedrooms_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[int]:
    """
    Extract bedrooms using pattern matching.
    VALIDATION: Must be 0-10 (rejects phone numbers!)

    Args:
        soup: BeautifulSoup object
        url: Page URL
        text_content: Plain text content

    Returns:
        Bedroom count (0-10), or None if not found/invalid
    """
    try:
        # Patterns for bedroom counts
        bedroom_patterns = [
            r'(\d+)\s*(?:bedroom|bed|br)s?(?:\s|,|\.|\|)',
            r'Bedroom[s]?:\s*(\d+)',
            r'(\d+)\s*(?:bed|br)\s*(?:apartment|flat|house|duplex|bungalow)',
            r'(\d+)B/?(?:\d+)?(?:\s|,)',  # Like "3B/2B" or "3B"
        ]

        for pattern in bedroom_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                try:
                    count = int(matches[0])
                    # UNIVERSAL VALIDATION: Bedrooms must be 0-10
                    # This rejects phone numbers like 08012345678
                    if 0 <= count <= 10:
                        return count
                    else:
                        logger.debug(f"Rejected bedroom count {count} (out of range 0-10)")
                except (ValueError, TypeError):
                    continue

        # Fallback: Schema.org
        beds_schema = soup.find('span', {'itemprop': 'numberOfBedrooms'})
        if beds_schema:
            try:
                count = int(beds_schema.get_text(strip=True))
                if 0 <= count <= 10:
                    return count
            except (ValueError, TypeError):
                pass

        return None

    except Exception as e:
        logger.error(f"Error extracting bedrooms from {url[:50]}...: {e}")
        return None


def extract_bathrooms_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[int]:
    """
    Extract bathrooms using pattern matching.
    VALIDATION: Must be 0-10 (rejects phone numbers!)

    Args:
        soup: BeautifulSoup object
        url: Page URL
        text_content: Plain text content

    Returns:
        Bathroom count (0-10), or None if not found/invalid
    """
    try:
        # Patterns for bathroom counts
        bathroom_patterns = [
            r'(\d+)\s*(?:bathroom|bath|ba)s?(?:\s|,|\.|\|)',
            r'Bathroom[s]?:\s*(\d+)',
            r'(\d+)\s*(?:bath|ba)\s*(?:apartment|flat|house|duplex|bungalow)',
            r'(?:\d+B/)(\d+)B(?:\s|,)',  # Like "3B/2B" - capture the second number
        ]

        for pattern in bathroom_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                try:
                    count = int(matches[0])
                    # UNIVERSAL VALIDATION: Bathrooms must be 0-10
                    # This rejects phone numbers like 08012345678
                    if 0 <= count <= 10:
                        return count
                    else:
                        logger.debug(f"Rejected bathroom count {count} (out of range 0-10)")
                except (ValueError, TypeError):
                    continue

        # Fallback: Schema.org
        baths_schema = soup.find('span', {'itemprop': 'numberOfBathroomsTotal'})
        if baths_schema:
            try:
                count = int(baths_schema.get_text(strip=True))
                if 0 <= count <= 10:
                    return count
            except (ValueError, TypeError):
                pass

        return None

    except Exception as e:
        logger.error(f"Error extracting bathrooms from {url[:50]}...: {e}")
        return None


def extract_title_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[str]:
    """
    Extract property title using intelligent fallback cascade.

    Args:
        soup: BeautifulSoup object
        url: Page URL
        text_content: Plain text content

    Returns:
        Property title, or None if not found
    """
    try:
        # 1. Schema.org name
        title = soup.find('h1', {'itemprop': 'name'})
        if title:
            title_text = title.get_text(strip=True)
            if len(title_text) > 10:
                return title_text

        # 2. og:title meta tag
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            title_text = og_title.get('content', '').strip()
            # Remove site name suffix (e.g., "Property - SiteName")
            title_text = re.sub(r'\s*[-|]\s*[\w\s]+$', '', title_text)
            if len(title_text) > 10:
                return title_text

        # 3. First H1 on page
        h1 = soup.find('h1')
        if h1:
            title_text = h1.get_text(strip=True)
            if len(title_text) > 10:
                return title_text

        # 4. Page title tag
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Remove site name
            title_text = re.sub(r'\s*[-|]\s*[\w\s]+$', '', title_text)
            if len(title_text) > 10:
                return title_text

        # 5. Twitter card title
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title:
            title_text = twitter_title.get('content', '').strip()
            if len(title_text) > 10:
                return title_text

        return None

    except Exception as e:
        logger.error(f"Error extracting title from {url[:50]}...: {e}")
        return None


def extract_description_universal(soup: BeautifulSoup, url: str, text_content: str) -> Optional[str]:
    """
    Extract property description.

    Args:
        soup: BeautifulSoup object
        url: Page URL
        text_content: Plain text content

    Returns:
        Property description, or None if not found
    """
    try:
        # 1. Schema.org description
        desc = soup.find('div', {'itemprop': 'description'})
        if desc:
            desc_text = desc.get_text(strip=True)
            if len(desc_text) > 50:
                return desc_text

        # 2. og:description meta tag
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            desc_text = og_desc.get('content', '').strip()
            if len(desc_text) > 50:
                return desc_text

        # 3. meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            desc_text = meta_desc.get('content', '').strip()
            if len(desc_text) > 50:
                return desc_text

        # 4. Look for divs/sections with common description class names
        desc_selectors = [
            'div.description',
            'div.property-description',
            'section.description',
            'div.details',
            'div.about'
        ]

        for selector in desc_selectors:
            desc = soup.select_one(selector)
            if desc:
                desc_text = desc.get_text(strip=True)
                if len(desc_text) > 50:
                    return desc_text

        return None

    except Exception as e:
        logger.error(f"Error extracting description from {url[:50]}...: {e}")
        return None


def extract_all_universal(soup: BeautifulSoup, url: str, text_content: str) -> Dict:
    """
    Extract all fields using universal extraction.

    Args:
        soup: BeautifulSoup object
        url: Page URL
        text_content: Plain text content

    Returns:
        Dictionary with all extracted fields
    """
    return {
        'title': extract_title_universal(soup, url, text_content),
        'price': extract_price_universal(soup, url, text_content),
        'location': extract_location_universal(soup, url, text_content),
        'bedrooms': extract_bedrooms_universal(soup, url, text_content),
        'bathrooms': extract_bathrooms_universal(soup, url, text_content),
        'description': extract_description_universal(soup, url, text_content)
    }


# Example usage and testing
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    # Test HTML content
    test_html = """
    <html>
        <head>
            <title>Luxury 3 Bedroom Apartment in Lekki - PropertySite</title>
            <meta property="og:title" content="Luxury 3 Bedroom Apartment in Lekki Phase 1">
        </head>
        <body>
            <h1>Luxury 3 Bedroom Apartment in Lekki Phase 1, Victoria Island</h1>
            <div class="price">₦35,000,000</div>
            <div class="property-details">
                <span>3 Bedrooms</span>
                <span>2 Bathrooms</span>
                <span>Location: Lekki Phase 1, Lagos</span>
            </div>
            <div class="description">
                This beautiful 3 bedroom apartment is located in the heart of Lekki Phase 1.
                Features include modern kitchen, spacious living room, and secure parking.
            </div>
        </body>
    </html>
    """

    soup = BeautifulSoup(test_html, 'html.parser')
    text = soup.get_text()
    url = "https://example.com/property/12345"

    print("Testing Universal Extractor:\n")
    print(f"Title: {extract_title_universal(soup, url, text)}")
    print(f"Price: {extract_price_universal(soup, url, text)}")
    print(f"Location: {extract_location_universal(soup, url, text)}")
    print(f"Bedrooms: {extract_bedrooms_universal(soup, url, text)}")
    print(f"Bathrooms: {extract_bathrooms_universal(soup, url, text)}")
    print(f"Description: {extract_description_universal(soup, url, text)[:100]}...")

    print("\n\nTesting All Fields Extraction:")
    all_fields = extract_all_universal(soup, url, text)
    for key, value in all_fields.items():
        print(f"{key}: {value}")
