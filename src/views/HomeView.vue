<script setup lang="ts">
import { computed, inject } from 'vue'
import { RouterLink } from 'vue-router'
import ListingCard from '@/components/ListingCard.vue'
import MapExplorer from '@/components/MapExplorer.vue'
import SectionCard from '@/components/SectionCard.vue'
import { sellers } from '@/data/mockMarket'
import type { createMarketStore } from '@/stores/marketStore'
import type { Listing } from '@/types/market'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')

const topListing = computed<Listing | undefined>(() => marketStore?.activeListing)

function sellerName(listingId: string) {
  const sellerId = marketStore?.listings.find((item) => item.id === listingId)?.sellerId ?? 's1'
  return sellers[sellerId]?.name ?? '未知賣家'
}
</script>

<template>
  <div v-if="marketStore" class="page-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">在地化・永續・社區信任</p>
        <h2>把二手交易做成鄰里中的日常協作</h2>
        <p class="lead">
          從附近商品、賣家信任分數到面交點建議，所有互動都優先支援面交與鄰近交易。
        </p>
      </div>
      <div class="hero-actions">
        <RouterLink to="/map" class="primary-btn">開啟地圖</RouterLink>
        <RouterLink to="/chat" class="secondary-btn">查看訊息</RouterLink>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">搜尋與篩選</p>
          <h2>附近商品</h2>
        </div>
        <button
          class="ghost-btn"
          @click="marketStore.setLocationMode(marketStore.locationMode === 'granted' ? 'denied' : 'granted')"
        >
          {{ marketStore.locationMode === 'granted' ? '關閉定位' : '開啟定位' }}
        </button>
      </div>
      <div class="filters">
        <label>
          <span class="sr-only">搜尋商品</span>
          <input v-model="marketStore.searchTerm" type="search" placeholder="搜尋家具、家飾、收納..." />
        </label>
        <button
          v-for="category in marketStore.categories"
          :key="category"
          class="filter-chip"
          :class="{ active: category === marketStore.categoryFilter }"
          @click="marketStore.categoryFilter = category"
        >
          {{ category }}
        </button>
      </div>
    </section>

    <section class="content-grid">
      <SectionCard>
        <template #title>
          <div>
            <p class="eyebrow">清單</p>
            <h2>鄰近商品</h2>
          </div>
        </template>
        <div class="listing-grid">
          <ListingCard
            v-for="listing in marketStore.filteredListings"
            :key="listing.id"
            :listing="listing"
            :seller-name="sellerName(listing.id)"
            :selected="listing.id === marketStore.activeListingId"
            @select="marketStore.selectListing"
          />
        </div>
      </SectionCard>

      <MapExplorer
        :listings="marketStore.filteredListings"
        :active-id="marketStore.activeListingId"
        :location-mode="marketStore.locationMode"
        @select="marketStore.selectListing"
      />
    </section>

    <section class="content-grid compact">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">焦點商品</p>
            <h2>{{ topListing?.title }}</h2>
          </div>
          <RouterLink v-if="topListing" :to="`/listings/${topListing.id}`" class="secondary-btn">查看詳情</RouterLink>
        </div>
        <p class="muted">{{ topListing?.description }}</p>
        <div class="inline-stats">
          <span>距離 {{ topListing?.distanceKm }} km</span>
          <span>面交提示：{{ topListing?.meetupHint }}</span>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">社區動態</p>
            <h2>即時協調</h2>
          </div>
        </div>
        <p class="muted">從商品頁直接進入對話，快速確認細節與面交時間。</p>
        <RouterLink to="/chat" class="primary-btn">前往聊天</RouterLink>
      </section>
    </section>
  </div>
</template>
