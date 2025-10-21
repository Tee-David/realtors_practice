"""
core/url_validator.py

URL validation module to filter out invalid property URLs.
Filters out:
- WhatsApp links (whatsapp://)
- Email links (mailto:)
- Phone links (tel:)
- Invalid/malformed URLs
- Non-HTTP(S) schemes

Usage:
    from core.url_validator import is_valid_property_url, filter_valid_urls

    if is_valid_property_url(url):
        # Process URL
        pass

    valid_urls = filter_valid_urls(url_list)
"""

import re
import os
import logging
from urllib.parse import urlparse
from typing import List, Tuple

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"

# Invalid URL schemes that should be filtered out
INVALID_SCHEMES = {
    'whatsapp',
    'mailto',
    'tel',
    'sms',
    'skype',
    'viber',
    'telegram',
    'javascript',
    'data',
    'file',
    'ftp',
}

# Valid schemes for property URLs
VALID_SCHEMES = {'http', 'https'}


def is_valid_property_url(url: str) -> bool:
    """
    Check if a URL is valid for property scraping.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid for property scraping, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # Empty or whitespace-only URLs
    if not url:
        return False

    # Check for obvious invalid patterns
    if url.startswith('#') or url.startswith('javascript:'):
        return False

    try:
        parsed = urlparse(url)

        # Must have a scheme
        if not parsed.scheme:
            return False

        # Scheme must be http or https
        if parsed.scheme.lower() not in VALID_SCHEMES:
            if RP_DEBUG:
                logger.debug(f"Invalid scheme '{parsed.scheme}' in URL: {url}")
            return False

        # Must have a netloc (domain)
        if not parsed.netloc:
            return False

        # Check for localhost/private IPs in production (optional)
        # Uncomment if you want to block these:
        # if parsed.netloc.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
        #     return False

        return True

    except Exception as e:
        if RP_DEBUG:
            logger.debug(f"URL parsing error for '{url}': {e}")
        return False


def filter_valid_urls(urls: List[str], log_filtered: bool = False) -> Tuple[List[str], List[str]]:
    """
    Filter a list of URLs to only include valid property URLs.

    Args:
        urls: List of URL strings to filter
        log_filtered: If True, log filtered URLs for debugging

    Returns:
        Tuple of (valid_urls, filtered_urls)
    """
    valid = []
    filtered = []

    for url in urls:
        if is_valid_property_url(url):
            valid.append(url)
        else:
            filtered.append(url)
            if log_filtered and RP_DEBUG:
                logger.debug(f"Filtered invalid URL: {url}")

    return valid, filtered


def filter_listings_by_url(listings: List[dict], url_key: str = 'listing_url') -> Tuple[List[dict], int]:
    """
    Filter a list of listing dictionaries by URL validity.

    Args:
        listings: List of listing dictionaries
        url_key: Key name for URL field in listing dict

    Returns:
        Tuple of (filtered_listings, num_filtered)
    """
    valid_listings = []
    filtered_count = 0
    filtered_urls = []

    for listing in listings:
        url = listing.get(url_key, '')
        if is_valid_property_url(url):
            valid_listings.append(listing)
        else:
            filtered_count += 1
            filtered_urls.append(url)

    # Log summary of filtered URLs
    if filtered_count > 0:
        logger.info(f"Filtered {filtered_count} invalid URLs from listings")

        # Group filtered URLs by scheme for debugging
        if RP_DEBUG:
            schemes = {}
            for url in filtered_urls:
                try:
                    scheme = urlparse(url).scheme or 'no-scheme'
                    schemes[scheme] = schemes.get(scheme, 0) + 1
                except:
                    schemes['malformed'] = schemes.get('malformed', 0) + 1

            logger.debug(f"Filtered URL breakdown: {schemes}")
            # Log a few examples
            for url in filtered_urls[:3]:
                logger.debug(f"  Example filtered URL: {url}")

    return valid_listings, filtered_count


def get_url_scheme(url: str) -> str:
    """
    Extract the scheme from a URL.

    Args:
        url: URL string

    Returns:
        Scheme (lowercase) or empty string if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() if parsed.scheme else ''
    except:
        return ''


def is_whatsapp_url(url: str) -> bool:
    """
    Check if URL is a WhatsApp link.

    Args:
        url: URL string

    Returns:
        True if URL is a WhatsApp link
    """
    if not url:
        return False

    url_lower = url.lower().strip()

    # Direct WhatsApp scheme
    if url_lower.startswith('whatsapp:'):
        return True

    # WhatsApp web/API URLs
    whatsapp_patterns = [
        'wa.me/',
        'api.whatsapp.com/',
        'web.whatsapp.com/',
        'chat.whatsapp.com/',
    ]

    for pattern in whatsapp_patterns:
        if pattern in url_lower:
            return True

    return False
