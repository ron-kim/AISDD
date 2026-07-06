<script setup lang="ts">
import { computed, inject, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import ChatPanel from '@/components/ChatPanel.vue'
import MeetupSuggestions from '@/components/MeetupSuggestions.vue'
import SectionCard from '@/components/SectionCard.vue'
import TrustScoreCard from '@/components/TrustScoreCard.vue'
import { sellers } from '@/data/mockMarket'
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
        <p class="eyebrow">{{ listing.category }}</p>
        <h2>{{ listing.title }}</h2>
        <p class="lead">{{ listing.description }}</p>
      </div>
      <div class="hero-actions">
        <RouterLink to="/chat" class="primary-btn" @click="marketStore.openConversationForListing(listing.id)">
          開始對話
        </RouterLink>
        <RouterLink to="/meetup" class="secondary-btn">選擇面交點</RouterLink>
      </div>
    </section>

    <section class="content-grid">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">商品資訊</p>
            <h2>NT$ {{ listing.price.toLocaleString() }}</h2>
          </div>
          <span class="score-badge">{{ listing.distanceKm }} km</span>
        </div>
        <div class="inline-stats">
          <span>地點：{{ listing.location }}</span>
          <span>賣家：{{ seller?.name }}</span>
          <span>面交提示：{{ listing.meetupHint }}</span>
        </div>
        <div class="tag-row">
          <span v-for="tag in listing.tags" :key="tag" class="tag">{{ tag }}</span>
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
          <p class="eyebrow">面交建議</p>
          <h2>公開地點優先</h2>
        </div>
      </template>
      <p class="muted">建議先確認商品狀況，再透過聊天共享選定的面交地點。</p>
    </SectionCard>
  </div>
</template>
