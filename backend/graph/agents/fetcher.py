"""
Real-world data ingestion from:
- GDELT Events API (lightweight JSON, no zip download)
- UN News RSS
- ReliefWeb API (JSON, much more reliable than RSS)
"""
import json, hashlib, httpx
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

LIVE_CACHE = Path(__file__).parent.parent.parent / "data" / "live_events.json"

CATEGORY_HINTS = {
    "flood": "climate", "earthquake": "climate", "hurricane": "climate",
    "drought": "climate", "wildfire": "climate", "cyclone": "climate",
    "storm": "climate", "tsunami": "climate", "volcano": "climate",
    "conflict": "conflict", "war": "conflict", "attack": "conflict",
    "fighting": "conflict", "militia": "conflict", "ceasefire": "conflict",
    "violence": "conflict", "battle": "conflict", "troops": "conflict",
    "hunger": "famine", "food": "famine", "famine": "famine",
    "malnutrition": "famine", "starvation": "famine", "crops": "famine",
    "cholera": "disease", "outbreak": "disease", "epidemic": "disease",
    "malaria": "disease", "measles": "disease", "mpox": "disease",
    "dengue": "disease", "virus": "disease", "pandemic": "disease",
    "refugee": "displacement", "displaced": "displacement", "flee": "displacement",
    "asylum": "displacement", "migration": "displacement", "evacuation": "displacement",
}

COUNTRY_COORDS = {
    "Ukraine":      ("UA", "Eastern Europe",     48.38,  31.17),
    "Gaza":         ("PS", "Middle East",         31.35,  34.30),
    "Sudan":        ("SD", "Eastern Africa",      15.55,  32.53),
    "South Sudan":  ("SS", "Eastern Africa",       6.87,  31.57),
    "Somalia":      ("SO", "Eastern Africa",       5.15,  46.20),
    "Haiti":        ("HT", "Caribbean",           18.97, -72.28),
    "Myanmar":      ("MM", "Southeast Asia",      21.91,  95.96),
    "Ethiopia":     ("ET", "Eastern Africa",       9.14,  40.49),
    "Afghanistan":  ("AF", "South Asia",          33.93,  67.71),
    "Yemen":        ("YE", "Middle East",         15.55,  48.52),
    "Syria":        ("SY", "Middle East",         34.80,  38.99),
    "Bangladesh":   ("BD", "South Asia",          23.68,  90.35),
    "Pakistan":     ("PK", "South Asia",          30.38,  69.35),
    "Congo":        ("CD", "Central Africa",      -4.03,  21.75),
    "DRC":          ("CD", "Central Africa",      -4.03,  21.75),
    "Libya":        ("LY", "North Africa",        26.33,  17.23),
    "Mali":         ("ML", "West Africa",         17.57,  -3.99),
    "Mozambique":   ("MZ", "Southern Africa",    -18.67,  35.53),
    "Venezuela":    ("VE", "South America",        6.42, -66.59),
    "Indonesia":    ("ID", "Southeast Asia",      -0.79, 113.92),
    "Philippines":  ("PH", "Southeast Asia",      12.88, 121.77),
    "Nigeria":      ("NG", "West Africa",          9.08,   8.68),
    "Niger":        ("NE", "West Africa",         17.61,   8.08),
    "Burkina Faso": ("BF", "West Africa",         12.36,  -1.53),
    "Chad":         ("TD", "Central Africa",      15.45,  18.73),
    "Cameroon":     ("CM", "Central Africa",       3.85,  11.50),
    "Iraq":         ("IQ", "Middle East",         33.22,  43.68),
    "Lebanon":      ("LB", "Middle East",         33.85,  35.86),
    "Colombia":     ("CO", "South America",        4.57, -74.30),
    "Venezuela":    ("VE", "South America",        6.42, -66.59),
    "Brazil":       ("BR", "South America",      -14.23, -51.93),
    "India":        ("IN", "South Asia",          20.59,  78.96),
    "Nepal":        ("NP", "South Asia",          28.39,  84.12),
    "Kenya":        ("KE", "Eastern Africa",      -0.02,  37.91),
    "Tanzania":     ("TZ", "Eastern Africa",      -6.37,  34.89),
    "Malawi":       ("MW", "Southern Africa",    -13.25,  34.30),
    "Zimbabwe":     ("ZW", "Southern Africa",    -19.01,  29.15),
    "Madagascar":   ("MG", "Southern Africa",    -18.77,  46.87),
    "Morocco":      ("MA", "North Africa",        31.79,  -7.09),
    "Tunisia":      ("TN", "North Africa",        33.89,   9.54),
    "Greece":       ("GR", "Southern Europe",     39.07,  21.82),
    "Turkey":       ("TR", "Middle East",         38.96,  35.24),
    "Iran":         ("IR", "Middle East",         32.43,  53.69),
}


