import { computed, readonly, ref } from 'vue'
import { categoryOrder } from '@/data/mockMarket'
import type { CategoryId, LocalizedText, Locale, MessageState } from '@/types/market'

const STORAGE_KEY = 'aisdd-locale'
const locale = ref<Locale>('zh-TW')
let initialized = false

const messages = {
  'zh-TW': {
    app: {
      brand: 'Community Green Marketplace',
      title: '以信任為核心的在地二手交易',
      startupErrorTitle: '啟動錯誤',
      startupErrorBody: '應用程式無法初始化共用狀態，請檢查瀏覽器主控台。',
    },
    nav: {
      browse: '瀏覽',
      map: '地圖',
      chat: '聊天',
      meetup: '面交',
    },
    theme: {
      light: '淺色模式',
      dark: '深色模式',
    },
    language: {
      switchToEnglish: 'English',
      switchToChinese: '繁體中文',
    },
    categories: {
      all: '全部',
      furniture: '家具',
      decor: '裝飾',
      storage: '收納',
    },
    common: {
      searchPlaceholder: '搜尋商品、地點或標籤',
      viewDetails: '查看詳情',
      startChat: '開始聊天',
      locationOn: '定位開啟',
      locationOff: '定位關閉',
      loadingScore: '評分載入中',
      trusted: '可信',
      pending: '待確認',
      online: '線上',
      offline: '離線',
      unread: '未讀',
      send: '送出',
      messageLabel: '訊息',
      replyStateSending: '傳送中',
      replyStateSent: '已送出',
      replyStateDelivered: '已送達',
      noTrustData: '目前尚無信任資料。',
      currencyPrefix: 'NT$',
      kmUnit: '公里',
      averageResponse: '平均回覆時間',
      unknownSeller: '未知賣家',
    },
    home: {
      heroEyebrow: '社區綠色二手交易',
      heroTitle: '在地距離與彼此信任，讓交易更順手',
      heroLead:
        '找到合適商品、查看信任分數、挑選安全的面交地點，並透過聊天把整個流程串起來。',
      openMap: '打開地圖',
      openChat: '查看訊息',
      searchTitle: '探索商品',
      selectedTitle: '精選商品',
      emptyLead: '選擇一個商品，就能查看地圖、信任資訊與面交建議。',
      supportEyebrow: '即時協調',
      supportTitle: '訊息、地圖與面交建議會同步更新',
      supportBody: '選擇商品後，聊天與面交指引會一起更新，讓整個流程保持一致。',
      locationEnabled: '定位已開啟',
      locationDisabled: '定位已關閉',
    },
    listing: {
      productInfo: '商品資訊',
      meetupAdvice: '面交建議',
      meetupHeading: '先選公開地點',
      meetupBody: '先確認商品，再把選定的面交地點直接分享給對方。',
      startChat: '開始聊天',
      chooseMeetup: '選擇面交點',
    },
    chat: {
      listEyebrow: '對話列表',
      listTitle: '訊息',
      statusEyebrow: '狀態',
      statusTitle: '協調提醒',
      statusBody: '傳送狀態會即時顯示；如果離線，草稿會保留在輸入框中。',
      panelEyebrow: '即時聊天',
      panelOfflineTitle: '離線',
      panelOnlineTitle: '線上',
      placeholder: '詢問時間、地點或細節',
      autoReply: '沒問題，我會確認細節後再回覆你。',
      messageHint: '每則訊息下方都會顯示回覆狀態。',
      noMessages: '目前沒有訊息。',
    },
    map: {
      eyebrow: '地圖探索',
      title: '附近商品',
      locationOn: '定位開啟',
      locationOff: '定位關閉',
      fallbackTitle: '目前關閉定位，但仍可瀏覽',
      fallbackBody: '可以先用搜尋與商品卡片手動探索，之後再重新啟用定位。',
      panelEyebrow: '同步檢視',
      panelTitle: '地圖與清單保持同步',
      panelBody: '選擇地圖上的標記會同步更新商品焦點、信任視圖、聊天流程與面交建議。',
    },
    meetup: {
      eyebrow: '面交建議',
      title: '公開、就近、好找到',
      lead: '選擇一個雙方都容易抵達，也容易辨識的地點。',
      howEyebrow: '運作方式',
      howTitle: '把選擇直接分享到聊天',
      howBody: '選定的面交點會保留在狀態中，稍後可以直接在對話裡分享。',
      emptyState: '目前尚無面交建議。',
    },
    trust: {
      eyebrow: '賣家信任分數',
      titleFallback: '評分載入中',
      summaryFallback: '目前尚無信任資料。',
    },
  },
  en: {
    app: {
      brand: 'Community Green Marketplace',
      title: 'Local secondhand trading, built around trust',
      startupErrorTitle: 'Startup error',
      startupErrorBody: 'The app failed to initialize shared state. Check the browser console.',
    },
    nav: {
      browse: 'Browse',
      map: 'Map',
      chat: 'Chat',
      meetup: 'Meetup',
    },
    theme: {
      light: 'Light mode',
      dark: 'Dark mode',
    },
    language: {
      switchToEnglish: 'English',
      switchToChinese: '繁體中文',
    },
    categories: {
      all: 'All',
      furniture: 'Furniture',
      decor: 'Decor',
      storage: 'Storage',
    },
    common: {
      searchPlaceholder: 'Search items, places, or tags',
      viewDetails: 'View details',
      startChat: 'Go to chat',
      locationOn: 'Location on',
      locationOff: 'Location off',
      loadingScore: 'Loading score',
      trusted: 'Trusted',
      pending: 'Pending',
      online: 'Online',
      offline: 'Offline',
      unread: 'Unread',
      send: 'Send',
      messageLabel: 'Message',
      replyStateSending: 'sending',
      replyStateSent: 'sent',
      replyStateDelivered: 'delivered',
      noTrustData: 'No trust data available yet.',
      currencyPrefix: 'NT$',
      kmUnit: 'km',
      averageResponse: 'Average response time',
      unknownSeller: 'Unknown seller',
    },
    home: {
      heroEyebrow: 'Community green secondhand trading',
      heroTitle: 'A trading experience centered on nearby places and mutual trust',
      heroLead:
        'Find suitable items, inspect trust scores, choose a safe meetup point, and coordinate everything through chat.',
      openMap: 'Open map',
      openChat: 'View messages',
      searchTitle: 'Explore items',
      selectedTitle: 'Featured item',
      emptyLead: 'Pick an item to see the map, trust profile, and meetup suggestions.',
      supportEyebrow: 'Live coordination',
      supportTitle: 'Messages, map, and meetup suggestions stay in sync',
      supportBody: 'Selecting an item updates chat and meetup guidance so the whole flow stays aligned.',
      locationEnabled: 'Location enabled',
      locationDisabled: 'Location disabled',
    },
    listing: {
      productInfo: 'Product info',
      meetupAdvice: 'Meetup suggestions',
      meetupHeading: 'Public places first',
      meetupBody: 'Confirm the item, then share a chosen meetup point directly in chat.',
      startChat: 'Start conversation',
      chooseMeetup: 'Choose meetup point',
    },
    chat: {
      listEyebrow: 'Conversation list',
      listTitle: 'Messages',
      statusEyebrow: 'Status',
      statusTitle: 'Coordination notes',
      statusBody: 'Sending state appears inline. If you go offline, the draft stays in the box.',
      panelEyebrow: 'Real-time chat',
      panelOfflineTitle: 'Offline',
      panelOnlineTitle: 'Online',
      placeholder: 'Ask about timing, location, or details',
      autoReply: "Sure, I'll confirm the details and get back to you.",
      messageHint: 'Reply status shows beneath each message.',
      noMessages: 'No messages yet.',
    },
    map: {
      eyebrow: 'Map exploration',
      title: 'Nearby listings',
      locationOn: 'Location on',
      locationOff: 'Location off',
      fallbackTitle: 'Location is off, but browsing still works',
      fallbackBody: 'Use search and the listing cards to explore manually, or re-enable location later.',
      panelEyebrow: 'Synchronized view',
      panelTitle: 'Map and list stay aligned',
      panelBody: 'Selecting a pin updates the listing focus, trust view, chat flow, and meetup suggestions.',
    },
    meetup: {
      eyebrow: 'Meetup suggestions',
      title: 'Public, nearby, and easy to find',
      lead: 'Choose a place that is easy for both sides to reach and identify.',
      howEyebrow: 'How it works',
      howTitle: 'Share your choice in chat',
      howBody: 'The selected meetup point stays in state so it can be shared in conversation later.',
      emptyState: 'No meetup suggestions yet.',
    },
    trust: {
      eyebrow: 'Seller trust score',
      titleFallback: 'Loading score',
      summaryFallback: 'No trust data available yet.',
    },
  },
} as const

