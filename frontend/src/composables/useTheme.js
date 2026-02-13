import { ref, onMounted } from 'vue'

const STORAGE_KEY = 'lifehub-theme'

function getStoredTheme() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch (_) {}
  return 'dark'
}

function applyThemeToDocument(theme) {
  document.documentElement.setAttribute('data-theme', theme)
}

export function useTheme() {
  const theme = ref(getStoredTheme())

  function setTheme(value) {
    if (value !== 'light' && value !== 'dark') return
    theme.value = value
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch (_) {}
    applyThemeToDocument(value)
  }

  function toggle() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  onMounted(() => {
    applyThemeToDocument(theme.value)
  })

  return { theme, setTheme, toggle }
}

export function applyThemeFromStorage() {
  const stored = getStoredTheme()
  applyThemeToDocument(stored)
}
