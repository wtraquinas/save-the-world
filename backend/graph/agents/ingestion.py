import json, hashlib
from pathlib import Path
from graph.state import AgentState, NewsEvent

# Fallback coords for countries not in pycountry_convert
COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    "BD": (23.68, 90.35), "SD": (15.55, 32.53), "GR": (39.07, 21.82),
    "CD": (-4.03, 21.75), "SO": (5.15, 46.20), "MA": (31.79, -7.09),
    "BR": (-14.23, -51.93), "MM": (21.91, 95.96), "NO": (60.47, 8.47),
    "PS": (31.95, 35.23), "HT": (18.97, -72.28), "UA": (48.38, 31.17),
    "PK": (30.38, 69.35), "ID": (-0.79, 113.92), "ET": (9.14, 40.49),
    "PH": (12.88, 121.77), "YE": (15.55, 48.52), "ML": (17.57, -3.99),
    "VE": (6.42, -66.59), "IN": (20.59, 78.96),
}

def _event_hash(title: str) -> str:
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def ingest_node(state: AgentState) -> dict:
    """
    Reads raw_events, deduplicates by title hash,
    normalises all fields, fills missing lat/lng from country lookup.
    """
    raw = state.get("raw_events", [])
    seen: set[str] = set()
    ingested: list[NewsEvent] = []

    for evt in raw:
        h = _event_hash(evt.get("title", ""))
        if h in seen:
            print(f"[INGEST] Duplicate skipped: {evt.get('title','')[:60]}")
            continue
        seen.add(h)

        # Fill coords from country if missing
        lat = evt.get("lat") or 0.0
        lng = evt.get("lng") or 0.0
        country = evt.get("country", "")
        if (lat == 0.0 and lng == 0.0) and country in COUNTRY_COORDS:
            lat, lng = COUNTRY_COORDS[country]

        clean: NewsEvent = {
            "id":           evt.get("id", h[:8]),
            "title":        evt.get("title", "").strip(),
            "source":       evt.get("source", "Unknown"),
            "url":          evt.get("url", ""),
            "published_at": evt.get("published_at", ""),
            "body":         evt.get("body", "").strip(),
            "country":      country,
            "region":       evt.get("region", ""),
            "lat":          lat,
            "lng":          lng,
            # These get filled by later agents
            "category":     None,
            "urgency":      None,
            "summary":      None,
            "sdg_tags":     [],
            "trend_signal": None,
            "solutions":    [],
        }
        ingested.append(clean)

    print(f"[INGEST] ✅ {len(ingested)} events ingested ({len(raw)-len(ingested)} duplicates removed)")
    return {"ingested_events": ingested}