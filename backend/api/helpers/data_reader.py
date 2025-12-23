"""
Data Reader - Read and query Excel/CSV data files and Firestore

Prioritizes Firestore over Excel for better performance and real-time data.
"""
import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Firestore client (lazy loaded)
_firestore_client = None


def _get_firestore():
    """Get Firestore client (lazy initialization)"""
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    # Check if Firestore is enabled
    firestore_enabled = os.getenv('FIRESTORE_ENABLED', '1') == '1'
    if not firestore_enabled:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Check if already initialized
        if firebase_admin._apps:
            _firestore_client = firestore.client()
            return _firestore_client

        # Try to load credentials
        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        cred_json = os.getenv('FIREBASE_CREDENTIALS')

        if cred_path and Path(cred_path).exists():
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client()
            logger.info("Firestore initialized for API queries")
            return _firestore_client
        elif cred_json:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client()
            logger.info("Firestore initialized from env var")
            return _firestore_client

    except ImportError:
        logger.debug("firebase-admin not installed, using Excel fallback")
    except Exception as e:
        logger.warning(f"Firestore init failed, using Excel fallback: {e}")

    return None


class DataReader:
    """Helper class to read and query scraped data"""

    def __init__(self):
        self.exports_dir = Path("exports")
        self.sites_dir = self.exports_dir / "sites"
        self.cleaned_dir = self.exports_dir / "cleaned"

    def list_available_data(self) -> Dict:
        """List all available data files"""
        result = {
            'raw_sites': [],
            'cleaned_sites': []
        }

        # Check raw site exports
        if self.sites_dir.exists():
            for site_dir in self.sites_dir.iterdir():
                if site_dir.is_dir():
                    files = list(site_dir.glob("*.csv")) + list(site_dir.glob("*.xlsx"))
                    if files:
                        latest_file = max(files, key=lambda f: f.stat().st_mtime)
                        result['raw_sites'].append({
                            'site_key': site_dir.name,
                            'latest_file': str(latest_file.relative_to(self.exports_dir)),
                            'file_count': len(files),
                            'last_updated': latest_file.stat().st_mtime
                        })

        # Check cleaned site exports
        if self.cleaned_dir.exists():
            for site_dir in self.cleaned_dir.iterdir():
                if site_dir.is_dir():
                    csv_file = site_dir / f"{site_dir.name}_cleaned.csv"
                    if csv_file.exists():
                        result['cleaned_sites'].append({
                            'site_key': site_dir.name,
                            'file': str(csv_file.relative_to(self.exports_dir)),
                            'last_updated': csv_file.stat().st_mtime
                        })

        return result

    def get_site_data(self, site_key: str, limit: int = 100, offset: int = 0, source: str = 'cleaned') -> Dict:
        """
        Get data for a specific site

        Prioritizes Firestore over Excel for better performance.

        Args:
            site_key: Site identifier
            limit: Number of records to return
            offset: Pagination offset
            source: 'raw', 'cleaned', or 'firestore' (default: tries firestore first)
        """
        # Try Firestore first (if enabled and not explicitly requesting raw/cleaned)
        db = _get_firestore()
        if db and source != 'raw':
            try:
                collection_ref = db.collection('properties')
                query = collection_ref.where('site_key', '==', site_key)

                # Get total count (for pagination metadata)
                all_docs = list(query.stream())
                total_records = len(all_docs)

                # Apply pagination
                paginated_docs = all_docs[offset:offset + limit]

                # Convert to records
                records = []
                for doc in paginated_docs:
                    data = doc.to_dict()
                    records.append(data)

                logger.info(f"Served {len(records)} records from Firestore for {site_key}")

                return {
                    'site_key': site_key,
                    'data': records,
                    'total_records': total_records,
                    'limit': limit,
                    'offset': offset,
                    'source': 'firestore'
                }

            except Exception as e:
                logger.warning(f"Firestore query failed for {site_key}, falling back to Excel: {e}")
                # Fall through to Excel fallback

        # Fallback to Excel/CSV
        if source == 'cleaned':
            # Read from cleaned directory
            csv_file = self.cleaned_dir / site_key / f"{site_key}_cleaned.csv"
            if not csv_file.exists():
                raise FileNotFoundError(f"No cleaned data for {site_key}")

            df = pd.read_csv(csv_file)
        else:
            # Read from latest raw file
            site_dir = self.sites_dir / site_key
            if not site_dir.exists():
                raise FileNotFoundError(f"No raw data for {site_key}")

            files = list(site_dir.glob("*.csv")) + list(site_dir.glob("*.xlsx"))
            if not files:
                raise FileNotFoundError(f"No data files for {site_key}")

            latest_file = max(files, key=lambda f: f.stat().st_mtime)

            if latest_file.suffix == '.csv':
                df = pd.read_csv(latest_file)
            else:
                df = pd.read_excel(latest_file)

        # Apply pagination
        total_records = len(df)
        df_page = df.iloc[offset:offset + limit]

        # Convert to dict
        records = df_page.fillna('').to_dict('records')

        return {
            'site_key': site_key,
            'source': source,
            'total_records': total_records,
            'returned_records': len(records),
            'offset': offset,
            'limit': limit,
            'data': records
        }

    def get_master_data(self, limit: int = 100, site_filter: Optional[str] = None) -> Dict:
        """
        Get consolidated data from Firestore (or Excel fallback)

        Args:
            limit: Number of records per site
            site_filter: Optional filter by site key
        """
        # Try Firestore first
        db = _get_firestore()
        if db:
            try:
                query = db.collection('properties')

                # Apply site filter if provided
                if site_filter:
                    query = query.where('basic_info.site_key', '==', site_filter)

                # Apply limit
                query = query.limit(limit)

                # Get results
                docs = query.stream()
                properties = [doc.to_dict() for doc in docs]

                return {
                    'source': 'firestore',
                    'total_records': len(properties),
                    'properties': properties
                }
            except Exception as e:
                logger.warning(f"Firestore query failed, falling back to Excel: {e}")

        # Fallback to Excel (deprecated)
        master_file = self.cleaned_dir / "MASTER_CLEANED_WORKBOOK.xlsx"
        if not master_file.exists():
            return {
                'error': 'No data available',
                'message': 'Firestore not configured and Excel workbook not found',
                'source': 'none'
            }

        # Read all sheets (old method)
        excel_file = pd.ExcelFile(master_file)
        result = {
            'source': 'excel',
            'total_sheets': len(excel_file.sheet_names),
            'sheets': []
        }

        for sheet_name in excel_file.sheet_names:
            if sheet_name == 'Metadata':
                continue

            # Apply site filter if provided
            if site_filter and sheet_name != site_filter:
                continue

            df = pd.read_excel(master_file, sheet_name=sheet_name)
            total_records = len(df)

            # Apply limit
            df_limited = df.head(limit)
            records = df_limited.fillna('').to_dict('records')

            result['sheets'].append({
                'site_key': sheet_name,
                'total_records': total_records,
                'returned_records': len(records),
                'data': records
            })

        return result

    def search_data(self, query: str, fields: List[str], limit: int = 50) -> Dict:
        """
        Search across all data

        Args:
            query: Search term
            fields: Fields to search in
            limit: Max results
        """
        results = []
        query_lower = query.lower()

        # Search in cleaned data
        if self.cleaned_dir.exists():
            for site_dir in self.cleaned_dir.iterdir():
                if not site_dir.is_dir():
                    continue

                csv_file = site_dir / f"{site_dir.name}_cleaned.csv"
                if not csv_file.exists():
                    continue

                try:
                    df = pd.read_csv(csv_file)

                    # Search in specified fields
                    mask = pd.Series([False] * len(df))
                    for field in fields:
                        if field in df.columns:
                            mask |= df[field].fillna('').astype(str).str.lower().str.contains(query_lower)

                    matches = df[mask]

                    for _, row in matches.head(limit).iterrows():
                        results.append({
                            'site_key': site_dir.name,
                            'data': row.fillna('').to_dict()
                        })

                        if len(results) >= limit:
                            break

                    if len(results) >= limit:
                        break

                except Exception as e:
                    logger.error(f"Error searching {site_dir.name}: {e}")
                    continue

        return {
            'query': query,
            'fields': fields,
            'total_results': len(results),
            'results': results
        }

    def get_metadata(self) -> Dict:
        """Get metadata from cleaned directory"""
        metadata_file = self.cleaned_dir / "metadata.json"
        if not metadata_file.exists():
            return {}

        with open(metadata_file, 'r') as f:
            return json.load(f)
