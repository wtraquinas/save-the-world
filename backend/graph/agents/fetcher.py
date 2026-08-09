"""
Real-world data ingestion from:
- GDELT 2.0 GKG (Global Knowledge Graph) — free, no auth, geo-tagged events
- UN News RSS — official UN headlines
- ReliefWeb RSS — humanitarian situation reports
"""
import json, hashlib, httpx
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

LIVE_CACHE = Path(__file__).parent.parent.parent / "data" / "live_events.json"

# GDELT event themes we care about — maps to our crisis categories
GDELT_THEME_MAP = {
    "NATURAL_DISASTER":  "climate",
    "FLOOD":             "climate",
    "DROUGHT":           "climate",
    "EARTHQUAKE":        "climate",
    "FIRE":              "climate",
    "CONFLICT":          "conflict",
    "WAR":               "conflict",
    "REBEL":             "conflict",
    "KILL":              "conflict",
    "FOOD_SECURITY":     "famine",
    "HUNGER":            "famine",
    "FAMINE":            "famine",
    "DISEASE":           "disease",
    "EPIDEMIC":          "disease",
    "OUTBREAK":          "disease",
    "REFUGEE":           "displacement",
    "DISPLACED":         "displacement",
    "MIGRATION":         "displacement",
}

RSS_FEEDS = [
    {
        "url":    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "source": "UN News",
        "region": "Global",
    },
    {
        "url":    "https://reliefweb.int/updates/rss.xml",
        "source": "ReliefWeb",
        "region": "Global",
    },
]


def _make_id(title: str) -> str:
    return "live_" + hashlib.md5(title.lower().strip().encode()).hexdigest()[:8]


def fetch_gdelt_events(max_events: int = 10) -> list[dict]:
    """
    Fetches recent events from GDELT 2.0 GKG CSV (last 15 minutes).
    Filters to humanitarian themes, returns geo-tagged events.
    Free, no auth, updates every 15 minutes.
    """
    print("[FETCHER] 🌐 Fetching GDELT events...")
    events = []

    try:
        # GDELT GKG last file list
        r = httpx.get(
            "http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
            timeout=15
        )
        lines = r.text.strip().split("\n")

        # Find the GKG CSV URL
        gkg_url = None
        for line in lines:
            if "gkg.csv.zip" in line:
                gkg_url = line.split(" ")[-1].strip()
                break

        if not gkg_url:
            print("[FETCHER] ⚠️ No GKG URL found")
            return []

        # Download and parse GKG zip
        import io, zipfile, csv

        print(f"[FETCHER] 📥 Downloading GKG: {gkg_url}")
        r = httpx.get(gkg_url, timeout=30, follow_redirects=True)

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            fname = z.namelist()[0]
            with z.open(fname) as f:
                reader = csv.reader(
                    io.TextIOWrapper(f, encoding="utf-8", errors="ignore"),
                    delimiter="\t"
                )
                for i, row in enumerate(reader):
                    if i > 2000:   # scan first 2000 rows only
                        break
                    if len(row) < 10:
                        continue

                    try:
                        themes_raw = row[7] if len(row) > 7 else ""
                        locations  = row[9] if len(row) > 9 else ""
                        title      = row[4] if len(row) > 4 else ""

                        if not title or not locations:
                            continue

                        # Match themes to our categories
                        category = None
                        for theme_key, cat in GDELT_THEME_MAP.items():
                            if theme_key in themes_raw.upper():
                                category = cat
                                break

                        if not category:
                            continue

                        # Parse first location for lat/lng
                        loc_parts = locations.split(";")[0].split("#")
                        if len(loc_parts) < 5:
                            continue

                        lat = float(loc_parts[3]) if loc_parts[3] else 0.0
                        lng = float(loc_parts[4]) if loc_parts[4] else 0.0
                        country = loc_parts[2][:2].upper() if loc_parts[2] else "UN"
                        region  = loc_parts[1] if loc_parts[1] else "Global"

                        if lat == 0.0 and lng == 0.0:
                            continue

                        event = {
                            "id":           _make_id(title),
                            "title":        title[:200],
                            "source":       "GDELT",
                            "url":          row[4] if len(row) > 4 else "",
                            "published_at": datetime.now(timezone.utc).isoformat(),
                            "body":         f"GDELT event: {themes_raw[:300]}",
                            "country":      country,
                            "region":       region,
                            "lat":          lat,
                            "lng":          lng,
                            "category":     category,
                            "urgency":      None,
                            "summary":      None,
                            "sdg_tags":     [],
                            "trend_signal": None,
                            "solutions":    [],
                        }
                        events.append(event)

                        if len(events) >= max_events:
                            break

                    except (ValueError, IndexError):
                        continue

    except Exception as e:
        print(f"[FETCHER] ⚠️ GDELT fetch failed: {e}")

    print(f"[FETCHER] ✅ GDELT: {len(events)} events fetched")
    return events


