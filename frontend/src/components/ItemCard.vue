<template>
  <div class="item-card" @click="$emit('click', item)">
    <!-- Type Badge -->
    <div class="card-top">
      <span class="badge" :class="item.type === 'lost' ? 'badge-lost' : 'badge-found'">
        <span class="badge-dot" :class="item.type === 'lost' ? 'dot-lost' : 'dot-found'"></span>
        {{ item.type === 'lost' ? 'Hilang' : 'Ditemukan' }}
      </span>
      <span class="badge" :class="'badge-' + item.status">
        {{ statusLabel }}
      </span>
    </div>

    <!-- Content -->
    <h3 class="card-title">{{ item.title }}</h3>
    
    <div class="card-meta">
      <div class="meta-row">
        <span class="meta-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7V4a2 2 0 0 1 2-2h8.5L20 7.5V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-3"/></svg>
        </span>
        <span class="meta-value">{{ capitalize(item.category) }}</span>
      </div>
      <div class="meta-row" v-if="item.location">
        <span class="meta-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        </span>
        <span class="meta-value">{{ item.location }}</span>
      </div>
      <div class="meta-row">
        <span class="meta-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </span>
        <span class="meta-value">{{ item.reporter_name }}</span>
      </div>
      <div class="meta-row" v-if="item.reporter_contact">
        <span class="meta-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        </span>
        <span class="meta-value">{{ item.reporter_contact }}</span>
      </div>
    </div>

    <p class="card-desc" v-if="item.description">{{ item.description }}</p>

    <!-- Footer -->
    <div class="card-footer">
      <span class="card-date">{{ relativeTime }}</span>
      <span class="card-id">#{{ item.id }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

defineEmits(['click'])

const statusLabel = computed(() => {
  switch (props.item.status) {
    case 'open': return 'Open'
    case 'claimed': return 'Diklaim'
    case 'closed': return 'Selesai'
    default: return props.item.status
  }
})

function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const relativeTime = computed(() => {
  if (!props.item.created_at) return '-'
  const now = new Date()
  const then = new Date(props.item.created_at)
  const diff = Math.floor((now - then) / 1000) // seconds

  if (diff < 60) return 'Baru saja'
  if (diff < 3600) return `${Math.floor(diff / 60)} menit lalu`
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`
  if (diff < 604800) return `${Math.floor(diff / 86400)} hari lalu`
  return then.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
})
</script>

<style scoped>
.item-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  animation: scaleIn 0.4s ease both;
}

.item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-gray);
  transition: background 0.3s;
}

.item-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
  border-color: var(--color-primary);
}

.item-card:hover::before {
  background: var(--gradient-primary);
}

.card-top {
  display: flex;
  gap: 8px;
  align-items: center;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

.dot-lost {
  background: var(--color-white);
  animation: pulse 2s infinite;
}

.dot-found {
  background: var(--color-white);
}

.card-title {
  font-size: 20px;
  font-weight: var(--font-weight-heavy);
  letter-spacing: -0.02em;
  line-height: 1.15;
  color: var(--color-black);
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-row {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 13px;
}

.meta-icon {
  display: flex;
  align-items: center;
  color: var(--color-dark-gray);
  flex-shrink: 0;
}

.meta-value {
  font-weight: var(--font-weight-medium);
  color: var(--color-black);
}

.card-desc {
  font-size: 14px;
  color: var(--color-dark-gray);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--color-gray);
}

.card-date {
  font-size: 11px;
  font-weight: var(--font-weight-bold);
  color: var(--color-dark-gray);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.card-id {
  font-size: 12px;
  font-weight: var(--font-weight-heavy);
  color: var(--color-primary);
}
</style>
