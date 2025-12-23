"""
Log Parser - Parse and filter log files
"""
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LogParser:
    """Helper class to parse and filter log files"""

    def __init__(self):
        self.logs_dir = Path("logs")
        self.main_log = self.logs_dir / "scraper.log"
        self.watcher_log = Path("exports/cleaned/watcher.log")
        self.errors_log = Path("exports/cleaned/errors.log")

    def parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse a log line into structured format
        Format: 2025-10-05 11:49:27 - INFO - message
        """
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)$'
        match = re.match(pattern, line.strip())

        if match:
            timestamp_str, level, message = match.groups()
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                return {
                    'timestamp': timestamp.isoformat(),
                    'level': level,
                    'message': message
                }
            except ValueError:
                pass

        return None

    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> Dict:
        """
        Get recent logs

        Args:
            limit: Number of log lines to return
            level: Filter by log level (INFO, WARNING, ERROR)
        """
        logs = []

        if not self.main_log.exists():
            return {
                'total': 0,
                'logs': []
            }

        try:
            with open(self.main_log, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last N lines efficiently
                lines = self._tail(f, limit * 2)  # Read more to account for filtering

                for line in lines:
                    parsed = self.parse_log_line(line)
                    if parsed:
                        # Apply level filter
                        if level and parsed['level'] != level:
                            continue

                        logs.append(parsed)

                        if len(logs) >= limit:
                            break

        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return {
                'error': str(e),
                'total': 0,
                'logs': []
            }

        # Reverse to show newest first
        logs.reverse()

        return {
            'total': len(logs),
            'filter': {'level': level} if level else {},
            'logs': logs
        }

    def get_errors(self, limit: int = 50) -> Dict:
        """Get error logs only"""
        return self.get_logs(limit=limit, level='ERROR')

    def get_site_logs(self, site_key: str, limit: int = 100) -> Dict:
        """
        Get logs for a specific site

        Args:
            site_key: Site identifier
            limit: Number of log lines
        """
        logs = []

        if not self.main_log.exists():
            return {
                'site_key': site_key,
                'total': 0,
                'logs': []
            }

        try:
            with open(self.main_log, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last N lines
                lines = self._tail(f, limit * 5)  # Read more to account for filtering

                for line in lines:
                    # Check if line mentions the site
                    if site_key.lower() in line.lower():
                        parsed = self.parse_log_line(line)
                        if parsed:
                            logs.append(parsed)

                            if len(logs) >= limit:
                                break

        except Exception as e:
            logger.error(f"Error reading logs for {site_key}: {e}")
            return {
                'site_key': site_key,
                'error': str(e),
                'total': 0,
                'logs': []
            }

        # Reverse to show newest first
        logs.reverse()

        return {
            'site_key': site_key,
            'total': len(logs),
            'logs': logs
        }

    def get_watcher_logs(self, limit: int = 100) -> Dict:
        """Get watcher service logs"""
        logs = []

        if not self.watcher_log.exists():
            return {
                'total': 0,
                'logs': []
            }

        try:
            with open(self.watcher_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = self._tail(f, limit)

                for line in lines:
                    parsed = self.parse_log_line(line)
                    if parsed:
                        logs.append(parsed)

        except Exception as e:
            logger.error(f"Error reading watcher logs: {e}")
            return {
                'error': str(e),
                'total': 0,
                'logs': []
            }

        # Reverse to show newest first
        logs.reverse()

        return {
            'total': len(logs),
            'logs': logs
        }

    def _tail(self, file_handle, n: int) -> List[str]:
        """
        Read last N lines from file efficiently

        Args:
            file_handle: Open file handle
            n: Number of lines to read

        Returns:
            List of last N lines
        """
        # Read all lines (for simplicity)
        # For very large files, use a more efficient approach
        all_lines = file_handle.readlines()
        return all_lines[-n:] if len(all_lines) > n else all_lines
