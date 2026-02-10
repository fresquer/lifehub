import { ref, computed } from 'vue'

const TOKEN_KEY = 'lifehub_token'
const stored = localStorage.getItem(TOKEN_KEY)
const token = ref(stored)
const user = ref(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)

  async function fetchUser() {
    if (!token.value) return null
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      if (!res.ok) {
        logout()
        return null
      }
      user.value = await res.json()
      return user.value
    } catch {
      logout()
      return null
    }
  }

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
      user.value = null
    }
  }

  function logout() {
    setToken(null)
  }

  return {
    token,
    user,
    isAuthenticated,
    setToken,
    logout,
    fetchUser,
  }
}
