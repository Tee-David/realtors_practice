# watcher.py
"""
Export Watcher Service

Monitors exports/ folder for new CSV/XLSX files and processes them through
cleaning pipeline. Cleaned data is exported to individual site folders.

Usage:
    python watcher.py --once              # Process all files once
    python watcher.py --watch             # Continuous monitoring
    python watcher.py --reset-state       # Reset processing state
    python watcher.py --dry-run           # Simulate without writing
"""

import sys
import os
import json
import hashlib
import logging
import time
import signal
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import argparse

# Service state
STATE_FILE = Path("exports/cleaned/.watcher_state.json")
EXPORTS_DIR = Path("exports/sites")  # Site exports are in exports/sites/
CLEANED_DIR = Path("exports/cleaned")

# Ensure cleaned directory exists for logging
CLEANED_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CLEANED_DIR / "watcher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM for graceful shutdown."""
    global shutdown_requested
    shutdown_requested = True
    logging.info("Shutdown signal received, finishing current processing...")


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Failed to hash {file_path}: {e}")
        return ""


class WatcherState:
    """Manages watcher service state (processed files tracking)."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.processed_files: Dict[str, Dict] = {}
        self.load()

    def load(self):
        """Load state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_files = data.get('processed_files', {})
                logging.info(f"Loaded state: {len(self.processed_files)} processed files")
            except Exception as e:
                logging.warning(f"Failed to load state: {e}, starting fresh")
                self.processed_files = {}
        else:
            logging.info("No existing state file, starting fresh")
            self.processed_files = {}

    def save(self):
        """Save state to disk."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'processed_files': self.processed_files,
                'last_updated': datetime.now().isoformat()
            }
            # Atomic write using temp file
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.state_file)
            logging.debug(f"State saved: {len(self.processed_files)} files")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    def is_processed(self, file_path: Path, file_hash: str) -> bool:
        """Check if file already processed (by path and hash)."""
        file_key = str(file_path.relative_to(EXPORTS_DIR))
        if file_key in self.processed_files:
            stored_hash = self.processed_files[file_key].get('hash', '')
            return stored_hash == file_hash
        return False

    def mark_processed(self, file_path: Path, file_hash: str, record_count: int):
        """Mark file as processed."""
        file_key = str(file_path.relative_to(EXPORTS_DIR))
        self.processed_files[file_key] = {
            'hash': file_hash,
            'timestamp': datetime.now().isoformat(),
            'record_count': record_count,
            'size_bytes': file_path.stat().st_size
        }

    def reset(self):
        """Clear all processed files state."""
        self.processed_files = {}
        self.save()
        logging.info("State reset complete")


class ExportScanner:
    """Scans exports/sites/ folder for CSV/XLSX files."""

    def __init__(self, exports_dir: Path):
        self.exports_dir = exports_dir

    def scan(self) -> List[Path]:
        """Scan exports/sites/ for all CSV and XLSX files."""
        files = []

        # Ensure exports_dir exists
        if not self.exports_dir.exists():
            logging.warning(f"Exports directory does not exist: {self.exports_dir}")
            return []

        # Scan all site directories
        for site_dir in self.exports_dir.iterdir():
            if not site_dir.is_dir():
                continue

            # Find all CSV and XLSX files
            for file in site_dir.iterdir():
                if file.suffix.lower() in ['.csv', '.xlsx']:
                    # Skip temp files (like ~$*.xlsx)
                    if file.name.startswith('~$'):
                        continue
                    files.append(file)

        # Sort by modification time (oldest first)
        files.sort(key=lambda f: f.stat().st_mtime)
        return files

    def get_new_files(self, state: WatcherState) -> List[Path]:
        """Get files that need processing (new or changed)."""
        all_files = self.scan()
        new_files = []

        for file_path in all_files:
            file_hash = compute_file_hash(file_path)
            if not file_hash:
                continue

            if not state.is_processed(file_path, file_hash):
                new_files.append(file_path)

        return new_files


def write_error_report(error_log: List[Dict]):
    """Write error summary report to file."""
    try:
        error_file = CLEANED_DIR / "errors.log"

        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Error Report - {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n\n")

            for i, err in enumerate(error_log, 1):
                f.write(f"{i}. {err['type'].upper()}\n")
                f.write(f"   File: {err['file']}\n")
                f.write(f"   Error: {err['error']}\n\n")

            f.write(f"Total Errors: {len(error_log)}\n")

        logging.info(f"Error report written: {error_file} ({len(error_log)} errors)")
    except Exception as e:
        logging.error(f"Failed to write error report: {e}")


def process_file(file_path: Path, state: WatcherState, dry_run: bool = False, error_log: List = None) -> int:
    """
    Process a single export file.

    Returns number of new records added.
    """
    logging.info(f"Processing: {file_path}")

    # Import processing modules
    from core.data_cleaner import clean_and_normalize

    try:
        # Step 1: Read and clean data
        cleaned_records = clean_and_normalize(file_path)
        logging.info(f"  Cleaned {len(cleaned_records)} records from {file_path.name}")

        if not cleaned_records:
            logging.warning(f"  No valid records in {file_path}")
            if error_log is not None:
                error_log.append({
                    'file': str(file_path),
                    'error': 'No valid records after cleaning',
                    'type': 'validation'
                })
            return 0

        # Step 2: Determine site from file path
        site_key = file_path.parent.name

        # Step 3: Export cleaned data to individual site folder
        site_cleaned_dir = CLEANED_DIR / site_key
        site_cleaned_dir.mkdir(parents=True, exist_ok=True)

        output_file = site_cleaned_dir / f"{site_key}_cleaned.csv"

        if not dry_run:
            import pandas as pd
            df = pd.DataFrame(cleaned_records)
            df.to_csv(output_file, index=False)
            logging.info(f"  Exported {len(cleaned_records)} records to {output_file}")
        else:
            logging.info(f"  [DRY RUN] Would export {len(cleaned_records)} records to {output_file}")

        # Step 4: Mark file as processed
        if not dry_run:
            file_hash = compute_file_hash(file_path)
            state.mark_processed(file_path, file_hash, len(cleaned_records))
            state.save()

        return len(cleaned_records)

    except Exception as e:
        logging.error(f"Failed to process {file_path}: {e}", exc_info=True)
        if error_log is not None:
            error_log.append({
                'file': str(file_path),
                'error': str(e),
                'type': 'processing_error'
            })
        return 0


def run_once(state: WatcherState, dry_run: bool = False, verbose: bool = False):
    """Process all pending files once and exit (with optional parallel processing)."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scanner = ExportScanner(EXPORTS_DIR)
    new_files = scanner.get_new_files(state)

    if not new_files:
        logging.info("No new or changed files to process")
        return

    logging.info(f"Found {len(new_files)} files to process")

    # PARALLEL PROCESSING (NEW!)
    # Use parallel processing if we have multiple files and it's enabled
    use_parallel = len(new_files) > 1 and os.getenv("RP_WATCHER_PARALLEL", "1") == "1"

    if use_parallel:
        # Parallel processing with ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Get max workers (default: 3, safe for GitHub Actions)
        max_workers = int(os.getenv("RP_WATCHER_WORKERS", "3"))
        max_workers = min(max_workers, len(new_files), 4)  # Cap at 4 for safety

        logging.info(f"Using parallel processing: {max_workers} workers")

        total_records = 0
        processed_count = 0
        error_log = []

        # Optional progress bar
        try:
            from tqdm import tqdm
            use_tqdm = True
        except ImportError:
            use_tqdm = False

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="watcher") as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(process_file, file_path, state, dry_run, error_log): file_path
                for file_path in new_files
            }

            # Process results as they complete
            if use_tqdm:
                with tqdm(total=len(new_files), desc="Processing files", unit="file") as pbar:
                    for future in as_completed(future_to_file):
                        if shutdown_requested:
                            logging.info("Shutdown requested, stopping processing")
                            break

                        file_path = future_to_file[future]
                        try:
                            record_count = future.result()
                            total_records += record_count
                            processed_count += 1
                            pbar.set_postfix({"records": total_records}, refresh=True)
                        except Exception as e:
                            logging.error(f"Failed to process {file_path}: {e}")
                        finally:
                            pbar.update(1)
            else:
                # No progress bar
                for future in as_completed(future_to_file):
                    if shutdown_requested:
                        logging.info("Shutdown requested, stopping processing")
                        break

                    file_path = future_to_file[future]
                    try:
                        record_count = future.result()
                        total_records += record_count
                        processed_count += 1
                    except Exception as e:
                        logging.error(f"Failed to process {file_path}: {e}")
    else:
        # Sequential processing (original behavior)
        if not use_parallel:
            logging.info("Using sequential processing (RP_WATCHER_PARALLEL=0 or single file)")

        total_records = 0
        processed_count = 0
        error_log = []

        for file_path in new_files:
            if shutdown_requested:
                logging.info("Shutdown requested, stopping processing")
                break

            record_count = process_file(file_path, state, dry_run, error_log)
            total_records += record_count
            processed_count += 1

    logging.info(f"Processing complete: {processed_count} files, {total_records} total records")

    # Write error summary report if there were errors
    if error_log and not dry_run:
        write_error_report(error_log)


