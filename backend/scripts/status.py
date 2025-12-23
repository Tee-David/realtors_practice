# status.py
"""
Site Health Status Tool

Shows scraping statistics and health for all sites.
Reads from logs/site_metadata.json to display:
- Last scrape attempt
- Last successful scrape
- Total scrapes
- Success rate
- Sites needing attention
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from core.config_loader import load_config


def load_site_metadata() -> Dict:
    """Load site metadata from JSON file."""
    metadata_file = Path("logs/site_metadata.json")
    if not metadata_file.exists():
        return {}

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return {}


def parse_timestamp(ts_str: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(ts_str)
    except:
        return datetime.min


def format_time_ago(ts_str: str) -> str:
    """Format timestamp as 'X hours ago' or 'X days ago'."""
    if not ts_str:
        return "Never"

    ts = parse_timestamp(ts_str)
    if ts == datetime.min:
        return "Unknown"

    delta = datetime.now() - ts
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"


def get_site_health_status(meta: Dict) -> Tuple[str, str]:
    """
    Determine site health status.

    Returns:
        (status, reason) tuple
        status: "healthy", "warning", "critical", "unknown"
    """
    if not meta:
        return ("unknown", "Never scraped")

    last_scrape = meta.get("last_scrape")
    last_success = meta.get("last_successful_scrape")
    last_count = meta.get("last_count", 0)

    if not last_scrape:
        return ("unknown", "No scrape data")

    # Check if last scrape was successful
    if last_scrape == last_success and last_count > 0:
        return ("healthy", f"{last_count} listings")

    # Check time since last success
    if last_success:
        time_since_success = datetime.now() - parse_timestamp(last_success)
        if time_since_success.days > 7:
            return ("critical", f"No success for {time_since_success.days}d")
        elif time_since_success.days > 3:
            return ("warning", f"No success for {time_since_success.days}d")

    # Last scrape failed
    return ("warning", "Last scrape failed (0 listings)")


def main():
    """Display site health status."""
    print("=" * 90)
    print("SITE HEALTH STATUS")
    print("=" * 90)

    # Load config and metadata
    try:
        config = load_config("config.yaml")
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    metadata = load_site_metadata()

    all_sites = config.get_all_sites()
    enabled_sites = config.get_enabled_sites()

    # Categorize sites
    healthy_sites = []
    warning_sites = []
    critical_sites = []
    unknown_sites = []

    for site_key in enabled_sites.keys():
        meta = metadata.get(site_key, {})
        status, reason = get_site_health_status(meta)

        site_info = (site_key, meta, reason)

        if status == "healthy":
            healthy_sites.append(site_info)
        elif status == "warning":
            warning_sites.append(site_info)
        elif status == "critical":
            critical_sites.append(site_info)
        else:
            unknown_sites.append(site_info)

    # Display summary
    print(f"\n[SUMMARY]")
    print(f"  Total sites: {len(all_sites)}")
    print(f"  Enabled: {len(enabled_sites)}")
    print(f"  Disabled: {len(all_sites) - len(enabled_sites)}")
    print()
    print(f"  [OK] Healthy: {len(healthy_sites)}")
    print(f"  [WARN] Warning: {len(warning_sites)}")
    print(f"  [CRITICAL] Critical: {len(critical_sites)}")
    print(f"  [UNKNOWN] Unknown: {len(unknown_sites)}")

    # Display critical sites (need immediate attention)
    if critical_sites:
        print(f"\n[CRITICAL SITES] (need attention)")
        print(f"{'Site':<20} {'Last Success':<15} {'Reason':<30}")
        print("-" * 65)
        for site_key, meta, reason in critical_sites:
            last_success = format_time_ago(meta.get("last_successful_scrape", ""))
            print(f"{site_key:<20} {last_success:<15} {reason:<30}")

    # Display warning sites
    if warning_sites:
        print(f"\n[WARNING SITES]")
        print(f"{'Site':<20} {'Last Scrape':<15} {'Reason':<30}")
        print("-" * 65)
        for site_key, meta, reason in warning_sites:
            last_scrape = format_time_ago(meta.get("last_scrape", ""))
            print(f"{site_key:<20} {last_scrape:<15} {reason:<30}")

    # Display healthy sites (summary)
    if healthy_sites:
        print(f"\n[HEALTHY SITES] ({len(healthy_sites)} total)")
        # Show first 10
        for site_key, meta, reason in healthy_sites[:10]:
            last_scrape = format_time_ago(meta.get("last_scrape", ""))
            print(f"  {site_key:<20} {last_scrape:<15} {reason:<30}")
        if len(healthy_sites) > 10:
            print(f"  ... and {len(healthy_sites) - 10} more")

    # Display unknown sites (never scraped)
    if unknown_sites:
        print(f"\n[UNKNOWN SITES] (never scraped)")
        for site_key, meta, reason in unknown_sites[:10]:
            print(f"  {site_key}")
        if len(unknown_sites) > 10:
            print(f"  ... and {len(unknown_sites) - 10} more")

    # Top performers
    if metadata:
        print(f"\n[TOP PERFORMERS] (by last count)")
        sorted_sites = sorted(
            [(k, v) for k, v in metadata.items() if k in enabled_sites and v.get("last_count", 0) > 0],
            key=lambda x: x[1].get("last_count", 0),
            reverse=True
        )[:10]

        for site_key, meta in sorted_sites:
            count = meta.get("last_count", 0)
            last_scrape = format_time_ago(meta.get("last_scrape", ""))
            print(f"  {site_key:<20} {count:>4} listings ({last_scrape})")

    # Most active (by total scrapes)
    if metadata:
        print(f"\n[MOST ACTIVE] (by total scrapes)")
        sorted_sites = sorted(
            [(k, v) for k, v in metadata.items() if k in enabled_sites],
            key=lambda x: x[1].get("total_scrapes", 0),
            reverse=True
        )[:10]

        for site_key, meta in sorted_sites:
            total = meta.get("total_scrapes", 0)
            print(f"  {site_key:<20} {total:>4} scrapes")

    print("\n" + "=" * 90)
    print(f"Status as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)


if __name__ == "__main__":
    main()
