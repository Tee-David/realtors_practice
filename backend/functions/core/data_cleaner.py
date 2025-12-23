# core/data_cleaner.py
"""
Data Cleaning and Normalization Module

Handles:
- File ingestion (CSV, XLSX with multiple encodings)
- Intelligent field mapping (fuzzy column matching)
- Data normalization (price, location, property_type)
- Schema validation
- Deduplication
"""

import logging
import csv
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import pandas as pd
from difflib import SequenceMatcher

# Canonical schema for cleaned data
CANONICAL_SCHEMA = [
    'title', 'price', 'price_per_sqm', 'price_per_bedroom',
    'location', 'estate_name', 'property_type',
    'bedrooms', 'bathrooms', 'toilets', 'bq', 'land_size',
    'title_tag', 'description', 'promo_tags',
    'initial_deposit', 'payment_plan', 'service_charge', 'launch_timeline',
    'agent_name', 'contact_info', 'images',
    'listing_url', 'source', 'scrape_timestamp', 'coordinates', 'hash'
]

# Column name variations (for fuzzy matching)
COLUMN_ALIASES = {
    'title': ['name', 'property_name', 'heading', 'property_title'],
    'price': ['cost', 'amount', 'property_price', 'asking_price'],
    'location': ['address', 'area', 'region', 'place', 'city'],
    'property_type': ['type', 'category', 'property_category'],
    'bedrooms': ['beds', 'bedroom', 'bed', 'num_bedrooms'],
    'bathrooms': ['baths', 'bathroom', 'bath', 'num_bathrooms'],
    'listing_url': ['url', 'link', 'property_url'],
    'source': ['site', 'website', 'origin'],
}


def fuzzy_match_column(column_name: str, target_names: List[str]) -> Optional[str]:
    """
    Fuzzy match a column name against target canonical names.

    Returns best matching canonical name or None.
    """
    column_lower = column_name.lower().strip()

    # Exact match first
    if column_lower in target_names:
        return column_lower

    # Check aliases
    for canonical, aliases in COLUMN_ALIASES.items():
        if column_lower in [canonical] + aliases:
            return canonical

    # Fuzzy match (similarity > 0.8)
    best_match = None
    best_score = 0.8

    for target in target_names:
        score = SequenceMatcher(None, column_lower, target).ratio()
        if score > best_score:
            best_score = score
            best_match = target

    return best_match


def read_csv_file(file_path: Path) -> List[Dict]:
    """
    Read CSV file with encoding detection and error handling.
    """
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
            logging.debug(f"Successfully read {file_path} with {encoding} encoding")
            return df.to_dict('records')
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logging.error(f"Error reading CSV {file_path} with {encoding}: {e}")
            continue

    logging.error(f"Failed to read {file_path} with any encoding")
    return []


def read_xlsx_file(file_path: Path) -> List[Dict]:
    """
    Read XLSX file (first sheet only).
    """
    try:
        df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        logging.debug(f"Successfully read {file_path}")
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error reading XLSX {file_path}: {e}")
        return []


def ingest_file(file_path: Path) -> List[Dict]:
    """
    Ingest file (CSV or XLSX) and return list of records.
    """
    suffix = file_path.suffix.lower()

    if suffix == '.csv':
        return read_csv_file(file_path)
    elif suffix == '.xlsx':
        return read_xlsx_file(file_path)
    else:
        logging.warning(f"Unsupported file type: {suffix}")
        return []


def normalize_column_names(record: Dict) -> Dict:
    """
    Normalize column names to canonical schema using fuzzy matching.
    """
    normalized = {}

    for original_key, value in record.items():
        # Try fuzzy match to canonical schema
        canonical_key = fuzzy_match_column(str(original_key), CANONICAL_SCHEMA)

        if canonical_key:
            # Use canonical name
            normalized[canonical_key] = value
        else:
            # Keep original key if no match (will be filtered later)
            normalized[str(original_key).lower().strip()] = value

    return normalized


