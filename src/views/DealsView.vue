<script setup lang="ts">
import { computed, inject, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import DealTable from '@/components/DealTable.vue'
import SectionCard from '@/components/SectionCard.vue'
import { sellers } from '@/data/mockMarket'
import { formatCurrency, formatDateTime, t, tf, text } from '@/composables/locale'
import { transportModes, watchMatches } from '@/services/dealHunter'
import type { createDealStore } from '@/stores/dealStore'
import type { createMarketStore } from '@/stores/marketStore'
import type { TransportMode, WatchItem } from '@/types/market'

const marketStore = inject<ReturnType<typeof createMarketStore>>('marketStore')
const dealStore = inject<ReturnType<typeof createDealStore>>('dealStore')
const route = useRoute()
const router = useRouter()

// Setup form (mirrors preferences until saved)
const setupMode = ref<TransportMode>(dealStore?.preferences.transportMode ?? 'mrt')
const setupDistance = ref(dealStore?.preferences.maxDistanceKm ?? 5)
const setupThreshold = ref(dealStore?.preferences.alertThresholdPercent ?? 5)

function saveSetup() {
  dealStore?.completeSetup({
    transportMode: setupMode.value,
    maxDistanceKm: Math.max(0.5, Number(setupDistance.value) || 5),
    alertThresholdPercent: Math.min(90, Math.max(1, Number(setupThreshold.value) || 5)),
  })
}

// Hunt form
const budgetInput = ref<string>('')
watch(budgetInput, (value) => {
  if (!dealStore) return
  const parsed = Number(value)
  dealStore.query.budget = value === '' || !Number.isFinite(parsed) || parsed <= 0 ? null : parsed
})

const listingName = (listingId: string) =>
  text(marketStore?.listings.find((listing) => listing.id === listingId)?.title) || listingId
const namesOf = (ids: string[]) => ids.map(listingName).join('、')

// Check before buying — supports /deals?check=<listingId>
watch(
  () => route.query.check,
  (check) => {
    if (typeof check === 'string' && dealStore) dealStore.checkListing(check)
  },
  { immediate: true },
)

function onPriceCheckChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  dealStore?.checkListing(value)
  void router.replace({ query: value ? { check: value } : {} })
}

// Watchlist
const watchKeyword = ref('')
const watchTarget = ref('')
function addKeywordWatch() {
  const target = Number(watchTarget.value)
  dealStore?.addWatch({
    keyword: watchKeyword.value,
    targetPrice: watchTarget.value && Number.isFinite(target) && target > 0 ? target : null,
  })
  watchKeyword.value = ''
  watchTarget.value = ''
}

function watchLabel(watchItem: WatchItem) {
  return watchItem.listingId
    ? tf('deals.watchListing', { name: listingName(watchItem.listingId) })
    : tf('deals.watchKeyword', { keyword: watchItem.keyword ?? '' })
}

function watchMatchCount(watchItem: WatchItem) {
  return marketStore ? watchMatches(watchItem, marketStore.listings).length : 0
}

// Never contact a seller without explicit confirmation
const pendingContactId = ref<string | null>(null)
const pendingSellerName = computed(() => {
  const listing = marketStore?.listings.find((item) => item.id === pendingContactId.value)
  return listing ? sellers[listing.sellerId]?.name ?? t('common.unknownSeller') : ''
})

async function confirmContact() {
  const listingId = pendingContactId.value
  pendingContactId.value = null
  if (!listingId || !marketStore) return
  marketStore.selectListing(listingId)
  await marketStore.ensureConversation(listingId)
  await router.push('/chat')
}
</script>

