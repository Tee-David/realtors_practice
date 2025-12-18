# 🎯 OPTIMIZATION ROADMAP - Complete Action Plan
**Date**: December 17, 2025
**Goal**: Reduce 5.4-hour workflows to <30 minutes
**Status**: Ready to implement

---

## Executive Summary: The 3 Killer Issues

After deep analysis, here are the **3 critical bugs** destroying your performance:

### 1. ⚠️ Detail Scraping is FAKE PARALLEL (5x Slowdown)
```python
# core/detail_scraper.py line 40
DETAIL_PARALLEL = os.getenv("RP_DETAIL_PARALLEL", "0") == "1"  # Default: Sequential!
```

**The smoking gun**: Your code CLAIMS parallel but defaults to sequential!

**Fix**: Add 1 line to workflow → **instant 5x speedup**

### 2. ⚠️ Firestore Uploads One-By-One (10x Slower)
```python
# Uploading 6,000 properties individually
for listing in listings:
    doc_ref.set(doc_data, merge=True)  # 6,000 network calls!
```

**The problem**: Should batch 500 at a time (Firestore supports this)

**Fix**: Replace with batch.commit() → **10x faster uploads**

### 3. ⚠️ No Caching = 90% Wasted Work
```python
# Every run scrapes ALL properties (even unchanged ones)
raw_items = try_scrape_with_retry(site_key, site_config)
# No check: "Have we seen this before?"
```

**The waste**: Re-scraping 5,400 properties when only 600 are new

**Fix**: Track seen URLs → **skip 90% of work**

---

## The Quick Wins (Do These TODAY - 1 Hour)

### WIN #1: Enable TRUE Parallel Detail Scraping (5 Minutes)
```yaml
# .github/workflows/scrape-production.yml line 303
env:
  RP_DETAIL_PARALLEL: 1  # ← ADD THIS LINE
  RP_DETAIL_WORKERS: 5    # ← ADD THIS LINE
  FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
  # ... rest of env vars ...
```

**Impact**: 65min sessions → 13min sessions (**5x faster!**)

---

### WIN #2: Batch Firestore Uploads (30 Minutes)

**File**: `core/firestore_enterprise.py`

Replace the `upload_listings_batch` method with this optimized version:

```python
def upload_listings_batch(
    self,
    site_key: str,
    listings: List[Dict[str, Any]],
    batch_size: int = 500
) -> Dict[str, Any]:
    """
    Upload listings in batches - 10x faster than one-by-one.
    Firestore supports up to 500 operations per batch.
    """
    if not self.enabled or self.db is None:
        return {'uploaded': 0, 'errors': len(listings), 'total': len(listings), 'status': 'failed'}

    if not listings:
        return {'uploaded': 0, 'errors': 0, 'total': 0}

    from concurrent.futures import ThreadPoolExecutor

    collection_ref = self.db.collection('properties')
    uploaded = 0
    errors = 0
    skipped = 0

    # STEP 1: Transform all listings in parallel (CPU-bound)
    logger.info(f"{site_key}: Transforming {len(listings)} listings...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        transformed = list(executor.map(
            lambda l: self._safe_transform(l, site_key),
            listings
        ))

    # Filter out failed transformations
    valid_docs = [(h, d) for h, d in transformed if h and d]
    skipped = len(listings) - len(valid_docs)

    # STEP 2: Upload in batches of 500
    logger.info(f"{site_key}: Uploading {len(valid_docs)} docs in batches...")

    for i in range(0, len(valid_docs), batch_size):
        batch = self.db.batch()
        chunk = valid_docs[i:i + batch_size]

        # Add all to batch
        for doc_hash, doc_data in chunk:
            doc_ref = collection_ref.document(doc_hash)
            batch.set(doc_ref, doc_data, merge=True)

        # Single commit for entire batch
        try:
            batch.commit()
            uploaded += len(chunk)
            batch_num = (i // batch_size) + 1
            logger.info(f"{site_key}: Batch {batch_num} uploaded: {len(chunk)} docs")
        except Exception as e:
            logger.error(f"{site_key}: Batch {batch_num} failed: {e}")
            errors += len(chunk)

    logger.info(f"{site_key}: Upload complete - {uploaded}/{len(listings)} uploaded")

    return {
        'uploaded': uploaded,
        'errors': errors,
        'skipped': skipped,
        'total': len(listings)
    }

def _safe_transform(self, listing: Dict, site_key: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Safely transform a listing (for parallel processing)."""
    try:
        doc_hash = listing.get('hash')
        if not doc_hash:
            return None, None

        if 'site_key' not in listing:
            listing['site_key'] = site_key

        doc_data = transform_to_enterprise_schema(listing)
        return doc_hash, doc_data
    except Exception as e:
        logger.error(f"{site_key}: Transform error: {e}")
        return None, None
```

