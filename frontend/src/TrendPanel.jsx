import { useState, useEffect } from "react"
import { API } from "./constants"
import SolutionCard from "./SolutionCard"

export default function TrendPanel({ trends, onClose }) {
  const [tab, setTab]           = useState("trends")
  const [solutions, setSolutions] = useState([])
  const [loading, setLoading]   = useState(false)

  useEffect(() => {
    async function fetchSolutions() {
      setLoading(true)
      try {
        const r = await fetch(`${API}/solutions`)
        const data = await r.json()
        setSolutions(data.proposals ?? [])
      } catch (e) {
        console.error("[SOLUTIONS]", e)
      }
      setLoading(false)
    }
    if (tab === "solutions") fetchSolutions()
  }, [tab])

  if (!trends) return null

  return (
    <div style={{
      position: "absolute", top: 58, left: "50%",
      transform: "translateX(-50%)",
      width: "min(700px, 90vw)", maxHeight: "78vh",
      zIndex: 1100,
      background: "rgba(13,17,23,0.97)", backdropFilter: "blur(16px)",
      border: "0.5px solid rgba(255,255,255,0.12)",
      borderRadius: 12, display: "flex", flexDirection: "column",
    }}>
      {/* Header */}
      <div style={{ padding: "16px 20px 0", flexShrink: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between",
                      alignItems: "center", marginBottom: 14 }}>
          <div style={{ fontWeight: 600, fontSize: 15 }}>
            📊 Global Intelligence
          </div>
          <button onClick={onClose} style={{
            background: "rgba(255,255,255,0.06)", border: "none",
            color: "#9ca3af", cursor: "pointer", borderRadius: 6,
            padding: "4px 10px", fontSize: 16,
          }}>×</button>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4, marginBottom: 0 }}>
          {[
            { id: "trends",    label: "📈 Trends"    },
            { id: "patterns",  label: "🔍 Patterns"  },
            { id: "solutions", label: "💡 Solutions"  },
            { id: "knowledge", label: "📚 Knowledge Base" },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              fontSize: 12, padding: "6px 14px", borderRadius: "6px 6px 0 0",
              cursor: "pointer", border: "0.5px solid rgba(255,255,255,0.08)",
              borderBottom: tab === t.id ? "none" : "0.5px solid rgba(255,255,255,0.08)",
              background: tab === t.id
                ? "rgba(255,255,255,0.06)" : "transparent",
              color: tab === t.id ? "#e6edf3" : "#6B7280",
              transition: "all 0.15s",
            }}>
              {t.label}
            </button>
          ))}
        </div>
        <div style={{ height: "0.5px", background: "rgba(255,255,255,0.08)" }} />
      </div>

      {/* Tab content */}
      <div style={{ overflowY: "auto", padding: "16px 20px", flex: 1 }}>

        {/* ── TRENDS tab ── */}
        {tab === "trends" && (
          <>
            {/* Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)",
                          gap: 8, marginBottom: 16 }}>
              {[
                { label: "Crisis Events",  value: trends.crisis_count ?? 0,           color: "#E24B4A" },
                { label: "Alert Events",   value: trends.alert_count  ?? 0,           color: "#EF9F27" },
                { label: "Dominant Type",  value: trends.dominant_category ?? "—",    color: "#378ADD" },
              ].map(s => (
                <div key={s.label} style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "0.5px solid rgba(255,255,255,0.08)",
                  borderRadius: 8, padding: "10px 12px", textAlign: "center",
                }}>
                  <div style={{ fontSize: 20, fontWeight: 600, color: s.color }}>
                    {s.value}
                  </div>
                  <div style={{ fontSize: 11, color: "#6B7280", marginTop: 2 }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>

            {/* Forecast */}
            {trends.forecast && (
              <div style={{
                background: "rgba(55,138,221,0.06)",
                border: "0.5px solid rgba(55,138,221,0.2)",
                borderRadius: 8, padding: "12px 14px", marginBottom: 16,
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
              <div>
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
          </>
        )}

        {/* ── PATTERNS tab ── */}
        {tab === "patterns" && (
          <>
            {trends.patterns?.length === 0 && (
              <div style={{ color: "#6B7280", fontSize: 13, textAlign: "center",
                            padding: "32px 0" }}>
                No patterns detected yet. Run Analysis first.
              </div>
            )}
            {trends.patterns?.map((p, i) => (
              <div key={i} style={{
                background: "rgba(255,255,255,0.03)",
                border: "0.5px solid rgba(255,255,255,0.07)",
                borderRadius: 8, padding: "12px 14px", marginBottom: 8,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between",
                              alignItems: "center", marginBottom: 6 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#e6edf3" }}>
                    {p.title}
                  </div>
                  <span style={{
                    fontSize: 10, padding: "2px 7px", borderRadius: 10,
                    background: p.severity === "rising"
                      ? "rgba(226,75,74,0.15)" : "rgba(29,158,117,0.15)",
                    color: p.severity === "rising" ? "#E24B4A" : "#1D9E75",
                    border: `0.5px solid ${p.severity === "rising" ? "#E24B4A55" : "#1D9E7555"}`,
                  }}>
                    {p.severity === "rising" ? "↑ Rising" : "→ Stable"}
                  </span>
                </div>
                <div style={{ fontSize: 12, color: "#9ca3af", lineHeight: 1.5,
                              marginBottom: 6 }}>
                  {p.description}
                </div>
                <div style={{ fontSize: 11, color: "#6B7280" }}>
                  📍 {p.affected_regions?.join(", ")}
                  &nbsp;·&nbsp;
                  {p.event_ids?.length} events
                </div>
              </div>
            ))}
          </>
        )}

        {/* ── SOLUTIONS tab ── */}
        {tab === "solutions" && (
          <>
            {loading && (
              <div style={{ color: "#6B7280", fontSize: 13, textAlign: "center",
                            padding: "32px 0" }}>
                ⏳ Loading solution proposals...
              </div>
            )}
            {!loading && solutions.length === 0 && (
              <div style={{ color: "#6B7280", fontSize: 13, textAlign: "center",
                            padding: "32px 0" }}>
                No solutions yet. Run Analysis first.
              </div>
            )}
            {!loading && solutions.map((proposal, pi) => (
              <div key={pi} style={{ marginBottom: 20 }}>
                <div style={{
                  fontSize: 12, fontWeight: 600, color: "#378ADD",
                  letterSpacing: "0.06em", marginBottom: 10,
                  padding: "6px 10px", borderRadius: 6,
                  background: "rgba(55,138,221,0.08)",
                  border: "0.5px solid rgba(55,138,221,0.2)",
                }}>
                  🎯 {proposal.pattern}
                </div>
                {proposal.solutions?.map((sol, si) => (
                  <SolutionCard key={si} solution={sol} index={si} />
                ))}
              </div>
            ))}
          </>
        )}

        {tab === "knowledge" && (
          <div>
            <div style={{ fontSize: 12, color: "#6B7280", lineHeight: 1.6,
                          marginBottom: 16 }}>
              The AI agents ground their summaries and solutions in these
              UN frameworks, embedded in ChromaDB and retrieved via RAG.
            </div>

            {[
              {
                code: "SDG 1",  title: "No Poverty",
                desc: "End poverty in all its forms everywhere.",
                color: "#E24B4A",
              },
              {
                code: "SDG 2",  title: "Zero Hunger",
                desc: "End hunger, achieve food security and improved nutrition.",
                color: "#EF9F27",
              },
              {
                code: "SDG 3",  title: "Good Health",
                desc: "Ensure healthy lives and promote well-being for all.",
                color: "#1D9E75",
              },
              {
                code: "SDG 6",  title: "Clean Water",
                desc: "Ensure access to water and sanitation for all.",
                color: "#378ADD",
              },
              {
                code: "SDG 10", title: "Reduced Inequalities",
                desc: "Reduce inequality within and among countries.",
                color: "#7F77DD",
              },
              {
                code: "SDG 13", title: "Climate Action",
                desc: "Take urgent action to combat climate change.",
                color: "#378ADD",
              },
              {
                code: "SDG 16", title: "Peace & Justice",
                desc: "Promote peaceful and inclusive societies.",
                color: "#E24B4A",
              },
              {
                code: "SDG 17", title: "Partnerships",
                desc: "Strengthen global partnerships for sustainable development.",
                color: "#1D9E75",
              },
            ].map(sdg => (
              <div key={sdg.code} style={{
                display: "flex", gap: 12, alignItems: "flex-start",
                padding: "10px 0",
                borderBottom: "0.5px solid rgba(255,255,255,0.06)",
              }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 8, flexShrink: 0,
                  background: `${sdg.color}22`,
                  border: `1px solid ${sdg.color}44`,
                  display: "flex", flexDirection: "column",
                  alignItems: "center", justifyContent: "center",
                }}>
                  <div style={{ fontSize: 9, color: sdg.color, fontWeight: 700 }}>
                    {sdg.code.split(" ")[0]}
                  </div>
                  <div style={{ fontSize: 14, color: sdg.color, fontWeight: 700 }}>
                    {sdg.code.split(" ")[1]}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600,
                                color: "#e6edf3", marginBottom: 3 }}>
                    {sdg.title}
                  </div>
                  <div style={{ fontSize: 12, color: "#6B7280", lineHeight: 1.5 }}>
                    {sdg.desc}
                  </div>
                </div>
              </div>
            ))}

            <div style={{ marginTop: 16, padding: "10px 12px", borderRadius: 8,
                          background: "rgba(55,138,221,0.06)",
                          border: "0.5px solid rgba(55,138,221,0.2)" }}>
              <div style={{ fontSize: 11, color: "#378ADD", fontWeight: 600,
                            marginBottom: 4 }}>
                📂 EMBEDDED SOURCES
              </div>
              {[
                "UN SDG Knowledge Base (Goals 1–17)",
                "UNHCR Global Compact on Refugees",
                "OCHA Humanitarian Response Framework",
                "WHO Epidemic Response Protocols",
                "WFP Food Security Intervention Models",
              ].map(doc => (
                <div key={doc} style={{ fontSize: 12, color: "#6B7280",
                                        padding: "3px 0", display: "flex",
                                        alignItems: "center", gap: 6 }}>
                  <span style={{ color: "#378ADD" }}>›</span> {doc}
                </div>
              ))}
              <div style={{ fontSize: 11, color: "#6B7280", marginTop: 8,
                            borderTop: "0.5px solid rgba(255,255,255,0.06)",
                            paddingTop: 8 }}>
                Stored in ChromaDB · Retrieved via cosine similarity ·
                Top-3 chunks per query
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}