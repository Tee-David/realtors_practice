# core/master_workbook.py
"""
Master Workbook Management Module

Handles:
- Creating and managing MASTER_CLEANED_WORKBOOK.xlsx
- Per-site sheet management (create, append)
- Append-only idempotent logic
- Workbook optimization (freeze panes, filters, column widths)
- Per-site CSV and Parquet exports
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo

from core.data_cleaner import CANONICAL_SCHEMA

# Metadata file for tracking master workbook state
METADATA_FILE = Path("exports/cleaned/metadata.json")


class MasterWorkbookManager:
    """Manages the master cleaned workbook with per-site sheets."""

    def __init__(self, workbook_path: Path):
        self.workbook_path = workbook_path
        self.workbook_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load metadata tracking master workbook state."""
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load metadata: {e}")
                return {}
        return {}

    def _save_metadata(self):
        """Save metadata to disk."""
        try:
            METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save metadata: {e}")

    def _ensure_workbook_exists(self):
        """Ensure master workbook file exists."""
        if not self.workbook_path.exists():
            logging.info(f"Creating new master workbook: {self.workbook_path}")
            wb = Workbook()

            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])

            # Create metadata sheet
            ws_meta = wb.create_sheet('_Metadata')
            ws_meta.append(['Field', 'Value'])
            ws_meta.append(['Created', datetime.now().isoformat()])
            ws_meta.append(['Total Sites', 0])
            ws_meta.append(['Total Records', 0])
            ws_meta.append(['Last Updated', datetime.now().isoformat()])

            # Format metadata sheet
            ws_meta['A1'].font = Font(bold=True)
            ws_meta['B1'].font = Font(bold=True)
            ws_meta.column_dimensions['A'].width = 20
            ws_meta.column_dimensions['B'].width = 40

            wb.save(self.workbook_path)
            logging.info("Master workbook created successfully")

    def _get_existing_hashes(self, sheet_name: str) -> Set[str]:
        """
        Get set of existing record hashes from a sheet.

        Used for deduplication during append.
        """
        try:
            wb = load_workbook(self.workbook_path, read_only=True)

            if sheet_name not in wb.sheetnames:
                return set()

            ws = wb[sheet_name]

            # Find hash column index
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            try:
                hash_col_idx = header_row.index('hash') + 1  # 1-indexed
            except ValueError:
                logging.warning(f"No 'hash' column found in {sheet_name}")
                return set()

            # Collect all hashes
            hashes = set()
            for row in ws.iter_rows(min_row=2, min_col=hash_col_idx, max_col=hash_col_idx, values_only=True):
                if row[0]:
                    hashes.add(str(row[0]))

            wb.close()
            return hashes

        except Exception as e:
            logging.error(f"Error reading existing hashes from {sheet_name}: {e}")
            return set()

    def _create_site_sheet(self, site_key: str) -> None:
        """
        Create a new sheet for a site.

        Sets up headers, formatting, and filters.
        """
        try:
            wb = load_workbook(self.workbook_path)

            # Create sheet
            ws = wb.create_sheet(site_key)

            # Add headers
            ws.append(CANONICAL_SCHEMA)

            # Format header row
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)

            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

            # Set column widths
            column_widths = {
                'A': 50,  # title
                'B': 15,  # price
                'C': 15,  # price_per_sqm
                'D': 15,  # price_per_bedroom
                'E': 30,  # location
                'F': 30,  # estate_name
                'G': 20,  # property_type
                'H': 10,  # bedrooms
                'I': 10,  # bathrooms
                'J': 10,  # toilets
                'K': 10,  # bq
                'L': 15,  # land_size
                'M': 15,  # title_tag
                'N': 50,  # description
                'O': 20,  # promo_tags
                'P': 15,  # initial_deposit
                'Q': 20,  # payment_plan
                'R': 15,  # service_charge
                'S': 20,  # launch_timeline
                'T': 30,  # agent_name
                'U': 30,  # contact_info
                'V': 50,  # images
                'W': 60,  # listing_url
                'X': 30,  # source
                'Y': 20,  # scrape_timestamp
                'Z': 25,  # coordinates
                'AA': 70, # hash
            }

            for col, width in column_widths.items():
                ws.column_dimensions[col].width = width

            # Freeze header row
            ws.freeze_panes = 'A2'

            # Add auto-filter (handle columns beyond Z)
            last_col_idx = len(CANONICAL_SCHEMA)
            if last_col_idx <= 26:
                last_col = chr(64 + last_col_idx)
            else:
                # For columns beyond Z (AA, AB, etc.)
                last_col = chr(64 + (last_col_idx - 1) // 26) + chr(65 + (last_col_idx - 1) % 26)
            ws.auto_filter.ref = f"A1:{last_col}1"

            wb.save(self.workbook_path)
            logging.info(f"Created new sheet: {site_key}")

        except Exception as e:
            logging.error(f"Failed to create sheet {site_key}: {e}")
            raise

    def _append_records_to_sheet(self, site_key: str, new_records: List[Dict]) -> int:
        """
        Append new records to a site sheet.

        Returns number of records actually appended (after deduplication).
        """
        try:
            # Get existing hashes for deduplication
            existing_hashes = self._get_existing_hashes(site_key)
            logging.debug(f"Sheet {site_key} has {len(existing_hashes)} existing records")

            # Filter out duplicates
            records_to_append = [
                r for r in new_records
                if r.get('hash') not in existing_hashes
            ]

            if not records_to_append:
                logging.info(f"No new records to append to {site_key} (all duplicates)")
                return 0

            # Load workbook
            wb = load_workbook(self.workbook_path)
            ws = wb[site_key]

            # Append records
            for record in records_to_append:
                row = [record.get(field, '') for field in CANONICAL_SCHEMA]
                ws.append(row)

            wb.save(self.workbook_path)
            logging.info(f"Appended {len(records_to_append)} new records to {site_key}")

            return len(records_to_append)

        except Exception as e:
            logging.error(f"Failed to append records to {site_key}: {e}")
            raise

    def _update_metadata_sheet(self):
        """Update _Metadata sheet with current statistics."""
        try:
            wb = load_workbook(self.workbook_path)

            # Count sites and records
            site_count = len([s for s in wb.sheetnames if s != '_Metadata'])
            total_records = 0

            for sheet_name in wb.sheetnames:
                if sheet_name == '_Metadata':
                    continue
                ws = wb[sheet_name]
                total_records += ws.max_row - 1  # Subtract header row

            # Update metadata sheet
            ws_meta = wb['_Metadata']
            ws_meta['B3'] = site_count
            ws_meta['B4'] = total_records
            ws_meta['B5'] = datetime.now().isoformat()

            wb.save(self.workbook_path)
            logging.debug("Updated metadata sheet")

        except Exception as e:
            logging.error(f"Failed to update metadata sheet: {e}")

    def append_to_site(self, site_key: str, records: List[Dict]) -> int:
        """
        Append records to a site sheet (idempotent).

        Creates sheet if it doesn't exist.
        Filters out duplicates based on hash.

        Returns number of new records appended.
        """
        if not records:
            logging.warning(f"No records to append for {site_key}")
            return 0

        # Ensure workbook exists
        self._ensure_workbook_exists()

        # Check if sheet exists
        wb = load_workbook(self.workbook_path, read_only=True)
        sheet_exists = site_key in wb.sheetnames
        wb.close()

        # Create sheet if needed
        if not sheet_exists:
            self._create_site_sheet(site_key)

        # Append records
        new_count = self._append_records_to_sheet(site_key, records)

        # Update metadata
        if new_count > 0:
            self._update_metadata_sheet()
            self._update_site_metadata(site_key, new_count)

        return new_count

    def _update_site_metadata(self, site_key: str, new_count: int):
        """Update metadata tracking for a specific site."""
        if site_key not in self.metadata:
            self.metadata[site_key] = {
                'total_records': 0,
                'first_added': datetime.now().isoformat(),
                'source_files': []
            }

        self.metadata[site_key]['total_records'] += new_count
        self.metadata[site_key]['last_updated'] = datetime.now().isoformat()

        self._save_metadata()

    def export_site_to_csv(self, site_key: str, output_dir: Path):
        """
        Export a site sheet to CSV file.

        Creates: exports/cleaned/<site>/<site>_cleaned.csv
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            csv_path = output_dir / f"{site_key}_cleaned.csv"

            # Read sheet
            wb = load_workbook(self.workbook_path, read_only=True)
            if site_key not in wb.sheetnames:
                logging.warning(f"Sheet {site_key} not found")
                return

            ws = wb[site_key]

            # Convert to dataframe
            data = ws.values
            cols = next(data)
            df = pd.DataFrame(data, columns=cols)

            # Export
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            logging.info(f"Exported {site_key} to {csv_path}")

            wb.close()

        except Exception as e:
            logging.error(f"Failed to export {site_key} to CSV: {e}")

    def export_site_to_parquet(self, site_key: str, output_dir: Path):
        """
        Export a site sheet to Parquet file.

        Creates: exports/cleaned/<site>/<site>_cleaned.parquet
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            parquet_path = output_dir / f"{site_key}_cleaned.parquet"

            # Read sheet
            wb = load_workbook(self.workbook_path, read_only=True)
            if site_key not in wb.sheetnames:
                logging.warning(f"Sheet {site_key} not found")
                return

            ws = wb[site_key]

            # Convert to dataframe
            data = ws.values
            cols = next(data)
            df = pd.DataFrame(data, columns=cols)

            # Export
            df.to_parquet(parquet_path, index=False, engine='pyarrow')
            logging.info(f"Exported {site_key} to {parquet_path}")

            wb.close()

        except Exception as e:
            logging.error(f"Failed to export {site_key} to Parquet: {e}")


def append_to_master(site_key: str, records: List[Dict], workbook_path: Path) -> int:
    """
    Main entry point: append records to master workbook for a site.

    Args:
        site_key: Site identifier
        records: List of cleaned, normalized records
        workbook_path: Path to MASTER_CLEANED_WORKBOOK.xlsx

    Returns:
        Number of new records appended
    """
    manager = MasterWorkbookManager(workbook_path)
    new_count = manager.append_to_site(site_key, records)

    # Also export to CSV and Parquet
    if new_count > 0:
        output_dir = workbook_path.parent / site_key
        try:
            manager.export_site_to_csv(site_key, output_dir)
        except Exception as e:
            logging.error(f"CSV export failed for {site_key}: {e}")

        try:
            manager.export_site_to_parquet(site_key, output_dir)
        except Exception as e:
            # Parquet may fail if pyarrow not installed
            logging.warning(f"Parquet export skipped for {site_key}: {e}")

    return new_count
