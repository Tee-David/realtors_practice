# parsers/specials.py
# Generic, config-driven parser with:
# - Lagos-scoped list paths when supported
# - Optional site search query support (adds ?q= or similar)
# - Pagination via explicit "Next" link or fallback ?page=N
# - Merges embedded JSON-LD + visible cards
# - Two-level scraping: list pages + property detail pages
# - Location discovery: auto-navigate location directories
# - Intelligent scraper: heuristic relevance detection + auto-adapt selectors
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import re, os, json, logging
from core.scraper_engine import fetch_adaptive
from core.detail_scraper import enrich_listings_with_details
from core.url_validator import filter_listings_by_url
from core.location_filter import get_location_filter

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"
RP_INTELLIGENT_MODE = os.getenv("RP_INTELLIGENT_MODE", "0") == "1"  # Enable intelligent scraper features

# NOTE: All site configurations are now in config.yaml
# No hard-coded site configs here - 100% config-driven architecture

GENERIC_CARD = "div[class*=listing], div[class*=property], article, li"
GENERIC_TITLE = "h1, h2, h3, .title, a"
GENERIC_PRICE = ".price, .amount, [class*=price]"
GENERIC_LOCATION = ".location, .address, .region, .area, [class*=location]"
GENERIC_IMAGE = "img"

def _first(el, selector_csv):
    if not selector_csv:
        return None
    for css in [c.strip() for c in selector_csv.split(",")]:
        node = el.select_one(css)
        if node:
            return node
    return None

def _text(el):
    return el.get_text(" ", strip=True) if el else ""

def _is_property_url(url_str):
    """
    Intelligent filtering to identify actual property listing URLs vs category/navigation links.

    Returns True if URL looks like a property listing, False for category/location pages.
    """
    if RP_DEBUG:
        logger.debug(f"Checking URL: {url_str}")
    if not url_str:
        return False

    url_lower = url_str.lower()

    # Skip obvious category/navigation pages
    category_patterns = [
        # Just location names (e.g., /lagos, /lekki, /victoria-island)
        r'^https?://[^/]+/(?:lagos|lekki|ikoyi|vi|victoria-island|ikeja|ajah|yaba|surulere|abuja|port-harcourt)/?$',
        # Location subdirectories without property info (e.g., /lagos/lekki, /for-sale/lagos)
        r'^https?://[^/]+/(?:for-sale|for-rent|to-let|buy|rent)/(?:lagos|lekki|ikoyi|vi|ikeja|ajah)?/?$',
        r'^https?://[^/]+/(?:lagos|lekki|ikoyi)/(?:lagos|lekki|ikoyi|vi|ikeja|ajah)?/?$',
        # Category pages ending in /showtype, /in/, or location-only
        r'.*/showtype/?$',
        r'.*/(?:for-sale|for-rent)/[^/]+/(?:lagos|abuja|port-harcourt)/?$',
        # Property type + location without specific listing (e.g., /houses/lagos)
        r'.*/(?:flats-apartments|houses|land|commercial)/(?:lagos|lekki|ajah|ikoyi)/?$',
        # Property type category pages (e.g., /property-type/detached/, /property-type/maisonette/)
        r'.*/property-type/[^/]+/?$',
    ]

    import re
    for pattern in category_patterns:
        if re.match(pattern, url_str):
            if RP_DEBUG:
                logger.debug(f"URL rejected: Category match - {pattern}")
            return False

    # Positive indicators of property listings
    property_indicators = [
        'bedroom',
        'bathroom',
        'property',
        'flat',
        'house',
        'duplex',
        'apartment',
        'bungalow',
        'terrace',
        'detached',
        'semi-detached',
        'plot',
        'land',
        'office',
        'shop',
        'warehouse',
        'hotel',
        'estate',
    ]

    # If URL contains property-related keywords, likely a listing
    for indicator in property_indicators:
        if indicator in url_lower:
            if RP_DEBUG:
                logger.debug(f"URL accepted: Indicator match - {indicator}")
            return True

    # URLs with numeric IDs are often property pages (e.g., /property/12345, /listing-123456)
    if re.search(r'/\d{4,}', url_str) or re.search(r'[-_]\d{4,}', url_str):
        if RP_DEBUG:
            logger.debug(f"URL accepted: Numeric ID found")
        return True

    # If URL has 4+ path segments, likely a detailed property page
    # e.g., /for-sale/flats-apartments/3-bedroom-flat-lekki-lagos
    path_segments = url_str.split('/')[3:]  # Skip protocol and domain
    if len([s for s in path_segments if s]) >= 3:
        if RP_DEBUG:
            logger.debug(f"URL accepted: Deep path (3+ segments)")
        return True

    # Default: reject if we're not confident it's a property
    if RP_DEBUG:
        logger.debug(f"URL rejected: No property indicators")
    return False

