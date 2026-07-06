<script setup lang="ts">
import { computed, inject } from 'vue'
import MeetupSuggestions from '@/components/MeetupSuggestions.vue'
import SectionCard from '@/components/SectionCard.vue'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')

const activeSuggestions = computed(() => marketStore?.activeMeetupSuggestions ?? [])

function handleChoose(id: string) {
  if (!marketStore) return
  marketStore.chooseMeetupPoint(marketStore.selectedMeetupListingId, id)
}
</script>

<template>
  <div v-if="marketStore" class="page-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">Meetup suggestions</p>
        <h2>Public, nearby, and easy to find</h2>
        <p class="lead">Keep trades simple by choosing a visible location that both people can reach quickly.</p>
      </div>
    </section>

    <MeetupSuggestions
      :suggestions="activeSuggestions"
      :selected-id="marketStore.selectedMeetupPointId"
      @choose="handleChoose"
    />

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">How it works</p>
          <h2>Share your choice in chat</h2>
        </div>
      </template>
      <p class="muted">The selected meetup point stays in state so it can be shared in conversation or copied for offline coordination.</p>
    </SectionCard>
  </div>
</template>
