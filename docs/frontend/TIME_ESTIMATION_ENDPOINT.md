# Time Estimation Endpoint Documentation

**Version**: 1.0
**Last Updated**: 2025-11-18
**Endpoint**: `POST /api/github/estimate-scrape-time`

---

## Overview

The Time Estimation Endpoint provides accurate predictions of scrape duration based on the number of enabled sites and pages per site. It includes built-in timeout warnings to prevent GitHub Actions workflow failures.

**Key Features:**
- Accurate time estimation based on workflow constants
- Automatic timeout risk assessment (safe/warning/danger)
- Recommendations to avoid timeouts
- Session breakdown and parallel execution calculations
- Matches actual GitHub Actions workflow configuration

---

## Endpoint Details

### Request

```http
POST /api/github/estimate-scrape-time
Content-Type: application/json
```

### Request Body

```json
{
  "max_pages": 15,          // Pages per site (default: 15)
  "geocode": 1,             // Enable geocoding: 1 or 0 (default: 1)
  "sites": ["npc", "..."]   // Optional: specific sites (empty = all enabled)
}
```

### Response

```json
{
  "estimated_duration_minutes": 180.5,
  "estimated_duration_hours": 3.01,
  "estimated_duration_text": "~3h 0m",
  "site_count": 51,
  "batch_type": "multi-session",
  "sessions": 17,
  "sites_per_session": 3,
  "max_parallel_sessions": 5,
  "session_time_minutes": 47.2,
  "session_timeout_limit": 90,
  "total_timeout_limit": 350,
  "timeout_risk": "safe",
  "timeout_message": null,
  "breakdown": {
    "scraping_per_site": 12.5,
    "geocoding_per_site": 3.0,
    "upload_per_site": 0.75,
    "watcher_overhead": 2.0,
    "buffer_multiplier": 1.3
  },
  "recommendations": [
    "✅ Estimated time is within safe limits."
  ],
  "configuration": {
    "max_pages": 15,
    "geocode_enabled": true,
    "estimated_properties_per_site": 225
  },
  "note": "Estimates based on workflow time constants. Actual time may vary by ±20%."
}
```

---

## Response Fields

### Timing Information

| Field | Type | Description |
|-------|------|-------------|
| `estimated_duration_minutes` | float | Total estimated time in minutes |
| `estimated_duration_hours` | float | Total estimated time in hours |
| `estimated_duration_text` | string | Human-readable time format (e.g., "~3h 0m") |
| `session_time_minutes` | float | Time for each session |

### Batch Configuration

| Field | Type | Description |
|-------|------|-------------|
| `site_count` | int | Number of sites to scrape |
| `batch_type` | string | "single-session" or "multi-session" |
| `sessions` | int | Total number of sessions required |
| `sites_per_session` | int | Sites per session (currently: 3) |
| `max_parallel_sessions` | int | Max parallel sessions (currently: 5) |

### Timeout Risk Assessment

| Field | Type | Description |
|-------|------|-------------|
| `timeout_risk` | string | "safe", "warning", or "danger" |
| `timeout_message` | string\|null | Warning message if at risk |
| `session_timeout_limit` | int | Session timeout limit (90 minutes) |
| `total_timeout_limit` | int | Total workflow limit (350 minutes / ~6 hours) |

### Recommendations

| Field | Type | Description |
|-------|------|-------------|
| `recommendations` | array | Array of actionable recommendations |

**Risk Levels:**

- **safe**: Estimated time is well within limits ✅
- **warning**: Time >4 hours or session >90 minutes ⚠️
- **danger**: Time exceeds GitHub Actions 6-hour limit ⛔

### Time Breakdown

| Field | Description |
|-------|-------------|
| `scraping_per_site` | Average scraping time per site (minutes) |
| `geocoding_per_site` | Geocoding time per site if enabled |
| `upload_per_site` | Firestore upload time per site |
| `watcher_overhead` | Data processing overhead |
| `buffer_multiplier` | Safety buffer multiplier (1.3 = 30%) |

---

## Timeout Warnings

### Safe ✅
```json
{
  "timeout_risk": "safe",
  "timeout_message": null,
  "recommendations": ["✅ Estimated time is within safe limits."]
}
```

### Warning ⚠️
```json
{
  "timeout_risk": "warning",
  "timeout_message": "⚠️ WARNING: Estimated time (260 min / 4.3h) is high. Risk of timeout.",
  "recommendations": ["Consider reducing pages or running in smaller batches."]
}
```

### Danger ⛔
```json
{
  "timeout_risk": "danger",
  "timeout_message": "⛔ CRITICAL: Estimated time (400 min) exceeds GitHub Actions limit (350 min). Scrape WILL timeout!",
  "recommendations": ["Reduce sites or pages. Try max 45 sites or 10 pages."]
}
```

---

## Usage Examples

### Example 1: Check Default Configuration (All Sites, 15 Pages)

```javascript
const response = await fetch('http://localhost:5000/api/github/estimate-scrape-time', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    max_pages: 15,
    geocode: 1
  })
});

const data = await response.json();
console.log(data.estimated_duration_text); // "~3h 0m"
console.log(data.timeout_risk); // "safe"
```

### Example 2: Check Specific Sites

```javascript
const response = await fetch('http://localhost:5000/api/github/estimate-scrape-time', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    max_pages: 2,
    geocode: 0,
    sites: ["npc", "propertypro"]
  })
});

const data = await response.json();
console.log(data.estimated_duration_minutes); // ~5.6
console.log(data.batch_type); // "single-session"
```

