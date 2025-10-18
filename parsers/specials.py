# parsers/specials.py
# Generic, config-driven parser with:
# - Lagos-scoped list paths when supported
# - Optional site search query support (adds ?q= or similar)
# - Pagination via explicit "Next" link or fallback ?page=N
# - Merges embedded JSON-LD + visible cards
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import re, os, json
from core.scraper_engine import fetch_adaptive

RP_DEBUG = os.getenv("RP_DEBUG") == "1"

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
            "listing_url": obj.get("url"),
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
    cards = soup.select(card_sel) or soup.select(GENERIC_CARD)
    for box in cards:
        title = _text(_first(box, cfg.get("title", GENERIC_TITLE)))
        price = _text(_first(box, cfg.get("price", GENERIC_PRICE)))
        location = _text(_first(box, cfg.get("location", GENERIC_LOCATION)))
        img_el = _first(box, cfg.get("image", GENERIC_IMAGE))
        img = img_el.get("src") if img_el and img_el.get("src") else None
        a = _first(box, "a[href]")
        href = urljoin(url, a.get("href")) if a and a.get("href") else None
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
    return all_items
