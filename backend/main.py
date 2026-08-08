from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from graph.graph import app_graph
from graph.state import AgentState
import json, uuid
from datetime import datetime, timezone
from pathlib import Path

app = FastAPI(title="Save the World — Situation Room API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://save-the-world.vercel.app",
        "https://*.vercel.app",   # covers preview deployments
    ],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_DATA = Path(__file__).parent / "data" / "mock_events.json"


@app.get("/health")
def health():
    return {"status": "ok", "message": "UN AI Situation Room is online"}


@app.get("/events")
def get_events():
    """Return raw mock events as GeoJSON FeatureCollection."""
    events = json.loads(MOCK_DATA.read_text())
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [e["lng"], e["lat"]]},
            "properties": {k: v for k, v in e.items() if k not in ("lat", "lng")},
        }
        for e in events
    ]
    return {"type": "FeatureCollection", "features": features}


@app.post("/analyze")
def run_analysis():
    """Trigger the full LangGraph pipeline on mock data."""
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
        "events_processed": len(result["summarized_events"]),
        "trend_report": result["trend_report"],
        "solutions": result["solution_proposals"],
    }