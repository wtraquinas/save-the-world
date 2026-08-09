export const API = import.meta.env.VITE_API_URL || "http://localhost:8000"
export const WS  = API.replace("https://", "wss://").replace("http://", "ws://")

export const CATEGORY_COLORS = {
  conflict:     "#E24B4A",
  climate:      "#378ADD",
  famine:       "#EF9F27",
  disease:      "#7F77DD",
  displacement: "#1D9E75",
  other:        "#6B7280",
}

export const URGENCY_COLORS = {
  crisis: "#E24B4A",
  alert:  "#EF9F27",
  watch:  "#1D9E75",
}

export const URGENCY_LABELS = {
  crisis: "🔴 CRISIS",
  alert:  "🟡 ALERT",
  watch:  "🟢 WATCH",
}