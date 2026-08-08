from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.agents.ingestion import ingest_node
from graph.agents.classifier import classify_node
from graph.agents.summarizer import summarize_node
from graph.agents.trend import trend_node
from graph.agents.solution import solution_node


def route_after_classify(state: AgentState) -> str:
    """Crisis events skip summarization and go straight to trend analysis."""
    has_crisis = any(e.get("urgency") == "crisis" for e in state["classified_events"])
    return "trend" if has_crisis else "summarize"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("ingest",    ingest_node)
    graph.add_node("classify",  classify_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("trend",     trend_node)
    graph.add_node("solution",  solution_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest",    "classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"summarize": "summarize", "trend": "trend"},
    )

    graph.add_edge("summarize", "trend")
    graph.add_edge("trend",     "solution")
    graph.add_edge("solution",  END)

    return graph.compile()


app_graph = build_graph()