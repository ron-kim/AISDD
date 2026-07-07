<script setup lang="ts">
import { inject, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppShell from '@/components/AppShell.vue'
import { useLocale } from '@/composables/locale'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>

const marketStore = inject<MarketStore>('marketStore')
const { t } = useLocale()

onMounted(() => {
  if (!marketStore) {
    console.error('marketStore injection failed')
    return
  }

  void marketStore.hydrate().catch((error) => {
    console.error('Failed to hydrate market store', error)
  })
})
</script>

<template>
  <AppShell>
    <section v-if="!marketStore" class="panel">
      <p class="eyebrow">{{ t('app.startupErrorTitle') }}</p>
      <h2>{{ t('app.startupErrorTitle') }}</h2>
      <p class="muted">{{ t('app.startupErrorBody') }}</p>
    </section>

    <RouterView />
  </AppShell>
</template>
