#!/usr/bin/env python3
"""
Query Properties CLI Tool

Command-line interface for querying property listings using the advanced query engine.

Usage:
    # Search by price range
    python scripts/query_properties.py --price-min 5000000 --price-max 50000000

    # Search by bedrooms
    python scripts/query_properties.py --bedrooms-min 3 --bedrooms-max 5

    # Search by location
    python scripts/query_properties.py --location "Lekki"

    # Combined filters
    python scripts/query_properties.py --price-max 30000000 --bedrooms 3 --location "Ikoyi"

    # Text search
    python scripts/query_properties.py --search "luxury apartment"

    # Sort results
    python scripts/query_properties.py --price-max 20000000 --sort-by price

    # Limit results
    python scripts/query_properties.py --location "VI" --limit 20

    # Get summary stats
    python scripts/query_properties.py --location "Lekki" --summary
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query_engine import PropertyQuery


def format_price(price):
    """Format price with commas and Naira symbol."""
    try:
        return f"N{float(price):,.0f}"
    except:
        return str(price)


def display_results(results, limit=None):
    """Display query results in a readable format."""
    if not results:
        print("\nNo results found.")
        return

    total = len(results)
    display_count = min(limit or total, total)

    print(f"\n{'='*80}")
    print(f"FOUND {total} PROPERTIES")
    if limit and total > limit:
        print(f"Showing first {display_count} results")
    print(f"{'='*80}\n")

    for i, prop in enumerate(results[:display_count], 1):
        print(f"{i}. {prop.get('title', 'No title')}")
        print(f"   Price: {format_price(prop.get('price', 'N/A'))}")
        print(f"   Location: {prop.get('location', 'N/A')}")

        bedrooms = prop.get('bedrooms', 'N/A')
        bathrooms = prop.get('bathrooms', 'N/A')
        prop_type = prop.get('property_type', 'N/A')

        print(f"   Type: {prop_type} | Beds: {bedrooms} | Baths: {bathrooms}")
        print(f"   Source: {prop.get('source', 'N/A')}")
        print(f"   URL: {prop.get('listing_url', 'N/A')}")
        print()


def display_summary(summary):
    """Display summary statistics."""
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")

    print(f"Total Results: {summary['total_results']}")

    if summary.get('filters_applied'):
        print(f"\nFilters Applied:")
        for filter_desc in summary['filters_applied']:
            print(f"  - {filter_desc}")

    if 'price_stats' in summary:
        stats = summary['price_stats']
        print(f"\nPrice Statistics:")
        print(f"  Min: {format_price(stats['min'])}")
        print(f"  Max: {format_price(stats['max'])}")
        print(f"  Mean: {format_price(stats['mean'])}")
        print(f"  Median: {format_price(stats['median'])}")

    if 'bedrooms_stats' in summary:
        stats = summary['bedrooms_stats']
        print(f"\nBedroom Statistics:")
        print(f"  Min: {stats['min']}")
        print(f"  Max: {stats['max']}")
        print(f"  Mean: {stats['mean']:.1f}")

    if 'property_types' in summary:
        print(f"\nProperty Types:")
        for prop_type, count in list(summary['property_types'].items())[:10]:
            print(f"  {prop_type}: {count}")

    if 'sources' in summary:
        print(f"\nSources:")
        for source, count in summary['sources'].items():
            print(f"  {source}: {count}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Query property listings with advanced filters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input file
    parser.add_argument(
        '--file',
        default='exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx',
        help='Path to Excel/CSV file (default: exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx)'
    )
    parser.add_argument(
        '--sheet',
        help='Excel sheet name (default: first sheet)'
    )

    # Price filters
    parser.add_argument('--price-min', type=float, help='Minimum price')
    parser.add_argument('--price-max', type=float, help='Maximum price')

    # Bedroom filters
    parser.add_argument('--bedrooms', type=int, help='Exact number of bedrooms')
    parser.add_argument('--bedrooms-min', type=int, help='Minimum bedrooms')
    parser.add_argument('--bedrooms-max', type=int, help='Maximum bedrooms')

    # Bathroom filters
    parser.add_argument('--bathrooms', type=int, help='Exact number of bathrooms')
    parser.add_argument('--bathrooms-min', type=int, help='Minimum bathrooms')
    parser.add_argument('--bathrooms-max', type=int, help='Maximum bathrooms')

    # Location and type
    parser.add_argument('--location', help='Location search (partial match)')
    parser.add_argument('--property-type', help='Property type (partial match)')
    parser.add_argument('--source', help='Source site name')

    # Text search
    parser.add_argument('--search', help='Search text in title, location, property type')

    # Sorting and pagination
    parser.add_argument('--sort-by', help='Sort by field (e.g., price, bedrooms)')
    parser.add_argument('--sort-desc', action='store_true', help='Sort in descending order')
    parser.add_argument('--limit', type=int, help='Limit number of results')
    parser.add_argument('--offset', type=int, default=0, help='Skip N results (pagination)')

    # Output options
    parser.add_argument('--summary', action='store_true', help='Show summary statistics only')
    parser.add_argument('--count', action='store_true', help='Show count only')

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.file).exists():
        print(f"[ERROR] File not found: {args.file}")
        print("\nPlease run the scraper first to generate data files.")
        sys.exit(1)

    # Load data
    print(f"Loading data from {args.file}...")
    try:
        if args.file.endswith('.csv'):
            query = PropertyQuery.from_csv(args.file)
        else:
            query = PropertyQuery.from_excel(args.file, sheet_name=args.sheet)
    except Exception as e:
        print(f"[ERROR] Failed to load file: {e}")
        sys.exit(1)

    # Build query
    filter_params = {}

    if args.price_min is not None:
        filter_params['price_min'] = args.price_min
    if args.price_max is not None:
        filter_params['price_max'] = args.price_max

    if args.bedrooms is not None:
        filter_params['bedrooms'] = args.bedrooms
    if args.bedrooms_min is not None:
        filter_params['bedrooms_min'] = args.bedrooms_min
    if args.bedrooms_max is not None:
        filter_params['bedrooms_max'] = args.bedrooms_max

    if args.bathrooms is not None:
        filter_params['bathrooms'] = args.bathrooms
    if args.bathrooms_min is not None:
        filter_params['bathrooms_min'] = args.bathrooms_min
    if args.bathrooms_max is not None:
        filter_params['bathrooms_max'] = args.bathrooms_max

    if args.location:
        filter_params['location'] = args.location
    if args.property_type:
        filter_params['property_type'] = args.property_type
    if args.source:
        filter_params['source'] = args.source

    # Apply filters
    if filter_params:
        query.filter(**filter_params)

    # Apply search
    if args.search:
        query.search(args.search)

    # Apply sorting
    if args.sort_by:
        query.sort_by(args.sort_by, ascending=not args.sort_desc)

    # Apply pagination
    if args.limit:
        query.limit(args.limit, offset=args.offset)

    # Output results
    if args.count:
        print(f"\nTotal Results: {query.count()}")
    elif args.summary:
        summary = query.get_summary()
        display_summary(summary)
    else:
        results = query.execute()
        display_results(results, limit=50)  # Show max 50 in CLI

        # Show summary if many results
        if len(results) > 50:
            print(f"[Note] Showing first 50 of {len(results)} results. Use --limit to see more.")


if __name__ == "__main__":
    main()
