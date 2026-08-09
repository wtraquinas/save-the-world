import { useState, useEffect } from "react"
import { API } from "./constants"

export default function DemoToggle() {
  const [mode, setMode] = useState(null)
  const [ingesting, setIngesting] = useState(false)

  useEffect(() => {
    fetch(`${API}/mode`)
      .then(r => r.json())
      .then(setMode)
      .catch(() => {})
  }, [])

  async function fetchLive() {
    setIngesting(true)
    try {
      const r = await fetch(`${API}/ingest`, { method: "POST" })
      const data = await r.json()
      console.log("[INGEST]", data)
      // Refresh mode
      const m = await fetch(`${API}/mode`).then(r => r.json())
      setMode(m)
    } catch (e) {
      console.error(e)
    }
    setIngesting(false)
  }

  if (!mode) return null

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span style={{
        fontSize: 11, padding: "3px 8px", borderRadius: 20,
        background: mode.demo_mode
          ? "rgba(239,159,39,0.15)" : "rgba(29,158,117,0.15)",
        color: mode.demo_mode ? "#EF9F27" : "#1D9E75",
        border: `0.5px solid ${mode.demo_mode ? "#EF9F27" : "#1D9E75"}`,
      }}>
        {mode.demo_mode ? "🎭 DEMO" : "🌐 LIVE"}
      </span>

      {mode.demo_mode && (
        <button
          onClick={fetchLive}
          disabled={ingesting}
          title="Fetch real events from GDELT + UN RSS"
          style={{
            fontSize: 11, padding: "3px 8px", borderRadius: 20,
            cursor: ingesting ? "default" : "pointer",
            background: "rgba(55,138,221,0.12)", color: "#378ADD",
            border: "0.5px solid rgba(55,138,221,0.4)",
          }}
        >
          {ingesting ? "⏳ Fetching..." : "📡 Fetch Live"}
        </button>
      )}

      {mode.live_events_available && (
        <span style={{ fontSize: 10, color: "#6B7280" }}>
          {mode.live_event_count} live events cached
        </span>
      )}
    </div>
  )
}