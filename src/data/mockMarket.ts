import type { Conversation, Listing, MeetupSuggestion, SellerProfile, TrustProfile } from '@/types/market'

const text = (zhTW: string, en: string) => ({ 'zh-TW': zhTW, en })

export const categoryOrder = ['furniture', 'decor', 'storage'] as const

export const sellers: Record<string, SellerProfile> = {
  s1: {
    name: '林小姐',
    verified: true,
    responseTime: text('平均回覆 8 分鐘', 'Average reply time: 8 minutes'),
    completionRate: 96,
    joinedAt: '2023-04-12',
  },
  s2: {
    name: '周先生',
    verified: true,
    responseTime: text('平均回覆 14 分鐘', 'Average reply time: 14 minutes'),
    completionRate: 91,
    joinedAt: '2022-10-03',
  },
  s3: {
    name: '陳小姐',
    verified: false,
    responseTime: text('平均回覆 22 分鐘', 'Average reply time: 22 minutes'),
    completionRate: 88,
    joinedAt: '2024-01-18',
  },
}

export const listings: Listing[] = [
  {
    id: 'cedar-chair',
    title: text('胡桃木餐椅', 'Walnut dining chair'),
    categoryId: 'furniture',
    countyId: 'taipei-city',
    districtId: 'songshan-district',
    price: 1800,
    distanceKm: 1.2,
    status: 'ready-today',
    description: text(
      '保存良好的一張餐椅，適合住家或工作室使用，今晚可在捷運站附近面交。',
      'Well-kept single chair, suitable for home or studio use. Can meet near the MRT station tonight.',
    ),
    location: text('松山區・民生社區', 'Songshan District · Minsheng Community'),
    coordinates: { x: 28, y: 36 },
    sellerId: 's1',
    tags: [text('可面交', 'Meetup available'), text('短途', 'Short trip'), text('永續', 'Sustainable')],
    meetupHint: text('民生公園南門', 'Minsheng Park south gate'),
  },
  {
    id: 'bamboo-lamp',
    title: text('竹編桌燈', 'Bamboo table lamp'),
    categoryId: 'decor',
    countyId: 'taipei-city',
    districtId: 'daan-district',
    price: 650,
    distanceKm: 0.8,
    status: 'active',
    description: text(
      '柔光桌燈，適合書桌與閱讀角落，賣家下班後可面交。',
      'Soft-glow table lamp, ideal for desks and reading corners. Seller can meet after work.',
    ),
    location: text('大安區・科技大樓', 'Da’an District · Technology Building'),
    coordinates: { x: 68, y: 52 },
    sellerId: 's2',
    tags: [text('近距離', 'Close by'), text('夜間可約', 'Evening meetup'), text('低碳', 'Low carbon')],
    meetupHint: text('科技大樓出口廣場', 'Technology Building exit plaza'),
  },
  {
    id: 'linen-rack',
    title: text('亞麻置物架', 'Linen storage rack'),
    categoryId: 'storage',
    countyId: 'taipei-city',
    districtId: 'zhongshan-district',
    price: 1200,
    distanceKm: 2.5,
    status: 'reserved',
    description: text(
      '四層置物架，表面乾淨俐落，適合小套房與租屋空間。',
      'Four-tier storage rack with a clean finish, great for small apartments and rentals.',
    ),
    location: text('中山區・晴光商圈', 'Zhongshan District · Chingguang Market area'),
    coordinates: { x: 55, y: 24 },
    sellerId: 's3',
    tags: [text('已預約', 'Reserved'), text('可議價', 'Negotiable'), text('社區取貨', 'Community pick-up')],
    meetupHint: text('晴光市場公共休憩區', 'Public seating area near Chingguang Market'),
  },
  {
    id: 'oak-shelf',
    title: text('橡木壁掛層架', 'Oak wall shelf'),
    categoryId: 'storage',
    countyId: 'taipei-city',
    districtId: 'xinyi-district',
    price: 980,
    distanceKm: 1.6,
    status: 'active',
    description: text(
      '天然橡木層架，可用在玄關或廚房，尺寸完整。',
      'Natural oak shelf, usable in the entryway or kitchen. Measurements are intact.',
    ),
    location: text('信義區・永春', 'Xinyi District · Yongchun'),
    coordinates: { x: 74, y: 28 },
    sellerId: 's1',
    tags: [text('熱門', 'Popular'), text('可立即取件', 'Ready for pickup'), text('社區信任', 'Community trusted')],
    meetupHint: text('永春市場對面咖啡館', 'Cafe across from Yongchun Market'),
  },
]

