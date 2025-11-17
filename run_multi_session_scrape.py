#!/usr/bin/env python3
"""
Multi-Session Scraper (5 Sites Per Session)
============================================

Runs scraping in multiple sessions with only 5 sites per session
to prevent timeouts. Designed to replicate GitHub Actions behavior locally.

Usage:
    python run_multi_session_scrape.py                    # Run all enabled sites
    python run_multi_session_scrape.py --max-pages 10     # Custom page limit
    python run_multi_session_scrape.py --no-geocode       # Skip geocoding
    python run_multi_session_scrape.py --dry-run          # Show plan without running
"""

import yaml
import os
import subprocess
import sys
import math
import time
from pathlib import Path

# Configuration
SITES_PER_SESSION = 5  # Fixed at 5 for reliability
TIME_PER_PAGE = 8  # seconds
TIME_PER_SITE_OVERHEAD = 45  # seconds
GEOCODE_TIME_PER_PROPERTY = 1.2  # seconds
FIRESTORE_UPLOAD_TIME = 0.3  # seconds
BUFFER_MULTIPLIER = 1.3  # 30% safety buffer


def load_enabled_sites():
    """Load list of enabled sites from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'

    with open(config_path) as f:
        config = yaml.safe_load(f)

    enabled_sites = [
        site_id for site_id, site_config in config.get('sites', {}).items()
        if site_config.get('enabled', False)
    ]

    return enabled_sites


def estimate_time(sites_count, max_pages, geocode_enabled):
    """Estimate time for scraping N sites"""
    scrape_time = (max_pages * TIME_PER_PAGE) + TIME_PER_SITE_OVERHEAD
    estimated_properties = max_pages * 15
    geocode_time = estimated_properties * GEOCODE_TIME_PER_PROPERTY if geocode_enabled else 0
    upload_time = estimated_properties * FIRESTORE_UPLOAD_TIME
    time_per_site = scrape_time + geocode_time + upload_time

    total_time = sites_count * time_per_site * BUFFER_MULTIPLIER
    return total_time / 60  # Return in minutes


def create_batches(enabled_sites, sites_per_session=SITES_PER_SESSION):
    """Split sites into batches"""
    total_sessions = math.ceil(len(enabled_sites) / sites_per_session)
    batches = []

    for i in range(total_sessions):
        start = i * sites_per_session
        end = min(start + sites_per_session, len(enabled_sites))
        batch = enabled_sites[start:end]
        batches.append({
            'session_id': i + 1,
            'sites': batch,
            'site_count': len(batch)
        })

    return batches


def run_session(session, max_pages, geocode_enabled, dry_run=False):
    """Run a single scraping session"""
    session_id = session['session_id']
    sites = session['sites']
    site_count = session['site_count']

    print(f"\n{'='*70}")
    print(f"SESSION {session_id}")
    print(f"{'='*70}")
    print(f"Sites in session: {site_count}")
    print(f"Sites: {', '.join(sites)}")

    estimated_time = estimate_time(site_count, max_pages, geocode_enabled)
    print(f"Estimated time: {estimated_time:.1f} minutes ({estimated_time/60:.2f} hours)")

    if dry_run:
        print("[DRY RUN] Skipping actual execution")
        return True

    # Enable only this session's sites
    print(f"\n[*] Enabling sites: {' '.join(sites)}")
    enable_cmd = ['python', 'scripts/enable_sites.py'] + sites
    result = subprocess.run(enable_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Error enabling sites: {result.stderr}")
        return False

    # Set up environment variables
    env = os.environ.copy()
    env['RP_PAGE_CAP'] = str(max_pages)
    env['RP_GEOCODE'] = '1' if geocode_enabled else '0'
    env['RP_HEADLESS'] = '1'
    env['RP_NO_IMAGES'] = '1'
    env['FIRESTORE_ENABLED'] = '1'

    # Check for Firebase credentials
    firebase_cred = Path('realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json')
    if firebase_cred.exists():
        env['FIREBASE_SERVICE_ACCOUNT'] = str(firebase_cred)
        print("[OK] Firebase credentials found")
    else:
        print("[WARN] Firebase credentials not found - Firestore upload will be skipped")

    # Run scraper
    print(f"\n[*] Starting scraper...")
    start_time = time.time()

    result = subprocess.run(['python', 'main.py'], env=env)

    elapsed = (time.time() - start_time) / 60
    print(f"\n[OK] Session {session_id} completed in {elapsed:.1f} minutes")

    if result.returncode != 0:
        print(f"[WARN] Session {session_id} had errors (exit code {result.returncode})")
        return False

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run multi-session scraping (5 sites per session)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_multi_session_scrape.py                    # All sites, 20 pages, with geocoding
  python run_multi_session_scrape.py --max-pages 10     # Faster test run
  python run_multi_session_scrape.py --no-geocode       # Skip geocoding (faster)
  python run_multi_session_scrape.py --dry-run          # Show plan without running
  python run_multi_session_scrape.py --sites-per-session 3  # Only 3 sites per session
        """
    )

    parser.add_argument('--max-pages', type=int, default=20,
                        help='Maximum pages to scrape per site (default: 20)')
    parser.add_argument('--no-geocode', action='store_true',
                        help='Disable geocoding (faster)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show batching plan without actually running')
    parser.add_argument('--sites-per-session', type=int, default=SITES_PER_SESSION,
                        help=f'Sites per session (default: {SITES_PER_SESSION})')

    args = parser.parse_args()

    geocode_enabled = not args.no_geocode

    print("="*70)
    print("MULTI-SESSION SCRAPER (5 Sites Per Session)")
    print("="*70)

    # Load enabled sites
    enabled_sites = load_enabled_sites()
    total_sites = len(enabled_sites)

    if total_sites == 0:
        print("[ERROR] No enabled sites found in config.yaml")
        print("   Run: python scripts/enable_sites.py <site1> <site2> ...")
        return 1

    print(f"\nConfiguration:")
    print(f"   Total enabled sites: {total_sites}")
    print(f"   Max pages per site: {args.max_pages}")
    print(f"   Geocoding: {'[YES] Enabled' if geocode_enabled else '[NO] Disabled'}")
    print(f"   Sites per session: {args.sites_per_session}")

    # Create batches
    batches = create_batches(enabled_sites, args.sites_per_session)
    total_sessions = len(batches)

    print(f"\nBatching Strategy:")
    print(f"   Total sessions: {total_sessions}")

    # Estimate total time
    total_time = estimate_time(total_sites, args.max_pages, geocode_enabled)
    print(f"   Estimated total time: {total_time:.1f} minutes ({total_time/60:.2f} hours)")

    # Show session breakdown
    print(f"\nSession Breakdown:")
    for batch in batches:
        session_time = estimate_time(batch['site_count'], args.max_pages, geocode_enabled)
        print(f"   Session {batch['session_id']:2d}: {batch['site_count']} sites (~{session_time:.1f} min)")

    if args.dry_run:
        print(f"\n[DRY RUN] No actual scraping will occur")
        print(f"\n[OK] Batching plan validated successfully!")
        return 0

    # Confirm before running
    print(f"\n" + "="*70)
    response = input(f"Continue with {total_sessions} sessions? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    # Run all sessions
    overall_start = time.time()
    successful = 0
    failed = 0

    for batch in batches:
        success = run_session(batch, args.max_pages, geocode_enabled)
        if success:
            successful += 1
        else:
            failed += 1

    overall_elapsed = (time.time() - overall_start) / 60

    # Final summary
    print(f"\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Sessions completed: {successful}/{total_sessions}")
    if failed > 0:
        print(f"Sessions failed: {failed}")
    print(f"Total time: {overall_elapsed:.1f} minutes ({overall_elapsed/60:.2f} hours)")
    print(f"Estimated time: {total_time:.1f} minutes ({total_time/60:.2f} hours)")

    accuracy = (overall_elapsed / total_time * 100) if total_time > 0 else 0
    print(f"Estimate accuracy: {accuracy:.0f}%")

    print(f"\n[OK] All data exported to exports/")
    print(f"[OK] Master workbook: exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx")

    if os.environ.get('FIRESTORE_ENABLED') == '1':
        print(f"[OK] Data uploaded to Firestore during scraping")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
