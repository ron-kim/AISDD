import type { LocalizedText } from '@/types/market'

const text = (zhTW: string, en: string): LocalizedText => ({ 'zh-TW': zhTW, en })

export interface TaiwanDistrictOption {
  id: string
  label: LocalizedText
}

export interface TaiwanCountyOption {
  id: string
  label: LocalizedText
  districts: TaiwanDistrictOption[]
}

export const taiwanLocationCatalog: TaiwanCountyOption[] = [
  {
    id: 'taipei-city',
    label: text('臺北市', 'Taipei City'),
    districts: [
      { id: 'songshan-district', label: text('松山區', 'Songshan District') },
      { id: 'daan-district', label: text('大安區', 'Da’an District') },
      { id: 'zhongshan-district', label: text('中山區', 'Zhongshan District') },
      { id: 'xinyi-district', label: text('信義區', 'Xinyi District') },
    ],
  },
]

const countyMap = new Map(taiwanLocationCatalog.map((county) => [county.id, county]))

export function getCountyOption(countyId: string) {
  return countyMap.get(countyId)
}

export function getDistrictOption(countyId: string, districtId: string) {
  return countyMap.get(countyId)?.districts.find((district) => district.id === districtId)
}
