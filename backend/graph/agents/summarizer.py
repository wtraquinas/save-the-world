import json, os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState, NewsEvent
from graph.rag.retriever import retrieve

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "summary_cache.json"

SYSTEM_PROMPT = """You are a UN humanitarian analyst writing situation briefs.
Given a news event and relevant UN/humanitarian context, write a concise 3-sentence summary.

Your summary must:
1. State what is happening and who is affected (1 sentence)
2. Explain the humanitarian impact using the provided UN context (1 sentence)  
3. Reference a specific SDG goal or UN framework relevant to this crisis (1 sentence)

Be factual, neutral, and professional. Do not add opinions.
Return ONLY the 3-sentence summary — no headers, no bullets, no preamble."""


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def _save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def summarize_node(state: AgentState) -> dict:
    """
    For each classified event:
    1. Retrieves top-3 relevant UN doc chunks via ChromaDB
    2. Makes one LLM call to generate a grounded 3-sentence summary
    3. Caches result by event id — never re-summarizes the same event
    """
    events = state.get("classified_events", [])
    cache = _load_cache()

    to_summarize = [e for e in events if e["id"] not in cache]
    print(f"[SUMMARIZE] {len(events)-len(to_summarize)} from cache, {len(to_summarize)} need LLM")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    for event in to_summarize:
        # RAG: retrieve relevant UN context (local ChromaDB — zero API cost)
        query = f"{event['title']} {event['category']} {event['region']}"
        try:
            context_chunks = retrieve(query, k=3)
            context = "\n---\n".join(context_chunks)
        except Exception as e:
            print(f"[SUMMARIZE] ⚠️ RAG failed for {event['id']}: {e} — using no context")
            context = "No additional context available."

        # One LLM call per event
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""NEWS EVENT:
Title: {event['title']}
Source: {event['source']}
Category: {event['category']} | Urgency: {event['urgency']}
Region: {event['region']} | Country: {event['country']}
Body: {event['body'][:500]}

RELEVANT UN CONTEXT:
{context}

Write the 3-sentence humanitarian brief:"""),
        ]

        try:
            response = llm.invoke(messages)
            summary = response.content.strip()
            cache[event["id"]] = summary
            print(f"[SUMMARIZE] ✅ {event['id']}: {summary[:80]}...")
        except Exception as e:
            print(f"[SUMMARIZE] ⚠️ LLM failed for {event['id']}: {e}")
            cache[event["id"]] = f"[Summary unavailable] {event['title']}"

    _save_cache(cache)

    # Merge summaries back into events
    summarized: list[NewsEvent] = []
    for event in events:
        summarized.append({
            **event,
            "summary": cache.get(event["id"], f"[Pending] {event['title']}"),
        })

    print(f"[SUMMARIZE] 📝 {len(summarized)} events summarized")
    return {"summarized_events": summarized}