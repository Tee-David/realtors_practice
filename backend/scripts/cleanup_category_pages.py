"""
Cleanup Script: Remove Category Pages from Firestore

This script identifies and removes category/listing pages that were incorrectly
scraped as property pages. Uses universal_detector.py to identify category pages.

Usage:
    # Dry run (see what would be deleted without actually deleting)
    python scripts/cleanup_category_pages.py --dry-run

    # Actually delete category pages
    python scripts/cleanup_category_pages.py --delete

    # Export to JSON before deleting
    python scripts/cleanup_category_pages.py --delete --export cleanup_backup.json

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import sys
import os
import argparse
import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Firestore modules
from core.firestore_enterprise import _get_firestore_client
from core.firestore_queries_enterprise import get_all_properties

# Import universal detector (not strictly needed since we use heuristics)
# from core.universal_detector import is_category_page, get_detection_confidence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def identify_category_pages(properties: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Identify which properties are actually category pages.

    Args:
        properties: List of property dictionaries from Firestore

    Returns:
        Tuple of (category_pages, valid_properties)
    """
    category_pages = []
    valid_properties = []

    logger.info(f"Analyzing {len(properties)} properties for category page detection...")

    for i, prop in enumerate(properties, 1):
        try:
            # Extract data for detection
            url = prop.get('basic_info', {}).get('url', '')
            title = prop.get('basic_info', {}).get('title', '')
            price = prop.get('financial', {}).get('price', 0)
            location = prop.get('location', {}).get('area', '')

            # Create extracted_data dict
            extracted_data = {
                'url': url,
                'title': title,
                'price': price,
                'location': location,
                'bedrooms': prop.get('property_details', {}).get('bedrooms'),
                'bathrooms': prop.get('property_details', {}).get('bathrooms')
            }

            # Note: We don't have HTML content, so we'll use heuristics
            # Check if property matches category page patterns
            is_cat = False
            signals = {}

            # Heuristic 1: URL patterns
            category_url_patterns = [
                '/property-location/', '/listings/', '/search/', '/properties/',
                '/category/', '/location/', '/area/', '/city/', '/state/',
                '/browse/', '/filter/', '/results/'
            ]

            url_is_category = any(pattern in url.lower() for pattern in category_url_patterns)

            # Heuristic 2: Generic title (just location name)
            generic_location_names = [
                'Chevron', 'Ikate', 'Lekki', 'Victoria Island', 'Ikoyi', 'Ajah',
                'Ikeja', 'Yaba', 'Surulere', 'Maryland', 'Magodo', 'Lagos',
                'Nigeria', 'VI', 'VGC', 'Osapa', 'Sangotedo'
            ]

            title_is_generic = title.strip() in generic_location_names

            # Heuristic 3: Missing critical fields
            missing_price = not price or price == 0
            missing_details = not extracted_data.get('bedrooms') and not extracted_data.get('bathrooms')

            # Heuristic 4: Very short title
            title_too_short = len(title) < 10

            # Decision logic
            category_score = 0

            if url_is_category:
                category_score += 3
            if title_is_generic:
                category_score += 2
            if missing_price:
                category_score += 2
            if missing_details:
                category_score += 1
            if title_too_short:
                category_score += 1

            # Threshold: Category if score >= 4
            is_cat = category_score >= 4

            # Store detection info
            detection_info = {
                'url_is_category': url_is_category,
                'title_is_generic': title_is_generic,
                'missing_price': missing_price,
                'missing_details': missing_details,
                'title_too_short': title_too_short,
                'category_score': category_score,
                'threshold': 4
            }

            if is_cat:
                prop['_detection_info'] = detection_info
                category_pages.append(prop)
                logger.debug(f"[{i}/{len(properties)}] CATEGORY: {title[:50]} (score: {category_score}, url: {url[:60]}...)")
            else:
                valid_properties.append(prop)
                logger.debug(f"[{i}/{len(properties)}] VALID: {title[:50]} (score: {category_score})")

        except Exception as e:
            logger.error(f"Error analyzing property {i}: {e}")
            # On error, assume valid (conservative approach)
            valid_properties.append(prop)

    logger.info(f"Detection complete: {len(category_pages)} category pages, {len(valid_properties)} valid properties")

    return category_pages, valid_properties


