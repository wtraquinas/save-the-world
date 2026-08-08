from langgraph.graph import StateGraph, END
from graph.state import AgentState
import uuid
from datetime import datetime, timezone


# ── Node stubs ────────────────────────────────────────────────────────────────
# Each node is a plain Python function: receives state, returns partial update.
# Today these just print and pass through. Real logic lands Day 2–4.

def ingest_node(state: AgentState) -> dict:
    """
    Day 2: fetch from APIs/RSS, deduplicate, geo-tag.
    Today: pass raw_events straight through.
    """
    print(f"[INGEST] Processing {len(state['raw_events'])} events")
    return {"ingested_events": state["raw_events"]}


def classify_node(state: AgentState) -> dict:
    """
    Day 2: LLM call to assign category + urgency to each event.
    Today: stub — mark everything 'watch' / 'other'.
    """
    print(f"[CLASSIFY] Classifying {len(state['ingested_events'])} events")
    stubbed = []
    for event in state["ingested_events"]:
        stubbed.append({**event, "category": "other", "urgency": "watch"})
    return {"classified_events": stubbed}


def summarize_node(state: AgentState) -> dict:
    """
    Day 3: RAG retrieval + LLM summarization grounded in UN docs.
    Today: stub — copy title as placeholder summary.
    """
    print(f"[SUMMARIZE] Summarizing {len(state['classified_events'])} events")
    summarized = []
    for event in state["classified_events"]:
        summarized.append({**event, "summary": f"[STUB] {event['title']}"})
    return {"summarized_events": summarized}


def trend_node(state: AgentState) -> dict:
    """
    Day 4: detect patterns across events, produce trend report.
    Today: stub — return empty report.
    """
    print("[TREND] Analysing trends (stub)")
    return {"trend_report": {"patterns": [], "forecast": "No trend data yet."}}


def solution_node(state: AgentState) -> dict:
    """
    Day 4: propose SDG-grounded solutions for crisis-level events.
    Today: stub — return empty proposals.
    """
    print("[SOLUTION] Generating solutions (stub)")
    return {"solution_proposals": []}


# ── Conditional routing ───────────────────────────────────────────────────────

def route_after_classify(state: AgentState) -> str:
    """
    If any event is 'crisis', fast-track to trend analysis.
    Otherwise go to summarize first.
    """
    has_crisis = any(
        e.get("urgency") == "crisis"
        for e in state["classified_events"]
    )
    return "trend" if has_crisis else "summarize"


# ── Build the graph ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("ingest", ingest_node)
    graph.add_node("classify", classify_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("trend", trend_node)
    graph.add_node("solution", solution_node)

    # Entry point
    graph.set_entry_point("ingest")

    # Linear edges
    graph.add_edge("ingest", "classify")

    # Conditional: crisis events skip directly to trend analysis
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "summarize": "summarize",
            "trend": "trend",
        }
    )

    graph.add_edge("summarize", "trend")
    graph.add_edge("trend", "solution")
    graph.add_edge("solution", END)

    return graph.compile()


# Singleton — import this in main.py
app_graph = build_graph()