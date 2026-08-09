/**
 * Formats an event's published_at into a readable relative or absolute date.
 * e.g. "2 hours ago", "Yesterday", "Aug 5"
 */
export function formatDate(dateStr) {
  if (!dateStr) return ""
  try {
    const date = new Date(dateStr)
    if (isNaN(date)) return dateStr.slice(0, 10)

    const now  = new Date()
    const diff = Math.floor((now - date) / 1000)   // seconds

    if (diff < 60)     return "Just now"
    if (diff < 3600)   return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400)  return `${Math.floor(diff / 3600)}h ago`
    if (diff < 172800) return "Yesterday"

    return date.toLocaleDateString("en-GB", {
      day:   "numeric",
      month: "short",
      year:  date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    })
  } catch {
    return ""
  }
}