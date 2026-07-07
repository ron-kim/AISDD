<script setup lang="ts">
import { computed, inject } from 'vue'
import ChatPanel from '@/components/ChatPanel.vue'
import SectionCard from '@/components/SectionCard.vue'
import { sellers } from '@/data/mockMarket'
import { text, t } from '@/composables/locale'
import type { createMarketStore } from '@/stores/marketStore'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')

const items = computed(() => marketStore?.conversations ?? [])

function sellerResponseTime(listingId: string) {
  const sellerId = listingId === 'cedar-chair' ? 's1' : listingId === 'bamboo-lamp' ? 's2' : 's3'
  return text(sellers[sellerId]?.responseTime) || t('common.averageResponse')
}
</script>

<template>
  <div v-if="marketStore" class="page-grid">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">{{ t('chat.listEyebrow') }}</p>
          <h2>{{ t('chat.listTitle') }}</h2>
        </div>
      </div>
      <div class="conversation-list">
        <button
          v-for="conversation in items"
          :key="conversation.id"
          class="conversation-item"
          :class="{ active: conversation.id === marketStore.activeConversationId }"
          @click="marketStore.selectConversation(conversation.id)"
        >
          <div>
            <strong>{{ conversation.sellerName }}</strong>
            <p>{{ sellerResponseTime(conversation.listingId) }}</p>
          </div>
          <span class="score-badge">{{ conversation.unread }} {{ t('common.unread') }}</span>
        </button>
      </div>
    </section>

    <ChatPanel
      v-if="marketStore.activeConversation"
      :conversation="marketStore.activeConversation"
      @send="marketStore.sendMessage"
    />

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">{{ t('chat.statusEyebrow') }}</p>
          <h2>{{ t('chat.statusTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('chat.statusBody') }}</p>
    </SectionCard>
  </div>
</template>
