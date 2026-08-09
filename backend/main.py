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
    """
    Streams events one by one to connected clients.
    On connect: replays all cached events immediately.
    Then keeps connection open for future pushes.
    """
    await manager.connect(websocket)
    try:
        # Replay existing events on connect so the map populates instantly
        events = json.loads(MOCK_DATA.read_text())
        clf    = json.loads(CLF_CACHE.read_text()) if CLF_CACHE.exists() else {}
        sums   = json.loads(SUM_CACHE.read_text()) if SUM_CACHE.exists() else {}

        for i, e in enumerate(events):
            if e["id"] in clf:
                e.update(clf[e["id"]])
            if e["id"] in sums:
                e["summary"] = sums[e["id"]]

            await websocket.send_json({"type": "event", "data": e})
            await asyncio.sleep(0.3)   # stagger so pins animate in one by one

        await websocket.send_json({"type": "ready", "data": {"count": len(events)}})

        # Keep alive — wait for disconnect
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/analyze")
async def run_analysis():
    """Runs full pipeline and broadcasts each classified event via WebSocket."""
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

    # Broadcast each processed event to all connected WebSocket clients
    processed = result.get("summarized_events") or result.get("classified_events", [])
    for e in processed:
        await manager.broadcast({"type": "event_updated", "data": e})

    # Broadcast trend report
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
    }


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