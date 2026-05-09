<template>
  <div class="item-list-wrapper">
    <!-- Search Bar Only -->
    <div class="filter-bar">
      <div class="search-box" style="flex: 1; max-width: 400px;">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search items..."
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
        :user="user"
        :style="{ animationDelay: idx * 0.05 + 's' }"
        @click="$emit('click-item', item)"
        @code-copied="code => $emit('code-copied', code)"
        @updated="id => $emit('updated', id)"
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
      <h3 class="empty-title">No Items Found</h3>
      <p>No items have been reported yet.</p>
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
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['code-copied', 'updated', 'click-item'])

const searchQuery = ref('')

const filteredItems = computed(() => {
  let result = props.items

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
  gap: 16px;
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
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 20px 10px 40px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-pill);
  background: rgba(255, 248, 236, 0.6);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-main);
  outline: none;
  transition: all 0.25s ease;
}

.search-input:focus {
  border-color: var(--color-primary);
  background: var(--color-surface);
}

.search-input::placeholder {
  color: var(--color-text-muted);
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
  background: rgba(84, 107, 65, 0.08);
  color: var(--color-text-muted);
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

.empty-title {
  font-size: 28px;
  letter-spacing: -0.02em;
  margin: 0 0 8px 0;
  color: var(--color-text-main);
  opacity: 0.9;
}

.empty-state p {
  font-size: 16px;
  font-weight: var(--font-weight-medium);
  opacity: 0.7;
  color: var(--color-text-muted);
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
