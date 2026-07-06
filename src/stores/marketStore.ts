import { computed, reactive, ref } from 'vue'
import { conversations as conversationFixtures, listings as listingFixtures } from '@/data/mockMarket'
import { marketService } from '@/services/marketService'
import type { Conversation, Listing, MeetupSuggestion, TrustProfile } from '@/types/market'

export type LocationMode = 'granted' | 'denied'

export function createMarketStore() {
  const listings = ref<Listing[]>([...listingFixtures])
  const conversations = ref<Conversation[]>([...conversationFixtures])
  const activeListingId = ref<string>(listings.value[0]?.id ?? '')
  const activeConversationId = ref<string>(conversations.value[0]?.id ?? '')
  const searchTerm = ref('')
  const categoryFilter = ref('全部')
  const locationMode = ref<LocationMode>('granted')
  const selectedMeetupListingId = ref<string>(listings.value[0]?.id ?? '')
  const selectedMeetupPointId = ref<string>('')
  const trustProfiles = reactive<Record<string, TrustProfile | undefined>>({})
  const meetupCache = reactive<Record<string, MeetupSuggestion[]>>({})

  const categories = computed(() => ['全部', ...new Set(listings.value.map((listing) => listing.category))])

  const filteredListings = computed(() => {
    const term = searchTerm.value.trim().toLowerCase()
    return listings.value.filter((listing) => {
      const matchesCategory = categoryFilter.value === '全部' || listing.category === categoryFilter.value
      const matchesTerm =
        term.length === 0 ||
        [listing.title, listing.category, listing.location, listing.description, ...listing.tags]
          .join(' ')
          .toLowerCase()
          .includes(term)
      return matchesCategory && matchesTerm
    })
  })

  const activeListing = computed(() => listings.value.find((listing) => listing.id === activeListingId.value) ?? listings.value[0])
  const activeConversation = computed(
    () => conversations.value.find((conversation) => conversation.id === activeConversationId.value) ?? conversations.value[0],
  )
  const activeTrustProfile = computed(() => (activeListing.value ? trustProfiles[activeListing.value.sellerId] : undefined))
  const activeMeetupSuggestions = computed(() =>
    selectedMeetupListingId.value ? meetupCache[selectedMeetupListingId.value] ?? [] : [],
  )

  async function hydrate() {
    await Promise.all(
      listings.value.map(async (listing) => {
        if (!trustProfiles[listing.sellerId]) {
          trustProfiles[listing.sellerId] = await marketService.getTrustProfile(listing.sellerId)
        }
      }),
    )

    if (selectedMeetupListingId.value) {
      meetupCache[selectedMeetupListingId.value] = await marketService.getMeetupSuggestions(selectedMeetupListingId.value)
    }
  }

  async function loadMeetupSuggestions(listingId: string) {
    meetupCache[listingId] = await marketService.getMeetupSuggestions(listingId)
  }

  function selectListing(id: string) {
    activeListingId.value = id
    selectedMeetupListingId.value = id
    void loadMeetupSuggestions(id)
  }

  function openConversationForListing(listingId: string) {
    const conversation = conversations.value.find((item) => item.listingId === listingId)
    if (conversation) {
      activeConversationId.value = conversation.id
    }
  }

  function selectConversation(id: string) {
    activeConversationId.value = id
  }

  function setLocationMode(mode: LocationMode) {
    locationMode.value = mode
  }

  async function loadConversation(listingId: string) {
    const conversation = await marketService.getConversationByListingId(listingId)
    if (conversation && !conversations.value.find((item) => item.id === conversation.id)) {
      conversations.value = [conversation, ...conversations.value]
    }
    if (conversation) {
      activeConversationId.value = conversation.id
    }
  }

  async function sendMessage(text: string) {
    const current = activeConversation.value
    if (!current || !text.trim()) return

    const sendingId = `msg-${Date.now()}`
    current.messages.push({
      id: sendingId,
      author: 'buyer',
      text,
      time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
      state: 'sending',
    })
    current.updatedAt = '剛剛'

    window.setTimeout(() => {
      const message = current.messages.find((item) => item.id === sendingId)
      if (message) message.state = 'sent'
    }, 500)

    window.setTimeout(() => {
      current.messages.push({
        id: `${sendingId}-reply`,
        author: 'seller',
        text: '收到，我們維持公開地點會面比較方便。',
        time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
        state: 'delivered',
      })
      current.unread += 1
      current.updatedAt = '剛剛'
    }, 1600)
  }

  function chooseMeetupPoint(listingId: string, pointId: string) {
    selectedMeetupListingId.value = listingId
    selectedMeetupPointId.value = pointId
  }

  return reactive({
    listings,
    conversations,
    categories,
    filteredListings,
    activeListing,
    activeConversation,
    activeTrustProfile,
    activeMeetupSuggestions,
    activeListingId,
    activeConversationId,
    searchTerm,
    categoryFilter,
    locationMode,
    selectedMeetupListingId,
    selectedMeetupPointId,
    hydrate,
    selectListing,
    openConversationForListing,
    selectConversation,
    setLocationMode,
    loadConversation,
    sendMessage,
    chooseMeetupPoint,
    trustProfiles,
    meetupCache,
  })
}
