import type {
  CategoryId,
  DealAlert,
  DealEvaluation,
  DealHuntResult,
  DealPreferences,
  DealQuery,
  Listing,
  ListingPricing,
  TransportMode,
  WatchItem,
} from '@/types/market'

/**
 * Deal hunter engine: pure functions that rank listings by their real
 * ("landed") cost — asking price plus the round trip to the meetup —
 * against a new-retail reference price, recent price history and seller trust.
 * It never contacts sellers or reserves items; the UI asks the user first.
 */

export const transportModes: TransportMode[] = ['walk', 'bike', 'mrt', 'taxi']

export const defaultDealPreferences: DealPreferences = {
  setupComplete: false,
  transportMode: 'mrt',
  alertThresholdPercent: 5,
  maxDistanceKm: 5,
}

/** Round-trip cost (NT$) of travelling `distanceKm` each way to pick up an item. */
export function transportCost(distanceKm: number, mode: TransportMode): number {
  const oneWay = (() => {
    switch (mode) {
      case 'walk':
        return 0
      case 'bike':
        // YouBike: NT$10 per 30 minutes, roughly 6 km per half hour.
        return 10 * Math.max(1, Math.ceil(distanceKm / 6))
      case 'mrt':
        return Math.min(65, 20 + Math.round(distanceKm * 3))
      case 'taxi':
        return 85 + Math.round(Math.max(0, distanceKm - 1.25) * 25)
    }
  })()
  return oneWay * 2
}

export function matchesKeyword(listing: Listing, keyword: string): boolean {
  const term = keyword.trim().toLowerCase()
  if (!term) return true
  const haystack = [listing.title, listing.description, listing.location, ...listing.tags]
    .flatMap((value) => [value['zh-TW'], value.en])
    .join(' ')
    .toLowerCase()
  return term.split(/\s+/).every((part) => haystack.includes(part))
}

function priceTrend(listing: Listing, pricing?: ListingPricing): DealEvaluation['priceTrend'] {
  const first = pricing?.history[0]?.price
  if (first === undefined || first === listing.price) return 'flat'
  return listing.price < first ? 'down' : 'up'
}

export function evaluateDeal(
  listing: Listing,
  pricing: ListingPricing | undefined,
  preferences: DealPreferences,
  trustScore: number | null,
  sellerVerified: boolean,
  budget: number | null = null,
): DealEvaluation {
  const travel = transportCost(listing.distanceKm, preferences.transportMode)
  const landedCost = listing.price + travel
  const referencePrice = pricing?.referencePrice ?? listing.price
  const savingsPercent = Math.round(((referencePrice - landedCost) / referencePrice) * 100)
  const lowestRecentPrice = Math.min(listing.price, ...(pricing?.history.map((point) => point.price) ?? []))
  const trend = priceTrend(listing, pricing)

  const warnings: DealEvaluation['warnings'] = []
  if (listing.status === 'reserved') warnings.push('reserved')
  if (budget !== null && landedCost > budget) warnings.push('over-budget')
  if (!sellerVerified) warnings.push('unverified-seller')
  if (listing.distanceKm > preferences.maxDistanceKm) warnings.push('too-far')

  let score = Math.max(0, savingsPercent) * 0.65 + (trustScore ?? 60) * 0.35
  if (trend === 'down') score += 5
  if (trend === 'up') score -= 5
  if (warnings.includes('reserved')) score -= 20
  if (warnings.includes('over-budget')) score -= 15
  if (warnings.includes('unverified-seller')) score -= 5
  if (warnings.includes('too-far')) score -= 10
  score = Math.round(Math.min(100, Math.max(0, score)))

  const verdict: DealEvaluation['verdict'] = score >= 70 ? 'great' : score >= 55 ? 'good' : score >= 40 ? 'fair' : 'skip'

  return {
    listing,
    transportCost: travel,
    landedCost,
    referencePrice,
    savingsPercent,
    lowestRecentPrice,
    priceTrend: trend,
    trustScore,
    score,
    verdict,
    warnings,
  }
}

