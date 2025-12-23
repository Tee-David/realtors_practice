"""
Scraper Manager - Manage scraping processes with intelligent batching
"""
import os
import json
import subprocess
import threading
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


class ScraperManager:
    """Helper class to manage scraping processes with intelligent batching"""

    def __init__(self):
        self.state_file = Path("logs/scraper_state.json")
        self.metadata_file = Path("logs/site_metadata.json")
        self.progress_file = Path("logs/batch_progress.json")
        self.config_file = Path("config.yaml")
        self.current_process = None
        self.process_lock = threading.Lock()
        self.batch_stats = {
            'total_time': 0,
            'total_sites': 0,
            'failed_sites': [],
            'retry_count': 0
        }

    def _load_state(self) -> Dict:
        """Load current scraper state"""
        if not self.state_file.exists():
            return {
                'is_running': False,
                'current_run': None,
                'last_run': None
            }

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {
                'is_running': False,
                'current_run': None,
                'last_run': None
            }

    def _save_state(self, state: Dict):
        """Save scraper state"""
        try:
            os.makedirs(self.state_file.parent, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

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

    def _save_progress(self, progress: Dict):
        """Save real-time progress data"""
        try:
            os.makedirs(self.progress_file.parent, exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def _load_progress(self) -> Dict:
        """Load real-time progress data"""
        if not self.progress_file.exists():
            return {}
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            return {}

    def _get_site_priority(self, site_key: str, config_data: Dict) -> int:
        """Get priority for a site (lower number = higher priority)"""
        site_config = config_data.get('sites', {}).get(site_key, {})
        metadata = site_config.get('metadata', {})
        return metadata.get('priority', 999)  # Default to low priority

    def _calculate_optimal_batch_size(self, total_sites: int) -> int:
        """Calculate optimal batch size based on site count and environment"""
        # Get override from environment
        env_batch_size = os.environ.get('RP_BATCH_SIZE')
        if env_batch_size:
            try:
                return int(env_batch_size)
            except ValueError:
                pass

        # Auto-calculate based on site count
        if total_sites <= 10:
            return total_sites  # No batching needed for small jobs
        elif total_sites <= 30:
            return 10
        elif total_sites <= 50:
            return 15
        else:
            return 20

    def _split_into_batches(self, sites: List[str], batch_size: int = None) -> List[List[str]]:
        """
        Split sites into optimal batches with priority sorting

        Args:
            sites: List of site keys to scrape
            batch_size: Override automatic batch sizing

        Returns:
            List of batches (each batch is a list of site keys)
        """
        if not sites:
            return []

        # Load config to get priorities
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config for priority sorting: {e}")
            config_data = {}

        # Sort sites by priority (lower number = higher priority = scraped first)
        sorted_sites = sorted(
            sites,
            key=lambda s: self._get_site_priority(s, config_data)
        )

        # Calculate batch size if not provided
        if batch_size is None:
            batch_size = self._calculate_optimal_batch_size(len(sorted_sites))

        # Split into batches
        batches = []
        for i in range(0, len(sorted_sites), batch_size):
            batch = sorted_sites[i:i + batch_size]
            batches.append(batch)

        logger.info(f"Split {len(sorted_sites)} sites into {len(batches)} batches (size={batch_size})")
        return batches

    def _get_resource_usage(self) -> Dict:
        """Get current system resource usage"""
        if not HAS_PSUTIL:
            return {'memory_percent': 0, 'cpu_percent': 0}

        try:
            process = psutil.Process()
            return {
                'memory_percent': round(process.memory_percent(), 1),
                'cpu_percent': round(process.cpu_percent(interval=0.1), 1)
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {'memory_percent': 0, 'cpu_percent': 0}

    def _calculate_eta(self, completed_sites: int, total_sites: int, elapsed_seconds: float) -> Dict:
        """Calculate estimated time to completion"""
        if completed_sites == 0:
            return {
                'estimated_remaining_seconds': None,
                'estimated_completion': None,
                'average_seconds_per_site': None
            }

        avg_time = elapsed_seconds / completed_sites
        remaining_sites = total_sites - completed_sites
        remaining_seconds = int(avg_time * remaining_sites)

        completion_time = datetime.now() + timedelta(seconds=remaining_seconds)

        return {
            'estimated_remaining_seconds': remaining_seconds,
            'estimated_completion': completion_time.isoformat(),
            'average_seconds_per_site': round(avg_time, 2)
        }

    def _update_batch_progress(self, state: Dict, batch_num: int, total_batches: int,
                              batch_sites: List[str], status: str = 'in_progress'):
        """Update real-time batch progress in state"""
        current_run = state.get('current_run', {})

        # Update batch info
        current_run['batch_info'] = {
            'total_batches': total_batches,
            'current_batch': batch_num,
            'current_batch_sites': batch_sites,
            'batch_status': status
        }

        # Calculate progress
        progress_data = self._load_progress()
        completed_sites = len(progress_data.get('completed', []))
        failed_sites = len(progress_data.get('failed', []))
        total_sites = len(current_run.get('sites', []))

        current_run['progress'] = {
            'total_sites': total_sites,
            'completed_sites': completed_sites,
            'in_progress_sites': len(batch_sites) if status == 'in_progress' else 0,
            'failed_sites': failed_sites,
            'pending_sites': total_sites - completed_sites - failed_sites - len(batch_sites)
        }

        # Calculate timing
        start_time = datetime.fromisoformat(current_run.get('started_at'))
        elapsed = (datetime.now() - start_time).total_seconds()
        eta_info = self._calculate_eta(completed_sites, total_sites, elapsed)

        current_run['timing'] = {
            'elapsed_seconds': int(elapsed),
            **eta_info
        }

        # Add resource usage
        current_run['resources'] = self._get_resource_usage()

        # Save updated state
        self._save_state(state)

    def _execute_single_batch(self, batch_sites: List[str], env: Dict, config_manager) -> Dict:
        """
        Execute a single batch of sites

        Args:
            batch_sites: List of site keys for this batch
            env: Environment variables
            config_manager: ConfigManager instance

        Returns:
            Dict with success status and details
        """
        try:
            # Enable only this batch's sites
            data = config_manager._load_yaml()
            for site_key in data.get('sites', {}).keys():
                data['sites'][site_key]['enabled'] = site_key in batch_sites
            config_manager._save_yaml(data)

            logger.info(f"Executing batch with sites: {batch_sites}")

            # Run main.py for this batch
            process = subprocess.Popen(
                ['python', 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )

            # Wait for completion
            stdout, stderr = process.communicate()

            success = process.returncode == 0

            if not success:
                logger.error(f"Batch failed with return code {process.returncode}")
                if stderr:
                    logger.error(f"Stderr: {stderr[:500]}")

            return {
                'success': success,
                'return_code': process.returncode,
                'sites': batch_sites,
                'stdout': stdout[-1000:] if stdout else '',  # Last 1000 chars
                'stderr': stderr[-1000:] if stderr else ''
            }

        except Exception as e:
            logger.error(f"Error executing batch: {e}")
            return {
                'success': False,
                'error': str(e),
                'sites': batch_sites
            }

    def start_scrape(self, sites: List[str] = None, max_pages: int = None, geocoding: bool = None) -> Dict:
        """
        Start a scraping run with intelligent batching

        Args:
            sites: List of site keys to scrape (empty = all enabled)
            max_pages: Override max pages
            geocoding: Override geocoding setting
        """
        with self.process_lock:
            # Check if already running
            state = self._load_state()
            if state.get('is_running', False):
                return {
                    'success': False,
                    'error': 'Scraper is already running',
                    'current_run': state.get('current_run')
                }

            # Prepare environment variables
            env = os.environ.copy()

            if max_pages is not None:
                env['RP_PAGE_CAP'] = str(max_pages)

            if geocoding is not None:
                env['RP_GEOCODE'] = '1' if geocoding else '0'

            # Determine which sites to scrape
            from api.helpers.config_manager import ConfigManager
            config_manager = ConfigManager()

            try:
                data = config_manager._load_yaml()

                if sites:
                    # Use specified sites
                    target_sites = sites
                else:
                    # Get all enabled sites
                    target_sites = [
                        site_key for site_key, site_config in data.get('sites', {}).items()
                        if site_config.get('enabled', False)
                    ]

                if not target_sites:
                    return {
                        'success': False,
                        'error': 'No sites to scrape (none enabled or specified)'
                    }

                logger.info(f"Starting scrape for {len(target_sites)} sites")

                # Split into batches
                batches = self._split_into_batches(target_sites)
                total_batches = len(batches)

                logger.info(f"Split into {total_batches} batches")

                # Initialize run state
                run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                current_run = {
                    'run_id': run_id,
                    'started_at': datetime.now().isoformat(),
                    'sites': target_sites,
                    'max_pages': max_pages,
                    'geocoding': geocoding,
                    'batch_info': {
                        'total_batches': total_batches,
                        'current_batch': 0,
                        'current_batch_sites': [],
                        'batch_status': 'initializing'
                    },
                    'progress': {
                        'total_sites': len(target_sites),
                        'completed_sites': 0,
                        'in_progress_sites': 0,
                        'failed_sites': 0,
                        'pending_sites': len(target_sites)
                    }
                }

                state = {
                    'is_running': True,
                    'current_run': current_run,
                    'last_run': state.get('last_run')
                }
                self._save_state(state)

                # Initialize progress tracking
                progress_data = {
                    'completed': [],
                    'failed': [],
                    'in_progress': []
                }
                self._save_progress(progress_data)

                # Start batch execution in background thread
                execution_thread = threading.Thread(
                    target=self._execute_batches,
                    args=(batches, env, config_manager, run_id, state)
                )
                execution_thread.daemon = True
                execution_thread.start()

                logger.info(f"Started scraping run: {run_id}")

                return {
                    'success': True,
                    'run_id': run_id,
                    'message': f'Scraping started successfully ({len(target_sites)} sites in {total_batches} batches)',
                    'current_run': current_run
                }

            except Exception as e:
                logger.error(f"Error starting scrape: {e}")

                # Reset state
                state['is_running'] = False
                state['current_run'] = None
                self._save_state(state)

                return {
                    'success': False,
                    'error': str(e)
                }

    def _execute_batches(self, batches: List[List[str]], env: Dict, config_manager, run_id: str, state: Dict):
        """
        Execute all batches sequentially with retry logic

        Args:
            batches: List of batches (each batch is a list of site keys)
            env: Environment variables
            config_manager: ConfigManager instance
            run_id: Run identifier
            state: Current state dict
        """
        try:
            total_batches = len(batches)
            failed_batches = []

            for batch_num, batch_sites in enumerate(batches, start=1):
                logger.info(f"Starting batch {batch_num}/{total_batches} with {len(batch_sites)} sites")

                # Update state - batch starting
                state = self._load_state()
                progress_data = self._load_progress()
                progress_data['in_progress'] = batch_sites
                self._save_progress(progress_data)
                self._update_batch_progress(state, batch_num, total_batches, batch_sites, 'in_progress')

                # Execute batch
                result = self._execute_single_batch(batch_sites, env, config_manager)

                # Update progress based on result
                progress_data = self._load_progress()
                progress_data['in_progress'] = []

                if result['success']:
                    # Mark batch sites as completed
                    progress_data['completed'].extend(batch_sites)
                    logger.info(f"Batch {batch_num}/{total_batches} completed successfully")
                else:
                    # Retry logic - one retry per batch
                    logger.warning(f"Batch {batch_num}/{total_batches} failed, retrying in 30 seconds...")
                    time.sleep(30)

                    retry_result = self._execute_single_batch(batch_sites, env, config_manager)

                    if retry_result['success']:
                        progress_data['completed'].extend(batch_sites)
                        logger.info(f"Batch {batch_num}/{total_batches} succeeded on retry")
                    else:
                        # Mark as failed after retry
                        progress_data['failed'].extend(batch_sites)
                        failed_batches.append({
                            'batch_num': batch_num,
                            'sites': batch_sites,
                            'error': retry_result.get('error', 'Unknown error')
                        })
                        logger.error(f"Batch {batch_num}/{total_batches} failed after retry")

                self._save_progress(progress_data)

                # Update batch progress
                state = self._load_state()
                self._update_batch_progress(state, batch_num, total_batches, batch_sites, 'completed')

                # Check if pause requested
                if state.get('current_run', {}).get('paused', False):
                    logger.info(f"Pause requested after batch {batch_num}/{total_batches}")

                    # Wait for resume
                    while state.get('current_run', {}).get('paused', False):
                        logger.info("Scraper paused. Waiting for resume...")
                        time.sleep(5)
                        state = self._load_state()

                        # Check if stopped while paused
                        if not state.get('is_running', False):
                            logger.info("Scraper stopped while paused")
                            return

                    logger.info(f"Scraper resumed, continuing with batch {batch_num + 1}")

                # Small delay between batches
                if batch_num < total_batches:
                    time.sleep(5)

            # All batches completed - finalize state
            state = self._load_state()
            current_run = state.get('current_run', {})
            current_run['completed_at'] = datetime.now().isoformat()
            current_run['success'] = len(failed_batches) == 0
            current_run['failed_batches'] = failed_batches

            # Calculate final statistics
            progress_data = self._load_progress()
            current_run['final_stats'] = {
                'total_sites': len(current_run.get('sites', [])),
                'successful_sites': len(progress_data.get('completed', [])),
                'failed_sites': len(progress_data.get('failed', [])),
                'failed_batches': len(failed_batches)
            }

            state['last_run'] = current_run
            state['is_running'] = False
            state['current_run'] = None
            self._save_state(state)

            logger.info(f"Scraping run {run_id} completed: {current_run['final_stats']}")

        except Exception as e:
            logger.error(f"Error in batch execution: {e}")

            # Update state with error
            state = self._load_state()
            if state.get('current_run'):
                current_run = state['current_run']
                current_run['completed_at'] = datetime.now().isoformat()
                current_run['success'] = False
                current_run['error'] = str(e)
                state['last_run'] = current_run

            state['is_running'] = False
            state['current_run'] = None
            self._save_state(state)

    def _monitor_process(self, process, run_id: str):
        """Monitor scraper process and update state when complete"""
        try:
            stdout, stderr = process.communicate()

            # Process completed
            state = self._load_state()
            current_run = state.get('current_run', {})
            current_run['completed_at'] = datetime.now().isoformat()
            current_run['return_code'] = process.returncode
            current_run['success'] = process.returncode == 0

            # Save as last run
            state['last_run'] = current_run
            state['is_running'] = False
            state['current_run'] = None
            self._save_state(state)

            logger.info(f"Scraping run {run_id} completed with code {process.returncode}")

        except Exception as e:
            logger.error(f"Error monitoring process: {e}")

    def get_status(self) -> Dict:
        """Get current scraping status"""
        state = self._load_state()
        metadata = self._load_metadata()

        result = {
            'is_running': state.get('is_running', False),
            'current_run': state.get('current_run'),
            'last_run': state.get('last_run')
        }

        # Add site metadata
        if metadata:
            result['site_metadata'] = metadata

        return result

    def stop_scrape(self) -> Dict:
        """Stop current scraping run"""
        with self.process_lock:
            state = self._load_state()

            if not state.get('is_running', False):
                return {
                    'success': False,
                    'error': 'No scraper is currently running'
                }

            try:
                if self.current_process and self.current_process.poll() is None:
                    # Terminate process
                    self.current_process.terminate()

                    # Wait for process to end (with timeout)
                    try:
                        self.current_process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # Force kill if not terminated
                        self.current_process.kill()
                        self.current_process.wait()

                    logger.info("Scraper process stopped")

                # Update state
                current_run = state.get('current_run', {})
                current_run['stopped_at'] = datetime.now().isoformat()
                current_run['stopped_manually'] = True

                state['last_run'] = current_run
                state['is_running'] = False
                state['current_run'] = None
                self._save_state(state)

                return {
                    'success': True,
                    'message': 'Scraper stopped successfully'
                }

            except Exception as e:
                logger.error(f"Error stopping scraper: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

    def pause_scrape(self) -> Dict:
        """
        Pause current scraping run

        Pauses after the current batch completes.
        """
        with self.process_lock:
            state = self._load_state()

            if not state.get('is_running', False):
                return {
                    'success': False,
                    'error': 'No scraper is currently running'
                }

            current_run = state.get('current_run', {})

            # Check if already paused
            if current_run.get('paused', False):
                return {
                    'success': False,
                    'error': 'Scraper is already paused'
                }

            # Set pause flag
            current_run['paused'] = True
            current_run['paused_at'] = datetime.now().isoformat()

            state['current_run'] = current_run
            self._save_state(state)

            logger.info("Scraper pause requested (will pause after current batch)")

            return {
                'success': True,
                'message': 'Scraper will pause after current batch completes',
                'current_batch': current_run.get('batch_info', {}).get('current_batch'),
                'total_batches': current_run.get('batch_info', {}).get('total_batches')
            }

    def resume_scrape(self) -> Dict:
        """
        Resume paused scraping run

        Resumes from the next pending batch.
        """
        with self.process_lock:
            state = self._load_state()

            if not state.get('is_running', False):
                return {
                    'success': False,
                    'error': 'No scraper is currently running'
                }

            current_run = state.get('current_run', {})

            # Check if paused
            if not current_run.get('paused', False):
                return {
                    'success': False,
                    'error': 'Scraper is not paused'
                }

            # Clear pause flag
            current_run['paused'] = False
            current_run['resumed_at'] = datetime.now().isoformat()

            state['current_run'] = current_run
            self._save_state(state)

            logger.info("Scraper resumed")

            return {
                'success': True,
                'message': 'Scraper resumed successfully',
                'current_batch': current_run.get('batch_info', {}).get('current_batch'),
                'total_batches': current_run.get('batch_info', {}).get('total_batches')
            }

    def get_history(self, limit: int = 20) -> Dict:
        """
        Get scraping history

        Args:
            limit: Number of recent runs to return
        """
        # For now, return last run from state
        # In production, store full history in a database or log file
        state = self._load_state()
        metadata = self._load_metadata()

        history = []

        # Add last run if exists
        if state.get('last_run'):
            history.append(state['last_run'])

        # Add site metadata as historical data
        for site_key, site_meta in metadata.items():
            if 'last_successful_scrape' in site_meta:
                history.append({
                    'site_key': site_key,
                    'timestamp': site_meta.get('last_successful_scrape'),
                    'count': site_meta.get('last_count', 0)
                })

        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            'total': len(history),
            'limit': limit,
            'history': history[:limit]
        }