<template>
  <div v-if="marketStore && dealStore" class="page-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">{{ t('deals.eyebrow') }}</p>
        <h2>{{ t('deals.title') }}</h2>
        <p class="lead">{{ t('deals.lead') }}</p>
      </div>
    </section>

    <!-- Setup -->
    <SectionCard v-if="!dealStore.preferences.setupComplete">
      <template #title>
        <div>
          <p class="eyebrow">{{ t('deals.setupEyebrow') }}</p>
          <h2>{{ t('deals.setupTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('deals.setupBody') }}</p>
      <form class="deal-form" @submit.prevent="saveSetup">
        <fieldset class="filter-field">
          <legend>{{ t('deals.transportMode') }}</legend>
          <div class="filters">
            <button
              v-for="mode in transportModes"
              :key="mode"
              type="button"
              class="filter-chip"
              :class="{ active: setupMode === mode }"
              :aria-pressed="setupMode === mode"
              @click="setupMode = mode"
            >
              {{ t(`deals.transport.${mode}`) }}
            </button>
          </div>
        </fieldset>
        <label class="filter-field">
          <span>{{ t('deals.maxDistance') }}</span>
          <input v-model.number="setupDistance" type="number" min="0.5" step="0.5" />
        </label>
        <label class="filter-field">
          <span>{{ t('deals.alertThreshold') }}</span>
          <input v-model.number="setupThreshold" type="number" min="1" max="90" />
        </label>
        <div class="hero-actions">
          <button class="primary-btn" type="submit">{{ t('deals.saveSetup') }}</button>
        </div>
      </form>
    </SectionCard>

    <template v-else>
      <section class="panel setup-summary">
        <p class="muted">
          {{
            tf('deals.setupSummary', {
              mode: t(`deals.transport.${dealStore.preferences.transportMode}`),
              km: dealStore.preferences.maxDistanceKm,
              pct: dealStore.preferences.alertThresholdPercent,
            })
          }}
        </p>
        <button class="ghost-btn" type="button" @click="dealStore.reopenSetup()">{{ t('deals.editSetup') }}</button>
      </section>

      <!-- Alerts -->
      <SectionCard v-if="dealStore.alerts.length">
        <template #title>
          <div>
            <p class="eyebrow">{{ t('deals.watchEyebrow') }}</p>
            <h2>{{ t('deals.alertsTitle') }}</h2>
          </div>
        </template>
        <ul class="alert-list">
          <li v-for="alert in dealStore.alerts" :key="alert.id" class="alert-item">
            <div>
              <strong>{{ listingName(alert.listingId) }}</strong>
              <p class="muted">
                {{
                  tf('deals.alertDrop', {
                    old: formatCurrency(alert.oldPrice),
                    new: formatCurrency(alert.newPrice),
                    pct: alert.dropPercent,
                  })
                }}
                <span v-if="alert.hitTarget" class="tag">{{ t('deals.alertHitTarget') }}</span>
              </p>
            </div>
            <div class="hero-actions">
              <RouterLink :to="`/listings/${alert.listingId}`" class="secondary-btn">{{ t('deals.viewListing') }}</RouterLink>
              <button class="ghost-btn" type="button" @click="dealStore.dismissAlert(alert.id)">{{ t('deals.dismiss') }}</button>
            </div>
          </li>
        </ul>
      </SectionCard>

      <!-- Hunt -->
      <SectionCard>
        <template #title>
          <div>
            <p class="eyebrow">{{ t('deals.huntEyebrow') }}</p>
            <h2>{{ t('deals.huntTitle') }}</h2>
          </div>
        </template>
        <form class="deal-form" @submit.prevent="dealStore.hunt()">
          <label class="filter-field">
            <span>{{ t('deals.keyword') }}</span>
            <input v-model="dealStore.query.keyword" type="search" :placeholder="t('deals.keywordPlaceholder')" />
          </label>
          <label class="filter-field">
            <span>{{ t('deals.budget') }}</span>
            <input v-model="budgetInput" type="number" min="0" step="50" :placeholder="t('deals.budgetPlaceholder')" />
          </label>
          <fieldset class="filter-field">
            <legend>{{ t('deals.category') }}</legend>
            <div class="filters">
              <button
                v-for="category in marketStore.categories"
                :key="category.id"
                type="button"
                class="filter-chip"
                :class="{ active: dealStore.query.categoryId === category.id }"
                @click="dealStore.query.categoryId = category.id"
              >
                {{ category.label }}
              </button>
            </div>
          </fieldset>
          <div class="hero-actions">
            <button class="primary-btn" type="submit">{{ t('deals.huntAction') }}</button>
          </div>
        </form>

        <div v-if="dealStore.huntResult" class="hunt-result" aria-live="polite">
          <p class="muted">
            {{ tf('deals.checkedSummary', { n: dealStore.huntResult.checkedListingIds.length }) }}
            {{ namesOf(dealStore.huntResult.checkedListingIds) }}
          </p>
          <p class="muted small">{{ tf('deals.checkedAt', { time: formatDateTime(dealStore.huntResult.ranAt) }) }}</p>
          <h3>{{ t('deals.picksTitle') }}</h3>
          <DealTable
            v-if="dealStore.huntResult.picks.length"
            :deals="dealStore.huntResult.picks"
            :watched="dealStore.isWatchingListing"
            @watch="(id) => dealStore?.addWatch({ listingId: id, targetPrice: null })"
            @contact="(id) => (pendingContactId = id)"
          />
          <p v-else class="muted">{{ t('deals.noPicks') }}</p>
        </div>
      </SectionCard>

      <section class="content-grid">
        <!-- Check before buying -->
        <SectionCard>
          <template #title>
            <div>
              <p class="eyebrow">{{ t('deals.priceCheckEyebrow') }}</p>
              <h2>{{ t('deals.priceCheckTitle') }}</h2>
            </div>
          </template>
          <p class="muted">{{ t('deals.priceCheckBody') }}</p>
          <label class="filter-field deal-form">
            <span>{{ t('deals.chooseListing') }}</span>
            <select :value="dealStore.priceCheckListingId" @change="onPriceCheckChange">
              <option value="">{{ t('deals.chooseListingPlaceholder') }}</option>
              <option v-for="listing in marketStore.listings" :key="listing.id" :value="listing.id">
                {{ text(listing.title) }} · {{ formatCurrency(listing.price) }}
              </option>
            </select>
          </label>

          <div v-if="dealStore.priceCheck" class="hunt-result" aria-live="polite">
            <DealTable
              :deals="[dealStore.priceCheck.target]"
              :watched="dealStore.isWatchingListing"
              @watch="(id) => dealStore?.addWatch({ listingId: id, targetPrice: null })"
              @contact="(id) => (pendingContactId = id)"
            />
            <p class="muted">
              {{
                dealStore.priceCheck.checkedListingIds.length
                  ? tf('deals.comparedWith', { names: namesOf(dealStore.priceCheck.checkedListingIds) })
                  : t('deals.noneCompared')
              }}
            </p>
            <p v-if="dealStore.priceCheck.verdict === 'best-available'" class="verdict-banner verdict-great">
              {{ t('deals.bestAvailable') }}
            </p>
            <template v-else>
              <p class="verdict-banner verdict-fair">
                {{ tf('deals.cheaperExists', { n: dealStore.priceCheck.cheaper.length }) }}
              </p>
              <ul class="alert-list">
                <li v-for="option in dealStore.priceCheck.cheaper" :key="option.listing.id" class="alert-item">
                  <div>
                    <strong>{{ text(option.listing.title) }}</strong>
                    <p class="muted">
                      {{ formatCurrency(option.landedCost) }} ·
                      {{
                        tf('deals.cheaperBy', {
                          amount: formatCurrency(dealStore.priceCheck.target.landedCost - option.landedCost),
                        })
                      }}
                    </p>
                  </div>
                  <button class="secondary-btn" type="button" @click="dealStore.checkListing(option.listing.id)">
                    {{ t('deals.checkDeal') }}
                  </button>
                </li>
              </ul>
            </template>
          </div>
        </SectionCard>

        <!-- Watchlist -->
        <SectionCard>
          <template #title>
            <div>
              <p class="eyebrow">{{ t('deals.watchEyebrow') }}</p>
              <h2>{{ t('deals.watchTitle') }}</h2>
            </div>
          </template>
          <p class="muted">{{ t('deals.watchBody') }}</p>
          <form class="deal-form" @submit.prevent="addKeywordWatch">
            <label class="filter-field">
              <span>{{ t('deals.keyword') }}</span>
              <input v-model="watchKeyword" type="text" :placeholder="t('deals.watchKeywordPlaceholder')" />
            </label>
            <label class="filter-field">
              <span>{{ t('deals.targetPrice') }}</span>
              <input v-model="watchTarget" type="number" min="0" step="50" />
            </label>
            <div class="hero-actions">
              <button class="secondary-btn" type="submit" :disabled="!watchKeyword.trim()">{{ t('deals.addWatch') }}</button>
            </div>
          </form>

          <ul v-if="dealStore.watchlist.length" class="alert-list">
            <li v-for="watchItem in dealStore.watchlist" :key="watchItem.id" class="alert-item">
              <div>
                <strong>{{ watchLabel(watchItem) }}</strong>
                <p class="muted">
                  {{ tf('deals.matches', { n: watchMatchCount(watchItem) }) }}
                  <template v-if="watchItem.targetPrice">
                    · {{ tf('deals.target', { price: formatCurrency(watchItem.targetPrice) }) }}
                  </template>
                </p>
              </div>
              <button class="ghost-btn" type="button" @click="dealStore.removeWatch(watchItem.id)">
                {{ t('deals.removeWatch') }}
              </button>
            </li>
          </ul>
          <p v-else class="muted">{{ t('deals.emptyWatch') }}</p>

          <div class="hero-actions">
            <button
              class="primary-btn"
              type="button"
              :disabled="dealStore.scanning || !dealStore.watchlist.length"
              @click="dealStore.runWatchlistCheck()"
            >
              {{ dealStore.scanning ? t('deals.checking') : t('deals.runCheck') }}
            </button>
          </div>
          <p v-if="dealStore.lastScan" class="muted" aria-live="polite">
            {{
              dealStore.lastScan.newAlerts
                ? tf('deals.scanAlerts', { n: dealStore.lastScan.newAlerts })
                : t('deals.scanQuiet')
            }}
            ({{ formatDateTime(dealStore.lastScan.at) }})
          </p>
        </SectionCard>
      </section>
    </template>

    <div v-if="pendingContactId" class="confirm-backdrop" role="presentation" @click.self="pendingContactId = null">
      <section class="panel confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-contact-title">
        <p class="eyebrow">{{ t('deals.eyebrow') }}</p>
        <h2 id="confirm-contact-title">{{ t('deals.confirmContactTitle') }}</h2>
        <p class="muted">{{ tf('deals.confirmContactBody', { seller: pendingSellerName }) }}</p>
        <div class="hero-actions">
          <button class="primary-btn" type="button" @click="confirmContact">{{ t('deals.confirmContact') }}</button>
          <button class="ghost-btn" type="button" @click="pendingContactId = null">{{ t('deals.cancel') }}</button>
        </div>
      </section>
    </div>
  </div>
</template>
