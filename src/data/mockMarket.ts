import type { Conversation, Listing, MeetupSuggestion, SellerProfile, TrustProfile } from '@/types/market'

export const sellers: Record<string, SellerProfile> = {
  s1: {
    name: '林怡安',
    verified: true,
    responseTime: '平均 8 分鐘回覆',
    completionRate: 96,
    joinedAt: '2023-04-12',
  },
  s2: {
    name: '陳柏宇',
    verified: true,
    responseTime: '平均 14 分鐘回覆',
    completionRate: 91,
    joinedAt: '2022-10-03',
  },
  s3: {
    name: '吳晴',
    verified: false,
    responseTime: '平均 22 分鐘回覆',
    completionRate: 88,
    joinedAt: '2024-01-18',
  },
}

export const listings: Listing[] = [
  {
    id: 'cedar-chair',
    title: '榫接胡桃木餐椅',
    category: '家具',
    price: 1800,
    distanceKm: 1.2,
    status: 'ready-today',
    description: '保養良好的單椅一張，適合住家與工作室使用，今晚可在捷運站附近面交。',
    location: '松山區・民生社區',
    coordinates: { x: 28, y: 36 },
    sellerId: 's1',
    tags: ['可面交', '短途', '永續'],
    meetupHint: '民生公園南門',
  },
  {
    id: 'bamboo-lamp',
    title: '竹編桌燈',
    category: '家飾',
    price: 650,
    distanceKm: 0.8,
    status: 'active',
    description: '柔光桌燈，適合書桌與閱讀角落，賣家可在下班後配合時間。',
    location: '大安區・科技大樓',
    coordinates: { x: 68, y: 52 },
    sellerId: 's2',
    tags: ['近距離', '夜間可約', '低碳'],
    meetupHint: '科技大樓出口廣場',
  },
  {
    id: 'linen-rack',
    title: '亞麻布置物架',
    category: '收納',
    price: 1200,
    distanceKm: 2.5,
    status: 'reserved',
    description: '四層收納架，外觀乾淨，適合小宅與租屋空間。',
    location: '中山區・晴光商圈',
    coordinates: { x: 55, y: 24 },
    sellerId: 's3',
    tags: ['已預約', '可議價', '社區'],
    meetupHint: '晴光市場公共休憩區',
  },
  {
    id: 'oak-shelf',
    title: '橡木壁掛層架',
    category: '收納',
    price: 980,
    distanceKm: 1.6,
    status: 'active',
    description: '原木色層架，可作玄關或廚房收納，尺寸完整。',
    location: '信義區・永春',
    coordinates: { x: 74, y: 28 },
    sellerId: 's1',
    tags: ['熱門', '可立即取件', '社區信任'],
    meetupHint: '永春市場對面咖啡館',
  },
]

export const trustProfiles: Record<string, TrustProfile> = {
  s1: {
    score: 94,
    summary: '高互動、高完成率的在地賣家，適合快速面交。',
    factors: [
      { label: '完成率', value: '96%' },
      { label: '回覆速度', value: '8 分鐘內' },
      { label: '檔案完整度', value: '已驗證' },
    ],
  },
  s2: {
    score: 88,
    summary: '穩定交易紀錄，近期回覆略慢但整體表現可靠。',
    factors: [
      { label: '完成率', value: '91%' },
      { label: '回覆速度', value: '14 分鐘內' },
      { label: '檔案完整度', value: '已驗證' },
    ],
  },
  s3: {
    score: 81,
    summary: '有良好交易紀錄，建議優先選擇公開地點面交。',
    factors: [
      { label: '完成率', value: '88%' },
      { label: '回覆速度', value: '22 分鐘內' },
      { label: '檔案完整度', value: '未驗證' },
    ],
  },
}

export const meetupSuggestions: Record<string, MeetupSuggestion[]> = {
  'cedar-chair': [
    {
      id: 'm1',
      title: '民生公園南門',
      distance: '步行 6 分鐘',
      safety: '公共空間、照明充足',
      transit: '近公車站與自行車停放區',
      rationale: '距離最近且適合搬運家具。',
      rank: 1,
    },
    {
      id: 'm2',
      title: '民生社區圖書館門口',
      distance: '步行 9 分鐘',
      safety: '人流穩定、環境安靜',
      transit: '鄰近捷運接駁線',
      rationale: '適合簡短檢查商品與確認細節。',
      rank: 2,
    },
  ],
  'bamboo-lamp': [
    {
      id: 'm3',
      title: '科技大樓出口廣場',
      distance: '步行 4 分鐘',
      safety: '公共空間、監視設備完善',
      transit: '捷運與公車轉乘便利',
      rationale: '適合小型商品的快速交付。',
      rank: 1,
    },
    {
      id: 'm4',
      title: '附近連鎖咖啡館',
      distance: '步行 7 分鐘',
      safety: '座位充足、適合檢查商品',
      transit: '靠近大眾運輸',
      rationale: '便於當面確認燈具狀況。',
      rank: 2,
    },
  ],
  'linen-rack': [
    {
      id: 'm5',
      title: '晴光市場公共休憩區',
      distance: '步行 8 分鐘',
      safety: '公開且方便停留',
      transit: '鄰近公車與共享運具',
      rationale: '方便搬運與臨時停靠。',
      rank: 1,
    },
    {
      id: 'm6',
      title: '商場一樓服務台旁',
      distance: '步行 11 分鐘',
      safety: '人流穩定、易於會合',
      transit: '近捷運出口',
      rationale: '適合需要預留確認時間的交易。',
      rank: 2,
    },
  ],
  'oak-shelf': [
    {
      id: 'm7',
      title: '永春市場對面咖啡館',
      distance: '步行 5 分鐘',
      safety: '坐席舒適、公開可見',
      transit: '近捷運與公車站',
      rationale: '可在室內檢查層架外觀與尺寸。',
      rank: 1,
    },
    {
      id: 'm8',
      title: '社區活動中心入口',
      distance: '步行 10 分鐘',
      safety: '公共場所、停留便利',
      transit: '步行可達轉乘點',
      rationale: '適合需要較穩定交接的時段。',
      rank: 2,
    },
  ],
}

export const conversations: Conversation[] = [
  {
    id: 'c1',
    listingId: 'cedar-chair',
    buyerName: '你',
    sellerName: '林怡安',
    online: true,
    unread: 1,
    updatedAt: '10:42',
    messages: [
      { id: 'm1', author: 'seller', text: '椅子還在，今晚 7 點後可約。', time: '10:12', state: 'delivered' },
      { id: 'm2', author: 'buyer', text: '請問民生公園南門可以嗎？', time: '10:18', state: 'delivered' },
      { id: 'm3', author: 'seller', text: '可以，面交前我會先拍細節給你。', time: '10:42', state: 'delivered' },
    ],
  },
  {
    id: 'c2',
    listingId: 'bamboo-lamp',
    buyerName: '你',
    sellerName: '陳柏宇',
    online: true,
    unread: 0,
    updatedAt: '09:35',
    messages: [
      { id: 'm4', author: 'seller', text: '桌燈可當天交付。', time: '09:05', state: 'delivered' },
      { id: 'm5', author: 'buyer', text: '科技大樓出口廣場方便嗎？', time: '09:12', state: 'delivered' },
      { id: 'm6', author: 'seller', text: '可以，15 分鐘內到。', time: '09:35', state: 'delivered' },
    ],
  },
]
