import { conversations, listings, meetupSuggestions, sellers, trustProfiles } from '@/data/mockMarket'
import type { Conversation, Listing, MeetupSuggestion, TrustProfile } from '@/types/market'

const pause = (ms = 160) => new Promise((resolve) => window.setTimeout(resolve, ms))

export const marketService = {
  async listListings(): Promise<Listing[]> {
    await pause()
    return listings
  },
  async getListing(id: string): Promise<Listing | undefined> {
    await pause()
    return listings.find((listing) => listing.id === id)
  },
  async getSellerName(sellerId: string): Promise<string> {
    await pause(40)
    return sellers[sellerId]?.name ?? '未知賣家'
  },
  async getTrustProfile(sellerId: string): Promise<TrustProfile | undefined> {
    await pause(120)
    return trustProfiles[sellerId]
  },
  async getConversationByListingId(listingId: string): Promise<Conversation | undefined> {
    await pause(80)
    return conversations.find((conversation) => conversation.listingId === listingId)
  },
  async listConversations(): Promise<Conversation[]> {
    await pause(100)
    return conversations
  },
  async getMeetupSuggestions(listingId: string): Promise<MeetupSuggestion[]> {
    await pause(120)
    return meetupSuggestions[listingId] ?? []
  },
}
