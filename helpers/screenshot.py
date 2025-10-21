# helpers/screenshot.py
# Screenshot utility for debugging and visual inspection
# NOT for AI vision - just for human debugging

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Environment variable to enable/disable screenshots
RP_SCREENSHOT = os.getenv("RP_SCREENSHOT", "0") == "1"
SCREENSHOT_DIR = "debug_screenshots"


def ensure_screenshot_dir():
    """Create screenshot directory if it doesn't exist."""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)


def take_screenshot(page, site_key: str, page_type: str = "page", context: str = "") -> Optional[str]:
    """
    Take a screenshot of the current page for debugging purposes.

    Args:
        page: Playwright page object
        site_key: Site identifier (e.g., 'npc', 'propertypro')
        page_type: Type of page being captured (e.g., 'list', 'detail', 'error')
        context: Additional context for filename (e.g., page number, error type)

    Returns:
        Path to saved screenshot, or None if screenshots disabled

    Example:
        take_screenshot(page, "npc", "list", "page_1")
        # Saves: debug_screenshots/npc_list_page_1_20251019_143052.png
    """
    if not RP_SCREENSHOT:
        return None

    try:
        ensure_screenshot_dir()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        context_part = f"_{context}" if context else ""
        filename = f"{site_key}_{page_type}{context_part}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)

        # Take screenshot
        page.screenshot(path=filepath, full_page=True)

        logger.info(f"Screenshot saved: {filepath}")
        return filepath

    except Exception as e:
        logger.warning(f"Failed to take screenshot: {e}")
        return None


def take_error_screenshot(page, site_key: str, error_type: str, error_msg: str = "") -> Optional[str]:
    """
    Take a screenshot when an error occurs for debugging.

    Args:
        page: Playwright page object
        site_key: Site identifier
        error_type: Type of error (e.g., 'timeout', 'selector_not_found', 'parse_error')
        error_msg: Optional error message for logging

    Returns:
        Path to saved screenshot, or None if screenshots disabled

    Example:
        take_error_screenshot(page, "npc", "timeout", "Page took too long to load")
    """
    if not RP_SCREENSHOT:
        return None

    try:
        # Clean error type for filename
        clean_error = error_type.replace(" ", "_").replace("/", "_")[:50]

        # Take screenshot with error context
        filepath = take_screenshot(page, site_key, "error", clean_error)

        if filepath and error_msg:
            logger.error(f"{site_key}: {error_type} - Screenshot: {filepath} - {error_msg}")

        return filepath

    except Exception as e:
        logger.warning(f"Failed to take error screenshot: {e}")
        return None


def take_element_screenshot(page, selector: str, site_key: str, context: str = "") -> Optional[str]:
    """
    Take a screenshot of a specific element for debugging.

    Args:
        page: Playwright page object
        selector: CSS selector for the element to capture
        site_key: Site identifier
        context: Additional context for filename

    Returns:
        Path to saved screenshot, or None if screenshots disabled or element not found

    Example:
        take_element_screenshot(page, "li.property-list", "npc", "listing_card_1")
    """
    if not RP_SCREENSHOT:
        return None

    try:
        element = page.query_selector(selector)
        if not element:
            logger.warning(f"Element not found for screenshot: {selector}")
            return None

        ensure_screenshot_dir()

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        context_part = f"_{context}" if context else ""
        filename = f"{site_key}_element{context_part}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)

        # Take element screenshot
        element.screenshot(path=filepath)

        logger.info(f"Element screenshot saved: {filepath}")
        return filepath

    except Exception as e:
        logger.warning(f"Failed to take element screenshot: {e}")
        return None


def cleanup_old_screenshots(days: int = 7):
    """
    Remove screenshots older than specified days to save disk space.

    Args:
        days: Delete screenshots older than this many days (default: 7)
    """
    if not os.path.exists(SCREENSHOT_DIR):
        return

    try:
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0

        for filename in os.listdir(SCREENSHOT_DIR):
            filepath = os.path.join(SCREENSHOT_DIR, filename)

            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old screenshots (older than {days} days)")

    except Exception as e:
        logger.warning(f"Failed to cleanup old screenshots: {e}")


# Usage examples in comments:
"""
USAGE EXAMPLES:

1. Enable screenshots via environment variable:
   set RP_SCREENSHOT=1
   python main.py

2. Take screenshot of list page:
   from helpers.screenshot import take_screenshot
   take_screenshot(page, "npc", "list", "page_1")

3. Take screenshot on error:
   from helpers.screenshot import take_error_screenshot
   try:
       # ... scraping logic ...
   except TimeoutError as e:
       take_error_screenshot(page, "npc", "timeout", str(e))

4. Take screenshot of specific element:
   from helpers.screenshot import take_element_screenshot
   take_element_screenshot(page, "li.property-list", "npc", "first_card")

5. Cleanup old screenshots:
   from helpers.screenshot import cleanup_old_screenshots
   cleanup_old_screenshots(days=7)  # Remove screenshots older than 7 days
"""
