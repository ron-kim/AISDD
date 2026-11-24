<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { formatCurrency, t, tf, text } from '@/composables/locale'
import type { DealEvaluation } from '@/types/market'

defineProps<{ deals: DealEvaluation[]; watched: (listingId: string) => boolean }>()
defineEmits<{ watch: [listingId: string]; contact: [listingId: string] }>()
</script>

<template>
  <ol class="deal-list">
    <li v-for="(deal, index) in deals" :key="deal.listing.id" class="deal-card">
      <div class="deal-card-head">
        <div>
          <span class="deal-rank">#{{ index + 1 }}</span>
          <h3>{{ text(deal.listing.title) }}</h3>
          <p class="muted">{{ text(deal.listing.location) }} · {{ deal.listing.distanceKm }} {{ t('common.kmUnit') }}</p>
        </div>
        <div class="deal-score" :class="`verdict-${deal.verdict}`">
          <strong>{{ deal.score }}</strong>
          <span>{{ t(`deals.verdict.${deal.verdict}`) }}</span>
        </div>
      </div>

      <dl class="deal-figures">
        <div>
          <dt>{{ t('deals.col.price') }}</dt>
          <dd>{{ formatCurrency(deal.listing.price) }}</dd>
        </div>
        <div>
          <dt>{{ t('deals.col.travel') }}</dt>
          <dd>+ {{ formatCurrency(deal.transportCost) }}</dd>
        </div>
        <div class="deal-figure-strong">
          <dt>{{ t('deals.col.landed') }}</dt>
          <dd>{{ formatCurrency(deal.landedCost) }}</dd>
        </div>
        <div>
          <dt>{{ t('deals.col.reference') }}</dt>
          <dd>{{ formatCurrency(deal.referencePrice) }}</dd>
        </div>
        <div>
          <dt>{{ t('deals.col.savings') }}</dt>
          <dd>{{ deal.savingsPercent }}%</dd>
        </div>
        <div>
          <dt>{{ t('deals.col.trend') }}</dt>
          <dd :class="`trend-${deal.priceTrend}`">
            {{ t(`deals.trend.${deal.priceTrend}`) }}
            <small>{{ tf('deals.lowestRecent', { price: formatCurrency(deal.lowestRecentPrice) }) }}</small>
          </dd>
        </div>
        <div>
          <dt>{{ t('deals.col.trust') }}</dt>
          <dd>{{ deal.trustScore ?? '—' }}</dd>
        </div>
      </dl>

      <div v-if="deal.warnings.length" class="tag-row">
        <span v-for="warning in deal.warnings" :key="warning" class="tag warning-tag">
          {{ t(`deals.warning.${warning}`) }}
        </span>
      </div>

      <div class="hero-actions">
        <RouterLink :to="`/listings/${deal.listing.id}`" class="secondary-btn">{{ t('deals.viewListing') }}</RouterLink>
        <button
          class="ghost-btn"
          type="button"
          :disabled="watched(deal.listing.id)"
          @click="$emit('watch', deal.listing.id)"
        >
          {{ watched(deal.listing.id) ? t('deals.watching') : t('deals.watchThis') }}
        </button>
        <button class="primary-btn" type="button" @click="$emit('contact', deal.listing.id)">
          {{ t('deals.contactSeller') }}
        </button>
      </div>
    </li>
  </ol>
</template>
