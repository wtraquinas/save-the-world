import { URGENCY_COLORS, URGENCY_LABELS, CATEGORY_COLORS } from "./constants"
import { formatDate } from "./utils"

export default function Drawer({ event, onClose }) {
  return (
    <div style={{
      position: "absolute", top: 48, right: 0, bottom: 0,
      width: 340, zIndex: 900,
      background: "rgba(13,17,23,0.95)", backdropFilter: "blur(12px)",
      borderLeft: "0.5px solid rgba(255,255,255,0.08)",
      overflowY: "auto", padding: "16px",
    }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ flex: 1, marginRight: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#e6edf3",
                        lineHeight: 1.4, marginBottom: 6 }}>
            {event.title}
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span style={{
              fontSize: 11, padding: "2px 8px", borderRadius: 20,
              background: `${URGENCY_COLORS[event.urgency]}22`,
              color: URGENCY_COLORS[event.urgency],
              border: `0.5px solid ${URGENCY_COLORS[event.urgency]}`,
              fontWeight: 600,
            }}>
              {URGENCY_LABELS[event.urgency]}
            </span>
            <span style={{
              fontSize: 11, padding: "2px 8px", borderRadius: 20,
              background: `${CATEGORY_COLORS[event.category] ?? "#6B7280"}22`,
              color: CATEGORY_COLORS[event.category] ?? "#6B7280",
              border: `0.5px solid ${CATEGORY_COLORS[event.category] ?? "#6B7280"}55`,
            }}>
              {event.category}
            </span>
          </div>
        </div>
        <button onClick={onClose} style={{
          background: "rgba(255,255,255,0.06)", border: "none",
          color: "#9ca3af", cursor: "pointer", borderRadius: 6,
          padding: "4px 8px", fontSize: 16,
        }}>×</button>
      </div>

      {/* Meta */}
      <div style={{ fontSize: 11, color: "#6B7280", marginBottom: 14,
                    display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
        <span>📍 {event.region} · {event.country}</span>
        <span style={{ color: "#374151" }}>|</span>
        <span>🗞 {event.source}</span>
        {event.published_at && (
          <>
            <span style={{ color: "#374151" }}>|</span>
            <span>🕐 {formatDate(event.published_at)}</span>
          </>
        )}
      </div>

      {/* AI Summary */}
      {event.summary && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                        letterSpacing: "0.06em", marginBottom: 6 }}>
            🤖 AI BRIEF
          </div>
          <div style={{
            fontSize: 13, color: "#c9d1d9", lineHeight: 1.6,
            background: "rgba(55,138,221,0.06)",
            border: "0.5px solid rgba(55,138,221,0.2)",
            borderRadius: 8, padding: "10px 12px",
          }}>
            {event.summary}
          </div>
        </div>
      )}

      {/* SDG Tags */}
      {event.sdg_tags?.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                        letterSpacing: "0.06em", marginBottom: 6 }}>
            🎯 SDG ALIGNMENT
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {event.sdg_tags.map(tag => (
              <span key={tag} style={{
                fontSize: 11, padding: "3px 10px", borderRadius: 20,
                background: "rgba(55,138,221,0.15)", color: "#378ADD",
                border: "0.5px solid rgba(55,138,221,0.4)",
              }}>
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Raw body */}
      {event.body && (
        <div>
          <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                        letterSpacing: "0.06em", marginBottom: 6 }}>
            📰 SOURCE EXCERPT
          </div>
          <div style={{ fontSize: 12, color: "#6B7280", lineHeight: 1.6 }}>
            {event.body.slice(0, 300)}{event.body.length > 300 ? "..." : ""}
          </div>
        </div>
      )}
    </div>
  )
}