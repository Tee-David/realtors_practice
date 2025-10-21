# helpers/__init__.py
# Modular helper functions for intelligent scraping

# Import screenshot utilities
from .screenshot import (
    take_screenshot,
    take_error_screenshot,
    take_element_screenshot,
    cleanup_old_screenshots
)

# Import relevance detection utilities
from .relevance import (
    is_relevant_listing,
    score_element_relevance,
    find_best_selector
)

__all__ = [
    # Screenshot utilities
    'take_screenshot',
    'take_error_screenshot',
    'take_element_screenshot',
    'cleanup_old_screenshots',

    # Relevance detection
    'is_relevant_listing',
    'score_element_relevance',
    'find_best_selector',
]
