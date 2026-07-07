<script setup lang="ts">
import { computed, inject } from 'vue'
import { RouterLink } from 'vue-router'
import ListingCard from '@/components/ListingCard.vue'
import MapExplorer from '@/components/MapExplorer.vue'
import SectionCard from '@/components/SectionCard.vue'
import { sellers } from '@/data/mockMarket'
import { formatDistance, t, text } from '@/composables/locale'
import type { createMarketStore } from '@/stores/marketStore'
import type { Listing } from '@/types/market'

type MarketStore = ReturnType<typeof createMarketStore>
const marketStore = inject<MarketStore>('marketStore')

const topListing = computed<Listing | undefined>(() => marketStore?.activeListing)

function sellerName(listingId: string) {
  const sellerId = marketStore?.listings.find((item) => item.id === listingId)?.sellerId ?? 's1'
  return sellers[sellerId]?.name ?? t('common.unknownSeller')
}

function handleCountyChange(event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) return
  marketStore?.setCountyFilter(target.value)
}

function handleDistrictChange(event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) return
  marketStore?.setDistrictFilter(target.value)
}
</script>

<template>
  <div v-if="marketStore" class="page-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">{{ t('home.heroEyebrow') }}</p>
        <h2>{{ t('home.heroTitle') }}</h2>
        <p class="lead">{{ t('home.heroLead') }}</p>
      </div>
      <div class="hero-actions">
        <RouterLink to="/map" class="primary-btn">{{ t('home.openMap') }}</RouterLink>
        <RouterLink to="/chat" class="secondary-btn">{{ t('home.openChat') }}</RouterLink>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">{{ t('home.searchTitle') }}</p>
          <h2>{{ t('home.searchTitle') }}</h2>
        </div>
        <button
          class="ghost-btn"
          @click="marketStore.setLocationMode(marketStore.locationMode === 'granted' ? 'denied' : 'granted')"
        >
          {{ marketStore.locationMode === 'granted' ? t('home.locationEnabled') : t('home.locationDisabled') }}
        </button>
      </div>
      <div class="filters">
        <label>
          <span class="sr-only">{{ t('home.searchTitle') }}</span>
          <input v-model="marketStore.searchTerm" type="search" :placeholder="t('common.searchPlaceholder')" />
        </label>
        <button
          v-for="category in marketStore.categories"
          :key="category.id"
          class="filter-chip"
          :class="{ active: category.id === marketStore.categoryFilter }"
          @click="marketStore.categoryFilter = category.id"
        >
          {{ category.label }}
        </button>
      </div>
      <div class="location-filters">
        <label class="filter-field">
          <span>{{ t('filters.county') }}</span>
          <select :value="marketStore.countyFilter" @change="handleCountyChange">
            <option v-for="option in marketStore.countyOptions" :key="option.id" :value="option.id">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="filter-field">
          <span>{{ t('filters.district') }}</span>
          <select
            :value="marketStore.districtFilter"
            :disabled="marketStore.countyFilter === 'all'"
            @change="handleDistrictChange"
          >
            <option v-if="marketStore.countyFilter === 'all'" value="all">
              {{ t('filters.selectCountyFirst') }}
            </option>
            <option v-else v-for="option in marketStore.districtOptions" :key="option.id" :value="option.id">
              {{ option.label }}
            </option>
          </select>
        </label>
      </div>
    </section>

    <section class="content-grid">
      <SectionCard>
        <template #title>
          <div>
            <p class="eyebrow">{{ t('home.searchTitle') }}</p>
            <h2>{{ t('home.searchTitle') }}</h2>
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
        <p v-if="marketStore.filteredListings.length === 0" class="muted">{{ t('home.noResults') }}</p>
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
            <p class="eyebrow">{{ t('home.selectedTitle') }}</p>
            <h2>{{ text(topListing?.title) }}</h2>
          </div>
          <RouterLink v-if="topListing" :to="`/listings/${topListing.id}`" class="secondary-btn">
            {{ t('common.viewDetails') }}
          </RouterLink>
        </div>
        <p class="muted">{{ text(topListing?.description) || t('home.emptyLead') }}</p>
        <div class="inline-stats">
          <span>{{ formatDistance(topListing?.distanceKm ?? 0) }}</span>
          <span>{{ text(topListing?.meetupHint) }}</span>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">{{ t('home.supportEyebrow') }}</p>
            <h2>{{ t('home.supportTitle') }}</h2>
          </div>
        </div>
        <p class="muted">{{ t('home.supportBody') }}</p>
        <RouterLink to="/chat" class="primary-btn">{{ t('home.openChat') }}</RouterLink>
      </section>
    </section>
  </div>
</template>
