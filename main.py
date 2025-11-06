# main.py
import os
import sys
import time
import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from core.config_loader import load_config, ConfigValidationError
from core.dispatcher import get_parser
from core.cleaner import normalize_listing
from core.geo import geocode_listings
from core.exporter import export_listings
from core.utils import is_lagos_like
from core.firestore_direct import upload_listings_to_firestore

# ---------------- LOGGING SETUP (will be reconfigured after loading config) ----------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------- LOAD CONFIGURATION ----------------
try:
    logging.info("Loading configuration from config.yaml...")
    CONFIG = load_config("config.yaml")
    logging.info("Configuration loaded successfully")
except FileNotFoundError:
    logging.error("config.yaml not found. Copy config.example.yaml to config.yaml")
    sys.exit(1)
except ConfigValidationError as e:
    logging.error(f"Configuration validation failed: {e}")
    logging.error("Please fix the errors in config.yaml and try again")
    sys.exit(1)
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    sys.exit(1)

# Get global settings
GLOBAL_SETTINGS = CONFIG.get_global_settings()

# Configure logging from config
log_config = GLOBAL_SETTINGS.get("logging", {})
log_level = getattr(logging, log_config.get("level", "INFO").upper(), logging.INFO)
logging.getLogger().setLevel(log_level)

