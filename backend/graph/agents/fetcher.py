# backend/graph/agents/fetcher.py — full replacement

import json, hashlib, httpx
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

LIVE_CACHE = Path(__file__).parent.parent.parent / "data" / "live_events.json"

CATEGORY_HINTS = {
    "flood": "climate", "earthquake": "climate", "hurricane": "climate",
    "drought": "climate", "wildfire": "climate", "cyclone": "climate",
    "storm": "climate", "tsunami": "climate", "volcano": "climate",
    "fire": "climate", "heatwave": "climate", "landslide": "climate",
    "conflict": "conflict", "war": "conflict", "attack": "conflict",
    "fighting": "conflict", "militia": "conflict", "ceasefire": "conflict",
    "violence": "conflict", "battle": "conflict", "troops": "conflict",
    "shelling": "conflict", "armed": "conflict", "killed": "conflict",
    "hunger": "famine", "food": "famine", "famine": "famine",
    "malnutrition": "famine", "starvation": "famine", "harvest": "famine",
    "cholera": "disease", "outbreak": "disease", "epidemic": "disease",
    "malaria": "disease", "measles": "disease", "mpox": "disease",
    "dengue": "disease", "virus": "disease", "ebola": "disease",
    "refugee": "displacement", "displaced": "displacement", "flee": "displacement",
    "asylum": "displacement", "migration": "displacement", "evacuation": "displacement",
    "stateless": "displacement", "shelter": "displacement",
}

