import { useEffect, useRef, useState } from "react"
import { WS } from "./constants"

export function useWebSocket({ onEvent, onTrend, onReady }) {
  const ws = useRef(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    function connect() {
      ws.current = new WebSocket(`${WS}/ws/feed`)

      ws.current.onopen = () => {
        setConnected(true)
        console.log("[WS] Connected")
      }

      ws.current.onmessage = (msg) => {
        try {
          const { type, data } = JSON.parse(msg.data)
          if (type === "event" || type === "event_updated") onEvent?.(data)
          if (type === "trend_updated") onTrend?.(data)
          if (type === "ready") onReady?.(data)
        } catch (e) { /* ignore malformed */ }
      }

      ws.current.onclose = () => {
        setConnected(false)
        console.log("[WS] Disconnected — retrying in 3s")
        setTimeout(connect, 3000)   // auto-reconnect
      }

      ws.current.onerror = () => ws.current.close()
    }

    connect()
    return () => ws.current?.close()
  }, [])

  return { connected }
}