<script setup lang="ts">
import { computed, inject } from 'vue'
import MeetupSuggestions from '@/components/MeetupSuggestions.vue'
import SectionCard from '@/components/SectionCard.vue'
import { t } from '@/composables/locale'
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
        <p class="eyebrow">{{ t('meetup.eyebrow') }}</p>
        <h2>{{ t('meetup.title') }}</h2>
        <p class="lead">{{ t('meetup.lead') }}</p>
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
          <p class="eyebrow">{{ t('meetup.howEyebrow') }}</p>
          <h2>{{ t('meetup.howTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('meetup.howBody') }}</p>
    </SectionCard>
  </div>
</template>
