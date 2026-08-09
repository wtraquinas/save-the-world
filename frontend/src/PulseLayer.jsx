import { useMap } from "react-leaflet"
import { useEffect, useRef } from "react"
import L from "leaflet"
import { CATEGORY_COLORS } from "./constants"

export default function PulseLayer({ events }) {
  const map = useMap()
  const layerRef = useRef(null)

  useEffect(() => {
    // Remove old layer
    if (layerRef.current) {
      layerRef.current.forEach(m => m.remove())
    }

    const crisisEvents = events.filter(e => e.urgency === "crisis")
    const markers = []

    crisisEvents.forEach(event => {
      const color = CATEGORY_COLORS[event.category] ?? "#E24B4A"

      // Create pulsing div icon
      const pulseIcon = L.divIcon({
        className: "",
        html: `
          <div style="position:relative;width:40px;height:40px;margin:-20px 0 0 -20px">
            <div style="
              position:absolute;inset:0;border-radius:50%;
              background:${color};opacity:0.15;
              animation:pulse-ring 2s ease-out infinite;
            "></div>
            <div style="
              position:absolute;inset:6px;border-radius:50%;
              background:${color};opacity:0.25;
              animation:pulse-ring 2s ease-out infinite 0.4s;
            "></div>
            <div style="
              position:absolute;inset:12px;border-radius:50%;
              background:${color};opacity:0.9;
            "></div>
          </div>
          <style>
            @keyframes pulse-ring {
              0%   { transform: scale(0.8); opacity: 0.4; }
              70%  { transform: scale(1.6); opacity: 0;   }
              100% { transform: scale(0.8); opacity: 0;   }
            }
          </style>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      })

      const marker = L.marker([event.lat, event.lng], { icon: pulseIcon })
        .addTo(map)
      markers.push(marker)
    })

    layerRef.current = markers

    return () => markers.forEach(m => m.remove())
  }, [events, map])

  return null
}