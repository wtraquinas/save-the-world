export default function SolutionCard({ solution, index }) {
  const TIMEFRAME_COLORS = {
    immediate:   { bg: "rgba(226,75,74,0.12)",  color: "#E24B4A",  label: "⚡ Immediate" },
    "short-term":{ bg: "rgba(239,159,39,0.12)", color: "#EF9F27",  label: "📅 Short-term" },
    "long-term": { bg: "rgba(55,138,221,0.12)", color: "#378ADD",  label: "🔭 Long-term" },
  }

  const tf = TIMEFRAME_COLORS[solution.timeframe] ?? TIMEFRAME_COLORS["short-term"]

  return (
    <div style={{
      background: "rgba(255,255,255,0.03)",
      border: "0.5px solid rgba(255,255,255,0.08)",
      borderRadius: 8, padding: "12px 14px", marginBottom: 8,
    }}>
      {/* Title row */}
      <div style={{ display: "flex", alignItems: "flex-start",
                    justifyContent: "space-between", gap: 8, marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
            background: "rgba(55,138,221,0.2)", color: "#378ADD",
            fontSize: 11, fontWeight: 700,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            {index + 1}
          </div>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#e6edf3",
                        lineHeight: 1.3 }}>
            {solution.title}
          </div>
        </div>
        <span style={{
          fontSize: 10, padding: "2px 7px", borderRadius: 10, flexShrink: 0,
          background: tf.bg, color: tf.color,
          border: `0.5px solid ${tf.color}55`,
        }}>
          {tf.label}
        </span>
      </div>

      {/* Description */}
      <div style={{ fontSize: 12, color: "#9ca3af", lineHeight: 1.6, marginBottom: 8 }}>
        {solution.description}
      </div>

      {/* Precedent */}
      {solution.precedent && (
        <div style={{
          fontSize: 11, color: "#6B7280", lineHeight: 1.5,
          borderLeft: "2px solid rgba(55,138,221,0.4)",
          paddingLeft: 8, marginBottom: 8, fontStyle: "italic",
        }}>
          {solution.precedent}
        </div>
      )}

      {/* Footer: implementing bodies + SDGs */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
        {solution.implementing_bodies?.map(body => (
          <span key={body} style={{
            fontSize: 10, padding: "2px 6px", borderRadius: 10,
            background: "rgba(29,158,117,0.12)", color: "#1D9E75",
            border: "0.5px solid rgba(29,158,117,0.3)",
          }}>
            {body}
          </span>
        ))}
        {solution.sdg_alignment?.map(sdg => (
          <span key={sdg} style={{
            fontSize: 10, padding: "2px 6px", borderRadius: 10,
            background: "rgba(55,138,221,0.12)", color: "#378ADD",
            border: "0.5px solid rgba(55,138,221,0.3)",
          }}>
            {sdg}
          </span>
        ))}
      </div>
    </div>
  )
}