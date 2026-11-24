export type Locale = 'zh-TW' | 'en'
export type ListingStatus = 'ready-today' | 'reserved' | 'active'
export type MessageState = 'sending' | 'sent' | 'delivered'
export type CategoryId = 'furniture' | 'decor' | 'storage'

export interface LocalizedText {
  'zh-TW': string
  en: string
}

export interface SellerProfile {
  name: string
  verified: boolean
  responseTime: LocalizedText
  completionRate: number
  joinedAt: string
}

export interface Listing {
  id: string
  title: LocalizedText
  categoryId: CategoryId
  countyId: string
  districtId: string
  price: number
  distanceKm: number
  status: ListingStatus
  description: LocalizedText
  location: LocalizedText
  coordinates: { x: number; y: number }
  sellerId: string
  tags: LocalizedText[]
  meetupHint: LocalizedText
}

export interface TrustFactor {
  label: LocalizedText
  value: LocalizedText
}

export interface TrustProfile {
  score: number
  summary: LocalizedText
  factors: TrustFactor[]
}

export interface Message {
  id: string
  author: 'buyer' | 'seller' | 'system'
  text: LocalizedText
  time: string
  state?: MessageState
}

export interface Conversation {
  id: string
  listingId: string
  buyerName: string
  sellerName: string
  online: boolean
  unread: number
  updatedAt: string
  messages: Message[]
}

export interface MeetupSuggestion {
  id: string
  title: LocalizedText
  distance: LocalizedText
  safety: LocalizedText
  transit: LocalizedText
  rationale: LocalizedText
  rank: number
}

export interface PricePoint {
  date: string
  price: number
}

export interface ListingPricing {
  referencePrice: number
  history: PricePoint[]
}

export interface ScheduledPriceChange {
  listingId: string
  price: number
}

export type TransportMode = 'walk' | 'bike' | 'mrt' | 'taxi'

export interface DealPreferences {
  setupComplete: boolean
  transportMode: TransportMode
  alertThresholdPercent: number
  maxDistanceKm: number
}

export interface DealQuery {
  keyword: string
  budget: number | null
  categoryId: 'all' | CategoryId
}

export interface DealEvaluation {
  listing: Listing
  transportCost: number
  landedCost: number
  referencePrice: number
  savingsPercent: number
  lowestRecentPrice: number
  priceTrend: 'down' | 'flat' | 'up'
  trustScore: number | null
  score: number
  verdict: 'great' | 'good' | 'fair' | 'skip'
  warnings: Array<'reserved' | 'over-budget' | 'unverified-seller' | 'too-far'>
}

export interface DealHuntResult {
  checkedListingIds: string[]
  picks: DealEvaluation[]
  ranAt: string
}

export interface WatchItem {
  id: string
  listingId?: string
  keyword?: string
  targetPrice: number | null
  /** Last price seen per matching listing; alerts compare against this. */
  baselines: Record<string, number>
  createdAt: string
}

export interface DealAlert {
  id: string
  watchId: string
  listingId: string
  oldPrice: number
  newPrice: number
  dropPercent: number
  hitTarget: boolean
  createdAt: string
}