export interface DealContext {
  listings: Listing[]
  pricing: Record<string, ListingPricing>
  preferences: DealPreferences
  trustScore: (sellerId: string) => number | null
  sellerVerified: (sellerId: string) => boolean
}

function evaluateAll(context: DealContext, listings: Listing[], budget: number | null) {
  return listings.map((listing) =>
    evaluateDeal(
      listing,
      context.pricing[listing.id],
      context.preferences,
      context.trustScore(listing.sellerId),
      context.sellerVerified(listing.sellerId),
      budget,
    ),
  )
}

const byScore = (a: DealEvaluation, b: DealEvaluation) => b.score - a.score || a.landedCost - b.landedCost

/** Search every matching listing and return up to `limit` picks, naming everything checked. */
export function huntDeals(context: DealContext, query: DealQuery, limit = 3): DealHuntResult {
  const candidates = context.listings.filter(
    (listing) =>
      (query.categoryId === 'all' || listing.categoryId === query.categoryId) && matchesKeyword(listing, query.keyword),
  )
  const evaluations = evaluateAll(context, candidates, query.budget).sort(byScore)
  return {
    checkedListingIds: candidates.map((listing) => listing.id),
    picks: evaluations.filter((evaluation) => !evaluation.warnings.includes('over-budget')).slice(0, limit),
    ranAt: new Date().toISOString(),
  }
}

export interface PriceCheckResult {
  target: DealEvaluation
  checkedListingIds: string[]
  cheaper: DealEvaluation[]
  verdict: 'best-available' | 'cheaper-exists'
}

/** "About to buy this?" — compare one listing against every similar listing. */
export function checkBeforeBuying(context: DealContext, listingId: string): PriceCheckResult | undefined {
  const listing = context.listings.find((item) => item.id === listingId)
  if (!listing) return undefined
  const similar = context.listings.filter((item) => item.categoryId === listing.categoryId && item.id !== listing.id)
  const [target] = evaluateAll(context, [listing], null)
  const cheaper = evaluateAll(context, similar, null)
    .filter((evaluation) => evaluation.landedCost < target.landedCost && !evaluation.warnings.includes('reserved'))
    .sort((a, b) => a.landedCost - b.landedCost)
  return {
    target,
    checkedListingIds: similar.map((item) => item.id),
    cheaper,
    verdict: cheaper.length ? 'cheaper-exists' : 'best-available',
  }
}

export function watchMatches(watch: WatchItem, listings: Listing[], categoryId: 'all' | CategoryId = 'all') {
  if (watch.listingId) return listings.filter((listing) => listing.id === watch.listingId)
  return listings.filter(
    (listing) => (categoryId === 'all' || listing.categoryId === categoryId) && matchesKeyword(listing, watch.keyword ?? ''),
  )
}

/**
 * Compare current prices with each watch's baselines. Only moves at or above the
 * threshold (or reaching the target price) raise an alert; everything else stays quiet.
 * Returns the alerts plus updated baselines so the same drop is not reported twice.
 */
export function scanWatchlist(watchlist: WatchItem[], listings: Listing[], thresholdPercent: number) {
  const alerts: DealAlert[] = []
  const now = new Date().toISOString()
  const updated = watchlist.map((watch) => {
    const baselines = { ...watch.baselines }
    for (const listing of watchMatches(watch, listings)) {
      const previous = baselines[listing.id]
      if (previous === undefined) {
        baselines[listing.id] = listing.price
        continue
      }
      if (listing.price >= previous) {
        baselines[listing.id] = Math.max(previous, listing.price)
        continue
      }
      const dropPercent = Math.round(((previous - listing.price) / previous) * 1000) / 10
      const hitTarget = watch.targetPrice !== null && listing.price <= watch.targetPrice
      if (dropPercent >= thresholdPercent || hitTarget) {
        alerts.push({
          id: `alert-${watch.id}-${listing.id}-${listing.price}`,
          watchId: watch.id,
          listingId: listing.id,
          oldPrice: previous,
          newPrice: listing.price,
          dropPercent,
          hitTarget,
          createdAt: now,
        })
        baselines[listing.id] = listing.price
      }
    }
    return { ...watch, baselines }
  })
  return { alerts, watchlist: updated }
}