const resolvedLocale = (value: string): Locale => (value.startsWith('zh') ? 'zh-TW' : 'en')

function canUseDom() {
  return typeof window !== 'undefined' && typeof document !== 'undefined'
}

function getBrowserLocale(): Locale {
  return resolvedLocale(window.navigator.language)
}

function setDocumentLocale(next: Locale) {
  if (!canUseDom()) {
    return
  }

  document.documentElement.lang = next === 'zh-TW' ? 'zh-Hant' : 'en'
}

function setLocale(next: Locale) {
  locale.value = next

  if (!canUseDom()) {
    return
  }

  window.localStorage.setItem(STORAGE_KEY, next)
  setDocumentLocale(next)
}

export function initLocale() {
  if (!canUseDom() || initialized) {
    return locale.value
  }

  initialized = true
  const stored = window.localStorage.getItem(STORAGE_KEY)
  setLocale(stored === 'zh-TW' || stored === 'en' ? stored : getBrowserLocale())
  return locale.value
}

export function toggleLocale() {
  setLocale(locale.value === 'zh-TW' ? 'en' : 'zh-TW')
}

export function setAppLocale(next: Locale) {
  setLocale(next)
}

function getValueByPath(source: Record<string, unknown>, path: string) {
  return path.split('.').reduce<unknown>((current, segment) => {
    if (current && typeof current === 'object' && segment in (current as Record<string, unknown>)) {
      return (current as Record<string, unknown>)[segment]
    }
    return undefined
  }, source)
}

