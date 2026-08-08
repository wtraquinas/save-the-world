# Save The World
Did you ever ask yourself : 
- "what a UN Situation Room would look like if it ran on AI."?

<br>

---


## Architecture

(insert image)

<br>

---

## Why LangGraph is Perfect Here

 **well-defined branching workflows** — an incoming news item about a flood in Bangladesh needs a different agent path than a diplomatic conflict in the Middle East. LangGraph lets you encode those routes explicitly.

<br>

---

## The Agent Pipeline

**1. Ingestion agent** — polls News APIs (GDELT is gold for this — it geo-tags events automatically), RSS from UN/WHO/UNHCR, and scrapes structured open data. It deduplicates, normalizes, and geo-tags every event with lat/lng.

**2. Classifier agent** — categorizes each event by topic (climate, conflict, famine, disease), urgency level (watch / alert / crisis), and affected SDG goals. This drives how the map pin looks and whether the trend agent gets triggered.

**3. Summarizer agent (RAG-powered)** — uses LangChain RAG over a vector store of UN resolutions, historical crisis reports, and humanitarian docs. It produces multi-lingual summaries grounded in authoritative sources, not just the raw article.

**4. Trend analyst agent** — runs over a sliding window of events, detects patterns ("floods in 4 SE Asian countries in 10 days"), generates forecasts, and flags emerging crises before they explode.

**5. Solution bot** — the most creative piece. Given a detected crisis, it retrieves relevant UN SDG targets, past successful interventions, and NGO responses via RAG, then proposes concrete, cited possible solutions.

<br>

---

## The World Map UI

This is where it gets visually stunning. You'd use **Mapbox GL** or **Leaflet** with:

- Clustered pins by crisis category (conflict = red, climate = blue, disease = orange)
- Heat overlay driven by event density/urgency
- Click a pin → right panel opens with the AI-generated summary, trend sparkline, and solution suggestions
- Time-scrubbing slider to replay how a crisis evolved over weeks

<br>
---

## What Makes This Bootcamp-Worthy

The key technical differentiators to highlight in a presentation:

- **Agentic loop with feedback** — the trend agent can trigger the solution agent, which can trigger a human-review node before publishing
- **RAG grounded in real UN docs** — not hallucinated solutions, but proposals citing actual resolutions
- **Real-time streaming** — WebSockets push new events to the map live
- **Multi-lingual** — using an LLM to normalize news from Arabic, French, Spanish sources into the same schema

The pitch is simple: *"This is what a UN Situation Room would look like if it ran on AI."* Hard to top that in a bootcamp demo.
