"""
Data Reader - Read and query Excel/CSV data files
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


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
            'cleaned_sites': [],
            'master_workbook_exists': False
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

        # Check master workbook
        master_file = self.cleaned_dir / "MASTER_CLEANED_WORKBOOK.xlsx"
        if master_file.exists():
            result['master_workbook_exists'] = True
            result['master_workbook_path'] = str(master_file.relative_to(self.exports_dir))
            result['master_workbook_updated'] = master_file.stat().st_mtime

        return result

    def get_site_data(self, site_key: str, limit: int = 100, offset: int = 0, source: str = 'cleaned') -> Dict:
        """
        Get data for a specific site

        Args:
            site_key: Site identifier
            limit: Number of records to return
            offset: Pagination offset
            source: 'raw' or 'cleaned'
        """
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
        Get consolidated master workbook data

        Args:
            limit: Number of records per site
            site_filter: Optional filter by site key
        """
        master_file = self.cleaned_dir / "MASTER_CLEANED_WORKBOOK.xlsx"
        if not master_file.exists():
            raise FileNotFoundError("Master workbook not found")

        # Read all sheets
        excel_file = pd.ExcelFile(master_file)
        result = {
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
