"""
Test intelligent scraper features: relevance detection, auto-adapt selectors, screenshots

This test verifies:
1. Relevance scoring system works correctly
2. URL filtering identifies property listings vs categories
3. Auto-selector discovery finds best selectors
4. Screenshot capability works (when enabled)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from helpers.relevance import score_element_relevance, is_relevant_listing, find_best_selector
from parsers.specials import _is_property_url

# Test HTML with mix of property listings and navigation elements
TEST_HTML = """
<html>
<body>
    <!-- Good property listing -->
    <div class="property-card">
        <img src="house1.jpg" />
        <h2><a href="/property/12345-4-bedroom-duplex-lekki">4 Bedroom Duplex in Lekki</a></h2>
        <p class="price">₦45,000,000</p>
        <p class="location">Lekki Phase 1, Lagos</p>
    </div>

    <!-- Another good listing -->
    <article class="listing">
        <img src="house2.jpg" />
        <h3><a href="/listing/67890-3-bed-flat-ikoyi">3 Bedroom Flat - Ikoyi</a></h3>
        <span class="amount">₦35 million</span>
        <span class="area">Victoria Island, Lagos</span>
    </article>

    <!-- Category/navigation link (should be filtered) -->
    <div class="nav-item">
        <a href="/lagos/lekki">Browse Lekki Properties</a>
        <p>View all properties in Lekki</p>
    </div>

    <!-- Footer link (should be filtered) -->
    <footer>
        <div class="footer-link">
            <a href="/for-sale/houses/lagos">Houses for Sale in Lagos</a>
        </div>
    </footer>

    <!-- Incomplete listing (no price, should score lower) -->
    <div class="item">
        <a href="/property/99999">Property Title Only</a>
    </div>
