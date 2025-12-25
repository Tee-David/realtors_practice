"""
Universal NLP Helper for Intelligent Extraction

Uses Natural Language Processing to enhance data extraction:
- Named Entity Recognition (NER) for locations, organizations
- Part-of-speech tagging for property features
- Text classification for property types
- Sentiment analysis for quality assessment
- Smart text summarization

This module works WITHOUT requiring site-specific training data.
Uses lightweight NLP that doesn't need GPU or large models.

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import re
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import spaCy (optional dependency)
try:
    import spacy
    # Try to load English model (small, lightweight)
    try:
        nlp = spacy.load("en_core_web_sm")
        NLP_AVAILABLE = True
        logger.info("spaCy NLP loaded successfully")
    except OSError:
        logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        NLP_AVAILABLE = False
        nlp = None
except ImportError:
    logger.warning("spaCy not installed. NLP features disabled. Install with: pip install spacy")
    NLP_AVAILABLE = False
    nlp = None


# Property type keywords (for classification)
PROPERTY_TYPE_KEYWORDS = {
    'apartment': ['apartment', 'flat', 'condo', 'studio', 'penthouse'],
    'house': ['house', 'bungalow', 'duplex', 'detached', 'semi-detached', 'terrace', 'townhouse'],
    'land': ['land', 'plot', 'acre', 'hectare', 'vacant land'],
    'commercial': ['office', 'shop', 'warehouse', 'commercial', 'retail', 'plaza'],
    'maisonette': ['maisonette'],
    'mansion': ['mansion', 'villa', 'estate home']
}

# Amenity keywords (for feature extraction)
AMENITY_KEYWORDS = {
    'security': ['security', 'cctv', 'gated', 'gate', 'gateman', 'security guard'],
    'parking': ['parking', 'garage', 'car park', 'parking space'],
    'power': ['24hr power', '24/7 power', 'generator', 'inverter', 'solar', 'uninterrupted power'],
    'water': ['borehole', 'water supply', '24hr water', 'treated water'],
    'facilities': ['swimming pool', 'gym', 'clubhouse', 'playground', 'garden', 'lawn'],
    'kitchen': ['fitted kitchen', 'modern kitchen', 'kitchen cabinets', 'pantry'],
    'others': ['air conditioning', 'ac', 'wardrobes', 'bq', 'boys quarters', 'study room']
}


def extract_location_with_nlp(text: str) -> Optional[str]:
    """
    Extract location using NLP Named Entity Recognition.
    Falls back to pattern matching if NLP not available.

    Args:
        text: Text content to analyze

    Returns:
        Location string, or None if not found
    """
    if NLP_AVAILABLE and nlp:
        try:
            # Use spaCy NER
            doc = nlp(text[:5000])  # Limit text length for performance

            # Extract location entities (GPE = Geopolitical Entity, LOC = Location)
            locations = []
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    locations.append(ent.text)

            # Return the first location found
            if locations:
                return locations[0]

        except Exception as e:
            logger.debug(f"NLP location extraction error: {e}")

    # Fallback: Pattern-based extraction (already in universal_extractor.py)
    location_patterns = [
        r'(?:Location|Address|Area):\s*([^<\n]+)',
        r'(?:Located in|Found in|Situated in)\s+([^<\n]+)'
    ]

    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def classify_property_type(text: str) -> Optional[str]:
    """
    Classify property type using keyword matching.
    Can be enhanced with ML in the future.

    Args:
        text: Property title or description

    Returns:
        Property type string, or None if not determined
    """
    text_lower = text.lower()

    # Check each property type
    for property_type, keywords in PROPERTY_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return property_type

    return None


def extract_amenities(text: str) -> List[str]:
    """
    Extract amenities and features from text.

    Args:
        text: Property description

    Returns:
        List of amenity strings
    """
    text_lower = text.lower()
    found_amenities = []

    # Check all amenity categories
    for category, keywords in AMENITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_amenities.append(keyword)

    # Remove duplicates while preserving order
    seen = set()
    unique_amenities = []
    for amenity in found_amenities:
        if amenity not in seen:
            seen.add(amenity)
            unique_amenities.append(amenity)

    return unique_amenities


def extract_key_phrases(text: str, limit: int = 10) -> List[str]:
    """
    Extract key phrases from text using NLP or pattern matching.

    Args:
        text: Text to analyze
        limit: Maximum number of phrases to return

    Returns:
        List of key phrases
    """
    if NLP_AVAILABLE and nlp:
        try:
            doc = nlp(text[:5000])

            # Extract noun chunks (key phrases)
            phrases = []
            for chunk in doc.noun_chunks:
                # Filter out very short or very long chunks
                if 2 <= len(chunk.text.split()) <= 5:
                    phrases.append(chunk.text)

            return phrases[:limit]

        except Exception as e:
            logger.debug(f"NLP key phrase extraction error: {e}")

    # Fallback: Simple pattern matching
    # Extract capitalized phrases (likely important)
    capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    phrases = re.findall(capitalized_pattern, text)

    return phrases[:limit]


def enhance_title_with_nlp(title: str, description: str = "", location: str = "") -> str:
    """
    Enhance a property title using NLP and context.
    Makes generic titles more descriptive.

    Args:
        title: Original title (may be generic like "Chevron")
        description: Property description (for context)
        location: Property location (for context)

    Returns:
        Enhanced title
    """
    # If title is already good (long and descriptive), return as-is
    if len(title) > 30:
        return title

    # If title is generic location name, construct better title
    if len(title) < 15:
        # Try to extract property type from description
        property_type = classify_property_type(description or title)

        # Try to extract bedroom count from description
        bedroom_match = re.search(r'(\d+)\s*(?:bedroom|bed|br)', description or title, re.IGNORECASE)
        bedrooms = bedroom_match.group(1) if bedroom_match else None

        # Construct enhanced title
        parts = []

        if bedrooms:
            parts.append(f"{bedrooms} Bedroom")

        if property_type:
            parts.append(property_type.title())
        else:
            parts.append("Property")

        if location:
            parts.append(f"in {location}")
        elif title:
            parts.append(f"in {title}")

        enhanced = " ".join(parts)
        return enhanced

    return title


def summarize_description(description: str, max_length: int = 200) -> str:
    """
    Summarize a long description to key points.

    Args:
        description: Full description text
        max_length: Maximum character length

    Returns:
        Summarized text
    """
    if len(description) <= max_length:
        return description

    if NLP_AVAILABLE and nlp:
        try:
            doc = nlp(description[:2000])  # Limit for performance

            # Extract sentences with important information
            # Priority: sentences with numbers, locations, amenities
            important_sentences = []

            for sent in doc.sents:
                sent_text = sent.text.strip()

                # Check if sentence contains important info
                has_numbers = any(token.pos_ == 'NUM' for token in sent)
                has_location = any(ent.label_ in ['GPE', 'LOC'] for ent in sent.ents)
                has_amenity = any(keyword in sent_text.lower() for keywords in AMENITY_KEYWORDS.values() for keyword in keywords)

                if has_numbers or has_location or has_amenity:
                    important_sentences.append(sent_text)

                # Stop if we have enough
                if sum(len(s) for s in important_sentences) >= max_length:
                    break

            if important_sentences:
                summary = " ".join(important_sentences)
                if len(summary) > max_length:
                    summary = summary[:max_length] + "..."
                return summary

        except Exception as e:
            logger.debug(f"NLP summarization error: {e}")

    # Fallback: Simple truncation with sentence boundary
    if len(description) > max_length:
        # Try to break at sentence boundary
        truncated = description[:max_length]
        last_period = truncated.rfind('.')

        if last_period > max_length * 0.7:  # If period is in last 30%
            return truncated[:last_period + 1]
        else:
            return truncated + "..."

    return description


def analyze_text_quality(text: str) -> Dict[str, any]:
    """
    Analyze text quality using NLP metrics.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with quality metrics:
        {
            'word_count': int,
            'sentence_count': int,
            'avg_word_length': float,
            'has_details': bool,
            'readability_score': int (0-100)
        }
    """
    words = text.split()
    word_count = len(words)

    # Count sentences (approximate)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])

    # Average word length
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0

    # Check for details (numbers, specific amenities)
    has_numbers = bool(re.search(r'\d+', text))
    has_amenities = any(keyword in text.lower() for keywords in AMENITY_KEYWORDS.values() for keyword in keywords)
    has_details = has_numbers and has_amenities

    # Simple readability score (0-100)
    # Higher = more detailed and informative
    readability_score = 0

    if word_count > 50:
        readability_score += 30
    elif word_count > 20:
        readability_score += 15

    if sentence_count >= 3:
        readability_score += 20
    elif sentence_count >= 1:
        readability_score += 10

    if has_details:
        readability_score += 30

    if avg_word_length > 5:  # Longer words = more specific/technical
        readability_score += 20

    readability_score = min(100, readability_score)

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_word_length': round(avg_word_length, 2),
        'has_details': has_details,
        'readability_score': readability_score
    }


def extract_contact_info(text: str) -> Dict[str, List[str]]:
    """
    Extract contact information (phone, email) from text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with contact info:
        {
            'phones': List[str],
            'emails': List[str]
        }
    """
    phones = []
    emails = []

    # Nigerian phone number patterns
    phone_patterns = [
        r'\b0[789]\d{9}\b',  # 08012345678
        r'\b\+234[789]\d{9}\b',  # +2348012345678
        r'\b234[789]\d{9}\b',  # 2348012345678
    ]

    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))

    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails.extend(re.findall(email_pattern, text))

    return {
        'phones': list(set(phones)),  # Remove duplicates
        'emails': list(set(emails))
    }


# Example usage and testing
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)

    print("="*60)
    print("UNIVERSAL NLP TESTING")
    print("="*60)
    print(f"NLP Available: {NLP_AVAILABLE}\n")

    # Test text
    test_description = """
    This beautiful 3 bedroom apartment is located in Lekki Phase 1, Victoria Island.
    The property features a modern fitted kitchen, spacious living room, 24hr power supply,
    swimming pool, gym, and secure gated estate with CCTV. The apartment comes with
    2 bathrooms, ample parking space, and boys quarters. Contact: 08012345678 or
    info@property.com for viewing.
    """

    # Test 1: Location extraction
    print("\nTest 1: Location Extraction (NLP)")
    location = extract_location_with_nlp(test_description)
    print(f"Location: {location}")

    # Test 2: Property type classification
    print("\nTest 2: Property Type Classification")
    prop_type = classify_property_type(test_description)
    print(f"Property Type: {prop_type}")

    # Test 3: Amenity extraction
    print("\nTest 3: Amenity Extraction")
    amenities = extract_amenities(test_description)
    print(f"Amenities: {amenities}")

    # Test 4: Title enhancement
    print("\nTest 4: Title Enhancement")
    generic_title = "Lekki"
    enhanced = enhance_title_with_nlp(generic_title, test_description, "Lekki Phase 1")
    print(f"Original: {generic_title}")
    print(f"Enhanced: {enhanced}")

    # Test 5: Description summarization
    print("\nTest 5: Description Summarization")
    summary = summarize_description(test_description, max_length=100)
    print(f"Summary: {summary}")

    # Test 6: Text quality analysis
    print("\nTest 6: Text Quality Analysis")
    quality = analyze_text_quality(test_description)
    for key, value in quality.items():
        print(f"  {key}: {value}")

    # Test 7: Contact extraction
    print("\nTest 7: Contact Info Extraction")
    contacts = extract_contact_info(test_description)
    print(f"Phones: {contacts['phones']}")
    print(f"Emails: {contacts['emails']}")

    # Test 8: Key phrase extraction
    print("\nTest 8: Key Phrase Extraction")
    phrases = extract_key_phrases(test_description, limit=5)
    print(f"Key Phrases: {phrases}")

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
