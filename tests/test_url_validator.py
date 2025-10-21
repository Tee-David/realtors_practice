#!/usr/bin/env python3
"""
Test URL Validator Module

Tests the URL validation functionality to ensure:
- Valid HTTP/HTTPS URLs are accepted
- WhatsApp, mailto, tel, and other invalid schemes are rejected
- Malformed URLs are rejected
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.url_validator import (
    is_valid_property_url,
    filter_valid_urls,
    filter_listings_by_url,
    is_whatsapp_url,
    get_url_scheme
)


def test_valid_urls():
    """Test that valid HTTP/HTTPS URLs are accepted"""
    print("\n=== Testing Valid URLs ===")

    valid_urls = [
        "https://propertypro.ng/property/123",
        "http://www.example.com/listing",
        "https://npc.gov.ng/properties",
        "http://jiji.ng/cars/toyota"
    ]

    for url in valid_urls:
        result = is_valid_property_url(url)
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {url} -> {result}")

    print()


def test_invalid_urls():
    """Test that invalid URLs are rejected"""
    print("=== Testing Invalid URLs ===")

    invalid_urls = [
        "whatsapp://send?phone=+234",
        "mailto:agent@example.com",
        "tel:+2341234567890",
        "javascript:alert('xss')",
        "ftp://files.example.com/file.zip",
        "#anchor-link",
        "",
        None,
        "not-a-url",
        "https://",  # No domain
    ]

    for url in invalid_urls:
        result = is_valid_property_url(url)
        status = "[PASS]" if not result else "[FAIL]"
        print(f"{status}: {url} -> {result}")

    print()


def test_whatsapp_detection():
    """Test WhatsApp URL detection"""
    print("=== Testing WhatsApp Detection ===")

    whatsapp_urls = [
        "whatsapp://send?phone=+234",
        "https://wa.me/234",
        "https://api.whatsapp.com/send?phone=234",
        "https://web.whatsapp.com/send?phone=234",
    ]

    for url in whatsapp_urls:
        result = is_whatsapp_url(url)
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {url} -> {result}")

    print()


def test_filter_valid_urls():
    """Test filtering a list of URLs"""
    print("=== Testing URL List Filtering ===")

    test_urls = [
        "https://propertypro.ng/property/1",
        "whatsapp://send?phone=+234",
        "https://npc.gov.ng/property/2",
        "mailto:agent@example.com",
        "https://jiji.ng/property/3",
        "tel:+234",
    ]

    valid, filtered = filter_valid_urls(test_urls, log_filtered=True)

    print(f"Input URLs: {len(test_urls)}")
    print(f"Valid URLs: {len(valid)}")
    print(f"Filtered URLs: {len(filtered)}")
    print()
    print("Valid:")
    for url in valid:
        print(f"  [+] {url}")
    print()
    print("Filtered:")
    for url in filtered:
        print(f"  [-] {url}")
    print()


def test_filter_listings():
    """Test filtering listings by URL"""
    print("=== Testing Listings Filtering ===")

    listings = [
        {"title": "House 1", "listing_url": "https://example.com/house1"},
        {"title": "House 2", "listing_url": "whatsapp://send?phone=+234"},
        {"title": "House 3", "listing_url": "https://example.com/house3"},
        {"title": "House 4", "listing_url": "mailto:agent@example.com"},
        {"title": "House 5", "listing_url": "https://example.com/house5"},
    ]

    filtered_listings, num_filtered = filter_listings_by_url(listings)

    print(f"Input listings: {len(listings)}")
    print(f"Valid listings: {len(filtered_listings)}")
    print(f"Filtered listings: {num_filtered}")
    print()
    print("Valid listings:")
    for listing in filtered_listings:
        print(f"  [+] {listing['title']}: {listing['listing_url']}")
    print()


def test_scheme_extraction():
    """Test URL scheme extraction"""
    print("=== Testing Scheme Extraction ===")

    test_cases = [
        ("https://example.com", "https"),
        ("http://example.com", "http"),
        ("whatsapp://send", "whatsapp"),
        ("mailto:test@example.com", "mailto"),
        ("ftp://files.com", "ftp"),
        ("invalid-url", ""),
    ]

    for url, expected in test_cases:
        result = get_url_scheme(url)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status}: {url} -> '{result}' (expected '{expected}')")

    print()


def main():
    print("\n" + "="*60)
    print("URL VALIDATOR TESTS")
    print("="*60)

    test_valid_urls()
    test_invalid_urls()
    test_whatsapp_detection()
    test_filter_valid_urls()
    test_filter_listings()
    test_scheme_extraction()

    print("="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