export const trustProfiles: Record<string, TrustProfile> = {
  s1: {
    score: 94,
    summary: text('互動與完成率都很高，適合快速的在地面交。', 'High engagement and completion rate. Good fit for quick local meetups.'),
    factors: [
      { label: text('完成率', 'Completion rate'), value: text('96%', '96%') },
      { label: text('回覆速度', 'Reply speed'), value: text('8 分鐘內', 'Within 8 min') },
      { label: text('檔案完整度', 'Profile completeness'), value: text('已驗證', 'Verified') },
    ],
  },
  s2: {
    score: 88,
    summary: text('交易紀錄穩定，最近回覆稍慢，但整體仍然可靠。', 'Stable transaction history. Replies are a bit slower lately, but overall reliable.'),
    factors: [
      { label: text('完成率', 'Completion rate'), value: text('91%', '91%') },
      { label: text('回覆速度', 'Reply speed'), value: text('14 分鐘內', 'Within 14 min') },
      { label: text('檔案完整度', 'Profile completeness'), value: text('已驗證', 'Verified') },
    ],
  },
  s3: {
    score: 81,
    summary: text('交易紀錄正常，建議選擇公開面交地點。', 'Good transaction history. Prefer a public meetup location.'),
    factors: [
      { label: text('完成率', 'Completion rate'), value: text('88%', '88%') },
      { label: text('回覆速度', 'Reply speed'), value: text('22 分鐘內', 'Within 22 min') },
      { label: text('檔案完整度', 'Profile completeness'), value: text('未驗證', 'Unverified') },
    ],
  },
}