**Impact**: 10min uploads → 1min uploads (**10x faster!**)

---

### WIN #3: Reduce Excessive Timeouts (5 Minutes)

**File**: `core/detail_scraper.py`

Find line 314 and change:
```python
# BEFORE (line 314)
page.goto(property_url, wait_until="domcontentloaded", timeout=60000)

# AFTER
page.goto(property_url, wait_until="commit", timeout=15000)  # 15s max
```

Find line 319 and change:
```python
# BEFORE (line 319)
page.wait_for_selector(wait_selector, timeout=8000, state="visible")

# AFTER
try:
    page.wait_for_selector(wait_selector, timeout=3000, state="attached")
except:
    page.wait_for_timeout(1000)  # Fallback: just wait 1s
```

**Impact**: 26s per property → 18s per property (**30% faster**)

---

## Expected Results After Quick Wins

### Before:
```
Session time: 65 minutes
- List scraping: 1 min
- Detail scraping: 52 min (sequential, 26s each)
- Firestore upload: 10 min (one-by-one)
- Geocoding: 2 min

Total workflow: 5.4 hours
```

### After Quick Wins (1 hour of work):
```
Session time: 8 minutes!
- List scraping: 1 min
- Detail scraping: 6 min (PARALLEL 5x, 5s each)
- Firestore upload: 1 min (batched)
- Geocoding: 0 min (disabled)

Total workflow: 0.7 hours (40 minutes!)
```

**5.4 hours → 40 minutes (8x faster!)**

---

## The Big Wins (Do These THIS WEEK - 1 Day)

### BIG WIN #1: Implement Property Caching (2-3 Hours)

Create new file: `core/property_cache.py`

