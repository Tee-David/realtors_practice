# helpers/relevance.py
# Heuristic-based relevance detection for property listings
# 100% FREE - No AI APIs, only programmatic rules

import re
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# Property-related keywords for text pattern matching
PROPERTY_KEYWORDS = {
    'type': ['bedroom', 'bathroom', 'toilet', 'bq', 'flat', 'apartment', 'house',
             'duplex', 'bungalow', 'terrace', 'detached', 'semi-detached', 'plot',
             'land', 'office', 'shop', 'warehouse', 'hotel', 'estate'],
    'action': ['for sale', 'for rent', 'to let', 'buy', 'rent', 'lease', 'shortlet'],
    'location': ['lagos', 'lekki', 'ikoyi', 'victoria island', 'vi', 'ikeja', 'ajah',
                 'yaba', 'surulere', 'abuja', 'port harcourt', 'ibadan'],
    'price': ['₦', 'naira', 'million', 'billion', 'k', 'm', 'price', 'cost', 'amount'],
}

# Category/navigation patterns to exclude
CATEGORY_PATTERNS = [
    'all properties', 'view all', 'see more', 'browse', 'categories',
    'property types', 'locations', 'navigation', 'menu', 'footer',
    'header', 'sidebar', 'advertisement', 'sponsored'
]


