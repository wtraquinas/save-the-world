import json, os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from graph.rag.retriever import retrieve

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "solution_cache.json"

SYSTEM_PROMPT = """You are a UN policy advisor specialising in humanitarian response.
Given a crisis cluster and relevant UN frameworks, propose 3 concrete actionable solutions.

Return ONLY a JSON array of exactly 3 solution objects:
[
  {
    "title": "Short solution title (5-8 words)",
    "description": "2-3 sentence description of the intervention",
    "sdg_alignment": ["SDG 2", "SDG 13"],
    "implementing_bodies": ["WFP", "OCHA"],
    "timeframe": "immediate|short-term|long-term",
    "precedent": "One sentence citing a past successful similar intervention"
  }
]

Be specific, cite UN frameworks where possible, and draw on the provided context.
No preamble, no markdown, only the JSON array."""


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def _save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def solution_node(state: AgentState) -> dict:
    """
    For each detected pattern/hotspot, proposes 3 UN-grounded solutions.
    Uses RAG to ground proposals in real UN frameworks.
    One LLM call per pattern, all cached.
    """
    trend_report = state.get("trend_report", {})
    patterns = trend_report.get("patterns", [])
    events = state.get("summarized_events") or state.get("classified_events", [])

    # If no patterns, generate solutions for crisis-level events directly
    if not patterns:
        crisis_events = [e for e in events if e.get("urgency") == "crisis"]
        if crisis_events:
            patterns = [{
                "title": f"Crisis cluster: {crisis_events[0].get('category','unknown')}",
                "description": f"{len(crisis_events)} crisis-level events detected",
                "affected_regions": list(set(e.get("region","") for e in crisis_events)),
                "categories": list(set(e.get("category","") for e in crisis_events)),
                "event_ids": [e["id"] for e in crisis_events],
                "severity": "rising",
            }]

    cache = _load_cache()
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    all_proposals = []

    for pattern in patterns:
        cache_key = pattern["title"].lower().replace(" ", "_")[:60]

        if cache_key in cache:
            print(f"[SOLUTION] ✅ Cache hit: {pattern['title']}")
            all_proposals.append({"pattern": pattern["title"], "solutions": cache[cache_key]})
            continue

        print(f"[SOLUTION] 🧠 Generating solutions for: {pattern['title']}")

        # RAG: retrieve relevant UN frameworks for this pattern
        rag_query = f"{pattern['title']} {' '.join(pattern.get('categories', []))} {' '.join(pattern.get('affected_regions', []))}"
        try:
            context_chunks = retrieve(rag_query, k=3)
            context = "\n---\n".join(context_chunks)
        except Exception:
            context = "UN SDG framework, humanitarian response principles, OCHA coordination."

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""CRISIS PATTERN:
Title: {pattern['title']}
Description: {pattern['description']}
Affected regions: {', '.join(pattern.get('affected_regions', []))}
Crisis categories: {', '.join(pattern.get('categories', []))}
Severity trend: {pattern.get('severity', 'unknown')}
Events involved: {len(pattern.get('event_ids', []))}

RELEVANT UN FRAMEWORKS & CONTEXT:
{context}

Propose 3 concrete solutions:"""),
        ]

        try:
            response = llm.invoke(messages)
            raw = response.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            solutions = json.loads(raw)
            cache[cache_key] = solutions
            _save_cache(cache)

            all_proposals.append({"pattern": pattern["title"], "solutions": solutions})
            print(f"[SOLUTION] ✅ {len(solutions)} solutions generated for {pattern['title']}")

        except Exception as e:
            print(f"[SOLUTION] ⚠️ Failed for {pattern['title']}: {e}")
            all_proposals.append({
                "pattern": pattern["title"],
                "solutions": [{
                    "title": "Emergency humanitarian response",
                    "description": "Deploy emergency response teams and coordinate with local authorities.",
                    "sdg_alignment": ["SDG 16", "SDG 17"],
                    "implementing_bodies": ["OCHA", "UNHCR"],
                    "timeframe": "immediate",
                    "precedent": "Applied successfully in multiple humanitarian emergencies.",
                }]
            })

    print(f"[SOLUTION] 🌍 {len(all_proposals)} solution sets generated")
    return {"solution_proposals": all_proposals}