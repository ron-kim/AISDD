import type { RouteRecordRaw } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ListingView from '@/views/ListingView.vue'
import ChatView from '@/views/ChatView.vue'
import MeetupView from '@/views/MeetupView.vue'
import MapView from '@/views/MapView.vue'

export const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/map', name: 'map', component: MapView },
  { path: '/listings/:id', name: 'listing', component: ListingView, props: true },
  { path: '/chat', name: 'chat', component: ChatView },
  { path: '/meetup', name: 'meetup', component: MeetupView },
]
