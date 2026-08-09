export default function TrendPanel({ trends, onClose }) {
  if (!trends) return null

  return (
    <div style={{
      position: "absolute", top: 58, left: "50%",
      transform: "translateX(-50%)",
      width: "min(680px, 90vw)", maxHeight: "75vh",
      zIndex: 1100, overflowY: "auto",
      background: "rgba(13,17,23,0.97)", backdropFilter: "blur(16px)",
      border: "0.5px solid rgba(255,255,255,0.12)",
      borderRadius: 12, padding: 20,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", marginBottom: 16 }}>
        <div style={{ fontWeight: 600, fontSize: 15 }}>📊 Global Trend Analysis</div>
        <button onClick={onClose} style={{
          background: "rgba(255,255,255,0.06)", border: "none",
          color: "#9ca3af", cursor: "pointer", borderRadius: 6,
          padding: "4px 10px", fontSize: 16,
        }}>×</button>
      </div>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)",
                    gap: 8, marginBottom: 16 }}>
        {[
          { label: "Crisis Events",    value: trends.crisis_count ?? 0, color: "#E24B4A" },
          { label: "Alert Events",     value: trends.alert_count  ?? 0, color: "#EF9F27" },
          { label: "Dominant Type",    value: trends.dominant_category ?? "—", color: "#378ADD" },
        ].map(s => (
          <div key={s.label} style={{
            background: "rgba(255,255,255,0.04)",
            border: "0.5px solid rgba(255,255,255,0.08)",
            borderRadius: 8, padding: "10px 12px", textAlign: "center",
          }}>
            <div style={{ fontSize: 20, fontWeight: 600, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 11, color: "#6B7280", marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Forecast */}
      {trends.forecast && (
        <div style={{ marginBottom: 16,
          background: "rgba(55,138,221,0.06)",
          border: "0.5px solid rgba(55,138,221,0.2)",
          borderRadius: 8, padding: "12px 14px",
        }}>
          <div style={{ fontSize: 11, color: "#378ADD", fontWeight: 600,
                        marginBottom: 6, letterSpacing: "0.06em" }}>
            🔮 30-DAY FORECAST
          </div>
          <div style={{ fontSize: 13, color: "#c9d1d9", lineHeight: 1.6 }}>
            {trends.forecast}
          </div>
        </div>
      )}

      {/* Hotspots */}
      {trends.hotspots?.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                        letterSpacing: "0.06em", marginBottom: 8 }}>
            🔥 HOTSPOTS
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {trends.hotspots.map(h => (
              <span key={h} style={{
                fontSize: 12, padding: "4px 10px", borderRadius: 20,
                background: "rgba(226,75,74,0.15)", color: "#E24B4A",
                border: "0.5px solid rgba(226,75,74,0.4)",
              }}>
                {h}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Patterns */}
      {trends.patterns?.length > 0 && (
        <div>
          <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                        letterSpacing: "0.06em", marginBottom: 8 }}>
            📈 DETECTED PATTERNS
          </div>
          {trends.patterns.map((p, i) => (
            <div key={i} style={{
              background: "rgba(255,255,255,0.03)",
              border: "0.5px solid rgba(255,255,255,0.07)",
              borderRadius: 8, padding: "10px 12px", marginBottom: 8,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between",
                            alignItems: "center", marginBottom: 4 }}>
                <div style={{ fontSize: 13, fontWeight: 500, color: "#e6edf3" }}>
                  {p.title}
                </div>
                <span style={{
                  fontSize: 10, padding: "2px 7px", borderRadius: 10,
                  background: p.severity === "rising"
                    ? "rgba(226,75,74,0.15)" : "rgba(29,158,117,0.15)",
                  color: p.severity === "rising" ? "#E24B4A" : "#1D9E75",
                  border: `0.5px solid ${p.severity === "rising" ? "#E24B4A" : "#1D9E75"}55`,
                }}>
                  {p.severity === "rising" ? "↑ Rising" : "→ Stable"}
                </span>
              </div>
              <div style={{ fontSize: 12, color: "#9ca3af", lineHeight: 1.5 }}>
                {p.description}
              </div>
              {p.affected_regions?.length > 0 && (
                <div style={{ fontSize: 11, color: "#6B7280", marginTop: 4 }}>
                  📍 {p.affected_regions.join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}