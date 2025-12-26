# LLM Integration Strategic Plan
**For**: Nigerian Real Estate Aggregation System
**Purpose**: Improve schema alignment and data consistency using ApiFreeLLM
**Date**: 2025-12-25
**Status**: STRATEGIC PLAN - NO CODE YET

---

## Executive Summary

This plan proposes adding a free LLM layer (ApiFreeLLM) to enhance data quality in a production real estate aggregation system. The LLM will serve as an **intelligent normalization layer** between raw scraping and database storage, focusing on schema alignment, classification, and standardization while preserving the existing rule-based pipeline.

**Key Principle**: LLM augments (not replaces) existing logic. Rule-based cleaning handles deterministic tasks; LLM handles ambiguous classification and normalization.

---

## 1. Pipeline Position & Architecture

### 1.1 Proposed LLM Layer Position

```
┌─────────────┐
│  GitHub     │
│  Actions    │
│  Trigger    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ SCRAPER (Playwright + Parsers)             │
│ - Extracts 85+ fields                       │
│ - Site-specific selectors                   │
│ - Raw, unstructured data                    │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ RULE-BASED CLEANER (Existing)              │
│ - Deduplication (hash-based)                │
│ - Price parsing (₦, NGN, million, billion)  │
│ - Location filtering (Lagos only)           │
│ - Phone number validation                   │
│ - Data type coercion                        │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ *** LLM NORMALIZATION LAYER (NEW) ***      │  <-- INSERT HERE
│ - Schema alignment                          │
│ - Classification (property_type, furnishing)│
│ - Standardization (location names)          │
│ - Validation (cross-field consistency)      │
│ - Enrichment (inferred fields)              │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ FIRESTORE UPLOAD                            │
│ - Enterprise schema (9 categories)          │
│ - Indexed & queryable                       │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ FRONTEND API (91 endpoints)                │
│ - Next.js consumption                       │
└─────────────────────────────────────────────┘
```

### 1.2 Why This Position?

**After rule-based cleaning, before Firestore upload**

**Reasons**:
1. **Clean Input**: LLM receives deduped, validated data (not raw HTML)
2. **Focused Task**: LLM handles ambiguous cases only (classification, normalization)
3. **Fallback Safety**: If LLM fails, rule-based data still available
4. **Performance**: LLM processes fewer records (only Lagos properties after filtering)
5. **Cost Control**: Rate limiting happens on pre-validated data
6. **Testing**: Can A/B test LLM vs non-LLM in parallel

**Not Before Scraping** ❌
- Scraping is deterministic (CSS selectors)
- LLM can't improve HTML parsing
- Would waste API calls

**Not After Database** ❌
- Database schema already applied
- Can't fix schema mismatches retroactively
- Would require duplicate storage

---

## 2. Responsibilities: LLM vs Rule-Based Logic

### 2.1 RULE-BASED LOGIC (Existing - Keep)

**What it does well** (deterministic, fast, reliable):

| Task | Why Rule-Based? |
|------|-----------------|
| **Price parsing** | Regex patterns are 100% accurate for ₦ symbols |
| **Deduplication** | Hash-based (URL + title) is deterministic |
| **Phone validation** | Regex for Nigerian numbers (0803..., +234...) |
| **Location filtering** | Exact match against Lagos LGA list |
| **Data type coercion** | String → Number conversion is deterministic |
| **Empty field rejection** | Boolean check (is None or "") |
| **Geocoding** | Google Maps API (not LLM task) |

**Keep these rule-based** - LLM offers no advantage and adds latency/cost.

---

### 2.2 LLM LAYER (New - Strategic Tasks)

**What LLM does better** (ambiguous, classification, normalization):

| Task | Why LLM? | Example |
|------|---------|---------|
| **Property Type Classification** | Ambiguous labels vary across sites | "3BR Flat" → apartment, "Duplex House" → house, "Terrace" → house |
| **Furnishing Standardization** | Inconsistent terminology | "Fully Fitted" → furnished, "Empty" → unfurnished, "Part Furnished" → semi-furnished |
| **Location Normalization** | Variants of same area | "Lekki Phase 1" = "Lekki Ph 1" = "Phase 1 Lekki" → "Lekki Phase 1" |
| **Amenity Extraction** | Unstructured descriptions | "Swimming pool, gym, 24hr power" → [pool, gym, power] |
| **Property Condition Inference** | Implicit from description | "Newly built" → new, "Renovated" → renovated, "As is" → needs_renovation |
| **Cross-Field Validation** | Logical consistency | If bedrooms=0 AND property_type=apartment → flag as suspicious |
| **Missing Field Inference** | Context-based guessing | Title="Office Space Ikeja" + type=missing → property_type="commercial" |

