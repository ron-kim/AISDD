<script setup lang="ts">
import { text, t } from '@/composables/locale'
import type { MeetupSuggestion } from '@/types/market'

defineProps<{
  suggestions: MeetupSuggestion[]
  selectedId?: string
}>()

defineEmits<{
  choose: [id: string]
}>()
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">{{ t('meetup.eyebrow') }}</p>
        <h2>{{ t('meetup.title') }}</h2>
      </div>
    </div>

    <p v-if="!suggestions.length" class="muted">{{ t('meetup.emptyState') }}</p>

    <div v-else class="meetup-list">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="meetup-card"
        :class="{ selected: suggestion.id === selectedId }"
        @click="$emit('choose', suggestion.id)"
      >
        <div class="meetup-header">
          <strong>#{{ suggestion.rank }} {{ text(suggestion.title) }}</strong>
          <span>{{ text(suggestion.distance) }}</span>
        </div>
        <p>{{ text(suggestion.rationale) }}</p>
        <div class="meetup-meta">
          <span>{{ text(suggestion.safety) }}</span>
          <span>{{ text(suggestion.transit) }}</span>
        </div>
      </button>
    </div>
  </section>
</template>
