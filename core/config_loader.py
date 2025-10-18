# core/config_loader.py
"""
Configuration loader and validator for Realtors Practice.

Loads config.yaml and validates structure, provides defaults, and merges
environment variable overrides.

Usage:
    from core.config_loader import load_config, ConfigValidationError

    try:
        config = load_config("config.yaml")
        sites = config.get_enabled_sites()
        global_settings = config.get_global_settings()
    except ConfigValidationError as e:
        print(f"Invalid configuration: {e}")
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from datetime import datetime

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required. Install with: pip install pyyaml")


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Config:
    """
    Configuration container with validation and environment variable override support.
    """

    # Default values for global settings
    DEFAULTS = {
        "fallback_order": ["requests", "playwright"],
        "geocoding": {
            "enabled": True,
            "max_per_run": 120,
            "user_agent": "RealtorsPractice/1.0 (+contact: you@example.com)",
            "cache_path": "logs/geocache.json",
        },
        "pagination": {
            "max_pages": 30,
            "scroll_steps": 12,
            "page_timeout_ms": 45000,
        },
        "retry": {
            "network_retry_seconds": 180,
            "retry_on_zero_results": False,
        },
        "browser": {
            "headless": True,
            "block_images": False,
            "user_data_dir": None,
        },
        "export": {
            "formats": ["csv", "xlsx"],
            "output_dir": "exports",
            "timestamp_format": "%Y-%m-%d_%H-%M-%S",
        },
        "logging": {
            "level": "INFO",
            "file": "logs/scraper.log",
            "console": True,
        },
        "location_filters": {
            "enabled": True,
            "include_keywords": ["lagos", "lekki", "ikeja", "ajah", "ikoyi", "victoria island", "vi"],
            "exclude_keywords": [],
        },
        "deduplication": {
            "enabled": True,
            "fields": ["title", "price", "location"],
            "cross_site": False,
        },
        "rate_limiting": {
            "enabled": False,
            "requests_per_minute": 60,
            "delay_between_sites_seconds": 2,
        },
        "notifications": {
            "enabled": False,
            "email": None,
            "slack_webhook": None,
            "on_failure": True,
            "on_success": False,
        },
    }

    # Required fields for each site
    SITE_REQUIRED_FIELDS = ["name", "url", "enabled"]

    def __init__(self, config_dict: Dict[str, Any], config_path: str = "config.yaml"):
        """
        Initialize configuration.

        Args:
            config_dict: Raw configuration dictionary from YAML
            config_path: Path to config file (for error messages)
        """
        self.config_path = config_path
        self.raw_config = config_dict
        self._sites = config_dict.get("sites", {})
        self._global_settings = self._merge_with_defaults(config_dict)
        self._apply_env_overrides()

    def _merge_with_defaults(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults (user config takes precedence)."""
        merged = {}
        for key, default_value in self.DEFAULTS.items():
            user_value = config_dict.get(key)
            if isinstance(default_value, dict) and isinstance(user_value, dict):
                # Deep merge for nested dicts
                merged[key] = {**default_value, **user_value}
            elif user_value is not None:
                merged[key] = user_value
            else:
                merged[key] = default_value
        return merged

    def _apply_env_overrides(self):
        """Apply environment variable overrides (env vars take highest precedence)."""
        # Fallback order
        if os.getenv("RP_FALLBACK"):
            self._global_settings["fallback_order"] = [
                s.strip() for s in os.getenv("RP_FALLBACK").split(",") if s.strip()
            ]

        # Geocoding
        if os.getenv("RP_GEOCODE") is not None:
            self._global_settings["geocoding"]["enabled"] = os.getenv("RP_GEOCODE") != "0"
        if os.getenv("RP_MAX_GEOCODES"):
            self._global_settings["geocoding"]["max_per_run"] = int(os.getenv("RP_MAX_GEOCODES"))
        if os.getenv("NOMINATIM_UA"):
            self._global_settings["geocoding"]["user_agent"] = os.getenv("NOMINATIM_UA")

        # Pagination
        if os.getenv("RP_PAGE_CAP"):
            self._global_settings["pagination"]["max_pages"] = int(os.getenv("RP_PAGE_CAP"))
        if os.getenv("RP_SCROLL_STEPS"):
            self._global_settings["pagination"]["scroll_steps"] = int(os.getenv("RP_SCROLL_STEPS"))

        # Retry
        if os.getenv("RP_NET_RETRY_SECS"):
            self._global_settings["retry"]["network_retry_seconds"] = int(os.getenv("RP_NET_RETRY_SECS"))
        if os.getenv("RP_RETRY_ON_ZERO"):
            self._global_settings["retry"]["retry_on_zero_results"] = os.getenv("RP_RETRY_ON_ZERO") == "1"

        # Browser
        if os.getenv("RP_HEADLESS") is not None:
            self._global_settings["browser"]["headless"] = os.getenv("RP_HEADLESS") != "0"
        if os.getenv("RP_NO_IMAGES"):
            self._global_settings["browser"]["block_images"] = os.getenv("RP_NO_IMAGES") == "1"

        # Debug/logging
        if os.getenv("RP_DEBUG"):
            if os.getenv("RP_DEBUG") == "1":
                self._global_settings["logging"]["level"] = "DEBUG"

    def get_global_settings(self) -> Dict[str, Any]:
        """Get all global settings with environment overrides applied."""
        return self._global_settings

    def get_enabled_sites(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled sites."""
        return {
            key: site_config
            for key, site_config in self._sites.items()
            if site_config.get("enabled", False)
        }

    def get_all_sites(self) -> Dict[str, Dict[str, Any]]:
        """Get all sites (enabled and disabled)."""
        return self._sites

    def get_site_config(self, site_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific site."""
        return self._sites.get(site_key)

    def count_sites(self) -> tuple[int, int]:
        """Return (total_sites, enabled_sites) counts."""
        total = len(self._sites)
        enabled = len(self.get_enabled_sites())
        return total, enabled


def _validate_url(url: str, site_key: str) -> None:
    """
    Validate URL format.

    Args:
        url: URL to validate
        site_key: Site key (for error messages)

    Raises:
        ConfigValidationError: If URL is invalid
    """
    if not url:
        raise ConfigValidationError(f"Site '{site_key}': URL is empty")

    parsed = urlparse(url)
    if not parsed.scheme in ("http", "https"):
        raise ConfigValidationError(
            f"Site '{site_key}': Invalid URL scheme '{parsed.scheme}' (must be http or https)"
        )
    if not parsed.netloc:
        raise ConfigValidationError(f"Site '{site_key}': URL missing domain")


def _validate_site(site_key: str, site_config: Dict[str, Any]) -> None:
    """
    Validate a single site configuration.

    Args:
        site_key: Site identifier
        site_config: Site configuration dict

    Raises:
        ConfigValidationError: If site config is invalid
    """
    # Check required fields
    for field in Config.SITE_REQUIRED_FIELDS:
        if field not in site_config:
            raise ConfigValidationError(
                f"Site '{site_key}': Missing required field '{field}'"
            )

    # Validate URL
    _validate_url(site_config["url"], site_key)

    # Validate enabled flag is boolean
    if not isinstance(site_config["enabled"], bool):
        raise ConfigValidationError(
            f"Site '{site_key}': 'enabled' must be true or false, got '{site_config['enabled']}'"
        )

    # Validate parser field if present
    if "parser" in site_config:
        valid_parsers = ["specials", "generic", "custom"]
        parser = site_config["parser"]
        if parser not in valid_parsers:
            logging.warning(
                f"Site '{site_key}': Unknown parser type '{parser}' "
                f"(valid options: {', '.join(valid_parsers)})"
            )

        # For custom parsers, verify the module can be imported
        if parser == "custom":
            try:
                import importlib
                importlib.import_module(f"parsers.{site_key}")
            except ImportError:
                raise ConfigValidationError(
                    f"Site '{site_key}': parser='custom' but module 'parsers.{site_key}' not found. "
                    f"Create parsers/{site_key}.py or use parser='specials' or 'generic'"
                )

    # Validate selectors if present
    if "selectors" in site_config:
        if not isinstance(site_config["selectors"], dict):
            raise ConfigValidationError(
                f"Site '{site_key}': 'selectors' must be a dictionary"
            )

    # Validate overrides if present
    if "overrides" in site_config:
        overrides = site_config["overrides"]
        if not isinstance(overrides, dict):
            raise ConfigValidationError(
                f"Site '{site_key}': 'overrides' must be a dictionary"
            )

        # Validate numeric overrides
        for key in ["max_pages", "scroll_steps", "retry_seconds"]:
            if key in overrides:
                try:
                    val = int(overrides[key])
                    if val < 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ConfigValidationError(
                        f"Site '{site_key}': overrides.{key} must be a positive integer"
                    )


def _validate_global_settings(config_dict: Dict[str, Any]) -> None:
    """
    Validate global settings.

    Args:
        config_dict: Raw configuration dictionary

    Raises:
        ConfigValidationError: If global settings are invalid
    """
    # Validate fallback_order
    if "fallback_order" in config_dict:
        fallback = config_dict["fallback_order"]
        if not isinstance(fallback, list):
            raise ConfigValidationError("'fallback_order' must be a list")
        valid_options = ["requests", "playwright", "scraperapi"]
        for option in fallback:
            if option not in valid_options:
                raise ConfigValidationError(
                    f"Invalid fallback option '{option}' (valid: {', '.join(valid_options)})"
                )

    # Validate geocoding settings
    if "geocoding" in config_dict:
        geo = config_dict["geocoding"]
        if "max_per_run" in geo:
            try:
                val = int(geo["max_per_run"])
                if val < 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ConfigValidationError("geocoding.max_per_run must be a positive integer")

    # Validate pagination settings
    if "pagination" in config_dict:
        pag = config_dict["pagination"]
        for key in ["max_pages", "scroll_steps", "page_timeout_ms"]:
            if key in pag:
                try:
                    val = int(pag[key])
                    if val < 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ConfigValidationError(f"pagination.{key} must be a positive integer")


def validate_config(config_dict: Dict[str, Any]) -> None:
    """
    Validate entire configuration.

    Args:
        config_dict: Raw configuration dictionary

    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Validate global settings
    _validate_global_settings(config_dict)

    # Validate sites section exists
    if "sites" not in config_dict:
        raise ConfigValidationError("Configuration missing 'sites' section")

    sites = config_dict["sites"]
    if not isinstance(sites, dict):
        raise ConfigValidationError("'sites' must be a dictionary")

    if len(sites) == 0:
        logging.warning("No sites defined in configuration")

    # Validate each site
    for site_key, site_config in sites.items():
        if not isinstance(site_config, dict):
            raise ConfigValidationError(f"Site '{site_key}': Configuration must be a dictionary")
        _validate_site(site_key, site_config)


# Config cache for performance: {config_path: (Config, mtime)}
_config_cache: Dict[str, tuple] = {}


def load_config(config_path: str = "config.yaml", use_cache: bool = True) -> Config:
    """
    Load and validate configuration from YAML file with optional caching.

    Args:
        config_path: Path to config.yaml file
        use_cache: Use cached config if file hasn't changed (default: True)

    Returns:
        Config: Validated configuration object

    Raises:
        ConfigValidationError: If configuration is invalid
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    path = Path(config_path)

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Copy config.example.yaml to config.yaml to get started."
        )

    # Check cache if enabled
    if use_cache and config_path in _config_cache:
        cached_config, cached_mtime = _config_cache[config_path]
        current_mtime = path.stat().st_mtime

        # Return cached config if file hasn't changed
        if cached_mtime == current_mtime:
            logging.debug(f"Using cached configuration for {config_path}")
            return cached_config

    # Load YAML
    try:
        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigValidationError(f"YAML parsing error in {config_path}: {e}")

    if config_dict is None:
        raise ConfigValidationError(f"Configuration file is empty: {config_path}")

    if not isinstance(config_dict, dict):
        raise ConfigValidationError(f"Configuration must be a dictionary, got {type(config_dict)}")

    # Validate structure
    validate_config(config_dict)

    # Create Config object
    config = Config(config_dict, config_path)

    # Cache config with modification time
    if use_cache:
        mtime = path.stat().st_mtime
        _config_cache[config_path] = (config, mtime)
        logging.debug(f"Cached configuration for {config_path}")

    # Log summary
    total, enabled = config.count_sites()
    logging.info(f"Loaded configuration from {config_path}: {enabled}/{total} sites enabled")

    return config