export function t(path: string) {
  const value = getValueByPath(messages[locale.value] as Record<string, unknown>, path)
  return typeof value === 'string' ? value : path
}

export function text(value?: LocalizedText | string) {
  if (!value) return ''
  if (typeof value === 'string') return value
  return value[locale.value] ?? value['zh-TW'] ?? value.en
}

export function categoryLabel(categoryId: CategoryId) {
  return t(`categories.${categoryId}`)
}

export function formatCurrency(amount: number) {
  return `${t('common.currencyPrefix')} ${amount.toLocaleString(locale.value === 'zh-TW' ? 'zh-TW' : 'en-US')}`
}

export function formatDistance(distanceKm: number) {
  const formatted = distanceKm.toFixed(distanceKm % 1 === 0 ? 0 : 1)
  return `${formatted} ${t('common.kmUnit')}`
}

export function formatDate(dateString: string) {
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return dateString
  return new Intl.DateTimeFormat(locale.value === 'zh-TW' ? 'zh-TW' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

export function formatClock(date = new Date()) {
  return new Intl.DateTimeFormat(locale.value === 'zh-TW' ? 'zh-TW' : 'en-US', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function messageStateLabel(state?: MessageState) {
  if (!state) return ''
  return t(`common.replyState${state[0].toUpperCase()}${state.slice(1)}`)
}

export function useLocale() {
  return {
    locale: readonly(locale),
    isEnglish: computed(() => locale.value === 'en'),
    t,
    text,
    categoryLabel,
    formatCurrency,
    formatDistance,
    formatDate,
    formatClock,
    messageStateLabel,
    toggleLocale,
    setAppLocale,
  }
}
