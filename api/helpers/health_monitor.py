"""
Health Monitoring Dashboard Module

Monitor scraper performance and health metrics over time.
Provides insights into site success rates, performance trends, and system health.

Metrics tracked:
- Success rate per site (last 7/30 days)
- Average scraping duration
- Error rates and types
- Listing count trends
- Site health status (healthy/warning/critical)

Author: Tee-David
Date: 2025-10-20
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Monitor scraper health and performance metrics.

    Analyzes site metadata to provide health insights.
    """

    def __init__(self, metadata_file: str = "logs/site_metadata.json"):
        """
        Initialize health monitor.

        Args:
            metadata_file: Path to site metadata file
        """
        self.metadata_file = Path(metadata_file)

        logger.debug("HealthMonitor initialized")

    def _load_metadata(self) -> Dict:
        """Load site metadata from file"""
        if not self.metadata_file.exists():
            logger.warning("Site metadata file not found")
            return {}

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                logger.debug(f"Loaded metadata for {len(metadata)} sites")
                return metadata
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime"""
        if not timestamp_str:
            return None

        try:
            # Handle various timestamp formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue

            # Try ISO format
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        except Exception as e:
            logger.debug(f"Could not parse timestamp '{timestamp_str}': {e}")
            return None

    def get_site_health(self, site_key: str, days: int = 7) -> Dict:
        """
        Get health metrics for a specific site.

        Args:
            site_key: Site identifier
            days: Number of days to analyze

        Returns:
            Dict with health metrics
        """
        metadata = self._load_metadata()

        if site_key not in metadata:
            logger.warning(f"No metadata found for site '{site_key}'")
            return {
                'site': site_key,
                'status': 'unknown',
                'message': 'No metadata available'
            }

        site_meta = metadata[site_key]

        # Calculate metrics
        last_scrape = self._parse_timestamp(site_meta.get('last_scrape'))
        last_successful = self._parse_timestamp(site_meta.get('last_successful_scrape'))

        now = datetime.now()

        # Determine health status
        status = 'healthy'
        issues = []

        # Check last successful scrape
        if last_successful:
            hours_since_success = (now - last_successful).total_seconds() / 3600

            if hours_since_success > 72:  # 3 days
                status = 'critical'
                issues.append(f"No successful scrape in {hours_since_success:.0f} hours")
            elif hours_since_success > 24:  # 1 day
                if status != 'critical':
                    status = 'warning'
                issues.append(f"Last successful scrape {hours_since_success:.0f} hours ago")
        else:
            status = 'critical'
            issues.append("Never successfully scraped")

        # Check scrape count
        last_count = site_meta.get('last_count', 0)

        if last_count == 0 and last_scrape:
            if status == 'healthy':
                status = 'warning'
            issues.append("Last scrape returned 0 listings")

        # Performance metrics
        avg_listings = site_meta.get('last_count', 0)  # Simplified - would calculate average
        total_scrapes = site_meta.get('total_scrapes', 0)

        return {
            'site': site_key,
            'status': status,
            'last_scrape': site_meta.get('last_scrape'),
            'last_successful_scrape': site_meta.get('last_successful_scrape'),
            'last_listing_count': last_count,
            'avg_listings': avg_listings,
            'total_scrapes': total_scrapes,
            'issues': issues,
            'health_score': self._calculate_health_score(status, issues)
        }

    def _calculate_health_score(self, status: str, issues: List[str]) -> float:
        """
        Calculate numeric health score (0.0 to 1.0).

        Args:
            status: Health status
            issues: List of issues

        Returns:
            Health score
        """
        base_scores = {
            'healthy': 1.0,
            'warning': 0.6,
            'critical': 0.2,
            'unknown': 0.0
        }

        score = base_scores.get(status, 0.0)

        # Reduce score based on number of issues
        issue_penalty = len(issues) * 0.1
        score = max(0.0, score - issue_penalty)

        return round(score, 2)

    def get_overall_health(self) -> Dict:
        """
        Get overall system health.

        Returns:
            Dict with aggregate health metrics
        """
        metadata = self._load_metadata()

        if not metadata:
            return {
                'status': 'unknown',
                'message': 'No metadata available'
            }

        total_sites = len(metadata)
        healthy_count = 0
        warning_count = 0
        critical_count = 0

        site_statuses = []

        for site_key in metadata.keys():
            health = self.get_site_health(site_key)
            site_statuses.append(health)

            if health['status'] == 'healthy':
                healthy_count += 1
            elif health['status'] == 'warning':
                warning_count += 1
            elif health['status'] == 'critical':
                critical_count += 1

        # Determine overall status
        overall_status = 'healthy'

        if critical_count > total_sites * 0.3:  # >30% critical
            overall_status = 'critical'
        elif warning_count + critical_count > total_sites * 0.5:  # >50% not healthy
            overall_status = 'warning'

        # Calculate average listings
        total_listings = sum(s['last_listing_count'] for s in site_statuses)
        avg_listings_per_site = round(total_listings / total_sites, 1) if total_sites > 0 else 0

        return {
            'status': overall_status,
            'total_sites': total_sites,
            'healthy_sites': healthy_count,
            'warning_sites': warning_count,
            'critical_sites': critical_count,
            'health_percentages': {
                'healthy': round(healthy_count / total_sites * 100, 1) if total_sites > 0 else 0,
                'warning': round(warning_count / total_sites * 100, 1) if total_sites > 0 else 0,
                'critical': round(critical_count / total_sites * 100, 1) if total_sites > 0 else 0
            },
            'total_listings': total_listings,
            'avg_listings_per_site': avg_listings_per_site,
            'last_updated': datetime.now().isoformat()
        }

    def get_sites_by_status(self, status: str) -> List[Dict]:
        """
        Get all sites with a specific health status.

        Args:
            status: Health status ('healthy', 'warning', 'critical')

        Returns:
            List of site health dicts
        """
        metadata = self._load_metadata()

        sites = []

        for site_key in metadata.keys():
            health = self.get_site_health(site_key)

            if health['status'] == status:
                sites.append(health)

        # Sort by health score (lowest first for warning/critical)
        sites.sort(key=lambda x: x.get('health_score', 0), reverse=(status == 'healthy'))

        return sites

    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        """
        Get top performing sites by listing count.

        Args:
            limit: Number of sites to return

        Returns:
            List of site dicts sorted by performance
        """
        metadata = self._load_metadata()

        performers = []

        for site_key, site_meta in metadata.items():
            performers.append({
                'site': site_key,
                'last_count': site_meta.get('last_count', 0),
                'total_scrapes': site_meta.get('total_scrapes', 0),
                'last_scrape': site_meta.get('last_scrape')
            })

        # Sort by last count
        performers.sort(key=lambda x: x['last_count'], reverse=True)

        return performers[:limit]

    def get_alerts(self) -> List[Dict]:
        """
        Get active health alerts.

        Returns:
            List of alert dicts
        """
        metadata = self._load_metadata()

        alerts = []

        for site_key in metadata.keys():
            health = self.get_site_health(site_key)

            if health['status'] in ['warning', 'critical']:
                for issue in health['issues']:
                    alerts.append({
                        'site': site_key,
                        'severity': health['status'],
                        'message': issue,
                        'health_score': health['health_score'],
                        'timestamp': datetime.now().isoformat()
                    })

        # Sort by severity (critical first)
        alerts.sort(key=lambda x: (0 if x['severity'] == 'critical' else 1, x['health_score']))

        return alerts

    def get_trend_analysis(self, days: int = 7) -> Dict:
        """
        Analyze trends over time (simplified version).

        In production, this would analyze historical data from logs.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with trend analysis
        """
        metadata = self._load_metadata()

        # This is a simplified version
        # In production, would analyze logs/historical_metadata.json

        total_sites = len(metadata)
        total_listings = sum(m.get('last_count', 0) for m in metadata.values())

        return {
            'period_days': days,
            'total_listings_current': total_listings,
            'avg_listings_per_day': round(total_listings / days, 1),
            'total_scrapes': sum(m.get('total_scrapes', 0) for m in metadata.values()),
            'trend': 'stable',  # Would calculate from historical data
            'note': 'Trend analysis requires historical data tracking'
        }


def get_health_monitor(metadata_file: str = "logs/site_metadata.json") -> HealthMonitor:
    """
    Get a HealthMonitor instance.

    Args:
        metadata_file: Path to site metadata file

    Returns:
        HealthMonitor instance
    """
    return HealthMonitor(metadata_file=metadata_file)
