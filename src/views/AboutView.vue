<script setup lang="ts">
import SectionCard from '@/components/SectionCard.vue'
import { t } from '@/composables/locale'

const contactEmail = 'ironya@rondaymemories.com'
</script>

<template>
  <div class="page-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">{{ t('about.eyebrow') }}</p>
        <h2>{{ t('about.title') }}</h2>
        <p class="lead">{{ t('about.lead') }}</p>
      </div>
      <div class="hero-actions">
        <a :href="`mailto:${contactEmail}`" class="primary-btn">{{ t('about.contactAction') }}</a>
      </div>
    </section>

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">{{ t('about.missionEyebrow') }}</p>
          <h2>{{ t('about.missionTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('about.missionBody') }}</p>
    </SectionCard>

    <SectionCard>
      <template #title>
        <div>
          <p class="eyebrow">{{ t('about.contactEyebrow') }}</p>
          <h2>{{ t('about.contactTitle') }}</h2>
        </div>
      </template>
      <p class="muted">{{ t('about.contactBody') }}</p>
      <p>
        <a :href="`mailto:${contactEmail}`">{{ contactEmail }}</a>
      </p>
    </SectionCard>
  </div>
</template>
