"""
core/rate_limiter.py

Rate limiting and robots.txt compliance module.

Features:
- Per-domain request delay tracking
- robots.txt parsing and enforcement
- Configurable minimum delays between requests
- Respects Crawl-delay directive in robots.txt
- Thread-safe for parallel scraping

Usage:
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter(min_delay=1.0)  # 1 second minimum delay

    # Check if URL can be fetched (robots.txt)
    if limiter.can_fetch("https://example.com/page", user_agent="MyBot"):
        # Wait if needed to respect rate limit
        limiter.wait_if_needed("example.com")

        # Make request...
        response = fetch(url)

        # Record request time
        limiter.record_request("example.com")
"""

import time
import logging
import os
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from threading import Lock
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"


class RateLimiter:
    """
    Rate limiter with robots.txt compliance.

    Tracks request timestamps per domain and enforces:
    1. Minimum delay between requests to same domain
    2. robots.txt rules (can_fetch, crawl_delay)
    3. Thread-safe operation for parallel scraping
    """

    def __init__(self, min_delay: float = 1.0, respect_robots: bool = True, user_agent: str = "RealtorsPracticeBot/1.0"):
        """
        Initialize rate limiter.

        Args:
            min_delay: Minimum seconds between requests to same domain (default: 1.0)
            respect_robots: Whether to check robots.txt (default: True)
            user_agent: User agent string for robots.txt checks
        """
        self.min_delay = min_delay
        self.respect_robots = respect_robots
        self.user_agent = user_agent

        # Per-domain tracking
        self.last_request_times: Dict[str, float] = {}
        self.robots_parsers: Dict[str, Optional[RobotFileParser]] = {}
        self.crawl_delays: Dict[str, float] = {}

        # Thread safety
        self.lock = Lock()

        if RP_DEBUG:
            logger.debug(f"RateLimiter initialized: min_delay={min_delay}s, respect_robots={respect_robots}")

    def get_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain (e.g., "example.com")
        """
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def get_robots_txt_url(self, url: str) -> str:
        """
        Get robots.txt URL for given URL.

        Args:
            url: Full URL

        Returns:
            robots.txt URL (e.g., "https://example.com/robots.txt")
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def load_robots_txt(self, url: str) -> Optional[RobotFileParser]:
        """
        Load and parse robots.txt for a domain.

        Args:
            url: Full URL to determine domain

        Returns:
            RobotFileParser instance or None if failed
        """
        domain = self.get_domain(url)

        # Check cache first
        with self.lock:
            if domain in self.robots_parsers:
                return self.robots_parsers[domain]

        # Load robots.txt
        robots_url = self.get_robots_txt_url(url)
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            # Try to fetch robots.txt
            parser.read()

            # Check for Crawl-delay directive
            crawl_delay = parser.crawl_delay(self.user_agent)
            if crawl_delay:
                with self.lock:
                    self.crawl_delays[domain] = float(crawl_delay)
                if RP_DEBUG:
                    logger.debug(f"{domain}: Found Crawl-delay: {crawl_delay}s in robots.txt")

            with self.lock:
                self.robots_parsers[domain] = parser

            logger.info(f"{domain}: Loaded robots.txt from {robots_url}")
            return parser

        except Exception as e:
            # Failed to load robots.txt - allow crawling by default
            if RP_DEBUG:
                logger.debug(f"{domain}: Failed to load robots.txt: {e} - allowing crawling")

            with self.lock:
                self.robots_parsers[domain] = None

            return None

    def can_fetch(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check
            user_agent: User agent (default: instance user_agent)

        Returns:
            True if URL can be fetched, False otherwise
        """
        if not self.respect_robots:
            return True

        user_agent = user_agent or self.user_agent
        domain = self.get_domain(url)

        # Load robots.txt if not cached
        parser = self.robots_parsers.get(domain)
        if parser is None and domain not in self.robots_parsers:
            parser = self.load_robots_txt(url)

        # No robots.txt or failed to load - allow
        if parser is None:
            return True

        # Check if URL is allowed
        try:
            allowed = parser.can_fetch(user_agent, url)
            if not allowed and RP_DEBUG:
                logger.debug(f"{domain}: URL blocked by robots.txt: {url}")
            return allowed
        except Exception as e:
            logger.warning(f"{domain}: Error checking robots.txt: {e}")
            return True  # Allow on error

    def get_delay_for_domain(self, domain: str) -> float:
        """
        Get the delay to use for a domain.

        Returns max of:
        - min_delay (configured minimum)
        - crawl_delay from robots.txt (if present)

        Args:
            domain: Domain name

        Returns:
            Delay in seconds
        """
        crawl_delay = self.crawl_delays.get(domain, 0)
        return max(self.min_delay, crawl_delay)

    def wait_if_needed(self, domain: str) -> float:
        """
        Wait if needed to respect rate limit for domain.

        Args:
            domain: Domain to check

        Returns:
            Time waited in seconds (0 if no wait needed)
        """
        with self.lock:
            last_time = self.last_request_times.get(domain, 0)
            delay = self.get_delay_for_domain(domain)

        current_time = time.time()
        elapsed = current_time - last_time

        if elapsed < delay:
            wait_time = delay - elapsed
            if RP_DEBUG:
                logger.debug(f"{domain}: Rate limit - waiting {wait_time:.2f}s (delay={delay}s)")
            time.sleep(wait_time)
            return wait_time

        return 0.0

    def record_request(self, domain: str):
        """
        Record that a request was made to domain.

        Args:
            domain: Domain that was requested
        """
        with self.lock:
            self.last_request_times[domain] = time.time()

    def check_and_wait(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Convenience method: check robots.txt and wait if needed.

        Args:
            url: URL to fetch
            user_agent: User agent (optional)

        Returns:
            True if request should proceed, False if blocked by robots.txt
        """
        # Check robots.txt
        if not self.can_fetch(url, user_agent):
            return False

        # Wait if needed
        domain = self.get_domain(url)
        self.wait_if_needed(domain)

        return True

    def get_stats(self) -> dict:
        """
        Get statistics about rate limiter state.

        Returns:
            Dict with stats (domains tracked, robots.txt loaded, etc.)
        """
        with self.lock:
            return {
                "domains_tracked": len(self.last_request_times),
                "robots_txt_loaded": len([p for p in self.robots_parsers.values() if p is not None]),
                "crawl_delays": dict(self.crawl_delays),
                "min_delay": self.min_delay,
                "respect_robots": self.respect_robots,
            }


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None
_limiter_lock = Lock()


def get_rate_limiter(min_delay: Optional[float] = None, respect_robots: Optional[bool] = None) -> RateLimiter:
    """
    Get global rate limiter instance (singleton).

    Creates instance on first call. Subsequent calls return the same instance.

    Args:
        min_delay: Minimum delay between requests (only used on first call)
        respect_robots: Whether to respect robots.txt (only used on first call)

    Returns:
        Global RateLimiter instance
    """
    global _global_limiter

    with _limiter_lock:
        if _global_limiter is None:
            # Read from environment if not specified
            if min_delay is None:
                min_delay = float(os.getenv("RP_RATE_LIMIT_DELAY", "1.0"))
            if respect_robots is None:
                respect_robots = os.getenv("RP_RESPECT_ROBOTS", "1") == "1"

            _global_limiter = RateLimiter(min_delay=min_delay, respect_robots=respect_robots)

        return _global_limiter


def reset_rate_limiter():
    """
    Reset global rate limiter (useful for testing).
    """
    global _global_limiter
    with _limiter_lock:
        _global_limiter = None
