import json, os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState, NewsEvent, CrisisCategory, UrgencyLevel

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "classifier_cache.json"

SYSTEM_PROMPT = """You are a UN crisis intelligence analyst.
Classify each news event and return ONLY a JSON array — no preamble, no markdown, no explanation.

Each item must have exactly these keys:
  "id"       : string  (the original event id)
  "category" : one of ["conflict","climate","famine","disease","displacement","other"]
  "urgency"  : one of ["watch","alert","crisis"]
  "sdg_tags" : array of strings from ["SDG 1","SDG 2","SDG 3","SDG 6","SDG 10","SDG 11","SDG 13","SDG 16","SDG 17"]

Urgency guide:
  crisis  = immediate threat to life, mass casualties, acute emergency
  alert   = deteriorating situation, high risk of escalation
  watch   = developing situation, monitoring required

Return ONLY the JSON array. No other text."""

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def _save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

def classify_node(state: AgentState) -> dict:
    """
    Classifies all ingested events via a single batched LLM call.
    Results are cached by event id — re-running never re-classifies the same event.
    """
    events = state.get("ingested_events", [])
    cache = _load_cache()

    # Split into cached vs needs classification
    to_classify = [e for e in events if e["id"] not in cache]
    already_cached = [e for e in events if e["id"] in cache]

    print(f"[CLASSIFY] {len(already_cached)} from cache, {len(to_classify)} need LLM call")

    if to_classify:
        llm = ChatOpenAI(
            model="gpt-4o-mini",      # cheap + fast, plenty good for classification
            temperature=0,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Build the batch prompt — ONE call for all events
        events_text = "\n".join(
            f'- id: "{e["id"]}" | title: "{e["title"]}" | body excerpt: "{e["body"][:200]}"'
            for e in to_classify
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Classify these events:\n\n{events_text}"),
        ]

        try:
            response = llm.invoke(messages)
            raw = response.content.strip()

            # Strip markdown fences if model adds them despite instructions
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            classifications: list[dict] = json.loads(raw)

            # Store in cache
            for item in classifications:
                cache[item["id"]] = item
            _save_cache(cache)

            print(f"[CLASSIFY] ✅ LLM classified {len(classifications)} events (1 API call)")

        except Exception as e:
            print(f"[CLASSIFY] ⚠️ LLM call failed: {e} — falling back to stub")
            for e_item in to_classify:
                cache[e_item["id"]] = {
                    "id": e_item["id"],
                    "category": "other",
                    "urgency": "watch",
                    "sdg_tags": [],
                }
            _save_cache(cache)

    # Merge classifications back into events
    classified: list[NewsEvent] = []
    for event in events:
        hit = cache.get(event["id"], {})
        classified.append({
            **event,
            "category": hit.get("category", "other"),
            "urgency":  hit.get("urgency", "watch"),
            "sdg_tags": hit.get("sdg_tags", []),
        })

    crisis_count = sum(1 for e in classified if e["urgency"] == "crisis")
    print(f"[CLASSIFY] 🚨 {crisis_count} crisis-level events detected")
    return {"classified_events": classified}