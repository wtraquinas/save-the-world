


# 🌍 UN AI Situation Room — Save the World

> A LangGraph-powered humanitarian intelligence platform that monitors global crises,
> analyses trends, and proposes UN-grounded solutions in real time.

[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7)](https://save-the-world-pxbs.onrender.com/health)
[![Frontend](https://img.shields.io/badge/Frontend-Vercel-000000)](https://save-the-world-mu.vercel.app)

## 🚀 Live Demo

| Service | URL |
|---|---|
| Frontend | https://save-the-world-mu.vercel.app |
| Backend API | https://save-the-world-pxbs.onrender.com |
| Health check | https://save-the-world-pxbs.onrender.com/health |

## 🏗 Architecture

```
Data Sources (GDELT, UN RSS, ReliefWeb, Mock)
↓
LangGraph Orchestrator
├── Ingestion Agent — fetch, dedupe, geo-tag
├── Classifier Agent — category + urgency (GPT-4o-mini, batched)
├── Summarizer Agent — RAG + UN docs → 3-sentence brief
├── Trend Analyst — pattern detection + 30-day forecast
└── Solution Bot — SDG-grounded proposals per crisis pattern
↓
FastAPI + WebSocket
↓
React Frontend
├── World Map (Leaflet) — colour-coded pins, pulse rings on crisis events
├── Crisis Feed Sidebar — live, sorted by urgency
├── Event Drawer — AI brief, SDG tags, source excerpt
└── Intelligence Panel — Trends · Patterns · Solutions tabs
```


## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Orchestration | LangGraph 0.2 |
| RAG | LangChain + ChromaDB |
| Backend | FastAPI + WebSocket |
| Frontend | React + Leaflet |
| Deployment | Render (backend) + Vercel (frontend) |
| Data | GDELT 2.0, UN News RSS, ReliefWeb RSS |

## 🗓 Built in 7 Days

| Day | What was built |
|---|---|
| 1 | Project scaffold, LangGraph skeleton, mock data, Leaflet map |
| 2 | Ingestion + Classifier agents with caching |
| 3 | RAG pipeline, ChromaDB, Summarizer agent |
| 4 | Trend Analyst + Solution Bot agents |
| 5 | FastAPI WebSocket, full frontend connected to all endpoints |
| 6 | Pulse rings, Solutions panel, loading overlay |
| 7 | GDELT + RSS ingestion, Demo mode, README |

## 🔑 Environment Variables

```bash
# backend/.env
OPENAI_API_KEY=sk-...
```

## 🏃 Run Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/events` | All events as GeoJSON |
| GET | `/events/summarized` | Events with AI summaries |
| GET | `/trends` | Latest trend report |
| GET | `/solutions` | Solution proposals |
| GET | `/mode` | Demo vs live mode |
| POST | `/analyze` | Run full LangGraph pipeline |
| POST | `/ingest` | Fetch live events from GDELT + RSS |
| WS | `/ws/feed` | Live event stream |

## 🌍 Crisis Categories

| Colour | Category |
|---|---|
| 🔴 Red | Conflict |
| 🔵 Blue | Climate |
| 🟡 Amber | Famine |
| 🟣 Purple | Disease |
| 🟢 Teal | Displacement |

## 📖 UN Knowledge Base

The RAG pipeline is grounded in:
- UN Sustainable Development Goals (SDGs 1–17)
- UNHCR Global Compact on Refugees
- OCHA Humanitarian Response frameworks
- WHO epidemic response protocols
- WFP food security intervention models



---

---

<br>

<br>

---

---

# FIRST README

---

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
