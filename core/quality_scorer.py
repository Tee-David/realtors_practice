"""
Data Quality Scoring Module

Assigns quality scores (0.0 to 1.0) to listings based on field completeness.
Helps identify high-quality listings with complete information.

Scoring tiers:
- Required fields (40 points): title, price, location, listing_url
- Recommended fields (30 points): bedrooms, bathrooms, property_type, images
- Bonus fields (30 points): coordinates, land_size, description, contact_info

Author: Tee-David
Date: 2025-10-20
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class QualityScorer:
    """
    Assign quality scores to listings based on data completeness.

    Scores range from 0.0 (minimal data) to 1.0 (complete data).
    """

    # Field definitions
    REQUIRED_FIELDS = ['title', 'price', 'location', 'listing_url']
    RECOMMENDED_FIELDS = ['bedrooms', 'bathrooms', 'property_type', 'images']
    BONUS_FIELDS = ['coordinates', 'land_size', 'description', 'contact_info']

    # Point allocations
    REQUIRED_POINTS = 40
    RECOMMENDED_POINTS = 30
    BONUS_POINTS = 30

    def __init__(self):
        """Initialize quality scorer"""
        self.total_points = (
            self.REQUIRED_POINTS +
            self.RECOMMENDED_POINTS +
            self.BONUS_POINTS
        )

        logger.debug(
            f"QualityScorer initialized: "
            f"{len(self.REQUIRED_FIELDS)} required, "
            f"{len(self.RECOMMENDED_FIELDS)} recommended, "
            f"{len(self.BONUS_FIELDS)} bonus fields"
        )

    def _is_field_present(self, value) -> bool:
        """
        Check if field value is meaningfully present.

        Args:
            value: Field value to check

        Returns:
            True if value is present and non-empty
        """
        if value is None:
            return False

        if isinstance(value, str):
            return len(value.strip()) > 0

        if isinstance(value, (list, dict)):
            return len(value) > 0

        if isinstance(value, (int, float)):
            return value > 0

        return bool(value)

    def score_listing(self, listing: Dict) -> Tuple[float, List[str]]:
        """
        Calculate quality score for a listing.

        Args:
            listing: Listing dictionary to score

        Returns:
            (score: float, issues: List[str])
            - score: Quality score from 1% to 100%
            - issues: List of missing/problematic fields
        """
        score = 0.0
        issues = []

        # Score required fields (40 points total)
        required_present = 0
        for field in self.REQUIRED_FIELDS:
            if self._is_field_present(listing.get(field)):
                required_present += 1
            else:
                issues.append(f"Missing required field: {field}")

        required_score = (required_present / len(self.REQUIRED_FIELDS)) * self.REQUIRED_POINTS
        score += required_score

        # Score recommended fields (30 points total)
        recommended_present = 0
        for field in self.RECOMMENDED_FIELDS:
            if self._is_field_present(listing.get(field)):
                recommended_present += 1
            else:
                issues.append(f"Missing recommended field: {field}")

        recommended_score = (recommended_present / len(self.RECOMMENDED_FIELDS)) * self.RECOMMENDED_POINTS
        score += recommended_score

        # Score bonus fields (30 points total)
        bonus_present = 0
        for field in self.BONUS_FIELDS:
            if self._is_field_present(listing.get(field)):
                bonus_present += 1

        bonus_score = (bonus_present / len(self.BONUS_FIELDS)) * self.BONUS_POINTS
        score += bonus_score

        # Convert to percentage (1-100%)
        percentage_score = round((score / self.total_points) * 100, 1)

        # Ensure minimum of 1% (not 0%)
        if percentage_score < 1 and listing:
            percentage_score = 1.0

        return percentage_score, issues

    def score_listings_batch(self, listings: List[Dict]) -> List[Dict]:
        """
        Score multiple listings at once, adding quality_score field.

        Args:
            listings: List of listing dictionaries

        Returns:
            Updated listings with quality_score and quality_issues fields
        """
        logger.info(f"Scoring {len(listings)} listings for quality...")

        high_quality_count = 0
        medium_quality_count = 0
        low_quality_count = 0

        for listing in listings:
            score, issues = self.score_listing(listing)

            listing['quality_score'] = round(score, 3)
            listing['quality_issues'] = issues

            # Count by quality tier
            if score >= 80:
                high_quality_count += 1
            elif score >= 50:
                medium_quality_count += 1
            else:
                low_quality_count += 1

        logger.info(
            f"Quality distribution: "
            f"High (>=80%): {high_quality_count}, "
            f"Medium (50-79%): {medium_quality_count}, "
            f"Low (<50%): {low_quality_count}"
        )

        return listings

    def filter_by_quality(self, listings: List[Dict],
                         min_score: float = 80) -> List[Dict]:
        """
        Filter listings by minimum quality score.

        Args:
            listings: List of listing dictionaries
            min_score: Minimum quality score (1% to 100%)

        Returns:
            Filtered list of high-quality listings
        """
        # Ensure quality scores are calculated
        if 'quality_score' not in listings[0]:
            listings = self.score_listings_batch(listings)

        filtered = [
            listing for listing in listings
            if listing.get('quality_score', 0.0) >= min_score
        ]

        logger.info(
            f"Quality filter (min_score={min_score}): "
            f"{len(listings)} -> {len(filtered)} listings "
            f"({len(filtered)/len(listings)*100:.1f}% retained)"
        )

        return filtered

    def get_quality_summary(self, listings: List[Dict]) -> Dict:
        """
        Get summary statistics about listing quality.

        Args:
            listings: List of listing dictionaries (must have quality_score)

        Returns:
            Dictionary with quality statistics
        """
        if not listings:
            return {
                'total_listings': 0,
                'avg_quality_score': 0.0,
                'quality_distribution': {}
            }

        scores = [l.get('quality_score', 1.0) for l in listings]

        # Quality tiers
        high_quality = sum(1 for s in scores if s >= 80)
        medium_quality = sum(1 for s in scores if 50 <= s < 80)
        low_quality = sum(1 for s in scores if s < 50)

        # Most common issues
        all_issues = []
        for listing in listings:
            all_issues.extend(listing.get('quality_issues', []))

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Sort by frequency
        top_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'total_listings': len(listings),
            'avg_quality_score': round(sum(scores) / len(scores), 3),
            'min_quality_score': round(min(scores), 3),
            'max_quality_score': round(max(scores), 3),
            'quality_distribution': {
                'high_quality_count': high_quality,
                'high_quality_pct': round(high_quality / len(listings) * 100, 1),
                'medium_quality_count': medium_quality,
                'medium_quality_pct': round(medium_quality / len(listings) * 100, 1),
                'low_quality_count': low_quality,
                'low_quality_pct': round(low_quality / len(listings) * 100, 1),
            },
            'top_issues': [
                {'issue': issue, 'count': count, 'pct': round(count / len(listings) * 100, 1)}
                for issue, count in top_issues
            ]
        }

    def categorize_by_quality(self, listings: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize listings into quality tiers.

        Args:
            listings: List of listing dictionaries

        Returns:
            Dictionary with 'high', 'medium', 'low' quality lists
        """
        # Ensure quality scores are calculated
        if not listings or 'quality_score' not in listings[0]:
            listings = self.score_listings_batch(listings)

        categorized = {
            'high_quality': [],
            'medium_quality': [],
            'low_quality': []
        }

        for listing in listings:
            score = listing.get('quality_score', 0.0)

            if score >= 0.8:
                categorized['high_quality'].append(listing)
            elif score >= 0.5:
                categorized['medium_quality'].append(listing)
            else:
                categorized['low_quality'].append(listing)

        logger.info(
            f"Categorized: High={len(categorized['high_quality'])}, "
            f"Medium={len(categorized['medium_quality'])}, "
            f"Low={len(categorized['low_quality'])}"
        )

        return categorized


def get_quality_scorer() -> QualityScorer:
    """
    Get a QualityScorer instance.

    Returns:
        QualityScorer instance
    """
    return QualityScorer()
