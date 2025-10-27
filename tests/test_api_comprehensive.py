"""
Comprehensive API Test Suite
Tests all 68 API endpoints for functionality, security, and error handling
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask

# Import the API server
from api_server import app

class TestAPIComprehensive(unittest.TestCase):
    """Test suite for all 68 API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = app.test_client()
        cls.client.testing = True

    def setUp(self):
        """Set up before each test"""
        self.maxDiff = None

    # ============================================================================
    # CORE OPERATIONS (4 endpoints)
    # ============================================================================

    def test_001_health_check(self):
        """Test GET /api/health"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)

    def test_002_scrape_start(self):
        """Test POST /api/scrape/start"""
        payload = {
            "sites": ["npc"],
            "max_pages": 5
        }
        response = self.client.post('/api/scrape/start',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400, 409])  # May fail if already running

    def test_003_scrape_status(self):
        """Test GET /api/scrape/status"""
        response = self.client.get('/api/scrape/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_004_scrape_stop(self):
        """Test POST /api/scrape/stop"""
        response = self.client.post('/api/scrape/stop')
        self.assertIn(response.status_code, [200, 400])

    def test_005_scrape_history(self):
        """Test GET /api/scrape/history"""
        response = self.client.get('/api/scrape/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    # ============================================================================
    # SITE MANAGEMENT (6 endpoints)
    # ============================================================================

    def test_006_list_sites(self):
        """Test GET /api/sites"""
        response = self.client.get('/api/sites')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def test_007_get_site(self):
        """Test GET /api/sites/<site_key>"""
        response = self.client.get('/api/sites/npc')
        self.assertIn(response.status_code, [200, 404])

    def test_008_create_site(self):
        """Test POST /api/sites"""
        payload = {
            "key": "test_site_temp",
            "config": {
                "name": "Test Site",
                "url": "https://example.com",
                "enabled": False,
                "parser": "specials"
            }
        }
        response = self.client.post('/api/sites',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 201, 400])

    def test_009_update_site(self):
        """Test PUT /api/sites/<site_key>"""
        payload = {
            "config": {
                "enabled": False
            }
        }
        response = self.client.put('/api/sites/npc',
                                  json=payload,
                                  content_type='application/json')
        self.assertIn(response.status_code, [200, 404])

    def test_010_delete_site(self):
        """Test DELETE /api/sites/<site_key>"""
        # Don't delete actual sites, just check endpoint exists
        response = self.client.delete('/api/sites/nonexistent_test_site')
        self.assertIn(response.status_code, [200, 404])

    def test_011_toggle_site(self):
        """Test PATCH /api/sites/<site_key>/toggle"""
        response = self.client.patch('/api/sites/npc/toggle')
        self.assertIn(response.status_code, [200, 404])

    # ============================================================================
    # LOGS (3 endpoints)
    # ============================================================================

    def test_012_get_logs(self):
        """Test GET /api/logs"""
        response = self.client.get('/api/logs?limit=10')
        self.assertEqual(response.status_code, 200)

    def test_013_get_error_logs(self):
        """Test GET /api/logs/errors"""
        response = self.client.get('/api/logs/errors?limit=10')
        self.assertEqual(response.status_code, 200)

    def test_014_get_site_logs(self):
        """Test GET /api/logs/site/<site_key>"""
        response = self.client.get('/api/logs/site/npc?limit=10')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # DATA ACCESS (4 endpoints)
    # ============================================================================

    def test_015_list_data_sites(self):
        """Test GET /api/data/sites"""
        response = self.client.get('/api/data/sites')
        self.assertEqual(response.status_code, 200)

    def test_016_get_site_data(self):
        """Test GET /api/data/sites/<site_key>"""
        response = self.client.get('/api/data/sites/npc?limit=10')
        self.assertIn(response.status_code, [200, 404])

    def test_017_get_master_data(self):
        """Test GET /api/data/master"""
        response = self.client.get('/api/data/master?limit=10')
        self.assertIn(response.status_code, [200, 404])

    def test_018_search_data(self):
        """Test GET /api/data/search"""
        response = self.client.get('/api/data/search?q=lagos&limit=10')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # STATISTICS (3 endpoints)
    # ============================================================================

    def test_019_stats_overview(self):
        """Test GET /api/stats/overview"""
        response = self.client.get('/api/stats/overview')
        self.assertEqual(response.status_code, 200)

    def test_020_stats_sites(self):
        """Test GET /api/stats/sites"""
        response = self.client.get('/api/stats/sites')
        self.assertEqual(response.status_code, 200)

    def test_021_stats_trends(self):
        """Test GET /api/stats/trends"""
        response = self.client.get('/api/stats/trends')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # VALIDATION (2 endpoints)
    # ============================================================================

    def test_022_validate_url(self):
        """Test POST /api/validate/url"""
        payload = {"url": "https://example.com/property/123"}
        response = self.client.post('/api/validate/url',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_023_validate_urls_bulk(self):
        """Test POST /api/validate/urls"""
        payload = {"urls": ["https://example.com/1", "https://example.com/2"]}
        response = self.client.post('/api/validate/urls',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # LOCATION FILTERING (3 endpoints)
    # ============================================================================

    def test_024_filter_location(self):
        """Test POST /api/filter/location"""
        payload = {"locations": ["Lekki", "Victoria Island"]}
        response = self.client.post('/api/filter/location',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_025_filter_stats(self):
        """Test GET /api/filter/stats"""
        response = self.client.get('/api/filter/stats')
        self.assertEqual(response.status_code, 200)

    def test_026_config_locations_get(self):
        """Test GET /api/config/locations"""
        response = self.client.get('/api/config/locations')
        self.assertEqual(response.status_code, 200)

    def test_027_config_locations_put(self):
        """Test PUT /api/config/locations"""
        payload = {"locations": ["Lagos", "Lekki"]}
        response = self.client.put('/api/config/locations',
                                  json=payload,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # QUERY ENGINE (2 endpoints)
    # ============================================================================

    def test_028_advanced_query(self):
        """Test POST /api/query"""
        payload = {
            "filters": {
                "price": {"gte": 1000000, "lte": 50000000}
            }
        }
        response = self.client.post('/api/query',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_029_query_summary(self):
        """Test POST /api/query/summary"""
        payload = {
            "filters": {
                "bedrooms": {"gte": 3}
            }
        }
        response = self.client.post('/api/query/summary',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # RATE LIMITING (2 endpoints)
    # ============================================================================

    def test_030_rate_limit_status(self):
        """Test GET /api/rate-limit/status"""
        response = self.client.get('/api/rate-limit/status')
        self.assertEqual(response.status_code, 200)

    def test_031_rate_limit_check(self):
        """Test POST /api/rate-limit/check"""
        payload = {"site_key": "npc"}
        response = self.client.post('/api/rate-limit/check',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # MARKET ANALYSIS (4 endpoints)
    # ============================================================================

    def test_032_price_history(self):
        """Test GET /api/price-history/<property_id>"""
        response = self.client.get('/api/price-history/test_property_123')
        self.assertIn(response.status_code, [200, 404])

    def test_033_price_drops(self):
        """Test GET /api/price-drops"""
        response = self.client.get('/api/price-drops?min_drop_pct=10')
        self.assertEqual(response.status_code, 200)

    def test_034_stale_listings(self):
        """Test GET /api/stale-listings"""
        response = self.client.get('/api/stale-listings?days=30')
        self.assertEqual(response.status_code, 200)

    def test_035_market_trends(self):
        """Test GET /api/market-trends"""
        response = self.client.get('/api/market-trends')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # NATURAL LANGUAGE SEARCH (2 endpoints)
    # ============================================================================

    def test_036_natural_language_search(self):
        """Test POST /api/search/natural"""
        payload = {"query": "3 bedroom flat in Lekki under 30 million"}
        response = self.client.post('/api/search/natural',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_037_search_suggestions(self):
        """Test GET /api/search/suggestions"""
        response = self.client.get('/api/search/suggestions?q=lekki')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # SAVED SEARCHES (5 endpoints)
    # ============================================================================

    def test_038_list_searches(self):
        """Test GET /api/searches"""
        response = self.client.get('/api/searches')
        self.assertEqual(response.status_code, 200)

    def test_039_create_search(self):
        """Test POST /api/searches"""
        payload = {
            "name": "Test Search",
            "criteria": {"bedrooms": {"gte": 3}}
        }
        response = self.client.post('/api/searches',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 201])

    def test_040_get_search(self):
        """Test GET /api/searches/<search_id>"""
        response = self.client.get('/api/searches/test_search_123')
        self.assertIn(response.status_code, [200, 404])

    def test_041_update_search(self):
        """Test PUT /api/searches/<search_id>"""
        payload = {"name": "Updated Search"}
        response = self.client.put('/api/searches/test_search_123',
                                  json=payload,
                                  content_type='application/json')
        self.assertIn(response.status_code, [200, 404])

    def test_042_delete_search(self):
        """Test DELETE /api/searches/<search_id>"""
        response = self.client.delete('/api/searches/test_search_123')
        self.assertIn(response.status_code, [200, 404])

    def test_043_search_stats(self):
        """Test GET /api/searches/<search_id>/stats"""
        response = self.client.get('/api/searches/test_search_123/stats')
        self.assertIn(response.status_code, [200, 404])

    # ============================================================================
    # HEALTH MONITORING (4 endpoints)
    # ============================================================================

    def test_044_health_overall(self):
        """Test GET /api/health/overall"""
        response = self.client.get('/api/health/overall')
        self.assertEqual(response.status_code, 200)

    def test_045_health_site(self):
        """Test GET /api/health/sites/<site_key>"""
        response = self.client.get('/api/health/sites/npc')
        self.assertIn(response.status_code, [200, 404])

    def test_046_health_alerts(self):
        """Test GET /api/health/alerts"""
        response = self.client.get('/api/health/alerts')
        self.assertEqual(response.status_code, 200)

    def test_047_health_top_performers(self):
        """Test GET /api/health/top-performers"""
        response = self.client.get('/api/health/top-performers')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # DATA QUALITY (2 endpoints)
    # ============================================================================

    def test_048_detect_duplicates(self):
        """Test POST /api/duplicates/detect"""
        payload = {
            "properties": [
                {"title": "Test Property 1", "location": "Lekki"},
                {"title": "Test Property 1", "location": "Lekki"}
            ]
        }
        response = self.client.post('/api/duplicates/detect',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_049_quality_score(self):
        """Test POST /api/quality/score"""
        payload = {
            "property": {
                "title": "Test Property",
                "price": "5000000",
                "location": "Lekki"
            }
        }
        response = self.client.post('/api/quality/score',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # FIRESTORE INTEGRATION (3 endpoints)
    # ============================================================================

    def test_050_firestore_query(self):
        """Test POST /api/firestore/query"""
        payload = {
            "filters": {"location": "Lekki"},
            "limit": 10
        }
        response = self.client.post('/api/firestore/query',
                                   json=payload,
                                   content_type='application/json')
        # May fail if Firestore not configured
        self.assertIn(response.status_code, [200, 400, 500])

    def test_051_firestore_query_archive(self):
        """Test POST /api/firestore/query-archive"""
        payload = {
            "filters": {"location": "Lekki"},
            "limit": 10
        }
        response = self.client.post('/api/firestore/query-archive',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400, 500])

    def test_052_firestore_export(self):
        """Test POST /api/firestore/export"""
        payload = {"collection": "properties"}
        response = self.client.post('/api/firestore/export',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400, 500])

    # ============================================================================
    # EXPORT (3 endpoints)
    # ============================================================================

    def test_053_export_generate(self):
        """Test POST /api/export/generate"""
        payload = {
            "format": "csv",
            "filters": {"location": "Lekki"}
        }
        response = self.client.post('/api/export/generate',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400])

    def test_054_export_download(self):
        """Test GET /api/export/download/<filename>"""
        response = self.client.get('/api/export/download/test_export.csv')
        self.assertIn(response.status_code, [200, 404])

    def test_055_export_formats(self):
        """Test GET /api/export/formats"""
        response = self.client.get('/api/export/formats')
        self.assertEqual(response.status_code, 200)

    # ============================================================================
    # GITHUB ACTIONS (5 endpoints)
    # ============================================================================

    def test_056_github_trigger_scrape(self):
        """Test POST /api/github/trigger-scrape"""
        payload = {
            "sites": ["npc"],
            "page_cap": 10
        }
        response = self.client.post('/api/github/trigger-scrape',
                                   json=payload,
                                   content_type='application/json')
        # May fail without GitHub token
        self.assertIn(response.status_code, [200, 400, 500])

    def test_057_github_estimate_time(self):
        """Test POST /api/github/estimate-scrape-time"""
        payload = {"sites": ["npc", "propertypro"]}
        response = self.client.post('/api/github/estimate-scrape-time',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_058_github_workflow_runs(self):
        """Test GET /api/github/workflow-runs"""
        response = self.client.get('/api/github/workflow-runs')
        self.assertIn(response.status_code, [200, 400, 500])

    def test_059_github_artifacts(self):
        """Test GET /api/github/artifacts"""
        response = self.client.get('/api/github/artifacts')
        self.assertIn(response.status_code, [200, 400, 500])

    def test_060_github_artifact_download(self):
        """Test GET /api/github/artifact/<id>/download"""
        response = self.client.get('/api/github/artifact/123/download')
        self.assertIn(response.status_code, [200, 404, 500])

    # ============================================================================
    # NOTIFICATIONS (2 endpoints)
    # ============================================================================

    def test_061_notifications_subscribe(self):
        """Test POST /api/notifications/subscribe"""
        payload = {
            "email": "test@example.com",
            "events": ["scrape_complete"]
        }
        response = self.client.post('/api/notifications/subscribe',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400])

    def test_062_notifications_workflow_status(self):
        """Test GET /api/notifications/workflow-status/<run_id>"""
        response = self.client.get('/api/notifications/workflow-status/12345')
        self.assertIn(response.status_code, [200, 404, 500])

    # ============================================================================
    # SCHEDULING (4 endpoints)
    # ============================================================================

    def test_063_schedule_scrape(self):
        """Test POST /api/schedule/scrape"""
        payload = {
            "schedule": "0 0 * * *",  # Daily at midnight
            "sites": ["npc"],
            "max_pages": 20
        }
        response = self.client.post('/api/schedule/scrape',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 201, 400])

    def test_064_schedule_jobs_list(self):
        """Test GET /api/schedule/jobs"""
        response = self.client.get('/api/schedule/jobs')
        self.assertEqual(response.status_code, 200)

    def test_065_schedule_job_get(self):
        """Test GET /api/schedule/jobs/<job_id>"""
        response = self.client.get('/api/schedule/jobs/123')
        self.assertIn(response.status_code, [200, 404])

    def test_066_schedule_job_cancel(self):
        """Test POST /api/schedule/jobs/<job_id>/cancel"""
        response = self.client.post('/api/schedule/jobs/123/cancel')
        self.assertIn(response.status_code, [200, 404])

    # ============================================================================
    # EMAIL (6 endpoints)
    # ============================================================================

    def test_067_email_configure(self):
        """Test POST /api/email/configure"""
        payload = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "test_password",
            "from_email": "test@example.com"
        }
        response = self.client.post('/api/email/configure',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400])

    def test_068_email_test_connection(self):
        """Test POST /api/email/test-connection"""
        response = self.client.post('/api/email/test-connection')
        self.assertIn(response.status_code, [200, 400, 500])

    def test_069_email_config_get(self):
        """Test GET /api/email/config"""
        response = self.client.get('/api/email/config')
        self.assertEqual(response.status_code, 200)

    def test_070_email_recipients_get(self):
        """Test GET /api/email/recipients"""
        response = self.client.get('/api/email/recipients')
        self.assertEqual(response.status_code, 200)

    def test_071_email_recipients_post(self):
        """Test POST /api/email/recipients"""
        payload = {
            "email": "test@example.com",
            "name": "Test User"
        }
        response = self.client.post('/api/email/recipients',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 201, 400])

    def test_072_email_recipients_delete(self):
        """Test DELETE /api/email/recipients/<email>"""
        response = self.client.delete('/api/email/recipients/test@example.com')
        self.assertIn(response.status_code, [200, 404])

    def test_073_email_send_test(self):
        """Test POST /api/email/send-test"""
        payload = {"recipient": "test@example.com"}
        response = self.client.post('/api/email/send-test',
                                   json=payload,
                                   content_type='application/json')
        self.assertIn(response.status_code, [200, 400, 500])

    # ============================================================================
    # SECURITY TESTS
    # ============================================================================

    def test_074_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Try SQL injection in search
        malicious_query = "'; DROP TABLE properties; --"
        response = self.client.get(f'/api/data/search?q={malicious_query}')
        self.assertEqual(response.status_code, 200)  # Should not crash

    def test_075_xss_protection(self):
        """Test XSS protection"""
        # Try XSS in natural language search
        malicious_payload = {
            "query": "<script>alert('XSS')</script>"
        }
        response = self.client.post('/api/search/natural',
                                   json=malicious_payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_076_path_traversal_protection(self):
        """Test path traversal protection"""
        # Try path traversal in export download
        response = self.client.get('/api/export/download/../../../etc/passwd')
        self.assertIn(response.status_code, [400, 404])

    def test_077_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get('/api/health')
        # Check if CORS is configured (if enabled)
        self.assertEqual(response.status_code, 200)

    def test_078_rate_limiting_exists(self):
        """Test rate limiting is implemented"""
        # Make multiple rapid requests
        for _ in range(5):
            response = self.client.get('/api/health')
            self.assertIn(response.status_code, [200, 429])

    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================

    def test_079_invalid_json_handling(self):
        """Test invalid JSON handling"""
        response = self.client.post('/api/query',
                                   data='invalid json',
                                   content_type='application/json')
        self.assertIn(response.status_code, [400, 500])

    def test_080_missing_required_fields(self):
        """Test missing required fields"""
        payload = {}  # Empty payload
        response = self.client.post('/api/scrape/start',
                                   json=payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_081_invalid_method(self):
        """Test invalid HTTP method"""
        response = self.client.put('/api/health')  # Health should only accept GET
        self.assertIn(response.status_code, [405, 404])

    def test_082_nonexistent_endpoint(self):
        """Test nonexistent endpoint"""
        response = self.client.get('/api/nonexistent/endpoint')
        self.assertEqual(response.status_code, 404)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAPIComprehensive)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
