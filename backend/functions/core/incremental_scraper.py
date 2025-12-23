"""
Incremental Scraping Module

Tracks previously seen listings to enable delta updates (only scrape new content).
Dramatically reduces scraping time by stopping when we encounter known listings.

Strategy:
- Track seen URLs per site in logs/seen_urls_{site}.json
- Start from page 1 (newest listings typically at top)
- Check each listing URL against seen set
- Stop after N consecutive seen listings (assumes newest first)
- Enables frequent scheduled runs (hourly instead of daily)

Author: Tee-David
Date: 2025-10-20
"""

import json
import logging
import time
from pathlib import Path
from typing import Set, Optional, Dict, List
from threading import Lock

logger = logging.getLogger(__name__)


class IncrementalScraper:
    """
    Tracks previously seen listings to enable incremental (delta) scraping.

    Only scrapes new content by stopping when encountering consecutive known listings.
    Assumes newest listings appear first (typical for most real estate sites).
    """

    def __init__(self, site_key: str, seen_urls_dir: str = "logs/seen_urls"):
        """
        Initialize incremental scraper for a specific site.

        Args:
            site_key: Unique identifier for the site (e.g., 'npc', 'propertypro')
            seen_urls_dir: Directory to store seen URL tracking files
        """
        self.site_key = site_key
        self.seen_urls_dir = Path(seen_urls_dir)
        self.seen_urls_dir.mkdir(parents=True, exist_ok=True)

        self.seen_urls_file = self.seen_urls_dir / f"{site_key}.json"

        # Load existing seen URLs
        self.seen_urls: Set[str] = self._load_seen_urls()

        # Tracking for consecutive seen count
        self.consecutive_seen = 0
        self.stop_threshold = 10  # Stop after N consecutive seen URLs

        # Stats
        self.new_urls_count = 0
        self.skipped_urls_count = 0

        # Thread safety
        self._lock = Lock()

        logger.debug(
            f"{site_key}: Incremental scraper initialized - "
            f"{len(self.seen_urls)} known URLs, stop_threshold={self.stop_threshold}"
        )

    def _load_seen_urls(self) -> Set[str]:
        """Load previously seen URLs from file"""
        if not self.seen_urls_file.exists():
            logger.debug(f"{self.site_key}: No seen URLs file found - starting fresh")
            return set()

        try:
            with open(self.seen_urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                seen_urls = set(data.get('urls', []))
                last_updated = data.get('last_updated', 'unknown')

                logger.info(
                    f"{self.site_key}: Loaded {len(seen_urls)} seen URLs "
                    f"(last updated: {last_updated})"
                )
                return seen_urls
        except Exception as e:
            logger.error(f"{self.site_key}: Error loading seen URLs: {e}")
            return set()

    def _save_seen_urls(self):
        """Save seen URLs to file with metadata"""
        try:
            with self._lock:
                data = {
                    'site_key': self.site_key,
                    'urls': list(self.seen_urls),
                    'total_count': len(self.seen_urls),
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'new_this_run': self.new_urls_count,
                    'skipped_this_run': self.skipped_urls_count
                }

                with open(self.seen_urls_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                logger.debug(
                    f"{self.site_key}: Saved {len(self.seen_urls)} seen URLs "
                    f"({self.new_urls_count} new, {self.skipped_urls_count} skipped)"
                )
        except Exception as e:
            logger.error(f"{self.site_key}: Error saving seen URLs: {e}")

    def is_url_seen(self, url: str) -> bool:
        """
        Check if URL has been seen before.

        Args:
            url: Listing URL to check

        Returns:
            True if URL was seen before, False if new
        """
        with self._lock:
            return url in self.seen_urls

    def mark_url_seen(self, url: str) -> bool:
        """
        Mark a URL as seen.

        Args:
            url: Listing URL to mark as seen

        Returns:
            True if URL was new (added), False if already existed
        """
        with self._lock:
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                self.new_urls_count += 1
                return True
            return False

    def should_continue_scraping(self, listing_url: str) -> bool:
        """
        Determine if scraping should continue based on seen URLs.

        Strategy:
        - If URL is new: Reset consecutive counter, continue
        - If URL is seen: Increment consecutive counter
        - If consecutive seen >= threshold: Stop scraping

        Args:
            listing_url: Current listing URL being processed

        Returns:
            True if should continue scraping, False if should stop
        """
        with self._lock:
            if listing_url in self.seen_urls:
                # Known URL - increment consecutive count
                self.consecutive_seen += 1
                self.skipped_urls_count += 1

                if self.consecutive_seen >= self.stop_threshold:
                    logger.info(
                        f"{self.site_key}: Stopping - encountered {self.consecutive_seen} "
                        f"consecutive known listings (threshold: {self.stop_threshold})"
                    )
                    return False

                logger.debug(
                    f"{self.site_key}: Known URL (consecutive: {self.consecutive_seen}): {listing_url}"
                )
            else:
                # New URL - reset consecutive count and add to seen
                if self.consecutive_seen > 0:
                    logger.debug(
                        f"{self.site_key}: New URL found - resetting consecutive counter "
                        f"(was {self.consecutive_seen})"
                    )
                self.consecutive_seen = 0
                self.seen_urls.add(listing_url)
                self.new_urls_count += 1

                logger.debug(f"{self.site_key}: New URL discovered: {listing_url}")

            return True

    def mark_urls_seen_batch(self, urls: List[str]):
        """
        Mark multiple URLs as seen at once.

        Args:
            urls: List of listing URLs to mark as seen
        """
        with self._lock:
            new_count = 0
            for url in urls:
                if url not in self.seen_urls:
                    self.seen_urls.add(url)
                    new_count += 1

            self.new_urls_count += new_count

            logger.debug(
                f"{self.site_key}: Marked {len(urls)} URLs as seen "
                f"({new_count} new, {len(urls) - new_count} duplicates)"
            )

    def get_stats(self) -> Dict:
        """
        Get statistics about current incremental scraping session.

        Returns:
            Dictionary with stats (total_seen, new_this_run, skipped_this_run, etc.)
        """
        with self._lock:
            return {
                'site_key': self.site_key,
                'total_seen_urls': len(self.seen_urls),
                'new_urls_this_run': self.new_urls_count,
                'skipped_urls_this_run': self.skipped_urls_count,
                'consecutive_seen': self.consecutive_seen,
                'stop_threshold': self.stop_threshold,
                'should_continue': self.consecutive_seen < self.stop_threshold
            }

    def reset_consecutive_counter(self):
        """Reset the consecutive seen counter (useful between pages)"""
        with self._lock:
            self.consecutive_seen = 0

    def save(self):
        """Save seen URLs to disk"""
        self._save_seen_urls()

    def clear_seen_urls(self):
        """Clear all seen URLs (full reset)"""
        with self._lock:
            self.seen_urls.clear()
            self.consecutive_seen = 0
            self.new_urls_count = 0
            self.skipped_urls_count = 0

        self._save_seen_urls()
        logger.info(f"{self.site_key}: Cleared all seen URLs - fresh start")


# Singleton pattern for global access
_incremental_scrapers: Dict[str, IncrementalScraper] = {}
_global_lock = Lock()


def get_incremental_scraper(site_key: str, stop_threshold: int = 10) -> IncrementalScraper:
    """
    Get or create an IncrementalScraper instance for a site.

    Uses singleton pattern to ensure one scraper per site.

    Args:
        site_key: Unique site identifier
        stop_threshold: Number of consecutive seen URLs before stopping

    Returns:
        IncrementalScraper instance for the site
    """
    with _global_lock:
        if site_key not in _incremental_scrapers:
            scraper = IncrementalScraper(site_key)
            scraper.stop_threshold = stop_threshold
            _incremental_scrapers[site_key] = scraper

        return _incremental_scrapers[site_key]


def clear_all_incremental_scrapers():
    """Clear all incremental scraper instances (useful for testing)"""
    with _global_lock:
        for scraper in _incremental_scrapers.values():
            scraper.save()
        _incremental_scrapers.clear()
