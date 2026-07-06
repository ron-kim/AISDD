import { computed, readonly, ref } from 'vue'

export type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'aisdd-theme'
const theme = ref<ThemeMode>('light')

let initialized = false

function canUseDom() {
  return typeof window !== 'undefined' && typeof document !== 'undefined'
}

function getSystemTheme(): ThemeMode {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(next: ThemeMode) {
  theme.value = next

  if (!canUseDom()) {
    return
  }

  document.documentElement.dataset.theme = next
  document.documentElement.style.colorScheme = next
}

export function initTheme() {
  if (!canUseDom() || initialized) {
    return theme.value
  }

  initialized = true

  const stored = window.localStorage.getItem(STORAGE_KEY)
  const initialTheme: ThemeMode =
    stored === 'light' || stored === 'dark' ? stored : getSystemTheme()

  applyTheme(initialTheme)

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleSystemThemeChange = () => {
    if (!window.localStorage.getItem(STORAGE_KEY)) {
      applyTheme(getSystemTheme())
    }
  }

  mediaQuery.addEventListener('change', handleSystemThemeChange)

  return theme.value
}

export function setTheme(next: ThemeMode) {
  if (canUseDom()) {
    window.localStorage.setItem(STORAGE_KEY, next)
  }

  applyTheme(next)
}

export function toggleTheme() {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

export function useTheme() {
  return {
    theme: readonly(theme),
    isDark: computed(() => theme.value === 'dark'),
    setTheme,
    toggleTheme,
  }
}
