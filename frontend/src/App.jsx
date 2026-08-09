import { useState, useCallback } from "react"
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import { CATEGORY_COLORS, URGENCY_LABELS, URGENCY_COLORS, API } from "./constants"
import { useWebSocket } from "./useWebSocket"
import Sidebar from "./Sidebar"
import Drawer from "./Drawer"
import TrendPanel from "./TrendPanel"
import PulseLayer from "./PulseLayer"
import DemoToggle from "./DemoToggle"

export default function App() {
  const [events, setEvents]       = useState({})   // keyed by id
  const [selected, setSelected]   = useState(null)
  const [trends, setTrends]       = useState(null)
  const [wsReady, setWsReady]     = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [showTrends, setShowTrends] = useState(false)

  const onEvent = useCallback((e) => {
      console.log("[EVENT]", e.id, e.category, e.urgency)  // ← add this
      setEvents(prev => ({ ...prev, [e.id]: e }))
  }, [])

  const onTrend = useCallback((t) => setTrends(t), [])
  const onReady = useCallback(() => setWsReady(true), [])

  const { connected } = useWebSocket({ onEvent, onTrend, onReady })

  async function runAnalysis() {
    setAnalyzing(true)
    try {
      const r = await fetch(`${API}/analyze`, { method: "POST" })
      const data = await r.json()
      console.log("[ANALYZE]", data)
    } catch (e) {
      console.error(e)
    }
    setAnalyzing(false)
  }

  const eventList = Object.values(events)
  const crisisCount = eventList.filter(e => e.urgency === "crisis").length

  return (
    <div style={{ position: "relative", height: "100vh", width: "100vw" }}>

      {/* ── Header ── */}
      <header style={{
        position: "absolute", top: 0, left: 0, right: 0, zIndex: 1000,
        padding: "10px 16px", background: "rgba(13,17,23,0.92)",
        backdropFilter: "blur(8px)",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
        display: "flex", alignItems: "center", gap: 12,
      }}>
        <span style={{ fontSize: 20 }}>🌍</span>
        <span style={{ fontWeight: 600, fontSize: 15, color: "#fff" }}>
          UN AI Situation Room
        </span>

        {/* Status badges */}
        <span style={{
          fontSize: 11, padding: "3px 8px", borderRadius: 20,
          background: connected ? "rgba(29,158,117,0.2)" : "rgba(107,114,128,0.2)",
          color: connected ? "#1D9E75" : "#6B7280",
          border: `0.5px solid ${connected ? "#1D9E75" : "#6B7280"}`,
        }}>
          {connected ? "● LIVE" : "○ Connecting..."}
        </span>

        {crisisCount > 0 && (
          <span style={{
            fontSize: 11, padding: "3px 8px", borderRadius: 20,
            background: "rgba(226,75,74,0.2)", color: "#E24B4A",
            border: "0.5px solid #E24B4A", fontWeight: 600,
          }}>
            🚨 {crisisCount} CRISIS
          </span>
        )}

        {/* after the crisis count badge */}
        <DemoToggle />

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}></div>

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button onClick={() => setShowTrends(!showTrends)} style={{
            fontSize: 12, padding: "5px 12px", borderRadius: 6, cursor: "pointer",
            background: showTrends ? "rgba(55,138,221,0.3)" : "rgba(255,255,255,0.05)",
            color: "#e6edf3", border: "0.5px solid rgba(255,255,255,0.15)",
          }}>
            📊 Trends
          </button>

          <button onClick={runAnalysis} disabled={analyzing} style={{
            fontSize: 12, padding: "5px 12px", borderRadius: 6, cursor: "pointer",
            background: analyzing ? "rgba(107,114,128,0.2)" : "rgba(29,158,117,0.2)",
            color: analyzing ? "#6B7280" : "#1D9E75",
            border: `0.5px solid ${analyzing ? "#6B7280" : "#1D9E75"}`,
          }}>
            {analyzing ? "⏳ Analysing..." : "⚡ Run Analysis"}
          </button>
        </div>
      </header>

      {/* ── Map ── */}
      <MapContainer
        center={[20, 10]} zoom={2.5}
        style={{ height: "100vh", width: "100%", background: "#0d1117" }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com">CARTO</a>'
        />

        {eventList.map(event => (
          <CircleMarker
            key={event.id}
            center={[event.lat, event.lng]}
            radius={event.urgency === "crisis" ? 12 : event.urgency === "alert" ? 9 : 7}
            pathOptions={{
              color:       CATEGORY_COLORS[event.category] ?? "#6B7280",
              fillColor:   CATEGORY_COLORS[event.category] ?? "#6B7280",
              fillOpacity: event.urgency === "crisis" ? 0.9 : 0.65,
              weight:      event.urgency === "crisis" ? 2.5 : 1.5,
            }}
            eventHandlers={{ click: () => setSelected(event) }}
          >
            <Popup>
              <div style={{ minWidth: 160 }}>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
                  {event.title}
                </div>
                <div style={{ fontSize: 11, color: URGENCY_COLORS[event.urgency] }}>
                  {URGENCY_LABELS[event.urgency] ?? event.urgency}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
        {/* Pulse rings on crisis events */}
        <PulseLayer events={eventList.filter(e => e.urgency === "crisis")} />
      </MapContainer>

      {/* ── Left sidebar — crisis feed ── */}
      <Sidebar
        events={eventList}
        onSelect={setSelected}
        selected={selected}
      />

      {/* ── Right drawer — event detail ── */}
      {selected && (
        <Drawer event={selected} onClose={() => setSelected(null)} />
      )}

      {/* ── Trend panel ── */}
      {showTrends && trends && (
        <TrendPanel trends={trends} onClose={() => setShowTrends(false)} />
      )}

      {/* ── Legend ── */}
      <div style={{
        position: "absolute", bottom: 24, right: 16, zIndex: 1000,  // ← right: 16 instead of left: 16
        background: "rgba(13,17,23,0.85)", backdropFilter: "blur(8px)",
        border: "0.5px solid rgba(255,255,255,0.08)",
        borderRadius: 8, padding: "10px 14px",
      }}>
        <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                      letterSpacing: "0.06em", marginBottom: 6 }}>
          CATEGORY
        </div>
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} style={{ display: "flex", alignItems: "center", gap: 6,
                                  fontSize: 11, color: "#9ca3af", marginBottom: 3 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </div>
        ))}
        {/* Add urgency size guide */}
        <div style={{ fontSize: 11, color: "#6B7280", fontWeight: 600,
                      letterSpacing: "0.06em", margin: "8px 0 6px" }}>
          URGENCY
        </div>
        {[
          { label: "Crisis",  size: 12, color: "#E24B4A" },
          { label: "Alert",   size: 9,  color: "#EF9F27" },
          { label: "Watch",   size: 7,  color: "#1D9E75" },
        ].map(u => (
          <div key={u.label} style={{ display: "flex", alignItems: "center", gap: 6,
                                      fontSize: 11, color: "#9ca3af", marginBottom: 3 }}>
            <div style={{
              width: u.size, height: u.size, borderRadius: "50%",
              background: u.color, flexShrink: 0,
              marginLeft: (12 - u.size) / 2,   // centre-align different sizes
            }} />
            {u.label}
          </div>
        ))}
      </div>
      {/* ── Loading overlay — shows until WS sends first event ── */}
      {!wsReady && Object.keys(events).length === 0 && (
        <div style={{
          position: "absolute", inset: 0, zIndex: 2000,
          background: "rgba(13,17,23,0.85)", backdropFilter: "blur(4px)",
          display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", gap: 16,
        }}>
          <div style={{ fontSize: 48 }}>🌍</div>
          <div style={{ fontSize: 16, fontWeight: 600, color: "#e6edf3" }}>
            UN AI Situation Room
          </div>
          <div style={{ fontSize: 13, color: "#6B7280" }}>
            Connecting to live feed...
          </div>
          <div style={{
            width: 200, height: 2, background: "rgba(255,255,255,0.06)",
            borderRadius: 1, overflow: "hidden",
          }}>
            <div style={{
              height: "100%", width: "40%", borderRadius: 1,
              background: "#1D9E75",
              animation: "slide 1.2s ease-in-out infinite",
            }} />
          </div>
          <style>{`
            @keyframes slide {
              0%   { transform: translateX(-100%); }
              100% { transform: translateX(600%); }
            }
          `}</style>
        </div>
      )}
    </div>
  )
}