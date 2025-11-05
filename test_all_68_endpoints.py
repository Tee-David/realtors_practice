"""
Test all 68 API endpoints and generate comprehensive documentation
"""
import requests
import json
from typing import Dict, Any, List
import time

BASE_URL = "http://localhost:5000"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()

    def test_endpoint(self, method: str, path: str, description: str,
                     data: Dict = None, params: Dict = None,
                     expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{BASE_URL}{path}"

        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
            elif method == "PATCH":
                response = self.session.patch(url, json=data, timeout=10)

            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text

            result = {
                "method": method,
                "path": path,
                "description": description,
                "status": response.status_code,
                "success": response.status_code == expected_status,
                "response": response_data,
                "request_data": data or params
            }

            print(f"[OK] {method} {path} - {response.status_code}")

        except Exception as e:
            result = {
                "method": method,
                "path": path,
                "description": description,
                "status": None,
                "success": False,
                "error": str(e),
                "request_data": data or params
            }
            print(f"[FAIL] {method} {path} - ERROR: {str(e)}")

        self.results.append(result)
        return result

    def run_all_tests(self):
        """Test all 68 endpoints"""

        print("\n=== CATEGORY 1: SCRAPING MANAGEMENT (5 endpoints) ===\n")

        # 1. Health check
        self.test_endpoint("GET", "/api/health", "Check API health status")

        # 2. Get scrape status
        self.test_endpoint("GET", "/api/scrape/status", "Get current scraping status")

        # 3. Get scrape history
        self.test_endpoint("GET", "/api/scrape/history", "Get scraping history")

        # 4. Start scraping (with test data)
        self.test_endpoint("POST", "/api/scrape/start",
                          "Start scraping specific sites",
                          data={"sites": ["cwlagos"], "max_pages": 2, "test_mode": True})

        # 5. Stop scraping
        self.test_endpoint("POST", "/api/scrape/stop", "Stop current scraping process")

        print("\n=== CATEGORY 2: SITE CONFIGURATION (6 endpoints) ===\n")

        # 6. Get all sites
        self.test_endpoint("GET", "/api/sites", "Get all configured sites")

        # 7. Get specific site
        self.test_endpoint("GET", "/api/sites/cwlagos", "Get specific site configuration")

        # 8. Add new site
        self.test_endpoint("POST", "/api/sites",
                          "Add a new site configuration",
                          data={
                              "site_key": "test_site_api",
                              "name": "Test Site for API",
                              "url": "https://example.com",
                              "enabled": False
                          })

        # 9. Update site
        self.test_endpoint("PUT", "/api/sites/test_site_api",
                          "Update site configuration",
                          data={"enabled": True, "max_pages": 10})

        # 10. Toggle site
        self.test_endpoint("PATCH", "/api/sites/test_site_api/toggle",
                          "Toggle site enable/disable status")

        # 11. Delete site
        self.test_endpoint("DELETE", "/api/sites/test_site_api",
                          "Delete a site configuration")

        print("\n=== CATEGORY 3: DATA ACCESS (4 endpoints) ===\n")

        # 12. Get all sites data
        self.test_endpoint("GET", "/api/data/sites",
                          "Get data from all sites",
                          params={"limit": 5})

        # 13. Get specific site data
        self.test_endpoint("GET", "/api/data/sites/cwlagos",
                          "Get data from specific site",
                          params={"limit": 5})

        # 14. Get master workbook data
        self.test_endpoint("GET", "/api/data/master",
                          "Get master workbook data",
                          params={"limit": 5})

        # 15. Search data
        self.test_endpoint("GET", "/api/data/search",
                          "Search property data",
                          params={"query": "Lekki", "limit": 5})

        print("\n=== CATEGORY 4: LOGS (3 endpoints) ===\n")

        # 16. Get logs
        self.test_endpoint("GET", "/api/logs",
                          "Get application logs",
                          params={"limit": 20})

        # 17. Get error logs
        self.test_endpoint("GET", "/api/logs/errors",
                          "Get error logs only",
                          params={"limit": 10})

        # 18. Get site-specific logs
        self.test_endpoint("GET", "/api/logs/site/cwlagos",
                          "Get logs for specific site",
                          params={"limit": 10})

        print("\n=== CATEGORY 5: STATISTICS (3 endpoints) ===\n")

        # 19. Get overview stats
        self.test_endpoint("GET", "/api/stats/overview",
                          "Get overall statistics overview")

        # 20. Get site stats
        self.test_endpoint("GET", "/api/stats/sites",
                          "Get statistics for all sites")

        # 21. Get trends
        self.test_endpoint("GET", "/api/stats/trends",
                          "Get market trends analysis",
                          params={"days": 30})

        print("\n=== CATEGORY 6: VALIDATION (2 endpoints) ===\n")

        # 22. Validate single URL
        self.test_endpoint("POST", "/api/validate/url",
                          "Validate a single property URL",
                          data={"url": "https://cwlagos.com/property/5-bedroom-villa"})

        # 23. Validate multiple URLs
        self.test_endpoint("POST", "/api/validate/urls",
                          "Validate multiple property URLs",
                          data={"urls": [
                              "https://cwlagos.com/property/5-bedroom-villa",
                              "https://invalid-url"
                          ]})

        print("\n=== CATEGORY 7: FILTERING (3 endpoints) ===\n")

        # 24. Filter by location
        self.test_endpoint("POST", "/api/filter/location",
                          "Filter properties by location",
                          data={"location": "Lekki", "limit": 5})

        # 25. Get filter stats
        self.test_endpoint("GET", "/api/filter/stats",
                          "Get filtering statistics")

        # 26. Get location config
        self.test_endpoint("GET", "/api/config/locations",
                          "Get location configuration")

        print("\n=== CATEGORY 8: ADVANCED QUERY (2 endpoints) ===\n")

        # 27. Advanced query
        self.test_endpoint("POST", "/api/query",
                          "Perform advanced property query",
                          data={
                              "filters": {
                                  "location": "Lekki",
                                  "min_price": 50000000,
                                  "max_price": 500000000,
                                  "bedrooms": 4
                              },
                              "limit": 5
                          })

        # 28. Query summary
        self.test_endpoint("POST", "/api/query/summary",
                          "Get query results summary",
                          data={
                              "filters": {
                                  "location": "Lekki"
                              }
                          })

        print("\n=== CATEGORY 9: RATE LIMITING (2 endpoints) ===\n")

        # 29. Get rate limit status
        self.test_endpoint("GET", "/api/rate-limit/status",
                          "Get rate limiting status")

        # 30. Check rate limit
        self.test_endpoint("POST", "/api/rate-limit/check",
                          "Check rate limit for operation",
                          data={"operation": "scrape"})

        print("\n=== CATEGORY 10: PRICE INTELLIGENCE (4 endpoints) ===\n")

        # 31. Get price history
        self.test_endpoint("GET", "/api/price-history/test_property_123",
                          "Get price history for property")

        # 32. Get price drops
        self.test_endpoint("GET", "/api/price-drops",
                          "Get properties with price drops",
                          params={"days": 30, "limit": 5})

        # 33. Get stale listings
        self.test_endpoint("GET", "/api/stale-listings",
                          "Get stale property listings",
                          params={"days": 60, "limit": 5})

        # 34. Get market trends
        self.test_endpoint("GET", "/api/market-trends",
                          "Get market trends analysis",
                          params={"location": "Lekki", "days": 30})

        print("\n=== CATEGORY 11: NATURAL LANGUAGE SEARCH (2 endpoints) ===\n")

        # 35. Natural language search
        self.test_endpoint("POST", "/api/search/natural",
                          "Search using natural language",
                          data={
                              "query": "4 bedroom house in Lekki under 200 million",
                              "limit": 5
                          })

        # 36. Get search suggestions
        self.test_endpoint("GET", "/api/search/suggestions",
                          "Get search suggestions",
                          params={"query": "4 bed"})

        print("\n=== CATEGORY 12: SAVED SEARCHES (5 endpoints) ===\n")

        # 37. Create saved search
        search_response = self.test_endpoint("POST", "/api/searches",
                          "Create a saved search",
                          data={
                              "name": "Lekki Properties",
                              "query": {
                                  "location": "Lekki",
                                  "min_bedrooms": 4
                              },
                              "alert_enabled": True
                          })

        # Get search_id from response
        search_id = None
        if search_response.get("success") and "response" in search_response:
            search_id = search_response["response"].get("search_id")

        # 38. Get all saved searches
        self.test_endpoint("GET", "/api/searches",
                          "Get all saved searches")

        if search_id:
            # 39. Get specific search
            self.test_endpoint("GET", f"/api/searches/{search_id}",
                              "Get specific saved search")

            # 40. Update search
            self.test_endpoint("PUT", f"/api/searches/{search_id}",
                              "Update a saved search",
                              data={"name": "Updated Lekki Properties"})

            # 41. Get search stats
            self.test_endpoint("GET", f"/api/searches/{search_id}/stats",
                              "Get statistics for saved search")
        else:
            # Use placeholder
            self.test_endpoint("GET", "/api/searches/test_search_id",
                              "Get specific saved search", expected_status=404)
            self.test_endpoint("PUT", "/api/searches/test_search_id",
                              "Update a saved search",
                              data={"name": "Updated Search"}, expected_status=404)
            self.test_endpoint("GET", "/api/searches/test_search_id/stats",
                              "Get statistics for saved search", expected_status=404)

        print("\n=== CATEGORY 13: HEALTH MONITORING (4 endpoints) ===\n")

        # 42. Overall health
        self.test_endpoint("GET", "/api/health/overall",
                          "Get overall system health")

        # 43. Site health
        self.test_endpoint("GET", "/api/health/sites/cwlagos",
                          "Get health status for specific site")

        # 44. Health alerts
        self.test_endpoint("GET", "/api/health/alerts",
                          "Get health monitoring alerts")

        # 45. Top performers
        self.test_endpoint("GET", "/api/health/top-performers",
                          "Get top performing sites",
                          params={"limit": 5})

        print("\n=== CATEGORY 14: DATA QUALITY (2 endpoints) ===\n")

        # 46. Detect duplicates
        self.test_endpoint("POST", "/api/duplicates/detect",
                          "Detect duplicate properties",
                          data={"source": "master", "limit": 5})

        # 47. Score quality
        self.test_endpoint("POST", "/api/quality/score",
                          "Calculate data quality score",
                          data={"source": "master", "limit": 5})

        print("\n=== CATEGORY 15: FIRESTORE INTEGRATION (3 endpoints) ===\n")

        # 48. Query Firestore
        self.test_endpoint("POST", "/api/firestore/query",
                          "Query Firestore database",
                          data={
                              "filters": {"location": "Lekki"},
                              "limit": 5
                          })

        # 49. Query archive
        self.test_endpoint("POST", "/api/firestore/query-archive",
                          "Query Firestore archive",
                          data={
                              "filters": {"location": "Lekki"},
                              "limit": 5
                          })

        # 50. Export to Firestore
        self.test_endpoint("POST", "/api/firestore/export",
                          "Export data to Firestore",
                          data={
                              "source": "master",
                              "test_mode": True,
                              "limit": 5
                          })

        print("\n=== CATEGORY 16: EXPORT (3 endpoints) ===\n")

        # 51. Generate export
        self.test_endpoint("POST", "/api/export/generate",
                          "Generate data export file",
                          data={
                              "format": "csv",
                              "source": "master",
                              "limit": 10
                          })

        # 52. Get export formats
        self.test_endpoint("GET", "/api/export/formats",
                          "Get available export formats")

        # 53. Download export (skip actual download)
        self.test_endpoint("GET", "/api/export/download/test.csv",
                          "Download export file", expected_status=404)

        print("\n=== CATEGORY 17: GITHUB ACTIONS (4 endpoints) ===\n")

        # 54. Trigger scrape
        self.test_endpoint("POST", "/api/github/trigger-scrape",
                          "Trigger GitHub Actions scrape workflow",
                          data={
                              "sites": ["cwlagos"],
                              "test_mode": True
                          })

        # 55. Estimate scrape time
        self.test_endpoint("POST", "/api/github/estimate-scrape-time",
                          "Estimate scraping time",
                          data={"sites": ["cwlagos", "npc"]})

        # 56. Get workflow runs
        self.test_endpoint("GET", "/api/github/workflow-runs",
                          "Get GitHub workflow runs",
                          params={"limit": 5})

        # 57. Get artifacts
        self.test_endpoint("GET", "/api/github/artifacts",
                          "Get workflow artifacts",
                          params={"limit": 5})

        print("\n=== CATEGORY 18: SCHEDULER (4 endpoints) ===\n")

        # 58. Schedule scrape
        job_response = self.test_endpoint("POST", "/api/schedule/scrape",
                          "Schedule a scraping job",
                          data={
                              "sites": ["cwlagos"],
                              "schedule_time": "2025-12-31T10:00:00",
                              "recurring": False
                          })

        # Get job_id
        job_id = None
        if job_response.get("success") and "response" in job_response:
            job_id = job_response["response"].get("job_id")

        # 59. Get all scheduled jobs
        self.test_endpoint("GET", "/api/schedule/jobs",
                          "Get all scheduled jobs")

        if job_id:
            # 60. Get specific job
            self.test_endpoint("GET", f"/api/schedule/jobs/{job_id}",
                              "Get specific scheduled job")

            # 61. Cancel job
            self.test_endpoint("POST", f"/api/schedule/jobs/{job_id}/cancel",
                              "Cancel a scheduled job")
        else:
            self.test_endpoint("GET", "/api/schedule/jobs/999",
                              "Get specific scheduled job", expected_status=404)
            self.test_endpoint("POST", "/api/schedule/jobs/999/cancel",
                              "Cancel a scheduled job", expected_status=404)

        print("\n=== CATEGORY 19: EMAIL NOTIFICATIONS (6 endpoints) ===\n")

        # 62. Configure email
        self.test_endpoint("POST", "/api/email/configure",
                          "Configure email settings",
                          data={
                              "smtp_server": "smtp.gmail.com",
                              "smtp_port": 587,
                              "sender_email": "test@example.com",
                              "test_mode": True
                          })

        # 63. Test connection
        self.test_endpoint("POST", "/api/email/test-connection",
                          "Test email connection",
                          data={
                              "smtp_server": "smtp.gmail.com",
                              "smtp_port": 587
                          })

        # 64. Get email config
        self.test_endpoint("GET", "/api/email/config",
                          "Get email configuration")

        # 65. Get recipients
        self.test_endpoint("GET", "/api/email/recipients",
                          "Get email recipients list")

        # 66. Add recipient
        self.test_endpoint("POST", "/api/email/recipients",
                          "Add email recipient",
                          data={"email": "test_recipient@example.com"})

        # 67. Send test email
        self.test_endpoint("POST", "/api/email/send-test",
                          "Send test email",
                          data={"recipient": "test@example.com"})

        # 68. Delete recipient
        self.test_endpoint("DELETE", "/api/email/recipients/test_recipient@example.com",
                          "Remove email recipient")

        print("\n\n=== TESTING COMPLETE ===\n")
        print(f"Total endpoints tested: {len(self.results)}")
        successful = sum(1 for r in self.results if r.get("success"))
        print(f"Successful: {successful}")
        print(f"Failed: {len(self.results) - successful}")

    def save_results(self, filename: str):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_all_tests()
    tester.save_results("endpoint_test_results.json")
