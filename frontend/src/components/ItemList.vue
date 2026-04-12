<template>
  <div class="item-list-wrapper">
    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <button
          v-for="t in typeFilters"
          :key="t.value"
          class="filter-btn"
          :class="{ active: activeType === t.value }"
          @click="activeType = t.value"
        >
          {{ t.label }}
          <span class="filter-count" v-if="t.count > 0">{{ t.count }}</span>
        </button>
      </div>

      <div class="filter-group">
        <select v-model="activeCategory" class="filter-select">
          <option value="">Semua Kategori</option>
          <option v-for="c in categories" :key="c" :value="c">{{ capitalize(c) }}</option>
        </select>
      </div>

      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari barang..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Items Grid -->
    <div class="items-grid" v-if="filteredItems.length > 0">
      <ItemCard
        v-for="(item, idx) in filteredItems"
        :key="item.id"
        :item="item"
        :style="{ animationDelay: idx * 0.05 + 's' }"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="8" y1="8" x2="14" y2="14"/>
          <line x1="14" y1="8" x2="8" y2="14"/>
        </svg>
      </div>
      <h3 class="empty-title">Tidak Ada Data</h3>
      <p>Belum ada laporan barang{{ activeType ? (activeType === 'lost' ? ' hilang' : ' ditemukan') : '' }}.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ItemCard from './ItemCard.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})

const activeType = ref('')
const activeCategory = ref('')
const searchQuery = ref('')

const typeFilters = computed(() => [
  { label: 'Semua', value: '', count: props.items.length },
  { label: 'Hilang', value: 'lost', count: props.items.filter(i => i.type === 'lost').length },
  { label: 'Ditemukan', value: 'found', count: props.items.filter(i => i.type === 'found').length },
])

const categories = [
  'elektronik', 'pakaian', 'dokumen', 'aksesoris', 'tas', 'kunci', 'lainnya'
]

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const filteredItems = computed(() => {
  let result = props.items

  if (activeType.value) {
    result = result.filter(item => item.type === activeType.value)
  }
  if (activeCategory.value) {
    result = result.filter(item => item.category === activeCategory.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(item =>
      item.title.toLowerCase().includes(q) ||
      (item.description && item.description.toLowerCase().includes(q)) ||
      (item.location && item.location.toLowerCase().includes(q))
    )
  }

  return result
})
</script>

<style scoped>
.item-list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  animation: slideIn 0.4s ease;
}

.filter-group {
  display: flex;
  gap: 4px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-pill);
  background: rgba(255,255,255,0.1);
  color: var(--color-white);
  font-weight: var(--font-weight-bold);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 0.25s ease;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.filter-btn:hover {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.5);
}

.filter-btn.active {
  background: var(--color-white);
  color: var(--color-black);
  border-color: var(--color-white);
}

.filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background: rgba(255,255,255,0.2);
  font-size: 11px;
  font-weight: var(--font-weight-heavy);
  padding: 0 5px;
}

.filter-btn.active .filter-count {
  background: var(--color-black);
  color: var(--color-white);
}

.filter-select {
  padding: 10px 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-pill);
  background: rgba(255,255,255,0.1);
  color: var(--color-white);
  font-weight: var(--font-weight-bold);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.filter-select option {
  background: var(--color-white);
  color: var(--color-black);
}

.search-box {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.6);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 20px 10px 40px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-pill);
  background: rgba(255,255,255,0.1);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--color-white);
  outline: none;
  transition: all 0.25s ease;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.search-input:focus {
  border-color: rgba(255,255,255,0.6);
  background: rgba(255,255,255,0.15);
}

.search-input::placeholder {
  color: rgba(255,255,255,0.5);
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.empty-state {
  padding: 64px 0;
  text-align: center;
  animation: fadeIn 0.5s ease;
}

.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.4);
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

.empty-title {
  font-size: 28px;
  letter-spacing: -0.02em;
  margin: 0 0 8px 0;
  color: var(--color-white);
  opacity: 0.9;
}

.empty-state p {
  font-size: 16px;
  font-weight: var(--font-weight-medium);
  opacity: 0.7;
  color: var(--color-white);
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .items-grid {
    grid-template-columns: 1fr;
  }
}
</style>
