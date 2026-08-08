from typing import TypedDict, Literal, Optional
from datetime import datetime

# Urgency levels matching UN OCHA colour codes
UrgencyLevel = Literal["watch", "alert", "crisis"]

# Crisis categories aligned to UN thematic areas
CrisisCategory = Literal["conflict", "climate", "famine", "disease", "displacement", "other"]

class NewsEvent(TypedDict):
    id: str
    title: str
    source: str
    url: str
    published_at: str          # ISO 8601
    body: str                  # Raw article text
    country: str               # ISO 3166-1 alpha-2
    region: str                # e.g. "Sub-Saharan Africa"
    lat: float
    lng: float
    category: Optional[CrisisCategory]
    urgency: Optional[UrgencyLevel]
    summary: Optional[str]     # RAG-generated summary (Day 3)
    sdg_tags: list[str]        # e.g. ["SDG 2", "SDG 13"]
    trend_signal: Optional[str]
    solutions: list[str]


class AgentState(TypedDict):
    """
    The single state object that flows through every LangGraph node.
    Each agent reads from and writes to this dict.
    """
    # Raw inputs
    raw_events: list[NewsEvent]

    # Processed at each stage
    ingested_events: list[NewsEvent]
    classified_events: list[NewsEvent]
    summarized_events: list[NewsEvent]
    trend_report: Optional[dict]
    solution_proposals: list[dict]

    # Control flow
    current_batch: list[str]     # event ids being processed
    errors: list[str]
    requires_human_review: bool
    human_approved: bool

    # Metadata
    run_id: str
    started_at: str