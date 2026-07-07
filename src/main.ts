import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { initLocale } from './composables/locale'
import { initTheme } from './composables/theme'
import './styles/theme.css'
import { routes } from './router'
import { createMarketStore } from './stores/marketStore'

initLocale()
initTheme()

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const app = createApp(App)
const marketStore = createMarketStore()

app.provide('marketStore', marketStore)
app.use(router)
app.mount('#app')
