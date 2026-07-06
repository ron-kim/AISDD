<script setup lang="ts">
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
        <p class="eyebrow">Meetup suggestions</p>
        <h2>Public locations first</h2>
      </div>
    </div>

    <div class="meetup-list">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="meetup-card"
        :class="{ selected: suggestion.id === selectedId }"
        @click="$emit('choose', suggestion.id)"
      >
        <div class="meetup-header">
          <strong>#{{ suggestion.rank }} {{ suggestion.title }}</strong>
          <span>{{ suggestion.distance }}</span>
        </div>
        <p>{{ suggestion.rationale }}</p>
        <div class="meetup-meta">
          <span>{{ suggestion.safety }}</span>
          <span>{{ suggestion.transit }}</span>
        </div>
      </button>
    </div>
  </section>
</template>