def fetch_rss_events(max_per_feed: int = 5) -> list[dict]:
    """
    Fetches latest headlines from UN News and ReliefWeb RSS feeds.
    Geo-tags by detecting country names in titles/descriptions.
    """
    print("[FETCHER] 📡 Fetching RSS feeds...")
    events = []

    # Simple country name → coords lookup for RSS geo-tagging
    COUNTRY_HINTS = {
        "ukraine":      ("UA", "Eastern Europe",    48.38, 31.17),
        "gaza":         ("PS", "Middle East",        31.35, 34.30),
        "sudan":        ("SD", "Eastern Africa",     15.55, 32.53),
        "somalia":      ("SO", "Eastern Africa",      5.15, 46.20),
        "haiti":        ("HT", "Caribbean",          18.97,-72.28),
        "myanmar":      ("MM", "Southeast Asia",     21.91, 95.96),
        "ethiopia":     ("ET", "Eastern Africa",      9.14, 40.49),
        "afghanistan":  ("AF", "South Asia",         33.93, 67.71),
        "yemen":        ("YE", "Middle East",        15.55, 48.52),
        "syria":        ("SY", "Middle East",        34.80, 38.99),
        "bangladesh":   ("BD", "South Asia",         23.68, 90.35),
        "pakistan":     ("PK", "South Asia",         30.38, 69.35),
        "drc":          ("CD", "Central Africa",     -4.03, 21.75),
        "congo":        ("CD", "Central Africa",     -4.03, 21.75),
        "libya":        ("LY", "North Africa",       26.33, 17.23),
        "mali":         ("ML", "West Africa",        17.57, -3.99),
        "mozambique":   ("MZ", "Southern Africa",   -18.67, 35.53),
        "venezuela":    ("VE", "South America",       6.42,-66.59),
        "indonesia":    ("ID", "Southeast Asia",     -0.79,113.92),
        "philippines":  ("PH", "Southeast Asia",     12.88,121.77),
    }

    CATEGORY_HINTS = {
        "flood": "climate", "earthquake": "climate", "hurricane": "climate",
        "drought": "climate", "wildfire": "climate", "cyclone": "climate",
        "conflict": "conflict", "war": "conflict", "attack": "conflict",
        "fighting": "conflict", "militia": "conflict", "ceasefire": "conflict",
        "hunger": "famine", "food": "famine", "famine": "famine",
        "cholera": "disease", "outbreak": "disease", "epidemic": "disease",
        "malaria": "disease", "measles": "disease",
        "refugee": "displacement", "displaced": "displacement", "flee": "displacement",
    }

    for feed in RSS_FEEDS:
        try:
            r = httpx.get(feed["url"], timeout=15, follow_redirects=True)
            root = ET.fromstring(r.content)
            items = root.findall(".//item")[:max_per_feed]

            for item in items:
                title = item.findtext("title", "").strip()
                desc  = item.findtext("description", "").strip()
                link  = item.findtext("link", "").strip()
                pub   = item.findtext("pubDate", "").strip()

                if not title:
                    continue

                combined = (title + " " + desc).lower()

                # Geo-tag by country mention
                lat, lng, country, region = 0.0, 0.0, "GL", "Global"
                for keyword, (c, reg, la, ln) in COUNTRY_HINTS.items():
                    if keyword in combined:
                        country, region, lat, lng = c, reg, la, ln
                        break

                if lat == 0.0:
                    continue   # skip events we can't place on map

                # Categorise by keyword
                category = "other"
                for keyword, cat in CATEGORY_HINTS.items():
                    if keyword in combined:
                        category = cat
                        break

                events.append({
                    "id":           _make_id(title),
                    "title":        title[:200],
                    "source":       feed["source"],
                    "url":          link,
                    "published_at": pub or datetime.now(timezone.utc).isoformat(),
                    "body":         desc[:500],
                    "country":      country,
                    "region":       region,
                    "lat":          lat,
                    "lng":          lng,
                    "category":     category,
                    "urgency":      None,
                    "summary":      None,
                    "sdg_tags":     [],
                    "trend_signal": None,
                    "solutions":    [],
                })

        except Exception as e:
            print(f"[FETCHER] ⚠️ RSS {feed['source']} failed: {e}")

    print(f"[FETCHER] ✅ RSS: {len(events)} events fetched")
    return events


def fetch_live_events(max_events: int = 15) -> list[dict]:
    """
    Combines GDELT + RSS, deduplicates, saves to live_events.json.
    Falls back to mock data if both fail.
    """
    all_events = []

    gdelt = fetch_gdelt_events(max_events=max_events // 2)
    all_events.extend(gdelt)

    rss = fetch_rss_events(max_per_feed=4)
    all_events.extend(rss)

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
        print(f"[FETCHER] 💾 Saved {len(unique)} live events to cache")
    else:
        print("[FETCHER] ⚠️ No live events — pipeline will use mock data")

    return unique