def normalize_price(price_str: Any) -> Optional[str]:
    """
    Normalize price format.

    Handles:
    - Currency symbols (₦, N, NGN)
    - Thousands separators (commas)
    - Abbreviations (million, m, k)
    - Ranges (e.g., "5M - 10M" -> "5000000")
    """
    if pd.isna(price_str) or price_str == '':
        return None

    price_str = str(price_str).upper().strip()

    # Remove currency symbols and common prefixes
    price_str = re.sub(r'[₦N£$€]|NGN|NAIRA', '', price_str, flags=re.IGNORECASE)
    price_str = price_str.strip()

    # Handle ranges (take first value)
    if '-' in price_str or 'TO' in price_str:
        price_str = re.split(r'[-–TO]', price_str)[0].strip()

    # Remove commas
    price_str = price_str.replace(',', '')

    # Handle abbreviations
    multiplier = 1
    if 'BILLION' in price_str or 'B' in price_str:
        multiplier = 1_000_000_000
        price_str = re.sub(r'BILLION|B', '', price_str, flags=re.IGNORECASE)
    elif 'MILLION' in price_str or 'M' in price_str:
        multiplier = 1_000_000
        price_str = re.sub(r'MILLION|M', '', price_str, flags=re.IGNORECASE)
    elif 'K' in price_str:
        multiplier = 1_000
        price_str = re.sub(r'K', '', price_str, flags=re.IGNORECASE)

    # Extract numeric value
    match = re.search(r'[\d.]+', price_str)
    if match:
        try:
            value = float(match.group()) * multiplier
            return str(int(value))
        except ValueError:
            return None

    return None


def normalize_location(location_str: Any) -> Optional[str]:
    """
    Normalize location string.

    - Trim whitespace
    - Title case
    - Handle common Lagos area aliases
    """
    if pd.isna(location_str) or location_str == '':
        return None

    location = str(location_str).strip()

    # Handle pipe-separated lists (take first)
    if '|' in location:
        location = location.split('|')[0].strip()

    # Title case
    location = location.title()

    # Common aliases
    aliases = {
        'Vi': 'Victoria Island',
        'V.I': 'Victoria Island',
        'V.I.': 'Victoria Island',
        'Vgc': 'VGC',
        'Gra': 'GRA',
    }

    for alias, canonical in aliases.items():
        if location == alias:
            return canonical

    return location


def normalize_property_type(prop_type: Any) -> Optional[str]:
    """
    Normalize property type values.

    Standardize common variations.
    """
    if pd.isna(prop_type) or prop_type == '':
        return None

    prop_type = str(prop_type).strip().lower()

    # Standardization mapping
    type_map = {
        'flat': 'Flat',
        'apartment': 'Flat',
        'house': 'House',
        'detached': 'Detached House',
        'semi-detached': 'Semi-Detached House',
        'semi detached': 'Semi-Detached House',
        'terrace': 'Terraced House',
        'terraced': 'Terraced House',
        'duplex': 'Duplex',
        'bungalow': 'Bungalow',
        'land': 'Land',
        'plot': 'Land',
        'commercial': 'Commercial Property',
        'office': 'Office Space',
        'warehouse': 'Warehouse',
    }

    for key, canonical in type_map.items():
        if key in prop_type:
            return canonical

    # Title case if no match
    return prop_type.title()


