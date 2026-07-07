<script setup lang="ts">
import { text, t } from '@/composables/locale'
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
        <p class="eyebrow">{{ t('map.eyebrow') }}</p>
        <h2>{{ t('map.title') }}</h2>
      </div>
      <span class="score-badge" :class="{ warning: locationMode === 'denied' }">
        {{ locationMode === 'granted' ? t('map.locationOn') : t('map.locationOff') }}
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
          <span>{{ text(listing.title) }}</span>
        </button>
      </template>
      <div v-else class="fallback-copy">
        <h3>{{ t('map.fallbackTitle') }}</h3>
        <p>{{ t('map.fallbackBody') }}</p>
      </div>
    </div>
  </section>
</template>
