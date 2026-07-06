<script setup lang="ts">
import { inject } from 'vue'
import MapExplorer from '@/components/MapExplorer.vue'
import SectionCard from '@/components/SectionCard.vue'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')
</script>

<template>
  <div v-if="marketStore" class="page-grid">
    <MapExplorer
      :listings="marketStore.filteredListings"
      :active-id="marketStore.activeListingId"
      :location-mode="marketStore.locationMode"
      @select="marketStore.selectListing"
    />

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">Synchronized view</p>
          <h2>Map and list stay aligned</h2>
        </div>
      </template>
      <p class="muted">Selecting a pin updates the listing focus, trust view, chat flow, and meetup suggestions.</p>
    </SectionCard>
  </div>
</template>
