<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useLocale } from '@/composables/locale'
import { useTheme } from '@/composables/theme'

const { isEnglish, t, toggleLocale } = useLocale()
const { isDark, toggleTheme } = useTheme()
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">{{ t('app.brand') }}</p>
        <h1>{{ t('app.title') }}</h1>
      </div>
      <nav class="nav">
        <button class="theme-toggle nav-link" type="button" :aria-pressed="isDark" @click="toggleTheme">
          {{ isDark ? t('theme.light') : t('theme.dark') }}
        </button>
        <button class="language-toggle nav-link" type="button" :aria-pressed="isEnglish" @click="toggleLocale">
          {{ isEnglish ? t('language.switchToChinese') : t('language.switchToEnglish') }}
        </button>
        <RouterLink to="/" class="nav-link">{{ t('nav.browse') }}</RouterLink>
        <RouterLink to="/map" class="nav-link">{{ t('nav.map') }}</RouterLink>
        <RouterLink to="/chat" class="nav-link">{{ t('nav.chat') }}</RouterLink>
        <RouterLink to="/meetup" class="nav-link">{{ t('nav.meetup') }}</RouterLink>
      </nav>
    </header>

    <main class="workspace">
      <slot />
    </main>
  </div>
</template>
