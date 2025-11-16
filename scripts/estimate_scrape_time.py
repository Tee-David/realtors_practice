#!/usr/bin/env python3
"""
Intelligent Scrape Time Estimation and Batch Calculator

Estimates scraping duration based on:
- Number of sites
- Pages per site
- Historical performance data
- GitHub Actions limits (6 hours = 360 minutes)
"""

import yaml
import json
import math
from pathlib import Path
from datetime import timedelta


class ScrapeTimeEstimator:
    """Estimates scrape time and calculates optimal batching"""

    # Constants based on empirical testing
    TIME_PER_PAGE = 8  # seconds per page (includes waiting, scrolling, parsing)
    TIME_PER_SITE_OVERHEAD = 45  # seconds (site initialization, navigation)
    GEOCODE_TIME_PER_PROPERTY = 1.2  # seconds per geocoded property
    FIRESTORE_UPLOAD_TIME = 0.3  # seconds per property upload
    WATCHER_OVERHEAD = 120  # seconds for watcher processing
    CONSOLIDATION_OVERHEAD = 180  # seconds for final consolidation
    BUFFER_MULTIPLIER = 1.3  # 30% buffer for variations

    # GitHub Actions limits
    GITHUB_ACTIONS_TIMEOUT_MINUTES = 350  # 6 hours minus 10 min buffer
    GITHUB_ACTIONS_MAX_PARALLEL = 3  # Safe parallel execution

    def __init__(self, config_path='config.yaml'):
        """Initialize estimator with config"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.enabled_sites = self._get_enabled_sites()

    def _load_config(self):
        """Load config.yaml"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _get_enabled_sites(self):
        """Get list of enabled sites"""
        return [
            site_id for site_id, site_config in self.config.get('sites', {}).items()
            if site_config.get('enabled', False)
        ]

    def estimate_single_site(self, max_pages=20, geocode=True):
        """
        Estimate time for a single site

        Args:
            max_pages: Maximum pages to scrape
            geocode: Whether geocoding is enabled

        Returns:
            dict with time estimates in seconds
        """
        # Base scraping time
        scrape_time = (max_pages * self.TIME_PER_PAGE) + self.TIME_PER_SITE_OVERHEAD

        # Estimate properties (conservative: 15 per page)
        estimated_properties = max_pages * 15

        # Geocoding time (if enabled)
        geocode_time = 0
        if geocode:
            geocode_time = estimated_properties * self.GEOCODE_TIME_PER_PROPERTY

        # Firestore upload time
        upload_time = estimated_properties * self.FIRESTORE_UPLOAD_TIME

        # Total time
        total_time = scrape_time + geocode_time + upload_time

        return {
            'scrape_time': scrape_time,
            'geocode_time': geocode_time,
            'upload_time': upload_time,
            'total_time': total_time,
            'estimated_properties': estimated_properties
        }

    def estimate_batch(self, num_sites, max_pages=20, geocode=True):
        """
        Estimate time for a batch of sites

        Args:
            num_sites: Number of sites in batch
            max_pages: Pages per site
            geocode: Geocoding enabled

        Returns:
            dict with batch time estimates
        """
        single_site = self.estimate_single_site(max_pages, geocode)

        # Total time for all sites (sequential)
        total_site_time = single_site['total_time'] * num_sites

        # Add watcher overhead
        total_time = total_site_time + self.WATCHER_OVERHEAD

        # Apply buffer for variations
        buffered_time = total_time * self.BUFFER_MULTIPLIER

        return {
            'num_sites': num_sites,
            'time_per_site': single_site['total_time'],
            'total_site_time': total_site_time,
            'watcher_overhead': self.WATCHER_OVERHEAD,
            'total_time_seconds': buffered_time,
            'total_time_minutes': buffered_time / 60,
            'estimated_properties': single_site['estimated_properties'] * num_sites
        }

    def calculate_optimal_batches(self, max_pages=20, geocode=True, parallel=3):
        """
        Calculate optimal batch strategy to avoid timeouts

        Args:
            max_pages: Pages per site
            geocode: Geocoding enabled
            parallel: Max parallel sessions (default: 3)

        Returns:
            dict with batching strategy
        """
        total_sites = len(self.enabled_sites)

        # Estimate time for one site
        single_site = self.estimate_single_site(max_pages, geocode)

        # Calculate max sites per session to stay under timeout
        # (timeout_minutes * 60) / buffer / time_per_site
        max_sites_per_session = int(
            (self.GITHUB_ACTIONS_TIMEOUT_MINUTES * 60) /
            self.BUFFER_MULTIPLIER /
            single_site['total_time']
        )

        # Ensure at least 1 site per session
        max_sites_per_session = max(1, max_sites_per_session)

        # Calculate number of sessions needed
        total_sessions = math.ceil(total_sites / max_sites_per_session)

        # Calculate batches (accounting for parallel execution)
        batches = []
        for i in range(0, total_sessions, parallel):
            parallel_sessions = min(parallel, total_sessions - i)
            batch_sites = min(max_sites_per_session * parallel_sessions, total_sites - (i * max_sites_per_session))

            batches.append({
                'batch_number': len(batches) + 1,
                'parallel_sessions': parallel_sessions,
                'sites_per_session': max_sites_per_session,
                'total_sites_in_batch': batch_sites
            })

        # Estimate total time
        session_estimate = self.estimate_batch(max_sites_per_session, max_pages, geocode)
        total_time_minutes = (session_estimate['total_time_minutes'] * total_sessions / parallel) + (self.CONSOLIDATION_OVERHEAD / 60)

        return {
            'total_sites': total_sites,
            'max_pages_per_site': max_pages,
            'geocoding_enabled': geocode,
            'max_parallel_sessions': parallel,
            'sites_per_session': max_sites_per_session,
            'total_sessions': total_sessions,
            'batches': batches,
            'estimated_total_minutes': total_time_minutes,
            'estimated_total_hours': total_time_minutes / 60,
            'github_actions_timeout_safe': total_time_minutes < self.GITHUB_ACTIONS_TIMEOUT_MINUTES,
            'recommendation': self._get_recommendation(total_time_minutes, max_sites_per_session)
        }

    def _get_recommendation(self, total_minutes, sites_per_session):
        """Generate recommendation based on estimates"""
        if total_minutes > self.GITHUB_ACTIONS_TIMEOUT_MINUTES:
            return f"⚠️ TIMEOUT RISK: Reduce to {sites_per_session} sites per session or lower max_pages"
        elif total_minutes > self.GITHUB_ACTIONS_TIMEOUT_MINUTES * 0.9:
            return f"⚠️ CLOSE TO LIMIT: Consider reducing to {sites_per_session - 5} sites per session for safety"
        else:
            return f"✅ SAFE: Estimated time well within GitHub Actions limits"

    def print_report(self, max_pages=20, geocode=True, parallel=3):
        """Print detailed estimation report"""
        strategy = self.calculate_optimal_batches(max_pages, geocode, parallel)

        print("=" * 80)
        print("INTELLIGENT SCRAPE TIME ESTIMATION & BATCHING STRATEGY")
        print("=" * 80)
        print()

        print("📊 INPUT PARAMETERS")
        print(f"  Total sites enabled: {strategy['total_sites']}")
        print(f"  Max pages per site: {strategy['max_pages_per_site']}")
        print(f"  Geocoding: {'Enabled' if strategy['geocoding_enabled'] else 'Disabled'}")
        print(f"  Max parallel sessions: {strategy['max_parallel_sessions']}")
        print()

        print("⏱️  TIME ESTIMATES")
        single_site = self.estimate_single_site(max_pages, geocode)
        print(f"  Time per site: {single_site['total_time']:.0f}s ({single_site['total_time']/60:.1f} min)")
        print(f"    - Scraping: {single_site['scrape_time']:.0f}s")
        print(f"    - Geocoding: {single_site['geocode_time']:.0f}s")
        print(f"    - Upload: {single_site['upload_time']:.0f}s")
        print(f"  Estimated properties per site: {single_site['estimated_properties']}")
        print()

        print("🎯 OPTIMAL BATCHING STRATEGY")
        print(f"  Sites per session: {strategy['sites_per_session']}")
        print(f"  Total sessions needed: {strategy['total_sessions']}")
        print(f"  Number of batches: {len(strategy['batches'])}")
        print()

        print("📦 BATCH BREAKDOWN")
        for batch in strategy['batches']:
            print(f"  Batch {batch['batch_number']}:")
            print(f"    - Parallel sessions: {batch['parallel_sessions']}")
            print(f"    - Sites per session: {batch['sites_per_session']}")
            print(f"    - Total sites: {batch['total_sites_in_batch']}")
        print()

        print("⏰ TOTAL TIME ESTIMATE")
        print(f"  Estimated duration: {strategy['estimated_total_minutes']:.1f} minutes ({strategy['estimated_total_hours']:.2f} hours)")
        print(f"  GitHub Actions limit: {self.GITHUB_ACTIONS_TIMEOUT_MINUTES} minutes (6 hours)")
        print(f"  Safety margin: {self.GITHUB_ACTIONS_TIMEOUT_MINUTES - strategy['estimated_total_minutes']:.1f} minutes")
        print()

        print("💡 RECOMMENDATION")
        print(f"  {strategy['recommendation']}")
        print()

        if not strategy['github_actions_timeout_safe']:
            print("⚠️  WARNING: TIMEOUT RISK DETECTED!")
            print()
            print("  Solutions:")
            print(f"    1. Reduce sites_per_session to {strategy['sites_per_session']}")
            print(f"    2. Reduce max_pages to {max(10, max_pages - 10)}")
            print("    3. Disable geocoding (saves ~50% time)")
            print("    4. Run in multiple separate workflow triggers")
            print()

        print("=" * 80)

        return strategy


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Estimate scrape time and calculate batching')
    parser.add_argument('--max-pages', type=int, default=20, help='Max pages per site (default: 20)')
    parser.add_argument('--no-geocode', action='store_true', help='Disable geocoding')
    parser.add_argument('--parallel', type=int, default=3, help='Max parallel sessions (default: 3)')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of report')

    args = parser.parse_args()

    estimator = ScrapeTimeEstimator()

    if args.json:
        strategy = estimator.calculate_optimal_batches(
            max_pages=args.max_pages,
            geocode=not args.no_geocode,
            parallel=args.parallel
        )
        print(json.dumps(strategy, indent=2))
    else:
        estimator.print_report(
            max_pages=args.max_pages,
            geocode=not args.no_geocode,
            parallel=args.parallel
        )


if __name__ == '__main__':
    main()
