<script setup lang="ts">
import { text, t } from '@/composables/locale'
import type { TrustProfile } from '@/types/market'

defineProps<{
  profile?: TrustProfile
}>()
</script>

<template>
  <section class="trust-card panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">{{ t('trust.eyebrow') }}</p>
        <h2>{{ profile ? `${profile.score} / 100` : t('common.loadingScore') }}</h2>
      </div>
      <span class="score-badge">{{ profile ? t('common.trusted') : t('common.pending') }}</span>
    </div>
    <p class="muted">{{ profile ? text(profile.summary) : t('trust.summaryFallback') }}</p>
    <ul v-if="profile" class="factor-list">
      <li v-for="factor in profile.factors" :key="text(factor.label)">
        <span>{{ text(factor.label) }}</span>
        <strong>{{ text(factor.value) }}</strong>
      </li>
    </ul>
  </section>
</template>
