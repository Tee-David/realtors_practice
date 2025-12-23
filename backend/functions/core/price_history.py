"""
Price History Tracking Module

Track property price changes over time to identify trends and opportunities.

Features:
- Track price changes for each property
- Alert on price drops
- Identify stale listings (overpriced/listed for months)
- Market trend analysis
- Price reduction percentage calculation

Author: Tee-David
Date: 2025-10-20
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)


class PriceHistoryTracker:
    """
    Track and analyze property price history.

    Stores price changes in JSON format for historical analysis.
    """

    def __init__(self, history_file: str = "logs/price_history.json"):
        """
        Initialize price history tracker.

        Args:
            history_file: Path to price history storage file
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing history
        self.history: Dict[str, List[Dict]] = self._load_history()

        # Thread safety
        self._lock = Lock()

        logger.debug(f"PriceHistoryTracker initialized: {len(self.history)} properties tracked")

    def _load_history(self) -> Dict[str, List[Dict]]:
        """Load price history from file"""
        if not self.history_file.exists():
            logger.debug("No price history file found - starting fresh")
            return {}

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                logger.info(f"Loaded price history for {len(history)} properties")
                return history
        except Exception as e:
            logger.error(f"Error loading price history: {e}")
            return {}

    def _save_history(self):
        """Save price history to file"""
        try:
            with self._lock:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, indent=2)

                logger.debug(f"Saved price history for {len(self.history)} properties")
        except Exception as e:
            logger.error(f"Error saving price history: {e}")

    def _get_property_id(self, listing: Dict) -> str:
        """
        Generate unique property ID from listing.

        Uses hash or URL as identifier.

        Args:
            listing: Listing dictionary

        Returns:
            Unique property ID
        """
        # Try hash first (most reliable)
        if 'hash' in listing and listing['hash']:
            return f"hash_{listing['hash']}"

        # Fallback to URL
        if 'listing_url' in listing and listing['listing_url']:
            return f"url_{listing['listing_url']}"

        # Last resort: title + location
        title = listing.get('title', 'unknown')[:50]
        location = listing.get('location', 'unknown')[:30]
        return f"title_{title}_{location}"

    def track_listing(self, listing: Dict) -> Optional[Dict]:
        """
        Track a listing's price.

        Records price if it's new or changed.

        Args:
            listing: Listing dictionary

        Returns:
            Dict with tracking info (price_changed, old_price, new_price, etc.)
            or None if price unchanged
        """
        property_id = self._get_property_id(listing)
        current_price = listing.get('price')

        if not current_price or current_price == 0:
            return None

        timestamp = datetime.now().isoformat()

        with self._lock:
            # Get existing history for this property
            if property_id not in self.history:
                # First time seeing this property
                self.history[property_id] = [{
                    'price': current_price,
                    'timestamp': timestamp,
                    'title': listing.get('title'),
                    'location': listing.get('location'),
                    'source': listing.get('source'),
                    'listing_url': listing.get('listing_url')
                }]

                self._save_history()

                return {
                    'property_id': property_id,
                    'price_changed': False,
                    'is_new': True,
                    'current_price': current_price,
                    'first_seen': timestamp
                }

            # Check if price changed
            last_entry = self.history[property_id][-1]
            last_price = last_entry['price']

            if current_price != last_price:
                # Price changed!
                price_diff = current_price - last_price
                price_diff_pct = (price_diff / last_price) * 100 if last_price > 0 else 0

                # Add new price entry
                self.history[property_id].append({
                    'price': current_price,
                    'timestamp': timestamp,
                    'price_change': price_diff,
                    'price_change_pct': round(price_diff_pct, 2)
                })

                self._save_history()

                logger.info(
                    f"Price change detected: {listing.get('title', 'Unknown')} - "
                    f"₦{last_price:,.0f} → ₦{current_price:,.0f} "
                    f"({price_diff_pct:+.1f}%)"
                )

                return {
                    'property_id': property_id,
                    'price_changed': True,
                    'is_new': False,
                    'old_price': last_price,
                    'new_price': current_price,
                    'price_diff': price_diff,
                    'price_diff_pct': round(price_diff_pct, 2),
                    'is_drop': price_diff < 0,
                    'is_increase': price_diff > 0,
                    'timestamp': timestamp
                }

            # Price unchanged
            return {
                'property_id': property_id,
                'price_changed': False,
                'is_new': False,
                'current_price': current_price
            }

    def get_price_history(self, property_id: str) -> List[Dict]:
        """
        Get price history for a property.

        Args:
            property_id: Property identifier

        Returns:
            List of price entries (chronological)
        """
        with self._lock:
            return self.history.get(property_id, [])

    def get_price_drops(self, min_drop_pct: float = 5.0, days: int = 30) -> List[Dict]:
        """
        Get properties with recent price drops.

        Args:
            min_drop_pct: Minimum price drop percentage
            days: Look back period in days

        Returns:
            List of properties with price drops
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        price_drops = []

        with self._lock:
            for property_id, entries in self.history.items():
                if len(entries) < 2:
                    continue

                # Check recent entries
                for entry in reversed(entries):
                    if 'price_change_pct' not in entry:
                        continue

                    # Check if within timeframe
                    try:
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if entry_date < cutoff_date:
                            break
                    except:
                        continue

                    # Check if significant drop
                    if entry['price_change_pct'] <= -min_drop_pct:
                        price_drops.append({
                            'property_id': property_id,
                            'title': entries[0].get('title'),
                            'location': entries[0].get('location'),
                            'source': entries[0].get('source'),
                            'listing_url': entries[0].get('listing_url'),
                            'old_price': entry['price'] - entry['price_change'],
                            'new_price': entry['price'],
                            'price_drop': abs(entry['price_change']),
                            'price_drop_pct': abs(entry['price_change_pct']),
                            'timestamp': entry['timestamp']
                        })
                        break

        # Sort by price drop percentage (highest first)
        price_drops.sort(key=lambda x: x['price_drop_pct'], reverse=True)

        logger.info(f"Found {len(price_drops)} properties with price drops >= {min_drop_pct}%")

        return price_drops

    def get_stale_listings(self, min_days: int = 90) -> List[Dict]:
        """
        Get properties listed for a long time without price change.

        Indicates overpriced or difficult-to-sell properties.

        Args:
            min_days: Minimum days listed

        Returns:
            List of stale listings
        """
        cutoff_date = datetime.now() - timedelta(days=min_days)
        stale_listings = []

        with self._lock:
            for property_id, entries in self.history.items():
                if len(entries) == 0:
                    continue

                # Get first seen date
                try:
                    first_seen = datetime.fromisoformat(entries[0]['timestamp'])
                except:
                    continue

                # Check if listed for long enough
                if first_seen >= cutoff_date:
                    continue

                days_listed = (datetime.now() - first_seen).days

                # Check if price has changed (if so, not really stale)
                has_price_change = any('price_change' in e for e in entries)

                stale_listings.append({
                    'property_id': property_id,
                    'title': entries[0].get('title'),
                    'location': entries[0].get('location'),
                    'source': entries[0].get('source'),
                    'listing_url': entries[0].get('listing_url'),
                    'current_price': entries[-1]['price'],
                    'first_seen': entries[0]['timestamp'],
                    'days_listed': days_listed,
                    'price_changes': len([e for e in entries if 'price_change' in e]),
                    'has_price_change': has_price_change
                })

        # Sort by days listed (longest first)
        stale_listings.sort(key=lambda x: x['days_listed'], reverse=True)

        logger.info(f"Found {len(stale_listings)} stale listings (>= {min_days} days)")

        return stale_listings

    def get_market_trends(self, days: int = 30) -> Dict:
        """
        Analyze overall market price trends.

        Args:
            days: Analysis period in days

        Returns:
            Dict with market trend statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        price_increases = 0
        price_decreases = 0
        total_changes = 0
        avg_change_pct = 0.0

        with self._lock:
            for property_id, entries in self.history.items():
                for entry in reversed(entries):
                    if 'price_change_pct' not in entry:
                        continue

                    # Check if within timeframe
                    try:
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if entry_date < cutoff_date:
                            break
                    except:
                        continue

                    total_changes += 1
                    avg_change_pct += entry['price_change_pct']

                    if entry['price_change_pct'] > 0:
                        price_increases += 1
                    elif entry['price_change_pct'] < 0:
                        price_decreases += 1

        if total_changes > 0:
            avg_change_pct = avg_change_pct / total_changes
        else:
            avg_change_pct = 0.0

        # Determine overall trend
        if price_decreases > price_increases * 1.2:
            trend = "declining"
        elif price_increases > price_decreases * 1.2:
            trend = "rising"
        else:
            trend = "stable"

        return {
            'period_days': days,
            'total_price_changes': total_changes,
            'price_increases': price_increases,
            'price_decreases': price_decreases,
            'avg_change_pct': round(avg_change_pct, 2),
            'trend': trend,
            'total_properties_tracked': len(self.history)
        }

    def track_batch(self, listings: List[Dict]) -> Dict:
        """
        Track multiple listings at once.

        Args:
            listings: List of listing dicts

        Returns:
            Summary statistics
        """
        new_count = 0
        changed_count = 0
        unchanged_count = 0
        price_drops_count = 0

        for listing in listings:
            result = self.track_listing(listing)

            if result:
                if result.get('is_new'):
                    new_count += 1
                elif result.get('price_changed'):
                    changed_count += 1
                    if result.get('is_drop'):
                        price_drops_count += 1
                else:
                    unchanged_count += 1

        logger.info(
            f"Batch tracking: {new_count} new, {changed_count} changed "
            f"({price_drops_count} drops), {unchanged_count} unchanged"
        )

        return {
            'total_tracked': len(listings),
            'new_properties': new_count,
            'price_changed': changed_count,
            'price_drops': price_drops_count,
            'unchanged': unchanged_count
        }


def get_price_history_tracker(history_file: str = "logs/price_history.json") -> PriceHistoryTracker:
    """
    Get a PriceHistoryTracker instance.

    Args:
        history_file: Path to price history file

    Returns:
        PriceHistoryTracker instance
    """
    return PriceHistoryTracker(history_file=history_file)
