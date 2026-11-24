import { computed, reactive, ref } from 'vue'
import { sellers } from '@/data/mockMarket'
import { marketService } from '@/services/marketService'
import {
  checkBeforeBuying,
  defaultDealPreferences,
  huntDeals,
  scanWatchlist,
  type DealContext,
} from '@/services/dealHunter'
import type { createMarketStore } from '@/stores/marketStore'
import type { DealAlert, DealHuntResult, DealPreferences, DealQuery, ListingPricing, WatchItem } from '@/types/market'

type MarketStore = ReturnType<typeof createMarketStore>

const STORAGE_KEY = 'aisdd-deal-hunter'

interface PersistedState {
  preferences: DealPreferences
  watchlist: WatchItem[]
  alerts: DealAlert[]
}

function loadPersisted(): Partial<PersistedState> {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Partial<PersistedState>) : {}
  } catch {
    return {}
  }
}

export function createDealStore(market: MarketStore) {
  const persisted = loadPersisted()
  const preferences = ref<DealPreferences>({ ...defaultDealPreferences, ...persisted.preferences })
  const watchlist = ref<WatchItem[]>(persisted.watchlist ?? [])
  const alerts = ref<DealAlert[]>(persisted.alerts ?? [])
  const pricing = reactive<Record<string, ListingPricing>>({})
  const query = reactive<DealQuery>({ keyword: '', budget: null, categoryId: 'all' })
  const lastHunt = ref<{ query: DealQuery; ranAt: string } | null>(null)
  const priceCheckListingId = ref<string>('')
  const scanning = ref(false)
  const lastScan = ref<{ at: string; newAlerts: number } | null>(null)
  let priceRound = 0

  function persist() {
    try {
      const state: PersistedState = {
        preferences: preferences.value,
        watchlist: watchlist.value,
        alerts: alerts.value,
      }
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage can be unavailable (private mode); the session still works in memory.
    }
  }

  const context = computed<DealContext>(() => ({
    listings: market.listings,
    pricing,
    preferences: preferences.value,
    trustScore: (sellerId) => market.trustProfiles[sellerId]?.score ?? null,
    sellerVerified: (sellerId) => sellers[sellerId]?.verified ?? false,
  }))

  const priceCheck = computed(() =>
    priceCheckListingId.value ? checkBeforeBuying(context.value, priceCheckListingId.value) : undefined,
  )

  // Re-rank the last hunt whenever prices, trust data or preferences change.
  const huntResult = computed<DealHuntResult | null>(() =>
    lastHunt.value ? { ...huntDeals(context.value, lastHunt.value.query), ranAt: lastHunt.value.ranAt } : null,
  )

  async function hydrate() {
    Object.assign(pricing, await marketService.getListingPricing())
  }

  function completeSetup(next: Omit<DealPreferences, 'setupComplete'>) {
    preferences.value = { ...next, setupComplete: true }
    persist()
  }

  function reopenSetup() {
    preferences.value = { ...preferences.value, setupComplete: false }
  }

  function hunt() {
    lastHunt.value = { query: { ...query }, ranAt: new Date().toISOString() }
  }

  function checkListing(listingId: string) {
    priceCheckListingId.value = listingId
  }

  function isWatchingListing(listingId: string) {
    return watchlist.value.some((watch) => watch.listingId === listingId)
  }

  function addWatch(input: { listingId?: string; keyword?: string; targetPrice: number | null }) {
    const keyword = input.keyword?.trim()
    if (!input.listingId && !keyword) return
    if (input.listingId && isWatchingListing(input.listingId)) return
    const watch: WatchItem = {
      id: `watch-${Date.now()}-${watchlist.value.length}`,
      listingId: input.listingId,
      keyword: input.listingId ? undefined : keyword,
      targetPrice: input.targetPrice,
      baselines: {},
      createdAt: new Date().toISOString(),
    }
    // Record today's prices as the baseline without raising alerts.
    const seeded = scanWatchlist([watch], market.listings, preferences.value.alertThresholdPercent).watchlist[0]
    watchlist.value = [...watchlist.value, seeded]
    persist()
  }

  function removeWatch(watchId: string) {
    watchlist.value = watchlist.value.filter((watch) => watch.id !== watchId)
    alerts.value = alerts.value.filter((alert) => alert.watchId !== watchId)
    persist()
  }

  function dismissAlert(alertId: string) {
    alerts.value = alerts.value.filter((alert) => alert.id !== alertId)
    persist()
  }

  /** Pull the latest seller prices, record them, then scan the watchlist. */
  async function runWatchlistCheck() {
    if (scanning.value) return
    scanning.value = true
    try {
      const changes = await marketService.fetchPriceUpdates(priceRound)
      priceRound += 1
      const today = new Date().toISOString().slice(0, 10)
      for (const change of changes) {
        const listing = market.listings.find((item) => item.id === change.listingId)
        if (!listing || listing.price === change.price) continue
        listing.price = change.price
        pricing[listing.id]?.history.push({ date: today, price: change.price })
      }
      const result = scanWatchlist(watchlist.value, market.listings, preferences.value.alertThresholdPercent)
      watchlist.value = result.watchlist
      alerts.value = [...result.alerts, ...alerts.value]
      lastScan.value = { at: new Date().toISOString(), newAlerts: result.alerts.length }
      persist()
    } finally {
      scanning.value = false
    }
  }

  return reactive({
    preferences,
    watchlist,
    alerts,
    pricing,
    query,
    huntResult,
    priceCheckListingId,
    priceCheck,
    scanning,
    lastScan,
    hydrate,
    completeSetup,
    reopenSetup,
    hunt,
    checkListing,
    isWatchingListing,
    addWatch,
    removeWatch,
    dismissAlert,
    runWatchlistCheck,
  })
}
