# core/parallel_scraper.py
"""
Parallel Site Scraping Module

Scrapes multiple sites concurrently using ThreadPoolExecutor.
Resource-aware and GitHub Actions safe!

Features:
- Dynamic worker allocation based on site count
- Resource monitoring (memory, CPU)
- Progress tracking with tqdm
- Error isolation (one site failure doesn't stop others)
- Configurable max workers via RP_SITE_WORKERS
"""

import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Callable, Optional
from pathlib import Path

# Optional dependencies
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


def calculate_workers(site_count: int, max_workers: Optional[int] = None) -> int:
    """
    Calculate safe number of workers based on site count and system resources.

    Strategy (Balanced - GitHub Actions safe):
    - 1-5 sites: 2 workers
    - 6-15 sites: 3 workers
    - 16+ sites: 4 workers
    - Never exceed cpu_count or user-specified max

    Args:
        site_count: Number of sites to scrape
        max_workers: User-specified maximum (overrides calculation)

    Returns:
        Number of workers to use
    """
    if max_workers and max_workers > 0:
        # User explicitly set max workers
        return max_workers

    # Auto-detect based on site count (Balanced approach)
    if site_count <= 5:
        calculated = 2
    elif site_count <= 15:
        calculated = 3
    else:
        calculated = 4

    # Cap at CPU count
    cpu_count = os.cpu_count() or 2
    calculated = min(calculated, cpu_count)

    # GitHub Actions safety: never exceed 4 workers
    calculated = min(calculated, 4)

    logger.info(f"Parallel scraping: {site_count} sites, {calculated} workers")
    return calculated


def check_resource_usage() -> Dict[str, float]:
    """
    Check current system resource usage.

    Returns:
        Dict with memory_percent and cpu_percent (if psutil available)
    """
    if not HAS_PSUTIL:
        return {"memory_percent": 0.0, "cpu_percent": 0.0}

    try:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        return {
            "memory_percent": mem.percent,
            "cpu_percent": cpu
        }
    except Exception as e:
        logger.debug(f"Failed to check resources: {e}")
        return {"memory_percent": 0.0, "cpu_percent": 0.0}


def log_resource_warning():
    """Log warning if resources are running high."""
    if not HAS_PSUTIL:
        return

    resources = check_resource_usage()

    if resources["memory_percent"] > 80:
        logger.warning(f"High memory usage: {resources['memory_percent']:.1f}%")

    if resources["cpu_percent"] > 90:
        logger.warning(f"High CPU usage: {resources['cpu_percent']:.1f}%")


def scrape_sites_parallel(
    sites: List[Tuple[str, Dict]],
    scrape_function: Callable[[str, Dict], Tuple[int, str]],
    max_workers: Optional[int] = None,
    progress_bar: bool = True
) -> Dict[str, Tuple[int, str]]:
    """
    Scrape multiple sites in parallel using ThreadPoolExecutor.

    Args:
        sites: List of (site_key, site_config) tuples
        scrape_function: Function to call for each site: (site_key, site_config) -> (count, url)
        max_workers: Override automatic worker calculation
        progress_bar: Show progress bar (requires tqdm)

    Returns:
        Dict mapping site_key to (count, url) results
    """
    if not sites:
        logger.info("No sites to scrape")
        return {}

    # Calculate optimal worker count
    workers = calculate_workers(len(sites), max_workers)

    # Log initial resources
    resources = check_resource_usage()
    logger.debug(f"Starting parallel scraping - Memory: {resources['memory_percent']:.1f}%, CPU: {resources['cpu_percent']:.1f}%")

    results = {}
    start_time = time.time()

    # Use ThreadPoolExecutor for parallel scraping
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="scraper") as executor:
        # Submit all site scraping tasks
        future_to_site = {
            executor.submit(scrape_function, site_key, site_config): site_key
            for site_key, site_config in sites
        }

        # Process results as they complete
        if progress_bar and HAS_TQDM:
            # With progress bar
            with tqdm(total=len(sites), desc="Scraping sites", unit="site") as pbar:
                for future in as_completed(future_to_site):
                    site_key = future_to_site[future]
                    try:
                        count, url = future.result()
                        results[site_key] = (count, url)
                        pbar.set_postfix({"last": site_key, "count": count}, refresh=True)
                    except Exception as e:
                        logger.error(f"Parallel scraping failed for {site_key}: {e}")
                        results[site_key] = (0, "")
                    finally:
                        pbar.update(1)

                        # Log resource warnings periodically
                        if len(results) % 5 == 0:
                            log_resource_warning()
        else:
            # Without progress bar
            for i, future in enumerate(as_completed(future_to_site), 1):
                site_key = future_to_site[future]
                try:
                    count, url = future.result()
                    results[site_key] = (count, url)
                    logger.info(f"Progress: {i}/{len(sites)} sites complete - {site_key}: {count} listings")
                except Exception as e:
                    logger.error(f"Parallel scraping failed for {site_key}: {e}")
                    results[site_key] = (0, "")

                # Log resource warnings periodically
                if i % 5 == 0:
                    log_resource_warning()

    # Log final stats
    elapsed = time.time() - start_time
    total_listings = sum(count for count, _ in results.values())
    successful = sum(1 for count, _ in results.values() if count > 0)

    final_resources = check_resource_usage()
    logger.info(f"Parallel scraping complete: {len(sites)} sites in {elapsed:.1f}s ({successful} successful, {total_listings} total listings)")
    logger.debug(f"Final resources - Memory: {final_resources['memory_percent']:.1f}%, CPU: {final_resources['cpu_percent']:.1f}%")

    return results


def get_max_workers_from_env() -> Optional[int]:
    """
    Get max workers from RP_SITE_WORKERS environment variable.

    Returns:
        Number of workers, or None for auto-detect
    """
    env_value = os.getenv("RP_SITE_WORKERS", "").strip().lower()

    if not env_value or env_value == "auto":
        return None  # Auto-detect

    try:
        workers = int(env_value)
        if workers < 1:
            logger.warning(f"Invalid RP_SITE_WORKERS={env_value}, using auto-detect")
            return None
        if workers > 8:
            logger.warning(f"RP_SITE_WORKERS={workers} is very high, capping at 8")
            return 8
        return workers
    except ValueError:
        logger.warning(f"Invalid RP_SITE_WORKERS={env_value}, using auto-detect")
        return None