# File handler
log_file = log_config.get("file", "logs/scraper.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)

# Console handler
if log_config.get("console", True):
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(console)

# ---------------- GLOBAL SETTINGS FROM CONFIG ----------------
# Retry settings
RP_NET_RETRY_SECS = GLOBAL_SETTINGS["retry"]["network_retry_seconds"]
RP_RETRY_ON_ZERO = GLOBAL_SETTINGS["retry"]["retry_on_zero_results"]

# Fallback order
FALLBACK_ORDER = GLOBAL_SETTINGS["fallback_order"]

# Optional global search hint
GLOBAL_SEARCH = os.getenv("RP_SEARCH", "").strip()
FILTERS = {"search_query": GLOBAL_SEARCH} if GLOBAL_SEARCH else {}

# ---------------- SITE CONFIGURATION (loaded from config.yaml) ----------------
# Get enabled sites from config
ENABLED_SITES = CONFIG.get_enabled_sites()
total_sites, enabled_count = CONFIG.count_sites()
disabled_count = total_sites - enabled_count

logging.info(f"Loaded {enabled_count} enabled sites from config.yaml")
if disabled_count > 0:
    logging.warning(f"{disabled_count} sites are disabled and will be skipped")

# ---------------- SCRAPE + RETRY WRAPPER ----------------
def try_scrape_with_retry(site_key: str, site_config: Dict) -> list:
    """
    Call parser.scrape() passing the kwargs many parsers expect:
        fallback_order, filters, site, site_key
    Use a simple backoff retry for network-y failures, for up to RP_NET_RETRY_SECS.
    Optionally retry on zero results if RP_RETRY_ON_ZERO=1.
    Supports per-site overrides for retry_seconds and retry_on_zero.
    """
    from core.config_loader import get_site_setting

    parser = get_parser(site_key, site_config)
    start = time.time()
    attempt = 0

    base_url = site_config.get("url", "")
    site_name = site_config.get("name", site_key)

    # Get retry settings with per-site overrides
    retry_seconds = get_site_setting(site_config, GLOBAL_SETTINGS, "retry.network_retry_seconds", RP_NET_RETRY_SECS)
    retry_on_zero = get_site_setting(site_config, GLOBAL_SETTINGS, "retry.retry_on_zero_results", RP_RETRY_ON_ZERO)

    while True:
        attempt += 1
        try:
            raw = parser.scrape(
                fallback_order=FALLBACK_ORDER,
                filters=FILTERS,
                site={"key": site_key, "url": base_url, "name": site_name},
                site_key=site_key,
            )
            if raw and len(raw) > 0:
                return raw
            if retry_on_zero:
                elapsed = time.time() - start
                if elapsed >= retry_seconds:
                    return raw or []
                sleep_s = min(6, 1 + attempt * 0.75)
                logging.info(f"{site_key}: 0 items, retrying in {sleep_s:.1f}s (elapsed {int(elapsed)}s/{int(retry_seconds)}s)…")
                time.sleep(sleep_s)
                continue
            return raw or []
        except Exception as e:
            elapsed = time.time() - start
            if elapsed >= retry_seconds:
                logging.error(f"{site_key}: network/parser error; giving up after {int(elapsed)}s: {e}")
                return []
            sleep_s = min(10, 1 + attempt * 0.85)
            logging.info(f"{site_key}: error, retrying in {sleep_s:.1f}s (elapsed {int(elapsed)}s/{int(retry_seconds)}s)…")
            time.sleep(sleep_s)

# ---------------- METADATA TRACKING ----------------
METADATA_FILE = Path("logs/site_metadata.json")

def load_metadata() -> Dict:
    """Load site metadata (last successful scrape times, etc.)"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load metadata: {e}")
    return {}

def save_metadata(metadata: Dict) -> None:
    """Save site metadata to disk."""
    try:
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        logging.warning(f"Failed to save metadata: {e}")

def update_site_metadata(metadata: Dict, site_key: str, count: int) -> None:
    """Update metadata for a site after scraping."""
    if site_key not in metadata:
        metadata[site_key] = {}

    metadata[site_key]["last_scrape"] = datetime.now().isoformat()
    if count > 0:
        metadata[site_key]["last_successful_scrape"] = datetime.now().isoformat()
        metadata[site_key]["last_count"] = count
    metadata[site_key]["total_scrapes"] = metadata[site_key].get("total_scrapes", 0) + 1

# ---------------- HELPERS ----------------
def get_config_hash(config: Dict) -> str:
    """Generate a short hash of site config for debugging."""
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()[:8]

# ---------------- ONE SITE RUN ----------------
def run_site(site_key: str, site_config: Dict) -> Tuple[int, str]:
    base_url = site_config.get("url", "")
    if not base_url:
        logging.info(f"{site_key}: no base URL; skipping.")
        return 0, base_url

    # Log site configuration details
    parser_type = site_config.get("parser", "specials")
    has_overrides = "overrides" in site_config and len(site_config["overrides"]) > 0
    has_custom_selectors = "selectors" in site_config
    config_hash = get_config_hash(site_config)

    logging.info(f"Scraping {site_key} -> {base_url}")
    logging.debug(f"  Parser: {parser_type}, Overrides: {has_overrides}, Custom selectors: {has_custom_selectors}, Config hash: {config_hash}")

    # 1) Scrape (with retry wrapper)
    raw_items = try_scrape_with_retry(site_key, site_config)
    if not raw_items:
        logging.info(f"{site_key}: skipped export (0 listings).")
        return 0, base_url

    # 2) Normalize + Lagos filter
    cleaned = []
    for r in raw_items:
        try:
            n = normalize_listing(r, site=site_key)
        except Exception:
            continue
        # Check location, title, AND listing URL for Lagos indicators
        check_text = f"{n.get('location','')} {n.get('title','')} {n.get('listing_url','')}"
        if is_lagos_like(check_text):
            cleaned.append(n)

    if not cleaned:
        logging.info(f"{site_key}: skipped export (no Lagos listings).")
        return 0, base_url

    # 3) Geocode (check per-site override)
    from core.config_loader import get_site_setting
    geocode_enabled = get_site_setting(site_config, GLOBAL_SETTINGS, "geocoding.enabled", True)

    if geocode_enabled:
        geocoded = geocode_listings(cleaned)
    else:
        logging.info(f"{site_key}: geocoding disabled for this site")
        geocoded = cleaned

    # 4) Export (CSV/XLSX) - check per-site format preferences
    export_formats = get_site_setting(site_config, GLOBAL_SETTINGS, "export.formats", ["csv", "xlsx"])

    try:
        export_listings(site_key, geocoded, formats=export_formats)
    except Exception as e:
        logging.error(f"{site_key}: export failed: {e}")
        return 0, base_url

    # 5) Upload to Firestore (PRIMARY DATA STORE - eliminates corruption)
    try:
        firestore_stats = upload_listings_to_firestore(site_key, geocoded)
        if firestore_stats.get('uploaded', 0) > 0:
            logging.info(f"{site_key}: Uploaded {firestore_stats['uploaded']} listings to Firestore")
    except Exception as e:
        logging.warning(f"{site_key}: Firestore upload failed (non-fatal): {e}")
        # Non-fatal - Excel export still succeeded

    logging.info(f"Exported {len(geocoded)} listings for {site_key}")
    return len(geocoded), base_url

# ---------------- MAIN ----------------
def main() -> None:
    logging.info("Realtors Practice Scraper Entry\n")

    # Log config summary
    logging.info("=== CONFIGURATION SUMMARY ===")
    logging.info(f"Fallback order: {' -> '.join(FALLBACK_ORDER)}")
    logging.info(f"Geocoding: {'enabled' if GLOBAL_SETTINGS['geocoding']['enabled'] else 'disabled'} (max {GLOBAL_SETTINGS['geocoding']['max_per_run']} per run)")
    logging.info(f"Pagination: max {GLOBAL_SETTINGS['pagination']['max_pages']} pages, {GLOBAL_SETTINGS['pagination']['scroll_steps']} scroll steps")
    logging.info(f"Retry: {GLOBAL_SETTINGS['retry']['network_retry_seconds']}s timeout, retry on zero: {GLOBAL_SETTINGS['retry']['retry_on_zero_results']}")
    logging.info(f"Export formats: {', '.join(GLOBAL_SETTINGS['export']['formats'])}")
    logging.info(f"Browser: headless={GLOBAL_SETTINGS['browser']['headless']}, block_images={GLOBAL_SETTINGS['browser']['block_images']}")
    logging.info("=============================\n")

    # Load metadata
    metadata = load_metadata()

    # Prepare sites for scraping
    valid_sites = []
    skipped_sites = []

    for site_key, site_config in ENABLED_SITES.items():
        if not site_config.get("url"):
            logging.warning(f"{site_key}: No URL configured, skipping")
            skipped_sites.append(site_key)
        else:
            valid_sites.append((site_key, site_config))

    # PARALLEL SCRAPING (NEW!)
    from core.parallel_scraper import scrape_sites_parallel, get_max_workers_from_env

    # Get max workers from environment (or auto-detect)
    max_workers = get_max_workers_from_env()

    # Wrapper function for parallel scraping with error handling
    def scrape_with_error_handling(site_key: str, site_config: Dict) -> Tuple[int, str]:
        """Wrapper that catches all exceptions for parallel scraping."""
        try:
            return run_site(site_key, site_config)
        except ConfigValidationError as e:
            logging.error(f"{site_key}: Configuration error - {e}")
            return 0, site_config.get("url", "")
        except Exception as e:
            logging.error(f"{site_key}: FAILED with {e}", exc_info=True)
            return 0, site_config.get("url", "")

    # Run parallel scraping
    if valid_sites:
        summary = scrape_sites_parallel(
            sites=valid_sites,
            scrape_function=scrape_with_error_handling,
            max_workers=max_workers,
            progress_bar=True  # Enable tqdm progress bar
        )
    else:
        summary = {}

    # Add skipped sites to summary
    for site_key in skipped_sites:
        summary[site_key] = (0, "")

    # Update metadata for all sites
    for site_key, (count, url) in summary.items():
        update_site_metadata(metadata, site_key, count)

    # Save metadata
    save_metadata(metadata)

    # Final report
    logging.info("\n=== SCRAPE REPORT ===")
    success_sites = 0
    total = 0
    for site, (count, url) in summary.items():
        if count > 0:
            logging.info(f"Found {count} listings from {site} ({url})")
            success_sites += 1
            total += count

    zero_sites = [s for s, (c, _) in summary.items() if c == 0]
    if success_sites == 0:
        logging.info("No listings found.")
    else:
        logging.info(f"Successful sites: {success_sites} / {len(summary)} | Total listings: {total}")
    if zero_sites:
        logging.info(f"Zero-listing sites: {', '.join(zero_sites)}")
    if skipped_sites:
        logging.warning(f"Skipped sites due to config errors: {', '.join(skipped_sites)}")

    # AUTO-WATCHER (PHASE 5 - NEW!)
    # Automatically trigger watcher to process exports
    if os.getenv("RP_NO_AUTO_WATCHER", "0") != "1" and success_sites > 0:
        logging.info("\n=== AUTO-WATCHER ===")
        logging.info("Processing exports into master workbook...")

        try:
            from watcher import run_once, WatcherState, STATE_FILE

            watcher_state = WatcherState(STATE_FILE)
            run_once(watcher_state, dry_run=False, verbose=False)

            logging.info("Auto-watcher processing complete!")
        except Exception as e:
            logging.error(f"Auto-watcher failed: {e}")
            logging.info("You can manually run: python watcher.py --once")
    elif success_sites == 0:
        logging.info("Skipping watcher (no successful scrapes)")
    else:
        logging.info("Auto-watcher disabled (RP_NO_AUTO_WATCHER=1)")

if __name__ == "__main__":
    main()