COUNTRY_COORDS = {
    # Common names
    "Ukraine":        ("UA", "Eastern Europe",      48.38,  31.17),
    "Gaza":           ("PS", "Middle East",          31.35,  34.30),
    "Sudan":          ("SD", "Eastern Africa",       15.55,  32.53),
    "South Sudan":    ("SS", "Eastern Africa",        6.87,  31.57),
    "Somalia":        ("SO", "Eastern Africa",        5.15,  46.20),
    "Haiti":          ("HT", "Caribbean",            18.97, -72.28),
    "Myanmar":        ("MM", "Southeast Asia",       21.91,  95.96),
    "Ethiopia":       ("ET", "Eastern Africa",        9.14,  40.49),
    "Afghanistan":    ("AF", "South Asia",           33.93,  67.71),
    "Yemen":          ("YE", "Middle East",          15.55,  48.52),
    "Syria":          ("SY", "Middle East",          34.80,  38.99),
    "Bangladesh":     ("BD", "South Asia",           23.68,  90.35),
    "Pakistan":       ("PK", "South Asia",           30.38,  69.35),
    "Congo":          ("CD", "Central Africa",       -4.03,  21.75),
    "DRC":            ("CD", "Central Africa",       -4.03,  21.75),
    "Libya":          ("LY", "North Africa",         26.33,  17.23),
    "Mali":           ("ML", "West Africa",          17.57,  -3.99),
    "Mozambique":     ("MZ", "Southern Africa",     -18.67,  35.53),
    "Venezuela":      ("VE", "South America",         6.42, -66.59),
    "Indonesia":      ("ID", "Southeast Asia",       -0.79, 113.92),
    "Philippines":    ("PH", "Southeast Asia",       12.88, 121.77),
    "Nigeria":        ("NG", "West Africa",           9.08,   8.68),
    "Niger":          ("NE", "West Africa",          17.61,   8.08),
    "Burkina Faso":   ("BF", "West Africa",          12.36,  -1.53),
    "Chad":           ("TD", "Central Africa",       15.45,  18.73),
    "Cameroon":       ("CM", "Central Africa",        3.85,  11.50),
    "Iraq":           ("IQ", "Middle East",          33.22,  43.68),
    "Lebanon":        ("LB", "Middle East",          33.85,  35.86),
    "Colombia":       ("CO", "South America",         4.57, -74.30),
    "Brazil":         ("BR", "South America",       -14.23, -51.93),
    "India":          ("IN", "South Asia",           20.59,  78.96),
    "Nepal":          ("NP", "South Asia",           28.39,  84.12),
    "Kenya":          ("KE", "Eastern Africa",       -0.02,  37.91),
    "Tanzania":       ("TZ", "Eastern Africa",       -6.37,  34.89),
    "Malawi":         ("MW", "Southern Africa",     -13.25,  34.30),
    "Zimbabwe":       ("ZW", "Southern Africa",     -19.01,  29.15),
    "Madagascar":     ("MG", "Southern Africa",     -18.77,  46.87),
    "Morocco":        ("MA", "North Africa",         31.79,  -7.09),
    "Greece":         ("GR", "Southern Europe",      39.07,  21.82),
    "Turkey":         ("TR", "Middle East",          38.96,  35.24),
    "Iran":           ("IR", "Middle East",          32.43,  53.69),
    "Uganda":         ("UG", "Eastern Africa",        1.37,  32.29),
    "Rwanda":         ("RW", "Central Africa",       -1.94,  29.87),
    "Burundi":        ("BI", "Central Africa",       -3.37,  29.92),
    "Guinea":         ("GN", "West Africa",          11.80, -15.18),
    "Senegal":        ("SN", "West Africa",          14.50, -14.45),
    "Sri Lanka":      ("LK", "South Asia",            7.87,  80.77),
    "Honduras":       ("HN", "Central America",      15.20, -86.24),
    "Guatemala":      ("GT", "Central America",      15.78, -90.23),
    "Mexico":         ("MX", "North America",        23.63, -102.55),
    "Peru":           ("PE", "South America",        -9.19, -75.02),
    "Bolivia":        ("BO", "South America",       -16.29, -63.59),
    "Ecuador":        ("EC", "South America",        -1.83, -78.18),
    "Zambia":         ("ZM", "Southern Africa",     -13.13,  27.85),
    "Jordan":         ("JO", "Middle East",          30.59,  36.24),
    "Tunisia":        ("TN", "North Africa",         33.89,   9.54),
    "Algeria":        ("DZ", "North Africa",         28.03,   1.66),
    "Egypt":          ("EG", "North Africa",         26.82,  30.80),
    "Eritrea":        ("ER", "Eastern Africa",       15.18,  39.78),
    "Djibouti":       ("DJ", "Eastern Africa",       11.83,  42.59),
    "Central African Republic": ("CF", "Central Africa", 6.61, 20.94),
    "Papua New Guinea":         ("PG", "Pacific",       -6.31, 143.96),
    # Official/alternate API names
    "Syrian Arab Republic":         ("SY", "Middle East",    34.80,  38.99),
    "Democratic Republic of Congo": ("CD", "Central Africa", -4.03,  21.75),
    "occupied Palestinian":         ("PS", "Middle East",    31.35,  34.30),
    "West Bank":                    ("PS", "Middle East",    31.35,  34.30),
    "DR Congo":                     ("CD", "Central Africa", -4.03,  21.75),
    "Republic of Sudan":            ("SD", "Eastern Africa", 15.55,  32.53),
}

REGION_COORDS = {
    "horn of africa":  ("SO", "Eastern Africa",   5.15,  46.20),
    "sahel":           ("ML", "West Africa",      17.57,  -3.99),
    "great lakes":     ("CD", "Central Africa",   -4.03,  21.75),
    "west africa":     ("NG", "West Africa",       9.08,   8.68),
    "central africa":  ("CD", "Central Africa",   -4.03,  21.75),
    "eastern africa":  ("ET", "Eastern Africa",    9.14,  40.49),
    "southern africa": ("MZ", "Southern Africa", -18.67,  35.53),
    "southeast asia":  ("MM", "Southeast Asia",  21.91,  95.96),
    "south asia":      ("PK", "South Asia",       30.38,  69.35),
    "middle east":     ("SY", "Middle East",      34.80,  38.99),
    "caribbean":       ("HT", "Caribbean",        18.97, -72.28),
    "latin america":   ("CO", "South America",     4.57, -74.30),
    "mediterranean":   ("GR", "Southern Europe",  39.07,  21.82),
}

