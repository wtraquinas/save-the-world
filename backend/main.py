from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json, uuid, asyncio
from pathlib import Path
from datetime import datetime, timezone
from graph.graph import app_graph
from graph.state import AgentState

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

MOCK_DATA      = Path(__file__).parent / "data" / "mock_events.json"
CLF_CACHE      = Path(__file__).parent / "data" / "classifier_cache.json"
SUM_CACHE      = Path(__file__).parent / "data" / "summary_cache.json"
TREND_CACHE    = Path(__file__).parent / "data" / "trend_cache.json"
SOLUTION_CACHE = Path(__file__).parent / "data" / "solution_cache.json"
LIVE_DATA  = Path(__file__).parent / "data" / "live_events.json"

DEMO_MODE  = True   # ← set False to use real APIs in production


# ── Helper ────────────────────────────────────────────────────────────────────
def _get_events() -> list[dict]:              # ← ADD THIS BLOCK
    if not DEMO_MODE and LIVE_DATA.exists():
        live = json.loads(LIVE_DATA.read_text())
        if live:
            return live
    return json.loads(MOCK_DATA.read_text())


# ── WebSocket connection manager ──────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        print(f"[WS] Client connected. Total: {len(self.active)}")

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)
        print(f"[WS] Client disconnected. Total: {len(self.active)}")

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)

manager = ConnectionManager()


@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Load all caches
        events = json.loads(MOCK_DATA.read_text())
        clf  = json.loads(CLF_CACHE.read_text())  if CLF_CACHE.exists()  else {}
        sums = json.loads(SUM_CACHE.read_text())  if SUM_CACHE.exists()  else {}

        for event in events:
            # Merge classifier results
            if event["id"] in clf:
                hit = clf[event["id"]]
                event["category"] = hit.get("category", "other")
                event["urgency"]  = hit.get("urgency",  "watch")
                event["sdg_tags"] = hit.get("sdg_tags", [])
            else:
                event["category"] = "other"
                event["urgency"]  = "watch"
                event["sdg_tags"] = []

            # Merge summary
            if event["id"] in sums:
                event["summary"] = sums[event["id"]]

            await websocket.send_json({"type": "event", "data": event})
            await asyncio.sleep(0.3)

        await websocket.send_json({"type": "ready", "data": {"count": len(events)}})

        # Keep alive
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
def health():
    return {"status": "ok", "message": "UN AI Situation Room is online"}


@app.get("/events")
def get_events():
    events = json.loads(MOCK_DATA.read_text())
    clf  = json.loads(CLF_CACHE.read_text()) if CLF_CACHE.exists() else {}
    sums = json.loads(SUM_CACHE.read_text()) if SUM_CACHE.exists() else {}
    for e in events:
        if e["id"] in clf:
            e.update(clf[e["id"]])
        if e["id"] in sums:
            e["summary"] = sums[e["id"]]
    features = [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [e["lng"], e["lat"]]},
         "properties": {k: v for k, v in e.items() if k not in ("lat", "lng")}}
        for e in events
    ]
    return {"type": "FeatureCollection", "features": features}


@app.get("/events/summarized")
def get_summarized_events():
    return get_events()   # same logic — alias


@app.get("/trends")
def get_trends():
    if not TREND_CACHE.exists():
        return {"message": "No trend data yet. Run POST /analyze first."}
    cache = json.loads(TREND_CACHE.read_text())
    if not cache:
        return {"message": "No trend data yet."}
    return max(cache.values(), key=lambda x: x.get("generated_at", ""))


@app.get("/solutions")
def get_solutions():
    if not SOLUTION_CACHE.exists():
        return {"proposals": [], "message": "No solutions yet."}
    cache = json.loads(SOLUTION_CACHE.read_text())
    proposals = [
        {"pattern": k.replace("_", " ").title(), "solutions": v}
        for k, v in cache.items()
    ]
    return {"proposals": proposals, "total": len(proposals)}


@app.get("/mode")
def get_mode():
    return {
        "demo_mode": DEMO_MODE,
        "live_events_available": LIVE_DATA.exists(),
        "live_event_count": len(json.loads(LIVE_DATA.read_text())) if LIVE_DATA.exists() else 0,
    }


@app.post("/ingest")
async def ingest_live():
    """
    Fetches real events from GDELT + UN RSS.
    Saves to live_events.json — picked up by next /analyze call if DEMO_MODE=False.
    """
    from graph.agents.fetcher import fetch_live_events
    try:
        events = fetch_live_events(max_events=15)
        # Broadcast new events to WebSocket clients
        for e in events:
            await manager.broadcast({"type": "event", "data": e})
        return {
            "status": "ok",
            "fetched": len(events),
            "sources": list(set(e["source"] for e in events)),
        }
    except Exception as ex:
        return {"status": "error", "message": str(ex)}


@app.post("/analyze")
async def run_analysis():
    events = _get_events()                        # ← respects DEMO_MODE
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
    processed = result.get("summarized_events") or result.get("classified_events", [])
    for e in processed:
        await manager.broadcast({"type": "event_updated", "data": e})
    if result.get("trend_report"):
        await manager.broadcast({"type": "trend_updated", "data": result["trend_report"]})
    trend = result.get("trend_report", {})
    return {
        "run_id":              result["run_id"],
        "events_processed":    len(processed),
        "crisis_count":        trend.get("crisis_count", 0),
        "alert_count":         trend.get("alert_count", 0),
        "hotspots":            trend.get("hotspots", []),
        "dominant_category":   trend.get("dominant_category", ""),
        "patterns_found":      len(trend.get("patterns", [])),
        "solutions_generated": len(result.get("solution_proposals", [])),
        "forecast":            trend.get("forecast", ""),
        "demo_mode":           DEMO_MODE,
    }


# Add this temporary debug endpoint to backend/main.py

@app.get("/debug/ingest")
async def debug_ingest():
    """Shows exactly what each data source returns and any errors."""
    from graph.agents.fetcher import (
        fetch_gdelt_events,
        fetch_reliefweb_events,
        fetch_rss_events,
    )
    import traceback

    results = {}

    # Test GDELT
    try:
        gdelt = fetch_gdelt_events(max_events=3)
        results["gdelt"] = {
            "status": "ok",
            "count": len(gdelt),
            "sample": gdelt[0]["title"] if gdelt else None,
        }
    except Exception as e:
        results["gdelt"] = {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    # Test ReliefWeb
    try:
        rw = fetch_reliefweb_events(max_events=3)
        results["reliefweb"] = {
            "status": "ok",
            "count": len(rw),
            "sample": rw[0]["title"] if rw else None,
        }
    except Exception as e:
        results["reliefweb"] = {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    # Test UN RSS
    try:
        rss = fetch_rss_events(max_per_feed=3)
        results["un_rss"] = {
            "status": "ok",
            "count": len(rss),
            "sample": rss[0]["title"] if rss else None,
        }
    except Exception as e:
        results["un_rss"] = {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    return results
