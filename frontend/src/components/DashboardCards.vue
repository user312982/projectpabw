<template>
  <div class="dashboard-cards">
    <div
      v-for="(card, idx) in cards"
      :key="card.label"
      class="card"
      :class="card.bg"
      :style="{ animationDelay: idx * 0.08 + 's' }"
    >
      <div class="card-top">
        <span class="card-icon" v-html="card.icon"></span>
        <div class="card-title">{{ card.label }}</div>
      </div>
      <div class="card-value">{{ card.value }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      total_lost: 0,
      total_found: 0,
      total_open: 0,
      total_claimed: 0,
      total_closed: 0,
    }),
  },
})

const cards = computed(() => [
  {
    label: 'Lost Items',
    value: props.data.total_lost,
    bg: 'bg-lost',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>',
  },
  {
    label: 'Found Items',
    value: props.data.total_found,
    bg: 'bg-found',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  },
  {
    label: 'Open Reports',
    value: props.data.total_open,
    bg: 'bg-accent',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  },
  {
    label: 'Claimed',
    value: props.data.total_claimed,
    bg: 'bg-claimed',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>',
  },
  {
    label: 'Closed',
    value: props.data.total_closed,
    bg: 'bg-gray-card',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>',
  },
])
</script>

<style scoped>
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 28px 28px 24px;
  border-radius: var(--radius-lg);
  min-height: 180px;
  background: var(--color-surface);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  animation: slideUp 0.5s ease both;
  position: relative;
  overflow: hidden;
}

.card::before {
  display: none;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

.bg-lost { 
  background: var(--color-surface); 
  color: var(--color-primary); 
  border: 1px solid rgba(11, 97, 170, 0.14);
  border-left: 4px solid var(--color-primary);
  box-shadow: 0 8px 24px rgba(11, 97, 170, 0.1);
}
.bg-found { 
  background: var(--color-surface); 
  color: #14532D; 
  border: 1px solid rgba(22, 163, 74, 0.18);
  border-left: 4px solid var(--color-success);
  box-shadow: 0 8px 24px rgba(22, 163, 74, 0.12);
}
.bg-accent { 
  background: var(--color-surface); 
  color: var(--color-primary);
  border: 1px solid rgba(11, 97, 170, 0.18);
  border-left: 4px solid var(--color-primary);
  box-shadow: 0 8px 24px rgba(11, 97, 170, 0.1);
}
.bg-claimed { 
  background: var(--color-surface); 
  color: #7C2D12; 
  border: 1px solid rgba(245, 183, 89, 0.3);
  border-left: 4px solid var(--color-accent);
  box-shadow: 0 8px 24px rgba(245, 183, 90, 0.18);
}
.bg-gray-card { 
  background: var(--color-surface); 
  color: var(--color-neutral-dark); 
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-neutral-dark);
  box-shadow: var(--shadow-md);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(11, 97, 170, 0.1);
  flex-shrink: 0;
}

.bg-accent .card-icon,
.bg-primary .card-icon {
  background: rgba(10, 97, 170, 0.12);
  color: var(--color-primary);
}

.bg-found .card-icon {
  background: rgba(25, 135, 84, 0.12);
}

.bg-claimed .card-icon {
  background: var(--color-accent-subtle);
}

.bg-gray-card .card-icon {
  background: rgba(55, 65, 81, 0.08);
}

.card-title {
  font-size: 13px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.9;
}

.card-value {
  font-size: clamp(3.5rem, 5vw, 5.5rem);
  font-weight: var(--font-weight-heavy);
  line-height: 0.85;
  letter-spacing: 0;
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

@media (max-width: 1400px) {
  .card-value {
    font-size: 3.5rem;
  }
}

@media (max-width: 600px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
  .card {
    min-height: 140px;
  }
}
</style>