def clear_config_cache() -> None:
    """Clear the configuration cache. Useful for forcing reload."""
    global _config_cache
    _config_cache.clear()
    logging.debug("Configuration cache cleared")


def get_site_setting(
    site_config: Dict[str, Any],
    global_settings: Dict[str, Any],
    setting_path: str,
    default: Any = None
) -> Any:
    """
    Get a setting for a site, checking site overrides first, then global settings, then default.

    Args:
        site_config: Site-specific configuration
        global_settings: Global settings
        setting_path: Dot-separated path to setting (e.g., "pagination.max_pages")
        default: Default value if not found

    Returns:
        Setting value

    Example:
        max_pages = get_site_setting(
            site_cfg, global_cfg, "pagination.max_pages", default=30
        )
    """
    # Check site overrides first
    if "overrides" in site_config:
        # Handle dot-separated paths
        keys = setting_path.split(".")
        # Try short form in overrides (e.g., "max_pages" instead of "pagination.max_pages")
        short_key = keys[-1]
        if short_key in site_config["overrides"]:
            return site_config["overrides"][short_key]

    # Check global settings
    keys = setting_path.split(".")
    value = global_settings
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Test loading config
    try:
        config = load_config("config.example.yaml")
        print(f"\n[OK] Config loaded successfully!")
        print(f"   Sites: {config.count_sites()}")
        print(f"   Enabled sites: {len(config.get_enabled_sites())}")
        print(f"   Fallback order: {config.get_global_settings()['fallback_order']}")

        # Test getting a specific site
        npc = config.get_site_config("npc")
        if npc:
            print(f"\n[OK] NPC site config:")
            print(f"   Name: {npc['name']}")
            print(f"   URL: {npc['url']}")
            print(f"   Enabled: {npc['enabled']}")

    except ConfigValidationError as e:
        print(f"\n[ERROR] Configuration validation failed:")
        print(f"   {e}")
    except FileNotFoundError as e:
        print(f"\n[ERROR] File not found:")
        print(f"   {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error:")
        print(f"   {e}")
