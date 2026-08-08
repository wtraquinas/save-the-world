import json, os
from pathlib import Path
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "trend_cache.json"

SYSTEM_PROMPT = """You are a UN crisis trend analyst.
Given a batch of classified humanitarian events, identify patterns and produce a trend report.

Return ONLY a JSON object with exactly these keys:
{
  "patterns": [
    {
      "title": "short pattern name",
      "description": "1-2 sentence description of the pattern",
      "affected_regions": ["region1", "region2"],
      "categories": ["conflict", "climate"],
      "event_ids": ["evt_001", "evt_002"],
      "severity": "rising|stable|declining"
    }
  ],
  "forecast": "2-3 sentence forecast of how the global situation may evolve in the next 30 days",
  "hotspots": ["country or region name", ...],
  "dominant_category": "the single most prevalent crisis type today",
  "crisis_count": <number of crisis-level events>,
  "alert_count": <number of alert-level events>
}

Be analytical, precise, and grounded in the data provided. No preamble, no markdown."""


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def _save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

def _make_cache_key(events: list) -> str:
    """Cache key based on event ids + urgencies — changes when data changes."""
    return "_".join(sorted(f"{e['id']}:{e.get('urgency','')}" for e in events))


def trend_node(state: AgentState) -> dict:
    """
    Analyses all classified events in one LLM call.
    Detects patterns, forecasts, identifies hotspots.
    """
    # Use summarized events if available, else classified
    events = state.get("summarized_events") or state.get("classified_events", [])

    cache = _load_cache()
    cache_key = _make_cache_key(events)

    if cache_key in cache:
        print(f"[TREND] ✅ Loaded from cache")
        return {"trend_report": cache[cache_key]}

    print(f"[TREND] 🔍 Analysing {len(events)} events for patterns...")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Build compact event list for the prompt
    events_text = "\n".join(
        f"- id:{e['id']} | {e.get('urgency','?').upper()} | "
        f"{e.get('category','?')} | {e.get('region','?')} | {e.get('country','?')} | "
        f"{e['title']}"
        for e in events
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Analyse these {len(events)} humanitarian events:\n\n{events_text}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        trend_report = json.loads(raw)
        trend_report["generated_at"] = __import__("datetime").datetime.utcnow().isoformat()

        cache[cache_key] = trend_report
        _save_cache(cache)

        print(f"[TREND] ✅ Found {len(trend_report.get('patterns', []))} patterns")
        print(f"[TREND] 🔥 Hotspots: {', '.join(trend_report.get('hotspots', []))}")

    except Exception as e:
        print(f"[TREND] ⚠️ Failed: {e} — returning stub")
        trend_report = {
            "patterns": [],
            "forecast": "Trend analysis unavailable.",
            "hotspots": [],
            "dominant_category": "unknown",
            "crisis_count": sum(1 for e in events if e.get("urgency") == "crisis"),
            "alert_count": sum(1 for e in events if e.get("urgency") == "alert"),
            "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        }

    return {"trend_report": trend_report}