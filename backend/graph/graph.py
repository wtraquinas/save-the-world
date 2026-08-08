from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.agents.ingestion import ingest_node
from graph.agents.classifier import classify_node


# ── Stub nodes for Day 3 & 4 (unchanged) ─────────────────────────────────────

def summarize_node(state: AgentState) -> dict:
    print(f"[SUMMARIZE] Stub — {len(state['classified_events'])} events")
    summarized = [{**e, "summary": f"[STUB] {e['title']}"} for e in state["classified_events"]]
    return {"summarized_events": summarized}

def trend_node(state: AgentState) -> dict:
    print("[TREND] Stub")
    return {"trend_report": {"patterns": [], "forecast": "No trend data yet."}}

def solution_node(state: AgentState) -> dict:
    print("[SOLUTION] Stub")
    return {"solution_proposals": []}


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_classify(state: AgentState) -> str:
    has_crisis = any(e.get("urgency") == "crisis" for e in state["classified_events"])
    return "trend" if has_crisis else "summarize"


# ── Build ─────────────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("ingest",    ingest_node)
    graph.add_node("classify",  classify_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("trend",     trend_node)
    graph.add_node("solution",  solution_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "classify")
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"summarize": "summarize", "trend": "trend"},
    )
    graph.add_edge("summarize", "trend")
    graph.add_edge("trend", "solution")
    graph.add_edge("solution", END)

    return graph.compile()

app_graph = build_graph()