### Example 3: React Hook

```typescript
import { useState } from 'react';

interface TimeEstimate {
  estimated_duration_text: string;
  timeout_risk: 'safe' | 'warning' | 'danger';
  timeout_message: string | null;
  recommendations: string[];
  site_count: number;
  sessions: number;
}

export function useTimeEstimation() {
  const [estimate, setEstimate] = useState<TimeEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const estimateTime = async (pageCap: number, geocode: boolean, sites?: string[]) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/github/estimate-scrape-time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_pages: pageCap,
          geocode: geocode ? 1 : 0,
          sites: sites || []
        })
      });

      if (!response.ok) throw new Error('Failed to estimate time');

      const data = await response.json();
      setEstimate(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return { estimate, loading, error, estimateTime };
}
```

### Example 4: Display Warning UI

```tsx
function ScrapeTimeWarning({ estimate }: { estimate: TimeEstimate }) {
  const getRiskColor = () => {
    switch (estimate.timeout_risk) {
      case 'safe': return 'green';
      case 'warning': return 'yellow';
      case 'danger': return 'red';
    }
  };

  return (
    <div style={{ padding: '1rem', backgroundColor: getRiskColor(), borderRadius: '4px' }}>
      <h3>Estimated Time: {estimate.estimated_duration_text}</h3>
      {estimate.timeout_message && <p>{estimate.timeout_message}</p>}
      <ul>
        {estimate.recommendations.map((rec, i) => (
          <li key={i}>{rec}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Calculation Logic

### Time Estimation Formula

Based on GitHub Actions workflow constants (`scrape-production.yml`):

```
TIME_PER_PAGE = 8 seconds
TIME_PER_SITE_OVERHEAD = 45 seconds
GEOCODE_TIME_PER_PROPERTY = 1.2 seconds
FIRESTORE_UPLOAD_TIME = 0.3 seconds
WATCHER_OVERHEAD = 120 seconds
BUFFER_MULTIPLIER = 1.3 (30% safety margin)
```

### Per-Site Time

```
Properties = max_pages × 15 (estimated properties per page)
Scrape Time = (max_pages × 8) + 45 seconds
Geocode Time = Properties × 1.2 seconds (if enabled)
Upload Time = Properties × 0.3 seconds
Total Per Site = Scrape + Geocode + Upload
```

### Session Time

```
Sites in Session = min(site_count, 3)
Session Time = (Total Per Site × Sites) + 120s + 30% buffer
```

### Total Workflow Time

```
Total Sessions = ceil(site_count / 3)
Parallel Batches = ceil(Total Sessions / 5)
Total Time = Parallel Batches × Session Time
```

---

## Best Practices

### 1. Always Check Before Scraping

```javascript
// Before triggering scrape
const estimate = await estimateTime(pageCap, geocode);

if (estimate.timeout_risk === 'danger') {
  alert('Scrape will timeout! Reduce pages or sites.');
  return;
}

// Proceed with scrape...
```

### 2. Show Estimates in UI

Display estimated time and warnings before user confirms scrape action.

### 3. Recommended Limits

| Configuration | Max Sites | Max Pages | Estimated Time |
|---------------|-----------|-----------|----------------|
| Safe | 51 | 15 | ~3 hours |
| Fast | 51 | 10 | ~2 hours |
| Quick Test | 5 | 2 | ~10 minutes |
| Single Site | 1 | 30 | ~15 minutes |

### 4. Handle Warnings Gracefully

```typescript
if (estimate.timeout_risk === 'warning') {
  const proceed = confirm(
    `${estimate.timeout_message}\n\n` +
    `Do you want to continue anyway?`
  );

  if (!proceed) return;
}
```

---

## Error Handling

### Common Errors

```javascript
try {
  const response = await fetch('/api/github/estimate-scrape-time', {
    method: 'POST',
    body: JSON.stringify({ max_pages: 15 })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return data;
} catch (error) {
  console.error('Time estimation failed:', error);
  // Fallback to default estimate or show error
}
```

---

## Testing

### Test Scenarios

```bash
# Safe: 2 sites, 2 pages
curl -X POST http://localhost:5000/api/github/estimate-scrape-time \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 2, "geocode": 0}'

# Warning: All sites, 30 pages
curl -X POST http://localhost:5000/api/github/estimate-scrape-time \
  -H "Content-Type": application/json" \
  -d '{"max_pages": 30, "geocode": 1}'

# Danger: All sites, 50 pages
curl -X POST http://localhost:5000/api/github/estimate-scrape-time \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 50, "geocode": 1}'
```

---

## Changelog

### Version 1.0 (2025-11-18)
- Initial release
- Accurate estimation matching workflow constants
- Timeout risk assessment (safe/warning/danger)
- Session and parallel execution calculations
- Actionable recommendations
- Conservative strategy support (3 sites/session, 5 parallel)

---

## Related Documentation

- [GitHub Actions Workflow](../../.github/workflows/scrape-production.yml)
- [Frontend Integration Guide](./FRONTEND_INTEGRATION_GUIDE.md)
- [API Endpoints Reference](./API_ENDPOINTS_ACTUAL.md)
- [Workflow Timeout Fix Summary](../../INTELLIGENT_BATCHING_SUMMARY.md)
