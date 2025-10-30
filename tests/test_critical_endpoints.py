"""
Test Critical Endpoints - Most Common Use Cases
Tests the endpoints your frontend developer will actually use
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)

        success = response.status_code == expected_status

        if success:
            print(f"[OK] {name}")
            return True, response.json() if response.content else None
        else:
            print(f"[FAIL] {name} - Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"[ERROR] {name} - {str(e)}")
        return False, None

print("="*80)
print("TESTING CRITICAL ENDPOINTS")
print("="*80)
print()

# Test 1: Health Check
print("1. Health Check")
success, data = test_endpoint(
    "GET /api/health",
    "GET",
    f"{API_BASE}/health"
)
if success:
    print(f"   Status: {data.get('status')}")
print()

# Test 2: List Sites
print("2. List Sites")
success, data = test_endpoint(
    "GET /api/sites",
    "GET",
    f"{API_BASE}/sites"
)
if success:
    print(f"   Total sites: {data.get('total')}")
    print(f"   Enabled: {data.get('enabled')}, Disabled: {data.get('disabled')}")
print()

# Test 3: Get Specific Site
print("3. Get Specific Site")
success, data = test_endpoint(
    "GET /api/sites/cwlagos",
    "GET",
    f"{API_BASE}/sites/cwlagos"
)
if success:
    print(f"   Site: {data.get('name')}")
    print(f"   Enabled: {data.get('enabled')}")
print()

# Test 4: Get All Properties
print("4. Get All Properties")
success, data = test_endpoint(
    "GET /api/data/sites?limit=10",
    "GET",
    f"{API_BASE}/data/sites?limit=10"
)
if success:
    print(f"   Total properties: {data.get('total')}")
    print(f"   Properties returned: {len(data.get('properties', []))}")
    if data.get('properties'):
        prop = data['properties'][0]
        print(f"   Sample property: {prop.get('title', 'N/A')[:50]}...")
print()

# Test 5: Get Site-Specific Properties
print("5. Get Site-Specific Properties")
success, data = test_endpoint(
    "GET /api/data/sites/cwlagos?limit=5",
    "GET",
    f"{API_BASE}/data/sites/cwlagos?limit=5"
)
if success:
    print(f"   Properties from cwlagos: {len(data.get('properties', []))}")
print()

# Test 6: Search Properties
print("6. Search Properties")
success, data = test_endpoint(
    "GET /api/data/search?query=Lagos",
    "GET",
    f"{API_BASE}/data/search?query=Lagos"
)
if success:
    print(f"   Search results: {data.get('total', 0)}")
print()

# Test 7: Overview Statistics
print("7. Overview Statistics")
success, data = test_endpoint(
    "GET /api/stats/overview",
    "GET",
    f"{API_BASE}/stats/overview"
)
if success:
    overview = data.get('overview', {})
    print(f"   Total sites: {overview.get('total_sites')}")
    print(f"   Total listings: {overview.get('total_listings')}")
    print(f"   Active sites: {overview.get('active_sites')}")
print()

# Test 8: Site Statistics
print("8. Site Statistics")
success, data = test_endpoint(
    "GET /api/stats/sites",
    "GET",
    f"{API_BASE}/stats/sites"
)
if success:
    print(f"   Sites with stats: {len(data) if isinstance(data, list) else 0}")
print()

# Test 9: Scraping Status
print("9. Scraping Status")
success, data = test_endpoint(
    "GET /api/scrape/status",
    "GET",
    f"{API_BASE}/scrape/status"
)
if success:
    print(f"   Status: {data.get('status')}")
print()

# Test 10: Scraping History
print("10. Scraping History")
success, data = test_endpoint(
    "GET /api/scrape/history",
    "GET",
    f"{API_BASE}/scrape/history"
)
if success:
    scrapes = data.get('scrapes', [])
    print(f"   History entries: {len(scrapes)}")
    if scrapes:
        print(f"   Latest scrape: {scrapes[0].get('start_time', 'N/A')}")
print()

# Test 11: Logs
print("11. Get Logs")
success, data = test_endpoint(
    "GET /api/logs?limit=10",
    "GET",
    f"{API_BASE}/logs?limit=10"
)
if success:
    logs = data.get('logs', [])
    print(f"   Log entries: {len(logs)}")
print()

# Test 12: Saved Searches
print("12. Saved Searches")
success, data = test_endpoint(
    "GET /api/searches",
    "GET",
    f"{API_BASE}/searches"
)
if success:
    searches = data if isinstance(data, list) else []
    print(f"   Saved searches: {len(searches)}")
print()

# Test 13: Market Trends
print("13. Market Trends")
success, data = test_endpoint(
    "GET /api/market-trends",
    "GET",
    f"{API_BASE}/market-trends"
)
if success:
    overall = data.get('overall', {})
    print(f"   Average price: ₦{overall.get('avg_price', 0):,.0f}")
    print(f"   Total listings: {overall.get('total_listings', 0)}")
print()

# Test 14: Validate URL
print("14. URL Validation")
success, data = test_endpoint(
    "POST /api/validate/url",
    "POST",
    f"{API_BASE}/validate/url",
    {"url": "https://example.com"}
)
if success:
    print(f"   Valid: {data.get('valid')}")
print()

# Test 15: Query Properties (Advanced)
print("15. Query Properties")
success, data = test_endpoint(
    "POST /api/query",
    "POST",
    f"{API_BASE}/query",
    {
        "filters": {"property_type": "apartment"},
        "pagination": {"limit": 5}
    }
)
if success:
    print(f"   Query results: {data.get('total', 0)}")
print()

print("="*80)
print("CRITICAL ENDPOINTS TEST COMPLETE")
print("="*80)
print()
print("All critical endpoints that your frontend developer will use have been tested!")
print("If you see [OK] for all tests, everything is working correctly.")