def _make_id(title: str) -> str:
    return "live_" + hashlib.md5(title.lower().strip().encode()).hexdigest()[:8]


def _categorise(text: str) -> str:
    text = text.lower()
    for keyword, cat in CATEGORY_HINTS.items():
        if keyword in text:
            return cat
    return "other"


def _geo_tag(text: str) -> tuple | None:
    """Find first country mention in text, return (code, region, lat, lng)."""
    for country, info in COUNTRY_COORDS.items():
        if country.lower() in text.lower():
            return info
    return None


def fetch_gdelt_events(max_events: int = 8) -> list[dict]:
    """
    Uses GDELT DOC 2.0 API — lightweight JSON search, no zip download.
    Searches for humanitarian keywords in last 24h of news.
    """
    print("[FETCHER] 🌐 Fetching GDELT via DOC API...")
    events = []

    queries = [
        "humanitarian crisis",
        "flood displaced",
        "famine hunger",
        "conflict civilians",
        "disease outbreak",
    ]

    seen_ids = set()

    for query in queries:
        if len(events) >= max_events:
            break
        try:
            r = httpx.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params={
                    "query":      query,
                    "mode":       "artlist",
                    "maxrecords": 5,
                    "format":     "json",
                    "timespan":   "24h",
                    "sort":       "hybridrel",
                },
                timeout=15,
            )
            data = r.json()
            articles = data.get("articles", [])

            for article in articles:
                title   = article.get("title", "").strip()
                url     = article.get("url", "")
                source  = article.get("domain", "GDELT")
                seendate = article.get("seendate", "")

                if not title:
                    continue

                geo = _geo_tag(title)
                if not geo:
                    continue

                country, region, lat, lng = geo
                event_id = _make_id(title)

                if event_id in seen_ids:
                    continue
                seen_ids.add(event_id)

                events.append({
                    "id":           event_id,
                    "title":        title[:200],
                    "source":       source,
                    "url":          url,
                    "published_at": seendate or datetime.now(timezone.utc).isoformat(),
                    "body":         f"Reported by {source}. Query: {query}.",
                    "country":      country,
                    "region":       region,
                    "lat":          lat,
                    "lng":          lng,
                    "category":     _categorise(title),
                    "urgency":      None,
                    "summary":      None,
                    "sdg_tags":     [],
                    "trend_signal": None,
                    "solutions":    [],
                })

        except Exception as e:
            print(f"[FETCHER] ⚠️ GDELT query '{query}' failed: {e}")
            continue

    print(f"[FETCHER] ✅ GDELT DOC API: {len(events)} events")
    return events