---

### 2.3 Hybrid Approach: Rule-First, LLM-Second

**Decision Tree**:

```
For each field:
1. Try rule-based extraction
2. If confident result → use it
3. If ambiguous/missing → pass to LLM
4. If LLM fails → use rule-based fallback
5. If both fail → mark as null + log
```

**Example - Property Type**:
1. Rule: Check if title contains exact match ("apartment", "house", "land")
2. If match → use it (fast, free)
3. If no match → LLM classify full description
4. If LLM returns invalid type → default to "property" + log
5. Always validate LLM output against allowed enum

---

## 3. ApiFreeLLM Limitations & Design Implications

### 3.1 Known Limitations

| Limitation | Value | Impact |
|------------|-------|--------|
| **Rate Limit** | ~30-60 requests/min | Must batch + throttle |
| **Accuracy** | 70-85% (vs GPT-4: 90-95%) | Requires validation |
| **Response Time** | 3-10 seconds | Adds latency to pipeline |
| **Free Tier** | May have daily limits | Need monitoring |
| **Model Quality** | Varies (GPT-3.5 level) | Not reliable for critical data |
| **No SLA** | Can go down anytime | Must have fallbacks |

### 3.2 Design Adaptations

**To Handle Rate Limits**:
- **Batch Processing**: Process properties in groups of 20-30
- **Throttling**: 1 request every 2 seconds (30/min = safe)
- **Prioritization**: Process high-value properties first (sale > rent > shortlet)
- **Caching**: Cache LLM responses by input hash (avoid repeat calls)
- **Async Pipeline**: Don't block scraping on LLM (process in background)

**To Handle Low Accuracy**:
- **Output Validation**: Strict enum checking (reject invalid types)
- **Confidence Scoring**: LLM returns confidence % → only use if >70%
- **Fallback Chain**: LLM → Rule-based → Default → Null
- **Human Review Queue**: Properties with confidence <70% flagged for review
- **A/B Testing**: Compare LLM vs non-LLM data quality metrics