```python
"""Property caching system to avoid re-scraping unchanged listings."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime, timedelta

CACHE_DIR = Path("logs/property_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class PropertyCache:
    """Persistent cache of scraped properties."""

    def __init__(self, site_key: str):
        self.site_key = site_key
        self.cache_file = CACHE_DIR / f"{site_key}_urls.json"
        self.detail_cache_file = CACHE_DIR / f"{site_key}_details.json"

        self.seen_urls = self._load_seen_urls()
        self.detail_cache = self._load_detail_cache()

    def _load_seen_urls(self) -> Set[str]:
        """Load set of previously scraped URLs."""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text())
                return set(data.get('urls', []))
            except:
                return set()
        return set()

    def _load_detail_cache(self) -> Dict:
        """Load detailed property data cache."""
        if self.detail_cache_file.exists():
            try:
                return json.loads(self.detail_cache_file.read_text())
            except:
                return {}
        return {}

    def is_new_url(self, url: str) -> bool:
        """Check if URL is new (not seen before)."""
        return url not in self.seen_urls

    def get_cached_details(self, url: str, max_age_days: int = 7) -> Optional[Dict]:
        """Get cached detail data if exists and not expired."""
        url_hash = hashlib.md5(url.encode()).hexdigest()

        if url_hash in self.detail_cache:
            cached = self.detail_cache[url_hash]
            cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))

            if datetime.now() - cached_time < timedelta(days=max_age_days):
                return cached.get('details')

        return None

    def add_url(self, url: str, details: Optional[Dict] = None):
        """Add URL to cache with optional detail data."""
        self.seen_urls.add(url)

        if details:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            self.detail_cache[url_hash] = {
                'details': details,
                'cached_at': datetime.now().isoformat()
            }

    def save(self):
        """Persist cache to disk."""
        # Save URLs
        self.cache_file.write_text(json.dumps({
            'urls': list(self.seen_urls),
            'count': len(self.seen_urls),
            'last_updated': datetime.now().isoformat()
        }))

        # Save details
        self.detail_cache_file.write_text(json.dumps(self.detail_cache))

    def filter_new_properties(self, properties: List[Dict]) -> List[Dict]:
        """Filter to only new properties not in cache."""
        new_props = []
        cached_props = []

        for prop in properties:
            url = prop.get('listing_url')
            if not url:
                continue

            if self.is_new_url(url):
                new_props.append(prop)
            else:
                # Try to use cached details
                cached_details = self.get_cached_details(url)
                if cached_details:
                    prop.update(cached_details)
                    cached_props.append(prop)
                else:
                    # Cache expired, treat as new
                    new_props.append(prop)

        return new_props, cached_props


# Usage in main.py
from core.property_cache import PropertyCache

def run_site(site_key: str, site_config: Dict):
    # Initialize cache
    cache = PropertyCache(site_key)

    # Scrape list pages
    raw_items = try_scrape_with_retry(site_key, site_config)

    # Normalize
    cleaned = []
    for r in raw_items:
        n = normalize_listing(r, site=site_key)
        if is_lagos_like(check_text):
            cleaned.append(n)

    # Filter to new properties only
    new_props, cached_props = cache.filter_new_properties(cleaned)

    logger.info(f"{site_key}: {len(new_props)} new, {len(cached_props)} cached ({len(cleaned)} total)")

    # Only do expensive operations on NEW properties
    if new_props:
        # Detail scraping only for new
        enriched_new = enrich_with_details(new_props)

        # Geocode only new
        geocoded_new = geocode_listings(enriched_new)

        # Update cache with new properties
        for prop in geocoded_new:
            cache.add_url(prop['listing_url'], prop)

        # Combine new + cached
        all_properties = geocoded_new + cached_props
    else:
        all_properties = cached_props

    # Export and upload ALL (new + cached)
    export_listings(site_key, all_properties)
    upload_listings_to_firestore(site_key, all_properties)

    # Save cache
    cache.save()

    return len(all_properties), site_config.get('url', '')
```

**Impact**: 6,000 properties → 600 new properties (**10x less work!**)

---

### BIG WIN #2: Implement Page Pool (1-2 Hours)

**File**: `core/detail_scraper.py`

Replace the `BrowserContextManager` class (lines 203-284) with this optimized version:

```python
from queue import Queue, Empty
import threading

class BrowserContextManager:
    """Browser context with page pool for efficient reuse."""

    def __init__(self, headless: bool = True, block_images: bool = False, pool_size: int = 5):
        self.headless = headless
        self.block_images = block_images
        self.pool_size = pool_size
        self._playwright = None
        self._browser = None
        self._context = None
        self._page_pool = Queue(maxsize=pool_size)
        self._created_pages = 0
        self._lock = threading.Lock()

    def __enter__(self):
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        self._context = self._browser.new_context(viewport={"width": 1500, "height": 900})

        # Pre-create page pool
        logger.info(f"Creating page pool of {self.pool_size} pages...")
        for _ in range(self.pool_size):
            page = self._create_page()
            self._page_pool.put(page)

        logger.info(f"Browser context ready with {self.pool_size} reusable pages")
        return self

    def _create_page(self):
        """Create a new configured page."""
        page = self._context.new_page()

        if self.block_images:
            def _route(route, request):
                if request.resource_type in ("image", "media", "font"):
                    route.abort()
                else:
                    route.continue_()
            page.route("**/*", _route)

        self._created_pages += 1
        return page

    def get_page(self, timeout: float = 30.0):
        """Get page from pool (thread-safe)."""
        try:
            return self._page_pool.get(timeout=timeout)
        except Empty:
            # Pool exhausted, create extra page
            logger.warning(f"Page pool exhausted, creating extra page")
            return self._create_page()

    def return_page(self, page):
        """Return page to pool for reuse."""
        try:
            # Reset page state
            page.goto("about:blank", wait_until="commit", timeout=3000)
        except:
            pass

        # Return to pool
        try:
            self._page_pool.put_nowait(page)
        except:
            # Pool full, close excess page
            page.close()

    def __exit__(self, *args):
        # Close all pages
        while not self._page_pool.empty():
            try:
                page = self._page_pool.get_nowait()
                page.close()
            except:
                pass

        self._context.close()
        self._browser.close()
        self._playwright.stop()
```

