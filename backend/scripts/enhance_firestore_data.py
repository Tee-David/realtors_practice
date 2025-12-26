"""
Enhance Firestore Data Quality Script

Uses the data_quality_enhancer module to:
1. Detect and remove category pages
2. Enhance property titles using NLP
3. Extract amenities from descriptions
4. Validate bedroom/bathroom counts
5. Calculate quality scores
6. Update Firestore with enhanced data

Usage:
    python scripts/enhance_firestore_data.py --preview  # Preview changes only
    python scripts/enhance_firestore_data.py --apply    # Apply changes to Firestore

Author: Claude Sonnet 4.5
Date: 2025-12-25
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Firestore client
try:
    from core.firestore_enterprise import FirestoreEnterpriseClient
    FIRESTORE_AVAILABLE = True
except ImportError:
    logging.error("Could not import FirestoreEnterpriseClient")
    FIRESTORE_AVAILABLE = False

# Import data quality enhancer
try:
    from core.data_quality_enhancer import (
        enhance_property_data,
        batch_enhance_properties,
        is_category_page
    )
    ENHANCER_AVAILABLE = True
except ImportError:
    logging.error("Could not import data_quality_enhancer")
    ENHANCER_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_all_properties(firestore_client: FirestoreEnterpriseClient) -> List[Dict]:
    """
    Load all properties from Firestore.

    Args:
        firestore_client: Firestore client instance

    Returns:
        List of property dictionaries
    """
    logger.info("Loading all properties from Firestore...")

    try:
        # Get reference to properties collection
        properties_ref = firestore_client.db.collection('properties')

        # Stream all documents
        all_properties = []
        for doc in properties_ref.stream():
            prop_data = doc.to_dict()
            prop_data['_firestore_id'] = doc.id  # Store document ID
            all_properties.append(prop_data)

        logger.info(f"Loaded {len(all_properties)} properties from Firestore")
        return all_properties

    except Exception as e:
        logger.error(f"Error loading properties: {e}")
        return []


def preview_enhancements(properties: List[Dict]) -> Dict[str, Any]:
    """
    Preview what enhancements would be made without applying them.

    Args:
        properties: List of property dictionaries

    Returns:
        Dictionary with preview statistics
    """
    logger.info("Previewing enhancements...")

    results = batch_enhance_properties(properties, validate_only=False)

    # Print summary
    print("\n" + "=" * 80)
    print("ENHANCEMENT PREVIEW")
    print("=" * 80)
    print(f"\nTotal properties analyzed: {results['total_processed']}")
    print(f"Category pages detected: {results['total_category_pages']}")
    print(f"Properties to enhance: {results['total_enhanced']}")
    print(f"Total changes to make: {results['total_changes']}")
    print(f"Average quality score: {results['average_quality_score']}/100")

    # Show category pages
    if results['category_pages']:
        print("\n" + "-" * 80)
        print("CATEGORY PAGES TO DELETE:")
        print("-" * 80)
        for i, cat_page in enumerate(results['category_pages'][:10], 1):  # Show first 10
            prop = cat_page['property']
            reason = cat_page['reason']
            title = prop.get('basic_info', {}).get('title', 'No title')
            url = prop.get('basic_info', {}).get('url', 'No URL')
            print(f"\n{i}. {title}")
            print(f"   URL: {url}")
            print(f"   Reason: {reason}")

        if len(results['category_pages']) > 10:
            print(f"\n... and {len(results['category_pages']) - 10} more category pages")

    # Show sample enhancements
    if results['enhanced_properties']:
        print("\n" + "-" * 80)
        print("SAMPLE ENHANCEMENTS (first 5 properties):")
        print("-" * 80)

        for i, enhanced_prop in enumerate(results['enhanced_properties'][:5], 1):
            # Re-run enhancer to get changes
            original_prop = properties[i - 1]  # Approximate
            enhancement_result = enhance_property_data(original_prop)

            if enhancement_result['changes_made']:
                title = enhanced_prop.get('basic_info', {}).get('title', 'No title')
                print(f"\n{i}. {title}")
                print(f"   Quality Score: {enhancement_result['quality_score']}/100")
                print("   Changes:")
                for change in enhancement_result['changes_made']:
                    print(f"     - {change}")

    print("\n" + "=" * 80)
    print("Preview complete. Use --apply to apply these changes.")
    print("=" * 80)

    return results


def apply_enhancements(firestore_client: FirestoreEnterpriseClient,
                      properties: List[Dict],
                      delete_category_pages: bool = True) -> Dict[str, Any]:
    """
    Apply enhancements to Firestore database.

    Args:
        firestore_client: Firestore client instance
        properties: List of property dictionaries
        delete_category_pages: Whether to delete detected category pages

    Returns:
        Dictionary with application statistics
    """
    logger.info("Applying enhancements to Firestore...")

    results = batch_enhance_properties(properties, validate_only=False)

    stats = {
        'updated': 0,
        'deleted': 0,
        'errors': 0,
        'skipped': 0
    }

    # Step 1: Delete category pages
    if delete_category_pages and results['category_pages']:
        logger.info(f"Deleting {len(results['category_pages'])} category pages...")

        for cat_page_info in results['category_pages']:
            try:
                cat_page = cat_page_info['property']
                doc_id = cat_page.get('_firestore_id')

                if doc_id:
                    firestore_client.db.collection('properties').document(doc_id).delete()
                    stats['deleted'] += 1
                    logger.info(f"Deleted category page: {cat_page.get('basic_info', {}).get('title', 'No title')}")
                else:
                    logger.warning("Category page missing Firestore ID, skipping deletion")
                    stats['skipped'] += 1

            except Exception as e:
                logger.error(f"Error deleting category page: {e}")
                stats['errors'] += 1

    # Step 2: Update enhanced properties
    logger.info(f"Updating {len(results['enhanced_properties'])} enhanced properties...")

    for enhanced_prop in results['enhanced_properties']:
        try:
            doc_id = enhanced_prop.get('_firestore_id')

            if not doc_id:
                logger.warning("Enhanced property missing Firestore ID, skipping update")
                stats['skipped'] += 1
                continue

            # Remove internal _firestore_id before saving
            update_data = {k: v for k, v in enhanced_prop.items() if k != '_firestore_id'}

            # Update document
            firestore_client.db.collection('properties').document(doc_id).set(update_data, merge=True)
            stats['updated'] += 1

            if stats['updated'] % 50 == 0:
                logger.info(f"Updated {stats['updated']} properties so far...")

        except Exception as e:
            logger.error(f"Error updating property: {e}")
            stats['errors'] += 1

    # Print results
    print("\n" + "=" * 80)
    print("ENHANCEMENT COMPLETE")
    print("=" * 80)
    print(f"\nProperties updated: {stats['updated']}")
    print(f"Category pages deleted: {stats['deleted']}")
    print(f"Errors encountered: {stats['errors']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"\nAverage quality score: {results['average_quality_score']}/100")
    print("=" * 80)

    return stats


def generate_report(properties: List[Dict],
                   results: Dict[str, Any],
                   output_file: str = "enhancement_report.json"):
    """
    Generate detailed enhancement report as JSON.

    Args:
        properties: Original properties
        results: Enhancement results
        output_file: Output file path
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_properties': len(properties),
            'total_category_pages': results['total_category_pages'],
            'total_enhanced': results['total_enhanced'],
            'total_changes': results['total_changes'],
            'average_quality_score': results['average_quality_score']
        },
        'category_pages': [
            {
                'title': cat['property'].get('basic_info', {}).get('title'),
                'url': cat['property'].get('basic_info', {}).get('url'),
                'reason': cat['reason']
            }
            for cat in results['category_pages']
        ]
    }

    # Write report
    report_path = Path(__file__).parent.parent / output_file
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report generated: {report_path}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Enhance Firestore data quality")
    parser.add_argument('--preview', action='store_true',
                       help='Preview changes without applying them')
    parser.add_argument('--apply', action='store_true',
                       help='Apply changes to Firestore')
    parser.add_argument('--keep-category-pages', action='store_true',
                       help='Keep category pages instead of deleting them')
    parser.add_argument('--report', type=str, default='enhancement_report.json',
                       help='Output report filename')

    args = parser.parse_args()

    # Validate arguments
    if not args.preview and not args.apply:
        parser.error("Must specify either --preview or --apply")

    # Check dependencies
    if not FIRESTORE_AVAILABLE:
        logger.error("Firestore client not available. Cannot proceed.")
        sys.exit(1)

    if not ENHANCER_AVAILABLE:
        logger.error("Data quality enhancer not available. Cannot proceed.")
        sys.exit(1)

    # Initialize Firestore client
    logger.info("Initializing Firestore client...")
    try:
        firestore_client = FirestoreEnterpriseClient()
        logger.info("Firestore client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firestore client: {e}")
        sys.exit(1)

    # Load all properties
    properties = load_all_properties(firestore_client)

    if not properties:
        logger.error("No properties found in Firestore. Exiting.")
        sys.exit(1)

    # Execute based on mode
    if args.preview:
        results = preview_enhancements(properties)
        generate_report(properties, results, args.report)

    elif args.apply:
        # Confirm before applying
        print("\n" + "=" * 80)
        print("WARNING: This will modify your Firestore database!")
        print("=" * 80)
        response = input("\nAre you sure you want to apply these changes? (yes/no): ")

        if response.lower() != 'yes':
            print("Operation cancelled.")
            sys.exit(0)

        # First preview
        results = preview_enhancements(properties)
        generate_report(properties, results, args.report)

        # Then apply
        delete_categories = not args.keep_category_pages
        apply_stats = apply_enhancements(firestore_client, properties, delete_categories)

        logger.info("Enhancement complete!")


if __name__ == '__main__':
    main()
