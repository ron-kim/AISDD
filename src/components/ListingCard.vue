<script setup lang="ts">
import { categoryLabel, formatCurrency, text } from '@/composables/locale'
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
      <span class="chip">{{ categoryLabel(listing.categoryId) }}</span>
      <span class="distance">{{ listing.distanceKm }} km</span>
    </div>
    <h3>{{ text(listing.title) }}</h3>
    <p class="listing-desc">{{ text(listing.description) }}</p>
    <div class="listing-meta">
      <strong>{{ formatCurrency(listing.price) }}</strong>
      <span>{{ sellerName }}</span>
    </div>
    <div class="tag-row">
      <span v-for="tag in listing.tags" :key="text(tag)" class="tag">{{ text(tag) }}</span>
    </div>
  </button>
</template>
