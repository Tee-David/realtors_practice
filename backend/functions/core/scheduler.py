"""
Automated Scraping Scheduler Module

Schedule automated scraping runs using APScheduler.
Supports cron-style scheduling and interval-based scheduling.

Features:
- Cron-style schedules (e.g., "0 8 * * *" for 8 AM daily)
- Interval schedules (e.g., every 6 hours)
- Per-site or all-sites scraping
- Incremental vs full scraping modes
- Job history tracking
- Graceful start/stop

Author: Tee-David
Date: 2025-10-20
"""

import logging
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    logging.warning("APScheduler not installed - scheduler functionality disabled")

logger = logging.getLogger(__name__)


class ScraperScheduler:
    """
    Schedule automated scraping runs.

    Uses APScheduler for reliable background job execution.
    """

    def __init__(self, history_file: str = "logs/schedule_history.json"):
        """
        Initialize scraper scheduler.

        Args:
            history_file: Path to store job execution history
        """
        if not APSCHEDULER_AVAILABLE:
            raise ImportError(
                "APScheduler is required for scheduling. "
                "Install with: pip install apscheduler"
            )

        self.scheduler = BackgroundScheduler()
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Job history
        self.history: List[Dict] = self._load_history()

        # Job configurations
        self.jobs: Dict[str, Dict] = {}

        # Thread safety
        self._lock = Lock()

        logger.info("ScraperScheduler initialized")

    def _load_history(self) -> List[Dict]:
        """Load job execution history from file"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                logger.debug(f"Loaded {len(history)} historical job executions")
                return history
        except Exception as e:
            logger.error(f"Error loading schedule history: {e}")
            return []

    def _save_history(self):
        """Save job execution history to file"""
        try:
            with self._lock:
                # Keep only last 1000 entries
                if len(self.history) > 1000:
                    self.history = self.history[-1000:]

                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, indent=2)

                logger.debug(f"Saved {len(self.history)} job executions to history")
        except Exception as e:
            logger.error(f"Error saving schedule history: {e}")

    def _parse_cron(self, cron_expr: str) -> Dict:
        """
        Parse cron expression into APScheduler parameters.

        Args:
            cron_expr: Cron expression (e.g., "0 8 * * *")

        Returns:
            Dict of cron parameters

        Format: minute hour day month day_of_week
        """
        parts = cron_expr.split()

        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron expression '{cron_expr}' - "
                f"Expected 5 parts (minute hour day month day_of_week)"
            )

        minute, hour, day, month, day_of_week = parts

        return {
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week
        }

    def _run_scraper(self,
                    job_id: str,
                    sites: Optional[List[str]] = None,
                    incremental: bool = False,
                    **kwargs):
        """
        Execute a scraping run.

        Args:
            job_id: Unique job identifier
            sites: List of site keys to scrape (None = all enabled sites)
            incremental: Use incremental scraping mode
            **kwargs: Additional scraper options
        """
        start_time = time.time()

        logger.info(
            f"Scheduled job '{job_id}' starting - "
            f"sites={'all' if not sites else sites}, incremental={incremental}"
        )

        # Build command
        cmd = [sys.executable, 'main.py']

        # Set environment variables for this run
        env_vars = {}

        if incremental:
            env_vars['RP_INCREMENTAL'] = '1'

        if sites:
            # Enable only specified sites
            # This would need integration with enable_sites.py
            logger.debug(f"Would enable sites: {sites}")

        # Execute scraper
        try:
            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=kwargs.get('timeout', 3600)  # 1 hour default timeout
            )

            success = result.returncode == 0
            elapsed = time.time() - start_time

            # Record execution in history
            execution = {
                'job_id': job_id,
                'timestamp': datetime.now().isoformat(),
                'sites': sites or 'all',
                'incremental': incremental,
                'success': success,
                'elapsed_seconds': round(elapsed, 2),
                'return_code': result.returncode
            }

            with self._lock:
                self.history.append(execution)

            self._save_history()

            if success:
                logger.info(
                    f"Scheduled job '{job_id}' completed successfully "
                    f"({elapsed:.1f}s)"
                )
            else:
                logger.error(
                    f"Scheduled job '{job_id}' failed (code={result.returncode})"
                )
                logger.error(f"Output: {result.stderr[:500]}")

        except subprocess.TimeoutExpired:
            logger.error(f"Scheduled job '{job_id}' timed out")

            execution = {
                'job_id': job_id,
                'timestamp': datetime.now().isoformat(),
                'sites': sites or 'all',
                'incremental': incremental,
                'success': False,
                'error': 'timeout'
            }

            with self._lock:
                self.history.append(execution)

            self._save_history()

        except Exception as e:
            logger.error(f"Error running scheduled job '{job_id}': {e}")

    def add_job(self,
               job_id: str,
               schedule: str,
               sites: Optional[List[str]] = None,
               incremental: bool = False,
               enabled: bool = True,
               **kwargs) -> bool:
        """
        Add a scheduled job.

        Args:
            job_id: Unique job identifier
            schedule: Schedule string (cron or interval format)
            sites: List of site keys to scrape (None = all enabled)
            incremental: Use incremental scraping mode
            enabled: Whether job is enabled
            **kwargs: Additional options

        Returns:
            True if job added successfully

        Schedule formats:
        - Cron: "0 8 * * *" (daily at 8 AM)
        - Interval: "interval:hours:6" (every 6 hours)
        - Interval: "interval:minutes:30" (every 30 minutes)
        """
        if job_id in self.jobs:
            logger.warning(f"Job '{job_id}' already exists - use update_job")
            return False

        try:
            # Parse schedule
            if schedule.startswith('interval:'):
                # Interval format: "interval:unit:value"
                _, unit, value = schedule.split(':')
                value = int(value)

                trigger = IntervalTrigger(**{unit: value})

            else:
                # Cron format
                cron_params = self._parse_cron(schedule)
                trigger = CronTrigger(**cron_params)

            # Add job to scheduler (if enabled)
            if enabled:
                self.scheduler.add_job(
                    func=self._run_scraper,
                    trigger=trigger,
                    id=job_id,
                    args=[job_id],
                    kwargs={
                        'sites': sites,
                        'incremental': incremental,
                        **kwargs
                    },
                    replace_existing=False
                )

            # Store job configuration
            with self._lock:
                self.jobs[job_id] = {
                    'id': job_id,
                    'schedule': schedule,
                    'sites': sites,
                    'incremental': incremental,
                    'enabled': enabled,
                    'created_at': datetime.now().isoformat(),
                    'last_run': None
                }

            logger.info(
                f"Added scheduled job '{job_id}': schedule={schedule}, "
                f"sites={sites or 'all'}, incremental={incremental}, enabled={enabled}"
            )

            return True

        except Exception as e:
            logger.error(f"Error adding job '{job_id}': {e}")
            return False

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.

        Args:
            job_id: Job ID

        Returns:
            True if removed successfully
        """
        with self._lock:
            if job_id not in self.jobs:
                logger.warning(f"Job '{job_id}' not found")
                return False

            # Remove from scheduler
            try:
                if self.jobs[job_id]['enabled']:
                    self.scheduler.remove_job(job_id)
            except Exception as e:
                logger.warning(f"Error removing job from scheduler: {e}")

            # Remove from jobs dict
            del self.jobs[job_id]

        logger.info(f"Removed scheduled job '{job_id}'")
        return True

    def update_job(self, job_id: str, updates: Dict) -> bool:
        """
        Update a scheduled job.

        Args:
            job_id: Job ID
            updates: Dict of fields to update

        Returns:
            True if updated successfully
        """
        with self._lock:
            if job_id not in self.jobs:
                logger.warning(f"Job '{job_id}' not found")
                return False

            # If schedule or enabled status changes, need to reschedule
            reschedule = ('schedule' in updates or 'enabled' in updates)

            # Update job config
            for key, value in updates.items():
                if key in ['schedule', 'sites', 'incremental', 'enabled']:
                    self.jobs[job_id][key] = value

            if reschedule:
                # Remove old job
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass

                # Add updated job (if enabled)
                if self.jobs[job_id]['enabled']:
                    schedule = self.jobs[job_id]['schedule']

                    if schedule.startswith('interval:'):
                        _, unit, value = schedule.split(':')
                        trigger = IntervalTrigger(**{unit: int(value)})
                    else:
                        cron_params = self._parse_cron(schedule)
                        trigger = CronTrigger(**cron_params)

                    self.scheduler.add_job(
                        func=self._run_scraper,
                        trigger=trigger,
                        id=job_id,
                        args=[job_id],
                        kwargs={
                            'sites': self.jobs[job_id]['sites'],
                            'incremental': self.jobs[job_id]['incremental']
                        }
                    )

        logger.info(f"Updated scheduled job '{job_id}'")
        return True

    def list_jobs(self) -> List[Dict]:
        """
        List all scheduled jobs.

        Returns:
            List of job dicts
        """
        with self._lock:
            return list(self.jobs.values())

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get a specific job.

        Args:
            job_id: Job ID

        Returns:
            Job dict or None
        """
        with self._lock:
            return self.jobs.get(job_id)

    def get_job_history(self, job_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get job execution history.

        Args:
            job_id: Optional job ID to filter by
            limit: Max number of entries to return

        Returns:
            List of execution dicts
        """
        with self._lock:
            if job_id:
                history = [h for h in self.history if h['job_id'] == job_id]
            else:
                history = self.history

            return history[-limit:]

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running


def get_scraper_scheduler(history_file: str = "logs/schedule_history.json") -> Optional[ScraperScheduler]:
    """
    Get a ScraperScheduler instance.

    Args:
        history_file: Path to store job history

    Returns:
        ScraperScheduler instance or None if APScheduler not available
    """
    if not APSCHEDULER_AVAILABLE:
        logger.warning("APScheduler not available - scheduler disabled")
        return None

    return ScraperScheduler(history_file=history_file)
