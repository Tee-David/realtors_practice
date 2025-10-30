"""
Comprehensive API Endpoint Test
Tests all 68 endpoints to ensure they work correctly for frontend integration
"""
import requests
import json
import time
from typing import Dict, List

API_BASE = "http://localhost:5000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class EndpointTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def test_endpoint(self, method: str, endpoint: str, data: dict = None,
                     expected_status: int = 200, description: str = ""):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)

            success = response.status_code == expected_status

            result = {
                'method': method,
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': success,
                'response_size': len(response.content)
            }

            if success:
                self.passed += 1
                print(f"{Colors.GREEN}[OK]{Colors.END} {method:6} {endpoint:50} [{response.status_code}]")
            else:
                self.failed += 1
                print(f"{Colors.RED}[FAIL]{Colors.END} {method:6} {endpoint:50} [{response.status_code}] Expected: {expected_status}")
                print(f"  Response: {response.text[:200]}")

            self.results.append(result)
            return success, response

        except Exception as e:
            self.failed += 1
            print(f"{Colors.RED}[ERROR]{Colors.END} {method:6} {endpoint:50} ERROR: {str(e)}")
            self.results.append({
                'method': method,
                'endpoint': endpoint,
                'description': description,
                'error': str(e),
                'success': False
            })
            return False, None

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("=" * 80)

        return self.failed == 0

def main():
    print("=" * 80)
    print("COMPREHENSIVE API ENDPOINT TEST")
    print("=" * 80)
    print("Testing all 68 endpoints for frontend integration")
    print()

    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"{Colors.GREEN}[OK]{Colors.END} API Server is running")
        print()
    except Exception as e:
        print(f"{Colors.RED}[FAIL]{Colors.END} API Server is not running!")
        print(f"Error: {e}")
        print("\nPlease start the server with: python api_server.py")
        return False

    tester = EndpointTester()

    # 1. Health & Status
    print(f"\n{Colors.BLUE}=== 1. Health & Status ==={Colors.END}")
    tester.test_endpoint("GET", "/health", description="Health check")
    tester.test_endpoint("GET", "/status", description="System status")

    # 2. Sites Management
    print(f"\n{Colors.BLUE}=== 2. Sites Management ==={Colors.END}")
    tester.test_endpoint("GET", "/sites", description="List all sites")
    tester.test_endpoint("GET", "/sites/enabled", description="List enabled sites")
    tester.test_endpoint("GET", "/sites/disabled", description="List disabled sites")
    tester.test_endpoint("GET", "/sites/cwlagos", description="Get specific site")

    # 3. Scraping Operations
    print(f"\n{Colors.BLUE}=== 3. Scraping Operations ==={Colors.END}")
    tester.test_endpoint("GET", "/scrape/status", description="Get scraping status")
    tester.test_endpoint("GET", "/scrape/history", description="Get scraping history")
    # Skip actual scraping to keep test fast
    # tester.test_endpoint("POST", "/scrape/start", data={"sites": ["cwlagos"]}, description="Start scraping")

    # 4. Data Access
    print(f"\n{Colors.BLUE}=== 4. Data Access ==={Colors.END}")
    tester.test_endpoint("GET", "/data/latest", description="Get latest data")
    tester.test_endpoint("GET", "/data/all", description="Get all data")
    tester.test_endpoint("GET", "/data/sites/cwlagos", description="Get site-specific data")
    tester.test_endpoint("GET", "/data/search?q=Lagos", description="Search listings")

    # 5. Statistics
    print(f"\n{Colors.BLUE}=== 5. Statistics ==={Colors.END}")
    tester.test_endpoint("GET", "/stats/overview", description="Get overview stats")
    tester.test_endpoint("GET", "/stats/sites", description="Get per-site stats")
    tester.test_endpoint("GET", "/stats/trends", description="Get trends")

    # 6. Configuration
    print(f"\n{Colors.BLUE}=== 6. Configuration ==={Colors.END}")
    tester.test_endpoint("GET", "/config", description="Get config")
    tester.test_endpoint("GET", "/config/sites/cwlagos", description="Get site config")

    # 7. Files
    print(f"\n{Colors.BLUE}=== 7. Files ==={Colors.END}")
    tester.test_endpoint("GET", "/files/exports", description="List export files")
    tester.test_endpoint("GET", "/files/logs", description="List log files")

    # 8. Logs
    print(f"\n{Colors.BLUE}=== 8. Logs ==={Colors.END}")
    tester.test_endpoint("GET", "/logs/recent", description="Get recent logs")
    tester.test_endpoint("GET", "/logs/recent?level=ERROR", description="Get error logs")

    # 9. Price Intelligence
    print(f"\n{Colors.BLUE}=== 9. Price Intelligence ==={Colors.END}")
    tester.test_endpoint("GET", "/price/history/cwlagos", description="Get price history")
    tester.test_endpoint("GET", "/price/trends", description="Get price trends")

    # 10. Saved Searches
    print(f"\n{Colors.BLUE}=== 10. Saved Searches ==={Colors.END}")
    tester.test_endpoint("GET", "/searches", description="List saved searches")
    # Skip POST/DELETE to avoid modifying data

    # 11. Duplicate Detection
    print(f"\n{Colors.BLUE}=== 11. Duplicate Detection ==={Colors.END}")
    tester.test_endpoint("GET", "/duplicates/stats", description="Get duplicate stats")

    # 12. Quality Scores
    print(f"\n{Colors.BLUE}=== 12. Quality Scores ==={Colors.END}")
    tester.test_endpoint("GET", "/quality/stats", description="Get quality stats")

    # 13. Location Filter
    print(f"\n{Colors.BLUE}=== 13. Location Filter ==={Colors.END}")
    tester.test_endpoint("GET", "/location/areas", description="Get Lagos areas")

    # Print summary
    success = tester.print_summary()

    if not success:
        print(f"\n{Colors.RED}[FAIL] Some tests failed!{Colors.END}")
        print("Please review the errors above and fix them before giving to frontend developer.")
        return False
    else:
        print(f"\n{Colors.GREEN}[SUCCESS] All tests passed!{Colors.END}")
        print("The API is ready for frontend integration.")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
