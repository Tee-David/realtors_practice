# core/exporter.py
"""
Exporter for Realtors Practice.

- Saves listings to CSV and XLSX under exports/<site>/
- Skips export if there are 0 listings
- Filenames: YYYY-MM-DD_HH-MM-SS_<sitename>.csv|.xlsx
- Core columns enforced; extra fields are ignored (but won't break export)
- Quality filtering: Only exports listings meeting minimum quality threshold
"""

import os
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

import openpyxl

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"

# Keep these aligned with cleaner.normalize_listing() output
CORE_COLUMNS = [
    "title",
    "price",
    "price_per_sqm",
    "price_per_bedroom",
    "location",
    "estate_name",
    "property_type",
    "bedrooms",
    "bathrooms",
    "toilets",
    "bq",
    "land_size",
    "title_tag",
    "description",
    "promo_tags",
    "initial_deposit",
    "payment_plan",
    "service_charge",
    "launch_timeline",
    "agent_name",
    "contact_info",
    "images",            # will serialize as comma-separated URLs
    "listing_url",
    "source",
    "scrape_timestamp",
    "coordinates",       # will serialize as "lat,lng"
    "hash"
]

def _ensure_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def _serialize_cell(value):
    """Make complex fields csv/xlsx-friendly."""
    if isinstance(value, dict) and "lat" in value and "lng" in value:
        return f"{value.get('lat')},{value.get('lng')}"
    if isinstance(value, (list, tuple)):
        # images list, amenities, etc.
        return ", ".join([str(v) for v in value if v is not None])
    return value if value is not None else ""


def _filter_by_quality(
    site: str,
    listings: List[Dict[str, Any]],
    min_quality_score: float = 40.0  # Quality threshold - reject low quality listings
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Filter listings by quality score and return stats.

    Args:
        site: Site identifier (for logging)
        listings: List of listings to filter
        min_quality_score: Minimum quality score (0-100)

    Returns:
        Tuple of (filtered_listings, quality_stats)
    """
    from core.quality_scorer import get_quality_scorer

    if not listings:
        return listings, {}

    # Score all listings
    scorer = get_quality_scorer()
    scored_listings = scorer.score_listings_batch(listings)

    # Calculate stats before filtering
    total_count = len(scored_listings)
    avg_score = sum(l['quality_score'] for l in scored_listings) / total_count if total_count > 0 else 0

    # Filter by quality threshold
    high_quality = [
        listing for listing in scored_listings
        if listing['quality_score'] >= min_quality_score
    ]

    filtered_count = len(high_quality)
    rejected_count = total_count - filtered_count

    # Log quality filtering results
    if rejected_count > 0:
        logger.warning(
            f"{site}: Quality filter rejected {rejected_count}/{total_count} listings "
            f"(below {min_quality_score}% threshold). Avg quality: {avg_score:.1f}%"
        )
    else:
        logger.info(
            f"{site}: All {total_count} listings passed quality filter "
            f"(>= {min_quality_score}%). Avg quality: {avg_score:.1f}%"
        )

    # Return filtered listings and stats
    stats = {
        'total_scraped': total_count,
        'high_quality': filtered_count,
        'rejected': rejected_count,
        'avg_quality_score': avg_score,
        'min_threshold': min_quality_score
    }

    return high_quality, stats

def export_listings(
    site: str,
    listings: List[Dict[str, Any]],
    formats: List[str] = None,
    min_quality_score: float = None,
    site_config: Dict = None
) -> Dict[str, Any]:
    """
    Export listings for a single site into specified formats with quality filtering.

    Args:
        site: Site identifier
        listings: List of normalized listings
        formats: List of export formats ('csv', 'xlsx'). Defaults to both.
        min_quality_score: Minimum quality score (0-100). If None, uses config or default (40)
        site_config: Site configuration dict (for per-site overrides)

    Returns:
        Dict with export stats including quality metrics

    Skips writing if listings is empty.
    """
    if not listings:
        logger.info(f"{site}: skipped export (0 listings)")
        return {'exported': 0, 'rejected': 0}

    if formats is None:
        formats = ["csv", "xlsx"]

    # Determine quality threshold
    if min_quality_score is None:
        # Check site config for override, otherwise use global default (40%)
        if site_config:
            min_quality_score = site_config.get('overrides', {}).get('min_quality_score', 40.0)
        else:
            min_quality_score = float(os.getenv('RP_MIN_QUALITY', '40'))

    # Apply quality filtering
    filtered_listings, quality_stats = _filter_by_quality(site, listings, min_quality_score)

    # Skip export if all listings were filtered out
    if not filtered_listings:
        logger.warning(
            f"{site}: No listings passed quality filter "
            f"({quality_stats.get('rejected', 0)} rejected). Export skipped."
        )
        return quality_stats

    out_dir = Path("exports/sites") / site
    _ensure_folder(out_dir)

    stamp = _timestamp()
    base = out_dir / f"{stamp}_{site}"

    exported_files = []

    # --- CSV ---
    if "csv" in formats:
        csv_path = str(base) + ".csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CORE_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for row in filtered_listings:
                safe_row = {col: _serialize_cell(row.get(col)) for col in CORE_COLUMNS}
                writer.writerow(safe_row)
        exported_files.append(csv_path)

    # --- XLSX ---
    if "xlsx" in formats:
        xlsx_path = str(base) + ".xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(CORE_COLUMNS)
        for row in filtered_listings:
            ws.append([_serialize_cell(row.get(col)) for col in CORE_COLUMNS])
        wb.save(xlsx_path)
        exported_files.append(xlsx_path)

    # Log export success with quality stats
    logger.info(
        f"Exported {len(filtered_listings)} listings for {site} "
        f"(avg quality: {quality_stats.get('avg_quality_score', 0):.1f}%)"
    )

    # Return comprehensive stats
    quality_stats['exported_count'] = len(filtered_listings)
    quality_stats['exported_files'] = exported_files
    return quality_stats