def run_watch(state: WatcherState, interval: int = 60, verbose: bool = False):
    """Continuously watch for new files."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info(f"Starting watch mode (checking every {interval}s)")
    logging.info("Press Ctrl+C to stop")

    scanner = ExportScanner(EXPORTS_DIR)

    while not shutdown_requested:
        try:
            new_files = scanner.get_new_files(state)
            error_log = []

            if new_files:
                logging.info(f"Found {len(new_files)} new/changed files")
                for file_path in new_files:
                    if shutdown_requested:
                        break
                    process_file(file_path, state, dry_run=False, error_log=error_log)

                # Write error report if there were errors
                if error_log:
                    write_error_report(error_log)
            else:
                logging.debug("No new files")

            # Sleep in small intervals to allow graceful shutdown
            for _ in range(interval):
                if shutdown_requested:
                    break
                time.sleep(1)

        except Exception as e:
            logging.error(f"Watch loop error: {e}", exc_info=True)
            time.sleep(interval)

    logging.info("Watch mode stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export Watcher Service - Process real estate scraper exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watcher.py --once              # Process all pending files once
  python watcher.py --watch             # Continuously monitor for changes
  python watcher.py --reset-state       # Reset processing state
  python watcher.py --dry-run --once    # Simulate processing
        """
    )

    parser.add_argument('--once', action='store_true',
                        help='Process all pending files once and exit')
    parser.add_argument('--watch', action='store_true',
                        help='Continuously watch for new files')
    parser.add_argument('--reset-state', action='store_true',
                        help='Reset processing state (all files will be reprocessed)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate processing without writing output')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose debug logging')
    parser.add_argument('--interval', type=int, default=60,
                        help='Watch mode check interval in seconds (default: 60)')

    args = parser.parse_args()

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Ensure cleaned directory exists
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize state
    state = WatcherState(STATE_FILE)

    # Reset state if requested
    if args.reset_state:
        logging.info("Resetting watcher state...")
        state.reset()
        if not (args.once or args.watch):
            logging.info("State reset complete. Use --once or --watch to process files.")
            return

    # Run requested mode
    if args.watch:
        run_watch(state, interval=args.interval, verbose=args.verbose)
    elif args.once or args.dry_run:
        run_once(state, dry_run=args.dry_run, verbose=args.verbose)
    else:
        parser.print_help()
        print("\nError: Must specify --once or --watch")
        sys.exit(1)


if __name__ == "__main__":
    main()
