"""
Scraper Manager - Manage scraping processes
"""
import os
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ScraperManager:
    """Helper class to manage scraping processes"""

    def __init__(self):
        self.state_file = Path("logs/scraper_state.json")
        self.metadata_file = Path("logs/site_metadata.json")
        self.current_process = None
        self.process_lock = threading.Lock()

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

    def start_scrape(self, sites: List[str] = None, max_pages: int = None, geocoding: bool = None) -> Dict:
        """
        Start a scraping run

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

            # If specific sites requested, enable only those
            if sites:
                # Import here to avoid circular import
                from api.helpers.config_manager import ConfigManager
                config_manager = ConfigManager()

                # Disable all sites first
                try:
                    data = config_manager._load_yaml()
                    for site_key in data.get('sites', {}).keys():
                        data['sites'][site_key]['enabled'] = site_key in sites

                    config_manager._save_yaml(data)
                except Exception as e:
                    logger.error(f"Error configuring sites: {e}")
                    return {
                        'success': False,
                        'error': f'Failed to configure sites: {str(e)}'
                    }

            # Start scraper process
            try:
                # Run main.py in background
                self.current_process = subprocess.Popen(
                    ['python', 'main.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )

                # Update state
                run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                current_run = {
                    'run_id': run_id,
                    'started_at': datetime.now().isoformat(),
                    'sites': sites or 'all_enabled',
                    'max_pages': max_pages,
                    'geocoding': geocoding,
                    'pid': self.current_process.pid
                }

                state = {
                    'is_running': True,
                    'current_run': current_run,
                    'last_run': state.get('last_run')
                }
                self._save_state(state)

                # Start monitoring thread
                monitor_thread = threading.Thread(
                    target=self._monitor_process,
                    args=(self.current_process, run_id)
                )
                monitor_thread.daemon = True
                monitor_thread.start()

                logger.info(f"Started scraping run: {run_id}")

                return {
                    'success': True,
                    'run_id': run_id,
                    'message': 'Scraping started successfully',
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