def extract_bedrooms_from_title(title: str) -> Optional[int]:
    """
    Extract bedroom count from title if not explicitly provided.

    Patterns: "3 bedroom", "3bed", "3BR", "3-bed"
    """
    if not title:
        return None

    patterns = [
        r'(\d+)\s*bed',
        r'(\d+)\s*br\b',
        r'(\d+)\s*-\s*bed',
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue

    return None


def compute_record_hash(record: Dict) -> str:
    """
    Compute unique hash for record deduplication.

    Uses: title + price + location
    """
    key_parts = [
        str(record.get('title', '')),
        str(record.get('price', '')),
        str(record.get('location', ''))
    ]

    key_string = '|'.join(key_parts).lower().strip()
    return hashlib.sha256(key_string.encode()).hexdigest()


def clean_record(record: Dict) -> Optional[Dict]:
    """
    Clean and normalize a single record.

    Returns None if record is invalid (missing required fields).
    """
    # Step 1: Normalize column names
    normalized = normalize_column_names(record)

    # Step 2: Create cleaned record with canonical schema
    cleaned = {}

    for field in CANONICAL_SCHEMA:
        cleaned[field] = normalized.get(field, None)

    # Step 3: Normalize specific fields
    cleaned['price'] = normalize_price(cleaned.get('price'))
    cleaned['location'] = normalize_location(cleaned.get('location'))
    cleaned['property_type'] = normalize_property_type(cleaned.get('property_type'))

    # Step 4: Extract bedrooms from title if missing
    if not cleaned.get('bedrooms') and cleaned.get('title'):
        extracted_beds = extract_bedrooms_from_title(cleaned['title'])
        if extracted_beds:
            cleaned['bedrooms'] = extracted_beds

    # Step 5: Validate required fields
    if not cleaned.get('title') and not cleaned.get('location'):
        logging.debug("Skipping record: missing both title and location")
        return None

    # Step 6: Compute hash for deduplication
    cleaned['hash'] = compute_record_hash(cleaned)

    # Step 7: Add processing timestamp if missing
    if not cleaned.get('scrape_timestamp'):
        cleaned['scrape_timestamp'] = datetime.now().isoformat()

    return cleaned


def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """
    Remove duplicate records based on hash.

    Keeps first occurrence of each unique hash.
    """
    seen_hashes: Set[str] = set()
    unique_records = []
    duplicates = 0

    for record in records:
        record_hash = record.get('hash', '')

        if record_hash and record_hash in seen_hashes:
            duplicates += 1
            continue

        seen_hashes.add(record_hash)
        unique_records.append(record)

    if duplicates > 0:
        logging.info(f"Removed {duplicates} duplicate records")

    return unique_records


def clean_and_normalize(file_path: Path) -> List[Dict]:
    """
    Main cleaning pipeline: ingest, clean, normalize, deduplicate.

    Args:
        file_path: Path to CSV or XLSX file

    Returns:
        List of cleaned, normalized, deduplicated records
    """
    logging.info(f"Cleaning file: {file_path}")

    # Step 1: Ingest file
    raw_records = ingest_file(file_path)
    if not raw_records:
        logging.warning(f"No records found in {file_path}")
        return []

    logging.debug(f"Ingested {len(raw_records)} raw records")

    # Step 2: Clean each record
    cleaned_records = []
    for i, record in enumerate(raw_records):
        try:
            cleaned = clean_record(record)
            if cleaned:
                cleaned_records.append(cleaned)
        except Exception as e:
            logging.error(f"Error cleaning record {i}: {e}")
            continue

    logging.debug(f"Cleaned {len(cleaned_records)} records")

    # Step 3: Deduplicate
    unique_records = deduplicate_records(cleaned_records)

    logging.info(f"Cleaning complete: {len(unique_records)} unique records")

    return unique_records


def validate_schema(records: List[Dict]) -> Dict[str, Any]:
    """
    Validate records against canonical schema and generate quality metrics.

    Returns quality metrics dict.
    """
    if not records:
        return {'valid': False, 'error': 'No records'}

    metrics = {
        'total_records': len(records),
        'missing_title': 0,
        'missing_price': 0,
        'missing_location': 0,
        'missing_listing_url': 0,
        'has_bedrooms': 0,
        'has_property_type': 0,
        'valid': True
    }

    for record in records:
        if not record.get('title'):
            metrics['missing_title'] += 1
        if not record.get('price'):
            metrics['missing_price'] += 1
        if not record.get('location'):
            metrics['missing_location'] += 1
        if not record.get('listing_url'):
            metrics['missing_listing_url'] += 1
        if record.get('bedrooms'):
            metrics['has_bedrooms'] += 1
        if record.get('property_type'):
            metrics['has_property_type'] += 1

    # Calculate percentages
    total = metrics['total_records']
    metrics['completeness'] = {
        'title': round((total - metrics['missing_title']) / total * 100, 1),
        'price': round((total - metrics['missing_price']) / total * 100, 1),
        'location': round((total - metrics['missing_location']) / total * 100, 1),
        'bedrooms': round(metrics['has_bedrooms'] / total * 100, 1),
        'property_type': round(metrics['has_property_type'] / total * 100, 1),
    }

    return metrics
