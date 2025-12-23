# Testing Guide

Complete guide for testing the Nigerian Real Estate Scraper platform.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Suites](#test-suites)
3. [Running Tests](#running-tests)
4. [API Testing](#api-testing)
5. [Security Testing](#security-testing)
6. [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all existing tests
cd tests
python run_all_improvement_tests.py
```

### Run Specific Test Suite

```bash
# API tests
python tests/test_api_comprehensive.py

# Security tests
python tests/test_security_comprehensive.py

# Firestore tests
python tests/test_firestore_integration.py
```

---

## Test Suites

### 1. API Endpoint Tests (`test_api_comprehensive.py`)
**Coverage:** All 68 API endpoints
**Purpose:** Verify all endpoints respond correctly

**Tests Include:**
- ✅ Core operations (health, scraping)
- ✅ Site management (CRUD operations)
- ✅ Data access and search
- ✅ Price tracking and market trends
- ✅ Authentication and authorization
- ✅ Error handling
- ✅ Security (SQL injection, XSS, path traversal)

### 2. Security Tests (`test_security_comprehensive.py`)
**Coverage:** 23 security checks
**Purpose:** Identify vulnerabilities and security issues

**Tests Include:**
- ✅ Credentials management
- ✅ Input validation
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ Path traversal protection
- ✅ CORS configuration
- ✅ Dependency security
- ✅ Error handling
- ✅ Secure defaults

### 3. Firestore Integration Tests (`test_firestore_integration.py`)
**Coverage:** 10 Firestore operations
**Purpose:** Verify cloud database integration

**Tests Include:**
- ✅ Initialization
- ✅ Data upload
- ✅ Querying
- ✅ Archiving
- ✅ Security rules
- ✅ Batch operations
- ✅ Duplicate prevention

### 4. Feature-Specific Tests

#### Duplicate Detection (`test_duplicate_detector.py`)
- Fuzzy matching across sites
- Title similarity
- Address matching
- Price comparison

#### Quality Scoring (`test_quality_scorer.py`)
- Data completeness
- Field validation
- Score calculation
- Quality thresholds

#### Natural Language Search (`test_natural_language_search.py`)
- Query parsing
- Intent recognition
- Result ranking
- Suggestions

#### Price History (`test_price_history.py`)
- Price tracking
- Change detection
- Trend analysis
- Drop alerts

#### Saved Searches (`test_saved_searches.py`)
- CRUD operations
- Match notification
- Search execution
- Statistics

#### Scheduler (`test_scheduler_logic.py`)
- Job creation
- Cron parsing
- Execution timing
- Cancellation

#### Health Monitor (`test_health_monitor.py`)
- Site status tracking
- Performance metrics
- Alert generation
- Top performers

#### Rate Limiter (`test_rate_limiter.py`)
- Request throttling
- Per-site limits
- Backoff strategy
- Rate tracking

#### Query Engine (`test_query_engine.py`)
- Complex filtering
- AND/OR logic
- Range queries
- Sorting and pagination

#### URL Validator (`test_url_validator.py`)
- Format validation
- Domain checking
- Protocol validation
- Accessibility check

#### Incremental Scraping (`test_incremental_scraping.py`)
- New listing detection
- Cache management
- Performance optimization
- State persistence

#### Parallel Scraping (`test_parallel_scraping.py`)
- Concurrent execution
- Resource management
- Error isolation
- Results aggregation

#### Watcher Integration (`test_watcher_integration.py`)
- File monitoring
- Processing triggers
- Master workbook creation
- Metadata tracking

---

## Running Tests

### Manual Testing

#### Run Individual Test File
```bash
python tests/test_duplicate_detector.py
```

#### Run with Verbose Output
```bash
python -m unittest tests.test_quality_scorer -v
```

#### Run Specific Test Method
```bash
python -m unittest tests.test_api_comprehensive.TestAPIComprehensive.test_001_health_check
```

### Automated Testing

#### Run All Improvement Tests
```bash
cd scripts
python run_all_improvement_tests.py
```

#### Run Comprehensive Test Suite
```bash
cd tests
python run_all_comprehensive_tests.py
```

---

## API Testing

### Using cURL

#### Test Health Endpoint
```bash
curl http://localhost:5000/api/health
```

#### Start Scraping
```bash
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"sites": ["npc"], "max_pages": 5}'
```

#### Natural Language Search
```bash
curl -X POST http://localhost:5000/api/search/natural \
  -H "Content-Type: application/json" \
  -d '{"query": "3 bedroom flat in Lekki under 30 million"}'
```

#### Query Properties
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "bedrooms": {"gte": 3},
      "price": {"lte": 30000000},
      "location": {"contains": "Lekki"}
    },
    "limit": 10
  }'
```

### Using Python Requests

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Start scraping
response = requests.post('http://localhost:5000/api/scrape/start', json={
    'sites': ['npc', 'propertypro'],
    'max_pages': 10
})
print(response.json())

# Get price drops
response = requests.get('http://localhost:5000/api/price-drops?min_drop_pct=10')
print(response.json())
```

### Using Postman

1. **Import Collection:**
   - See `docs/POSTMAN_GUIDE.md` for collection file
   - Import into Postman

2. **Set Environment Variables:**
   ```
   base_url: http://localhost:5000
   api_key: your_api_key (if auth enabled)
   ```

3. **Run Collection:**
   - Click "Run" in Postman
   - Select all requests
   - Click "Run Tests"

---

## Security Testing

### Automated Security Scan

```bash
# Run security test suite
python tests/test_security_comprehensive.py
```

### Manual Security Testing

#### Test SQL Injection
```bash
curl "http://localhost:5000/api/data/search?q='; DROP TABLE properties; --"
```
**Expected:** Should not crash, should sanitize input

#### Test XSS
```bash
curl -X POST http://localhost:5000/api/search/natural \
  -H "Content-Type: application/json" \
  -d '{"query": "<script>alert(1)</script>"}'
```
**Expected:** Script should be escaped

#### Test Path Traversal
```bash
curl "http://localhost:5000/api/export/download/../../../etc/passwd"
```
**Expected:** Should return 400 or 404, not file contents

#### Test Rate Limiting
```bash
# Make 100 rapid requests
for i in {1..100}; do
  curl http://localhost:5000/api/health
done
```
**Expected:** Should start returning 429 (Too Many Requests)

### Security Checklist

Before production deployment:

- [ ] No hardcoded credentials
- [ ] Environment variables for secrets
- [ ] API authentication enabled
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] Path traversal protection
- [ ] Error messages don't leak info
- [ ] Debug mode disabled
- [ ] Security headers added
- [ ] Dependencies updated
- [ ] Firestore security rules set

---

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to main branch
- Pull requests
- Manual trigger

#### Workflow File
```yaml
# .github/workflows/tests.yml
name: Run Tests

on:
  push:
    branches: [main]
    paths:
      - 'core/**'
      - 'tests/**'
      - 'api_server.py'
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          cd scripts
          python run_all_improvement_tests.py
```

#### View Test Results
1. Go to GitHub repository
2. Click "Actions" tab
3. Click on latest workflow run
4. View test results and logs

---

## Test Coverage

### Current Coverage

| Component | Test Coverage | Status |
|-----------|--------------|--------|
| API Endpoints | 68/68 (100%) | ✅ |
| Core Scraper | Full | ✅ |
| Data Quality | Full | ✅ |
| Search | Full | ✅ |
| Price Tracking | Full | ✅ |
| Automation | Full | ✅ |
| Security | 23 checks | ✅ |
| Firestore | 10 tests | ✅ |

### Adding New Tests

#### Template for New Test
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

class TestNewFeature(unittest.TestCase):
    """Test new feature functionality"""

    def setUp(self):
        """Set up before each test"""
        pass

    def test_001_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        self.assertEqual(result, expected_output)

    def tearDown(self):
        """Clean up after each test"""
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

---

## Troubleshooting

### Common Issues

#### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'core'`
**Solution:**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/Dynamic realtors_practice"
```

#### API Server Not Running
**Problem:** `Connection refused` when testing endpoints
**Solution:**
```bash
# Start API server first
python api_server.py

# Then run tests in another terminal
python tests/test_api_comprehensive.py
```

#### Firestore Credentials Missing
**Problem:** `DefaultCredentialsError: Could not load credentials`
**Solution:**
```bash
# Set environment variable
export FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json

# Or use the full path
export FIREBASE_SERVICE_ACCOUNT=/full/path/to/credentials.json
```

#### Permission Errors
**Problem:** `PermissionError: [Errno 13] Permission denied`
**Solution:**
```bash
# Windows
icacls logs /grant Users:F

# Linux/Mac
chmod -R 755 logs exports
```

---

## Best Practices

### Writing Tests

1. **Descriptive Names:** Use clear, descriptive test names
2. **Single Purpose:** Each test should test one thing
3. **Arrange-Act-Assert:** Follow AAA pattern
4. **Independent:** Tests shouldn't depend on each other
5. **Cleanup:** Always clean up after tests

### Running Tests

1. **Run Before Commit:** Always run tests before committing
2. **Check Coverage:** Aim for high code coverage
3. **Fix Failures:** Don't ignore failing tests
4. **Update Tests:** Update tests when code changes

### Security Testing

1. **Regular Scans:** Run security tests weekly
2. **Update Dependencies:** Keep dependencies current
3. **Review Logs:** Check security logs regularly
4. **Penetration Testing:** Conduct periodic pen tests

---

## Resources

### Documentation
- [API Documentation](FRONTEND_INTEGRATION_GUIDE.md)
- [Security Analysis](SECURITY_ANALYSIS.md)
- [Architecture](ARCHITECTURE.md)

### Tools
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Postman](https://www.postman.com/)
- [curl](https://curl.se/)

### Security Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)

---

**Last Updated:** 2025-10-22
**Version:** 2.2
**Status:** ✅ Comprehensive