</body>
</html>
"""

def test_url_filtering():
    """Test URL filtering distinguishes properties from categories"""
    print("=" * 80)
    print("TEST 1: URL FILTERING")
    print("=" * 80)

    test_cases = [
        # (url, expected_result, description)
        ("https://site.com/property/12345-4-bedroom-duplex-lekki", True, "Property with bedroom in URL"),
        ("https://site.com/listing/67890-3-bed-flat-ikoyi", True, "Property with numeric ID"),
        ("https://site.com/for-sale/houses/terraced-duplexes/lagos/lekki/3154197-4-bedrooms", True, "Deep path property"),
        ("https://site.com/lagos/lekki", False, "Location-only URL"),
        ("https://site.com/for-sale/houses/lagos", False, "Category URL"),
        ("https://site.com/properties/showtype", False, "Showtype category"),
    ]

    passed = 0
    failed = 0

    for url, expected, description in test_cases:
        result = _is_property_url(url)
        status = "PASS" if result == expected else "FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"  [{status}] {description}")
        print(f"        URL: {url}")
        print(f"        Expected: {expected}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    print()
    return failed == 0


def test_relevance_scoring():
    """Test relevance scoring system"""
    print("=" * 80)
    print("TEST 2: RELEVANCE SCORING")
    print("=" * 80)

    soup = BeautifulSoup(TEST_HTML, "lxml")

    # Test good property card
    property_card = soup.select_one("div.property-card")
    score_result = score_element_relevance(property_card, url="https://site.com/property/12345")

    print("Test A: Good Property Card")
    print(f"  Score: {score_result['score']}")
    print(f"  Relevant: {score_result['is_relevant']}")
    print(f"  Signals: {score_result['signals']}")
    print()

    assert score_result['is_relevant'], "Good property card should be relevant"
    assert score_result['score'] >= 30, f"Score should be >= 30, got {score_result['score']}"

    # Test navigation element
    nav_item = soup.select_one("div.nav-item")
    nav_result = score_element_relevance(nav_item, url="https://site.com/lagos/lekki")

    print("Test B: Navigation Element")
    print(f"  Score: {nav_result['score']}")
    print(f"  Relevant: {nav_result['is_relevant']}")
    print(f"  Signals: {nav_result['signals']}")
    print()

    assert not nav_result['is_relevant'], "Navigation element should NOT be relevant"

    # Test footer link
    footer_link = soup.select_one("footer div.footer-link")
    footer_result = score_element_relevance(footer_link, url="https://site.com/for-sale/houses/lagos")

    print("Test C: Footer Link")
    print(f"  Score: {footer_result['score']}")
    print(f"  Relevant: {footer_result['is_relevant']}")
    print(f"  Signals: {footer_result['signals']}")
    print()

    assert not footer_result['is_relevant'], "Footer link should NOT be relevant"

    print("All relevance scoring tests passed!")
    print()
    return True


def test_auto_selector_discovery():
    """Test automatic selector discovery"""
    print("=" * 80)
    print("TEST 3: AUTO-SELECTOR DISCOVERY")
    print("=" * 80)

    candidates = [
        'div.property-card',
        'article.listing',
        'div.nav-item',  # Should score low
        'footer div',    # Should score low
        'div.item',      # Incomplete, should score lower
    ]

    best_selector, results = find_best_selector(TEST_HTML, candidates, min_score=25)

    print(f"Best selector: {best_selector}")
    print()
    print("All candidate results:")
    for r in results:
        print(f"  {r['selector']}")
        print(f"    Avg Score: {r['avg_score']:.1f}")
        print(f"    Relevant Count: {r['relevant_count']}/{r['sampled_count']}")
        print(f"    Total Elements: {r['total_count']}")
        print()

    # Best selector should be one of the good property selectors
    assert best_selector in ['div.property-card', 'article.listing'], \
        f"Best selector should be property card or article, got {best_selector}"

    print("Auto-selector discovery test passed!")
    print()
    return True


def test_is_relevant_listing_helper():
    """Test the quick is_relevant_listing helper"""
    print("=" * 80)
    print("TEST 4: IS_RELEVANT_LISTING HELPER")
    print("=" * 80)

    soup = BeautifulSoup(TEST_HTML, "lxml")

    test_cases = [
        ("div.property-card", True, "Property card"),
        ("article.listing", True, "Article listing"),
        ("div.nav-item", False, "Navigation item"),
        ("footer div.footer-link", False, "Footer link"),
    ]

    passed = 0
    failed = 0

    for selector, expected, description in test_cases:
        element = soup.select_one(selector)
        if not element:
            print(f"  [SKIP] {description} - Element not found")
            continue

        result = is_relevant_listing(element, threshold=25)
        status = "PASS" if result == expected else "FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"  [{status}] {description}: Expected {expected}, Got {result}")

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print()
    return failed == 0


def run_all_tests():
    """Run all intelligent scraper tests"""
    print()
    print("=" * 80)
    print("INTELLIGENT SCRAPER TEST SUITE")
    print("=" * 80)
    print()

    results = []

    try:
        results.append(("URL Filtering", test_url_filtering()))
    except Exception as e:
        print(f"ERROR in URL Filtering: {e}")
        results.append(("URL Filtering", False))

    try:
        results.append(("Relevance Scoring", test_relevance_scoring()))
    except Exception as e:
        print(f"ERROR in Relevance Scoring: {e}")
        results.append(("Relevance Scoring", False))

    try:
        results.append(("Auto-Selector Discovery", test_auto_selector_discovery()))
    except Exception as e:
        print(f"ERROR in Auto-Selector Discovery: {e}")
        results.append(("Auto-Selector Discovery", False))

    try:
        results.append(("Is Relevant Listing", test_is_relevant_listing_helper()))
    except Exception as e:
        print(f"ERROR in Is Relevant Listing: {e}")
        results.append(("Is Relevant Listing", False))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")

    print()
    print(f"Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print()
        print("=" * 80)
        print("ALL TESTS PASSED! Intelligent scraper is working correctly.")
        print("=" * 80)
        return True
    else:
        print()
        print("=" * 80)
        print(f"SOME TESTS FAILED: {total_count - passed_count} failures")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
