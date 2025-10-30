# Actual API Endpoints - Verified Working List

This document lists **all** API endpoints that actually exist in `api_server.py` and are ready for frontend integration.

## Total: 67 Endpoints

---

## 1. Health & Monitoring (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Basic health check |
| GET | `/api/health/overall` | Overall system health |
| GET | `/api/health/sites/<site_key>` | Health check for specific site |
| GET | `/api/health/alerts` | Get health alerts |
| GET | `/api/health/top-performers` | Get top performing sites |

---

## 2. Scraping Operations (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scrape/start` | Start scraping (optionally filter by sites) |
| GET | `/api/scrape/status` | Get current scraping status |
| POST | `/api/scrape/stop` | Stop ongoing scraping |
| GET | `/api/scrape/history` | Get scraping history |

---

## 3. Sites Management (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sites` | List all sites |
| GET | `/api/sites/<site_key>` | Get specific site details |
| POST | `/api/sites` | Add new site |
| PUT | `/api/sites/<site_key>` | Update site configuration |
| DELETE | `/api/sites/<site_key>` | Delete site |
| PATCH | `/api/sites/<site_key>/toggle` | Enable/disable site |

---

## 4. Data Access (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data/sites` | Get data from all sites |
| GET | `/api/data/sites/<site_key>` | Get data from specific site |
| GET | `/api/data/master` | Get master workbook data |
| GET | `/api/data/search?query=<q>` | Search listings by query |

---

## 5. Statistics (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/overview` | Get overview statistics |
| GET | `/api/stats/sites` | Get per-site statistics |
| GET | `/api/stats/trends` | Get trend statistics |

---

## 6. Logs (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs` | Get recent logs |
| GET | `/api/logs/errors` | Get error logs only |
| GET | `/api/logs/site/<site_key>` | Get logs for specific site |

---

## 7. URL Validation (2 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/validate/url` | Validate single URL |
| POST | `/api/validate/urls` | Validate multiple URLs |

---

## 8. Location Filter (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/filter/location` | Filter listings by location |
| GET | `/api/filter/stats` | Get location filter statistics |
| GET | `/api/config/locations` | Get configured locations |
| PUT | `/api/config/locations` | Update location configuration |

---

## 9. Property Query Engine (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query` | Query properties with filters |
| POST | `/api/query/summary` | Get query result summary |

---

## 10. Rate Limiting (2 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rate-limit/status` | Get rate limit status |
| POST | `/api/rate-limit/check` | Check if action is rate limited |

---

## 11. Price Intelligence (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/price-history/<property_id>` | Get price history for property |
| GET | `/api/price-drops` | Get properties with price drops |
| GET | `/api/stale-listings` | Get stale listings |
| GET | `/api/market-trends` | Get market trends |

---

## 12. Natural Language Search (2 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search/natural` | Natural language search |
| GET | `/api/search/suggestions` | Get search suggestions |

---

## 13. Saved Searches (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/searches` | List all saved searches |
| POST | `/api/searches` | Create new saved search |
| GET | `/api/searches/<search_id>` | Get specific saved search |
| PUT | `/api/searches/<search_id>` | Update saved search |
| DELETE | `/api/searches/<search_id>` | Delete saved search |
| GET | `/api/searches/<search_id>/stats` | Get stats for saved search |

---

## 14. Duplicate Detection (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/duplicates/detect` | Detect duplicate listings |

---

## 15. Quality Scoring (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/quality/score` | Score listing quality |

---

## 16. Firestore Integration (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/firestore/query` | Query Firestore database |
| POST | `/api/firestore/query-archive` | Query Firestore archive |
| POST | `/api/firestore/export` | Export data to Firestore |

---

## 17. Export Management (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/export/generate` | Generate export file |
| GET | `/api/export/download/<filename>` | Download export file |
| GET | `/api/export/formats` | Get supported export formats |

---

## 18. GitHub Actions Integration (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/github/trigger-scrape` | Trigger GitHub Actions scrape |
| POST | `/api/github/estimate-scrape-time` | Estimate scraping time |
| POST | `/api/notifications/subscribe` | Subscribe to workflow notifications |
| GET | `/api/notifications/workflow-status/<run_id>` | Get workflow status |
| GET | `/api/github/workflow-runs` | List workflow runs |
| GET | `/api/github/artifacts` | List workflow artifacts |
| GET | `/api/github/artifact/<artifact_id>/download` | Download artifact |

---

## 19. Scheduling (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/schedule/scrape` | Schedule a scraping job |
| GET | `/api/schedule/jobs` | List scheduled jobs |
| GET | `/api/schedule/jobs/<job_id>` | Get specific job details |
| POST/DELETE | `/api/schedule/jobs/<job_id>/cancel` | Cancel scheduled job |

---

## 20. Email Notifications (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/email/configure` | Configure email settings |
| POST | `/api/email/test-connection` | Test email connection |
| GET | `/api/email/config` | Get email configuration |
| GET | `/api/email/recipients` | List email recipients |
| POST | `/api/email/recipients` | Add email recipient |
| DELETE | `/api/email/recipients/<email>` | Remove email recipient |
| POST | `/api/email/send-test` | Send test email |

---

## Summary by Category

1. Health & Monitoring: 5 endpoints
2. Scraping Operations: 4 endpoints
3. Sites Management: 6 endpoints
4. Data Access: 4 endpoints
5. Statistics: 3 endpoints
6. Logs: 3 endpoints
7. URL Validation: 2 endpoints
8. Location Filter: 3 endpoints
9. Property Query Engine: 2 endpoints
10. Rate Limiting: 2 endpoints
11. Price Intelligence: 4 endpoints
12. Natural Language Search: 2 endpoints
13. Saved Searches: 5 endpoints
14. Duplicate Detection: 1 endpoint
15. Quality Scoring: 1 endpoint
16. Firestore Integration: 3 endpoints
17. Export Management: 3 endpoints
18. GitHub Actions Integration: 7 endpoints
19. Scheduling: 4 endpoints
20. Email Notifications: 7 endpoints

**Total: 67 endpoints**

---

## Notes for Frontend Developer

- All endpoints use JSON for request/response (except file downloads)
- Authentication is optional (disabled by default in development)
- CORS is enabled for all origins in development mode
- Base URL: `http://localhost:5000/api` (development)
- All endpoints return consistent error format: `{"error": "message"}`
