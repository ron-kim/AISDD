<script setup lang="ts">
import { inject, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppShell from '@/components/AppShell.vue'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>

const marketStore = inject<MarketStore>('marketStore')

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
      <p class="eyebrow">Startup error</p>
      <h2>Market store unavailable</h2>
      <p class="muted">The app failed to initialize shared state. Check the browser console.</p>
    </section>

    <RouterView />
  </AppShell>
</template>
