"""
Stats Generator - Generate statistics from scraped data
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StatsGenerator:
    """Helper class to generate statistics"""

    def __init__(self):
        self.exports_dir = Path("exports")
        self.sites_dir = self.exports_dir / "sites"
        self.cleaned_dir = self.exports_dir / "cleaned"
        self.metadata_file = Path("logs/site_metadata.json")

    def _load_metadata(self) -> Dict:
        """Load site metadata"""
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}

    def get_overview(self) -> Dict:
        """Get overall statistics"""
        try:
            metadata = self._load_metadata()

            total_sites = len(metadata)
            active_sites = len([s for s in metadata.values() if s.get('last_successful_scrape')])
            total_listings = sum(s.get('last_count', 0) for s in metadata.values())

            # Count files
            raw_files = 0
            if self.sites_dir.exists():
                for site_dir in self.sites_dir.iterdir():
                    if site_dir.is_dir():
                        raw_files += len(list(site_dir.glob("*.*")))

            cleaned_files = 0
            if self.cleaned_dir.exists():
                for site_dir in self.cleaned_dir.iterdir():
                    if site_dir.is_dir():
                        cleaned_files += len(list(site_dir.glob("*.*")))

            # Get latest scrape time
            latest_scrape = None
            for site_meta in metadata.values():
                if 'last_scrape' in site_meta:
                    if latest_scrape is None or site_meta['last_scrape'] > latest_scrape:
                        latest_scrape = site_meta['last_scrape']

            return {
                'overview': {
                    'total_sites': total_sites,
                    'active_sites': active_sites,
                    'total_listings': total_listings,
                    'latest_scrape': latest_scrape
                },
                'files': {
                    'raw_files': raw_files,
                    'cleaned_files': cleaned_files
                }
            }

        except Exception as e:
            logger.error(f"Error generating overview stats: {e}")
            return {
                'error': str(e)
            }

    def get_site_stats(self) -> Dict:
        """Get per-site statistics"""
        try:
            metadata = self._load_metadata()

            site_stats = []

            for site_key, site_meta in metadata.items():
                stats = {
                    'site_key': site_key,
                    'last_scrape': site_meta.get('last_scrape'),
                    'last_successful_scrape': site_meta.get('last_successful_scrape'),
                    'last_count': site_meta.get('last_count', 0),
                    'total_scrapes': site_meta.get('total_scrapes', 0),
                    'status': 'active' if site_meta.get('last_successful_scrape') else 'inactive'
                }

                # Calculate health status
                if site_meta.get('last_count', 0) > 0:
                    if site_meta.get('last_count', 0) >= 100:
                        stats['health'] = 'healthy'
                    elif site_meta.get('last_count', 0) >= 10:
                        stats['health'] = 'warning'
                    else:
                        stats['health'] = 'critical'
                else:
                    stats['health'] = 'inactive'

                site_stats.append(stats)

            # Sort by last_count descending
            site_stats.sort(key=lambda x: x['last_count'], reverse=True)

            return {
                'total': len(site_stats),
                'sites': site_stats
            }

        except Exception as e:
            logger.error(f"Error generating site stats: {e}")
            return {
                'error': str(e)
            }

    def get_trends(self, days: int = 7) -> Dict:
        """
        Get historical trends

        Args:
            days: Number of days to analyze
        """
        try:
            # For now, return basic trend data based on metadata
            # In production, store time-series data for better trends
            metadata = self._load_metadata()

            # Get scrapes in the last N days
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            recent_scrapes = []
            for site_key, site_meta in metadata.items():
                if 'last_scrape' in site_meta and site_meta['last_scrape'] > cutoff_date:
                    recent_scrapes.append({
                        'site_key': site_key,
                        'timestamp': site_meta['last_scrape'],
                        'count': site_meta.get('last_count', 0)
                    })

            # Calculate totals by day
            daily_totals = {}
            for scrape in recent_scrapes:
                date = scrape['timestamp'][:10]  # Get YYYY-MM-DD
                if date not in daily_totals:
                    daily_totals[date] = {
                        'date': date,
                        'total_listings': 0,
                        'total_scrapes': 0
                    }

                daily_totals[date]['total_listings'] += scrape['count']
                daily_totals[date]['total_scrapes'] += 1

            # Convert to list and sort by date
            trends = list(daily_totals.values())
            trends.sort(key=lambda x: x['date'])

            return {
                'period_days': days,
                'total_scrapes': len(recent_scrapes),
                'daily_trends': trends
            }

        except Exception as e:
            logger.error(f"Error generating trends: {e}")
            return {
                'error': str(e)
            }

    def get_property_stats(self) -> Dict:
        """Get statistics about properties (from cleaned data)"""
        try:
            stats = {
                'by_type': {},
                'by_location': {},
                'price_ranges': {
                    'under_1m': 0,
                    '1m_to_5m': 0,
                    '5m_to_10m': 0,
                    '10m_to_50m': 0,
                    'over_50m': 0
                }
            }

            # Read master workbook if exists
            master_file = self.cleaned_dir / "MASTER_CLEANED_WORKBOOK.xlsx"
            if not master_file.exists():
                return stats

            excel_file = pd.ExcelFile(master_file)

            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'Metadata':
                    continue

                df = pd.read_excel(master_file, sheet_name=sheet_name)

                # Property type stats
                if 'property_type' in df.columns:
                    type_counts = df['property_type'].value_counts()
                    for prop_type, count in type_counts.items():
                        if pd.notna(prop_type):
                            if prop_type not in stats['by_type']:
                                stats['by_type'][prop_type] = 0
                            stats['by_type'][prop_type] += int(count)

                # Location stats
                if 'location' in df.columns:
                    location_counts = df['location'].value_counts()
                    for location, count in list(location_counts.items())[:20]:  # Top 20
                        if pd.notna(location):
                            if location not in stats['by_location']:
                                stats['by_location'][location] = 0
                            stats['by_location'][location] += int(count)

                # Price range stats
                if 'price' in df.columns:
                    for price in df['price']:
                        if pd.notna(price) and isinstance(price, (int, float)):
                            if price < 1_000_000:
                                stats['price_ranges']['under_1m'] += 1
                            elif price < 5_000_000:
                                stats['price_ranges']['1m_to_5m'] += 1
                            elif price < 10_000_000:
                                stats['price_ranges']['5m_to_10m'] += 1
                            elif price < 50_000_000:
                                stats['price_ranges']['10m_to_50m'] += 1
                            else:
                                stats['price_ranges']['over_50m'] += 1

            return stats

        except Exception as e:
            logger.error(f"Error generating property stats: {e}")
            return {
                'error': str(e)
            }
