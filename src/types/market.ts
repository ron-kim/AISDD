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
