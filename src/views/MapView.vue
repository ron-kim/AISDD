<script setup lang="ts">
import { inject } from 'vue'
import MapExplorer from '@/components/MapExplorer.vue'
import SectionCard from '@/components/SectionCard.vue'
import { t } from '@/composables/locale'
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
          <p class="eyebrow">{{ t('map.panelEyebrow') }}</p>
          <h2>{{ t('map.panelTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('map.panelBody') }}</p>
    </SectionCard>
  </div>
</template>
