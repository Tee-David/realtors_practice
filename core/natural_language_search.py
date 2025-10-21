"""
Natural Language Search Module

Parse natural language property search queries into structured filters.
No external NLP libraries required - uses pattern matching and rules.

Examples:
- "3 bedroom flat in Lekki under 30 million"
- "Land for sale near VI with C of O"
- "4BR duplex in Ikoyi between 50M and 100M"

Author: Tee-David
Date: 2025-10-20
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NaturalLanguageSearchParser:
    """
    Parse natural language search queries into structured filters.

    Uses regex patterns and keyword matching (no external NLP needed).
    """

    # Property type patterns
    PROPERTY_TYPES = {
        r'\b(flat|apartment|apt)\b': 'Flat',
        r'\b(duplex|duplexes)\b': 'Duplex',
        r'\b(terrace|terraced)\b': 'Terrace',
        r'\b(detached|house|bungalow)\b': 'Detached',
        r'\b(land|plot|plots)\b': 'Land',
        r'\b(commercial|office|shop)\b': 'Commercial',
        r'\b(warehouse)\b': 'Warehouse'
    }

    # Location patterns (Lagos-specific)
    LOCATIONS = [
        'Lekki', 'Ikoyi', 'Victoria Island', 'VI', 'Ajah', 'Banana Island',
        'Ikeja', 'Yaba', 'Surulere', 'Maryland', 'Magodo', 'Festac',
        'Lekki Phase 1', 'Lekki Phase 2', 'VGC', 'Parkview', 'Elegushi',
        'Sangotedo', 'Abijo', 'Bogije', 'Epe', 'Chevron', 'Oniru',
        'Osapa', 'Agungi', 'Igbo Efon', 'Eti-Osa', 'Badore', 'Idado'
    ]

    # Bedroom/bathroom patterns
    BEDROOM_PATTERNS = [
        r'(\d+)\s*(?:bedroom|bed|br|bdr)\b',
        r'\b(\d+)BR\b',
        r'\b(\d+)B\b'  # Less specific, use carefully
    ]

    BATHROOM_PATTERNS = [
        r'(\d+)\s*(?:bathroom|bath|ba)\b',
        r'\b(\d+)BA\b'
    ]

    # Price patterns
    PRICE_PATTERNS = {
        'under': r'(?:under|below|less than|max|maximum)\s+(?:₦|NGN|N)?\s*(\d+(?:\.\d+)?)\s*([MmKk]?)',
        'over': r'(?:over|above|more than|min|minimum)\s+(?:₦|NGN|N)?\s*(\d+(?:\.\d+)?)\s*([MmKk]?)',
        'exact': r'(?:₦|NGN|N)?\s*(\d+(?:\.\d+)?)\s*([MmKk]?)\b',
        'between': r'between\s+(?:₦|NGN|N)?\s*(\d+(?:\.\d+)?)\s*([MmKk]?)\s+and\s+(?:₦|NGN|N)?\s*(\d+(?:\.\d+)?)\s*([MmKk]?)'
    }

    # Special features patterns
    FEATURES = {
        'pool': r'\bpool|swimming\b',
        'bq': r'\bbq|boys?\s+quarters?\b',
        'c_of_o': r'\b(?:c\s*of\s*o|certificate of occupancy|title|documented)\b',
        'serviced': r'\bserviced\b',
        'gated': r'\bgated\b',
        'furnished': r'\bfurnished\b',
        'new': r'\bnew|newly\s+built\b'
    }

    def __init__(self):
        """Initialize NL search parser"""
        logger.debug("NaturalLanguageSearchParser initialized")

    def _parse_price(self, value: str, multiplier: str) -> float:
        """
        Parse price with multiplier.

        Args:
            value: Numeric value
            multiplier: 'M' (million), 'K' (thousand), or empty

        Returns:
            Price in Naira
        """
        try:
            num = float(value)

            if multiplier.upper() == 'M':
                return num * 1_000_000
            elif multiplier.upper() == 'K':
                return num * 1_000
            else:
                return num

        except ValueError:
            return 0.0

    def parse_query(self, query: str) -> Dict:
        """
        Parse natural language query into structured filters.

        Args:
            query: Natural language search query

        Returns:
            Dict with parsed filters compatible with query_engine

        Example:
            Input: "3 bedroom flat in Lekki under 30 million"
            Output: {
                'property_type': 'Flat',
                'bedrooms': 3,
                'location': 'Lekki',
                'price_max': 30000000,
                'confidence': 0.9
            }
        """
        query_lower = query.lower()

        result = {
            'original_query': query,
            'filters': {},
            'features': [],
            'confidence': 0.0
        }

        confidence_score = 0
        max_confidence = 0

        # 1. Extract property type
        for pattern, prop_type in self.PROPERTY_TYPES.items():
            if re.search(pattern, query_lower):
                result['filters']['property_type'] = {'contains': prop_type}
                confidence_score += 20
                logger.debug(f"Detected property type: {prop_type}")
                break

        max_confidence += 20

        # 2. Extract location
        location_found = None
        for location in self.LOCATIONS:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(location) + r'\b'
            if re.search(pattern, query, re.IGNORECASE):
                location_found = location
                break

        if location_found:
            result['filters']['location'] = {'contains': location_found}
            confidence_score += 20
            logger.debug(f"Detected location: {location_found}")

        max_confidence += 20

        # 3. Extract bedrooms
        for pattern in self.BEDROOM_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                bedrooms = int(match.group(1))
                result['filters']['bedrooms'] = {'gte': bedrooms}
                confidence_score += 15
                logger.debug(f"Detected bedrooms: {bedrooms}")
                break

        max_confidence += 15

        # 4. Extract bathrooms
        for pattern in self.BATHROOM_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                bathrooms = int(match.group(1))
                result['filters']['bathrooms'] = {'gte': bathrooms}
                confidence_score += 10
                logger.debug(f"Detected bathrooms: {bathrooms}")
                break

        max_confidence += 10

        # 5. Extract price constraints
        # Check "between" first (most specific)
        match = re.search(self.PRICE_PATTERNS['between'], query_lower)
        if match:
            min_val, min_mult, max_val, max_mult = match.groups()
            price_min = self._parse_price(min_val, min_mult or '')
            price_max = self._parse_price(max_val, max_mult or '')

            result['filters']['price'] = {'between': [price_min, price_max]}
            confidence_score += 25
            logger.debug(f"Detected price range: ₦{price_min:,.0f} - ₦{price_max:,.0f}")

        else:
            # Check "under"
            match = re.search(self.PRICE_PATTERNS['under'], query_lower)
            if match:
                val, mult = match.groups()
                price_max = self._parse_price(val, mult or '')
                result['filters']['price'] = {'lte': price_max}
                confidence_score += 20
                logger.debug(f"Detected max price: ₦{price_max:,.0f}")

            # Check "over"
            match = re.search(self.PRICE_PATTERNS['over'], query_lower)
            if match:
                val, mult = match.groups()
                price_min = self._parse_price(val, mult or '')
                result['filters']['price'] = {'gte': price_min}
                confidence_score += 20
                logger.debug(f"Detected min price: ₦{price_min:,.0f}")

        max_confidence += 25

        # 6. Extract special features
        for feature, pattern in self.FEATURES.items():
            if re.search(pattern, query_lower):
                result['features'].append(feature)
                confidence_score += 2
                logger.debug(f"Detected feature: {feature}")

        max_confidence += 10  # Max for features

        # Calculate confidence (0.0 to 1.0)
        result['confidence'] = round(confidence_score / max_confidence, 2) if max_confidence > 0 else 0.0

        logger.info(
            f"Parsed query with {result['confidence']:.0%} confidence: "
            f"{len(result['filters'])} filters, {len(result['features'])} features"
        )

        return result

    def generate_query_engine_filters(self, parsed: Dict) -> Dict:
        """
        Convert parsed NL query to query_engine compatible filters.

        Args:
            parsed: Output from parse_query()

        Returns:
            Dict compatible with PropertyQuery.filter()
        """
        return parsed.get('filters', {})

    def get_suggestions(self, partial_query: str) -> List[str]:
        """
        Get search suggestions based on partial query.

        Args:
            partial_query: Partial search text

        Returns:
            List of suggested completions
        """
        suggestions = []
        query_lower = partial_query.lower()

        # Suggest locations
        for location in self.LOCATIONS[:10]:  # Top 10
            if location.lower().startswith(query_lower):
                suggestions.append(f"{partial_query} {location}")

        # Suggest common queries
        common_patterns = [
            "3 bedroom flat in",
            "4 bedroom duplex in",
            "land for sale in",
            "under 30 million",
            "between 20M and 50M"
        ]

        for pattern in common_patterns:
            if pattern.startswith(query_lower):
                suggestions.append(pattern)

        return suggestions[:5]  # Return top 5


def get_nl_search_parser() -> NaturalLanguageSearchParser:
    """
    Get a NaturalLanguageSearchParser instance.

    Returns:
        NaturalLanguageSearchParser instance
    """
    return NaturalLanguageSearchParser()