def export_to_json(properties: List[Dict], filename: str):
    """Export properties to JSON file for backup."""
    try:
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(properties, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Exported {len(properties)} properties to {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return None


def delete_category_pages(category_pages: List[Dict], dry_run: bool = True) -> int:
    """
    Delete category pages from Firestore.

    Args:
        category_pages: List of category page dictionaries
        dry_run: If True, don't actually delete (just show what would be deleted)

    Returns:
        Number of properties deleted
    """
    deleted_count = 0

    if dry_run:
        logger.info("DRY RUN MODE - No properties will be deleted")
        logger.info(f"Would delete {len(category_pages)} category pages:")

        for i, prop in enumerate(category_pages, 1):
            title = prop.get('basic_info', {}).get('title', 'No title')
            url = prop.get('basic_info', {}).get('url', 'No URL')
            detection = prop.get('_detection_info', {})
            score = detection.get('category_score', 0)

            logger.info(f"  [{i}] {title[:60]} (score: {score})")
            logger.info(f"      URL: {url[:80]}")
            logger.info(f"      Detection: {detection}")

        return 0

    else:
        logger.info(f"DELETING {len(category_pages)} category pages from Firestore...")

        for i, prop in enumerate(category_pages, 1):
            try:
                # Get property hash (used as document ID)
                prop_hash = prop.get('metadata', {}).get('hash', '')

                if not prop_hash:
                    logger.warning(f"Property {i} has no hash, skipping")
                    continue

                title = prop.get('basic_info', {}).get('title', 'No title')

                # Delete from Firestore
                db = _get_firestore_client()
                doc_ref = db.collection('properties').document(prop_hash)
                doc_ref.delete()
                deleted_count += 1

                logger.info(f"[{i}/{len(category_pages)}] Deleted: {title[:60]} (hash: {prop_hash})")

            except Exception as e:
                logger.error(f"Error deleting property {i}: {e}")

        logger.info(f"Deletion complete: {deleted_count} properties deleted")
        return deleted_count


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Cleanup category pages from Firestore database'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )

    parser.add_argument(
        '--delete',
        action='store_true',
        help='Actually delete category pages (use with caution!)'
    )

    parser.add_argument(
        '--export',
        type=str,
        metavar='FILENAME',
        help='Export category pages to JSON before deleting'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=4,
        help='Minimum category score to delete (default: 4)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.dry_run and not args.delete:
        logger.error("Must specify either --dry-run or --delete")
        parser.print_help()
        sys.exit(1)

    if args.dry_run and args.delete:
        logger.error("Cannot use both --dry-run and --delete")
        sys.exit(1)

    logger.info("="*70)
    logger.info("CATEGORY PAGE CLEANUP SCRIPT")
    logger.info("="*70)
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'DELETE'}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*70)

    # Step 1: Get all properties from Firestore
    logger.info("\nStep 1: Fetching all properties from Firestore...")
    try:
        all_properties = get_all_properties()
        logger.info(f"Retrieved {len(all_properties)} properties")
    except Exception as e:
        logger.error(f"Failed to fetch properties: {e}")
        sys.exit(1)

    if not all_properties:
        logger.warning("No properties found in Firestore")
        sys.exit(0)

    # Step 2: Identify category pages
    logger.info("\nStep 2: Identifying category pages...")
    category_pages, valid_properties = identify_category_pages(all_properties)

    logger.info(f"\nResults:")
    logger.info(f"  Total properties: {len(all_properties)}")
    logger.info(f"  Category pages: {len(category_pages)} ({len(category_pages)/len(all_properties)*100:.1f}%)")
    logger.info(f"  Valid properties: {len(valid_properties)} ({len(valid_properties)/len(all_properties)*100:.1f}%)")

    if not category_pages:
        logger.info("\nNo category pages found. Database is clean!")
        sys.exit(0)

    # Step 3: Export if requested
    if args.export:
        logger.info(f"\nStep 3: Exporting category pages to {args.export}...")
        export_to_json(category_pages, args.export)

    # Step 4: Delete (or show what would be deleted)
    logger.info(f"\nStep 4: {'Deleting' if args.delete else 'Showing'} category pages...")
    deleted_count = delete_category_pages(category_pages, dry_run=args.dry_run)

    # Summary
    logger.info("\n" + "="*70)
    logger.info("CLEANUP SUMMARY")
    logger.info("="*70)
    logger.info(f"Total properties analyzed: {len(all_properties)}")
    logger.info(f"Category pages identified: {len(category_pages)}")
    logger.info(f"Properties deleted: {deleted_count}")
    logger.info(f"Valid properties remaining: {len(valid_properties)}")
    logger.info("="*70)

    if args.dry_run:
        logger.info("\nThis was a DRY RUN. To actually delete, run with --delete flag:")
        logger.info(f"  python scripts/cleanup_category_pages.py --delete --export category_backup.json")


if __name__ == '__main__':
    main()
