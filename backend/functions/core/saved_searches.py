"""
Saved Searches & Alerts Module

Allows users to save search criteria and get alerts when new matching listings appear.
Searches are stored in JSON format and can be checked periodically for new matches.

Features:
- Save complex search criteria
- Check for new matches against saved criteria
- Email/SMS alerts (basic implementation)
- Search history tracking

Author: Tee-David
Date: 2025-10-20
"""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class SavedSearchManager:
    """
    Manage saved searches and alerts for users.

    Searches are stored in JSON files in logs/saved_searches/
    """

    def __init__(self, storage_dir: str = "logs/saved_searches"):
        """
        Initialize saved search manager.

        Args:
            storage_dir: Directory to store saved searches
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.searches_file = self.storage_dir / "searches.json"
        self.history_file = self.storage_dir / "search_history.json"

        # Load existing searches
        self.searches: Dict[str, Dict] = self._load_searches()

        # Thread safety
        self._lock = Lock()

        logger.debug(
            f"SavedSearchManager initialized: {len(self.searches)} saved searches"
        )

    def _load_searches(self) -> Dict[str, Dict]:
        """Load saved searches from file"""
        if not self.searches_file.exists():
            logger.debug("No saved searches file found - starting fresh")
            return {}

        try:
            with open(self.searches_file, 'r', encoding='utf-8') as f:
                searches = json.load(f)
                logger.info(f"Loaded {len(searches)} saved searches")
                return searches
        except Exception as e:
            logger.error(f"Error loading saved searches: {e}")
            return {}

    def _save_searches(self):
        """Save searches to file"""
        try:
            with self._lock:
                with open(self.searches_file, 'w', encoding='utf-8') as f:
                    json.dump(self.searches, f, indent=2)

                logger.debug(f"Saved {len(self.searches)} searches to file")
        except Exception as e:
            logger.error(f"Error saving searches: {e}")

    def create_search(self,
                     user_id: str,
                     name: str,
                     criteria: Dict,
                     alert_frequency: str = "daily") -> str:
        """
        Create a new saved search.

        Args:
            user_id: Unique user identifier
            name: Human-readable search name
            criteria: Search criteria (filters dict compatible with query_engine)
            alert_frequency: How often to send alerts ("realtime", "daily", "weekly", "disabled")

        Returns:
            search_id: Unique ID for the saved search

        Example criteria:
        {
            "filters": {
                "bedrooms": {"gte": 3},
                "location": {"contains": "Lekki"},
                "price": {"between": [5000000, 30000000]}
            },
            "sort": {"field": "price", "order": "asc"}
        }
        """
        search_id = str(uuid.uuid4())

        saved_search = {
            'id': search_id,
            'user_id': user_id,
            'name': name,
            'criteria': criteria,
            'alert_frequency': alert_frequency,
            'created_at': datetime.now().isoformat(),
            'last_checked': None,
            'last_match_count': 0,
            'total_matches_sent': 0,
            'enabled': True
        }

        with self._lock:
            self.searches[search_id] = saved_search

        self._save_searches()

        logger.info(
            f"Created saved search '{name}' for user {user_id} "
            f"(id={search_id}, alert_frequency={alert_frequency})"
        )

        return search_id

    def get_search(self, search_id: str) -> Optional[Dict]:
        """
        Get a saved search by ID.

        Args:
            search_id: Search ID

        Returns:
            Search dict or None if not found
        """
        with self._lock:
            return self.searches.get(search_id)

    def list_searches(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        List all saved searches, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of search dicts
        """
        with self._lock:
            if user_id:
                return [
                    search for search in self.searches.values()
                    if search['user_id'] == user_id
                ]
            else:
                return list(self.searches.values())

    def update_search(self, search_id: str, updates: Dict) -> bool:
        """
        Update a saved search.

        Args:
            search_id: Search ID
            updates: Dict of fields to update

        Returns:
            True if updated, False if search not found
        """
        with self._lock:
            if search_id not in self.searches:
                logger.warning(f"Search {search_id} not found for update")
                return False

            # Update allowed fields
            allowed_fields = ['name', 'criteria', 'alert_frequency', 'enabled']
            for field in allowed_fields:
                if field in updates:
                    self.searches[search_id][field] = updates[field]

            self.searches[search_id]['updated_at'] = datetime.now().isoformat()

        self._save_searches()

        logger.info(f"Updated search {search_id}")
        return True

    def delete_search(self, search_id: str) -> bool:
        """
        Delete a saved search.

        Args:
            search_id: Search ID

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if search_id not in self.searches:
                logger.warning(f"Search {search_id} not found for deletion")
                return False

            search_name = self.searches[search_id]['name']
            del self.searches[search_id]

        self._save_searches()

        logger.info(f"Deleted search '{search_name}' (id={search_id})")
        return True

    def check_for_new_matches(self,
                             search_id: str,
                             all_listings: List[Dict]) -> List[Dict]:
        """
        Check for new listings matching a saved search.

        Args:
            search_id: Search ID
            all_listings: All available listings to search

        Returns:
            List of new matching listings
        """
        search = self.get_search(search_id)
        if not search:
            logger.warning(f"Search {search_id} not found")
            return []

        if not search.get('enabled', True):
            logger.debug(f"Search {search_id} is disabled - skipping")
            return []

        # Import query engine
        try:
            from core.query_engine import PropertyQuery
        except ImportError:
            logger.error("PropertyQuery not available - can't check matches")
            return []

        criteria = search.get('criteria', {})
        last_checked = search.get('last_checked')

        # Execute query
        try:
            # If we have a last_checked timestamp, only get newer listings
            filters = criteria.get('filters', {})

            if last_checked:
                # Add timestamp filter
                filters['scrape_timestamp'] = {'gte': last_checked}

            # Create query from listings
            # Note: This is simplified - in real implementation,
            # PropertyQuery would accept list of dicts directly
            matches = []
            for listing in all_listings:
                if self._listing_matches_criteria(listing, filters):
                    matches.append(listing)

            logger.info(
                f"Search '{search['name']}' (id={search_id}): "
                f"Found {len(matches)} new matches"
            )

            # Update search metadata
            with self._lock:
                self.searches[search_id]['last_checked'] = datetime.now().isoformat()
                self.searches[search_id]['last_match_count'] = len(matches)
                self.searches[search_id]['total_matches_sent'] += len(matches)

            self._save_searches()

            return matches

        except Exception as e:
            logger.error(f"Error checking matches for search {search_id}: {e}")
            return []

    def _listing_matches_criteria(self, listing: Dict, filters: Dict) -> bool:
        """
        Check if a listing matches filter criteria.

        Args:
            listing: Listing dict
            filters: Filters dict

        Returns:
            True if matches, False otherwise
        """
        for field, condition in filters.items():
            listing_value = listing.get(field)

            if isinstance(condition, dict):
                # Operator-based conditions
                for op, value in condition.items():
                    if op == 'gte' and not (listing_value and listing_value >= value):
                        return False
                    elif op == 'lte' and not (listing_value and listing_value <= value):
                        return False
                    elif op == 'gt' and not (listing_value and listing_value > value):
                        return False
                    elif op == 'lt' and not (listing_value and listing_value < value):
                        return False
                    elif op == 'eq' and listing_value != value:
                        return False
                    elif op == 'ne' and listing_value == value:
                        return False
                    elif op == 'contains' and not (listing_value and value.lower() in str(listing_value).lower()):
                        return False
                    elif op == 'between' and not (listing_value and value[0] <= listing_value <= value[1]):
                        return False
            else:
                # Direct value match
                if listing_value != condition:
                    return False

        return True

    def send_alert(self, search_id: str, matches: List[Dict]) -> bool:
        """
        Send alert for new matches (basic implementation).

        In production, this would integrate with email/SMS services.

        Args:
            search_id: Search ID
            matches: List of new matching listings

        Returns:
            True if alert sent successfully
        """
        search = self.get_search(search_id)
        if not search:
            return False

        # For now, just log the alert
        # In production, would send email via SendGrid, AWS SES, etc.
        logger.info(
            f"ALERT: Search '{search['name']}' has {len(matches)} new matches "
            f"for user {search['user_id']}"
        )

        # Example email content
        email_subject = f"New Properties Matching '{search['name']}'"
        email_body = f"""
        You have {len(matches)} new properties matching your saved search '{search['name']}'.

        {self._format_matches_for_email(matches[:5])}

        View all matches: [LINK TO FRONTEND]
        """

        logger.debug(f"Would send email: {email_subject}")
        # TODO: Integrate with email service

        return True

    def _format_matches_for_email(self, matches: List[Dict]) -> str:
        """Format matches for email body"""
        lines = []
        for i, match in enumerate(matches, 1):
            lines.append(
                f"{i}. {match.get('title', 'Untitled')} - "
                f"₦{match.get('price', 0):,.0f} - "
                f"{match.get('location', 'Unknown')}"
            )
        return "\n".join(lines)

    def get_search_stats(self, search_id: str) -> Optional[Dict]:
        """
        Get statistics about a saved search.

        Args:
            search_id: Search ID

        Returns:
            Stats dict or None if not found
        """
        search = self.get_search(search_id)
        if not search:
            return None

        return {
            'id': search['id'],
            'name': search['name'],
            'created_at': search['created_at'],
            'last_checked': search.get('last_checked'),
            'last_match_count': search.get('last_match_count', 0),
            'total_matches_sent': search.get('total_matches_sent', 0),
            'alert_frequency': search.get('alert_frequency', 'disabled'),
            'enabled': search.get('enabled', True)
        }


def get_saved_search_manager(storage_dir: str = "logs/saved_searches") -> SavedSearchManager:
    """
    Get a SavedSearchManager instance.

    Args:
        storage_dir: Directory to store saved searches

    Returns:
        SavedSearchManager instance
    """
    return SavedSearchManager(storage_dir=storage_dir)
