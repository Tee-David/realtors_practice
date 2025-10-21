"""
Tests for Data Quality Scoring Module

Tests quality score calculation and filtering.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.quality_scorer import QualityScorer, get_quality_scorer


class TestQualityScorer(unittest.TestCase):
    """Test QualityScorer functionality"""

    def setUp(self):
        """Create scorer instance"""
        self.scorer = QualityScorer()

    def test_initialization(self):
        """Test scorer initializes correctly"""
        self.assertEqual(len(self.scorer.REQUIRED_FIELDS), 4)
        self.assertEqual(len(self.scorer.RECOMMENDED_FIELDS), 4)
        self.assertEqual(len(self.scorer.BONUS_FIELDS), 4)
        self.assertEqual(self.scorer.total_points, 100)

    def test_perfect_score(self):
        """Test listing with all fields gets perfect score"""
        listing = {
            # Required
            'title': '3 Bedroom Flat',
            'price': 25000000,
            'location': 'Lekki',
            'listing_url': 'https://example.com/listing1',
            # Recommended
            'bedrooms': 3,
            'bathrooms': 2,
            'property_type': 'Flat',
            'images': ['image1.jpg', 'image2.jpg'],
            # Bonus
            'coordinates': {'lat': 6.4474, 'lng': 3.4706},
            'land_size': '500sqm',
            'description': 'Luxury apartment',
            'contact_info': '0801234567'
        }

        score, issues = self.scorer.score_listing(listing)

        self.assertEqual(score, 100.0)
        self.assertEqual(len(issues), 0)

    def test_minimum_score(self):
        """Test listing with only required fields"""
        listing = {
            'title': '3 Bedroom Flat',
            'price': 25000000,
            'location': 'Lekki',
            'listing_url': 'https://example.com/listing1'
        }

        score, issues = self.scorer.score_listing(listing)

        # Should get 40% (required only)
        self.assertEqual(score, 40.0)
        self.assertGreater(len(issues), 0)  # Should have issues for missing fields

    def test_partial_score(self):
        """Test listing with some fields missing"""
        listing = {
            # Required (4/4)
            'title': '3 Bedroom Flat',
            'price': 25000000,
            'location': 'Lekki',
            'listing_url': 'https://example.com/listing1',
            # Recommended (2/4)
            'bedrooms': 3,
            'property_type': 'Flat',
            # Bonus (1/4)
            'coordinates': {'lat': 6.4474, 'lng': 3.4706}
        }

        score, issues = self.scorer.score_listing(listing)

        # Required: 40, Recommended: 15 (2/4 * 30), Bonus: 7.5 (1/4 * 30)
        # Total: 62.5%
        self.assertAlmostEqual(score, 62.5, places=1)

    def test_empty_fields_not_counted(self):
        """Test empty/null fields are not counted as present"""
        listing = {
            'title': '3 Bedroom Flat',
            'price': 25000000,
            'location': '',  # Empty string
            'listing_url': 'https://example.com/listing1',
            'bedrooms': None,  # None
            'images': [],  # Empty list
            'coordinates': {}  # Empty dict
        }

        score, issues = self.scorer.score_listing(listing)

        # Should only count title, price, listing_url (3/4 required = 30%)
        self.assertLess(score, 50.0)

    def test_score_listings_batch(self):
        """Test batch scoring multiple listings"""
        listings = [
            {
                'title': 'Listing 1',
                'price': 25000000,
                'location': 'Lekki',
                'listing_url': 'https://example.com/1',
                'bedrooms': 3,
                'bathrooms': 2,
                'property_type': 'Flat',
                'images': ['img1.jpg']
            },
            {
                'title': 'Listing 2',
                'price': 30000000,
                'location': 'Ikoyi',
                'listing_url': 'https://example.com/2'
            }
        ]

        scored = self.scorer.score_listings_batch(listings)

        self.assertEqual(len(scored), 2)
        self.assertIn('quality_score', scored[0])
        self.assertIn('quality_issues', scored[0])

        # First listing should score higher
        self.assertGreater(scored[0]['quality_score'], scored[1]['quality_score'])

    def test_filter_by_quality(self):
        """Test filtering listings by quality threshold"""
        listings = [
            {
                'title': 'High Quality',
                'price': 25000000,
                'location': 'Lekki',
                'listing_url': 'https://example.com/1',
                'bedrooms': 3,
                'bathrooms': 2,
                'property_type': 'Flat',
                'images': ['img1.jpg'],
                'coordinates': {'lat': 6.4474, 'lng': 3.4706}
            },
            {
                'title': 'Low Quality',
                'price': None,
                'location': '',
                'listing_url': 'https://example.com/2'
            }
        ]

        filtered = self.scorer.filter_by_quality(listings, min_score=60.0)

        # Should keep only high quality listing
        self.assertLess(len(filtered), len(listings))

    def test_get_quality_summary(self):
        """Test quality summary statistics"""
        listings = [
            {
                'quality_score': 90.0,
                'quality_issues': []
            },
            {
                'quality_score': 60.0,
                'quality_issues': ['Missing recommended field: images']
            },
            {
                'quality_score': 30.0,
                'quality_issues': ['Missing required field: price', 'Missing recommended field: bedrooms']
            }
        ]

        summary = self.scorer.get_quality_summary(listings)

        self.assertEqual(summary['total_listings'], 3)
        self.assertGreater(summary['avg_quality_score'], 0)
        self.assertEqual(summary['quality_distribution']['high_quality_count'], 1)
        self.assertEqual(summary['quality_distribution']['medium_quality_count'], 1)
        self.assertEqual(summary['quality_distribution']['low_quality_count'], 1)

    def test_categorize_by_quality(self):
        """Test categorizing listings into quality tiers"""
        listings = [
            {
                'title': 'High',
                'price': 25000000,
                'location': 'Lekki',
                'listing_url': 'https://example.com/1',
                'bedrooms': 3,
                'bathrooms': 2,
                'property_type': 'Flat',
                'images': ['img1.jpg'],
                'coordinates': {'lat': 6.4474, 'lng': 3.4706},
                'description': 'Luxury apartment'
            },
            {
                'title': 'Medium',
                'price': 30000000,
                'location': 'Ikoyi',
                'listing_url': 'https://example.com/2',
                'bedrooms': 5
            },
            {
                'title': 'Low',
                'price': 20000000,
                'location': 'Ajah',
                'listing_url': 'https://example.com/3'
            }
        ]

        categorized = self.scorer.categorize_by_quality(listings)

        self.assertIn('high_quality', categorized)
        self.assertIn('medium_quality', categorized)
        self.assertIn('low_quality', categorized)

        # Verify total count
        total = (
            len(categorized['high_quality']) +
            len(categorized['medium_quality']) +
            len(categorized['low_quality'])
        )
        self.assertEqual(total, len(listings))

    def test_is_field_present(self):
        """Test field presence detection"""
        # Strings
        self.assertTrue(self.scorer._is_field_present('Some text'))
        self.assertFalse(self.scorer._is_field_present(''))
        self.assertFalse(self.scorer._is_field_present('   '))
        self.assertFalse(self.scorer._is_field_present(None))

        # Numbers
        self.assertTrue(self.scorer._is_field_present(25000000))
        self.assertTrue(self.scorer._is_field_present(3))
        self.assertFalse(self.scorer._is_field_present(0))
        self.assertFalse(self.scorer._is_field_present(None))

        # Lists
        self.assertTrue(self.scorer._is_field_present(['item1', 'item2']))
        self.assertFalse(self.scorer._is_field_present([]))

        # Dicts
        self.assertTrue(self.scorer._is_field_present({'key': 'value'}))
        self.assertFalse(self.scorer._is_field_present({}))

    def test_get_quality_scorer(self):
        """Test factory function"""
        scorer = get_quality_scorer()
        self.assertIsInstance(scorer, QualityScorer)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestQualityScorer)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("QUALITY SCORER TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All quality scorer tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