def count_keywords(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in text (case-insensitive)."""
    if not text:
        return 0
    text_lower = text.lower()
    return sum(1 for keyword in keywords if keyword in text_lower)


def extract_numbers(text: str) -> List[str]:
    """Extract numeric patterns from text (for bedroom counts, prices, etc.)."""
    if not text:
        return []
    # Match patterns like: "3", "4-bedroom", "5 bed", etc.
    return re.findall(r'\d+(?:\.\d+)?(?:\s*(?:bed|bath|toilet|m|k|billion|million))?', text, re.IGNORECASE)


def has_price_pattern(text: str) -> bool:
    """Check if text contains price-like patterns."""
    if not text:
        return False

    price_patterns = [
        r'₦\s*\d+',  # ₦5000000
        r'\d+\s*(?:million|billion|k|m)',  # 5 million, 500k
        r'price[:\s]*₦?\d+',  # Price: ₦5000000
        r'(?:from|starts?|cost)[:\s]*₦?\d+',  # From ₦5000000
    ]

    for pattern in price_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def score_element_relevance(element: Tag, url: Optional[str] = None) -> Dict[str, any]:
    """
    Score an HTML element's relevance as a property listing using heuristic rules.

    Returns a dict with:
        - score (int): Total relevance score (higher = more relevant)
        - signals (dict): Individual scoring signals
        - is_relevant (bool): True if score >= threshold

    Scoring breakdown:
        - Text patterns: +10 per property keyword, +5 per location, +15 for price
        - Element structure: +20 for image+title+price, +10 for proper nesting
        - URL patterns: +25 for property URL, -30 for category URL
        - Element attributes: +15 for property-related classes/IDs
        - Position: +10 if in main content area, -20 if in nav/footer
    """
    score = 0
    signals = {}

    # Extract text content
    text = element.get_text(" ", strip=True)
    text_lower = text.lower()

    # 1. TEXT PATTERN ANALYSIS (+0 to +50)
    property_count = count_keywords(text, PROPERTY_KEYWORDS['type'])
    location_count = count_keywords(text, PROPERTY_KEYWORDS['location'])
    action_count = count_keywords(text, PROPERTY_KEYWORDS['action'])

    signals['property_keywords'] = property_count
    signals['location_keywords'] = location_count
    signals['action_keywords'] = action_count

    score += property_count * 10  # Each property keyword: +10
    score += location_count * 5   # Each location: +5
    score += action_count * 3     # Each action: +3

    # Price detection
    has_price = has_price_pattern(text)
    signals['has_price'] = has_price
    if has_price:
        score += 15

    # Bedroom/bathroom counts
    numbers = extract_numbers(text)
    signals['numeric_values'] = len(numbers)
    if len(numbers) > 0:
        score += min(len(numbers) * 5, 20)  # Cap at +20

    # 2. ELEMENT STRUCTURE ANALYSIS (+0 to +30)
    has_image = element.find('img') is not None
    has_title = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a']) is not None
    has_link = element.find('a', href=True) is not None

    signals['has_image'] = has_image
    signals['has_title'] = has_title
    signals['has_link'] = has_link

    # Ideal structure: image + title + price + link
    if has_image and has_title and has_price and has_link:
        score += 20  # Perfect structure
    elif (has_image or has_title) and has_link:
        score += 10  # Decent structure

    # Nested elements suggest card-like structure
    child_count = len(list(element.find_all(recursive=False)))
    if 3 <= child_count <= 10:  # Reasonable nesting
        score += 10
        signals['proper_nesting'] = True
    else:
        signals['proper_nesting'] = False

    # 3. URL PATTERN ANALYSIS (+25 or -30)
    if url:
        from parsers.specials import _is_property_url

        is_property = _is_property_url(url)
        signals['property_url'] = is_property

        if is_property:
            score += 25
        else:
            score -= 30  # Strong penalty for category URLs
    else:
        # Extract href from element
        link = element.find('a', href=True)
        if link:
            href = link.get('href', '')
            signals['has_href'] = True

            # Basic URL heuristics
            if any(kw in href.lower() for kw in ['property', 'listing', 'detail', 'bedroom']):
                score += 10
            elif any(kw in href.lower() for kw in ['category', 'browse', 'search', 'filter']):
                score -= 15
        else:
            signals['has_href'] = False
            score -= 10  # No link = less likely to be listing

    # 4. ELEMENT ATTRIBUTES ANALYSIS (+0 to +15)
    element_classes = ' '.join(element.get('class', [])).lower()
    element_id = (element.get('id', '') or '').lower()
    combined_attrs = f"{element_classes} {element_id}"

    # Positive class names
    positive_attrs = ['listing', 'property', 'card', 'item', 'result', 'product']
    if any(attr in combined_attrs for attr in positive_attrs):
        score += 15
        signals['positive_class'] = True
    else:
        signals['positive_class'] = False

    # Negative class names (nav, footer, ads)
    negative_attrs = ['nav', 'menu', 'footer', 'header', 'sidebar', 'ad', 'banner', 'sponsor']
    if any(attr in combined_attrs for attr in negative_attrs):
        score -= 20
        signals['negative_class'] = True
    else:
        signals['negative_class'] = False

    # 5. POSITION ANALYSIS (+10 or -20)
    # Check if element is in navigation/footer area
    parent_tree = [p.name for p in element.parents if p.name]
    if any(p in ['nav', 'footer', 'header', 'aside'] for p in parent_tree):
        score -= 20
        signals['in_navigation'] = True
    elif 'main' in parent_tree or 'article' in parent_tree:
        score += 10
        signals['in_main_content'] = True
    else:
        signals['in_main_content'] = False

    # 6. CATEGORY EXCLUSION (-50)
    if any(pattern in text_lower for pattern in CATEGORY_PATTERNS):
        score -= 50
        signals['category_text'] = True

    # FINAL SCORE CALCULATION
    threshold = 30  # Minimum score to be considered relevant
    is_relevant = score >= threshold

    return {
        'score': score,
        'is_relevant': is_relevant,
        'signals': signals,
        'threshold': threshold,
    }


def is_relevant_listing(element: Tag, url: Optional[str] = None, threshold: int = 30) -> bool:
    """
    Quick boolean check if element is a relevant property listing.

    Args:
        element: BeautifulSoup Tag element to analyze
        url: Optional URL associated with this element
        threshold: Minimum score to be considered relevant (default: 30)

    Returns:
        True if element is likely a property listing, False otherwise
    """
    result = score_element_relevance(element, url)
    return result['score'] >= threshold


def find_best_selector(html: str, candidate_selectors: List[str], min_score: int = 30) -> Tuple[Optional[str], List[Dict]]:
    """
    Automatically discover the best CSS selector for property listings using heuristics.

    Args:
        html: HTML content to analyze
        candidate_selectors: List of CSS selectors to try (e.g., ['div.listing', 'li.property', 'article'])
        min_score: Minimum relevance score for an element to be considered

    Returns:
        Tuple of (best_selector, scored_results)
            - best_selector: CSS selector with highest average relevance score
            - scored_results: List of dicts with selector, count, avg_score
    """
    soup = BeautifulSoup(html, 'lxml')
    results = []

    for selector in candidate_selectors:
        elements = soup.select(selector)

        if not elements:
            continue

        scores = []
        relevant_count = 0

        for el in elements[:20]:  # Sample first 20 elements
            result = score_element_relevance(el)
            scores.append(result['score'])

            if result['is_relevant']:
                relevant_count += 1

        if scores:
            avg_score = sum(scores) / len(scores)
            results.append({
                'selector': selector,
                'total_count': len(elements),
                'sampled_count': len(scores),
                'relevant_count': relevant_count,
                'avg_score': avg_score,
                'max_score': max(scores),
                'min_score': min(scores),
            })

    # Sort by average score (descending)
    results.sort(key=lambda x: x['avg_score'], reverse=True)

    # Return best selector (highest avg score with at least some relevant items)
    best = None
    for result in results:
        if result['relevant_count'] > 0 and result['avg_score'] >= min_score:
            best = result['selector']
            break

    return best, results


# Usage examples in comments:
"""
USAGE EXAMPLES:

1. Score a single element:
   from helpers.relevance import score_element_relevance

   element = soup.select_one("div.property-card")
   result = score_element_relevance(element, url="https://site.com/property/12345")

   print(f"Score: {result['score']}")
   print(f"Relevant: {result['is_relevant']}")
   print(f"Signals: {result['signals']}")

2. Filter elements by relevance:
   from helpers.relevance import is_relevant_listing

   cards = soup.select("div.card")
   relevant_cards = [card for card in cards if is_relevant_listing(card)]

3. Auto-discover best selector:
   from helpers.relevance import find_best_selector

   candidates = ['div.listing', 'li.property', 'article', 'div[class*=card]']
   best_selector, results = find_best_selector(html, candidates)

   print(f"Best selector: {best_selector}")
   for r in results[:3]:
       print(f"{r['selector']}: {r['avg_score']:.1f} avg score, {r['relevant_count']} relevant")

4. Integration with scraper:
   # In parsers/specials.py
   from helpers.relevance import is_relevant_listing

   for card in soup.select(card_selector):
       # Filter out irrelevant cards
       if not is_relevant_listing(card):
           continue

       # Extract data from relevant cards only
       title = card.select_one("h2").text
       # ...
"""
