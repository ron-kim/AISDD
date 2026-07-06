<script setup lang="ts">
import { ref } from 'vue'
import type { Conversation } from '@/types/market'

const props = defineProps<{
  conversation: Conversation
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const draft = ref('')

function submit() {
  if (!draft.value.trim()) return
  emit('send', draft.value)
  draft.value = ''
}
</script>

<template>
  <section class="chat-panel panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Real-time chat</p>
        <h2>{{ props.conversation.sellerName }}</h2>
      </div>
      <span class="score-badge" :class="{ warning: !props.conversation.online }">
        {{ props.conversation.online ? 'Online' : 'Offline' }}
      </span>
    </div>

    <div class="thread" role="log" aria-live="polite">
      <article v-for="message in props.conversation.messages" :key="message.id" class="bubble" :class="message.author">
        <p>{{ message.text }}</p>
        <span class="message-meta">{{ message.time }} · {{ message.state ?? 'delivered' }}</span>
      </article>
    </div>

    <form class="composer" @submit.prevent="submit">
      <label class="sr-only" for="message">Message</label>
      <input id="message" v-model="draft" type="text" placeholder="Ask about timing, location, or details" />
      <button type="submit" class="primary-btn">Send</button>
    </form>
  </section>
</template>
