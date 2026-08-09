import { URGENCY_COLORS, URGENCY_LABELS, CATEGORY_COLORS } from "./constants"

export default function Sidebar({ events, onSelect, selected }) {
  const sorted = [...events].sort((a, b) => {
    const order = { crisis: 0, alert: 1, watch: 2 }
    return (order[a.urgency] ?? 3) - (order[b.urgency] ?? 3)
  })

  return (
    <div style={{
      position: "absolute", top: 48, left: 0, bottom: 0,
      width: 280, zIndex: 900,
      background: "rgba(13,17,23,0.88)", backdropFilter: "blur(8px)",
      borderRight: "0.5px solid rgba(255,255,255,0.08)",
      overflowY: "auto", paddingTop: 8,
    }}>
      <div style={{ padding: "8px 14px 4px", fontSize: 11,
                    color: "#6B7280", letterSpacing: "0.08em", fontWeight: 600 }}>
        CRISIS FEED — {events.length} EVENTS
      </div>

      {sorted.map(event => (
        <div
          key={event.id}
          onClick={() => onSelect(event)}
          style={{
            padding: "10px 14px", cursor: "pointer",
            borderLeft: `3px solid ${selected?.id === event.id
              ? (CATEGORY_COLORS[event.category] ?? "#6B7280")
              : "transparent"}`,
            background: selected?.id === event.id
              ? "rgba(255,255,255,0.04)" : "transparent",
            borderBottom: "0.5px solid rgba(255,255,255,0.04)",
            transition: "all 0.15s",
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 500, color: "#e6edf3",
                        marginBottom: 4, lineHeight: 1.4 }}>
            {event.title}
          </div>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span style={{ fontSize: 10, color: URGENCY_COLORS[event.urgency] ?? "#6B7280" }}>
              {URGENCY_LABELS[event.urgency] ?? event.urgency?.toUpperCase()}
            </span>
            <span style={{ fontSize: 10, color: "#6B7280" }}>·</span>
            <span style={{ fontSize: 10, color: "#6B7280" }}>{event.region}</span>
          </div>

          {event.published_at && (
            <div style={{ fontSize: 10, color: "#4B5563", marginTop: 3 }}>
              🕐 {formatDate(event.published_at)}
            </div>
          )}

          {event.sdg_tags?.length > 0 && (
            <div style={{ marginTop: 4, display: "flex", flexWrap: "wrap", gap: 3 }}>
              {event.sdg_tags.slice(0, 3).map(tag => (
                <span key={tag} style={{
                  fontSize: 9, padding: "1px 5px", borderRadius: 10,
                  background: "rgba(55,138,221,0.15)", color: "#378ADD",
                  border: "0.5px solid rgba(55,138,221,0.3)",
                }}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}