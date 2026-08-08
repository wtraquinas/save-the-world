import json, uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from graph.graph import app_graph
from graph.state import AgentState
from datetime import datetime, timezone

app = FastAPI(title="Save the World — UN AI Situation Room")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://save-the-world-mu.vercel.app",
        "https://*.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_DATA  = Path(__file__).parent / "data" / "mock_events.json"
CACHE_FILE = Path(__file__).parent / "data" / "classifier_cache.json"


@app.get("/health")
def health():
    return {"status": "ok", "message": "UN AI Situation Room is online"}


@app.get("/events")
def get_events():
    """Raw mock events as GeoJSON — used by the map before analysis runs."""
    events = json.loads(MOCK_DATA.read_text())
    # Merge any cached classifications if available
    cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    for e in events:
        if e["id"] in cache:
            e.update({k: cache[e["id"]][k] for k in ("category","urgency","sdg_tags")})
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [e["lng"], e["lat"]]},
            "properties": {k: v for k, v in e.items() if k not in ("lat","lng")},
        }
        for e in events
    ]
    return {"type": "FeatureCollection", "features": features}


@app.post("/analyze")
def run_analysis():
    """Trigger full LangGraph pipeline on mock data."""
    events = json.loads(MOCK_DATA.read_text())
    initial_state: AgentState = {
        "raw_events": events,
        "ingested_events": [],
        "classified_events": [],
        "summarized_events": [],
        "trend_report": None,
        "solution_proposals": [],
        "current_batch": [e["id"] for e in events],
        "errors": [],
        "requires_human_review": False,
        "human_approved": False,
        "run_id": str(uuid.uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    result = app_graph.invoke(initial_state)
    return {
        "run_id": result["run_id"],
        "events_processed": len(result["classified_events"]),
        "crisis_events": [
            {"id": e["id"], "title": e["title"], "urgency": e["urgency"], "category": e["category"]}
            for e in result["classified_events"] if e["urgency"] == "crisis"
        ],
        "trend_report": result["trend_report"],
    }

@app.get("/events/summarized")
def get_summarized_events():
    """
    Returns GeoJSON with full classifications + AI summaries merged in.
    The frontend calls this for the pin popup drawer.
    """
    events = json.loads(MOCK_DATA.read_text())

    # Merge classifier cache
    clf_cache_path = Path(__file__).parent / "data" / "classifier_cache.json"
    clf_cache = json.loads(clf_cache_path.read_text()) if clf_cache_path.exists() else {}

    # Merge summary cache
    sum_cache_path = Path(__file__).parent / "data" / "summary_cache.json"
    sum_cache = json.loads(sum_cache_path.read_text()) if sum_cache_path.exists() else {}

    for e in events:
        if e["id"] in clf_cache:
            hit = clf_cache[e["id"]]
            e.update({"category": hit.get("category","other"),
                       "urgency":  hit.get("urgency","watch"),
                       "sdg_tags": hit.get("sdg_tags",[])})
        if e["id"] in sum_cache:
            e["summary"] = sum_cache[e["id"]]

    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [e["lng"], e["lat"]]},
            "properties": {k: v for k, v in e.items() if k not in ("lat","lng")},
        }
        for e in events
    ]
    return {"type": "FeatureCollection", "features": features}