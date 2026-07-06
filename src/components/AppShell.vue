<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Community Green Marketplace</p>
        <h1>Local secondhand trading, built around trust</h1>
      </div>
      <nav class="nav">
        <RouterLink to="/" class="nav-link">Browse</RouterLink>
        <RouterLink to="/map" class="nav-link">Map</RouterLink>
        <RouterLink to="/chat" class="nav-link">Chat</RouterLink>
        <RouterLink to="/meetup" class="nav-link">Meetup</RouterLink>
      </nav>
    </header>

    <main class="workspace">
      <slot />
    </main>
  </div>
</template>