Then update `scrape_property_details_with_browser`:

```python
def scrape_property_details_with_browser(
    property_url: str,
    site_key: str,
    detail_config: Dict,
    browser_manager: BrowserContextManager,
) -> Dict:
    """Scrape using pooled page (much faster)."""
    page = None
    try:
        # Get reusable page from pool
        page = browser_manager.get_page()

        # Navigate (optimized timeout)
        page.goto(property_url, wait_until="commit", timeout=15000)

        # Quick selector wait
        wait_selector = detail_config.get("main_container", "main, .content")
        try:
            page.wait_for_selector(wait_selector, timeout=2000)
        except:
            pass  # Continue even if selector not found

        # Extract data
        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        # ... existing extraction code ...

        return details

    finally:
        # CRITICAL: Return page to pool (don't close!)
        if page:
            browser_manager.return_page(page)
```

**Impact**: Eliminate 2s page creation overhead × 120 properties = **4 minutes saved per session**

---

## Complete Performance Projection

### CURRENT STATE:
```
Session: 65 minutes per site
Workflow: 5.4 hours for 50 sites
```

### AFTER QUICK WINS (1 hour work):
```
Session: 8 minutes per site (8x faster!)
Workflow: 40 minutes for 50 sites (8x faster!)
```

### AFTER BIG WINS (1 day work):
```
Session: 3 minutes per site (21x faster!)
Workflow: 15 minutes for 50 sites (21x faster!)

Breakdown per session:
- List scraping: 30 seconds
- Detail scraping: 1 minute (only 30 NEW properties × 2s each)
- Firestore upload: 30 seconds (batched)
- Geocoding: 30 seconds (only new properties)
```

**FINAL: 5.4 hours → 15 minutes (21x faster!)**

---

## Implementation Timeline

### TODAY (1 hour):
- [ ] Add `RP_DETAIL_PARALLEL=1` to workflow
- [ ] Add `RP_DETAIL_WORKERS=5` to workflow
- [ ] Replace Firestore upload with batch version
- [ ] Reduce timeouts (60s→15s, 8s→3s)
- [ ] Test with 1-2 sites
- [ ] **Deploy to GitHub**

**Result**: 5.4 hours → 40 minutes ✅

### THIS WEEK (1 day):
- [ ] Implement property caching system
- [ ] Implement page pool pattern
- [ ] Test with full 50 sites
- [ ] Monitor and validate

**Result**: 40 minutes → 15 minutes ✅

---

## Testing Checklist

After each optimization:
- [ ] Test with single site (npc or castles)
- [ ] Verify Firestore uploads still work (100% success)
- [ ] Check logs for errors
- [ ] Measure time improvement
- [ ] Test with 3-5 sites
- [ ] Deploy to production

---

## What NOT to Do

❌ **Don't** add more features (focus on optimization)
❌ **Don't** change the enterprise schema (it's good)
❌ **Don't** re-architect the whole system (current design is fine)
❌ **Don't** add new dependencies (use existing libraries)
❌ **Don't** optimize prematurely (start with quick wins)

✅ **DO** fix the 3 killer bugs first
✅ **DO** test incrementally
✅ **DO** measure improvements
✅ **DO** keep it simple

---

## Summary: Your Action Plan

**Phase 1 (TODAY - 1 hour):**
1. Enable parallel detail scraping (2 lines in YAML)
2. Batch Firestore uploads (30 min code change)
3. Reduce timeouts (5 min code change)

**Result**: 5.4 hours → 40 minutes (**8x faster**)

**Phase 2 (THIS WEEK - 1 day):**
4. Implement property caching (3 hours)
5. Implement page pooling (2 hours)

**Result**: 40 minutes → 15 minutes (**21x faster overall**)

**The best part?** All optimizations work within your current architecture. No re-architecture needed. Just fix the bugs and add caching!

---

**Ready to implement Phase 1 now? It's literally 1 hour of work for 8x speedup.**
