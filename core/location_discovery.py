# core/location_discovery.py
"""
Location Discovery Module

Handles multi-level navigation for sites that organize property listings by location.

This module adds a "Layer 0.5" between the initial URL and property list scraping:
  1. Detect if starting page is a location directory
  2. Extract location category links (e.g., Ajah, Lekki, Ikoyi)
  3. Visit each location page
  4. Hand off to list page scraper for property extraction

Flow:
  Input: /property-for-sale/in/lagos (location directory)
    ↓
  Discover: [/lagos/ajah, /lagos/lekki, /lagos/ikoyi, ...]
    ↓
  For each location: Extract property listings
    ↓
  Output: Actual property listings with details
"""

import os
import re
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from core.scraper_engine import fetch_adaptive

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"


def is_location_directory(soup, url: str, config: Dict) -> bool:
    """
    Detect if the current page is a location directory (not a property listing page).

    A location directory page typically:
    - Shows links to different areas/neighborhoods
    - Has minimal property listings
    - URL ends with just /lagos or /for-sale/lagos

    Args:
        soup: BeautifulSoup object of the page
        url: Current page URL
        config: Location discovery configuration

    Returns:
        True if this is a location directory, False otherwise
    """
    # Strategy 1: Check URL patterns
    # Location directories typically have short URLs like /lagos, /for-sale/lagos
    url_lower = url.lower()

    # If URL is just a city name or broad category, likely a directory
    directory_patterns = [
        r'/(?:property-)?for-(?:sale|rent)/(?:in/)?lagos/?$',
        r'/lagos/?$',
        r'/property/lagos/?$',
    ]

    for pattern in directory_patterns:
        if re.search(pattern, url_lower):
            if RP_DEBUG:
                logger.debug(f"Location directory detected (URL pattern): {url}")
            return True

    # Strategy 2: Check page content
    # Location directories have many location links, few property-specific elements

    # Get configured location link selectors
    location_selectors = config.get("location_link_selectors", [])
    if location_selectors:
        # Count location-like links
        location_link_count = 0
        for selector in location_selectors:
            try:
                links = soup.select(selector)
                location_link_count += len(links)
            except Exception:
                continue

        # If we found many location links (>5), likely a directory
        if location_link_count > 5:
            if RP_DEBUG:
                logger.debug(f"Location directory detected ({location_link_count} location links found)")
            return True

    # Strategy 3: Check for property-specific elements
    # If page has property cards with prices/bedrooms, it's NOT a directory
    property_indicators = soup.select('.price, .bedrooms, .bathrooms, [class*="bedroom"], [class*="price"]')
    if len(property_indicators) > 3:
        # Has multiple property elements, likely a property listing page
        if RP_DEBUG:
            logger.debug(f"Property listing page detected ({len(property_indicators)} property indicators)")
        return False

    # Default: assume directory if uncertain
    return True


def extract_location_links(soup, url: str, config: Dict) -> List[str]:
    """
    Extract location category links from a directory page.

    Args:
        soup: BeautifulSoup object of the directory page
        url: Base URL for resolving relative links
        config: Location discovery configuration

    Returns:
        List of location URLs to scrape
    """
    location_urls = []
    seen_urls = set()

    # Get configured selectors
    location_selectors = config.get("location_link_selectors", [])

    if not location_selectors:
        # Default selectors for common patterns
        location_selectors = [
            "a[href*='/lagos/']",
            ".location-list a",
            ".area-list a",
            "a[href*='/for-sale/']",
            "a[href*='/for-rent/']",
        ]

    # Extract links using configured selectors
    for selector in location_selectors:
        try:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if not href:
                    continue

                # Resolve to absolute URL
                absolute_url = urljoin(url, href)

                # Skip if already seen
                if absolute_url in seen_urls:
                    continue

                # Apply filters
                if _should_skip_location(absolute_url, config):
                    if RP_DEBUG:
                        logger.debug(f"Skipping location (filtered): {absolute_url}")
                    continue

                location_urls.append(absolute_url)
                seen_urls.add(absolute_url)

        except Exception as e:
            logger.warning(f"Failed to extract links with selector '{selector}': {e}")
            continue

    # Apply max_locations limit
    max_locations = config.get("max_locations", 20)
    if len(location_urls) > max_locations:
        logger.info(f"Limiting locations from {len(location_urls)} to {max_locations}")
        location_urls = location_urls[:max_locations]

    if RP_DEBUG:
        logger.debug(f"Extracted {len(location_urls)} location URLs")
        for loc_url in location_urls[:5]:
            logger.debug(f"  - {loc_url}")

    return location_urls


def _should_skip_location(url: str, config: Dict) -> bool:
    """
    Check if a location URL should be skipped based on configured filters.

    Args:
        url: Location URL to check
        config: Location discovery configuration

    Returns:
        True if should skip, False otherwise
    """
    skip_patterns = config.get("skip_locations", [])

    # Default skip patterns
    default_skips = [
        r'/lagos/?$',  # Skip broad /lagos link
        r'/nigeria/?$',  # Skip country-wide links
        r'/property/?$',  # Skip generic property links
    ]

    all_patterns = skip_patterns + default_skips

    for pattern in all_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    return False


def discover_locations(
    start_url: str,
    site_config: Dict,
    fallback_order: List[str],
    site_key: str,
) -> List[str]:
    """
    Main orchestrator: Discover all location pages from a directory.

    This function:
    1. Fetches the starting URL
    2. Detects if it's a location directory
    3. Extracts location links
    4. Returns list of location URLs to scrape

    Args:
        start_url: Starting URL (potentially a location directory)
        site_config: Full site configuration from config.yaml
        fallback_order: Fetch method fallback order
        site_key: Site identifier for logging

    Returns:
        List of location URLs to scrape for properties
        If not a directory, returns [start_url] (original behavior)
    """
    location_config = site_config.get("location_discovery", {})

    if not location_config.get("enabled", False):
        # Location discovery disabled, return original URL
        return [start_url]

    logger.info(f"{site_key}: Location discovery enabled, checking {start_url}")

    try:
        # Fetch the starting page
        html, method, _ = fetch_adaptive(
            url=start_url,
            wait_selector="body",
            fallback_order=fallback_order,
            site_key=site_key,
            page_idx=0
        )

        if not html:
            logger.warning(f"{site_key}: Failed to fetch directory page, using original URL")
            return [start_url]

        soup = BeautifulSoup(html, "lxml")

        # Check if this is a location directory
        if is_location_directory(soup, start_url, location_config):
            logger.info(f"{site_key}: Location directory detected, extracting location links...")

            # Extract location links
            location_urls = extract_location_links(soup, start_url, location_config)

            if location_urls:
                logger.info(f"{site_key}: Discovered {len(location_urls)} locations to scrape")
                return location_urls
            else:
                logger.warning(f"{site_key}: No location links found, using original URL")
                return [start_url]
        else:
            logger.info(f"{site_key}: Not a location directory, treating as property listing page")
            return [start_url]

    except Exception as e:
        logger.error(f"{site_key}: Location discovery failed: {e}")
        logger.info(f"{site_key}: Falling back to original URL")
        return [start_url]
