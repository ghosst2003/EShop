import { recordCommerceEvent } from '../api'

const SESSION_KEY = 'becool-analytics-session'
const sessionId = sessionStorage.getItem(SESSION_KEY) || crypto.randomUUID()
sessionStorage.setItem(SESSION_KEY, sessionId)

export const analyticsAllowed = () => {
  try { return Boolean(JSON.parse(localStorage.getItem('becool-cookie-preferences') || '{}').analytics) }
  catch { return false }
}

export const trackCommerceEvent = (event_name, details = {}) => {
  if (!analyticsAllowed()) return Promise.resolve()
  return recordCommerceEvent({ session_id: sessionId, event_name, ...details }).catch(() => {})
}
