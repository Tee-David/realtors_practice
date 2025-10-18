# core/dispatcher.py
import importlib
import inspect
from typing import Any, Dict, List, Optional
from core.scraper_engine import generic_deep_crawl

def get_parser(site_key: str, site_config: Optional[Dict[str, Any]] = None):
    """
    Resolves a parser module with a scrape() function based on site config.

    Args:
        site_key: Site identifier
        site_config: Site configuration dict from config.yaml (optional for backward compatibility)

    Returns:
        ParserAdapter: Wrapped parser with uniform interface

    Parser type resolution (in order of precedence):
        1. site_config['parser'] if provided ('specials', 'generic', 'custom')
        2. Try parsers.<site_key> module
        3. Fall back to generic parser
    """
    # Get parser type from config (default to 'specials' for backward compatibility)
    parser_type = None
    if site_config:
        parser_type = site_config.get("parser", "specials")

    # Determine which module to load
    module = None

    if parser_type == "generic":
        # Generic parser - no module needed, will use generic_deep_crawl
        return ParserAdapter(site_key, None, site_config)

    elif parser_type == "custom":
        # Custom parser - try to load parsers.<site_key>
        module_name = f"parsers.{site_key}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            # Custom parser not found, fall back to generic
            pass

    else:
        # Default: 'specials' or backward compatibility
        # Try parsers.<site_key> or parsers.specials
        module_name = f"parsers.{site_key}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            # Site-specific parser not found, try specials
            try:
                module = importlib.import_module("parsers.specials")
            except Exception:
                # Even specials failed, fall back to generic
                pass

    return ParserAdapter(site_key, module, site_config)

class ParserAdapter:
    """
    Uniform interface around parser modules.
    - Attempts to call module.scrape(**kwargs) with only supported params.
    - If the module is None or call fails/returns 0, falls back to generic_deep_crawl.
    - Passes site_config to parsers that support it.
    """

    def __init__(self, site_key: str, module, site_config: Optional[Dict[str, Any]] = None):
        self.site_key = site_key
        self.module = module
        self.site_config = site_config or {}
        self.start_url = getattr(module, "START_URL", None) if module else None

    def _call_scrape_if_available(self, kwargs: Dict[str, Any]) -> List[Dict]:
        if not self.module or not hasattr(self.module, "scrape"):
            return []

        fn = getattr(self.module, "scrape")
        sig = inspect.signature(fn)

        # Add site_config to kwargs if parser supports it
        if "site_config" in sig.parameters:
            kwargs["site_config"] = self.site_config

        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}

        try:
            return fn(**allowed)
        except TypeError as e:
            # Retry without kwargs ONLY if function actually takes no required params
            try:
                if all(p.default != inspect._empty or p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL)
                       for p in sig.parameters.values()):
                    return fn()
            except Exception:
                pass
            # Reraise to trigger generic fallback
            raise e

    def scrape(self, **kwargs) -> List[Dict]:
        # 1) Try module scrape
        try:
            items = self._call_scrape_if_available(kwargs)
        except Exception:
            items = []

        # 2) If module missing or empty -> generic deep crawl
        if not items:
            start_url = kwargs.get("site", {}).get("url") or self.site_config.get("url") or getattr(self.module, "START_URL", None)
            if not start_url:
                # if absolutely no URL known, nothing we can do
                return []

            # Pass site_config to generic_deep_crawl if available
            items = generic_deep_crawl(start_url, site_config=self.site_config)

        return items
