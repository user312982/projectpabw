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
    label: 'Barang Hilang',
    value: props.data.total_lost,
    bg: 'bg-lost',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>',
  },
  {
    label: 'Ditemukan',
    value: props.data.total_found,
    bg: 'bg-found',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  },
  {
    label: 'Laporan Open',
    value: props.data.total_open,
    bg: 'bg-accent',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  },
  {
    label: 'Diklaim / Selesai',
    value: props.data.total_claimed + props.data.total_closed,
    bg: 'bg-gray-card',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>',
  },
])
</script>

<style scoped>
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 28px 28px 24px;
  border-radius: var(--radius-lg);
  min-height: 180px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: slideUp 0.5s ease both;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -30%;
  width: 200px;
  height: 200px;
  background: rgba(255,255,255,0.08);
  border-radius: 50%;
  pointer-events: none;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
}

.bg-lost { background: var(--gradient-lost); color: var(--color-on-primary); }
.bg-found { background: var(--gradient-found); color: var(--color-on-primary); }
.bg-accent { background: var(--gradient-accent); color: var(--color-on-primary); }
.bg-gray-card { background: linear-gradient(135deg, #E8E5E1 0%, #D4D0CC 100%); color: var(--color-text-main); }

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
  background: rgba(255,255,255,0.15);
  flex-shrink: 0;
}

.bg-gray-card .card-icon {
  background: rgba(0,0,0,0.08);
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
  letter-spacing: -0.05em;
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
