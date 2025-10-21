# core/dispatcher.py
"""
100% Adaptive Scraper Dispatcher

Always uses specials.py parser with intelligent scraping.
No site-specific parser files needed - fully config-driven!

The scraper adapts to ANY website via:
  1. Config.yaml selectors (if provided)
  2. Intelligent selector discovery (auto-detect)
  3. Heuristic relevance filtering (eliminate false positives)
"""
import inspect
from typing import Any, Dict, List, Optional
from core.scraper_engine import generic_deep_crawl

def get_parser(site_key: str, site_config: Optional[Dict[str, Any]] = None):
    """
    Get parser for ANY website - 100% adaptive scraping.

    Args:
        site_key: Site identifier (e.g., 'npc', 'jiji', 'newsite')
        site_config: Site configuration dict from config.yaml

    Returns:
        ParserAdapter: Wrapped parser with uniform interface

    Note:
        No site-specific parser files needed! The scraper adapts via:
        - Custom selectors in config.yaml (optional)
        - Auto-selector discovery (intelligent scraper)
        - Relevance-based filtering
    """
    # Always use specials.py - it's 100% adaptive!
    try:
        import parsers.specials as specials_module
        return ParserAdapter(site_key, specials_module, site_config)
    except Exception:
        # Fallback to generic deep crawl if specials.py somehow missing
        return ParserAdapter(site_key, None, site_config)


class ParserAdapter:
    """
    Uniform interface around parser modules.

    - Calls module.scrape(**kwargs) with only supported params
    - Passes site_config for intelligent scraping
    - Falls back to generic_deep_crawl if needed
    """

    def __init__(self, site_key: str, module, site_config: Optional[Dict[str, Any]] = None):
        self.site_key = site_key
        self.module = module
        self.site_config = site_config or {}
        self.start_url = getattr(module, "START_URL", None) if module else None

    def _call_scrape_if_available(self, kwargs: Dict[str, Any]) -> List[Dict]:
        """Call module.scrape() with supported parameters only."""
        if not self.module or not hasattr(self.module, "scrape"):
            return []

        fn = getattr(self.module, "scrape")
        sig = inspect.signature(fn)

        # Always pass site_config for intelligent scraping
        if "site_config" in sig.parameters:
            kwargs["site_config"] = self.site_config

        # Filter kwargs to only include supported parameters
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}

        try:
            return fn(**allowed)
        except TypeError as e:
            # Retry without kwargs ONLY if function takes no required params
            try:
                if all(p.default != inspect._empty or p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL)
                       for p in sig.parameters.values()):
                    return fn()
            except Exception:
                pass
            # Reraise to trigger generic fallback
            raise e

    def scrape(self, **kwargs) -> List[Dict]:
        """
        Main scraping entry point.

        1. Try module scrape (specials.py with intelligent scraping)
        2. Fall back to generic deep crawl if needed
        """
        # 1) Try module scrape (specials.py)
        try:
            items = self._call_scrape_if_available(kwargs)
        except Exception:
            items = []

        # 2) If module missing or empty -> generic deep crawl
        if not items:
            start_url = (
                kwargs.get("site", {}).get("url") or
                self.site_config.get("url") or
                getattr(self.module, "START_URL", None)
            )
            if not start_url:
                # No URL available, nothing we can do
                return []

            # Pass site_config to generic_deep_crawl for intelligent scraping
            items = generic_deep_crawl(start_url, site_config=self.site_config)

        return items
