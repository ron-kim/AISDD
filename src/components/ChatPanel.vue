<script setup lang="ts">
import { computed, ref } from 'vue'
import { messageStateLabel, t, text } from '@/composables/locale'
import type { Conversation } from '@/types/market'

const props = defineProps<{
  conversation: Conversation
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const draft = ref('')
const composerId = computed(() => `chat-composer-${props.conversation.id}`)

function submit() {
  const message = draft.value.trim()
  if (!message) return

  emit('send', message)
  draft.value = ''
}
</script>

<template>
  <section class="panel chat-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">{{ t('chat.panelEyebrow') }}</p>
        <h2>{{ conversation.sellerName }}</h2>
      </div>
      <span class="score-badge" :class="{ warning: !conversation.online }">
        {{ conversation.online ? t('chat.panelOnlineTitle') : t('chat.panelOfflineTitle') }}
      </span>
    </div>

    <div class="thread" aria-live="polite">
      <p v-if="!conversation.messages.length" class="muted">{{ t('chat.noMessages') }}</p>
      <article
        v-for="message in conversation.messages"
        :key="message.id"
        class="bubble"
        :class="message.author"
      >
        <p>{{ text(message.text) }}</p>
        <span class="message-meta">
          {{ message.time }}
          <template v-if="message.state">· {{ messageStateLabel(message.state) }}</template>
        </span>
      </article>
    </div>

    <form class="composer" @submit.prevent="submit">
      <label class="sr-only" :for="composerId">{{ t('common.messageLabel') }}</label>
      <input :id="composerId" v-model="draft" type="text" :placeholder="t('chat.placeholder')" />
      <button type="submit" class="primary-btn">{{ t('common.send') }}</button>
    </form>

    <p class="muted">{{ t('chat.messageHint') }}</p>
  </section>
</template>
