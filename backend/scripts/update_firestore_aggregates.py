"""
scripts/update_firestore_aggregates.py

Background job to update cached Firestore aggregates.
Run this after scraping to refresh dashboard statistics and summary views.

Usage:
    python scripts/update_firestore_aggregates.py

    # Or with specific environment
    FIREBASE_SERVICE_ACCOUNT="path/to/creds.json" python scripts/update_firestore_aggregates.py
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_dashboard_aggregate():
    """Update dashboard statistics aggregate"""
    from core.firestore_queries import get_dashboard_stats

    logger.info("Updating dashboard aggregate...")
    stats = get_dashboard_stats()

    if stats:
        logger.info(f"Dashboard updated: {stats.get('total_properties', 0)} properties, {stats.get('total_sites', 0)} sites")
        return True
    else:
        logger.error("Failed to update dashboard aggregate")
        return False


def update_top_deals_aggregate(limit=100):
    """Update top 100 cheapest properties aggregate"""
    from core.firestore_queries import get_cheapest_properties
    from core.firestore_direct import _get_firestore_client

    logger.info(f"Updating top {limit} cheapest properties aggregate...")

    db = _get_firestore_client()
    if db is None:
        logger.error("Firestore not available")
        return False

    try:
        # Get top deals
        properties = get_cheapest_properties(limit=limit)

        if not properties:
            logger.warning("No properties found for top deals")
            return False

        # Cache to aggregates collection
        from google.cloud.firestore import SERVER_TIMESTAMP
        aggregates_ref = db.collection('aggregates').document('top_deals')
        aggregates_ref.set({
            'properties': properties,
            'count': len(properties),
            'updated_at': SERVER_TIMESTAMP
        }, merge=True)

        logger.info(f"Top deals updated: {len(properties)} properties")
        return True

    except Exception as e:
        logger.error(f"Failed to update top deals: {e}")
        return False


def update_newest_listings_aggregate(limit=50, days_back=7):
    """Update newest listings aggregate"""
    from core.firestore_queries import get_newest_listings
    from core.firestore_direct import _get_firestore_client

    logger.info(f"Updating newest {limit} listings (last {days_back} days)...")

    db = _get_firestore_client()
    if db is None:
        logger.error("Firestore not available")
        return False

    try:
        # Get newest listings
        properties = get_newest_listings(limit=limit, days_back=days_back)

        if not properties:
            logger.warning("No recent properties found")
            return False

        # Cache to aggregates collection
        from google.cloud.firestore import SERVER_TIMESTAMP
        aggregates_ref = db.collection('aggregates').document('newest_listings')
        aggregates_ref.set({
            'properties': properties,
            'count': len(properties),
            'days_back': days_back,
            'updated_at': SERVER_TIMESTAMP
        }, merge=True)

        logger.info(f"Newest listings updated: {len(properties)} properties")
        return True

    except Exception as e:
        logger.error(f"Failed to update newest listings: {e}")
        return False


def update_site_metadata_aggregates():
    """Update per-site metadata aggregates"""
    from core.firestore_direct import _get_firestore_client

    logger.info("Updating site metadata aggregates...")

    db = _get_firestore_client()
    if db is None:
        logger.error("Firestore not available")
        return False

    try:
        # Get all unique sites
        properties = db.collection('properties').stream()
        sites = set()

        for doc in properties:
            site_key = doc.to_dict().get('site_key')
            if site_key:
                sites.add(site_key)

        logger.info(f"Found {len(sites)} sites to update")

        # Update metadata for each site
        from core.firestore_queries import get_site_statistics

        for site_key in sites:
            try:
                stats = get_site_statistics(site_key)
                logger.info(f"  {site_key}: {stats.get('total_properties', 0)} properties")
            except Exception as e:
                logger.warning(f"  Failed to update {site_key}: {e}")

        return True

    except Exception as e:
        logger.error(f"Failed to update site metadata: {e}")
        return False


def update_all_aggregates():
    """Update all cached aggregates"""
    logger.info("="*60)
    logger.info("UPDATING ALL FIRESTORE AGGREGATES")
    logger.info("="*60)

    results = {}

    # Update dashboard
    results['dashboard'] = update_dashboard_aggregate()

    # Update top deals
    results['top_deals'] = update_top_deals_aggregate(limit=100)

    # Update newest listings
    results['newest_listings'] = update_newest_listings_aggregate(limit=50, days_back=7)

    # Update site metadata
    results['site_metadata'] = update_site_metadata_aggregates()

    # Summary
    logger.info("="*60)
    logger.info("AGGREGATE UPDATE SUMMARY")
    logger.info("="*60)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for name, success in results.items():
        status = "[SUCCESS]" if success else "[FAILED]"
        logger.info(f"{status} {name}")

    logger.info("="*60)
    logger.info(f"Completed: {success_count}/{total_count} successful")
    logger.info("="*60)

    return all(results.values())


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Update Firestore aggregates')
    parser.add_argument('--dashboard-only', action='store_true', help='Update only dashboard stats')
    parser.add_argument('--top-deals-only', action='store_true', help='Update only top deals')
    parser.add_argument('--newest-only', action='store_true', help='Update only newest listings')
    parser.add_argument('--site-metadata-only', action='store_true', help='Update only site metadata')
    parser.add_argument('--all', action='store_true', help='Update all aggregates (default)')

    args = parser.parse_args()

    # Check if Firestore is enabled
    firestore_enabled = os.getenv('FIRESTORE_ENABLED', '1') == '1'
    if not firestore_enabled:
        logger.error("FIRESTORE_ENABLED is not set to 1. Exiting.")
        logger.error("Set FIRESTORE_ENABLED=1 to enable Firestore operations.")
        sys.exit(1)

    # Check for Firebase credentials
    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if not cred_path:
        logger.error("FIREBASE_SERVICE_ACCOUNT environment variable not set")
        logger.error("Set it to your Firebase service account JSON file path")
        sys.exit(1)

    if not Path(cred_path).exists():
        logger.error(f"Firebase credentials file not found: {cred_path}")
        sys.exit(1)

    logger.info(f"Using Firebase credentials: {cred_path}")

    # Run requested updates
    success = False

    if args.dashboard_only:
        success = update_dashboard_aggregate()
    elif args.top_deals_only:
        success = update_top_deals_aggregate()
    elif args.newest_only:
        success = update_newest_listings_aggregate()
    elif args.site_metadata_only:
        success = update_site_metadata_aggregates()
    else:
        # Default: update all
        success = update_all_aggregates()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
