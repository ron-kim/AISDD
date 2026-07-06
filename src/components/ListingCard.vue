<script setup lang="ts">
import type { Listing } from '@/types/market'

defineProps<{
  listing: Listing
  sellerName: string
  selected?: boolean
}>()

defineEmits<{ select: [id: string] }>()
</script>

<template>
  <button class="listing-card" :class="{ selected }" @click="$emit('select', listing.id)">
    <div class="listing-top">
      <span class="chip">{{ listing.category }}</span>
      <span class="distance">{{ listing.distanceKm }} km</span>
    </div>
    <h3>{{ listing.title }}</h3>
    <p class="listing-desc">{{ listing.description }}</p>
    <div class="listing-meta">
      <strong>NT$ {{ listing.price.toLocaleString() }}</strong>
      <span>{{ sellerName }}</span>
    </div>
    <div class="tag-row">
      <span v-for="tag in listing.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
  </button>
</template>
