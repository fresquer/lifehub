import { useAuth } from './useAuth'

const BASE = '/api'

/**
 * Fetch autenticado contra la API de LifeHub.
 * @param {string} path - Ruta relativa (ej: 'areas', 'projects')
 * @returns {Promise<Response>}
 */
export function useApi() {
  const { token } = useAuth()

  async function apiFetch(path, options = {}) {
    const url = path.startsWith('http') ? path : `${BASE}/${path.replace(/^\//, '')}`
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    if (token.value) {
      headers.Authorization = `Bearer ${token.value}`
    }
    return fetch(url, { ...options, headers })
  }

  async function get(path) {
    const res = await apiFetch(path)
    if (!res.ok) throw new Error(await res.text().catch(() => res.statusText))
    return res.json()
  }

  async function post(path, body) {
    const res = await apiFetch(path, { method: 'POST', body: JSON.stringify(body) })
    if (!res.ok) throw new Error(await res.text().catch(() => res.statusText))
    return res.json()
  }

  async function patch(path, body) {
    const res = await apiFetch(path, { method: 'PATCH', body: JSON.stringify(body) })
    if (!res.ok) throw new Error(await res.text().catch(() => res.statusText))
    return res.json()
  }

  async function del(path) {
    const res = await apiFetch(path, { method: 'DELETE' })
    if (!res.ok) throw new Error(await res.text().catch(() => res.statusText))
    if (res.status === 204) return null
    return res.json()
  }

  return { apiFetch, get, post, patch, delete: del }
}
