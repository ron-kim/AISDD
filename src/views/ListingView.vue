<script setup lang="ts">
import { computed, inject, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import ChatPanel from '@/components/ChatPanel.vue'
import MeetupSuggestions from '@/components/MeetupSuggestions.vue'
import SectionCard from '@/components/SectionCard.vue'
import TrustScoreCard from '@/components/TrustScoreCard.vue'
import { sellers } from '@/data/mockMarket'
import { categoryLabel, formatCurrency, t, text } from '@/composables/locale'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')
const route = useRoute()

const listingId = computed(() => String(route.params.id))
const listing = computed(() => marketStore?.listings.find((item) => item.id === listingId.value))
const seller = computed(() => (listing.value ? sellers[listing.value.sellerId] : undefined))

onMounted(() => {
  if (listing.value) {
    marketStore?.selectListing(listing.value.id)
    marketStore?.loadConversation(listing.value.id)
  }
})

function chooseMeetup(id: string) {
  if (listing.value) marketStore?.chooseMeetupPoint(listing.value.id, id)
}
</script>

<template>
  <div v-if="marketStore && listing" class="page-grid listing-layout">
    <section class="hero panel listing-hero">
      <div>
        <p class="eyebrow">{{ categoryLabel(listing.categoryId) }}</p>
        <h2>{{ text(listing.title) }}</h2>
        <p class="lead">{{ text(listing.description) }}</p>
      </div>
      <div class="hero-actions">
        <RouterLink to="/chat" class="primary-btn" @click="marketStore.openConversationForListing(listing.id)">
          {{ t('listing.startChat') }}
        </RouterLink>
        <RouterLink to="/meetup" class="secondary-btn">{{ t('listing.chooseMeetup') }}</RouterLink>
      </div>
    </section>

    <section class="content-grid">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">{{ t('listing.productInfo') }}</p>
            <h2>{{ formatCurrency(listing.price) }}</h2>
          </div>
          <span class="score-badge">{{ listing.distanceKm }} {{ t('common.kmUnit') }}</span>
        </div>
        <div class="inline-stats">
          <span>{{ text(listing.location) }}</span>
          <span>{{ seller?.name ?? t('common.unknownSeller') }}</span>
          <span>{{ t('listing.meetupAdvice') }}：{{ text(listing.meetupHint) }}</span>
        </div>
        <div class="tag-row">
          <span v-for="tag in listing.tags" :key="text(tag)" class="tag">{{ text(tag) }}</span>
        </div>
      </section>

      <TrustScoreCard :profile="marketStore.activeTrustProfile" />
    </section>

    <section class="content-grid">
      <ChatPanel
        v-if="marketStore.activeConversation"
        :conversation="marketStore.activeConversation"
        @send="marketStore.sendMessage"
      />
      <MeetupSuggestions
        :suggestions="marketStore.activeMeetupSuggestions"
        :selected-id="marketStore.selectedMeetupPointId"
        @choose="chooseMeetup"
      />
    </section>

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">{{ t('listing.meetupAdvice') }}</p>
          <h2>{{ t('listing.meetupHeading') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('listing.meetupBody') }}</p>
    </SectionCard>
  </div>
</template>