def _next_page_by_link(soup, current_url, next_selectors):
    for sel in next_selectors or []:
        a = soup.select_one(sel)
        if a and a.get("href"):
            return urljoin(current_url, a["href"])
    return None

def _next_page_by_param(current_url, page_num, page_param):
    parts = list(urlsplit(current_url))
    qs = dict(parse_qsl(parts[3]))
    qs[page_param] = str(page_num)
    parts[3] = urlencode(qs)
    return urlunsplit(parts)

def _apply_search_param(url, search_param, query):
    if not (search_param and query):
        return url
    parts = list(urlsplit(url))
    qs = dict(parse_qsl(parts[3]))
    # Append search term; don’t overwrite if already present
    if search_param not in qs:
        qs[search_param] = query
    parts[3] = urlencode(qs)
    return urlunsplit(parts)

def _harvest_from_embedded_json(embedded_json_list):
    items = []
    def push(obj):
        # Filter out category/navigation URLs from embedded JSON
        url = obj.get("url")
        if url and not _is_property_url(url):
            return  # Skip category links

        addr = obj.get("address")
        if isinstance(addr, dict):
            loc = addr.get("addressLocality") or addr.get("streetAddress") or addr.get("addressRegion")
        else:
            loc = addr if isinstance(addr, str) else None
        imgs = obj.get("image")
        images = imgs if isinstance(imgs, list) else ([imgs] if imgs else [])
        items.append({
            "title": obj.get("name") or obj.get("title"),
            "price": obj.get("price") or obj.get("priceValue"),
            "location": loc,
            "property_type": obj.get("@type") or obj.get("propertyType"),
            "estate_name": None,
            "details": "",
            "land_size": None,
            "title_tag": None,
            "description": obj.get("description"),
            "promo_tags": None,
            "service_charge": None,
            "launch_timeline": None,
            "agent_name": (obj.get("seller") or {}).get("name") if isinstance(obj.get("seller"), dict) else None,
            "contact_info": None,
            "images": images,
            "listing_url": url,
            "coordinates": None,
            "source": None,
            "scrape_timestamp": None,
            "hash": None,
        })
    def walk(o):
        if isinstance(o, dict):
            if any(k in o for k in ("@type","name")) and any(k in o for k in ("price","address","url","image")):
                push(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    for blob in embedded_json_list:
        walk(blob)
    return items

def _scrape_list_page(url, cfg, fallback_order, site_key, page_idx):
    card_sel = (cfg.get("card") or GENERIC_CARD).strip()
    html, method, embedded = fetch_adaptive(url, card_sel.split(",")[0].strip(), fallback_order, site_key, page_idx)
    if RP_DEBUG:
        print(f"    fetched via: {method or 'none'} -> {url}")
    if not html:
        return None, []

    soup = BeautifulSoup(html, "lxml")

    # Embedded JSON
    items = []
    json_items = _harvest_from_embedded_json(embedded)
    if json_items:
        items.extend(json_items)

    # Visible cards
    cards = soup.select(card_sel)
    used_fallback = False
    if not cards:  # Only use generic fallback if specific selector finds nothing
        cards = soup.select(GENERIC_CARD)
        used_fallback = True

    # INTELLIGENT SCRAPER: Auto-discover best selector if both specific and generic fail
    if RP_INTELLIGENT_MODE and not cards:
        try:
            from helpers.relevance import find_best_selector

            # Try common selector patterns
            candidates = [
                'div[class*=listing]', 'div[class*=property]', 'div[class*=card]',
                'li[class*=listing]', 'li[class*=property]', 'li[class*=item]',
                'article', 'div.item', 'div.result', 'div.product'
            ]

            best_selector, results = find_best_selector(html, candidates, min_score=25)

            if best_selector:
                logger.info(f"{site_key}: Auto-discovered selector: {best_selector}")
                cards = soup.select(best_selector)
                used_fallback = True
            else:
                logger.warning(f"{site_key}: No suitable selector found via auto-discovery")

        except Exception as e:
            logger.warning(f"{site_key}: Auto-discovery failed: {e}")

    for box in cards:
        # INTELLIGENT SCRAPER: Optional relevance filtering
        if RP_INTELLIGENT_MODE and used_fallback:
            try:
                from helpers.relevance import is_relevant_listing

                # Extract href first for relevance check
                a = _first(box, "a[href]")
                href = urljoin(url, a.get("href")) if a and a.get("href") else None

                # Apply heuristic relevance filter
                threshold = int(os.getenv("RP_RELEVANCE_THRESHOLD", "25"))
                if not is_relevant_listing(box, url=href, threshold=threshold):
                    if RP_DEBUG:
                        logger.debug(f"Skipping irrelevant element (failed heuristic check)")
                    continue

            except Exception as e:
                if RP_DEBUG:
                    logger.warning(f"Relevance check failed: {e}")
                # Continue processing if relevance check fails
                pass

        title = _text(_first(box, cfg.get("title", GENERIC_TITLE)))
        price = _text(_first(box, cfg.get("price", GENERIC_PRICE)))
        location = _text(_first(box, cfg.get("location", GENERIC_LOCATION)))
        img_el = _first(box, cfg.get("image", GENERIC_IMAGE))
        img = img_el.get("src") if img_el and img_el.get("src") else None

        # Extract href - look for property-specific links
        a = _first(box, "a[href]")
        href = urljoin(url, a.get("href")) if a and a.get("href") else None

        # CRITICAL FIX: Filter out category/navigation links
        if href and not _is_property_url(href):
            if RP_DEBUG:
                logger.debug(f"Skipping category link: {href}")
            continue

        # BUG FIX: If href is None, skip this card entirely!
        # Don't use page URL as fallback for listing_url
        if not href:
            continue

        if not (title or price or location or href):
            continue

        items.append({
            "title": title,
            "price": price,
            "location": location,
            "property_type": None,
            "estate_name": None,
            "details": "",
            "land_size": None,
            "title_tag": None,
            "description": None,
            "promo_tags": None,
            "service_charge": None,
            "launch_timeline": None,
            "agent_name": None,
            "contact_info": None,
            "images": [img] if img else [],
            "listing_url": href or url,
            "coordinates": None,
            "source": cfg.get("name"),
            "scrape_timestamp": None,
            "hash": None,
        })

    # Pagination: explicit next link/button
    next_url = _next_page_by_link(soup, url, cfg.get("next_selectors"))
    # Fallback: numeric ?page=N param
    if not next_url and cfg.get("page_param"):
        next_url = _next_page_by_param(url, page_idx + 1, cfg["page_param"])
    return next_url, items

def scrape(fallback_order, filters, start_url=None, site=None, site_key=None, site_config=None):
    """
    Scrape a site using config-driven selectors.

    Args:
        fallback_order: List of fetch methods to try
        filters: Search filters dict
        start_url: Optional starting URL
        site: Site info dict (legacy)
        site_key: Site identifier
        site_config: Full site configuration from config.yaml (new, preferred)
    """
    key = site_key or (site.get("key") if site else None)

    # Require site_config - 100% config-driven, no hard-coded fallbacks
    if not site_config:
        raise ValueError(
            f"Site '{key}': site_config is required. "
            f"All sites must be configured in config.yaml. "
            f"No hard-coded fallbacks available."
        )

    # Build config from site_config YAML
    cfg = {
        "name": site_config.get("name", "Unknown"),
        "url": site_config.get("url", ""),
        "list_paths": site_config.get("list_paths", [""]),
        "card": site_config.get("selectors", {}).get("card", GENERIC_CARD),
        "title": site_config.get("selectors", {}).get("title", GENERIC_TITLE),
        "price": site_config.get("selectors", {}).get("price", GENERIC_PRICE),
        "location": site_config.get("selectors", {}).get("location", GENERIC_LOCATION),
        "image": site_config.get("selectors", {}).get("image", GENERIC_IMAGE),
        "next_selectors": site_config.get("pagination", {}).get("next_selectors", ["a[rel='next']", "a[aria-label*='Next']", ".pagination a.next"]),
        "page_param": site_config.get("pagination", {}).get("page_param", "page"),
        "search_param": site_config.get("search_param"),
    }

    # Add lagos_paths if present
    if "lagos_paths" in site_config:
        cfg["lagos_paths"] = site_config["lagos_paths"]

    base = (cfg["url"] or (site.get("url") if site else "")).rstrip("/")
    # Prefer lagos_paths when present; else use list_paths
    list_paths = cfg.get("lagos_paths") or cfg.get("list_paths", [""])

    # Optional search query (e.g., "Lagos") – passed from main via config.yaml
    search_query = None
    if filters and isinstance(filters, dict):
        search_query = filters.get("search_query")

    # NEW: Location Discovery Layer (Layer 0.5)
    # If enabled, discover location pages first, then scrape each location
    location_discovery_enabled = site_config.get("location_discovery", {}).get("enabled", False)

    if location_discovery_enabled:
        from core.location_discovery import discover_locations

        # Get all starting URLs (from list_paths or lagos_paths)
        starting_urls = [urljoin(base + "/", path.lstrip("/")) for path in list_paths]

        # Discover locations from each starting URL
        all_location_urls = []
        for start_url in starting_urls:
            location_urls = discover_locations(
                start_url=start_url,
                site_config=site_config,
                fallback_order=fallback_order,
                site_key=key or "site"
            )
            all_location_urls.extend(location_urls)

        # Update list_paths to scrape discovered locations
        # Convert back to relative paths for compatibility
        list_paths = []
        for loc_url in all_location_urls:
            # Extract path from URL
            if base in loc_url:
                relative_path = loc_url.replace(base, "").lstrip("/")
                list_paths.append("/" + relative_path if relative_path else "")
            else:
                list_paths.append(loc_url)  # Use absolute if needed

    all_items, seen = [], set()
    for path in list_paths:
        url = urljoin(base + "/", path.lstrip("/"))
        # Apply simple per-site search param if configured
        url = _apply_search_param(url, cfg.get("search_param"), search_query)

        pages = 0
        empty_streak = 0
        while url and pages < int(os.getenv("RP_PAGE_CAP", "40")):
            pages += 1
            next_url, items = _scrape_list_page(url, cfg, fallback_order, key or "site", pages)
            if RP_DEBUG:
                print(f"    page {pages}: +{len(items)} items")
            for it in items:
                u = (it.get("listing_url") or "") + "|" + (it.get("title") or "")
                if u and u not in seen:
                    it["source"] = it.get("source") or cfg.get("name")
                    all_items.append(it); seen.add(u)

            if not items:
                empty_streak += 1
            else:
                empty_streak = 0
            if empty_streak >= 2:  # stop after 2 consecutive empty pages
                break
            url = next_url

    # URL Validation: Filter out invalid URLs (WhatsApp, mailto, etc.)
    original_count = len(all_items)
    all_items, filtered_count = filter_listings_by_url(all_items, url_key='listing_url')

    if filtered_count > 0:
        logger.info(f"{key}: Filtered {filtered_count} invalid URLs (e.g., WhatsApp, mailto). Remaining: {len(all_items)}/{original_count}")

    # Location Filtering: Filter out non-Lagos properties (if enabled)
    if os.getenv("RP_LOCATION_FILTER", "0") == "1":
        location_filter = get_location_filter()
        before_location_filter = len(all_items)
        all_items, location_filtered = location_filter.filter_listings_by_location(all_items, location_key='location')

        if location_filtered > 0:
            logger.info(f"{key}: Location filter removed {location_filtered} non-Lagos properties. Remaining: {len(all_items)}/{before_location_filter}")

    # Level 2 Scraping: Enrich with detail page data
    # This clicks into each property URL and extracts complete information
    detail_cap_env = os.getenv("RP_DETAIL_CAP", "0")
    detail_cap = int(detail_cap_env) if detail_cap_env else 0
    max_properties = detail_cap if detail_cap > 0 else None  # 0 or empty = unlimited

    if RP_DEBUG:
        logger.debug(f"{key}: RP_DETAIL_CAP='{detail_cap_env}' -> max_properties={max_properties} (will process {'all' if max_properties is None else max_properties} of {len(all_items)} listings)")

    all_items = enrich_listings_with_details(
        listings=all_items,
        site_key=key or "site",
        site_config=site_config,
        fallback_order=fallback_order,
        max_properties=max_properties
    )

    return all_items
