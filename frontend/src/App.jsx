import { useState, useCallback, useRef } from "react"
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import { CATEGORY_COLORS, URGENCY_LABELS, URGENCY_COLORS, API } from "./constants"
import { useWebSocket } from "./useWebSocket"
import Sidebar from "./Sidebar"
import Drawer from "./Drawer"
import TrendPanel from "./TrendPanel"
import DemoToggle from "./DemoToggle"

import L from "leaflet"
import { Marker } from "react-leaflet"

// Non-interactive glow marker — clicks pass through to CircleMarker below
function GlowMarker({ position, icon }) {
  return (
    <Marker
      position={position}
      icon={icon}
      interactive={false}
      keyboard={false}
      zIndexOffset={-1000}   // always behind the real pin
    />
  )
}

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

  const markerRefs = useRef({})
  const mapRef = useRef(null)

  // Update onSelect to fly to pin and open popup
  const handleSelect = useCallback((event) => {
    setSelected(event)
    const marker = markerRefs.current[event.id]
    if (marker) {
      marker.openPopup()
      marker._map?.flyTo([event.lat, event.lng], 4, { duration: 1.2 })  // 4 not 5
    }
  }, [])

  return (
    <div style={{ position: "relative", height: "100vh", width: "100vw" }}>
      {/* Global CSS for glow pulse animation */}
      <style>{`
        .pulse-ring {
          border-radius: 50%;
          position: absolute;
          inset: 0;
          animation: glow-pulse 2.2s ease-out infinite;
        }
        .pulse-ring-2 {
          border-radius: 50%;
          position: absolute;
          inset: 20%;
          animation: glow-pulse 2.2s ease-out infinite 0.7s;
        }
        @keyframes glow-pulse {
          0%   { transform: scale(0.7); opacity: 0.5; }
          70%  { transform: scale(1.8); opacity: 0;   }
          100% { transform: scale(0.7); opacity: 0;   }
        }
        .leaflet-popup-content-wrapper {
          background: #1a1f2e !important;
          border: 0.5px solid rgba(255,255,255,0.12) !important;
          border-radius: 10px !important;
          box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
          padding: 0 !important;
        }
        .leaflet-popup-content {
          margin: 0 !important;
          padding: 12px 14px !important;
        }
        .leaflet-popup-tip {
          background: #1a1f2e !important;
        }
        .leaflet-popup-tip-container {
          filter: drop-shadow(0 1px 2px rgba(0,0,0,0.4));
        }
      `}</style>
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
        center={[20, 10]}
        zoom={2.5}
        style={{ height: "100vh", width: "100%", background: "#0d1117" }}
        zoomControl={false}
        whenCreated={map => { mapRef.current = map }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com">CARTO</a>'
        />

        {/* Glow pulse rings — divIcon with interactive:false so clicks pass through */}
        {eventList
          .filter(e => e.urgency === "crisis")
          .map(event => {
            const color = CATEGORY_COLORS[event.category] ?? "#E24B4A"
            const glowIcon = L.divIcon({
              className: "",
              html: `
                <div style="
                  position: relative;
                  width: 48px;
                  height: 48px;
                ">
                  <div class="pulse-ring" style="background:${color};opacity:0.15;"></div>
                  <div class="pulse-ring-2" style="background:${color};opacity:0.2;"></div>
                </div>
              `,
              iconSize:   [48, 48],
              iconAnchor: [24, 24],
            })
            return (
              <GlowMarker
                key={`glow-${event.id}`}
                position={[event.lat, event.lng]}
                icon={glowIcon}
              />
            )
          })
        }

        {/* Event pins */}
        {eventList.map(event => (
          <CircleMarker
            key={event.id}
            center={[event.lat, event.lng]}
            radius={
              event.urgency === "crisis" ? 11 :
              event.urgency === "alert"  ?  8 : 6
            }
            pathOptions={{
              color:       CATEGORY_COLORS[event.category] ?? "#6B7280",
              fillColor:   CATEGORY_COLORS[event.category] ?? "#6B7280",
              fillOpacity: event.urgency === "crisis" ? 0.95 : 0.7,
              weight:      event.urgency === "crisis" ? 2    : 1.5,
            }}
            ref={marker => { if (marker) markerRefs.current[event.id] = marker }}
            eventHandlers={{ click: () => handleSelect(event) }}
          >
            <Popup>
              <div style={{ minWidth: 190 }}>
                <div style={{
                  fontWeight: 600, fontSize: 13,
                  lineHeight: 1.4, marginBottom: 8,
                  color: "#e6edf3",
                }}>
                  {event.title}
                </div>

                <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 8 }}>
                  <span style={{
                    fontSize: 10, padding: "2px 7px", borderRadius: 10,
                    background: `${URGENCY_COLORS[event.urgency] ?? "#6B7280"}22`,
                    color:       URGENCY_COLORS[event.urgency] ?? "#6B7280",
                    border:     `0.5px solid ${URGENCY_COLORS[event.urgency] ?? "#6B7280"}`,
                    fontWeight: 600,
                  }}>
                    {URGENCY_LABELS[event.urgency] ?? event.urgency}
                  </span>
                  <span style={{
                    fontSize: 10, padding: "2px 7px", borderRadius: 10,
                    background: `${CATEGORY_COLORS[event.category] ?? "#6B7280"}22`,
                    color:       CATEGORY_COLORS[event.category] ?? "#6B7280",
                    border:     `0.5px solid ${CATEGORY_COLORS[event.category] ?? "#6B7280"}55`,
                  }}>
                    {event.category}
                  </span>
                </div>

                <div style={{ fontSize: 11, color: "#6B7280", marginBottom: 8 }}>
                  📍 {event.region} &nbsp;·&nbsp; 🗞 {event.source}
                </div>

                {event.sdg_tags?.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap",
                                gap: 3, marginBottom: 8 }}>
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

                <button
                  onClick={() => handleSelect(event)}
                  style={{
                    width: "100%", fontSize: 11, padding: "6px 0",
                    borderRadius: 6, cursor: "pointer",
                    background: "rgba(55,138,221,0.15)",
                    color: "#378ADD",
                    border: "0.5px solid rgba(55,138,221,0.35)",
                    transition: "background 0.15s",
                  }}
                >
                  View full brief →
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}

      </MapContainer>

      {/* ── Left sidebar — crisis feed ── */}
      <Sidebar
        events={eventList}
        onSelect={handleSelect}   // ← was setSelected
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