export const meetupSuggestions: Record<string, MeetupSuggestion[]> = {
  'cedar-chair': [
    {
      id: 'm1',
      title: text('民生公園南門', 'Minsheng Park south gate'),
      distance: text('步行 6 分鐘', '6 min walk'),
      safety: text('公共空間，照明充足', 'Public space, well lit'),
      transit: text('近公車站與自行車停放區', 'Near bus stops and bike parking'),
      rationale: text('距離最近，也適合搬運家具。', 'Closest option and suitable for carrying furniture.'),
      rank: 1,
    },
    {
      id: 'm2',
      title: text('民生社區圖書館門口', 'Minsheng Community Library entrance'),
      distance: text('步行 9 分鐘', '9 min walk'),
      safety: text('人流穩定、環境安靜', 'Steady foot traffic, quiet setting'),
      transit: text('鄰近接駁線', 'Near transit shuttle routes'),
      rationale: text('適合快速檢查商品並確認細節。', 'Good for a short inspection and final confirmation.'),
      rank: 2,
    },
  ],
  'bamboo-lamp': [
    {
      id: 'm3',
      title: text('科技大樓出口廣場', 'Technology Building exit plaza'),
      distance: text('步行 4 分鐘', '4 min walk'),
      safety: text('公共空間，監視設備完善', 'Public space with good surveillance'),
      transit: text('捷運與公車轉乘方便', 'Easy MRT and bus transfer'),
      rationale: text('適合小型商品的快速交付。', 'Best for quick handoff of a small item.'),
      rank: 1,
    },
    {
      id: 'm4',
      title: text('附近連鎖咖啡館', 'Nearby chain cafe'),
      distance: text('步行 7 分鐘', '7 min walk'),
      safety: text('座位充足、方便檢查商品', 'Plenty of seats and space to inspect'),
      transit: text('靠近大眾運輸', 'Close to public transit'),
      rationale: text('方便當面確認燈具狀況。', 'Convenient for checking the lamp in person.'),
      rank: 2,
    },
  ],
  'linen-rack': [
    {
      id: 'm5',
      title: text('晴光市場公共休憩區', 'Public seating area near Chingguang Market'),
      distance: text('步行 8 分鐘', '8 min walk'),
      safety: text('公開且方便停留', 'Open and easy to stay a while'),
      transit: text('鄰近公車與共享運具', 'Near bus and shared mobility options'),
      rationale: text('便於搬運與短暫停靠。', 'Convenient for loading and short stops.'),
      rank: 1,
    },
    {
      id: 'm6',
      title: text('商場一樓服務台旁', 'Beside the mall first-floor service desk'),
      distance: text('步行 11 分鐘', '11 min walk'),
      safety: text('人流穩定、易於會合', 'Stable foot traffic and easy to meet'),
      transit: text('近捷運出口', 'Near the MRT exit'),
      rationale: text('適合需要多一點確認時間的交易。', 'Good for trades that need a bit of extra time.'),
      rank: 2,
    },
  ],
  'oak-shelf': [
    {
      id: 'm7',
      title: text('永春市場對面咖啡館', 'Cafe across from Yongchun Market'),
      distance: text('步行 5 分鐘', '5 min walk'),
      safety: text('座位舒適、完全可視', 'Comfortable seats and fully visible'),
      transit: text('近捷運與公車站', 'Near MRT and bus stops'),
      rationale: text('室內環境方便檢查外觀與尺寸。', 'Indoor setup for checking appearance and dimensions.'),
      rank: 1,
    },
    {
      id: 'm8',
      title: text('社區活動中心入口', 'Community activity center entrance'),
      distance: text('步行 10 分鐘', '10 min walk'),
      safety: text('公共場所、停留便利', 'Public place with room to pause'),
      transit: text('可步行至轉乘點', 'Walkable to transfer points'),
      rationale: text('適合需要更穩定交接的時段。', 'Good when the handoff needs a bit more stability.'),
      rank: 2,
    },
  ],
}

export const conversations: Conversation[] = [
  {
    id: 'c1',
    listingId: 'cedar-chair',
    buyerName: '買家',
    sellerName: '林小姐',
    online: true,
    unread: 1,
    updatedAt: '10:42',
    messages: [
      { id: 'm1', author: 'seller', text: text('椅子還在，今晚 7 點後可以約。', 'The chair is still available. I can meet after 7 PM tonight.'), time: '10:12', state: 'delivered' },
      { id: 'm2', author: 'buyer', text: text('可以在民生公園南門面交嗎？', 'Could we meet at the Minsheng Park south gate?'), time: '10:18', state: 'delivered' },
      { id: 'm3', author: 'seller', text: text('可以，面交前我會先拍細節給你。', 'Yes. I’ll send detailed photos before the meetup.'), time: '10:42', state: 'delivered' },
    ],
  },
  {
    id: 'c2',
    listingId: 'bamboo-lamp',
    buyerName: '買家',
    sellerName: '周先生',
    online: true,
    unread: 0,
    updatedAt: '09:35',
    messages: [
      { id: 'm4', author: 'seller', text: text('桌燈今天可以交付。', 'The lamp can be handed over today.'), time: '09:05', state: 'delivered' },
      { id: 'm5', author: 'buyer', text: text('科技大樓出口廣場方便嗎？', 'Is the Technology Building exit plaza convenient?'), time: '09:12', state: 'delivered' },
      { id: 'm6', author: 'seller', text: text('可以，我 15 分鐘內到。', 'Yes, I can be there within 15 minutes.'), time: '09:35', state: 'delivered' },
    ],
  },
]
