<script setup lang="ts">
import type { Listing } from '@/types/market'

defineProps<{
  listings: Listing[]
  activeId: string
  locationMode: 'granted' | 'denied'
}>()

defineEmits<{
  select: [id: string]
}>()
</script>

<template>
  <section class="map-explorer panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Map exploration</p>
        <h2>Nearby listings</h2>
      </div>
      <span class="score-badge" :class="{ warning: locationMode === 'denied' }">
        {{ locationMode === 'granted' ? 'Location on' : 'Location off' }}
      </span>
    </div>

    <div class="map-canvas" :class="{ fallback: locationMode === 'denied' }">
      <div class="map-grid" />
      <template v-if="locationMode === 'granted'">
        <button
          v-for="listing in listings"
          :key="listing.id"
          class="pin"
          :class="{ active: listing.id === activeId }"
          :style="{ left: `${listing.coordinates.x}%`, top: `${listing.coordinates.y}%` }"
          @click="$emit('select', listing.id)"
        >
          <span>{{ listing.title }}</span>
        </button>
      </template>
      <div v-else class="fallback-copy">
        <h3>Location is off, but browsing still works</h3>
        <p>Use search and the listing cards to explore manually, or re-enable location later.</p>
      </div>
    </div>
  </section>
</template>
