<script setup lang="ts">
import type { TrustProfile } from '@/types/market'

defineProps<{
  profile?: TrustProfile
}>()
</script>

<template>
  <section class="trust-card panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Seller trust score</p>
        <h2>{{ profile ? `${profile.score} / 100` : 'Loading score' }}</h2>
      </div>
      <span class="score-badge">{{ profile ? 'Trusted' : 'Pending' }}</span>
    </div>
    <p class="muted">{{ profile?.summary ?? 'No trust data available yet.' }}</p>
    <ul v-if="profile" class="factor-list">
      <li v-for="factor in profile.factors" :key="factor.label">
        <span>{{ factor.label }}</span>
        <strong>{{ factor.value }}</strong>
      </li>
    </ul>
  </section>
</template>