def fetch_reliefweb_events(max_events: int = 6) -> list[dict]:
    """
    ReliefWeb JSON API — much more reliable than their RSS.
    Returns structured humanitarian reports with country data.
    """
    print("[FETCHER] 📡 Fetching ReliefWeb API...")
    events = []

    try:
        r = httpx.post(
            "https://api.reliefweb.int/v1/reports",
            json={
                "appname": "un-ai-situation-room",
                "limit":   max_events,
                "fields": {
                    "include": ["title", "body", "date", "country", "disaster_type", "source"]
                },
                "filter": {
                    "operator": "AND",
                    "conditions": [
                        {"field": "status", "value": "published"},
                    ]
                },
                "sort": ["date:desc"],
            },
            timeout=15,
        )
        data = r.json()

        for item in data.get("data", []):
            fields  = item.get("fields", {})
            title   = fields.get("title", "").strip()
            body    = fields.get("body", "")[:500]
            date    = fields.get("date", {}).get("created", "")
            sources = fields.get("source", [{}])
            source  = sources[0].get("name", "ReliefWeb") if sources else "ReliefWeb"

            countries = fields.get("country", [{}])
            if not countries:
                continue

            country_name = countries[0].get("name", "")
            geo = _geo_tag(country_name) or _geo_tag(title)
            if not geo:
                continue

            country_code, region, lat, lng = geo

            events.append({
                "id":           _make_id(title),
                "title":        title[:200],
                "source":       source,
                "url":          f"https://reliefweb.int/node/{item.get('id','')}",
                "published_at": date or datetime.now(timezone.utc).isoformat(),
                "body":         body,
                "country":      country_code,
                "region":       region,
                "lat":          lat,
                "lng":          lng,
                "category":     _categorise(title + " " + body),
                "urgency":      None,
                "summary":      None,
                "sdg_tags":     [],
                "trend_signal": None,
                "solutions":    [],
            })

    except Exception as e:
        print(f"[FETCHER] ⚠️ ReliefWeb API failed: {e}")

    print(f"[FETCHER] ✅ ReliefWeb: {len(events)} events")
    return events


def fetch_rss_events(max_per_feed: int = 6) -> list[dict]:
    """UN News RSS — now with better geo-tagging."""
    print("[FETCHER] 📰 Fetching UN News RSS...")
    events = []

    try:
        r = httpx.get(
            "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
            timeout=15,
            follow_redirects=True,
        )
        root = ET.fromstring(r.content)
        items = root.findall(".//item")[:max_per_feed]

        for item in items:
            title = item.findtext("title", "").strip()
            desc  = item.findtext("description", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()

            if not title:
                continue

            combined = title + " " + desc
            geo = _geo_tag(combined)
            if not geo:
                continue

            country, region, lat, lng = geo

            events.append({
                "id":           _make_id(title),
                "title":        title[:200],
                "source":       "UN News",
                "url":          link,
                "published_at": pub or datetime.now(timezone.utc).isoformat(),
                "body":         desc[:500],
                "country":      country,
                "region":       region,
                "lat":          lat,
                "lng":          lng,
                "category":     _categorise(combined),
                "urgency":      None,
                "summary":      None,
                "sdg_tags":     [],
                "trend_signal": None,
                "solutions":    [],
            })

    except Exception as e:
        print(f"[FETCHER] ⚠️ UN RSS failed: {e}")

    print(f"[FETCHER] ✅ UN News RSS: {len(events)} events")
    return events


def fetch_live_events(max_events: int = 15) -> list[dict]:
    """Combines all sources, deduplicates, saves to cache."""
    all_events = []

    all_events.extend(fetch_gdelt_events(max_events=6))
    all_events.extend(fetch_reliefweb_events(max_events=6))
    all_events.extend(fetch_rss_events(max_per_feed=6))

    # Deduplicate by id
    seen = set()
    unique = []
    for e in all_events:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)

    unique = unique[:max_events]

    if unique:
        LIVE_CACHE.parent.mkdir(exist_ok=True)
        LIVE_CACHE.write_text(json.dumps(unique, indent=2))
        print(f"[FETCHER] 💾 {len(unique)} live events saved")
    else:
        print("[FETCHER] ⚠️ No live events fetched — mock data will be used")

    return unique