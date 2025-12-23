"""
Tests for Natural Language Search Module

Tests NL query parsing and filter generation.

Author: Tee-David
Date: 2025-10-20
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.natural_language_search import NaturalLanguageSearchParser, get_nl_search_parser


class TestNaturalLanguageSearchParser(unittest.TestCase):
    """Test NaturalLanguageSearchParser functionality"""

    def setUp(self):
        """Create parser instance"""
        self.parser = NaturalLanguageSearchParser()

    def test_initialization(self):
        """Test parser initializes correctly"""
        self.assertIsNotNone(self.parser)

    def test_parse_simple_query(self):
        """Test parsing simple query with bedrooms and location"""
        query = "3 bedroom flat in Lekki"
        result = self.parser.parse_query(query)

        self.assertEqual(result['original_query'], query)
        self.assertIn('property_type', result['filters'])
        self.assertIn('bedrooms', result['filters'])
        self.assertIn('location', result['filters'])

        self.assertEqual(result['filters']['bedrooms']['gte'], 3)
        self.assertIn('Lekki', result['filters']['location']['contains'])

    def test_parse_price_under(self):
        """Test parsing 'under' price constraint"""
        query = "flat in Lekki under 30 million"
        result = self.parser.parse_query(query)

        self.assertIn('price', result['filters'])
        self.assertEqual(result['filters']['price']['lte'], 30_000_000)

    def test_parse_price_between(self):
        """Test parsing 'between' price range"""
        query = "duplex in Ikoyi between 50M and 100M"
        result = self.parser.parse_query(query)

        self.assertIn('price', result['filters'])
        self.assertEqual(result['filters']['price']['between'], [50_000_000, 100_000_000])

    def test_parse_complex_query(self):
        """Test parsing complex query with multiple criteria"""
        query = "4 bedroom duplex in Victoria Island under 80 million with pool"
        result = self.parser.parse_query(query)

        # Check filters
        self.assertIn('bedrooms', result['filters'])
        self.assertEqual(result['filters']['bedrooms']['gte'], 4)

        self.assertIn('property_type', result['filters'])
        self.assertIn('Duplex', result['filters']['property_type']['contains'])

        self.assertIn('location', result['filters'])

        self.assertIn('price', result['filters'])
        self.assertEqual(result['filters']['price']['lte'], 80_000_000)

        # Check features
        self.assertIn('pool', result['features'])

        # Should have high confidence
        self.assertGreater(result['confidence'], 0.5)

    def test_parse_land_query(self):
        """Test parsing land search query"""
        query = "land for sale in Ajah with c of o"
        result = self.parser.parse_query(query)

        self.assertIn('property_type', result['filters'])
        self.assertIn('Land', result['filters']['property_type']['contains'])

        self.assertIn('location', result['filters'])

        self.assertIn('c_of_o', result['features'])

    def test_parse_price_millions(self):
        """Test parsing prices in millions"""
        queries_and_expected = [
            ("under 30M", 30_000_000),
            ("under 30 million", 30_000_000),
            ("under 30m", 30_000_000),
            ("max 25M", 25_000_000)
        ]

        for query, expected_price in queries_and_expected:
            result = self.parser.parse_query(query)
            if 'price' in result['filters']:
                actual_price = result['filters']['price'].get('lte', 0)
                self.assertEqual(actual_price, expected_price,
                               f"Failed for query: {query}")

    def test_parse_bedroom_variations(self):
        """Test different bedroom notation formats"""
        queries = [
            "3 bedroom flat",
            "3 bed apartment",
            "3BR flat",
            "3 br apartment"
        ]

        for query in queries:
            result = self.parser.parse_query(query)
            self.assertIn('bedrooms', result['filters'],
                         f"Failed for query: {query}")
            self.assertEqual(result['filters']['bedrooms']['gte'], 3,
                           f"Failed for query: {query}")

    def test_parse_property_types(self):
        """Test property type detection"""
        type_queries = {
            "flat in Lekki": "Flat",
            "duplex in Ikoyi": "Duplex",
            "land for sale": "Land",
            "terrace in Ikeja": "Terrace",
            "detached house": "Detached"
        }

        for query, expected_type in type_queries.items():
            result = self.parser.parse_query(query)
            self.assertIn('property_type', result['filters'],
                         f"Failed for query: {query}")
            self.assertIn(expected_type, result['filters']['property_type']['contains'],
                         f"Failed for query: {query}")

    def test_parse_locations(self):
        """Test location detection"""
        locations = ['Lekki', 'Ikoyi', 'Victoria Island', 'VI', 'Ajah', 'Ikeja']

        for location in locations:
            query = f"flat in {location}"
            result = self.parser.parse_query(query)

            self.assertIn('location', result['filters'],
                         f"Failed for location: {location}")

    def test_parse_features(self):
        """Test feature detection"""
        feature_queries = {
            "flat with pool": "pool",
            "house with bq": "bq",
            "land with c of o": "c_of_o",
            "serviced apartment": "serviced",
            "furnished flat": "furnished"
        }

        for query, expected_feature in feature_queries.items():
            result = self.parser.parse_query(query)
            self.assertIn(expected_feature, result['features'],
                         f"Failed for query: {query}")

    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # High confidence query (many criteria)
        high_conf_query = "3 bedroom flat in Lekki under 30 million with pool"
        high_result = self.parser.parse_query(high_conf_query)

        # Low confidence query (few criteria)
        low_conf_query = "property for sale"
        low_result = self.parser.parse_query(low_conf_query)

        self.assertGreater(high_result['confidence'], low_result['confidence'])

    def test_generate_query_engine_filters(self):
        """Test conversion to query engine format"""
        query = "3 bedroom flat in Lekki under 30M"
        parsed = self.parser.parse_query(query)

        filters = self.parser.generate_query_engine_filters(parsed)

        self.assertIsInstance(filters, dict)
        self.assertIn('bedrooms', filters)
        self.assertIn('location', filters)
        self.assertIn('price', filters)

    def test_parse_empty_query(self):
        """Test parsing empty query"""
        result = self.parser.parse_query("")

        self.assertEqual(len(result['filters']), 0)
        self.assertEqual(result['confidence'], 0.0)

    def test_get_suggestions(self):
        """Test search suggestions"""
        suggestions = self.parser.get_suggestions("3 bed")

        self.assertIsInstance(suggestions, list)

    def test_factory_function(self):
        """Test get_nl_search_parser factory"""
        parser = get_nl_search_parser()
        self.assertIsInstance(parser, NaturalLanguageSearchParser)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNaturalLanguageSearchParser)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("NATURAL LANGUAGE SEARCH TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All natural language search tests passed!")
    else:
        print("\n[FAIL] Some tests failed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