**To Handle Latency**:
- **Async Workers**: Separate queue for LLM processing (don't block main pipeline)
- **Progressive Enhancement**: Upload to Firestore immediately, LLM enriches later
- **Timeout**: 15-second timeout per LLM call (fail fast)
- **Parallel Requests**: Use threadpool (5 concurrent) where rate limits allow

**To Handle Unreliability**:
- **Circuit Breaker**: If 5 consecutive LLM failures → disable for 10 minutes
- **Fallback Mode**: System works 100% without LLM (LLM is enhancement, not dependency)
- **Health Monitoring**: Track LLM success rate, latency, daily quota
- **Graceful Degradation**: If LLM unavailable, log + continue with rule-based only

---

## 4. Data Flow After LLM Integration

### 4.1 Enhanced Pipeline Flow

```
SESSION 1 (Scraping - Unchanged)
├─ Scrape 30 properties from Site A
├─ Save raw data to exports/sites/site_a.csv
└─ Upload to Firestore (basic schema)

SESSION 2 (LLM Enrichment - NEW)
├─ Query Firestore for properties with missing/ambiguous fields
│  WHERE property_type = null OR furnishing = null
│  LIMIT 30  (rate limit friendly)
│
├─ For each property:
│  ├─ Build LLM prompt with context
│  ├─ Call ApiFreeLLM (async, throttled)
│  ├─ Validate response
│  ├─ Update Firestore if valid
│  └─ Log result (success/fail/skipped)
│
└─ Repeat until all properties enriched

FRONTEND (Read-Only - Unchanged)
├─ Queries enhanced Firestore data
└─ Displays properties with better classification
```

### 4.2 Detailed LLM Processing Flow

```python
# Pseudocode (NOT implementation)

for batch in get_properties_needing_enrichment(limit=30):
    for property in batch:
        # 1. Build prompt from property data
        prompt = f"""
        Classify this Nigerian property:
        Title: {property.title}
        Description: {property.description}
        Price: ₦{property.price:,}

        Return JSON:
        {{
          "property_type": "apartment|house|land|commercial|maisonette|mansion",
          "furnishing": "furnished|semi-furnished|unfurnished",
          "condition": "new|renovated|needs_renovation|unknown",
          "amenities": ["pool", "gym", "power", ...],
          "confidence": 0-100
        }}
        """

        # 2. Call LLM with retry + timeout
        try:
            response = call_llm(prompt, timeout=15, retries=2)
            data = json.loads(response)

            # 3. Validate response
            if not validate_llm_output(data):
                log_invalid_response(property.id, response)
                continue

            # 4. Apply confidence threshold
            if data['confidence'] < 70:
                log_low_confidence(property.id, data)
                continue

            # 5. Update Firestore
            update_property(property.id, {
                'property_details.property_type': data['property_type'],
                'property_details.furnishing': data['furnishing'],
                'property_details.condition': data['condition'],
                'amenities.features': data['amenities'],
                'metadata.llm_enriched': True,
                'metadata.llm_confidence': data['confidence']
            })

        except RateLimitError:
            sleep(60)  # Back off
        except TimeoutError:
            log_timeout(property.id)
            continue  # Skip this property
        except Exception as e:
            log_error(property.id, e)
            continue

        # Rate limiting
        sleep(2)  # 30 requests/min max
```

---

## 5. Risks & Mitigation Strategies

### 5.1 Risk Matrix

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Hallucinated Values** | HIGH | MEDIUM | Output validation, enum constraints |
| **Rate Limit Exceeded** | MEDIUM | HIGH | Throttling, batching, caching |
| **Schema Drift** | HIGH | LOW | Version prompts, validate against schema |
| **Latency Impact** | MEDIUM | HIGH | Async processing, timeouts |
| **Cost Overrun** | LOW | LOW | Free tier, monitor usage |
| **API Downtime** | MEDIUM | MEDIUM | Circuit breaker, fallback mode |
| **Inconsistent Classifications** | MEDIUM | MEDIUM | Prompt engineering, examples |
| **Data Corruption** | HIGH | LOW | Backups, rollback mechanism |

### 5.2 Detailed Mitigation Strategies

#### A. Hallucinated Values

**Problem**: LLM invents data (e.g., "5 bedrooms" when only title provided)

**Mitigations**:
1. **Strict Enum Validation**: Only accept predefined values
   ```python
   ALLOWED_TYPES = ['apartment', 'house', 'land', 'commercial', 'maisonette', 'mansion']
   if llm_type not in ALLOWED_TYPES:
       reject()
   ```

2. **Cross-Field Validation**: Check logical consistency
   ```python
   if property_type == 'land' AND bedrooms > 0:
       flag_suspicious()
   ```

3. **Confidence Thresholds**: Require 70%+ confidence from LLM

4. **Prompt Constraints**: Explicitly forbid hallucination
   ```
   "Only use information from the provided text. If uncertain, return 'unknown'."
   ```

5. **Audit Trail**: Log all LLM changes for manual review

#### B. Rate Limits & Costs

**Problem**: Exceeding API limits, unexpected costs

**Mitigations**:
1. **Daily Quota Monitoring**: Track API calls per day
   ```python
   if daily_calls >= 1000:  # Conservative limit
       disable_llm_for_today()
   ```

2. **Smart Throttling**: Adaptive rate limiting
   ```python
   if rate_limit_hit:
       backoff_seconds *= 2  # Exponential backoff
   ```

3. **Caching Layer**: Store LLM responses by input hash
   ```python
   cache_key = hash(title + description)
   if cache_key in llm_cache:
       return llm_cache[cache_key]
   ```

4. **Priority Queue**: Process high-value first
   ```python
   priority = sale > rent > shortlet
   process_by_priority()
   ```

#### C. Schema Drift

**Problem**: LLM output changes over time, breaks schema

**Mitigations**:
1. **Versioned Prompts**: Track prompt versions
   ```python
   prompt_version = "v1.2_nigerian_realestate_classification"
   ```

2. **Schema Enforcement**: Pydantic models for validation
   ```python
   class LLMResponse(BaseModel):
       property_type: Literal['apartment', 'house', ...]
       confidence: int = Field(ge=0, le=100)
   ```

3. **Regression Testing**: Test LLM on known examples daily
   ```python
   test_cases = load_golden_examples()
   accuracy = test_llm_accuracy(test_cases)
   if accuracy < 80%:
       alert_team()
   ```

4. **Immutable Fields**: Never LLM-modify critical fields (price, URL, source)

#### D. Latency

**Problem**: LLM adds 3-10 seconds per property

**Mitigations**:
1. **Async Workers**: Celery queue for background processing
   ```python
   @celery.task
   def enrich_property(property_id):
       # Process in background
   ```

2. **Progressive Enhancement**:
   - Upload basic property immediately (no LLM)
   - Enrich with LLM later (background job)
   - Frontend shows "enriching..." badge

3. **Timeout Enforcement**: 15-second hard limit
   ```python
   response = requests.post(llm_api, timeout=15)
   ```

4. **Parallel Processing**: 5 concurrent workers (rate limit permitting)

#### E. Debugging Difficulty

**Problem**: Hard to debug LLM decisions

**Mitigations**:
1. **Comprehensive Logging**: Log every LLM call
   ```python
   log_llm_call(
       property_id=prop.id,
       prompt=prompt_text,
       response=llm_output,
       confidence=confidence,
       applied=True/False,
       reason=rejection_reason
   )
   ```

2. **Explainability**: Ask LLM to explain
   ```
   "Explain your classification in one sentence."
   ```

3. **Manual Review Dashboard**: UI to review LLM decisions
   - Show original data vs LLM suggestion
   - Accept/reject buttons
   - Build training data for future fine-tuning

4. **Rollback Mechanism**: Revert LLM changes if needed
   ```python
   revert_llm_enrichment(property_id, before_timestamp)
   ```

---

## 6. Safeguards & Validation

### 6.1 Input Validation (Before LLM)

**What to Send**:
- ✅ `title` (clean, no HTML)
- ✅ `description` (first 500 chars max)
- ✅ `price` (already parsed to number)
- ✅ `location` (already filtered to Lagos)

**What to NEVER Send**:
- ❌ Raw HTML (context pollution)
- ❌ URL (privacy, not useful)
- ❌ Source site name (avoid bias)
- ❌ Scrape timestamp (irrelevant)
- ❌ User PII (if any)
- ❌ Internal IDs (security risk)

### 6.2 Output Validation (After LLM)

**Validation Checklist**:

```python
def validate_llm_response(response: dict, property: dict) -> bool:
    """Strict validation of LLM output"""

    # 1. Required fields present
    required = ['property_type', 'furnishing', 'confidence']
    if not all(k in response for k in required):
        return False

    # 2. Enum constraints
    if response['property_type'] not in ALLOWED_PROPERTY_TYPES:
        return False
    if response['furnishing'] not in ALLOWED_FURNISHING:
        return False

    # 3. Confidence threshold
    if response['confidence'] < 70:
        return False

    # 4. Cross-field logic
    if response['property_type'] == 'land' and response.get('bedrooms', 0) > 0:
        return False  # Land doesn't have bedrooms

    # 5. Suspicious patterns
    if response['property_type'] == 'apartment' and property.price > 500_000_000:
        # Apartments >500M NGN are rare, flag for review
        flag_for_review(property.id, reason="price_type_mismatch")

    # 6. JSON structure
    if not isinstance(response, dict):
        return False

    # 7. No hallucinated fields
    allowed_keys = ['property_type', 'furnishing', 'condition', 'amenities', 'confidence', 'reasoning']
    if any(k not in allowed_keys for k in response.keys()):
        return False  # LLM returned unexpected fields

    return True
```

### 6.3 Monitoring & Alerts

**Metrics to Track**:

| Metric | Threshold | Alert |
|--------|-----------|-------|
| LLM Success Rate | <80% | Investigate API |
| Average Latency | >10 seconds | Reduce batch size |
| Daily API Calls | >1000 | Approaching limit |
| Hallucination Rate | >5% | Review prompts |
| Low Confidence | >30% of responses | Improve prompts |
| Schema Validation Failures | >10% | LLM output drift |

**Dashboard (Future)**:
- Real-time LLM health status
- Last 100 LLM calls (with prompts/responses)
- Acceptance/rejection rate by field
- Cost tracking (if API becomes paid)
- A/B test results (LLM vs non-LLM quality)

---

## 7. Phased Rollout Plan

### Phase 1: PILOT (Week 1-2)

**Scope**: 100 properties, non-critical fields only

**Steps**:
1. **Setup**:
   - Create ApiFreeLLM account
   - Test API connectivity
   - Write LLM client wrapper
   - Create validation functions

2. **Test on Safe Subset**:
   - Query 100 properties with `furnishing = null`
   - Run LLM enrichment (offline, not in main pipeline)
   - Compare LLM output vs manual classification (gold standard)
   - Measure accuracy, latency, cost

3. **Success Criteria**:
   - ✅ Accuracy: >75% match with manual labels
   - ✅ Latency: <8 seconds average
   - ✅ No hallucinations caught by validation
   - ✅ No API errors/downtime

4. **Decision Point**:
   - If success → Proceed to Phase 2
   - If failure → Adjust prompts, retry OR abandon

---

### Phase 2: SHADOW MODE (Week 3-4)

**Scope**: All new properties, but don't save to database yet

**Steps**:
1. **Integration**:
   - Add LLM layer to pipeline (after rule-based cleaner)
   - Run LLM on all properties
   - Log results but DON'T update Firestore
   - Compare LLM vs rule-based results

2. **Monitoring**:
   - Track disagreements (LLM vs rules)
   - Measure improvement in coverage (fields filled)
   - Identify edge cases where LLM fails

3. **Success Criteria**:
   - ✅ LLM fills 30%+ more fields than rules alone
   - ✅ <5% invalid classifications (caught by validation)
   - ✅ No pipeline slowdown (async works)
   - ✅ No API quota exceeded

4. **Decision Point**:
   - If success → Proceed to Phase 3
   - If mixed → Adjust threshold/prompts, retry
   - If failure → Rollback to Phase 1

---

### Phase 3: LIVE (Week 5-6)

**Scope**: Production, save to database

**Steps**:
1. **Gradual Rollout**:
   - Enable LLM for 10% of properties (A/B test)
   - Monitor frontend search/filter accuracy
   - Collect user feedback
   - Gradually increase to 50%, then 100%

2. **A/B Testing**:
   - Group A: LLM-enriched properties
   - Group B: Rule-based only
   - Metric: User click-through rate, time-on-page
   - Hypothesis: LLM properties get 15%+ more engagement

3. **Rollback Plan**:
   - Add `llm_enriched: boolean` flag to schema
   - If quality issues → filter WHERE llm_enriched = false
   - If critical bug → disable LLM queue, revert changes

4. **Success Criteria**:
   - ✅ User engagement improves (or stays same)
   - ✅ No increase in error reports
   - ✅ Search/filter accuracy improves
   - ✅ LLM cost <$10/month (free tier)

---

### Phase 4: OPTIMIZATION (Week 7+)

**Scope**: Fine-tuning, cost reduction

**Steps**:
1. **Prompt Engineering**:
   - Add few-shot examples to prompts
   - A/B test prompt variations
   - Optimize for accuracy vs latency

2. **Cost Optimization**:
   - Implement aggressive caching
   - Prioritize high-value properties only
   - Consider switching to paid tier if better ROI

3. **Model Upgrade**:
   - If ApiFreeLLM quality is insufficient:
     - Test GPT-3.5-turbo (cheap, accurate)
     - Test Claude Haiku (balanced)
     - Compare cost vs accuracy tradeoff

---

## 8. What Inputs LLM Should See (and NOT See)

### 8.1 RECOMMENDED INPUTS

**Tier 1 - Always Include**:
```json
{
  "title": "3 Bedroom Apartment in Lekki Phase 1",
  "description": "Fully furnished with pool, gym, 24hr power...",
  "price": 35000000,
  "location": "Lekki Phase 1"
}
```

**Why**:
- Core context for classification
- Already cleaned by rule-based logic
- No sensitive data
- Essential for accurate LLM inference

---

**Tier 2 - Conditionally Include**:
```json
{
  "bedrooms": 3,  // If already extracted
  "bathrooms": 2,  // If already extracted
  "listing_type": "sale"  // If already known
}
```

**Why**:
- Helps LLM validate consistency
- Can catch errors (e.g., land with bedrooms)
- Already structured data (not free text)

---

**Tier 3 - Optional Context**:
```json
{
  "currency": "NGN",  // Implicit from price
  "state": "Lagos"  // Already filtered
}
```

**Why**:
- Provides geographic context for local terminology
- Helps with area-specific classifications

---

### 8.2 NEVER SEND TO LLM

**Security/Privacy**:
- ❌ URL (reveals source site, privacy concern)
- ❌ Source site name (can bias LLM: "Site A = luxury, Site B = budget")
- ❌ Scrape timestamp (irrelevant)
- ❌ Internal database IDs (security risk)
- ❌ Hash values (meaningless to LLM)
- ❌ Agent contact info (PII)
- ❌ User data (if any)

**Technical**:
- ❌ Raw HTML (too much noise, hallucination risk)
- ❌ CSS selectors (irrelevant)
- ❌ Image URLs (LLM can't process images, ApiFreeLLM is text-only)
- ❌ Geocoordinates (already have location name)
- ❌ Quality score (circular dependency)

**Example - BAD Prompt**:
```
URL: https://site-a.com/property/12345
Source: Site A Premium Listings
Scraped: 2025-12-25 08:30:15
ID: abc123def456
HTML: <div class="property">...2000 chars of markup...</div>
```

**Example - GOOD Prompt**:
```
Classify this Nigerian property:

Title: Luxury 3 Bedroom Apartment
Description: Spacious apartment with modern fittings, swimming pool, gym, 24hr power supply. Located in serene Lekki Phase 1 estate.
Price: ₦35,000,000
Location: Lekki Phase 1, Lagos
Bedrooms: 3
Bathrooms: 2

Return ONLY this JSON (no explanation):
{
  "property_type": "apartment|house|land|commercial|maisonette|mansion",
  "furnishing": "furnished|semi-furnished|unfurnished",
  "condition": "new|renovated|needs_renovation|unknown",
  "amenities": ["pool", "gym", "power", "security", ...],
  "confidence": 0-100,
  "reasoning": "Brief explanation"
}

Rules:
- Only use information provided above
- If uncertain, use "unknown" and confidence <70
- Amenities must be from actual description (no hallucination)
- Property type must match Nigerian real estate market
```

---

## 9. Success Metrics & KPIs

### 9.1 Data Quality Metrics

**Before LLM (Baseline)**:
| Metric | Current |
|--------|---------|
| Properties with property_type | 45% |
| Properties with furnishing | 20% |
| Properties with amenities | 10% |
| Properties with condition | 5% |
| Classification accuracy | N/A (no ground truth) |

**After LLM (Target)**:
| Metric | Goal | Stretch |
|--------|------|---------|
| Properties with property_type | 85% | 95% |
| Properties with furnishing | 70% | 85% |
| Properties with amenities | 60% | 75% |
| Properties with condition | 50% | 70% |
| Classification accuracy | 75% | 85% |

---

### 9.2 Operational Metrics

**Performance**:
- LLM latency: <8 seconds (avg)
- Pipeline throughput: No degradation (async processing)
- Cache hit rate: >40% (after 1 week)

**Reliability**:
- LLM API uptime: >95%
- Validation pass rate: >90%
- Hallucination rate: <5%

**Cost**:
- API calls per day: <1000 (free tier limit)
- Cost per property: $0 (free tier)
- If paid tier: <$0.01 per property

---

### 9.3 Business Impact

**User Experience**:
- Search relevance: +15% improvement
- Filter accuracy: +20% (more properties correctly classified)
- User engagement: +10% time-on-site

**Operational**:
- Manual data cleanup time: -50%
- Data completeness: +40%
- New site onboarding: -30% effort (less site-specific tuning)

---

## 10. Rollback Plan

### 10.1 Pre-Rollout Safeguards

Before enabling LLM in production:

1. **Full Database Backup**
   ```bash
   # Firestore export
   gcloud firestore export gs://backup-bucket/pre-llm-backup
   ```

2. **Feature Flag**
   ```python
   LLM_ENABLED = os.getenv('ENABLE_LLM', 'false') == 'true'
   ```

3. **Canary Deployment**
   - Enable for 1% of properties first
   - Monitor for 24 hours
   - Gradually increase to 100%

---

### 10.2 Rollback Triggers

**Automatic Rollback If**:
- LLM API error rate >20% for 5 minutes
- Validation failure rate >30%
- Average latency >15 seconds for 10 minutes
- Firestore write errors >10% (due to LLM schema)

**Manual Rollback If**:
- User reports of incorrect data spike
- Search/filter functionality broken
- API cost exceeds budget
- LLM hallucinations detected in production

---

### 10.3 Rollback Procedure

**Step 1: Disable LLM** (Immediate)
```python
# Set environment variable
export ENABLE_LLM=false

# Restart workers
systemctl restart celery-workers
```

**Step 2: Revert Database** (If needed)
```python
# Query LLM-modified properties
properties_to_revert = db.collection('properties').where('llm_enriched', '==', True).get()

# Restore from backup or delete LLM fields
for prop in properties_to_revert:
    prop.update({
        'property_details.property_type': original_value,  # From backup
        'llm_enriched': False
    })
```

**Step 3: Post-Mortem** (Within 24 hours)
- Analyze logs to identify root cause
- Document failure scenario
- Adjust validation or prompts
- Plan retry with fixes

---

## 11. Alternative Approaches (Considered & Rejected)

### 11.1 Fine-Tuned Model

**Approach**: Train custom model on Nigerian real estate data

**Pros**:
- Higher accuracy than generic LLM
- Tailored to local terminology
- No API rate limits

**Cons**:
- Requires 1000+ labeled examples (don't have)
- Training cost: $500-$2000
- Maintenance burden (retraining)
- Inference hosting cost: $50-$200/month

**Verdict**: ❌ REJECTED - Too expensive for pilot, revisit if ApiFreeLLM fails

---

### 11.2 On-Premise LLM (Llama, Mistral)

**Approach**: Self-host open-source LLM

**Pros**:
- No API limits
- No external dependency
- Data privacy

**Cons**:
- Requires GPU server ($100-$300/month)
- Inference latency: 2-5 seconds per request
- DevOps complexity
- Model updates manual

**Verdict**: ❌ REJECTED - Overkill for 366 properties, revisit at 10K+ scale

---

### 11.3 Rule-Based Enhancements

**Approach**: Improve existing regex/dict lookups

**Pros**:
- Free
- Fast
- Deterministic

**Cons**:
- Doesn't solve ambiguous classification
- Requires site-specific tuning
- High maintenance burden

**Verdict**: ⚠️ COMPLEMENTARY - Do both (rules for easy cases, LLM for hard cases)

---

## 12. Summary & Recommendation

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Where in pipeline?** | After rule-based cleaner, before Firestore | Clean input, focused task, fallback safety |
| **What does LLM do?** | Classification & normalization only | Augment rules, not replace |
| **What does LLM NOT do?** | Price parsing, geocoding, deduplication | Rules are better |
| **How to handle errors?** | Validation + fallback + circuit breaker | Graceful degradation |
| **How to handle rate limits?** | Batching + throttling + caching | Stay within free tier |
| **How to validate?** | Enum constraints + cross-field logic | Prevent hallucinations |
| **How to rollout?** | Pilot → Shadow → Canary → Full | Minimize risk |
| **What to send LLM?** | Title, description, price, location | Essential context only |
| **What NOT to send LLM?** | URL, HTML, IDs, PII | Security & privacy |

---

### Go/No-Go Recommendation

**RECOMMENDATION**: ✅ PROCEED WITH PILOT

**Conditions**:
1. Start with Phase 1 (100 properties, offline test)
2. Measure accuracy against manual labels
3. If accuracy >75% → Proceed to Phase 2
4. If accuracy <75% → Adjust prompts, retry OR consider paid LLM

**Expected Outcome**:
- +40% data completeness (more fields filled)
- +15% classification accuracy
- -50% manual cleanup effort
- Minimal cost (free tier)
- Low risk (fallback to rules)

**Timeline**:
- Week 1-2: Pilot (100 properties)
- Week 3-4: Shadow mode (all properties, no save)
- Week 5-6: Live canary (10% → 100%)
- Week 7+: Optimization

**Total Investment**: 20-30 hours engineering time, $0 API cost (free tier)

---

## Appendix A: Sample LLM Prompts

### Prompt 1: Property Type Classification

```
You are a Nigerian real estate expert. Classify this property.

INPUT:
Title: {title}
Description: {description}
Price: ₦{price:,}
Location: {location}

OUTPUT (JSON only, no explanation):
{
  "property_type": "apartment|house|land|commercial|maisonette|mansion",
  "confidence": 0-100,
  "reasoning": "one sentence"
}

RULES:
- Apartment: Flat, condo, studio in multi-unit building
- House: Detached, semi-detached, duplex, bungalow, terrace
- Land: Empty plot, no buildings
- Commercial: Office, shop, warehouse
- Maisonette: Multi-level apartment
- Mansion: Luxury house, villa, estate home
- If uncertain, use most specific type + confidence <70
```

---

### Prompt 2: Furnishing Classification

```
Determine furnishing status from Nigerian property listing.

INPUT:
Description: {description}

OUTPUT:
{
  "furnishing": "furnished|semi-furnished|unfurnished",
  "confidence": 0-100
}

EXAMPLES:
- "Fully fitted" → furnished
- "Empty" → unfurnished
- "Part furnished" → semi-furnished
- "With appliances" → furnished
- "Bare" → unfurnished
- "Move-in ready" → furnished
```

---

### Prompt 3: Amenity Extraction

```
Extract amenities from description (Nigerian context).

INPUT:
{description}

OUTPUT:
{
  "amenities": ["pool", "gym", "power", "security", ...],
  "confidence": 0-100
}

CATEGORIES:
- Security: CCTV, gated, gateman, security guard
- Power: 24hr power, generator, inverter, solar
- Water: Borehole, water supply, 24hr water
- Parking: Parking, garage, car park
- Facilities: Pool, gym, clubhouse, playground
- Kitchen: Fitted kitchen, modern kitchen
- Other: AC, wardrobes, BQ (boys quarters)

RULES:
- Only extract amenities explicitly mentioned
- Do not infer or hallucinate
- Use standard Nigerian terminology
```

---

## Appendix B: Validation Schema (Pydantic)

```python
# Pseudocode for validation (NOT implementation)

from pydantic import BaseModel, Field, validator
from typing import List, Literal

class LLMPropertyClassification(BaseModel):
    """Strict schema for LLM output validation"""

    property_type: Literal[
        'apartment', 'house', 'land',
        'commercial', 'maisonette', 'mansion'
    ]

    furnishing: Literal[
        'furnished', 'semi-furnished', 'unfurnished'
    ] = None

    condition: Literal[
        'new', 'renovated', 'needs_renovation', 'unknown'
    ] = 'unknown'

    amenities: List[str] = Field(default_factory=list, max_items=20)

    confidence: int = Field(ge=0, le=100)

    reasoning: str = Field(max_length=200)

    @validator('amenities')
    def validate_amenities(cls, v):
        """Ensure amenities are from allowed list"""
        ALLOWED = {
            'pool', 'gym', 'power', 'security', 'cctv',
            'parking', 'garage', 'borehole', 'water',
            'fitted_kitchen', 'ac', 'wardrobes', 'bq'
        }
        return [a for a in v if a.lower().replace(' ', '_') in ALLOWED]

    @validator('confidence')
    def confidence_threshold(cls, v):
        """Reject low confidence"""
        if v < 70:
            raise ValueError(f"Confidence {v}% too low (min 70%)")
        return v
```

---

## Appendix C: Monitoring Dashboard (Mockup)

```
╔════════════════════════════════════════════════╗
║  LLM ENRICHMENT DASHBOARD                      ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Status: ● ACTIVE                              ║
║  Last Run: 2 minutes ago                       ║
║                                                ║
║  TODAY'S STATS:                                ║
║  ├─ API Calls: 243 / 1000 (24%)               ║
║  ├─ Success Rate: 87.3%                        ║
║  ├─ Avg Latency: 6.2s                          ║
║  ├─ Cache Hit Rate: 42%                        ║
║  └─ Properties Enriched: 189                   ║
║                                                ║
║  QUALITY METRICS:                              ║
║  ├─ Validation Pass Rate: 94.1%                ║
║  ├─ Hallucination Rate: 2.8% ✅                ║
║  ├─ Low Confidence (<70%): 12.5%               ║
║  └─ Schema Validation Failures: 1.2% ✅        ║
║                                                ║
║  FIELD COVERAGE:                               ║
║  ├─ property_type: 45% → 87% (+42%) 📈         ║
║  ├─ furnishing: 20% → 76% (+56%) 📈            ║
║  ├─ amenities: 10% → 68% (+58%) 📈             ║
║  └─ condition: 5% → 54% (+49%) 📈              ║
║                                                ║
║  RECENT FAILURES (last 5):                     ║
║  1. Property #1234: Timeout (15s)              ║
║  2. Property #1235: Low confidence (68%)       ║
║  3. Property #1240: Invalid property_type      ║
║  4. Property #1245: Rate limit (429)           ║
║  5. Property #1250: API error (500)            ║
║                                                ║
╚════════════════════════════════════════════════╝

[View Logs] [Manual Review Queue] [Disable LLM]
```

---

**END OF STRATEGIC PLAN**

**Status**: Ready for review & approval before implementation
**Next Step**: User decision to proceed with Phase 1 (Pilot)
**Estimated Implementation Time**: 6-8 weeks (phased rollout)
**Risk Level**: LOW (free tier, fallback to rules, phased approach)
**Expected ROI**: HIGH (40%+ data completeness, minimal cost)
