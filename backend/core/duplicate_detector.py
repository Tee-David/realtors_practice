"""
Duplicate Detection Module

Detects duplicate listings across sites using fuzzy matching and coordinate comparison.
Same property may be listed on multiple sites or relisted with minor changes.

Uses multiple signals:
- Fuzzy title matching (SequenceMatcher)
- Location similarity
- Coordinate proximity (if available)
- Property attributes (bedrooms, price, type)

Author: Tee-David
Date: 2025-10-20
"""

import logging
import json
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import math

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """
    Detect duplicate listings across sites using fuzzy matching.

    Combines multiple signals to calculate similarity score:
    - Title similarity (40%)
    - Location similarity (30%)
    - Bedroom match (20%)
    - Price proximity (10%)
    - Coordinate distance (bonus if available)
    """

    def __init__(self, threshold: float = 0.85, action: str = "flag"):
        """
        Initialize duplicate detector.

        Args:
            threshold: Similarity threshold (0.0 to 1.0) for duplicate detection
            action: What to do with duplicates ("flag", "remove", "merge")
        """
        self.threshold = threshold
        self.action = action

        # Coordinate distance threshold (meters)
        self.coord_distance_threshold = 50  # 50 meters

        logger.debug(
            f"DuplicateDetector initialized: threshold={threshold}, action={action}"
        )

    def _title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate title similarity using SequenceMatcher.

        Args:
            title1, title2: Titles to compare

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not title1 or not title2:
            return 0.0

        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, t1, t2).ratio()

        return similarity

    def _location_similarity(self, loc1: str, loc2: str) -> float:
        """
        Calculate location similarity.

        Args:
            loc1, loc2: Locations to compare

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not loc1 or not loc2:
            return 0.0

        # Normalize locations
        l1 = loc1.lower().strip()
        l2 = loc2.lower().strip()

        # Use SequenceMatcher
        similarity = SequenceMatcher(None, l1, l2).ratio()

        return similarity

    def _coordinates_match(self, coords1: Dict, coords2: Dict) -> Tuple[bool, float]:
        """
        Check if coordinates are within threshold distance.

        Args:
            coords1, coords2: Coordinate dicts with 'lat' and 'lng'

        Returns:
            (match: bool, distance: float in meters)
        """
        if not coords1 or not coords2:
            return False, float('inf')

        try:
            lat1, lng1 = float(coords1.get('lat', 0)), float(coords1.get('lng', 0))
            lat2, lng2 = float(coords2.get('lat', 0)), float(coords2.get('lng', 0))

            # Haversine formula for distance
            R = 6371000  # Earth radius in meters

            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lng2 - lng1)

            a = math.sin(delta_phi / 2) ** 2 + \
                math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c  # Distance in meters

            match = distance <= self.coord_distance_threshold

            return match, distance

        except (ValueError, TypeError) as e:
            logger.debug(f"Error calculating coordinate distance: {e}")
            return False, float('inf')

    def _prices_close(self, price1: Optional[float], price2: Optional[float],
                     tolerance: float = 0.10) -> bool:
        """
        Check if prices are within tolerance percentage.

        Args:
            price1, price2: Prices to compare
            tolerance: Allowed difference as percentage (default: 10%)

        Returns:
            True if prices are close, False otherwise
        """
        if price1 is None or price2 is None:
            return False

        if price1 == 0 or price2 == 0:
            return False

        # Calculate percentage difference
        diff = abs(price1 - price2)
        avg = (price1 + price2) / 2

        if avg == 0:
            return False

        diff_pct = diff / avg

        return diff_pct <= tolerance

    def is_duplicate(self, listing1: Dict, listing2: Dict) -> Tuple[bool, float, Dict]:
        """
        Check if two listings are duplicates.

        Combines multiple signals to calculate overall similarity score.

        Args:
            listing1, listing2: Listing dictionaries to compare

        Returns:
            (is_duplicate: bool, similarity_score: float, breakdown: dict)
        """
        # Extract fields
        title1 = listing1.get('title', '')
        title2 = listing2.get('title', '')

        location1 = listing1.get('location', '')
        location2 = listing2.get('location', '')

        bedrooms1 = listing1.get('bedrooms')
        bedrooms2 = listing2.get('bedrooms')

        price1 = listing1.get('price')
        price2 = listing2.get('price')

        coords1 = listing1.get('coordinates', {})
        coords2 = listing2.get('coordinates', {})

        # Calculate individual similarity scores
        title_sim = self._title_similarity(title1, title2)
        location_sim = self._location_similarity(location1, location2)

        bedrooms_match = 1.0 if (bedrooms1 and bedrooms2 and bedrooms1 == bedrooms2) else 0.0
        price_close = 1.0 if self._prices_close(price1, price2) else 0.0

        # Check coordinates if available
        coord_match, coord_distance = self._coordinates_match(coords1, coords2)
        coord_bonus = 0.2 if coord_match else 0.0  # Extra 20% if coordinates match

        # Weighted similarity score
        # Base score: title(40%) + location(30%) + bedrooms(20%) + price(10%)
        base_score = (
            title_sim * 0.40 +
            location_sim * 0.30 +
            bedrooms_match * 0.20 +
            price_close * 0.10
        )

        # Add coordinate bonus (can push score above 1.0, we'll cap it)
        total_score = min(base_score + coord_bonus, 1.0)

        # Breakdown for debugging
        breakdown = {
            'title_similarity': title_sim,
            'location_similarity': location_sim,
            'bedrooms_match': bedrooms_match,
            'price_close': price_close,
            'coord_match': coord_match,
            'coord_distance_meters': coord_distance if coord_distance != float('inf') else None,
            'base_score': base_score,
            'coord_bonus': coord_bonus,
            'total_score': total_score
        }

        is_dup = total_score >= self.threshold

        if is_dup:
            logger.debug(
                f"Duplicate detected (score={total_score:.2f}): "
                f"'{title1[:50]}' vs '{title2[:50]}'"
            )

        return is_dup, total_score, breakdown

    def find_duplicates(self, listings: List[Dict]) -> List[Tuple[Dict, Dict, float, Dict]]:
        """
        Find all duplicate pairs in a list of listings.

        Args:
            listings: List of listing dictionaries

        Returns:
            List of tuples: (listing1, listing2, similarity_score, breakdown)
        """
        duplicates = []

        logger.info(f"Scanning {len(listings)} listings for duplicates...")

        # Compare all pairs
        for i, listing1 in enumerate(listings):
            for listing2 in listings[i + 1:]:
                is_dup, score, breakdown = self.is_duplicate(listing1, listing2)

                if is_dup:
                    duplicates.append((listing1, listing2, score, breakdown))

        logger.info(
            f"Found {len(duplicates)} duplicate pairs "
            f"(threshold={self.threshold})"
        )

        return duplicates

    def find_duplicate_groups(self, listings: List[Dict]) -> List[List[int]]:
        """
        Find groups of duplicates (transitive closure).

        If A=B and B=C, then all three are in same group.

        Args:
            listings: List of listing dictionaries

        Returns:
            List of groups, where each group is a list of indices
        """
        # Build adjacency list of duplicates
        adjacency = {i: set() for i in range(len(listings))}

        for i, listing1 in enumerate(listings):
            for j, listing2 in enumerate(listings[i + 1:], start=i + 1):
                is_dup, _, _ = self.is_duplicate(listing1, listing2)

                if is_dup:
                    adjacency[i].add(j)
                    adjacency[j].add(i)

        # Find connected components using DFS
        visited = set()
        groups = []

        def dfs(node, group):
            if node in visited:
                return
            visited.add(node)
            group.append(node)
            for neighbor in adjacency[node]:
                dfs(neighbor, group)

        for i in range(len(listings)):
            if i not in visited:
                group = []
                dfs(i, group)
                if len(group) > 1:  # Only include groups with duplicates
                    groups.append(sorted(group))

        logger.info(f"Found {len(groups)} duplicate groups")

        return groups

    def add_duplicate_ids_to_listings(self, listings: List[Dict]) -> List[Dict]:
        """
        Add duplicate_group_id field to listings.

        Listings in same duplicate group get same ID.

        Args:
            listings: List of listing dictionaries

        Returns:
            Updated listings with duplicate_group_id field
        """
        groups = self.find_duplicate_groups(listings)

        # Initialize all listings with no group
        for listing in listings:
            listing['duplicate_group_id'] = None
            listing['is_duplicate'] = False

        # Assign group IDs
        for group_id, group_indices in enumerate(groups, start=1):
            for idx in group_indices:
                listings[idx]['duplicate_group_id'] = group_id
                listings[idx]['is_duplicate'] = True

        dup_count = sum(1 for l in listings if l['is_duplicate'])

        logger.info(
            f"Marked {dup_count}/{len(listings)} listings as duplicates "
            f"({len(groups)} groups)"
        )

        return listings

    def filter_duplicates(self, listings: List[Dict],
                         keep_strategy: str = "first") -> List[Dict]:
        """
        Remove duplicates, keeping one per group.

        Args:
            listings: List of listing dictionaries
            keep_strategy: Which duplicate to keep
                - "first": Keep first occurrence
                - "most_complete": Keep listing with most fields
                - "cheapest": Keep cheapest listing
                - "newest": Keep newest listing (by scrape_timestamp)

        Returns:
            Filtered list with duplicates removed
        """
        groups = self.find_duplicate_groups(listings)

        # Track which indices to remove
        indices_to_remove = set()

        for group_indices in groups:
            if keep_strategy == "first":
                # Keep first, remove rest
                indices_to_remove.update(group_indices[1:])

            elif keep_strategy == "most_complete":
                # Keep listing with most non-null fields
                completeness = [
                    sum(1 for v in listings[i].values() if v not in [None, '', [], {}])
                    for i in group_indices
                ]
                best_idx = group_indices[completeness.index(max(completeness))]
                indices_to_remove.update(i for i in group_indices if i != best_idx)

            elif keep_strategy == "cheapest":
                # Keep cheapest listing
                prices = [
                    (listings[i].get('price', float('inf')), i)
                    for i in group_indices
                ]
                best_idx = min(prices)[1]
                indices_to_remove.update(i for i in group_indices if i != best_idx)

            elif keep_strategy == "newest":
                # Keep newest by scrape_timestamp
                timestamps = [
                    (listings[i].get('scrape_timestamp', ''), i)
                    for i in group_indices
                ]
                best_idx = max(timestamps)[1]
                indices_to_remove.update(i for i in group_indices if i != best_idx)

        # Filter out duplicates
        filtered = [
            listing for i, listing in enumerate(listings)
            if i not in indices_to_remove
        ]

        logger.info(
            f"Filtered duplicates: {len(listings)} -> {len(filtered)} listings "
            f"(removed {len(indices_to_remove)}, strategy='{keep_strategy}')"
        )

        return filtered


def get_duplicate_detector(threshold: float = 0.85, action: str = "flag") -> DuplicateDetector:
    """
    Get a DuplicateDetector instance.

    Args:
        threshold: Similarity threshold (0.0 to 1.0)
        action: What to do with duplicates ("flag", "remove", "merge")

    Returns:
        DuplicateDetector instance
    """
    return DuplicateDetector(threshold=threshold, action=action)
