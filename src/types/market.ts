export type ListingStatus = 'ready-today' | 'reserved' | 'active'
export type MessageState = 'sending' | 'sent' | 'delivered'

export interface SellerProfile {
  name: string
  verified: boolean
  responseTime: string
  completionRate: number
  joinedAt: string
}

export interface Listing {
  id: string
  title: string
  category: string
  price: number
  distanceKm: number
  status: ListingStatus
  description: string
  location: string
  coordinates: { x: number; y: number }
  sellerId: string
  tags: string[]
  meetupHint: string
}

export interface TrustFactor {
  label: string
  value: string
}

export interface TrustProfile {
  score: number
  summary: string
  factors: TrustFactor[]
}

export interface Message {
  id: string
  author: 'buyer' | 'seller' | 'system'
  text: string
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
  title: string
  distance: string
  safety: string
  transit: string
  rationale: string
  rank: number
}