# RSS feeds — all free, no auth, reliable from server environments
RSS_FEEDS = [
    {
        "url":    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "source": "UN News",
    },
    {
        "url":    "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
        "source": "BBC Africa",
    },
    {
        "url":    "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "source": "BBC Middle East",
    },
    {
        "url":    "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
        "source": "BBC Asia",
    },
    {
        "url":    "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
        "source": "BBC Latin America",
    },
    {
        "url":    "https://rss.app/feeds/UN9IKSzDpZqn3gPb.xml",   # AP World News
        "source": "AP News",
    },
]


def _make_id(title: str) -> str:
    return "live_" + hashlib.md5(title.lower().strip().encode()).hexdigest()[:8]


def _categorise(text: str) -> str:
    text = text.lower()
    for keyword, cat in CATEGORY_HINTS.items():
        if keyword in text:
            return cat
    return "other"


def _geo_tag(text: str) -> tuple | None:
    text_lower = text.lower()
    for name, info in COUNTRY_COORDS.items():
        if name.lower() in text_lower:
            return info
    for region, info in REGION_COORDS.items():
        if region in text_lower:
            return info
    return None


def fetch_rss_events(max_per_feed: int = 5) -> list[dict]:
    """
    Fetches from multiple reliable RSS feeds.
    Includes humanitarian-keyword filtering + geo-tagging.
    Falls back to UN HQ coords for ungeo-tagged UN News items.
    """
    print("[FETCHER] 📡 Fetching RSS feeds...")
    all_events = []
    seen_ids: set[str] = set()

    for feed in RSS_FEEDS:
        print(f"[FETCHER]   → {feed['source']}")
        try:
            r = httpx.get(
                feed["url"],
                timeout=12,
                follow_redirects=True,
                headers={"User-Agent": "UN-AI-Situation-Room/1.0"},
            )
            root = ET.fromstring(r.content)
            items = root.findall(".//item")

            feed_count = 0
            for item in items:
                if feed_count >= max_per_feed:
                    break

                title = item.findtext("title", "").strip()
                desc  = item.findtext("description", "").strip()
                link  = item.findtext("link",  "").strip()
                pub   = item.findtext("pubDate", "").strip()

                if not title:
                    continue

                combined = title + " " + desc

                # For BBC/AP — only include humanitarian topics
                is_un = "UN News" in feed["source"]
                if not is_un:
                    if _categorise(combined) == "other":
                        continue

                # Geo-tag
                geo = _geo_tag(combined)
                if geo:
                    country, region, lat, lng = geo
                elif is_un:
                    # UN News items without a country — place at UN HQ
                    country, region, lat, lng = "GL", "Global", 40.75, -73.98
                else:
                    continue   # skip non-UN ungeo-tagged items

                event_id = _make_id(title)
                if event_id in seen_ids:
                    continue
                seen_ids.add(event_id)

                all_events.append({
                    "id":           event_id,
                    "title":        title[:200],
                    "source":       feed["source"],
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
                feed_count += 1

        except Exception as e:
            print(f"[FETCHER] ⚠️ {feed['source']} failed: {e}")
            continue

    print(f"[FETCHER] ✅ Total RSS events: {len(all_events)}")
    return all_events


def fetch_live_events(max_events: int = 15) -> list[dict]:
    """Main entry point — RSS only, reliable from any server environment."""
    events = fetch_rss_events(max_per_feed=5)

    # Deduplicate
    seen = set()
    unique = []
    for e in events:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)

    unique = unique[:max_events]

    if unique:
        LIVE_CACHE.parent.mkdir(exist_ok=True)
        LIVE_CACHE.write_text(json.dumps(unique, indent=2))
        print(f"[FETCHER] 💾 {len(unique)} live events saved")
    else:
        print("[FETCHER] ⚠️ No live events — mock data will be used")

    return unique