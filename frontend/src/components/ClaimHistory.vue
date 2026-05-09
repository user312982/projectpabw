<template>
  <div class="history-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading claims history...</p>
    </div>

    <div v-else-if="claims.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
        </svg>
      </div>
      <h3>No Claims Yet</h3>
      <p>No items have been claimed yet.</p>
    </div>

    <div v-else class="table-wrapper bento-card">
      <table class="claims-table">
        <thead>
          <tr>
            <th>Item Code</th>
            <th>Item Name</th>
            <th>Claimer</th>
            <th>NIM / NIP</th>
            <th>Contact</th>
            <th>Date</th>
            <th>Processed By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="claim in claims" :key="claim.id" class="claim-row">
            <td>
              <span class="code-badge">{{ claim.item_title ? '' : '#' }}{{ claim.item_id }}</span>
            </td>
            <td class="item-name">{{ claim.item_title || `Item #${claim.item_id}` }}</td>
            <td class="claimer-name">{{ claim.nama_pengklaim }}</td>
            <td><code class="nim-code">{{ claim.nim_pengklaim }}</code></td>
            <td>{{ claim.kontak_pengklaim || '-' }}</td>
            <td class="date-cell">{{ formatDate(claim.tanggal_klaim) }}</td>
            <td>{{ claim.petugas_name || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api.js'

const claims = ref([])
const loading = ref(true)

async function fetchClaims() {
  loading.value = true
  try {
    const res = await api.get('/api/claims')
    claims.value = res.data
  } catch (err) {
    console.error('Failed to fetch claims:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchClaims()
})

defineExpose({ refresh: fetchClaims })
</script>

<style scoped>
.history-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 16px;
  color: var(--color-text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  padding: 64px 0;
  text-align: center;
}

.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(84, 107, 65, 0.08);
  color: var(--color-text-muted);
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  letter-spacing: -0.02em;
  margin: 0 0 8px;
  color: var(--color-text-main);
}

.empty-state p {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

.bento-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.claims-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.claims-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  background: rgba(84, 107, 65, 0.05);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.claims-table td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(220, 204, 172, 0.4);
  vertical-align: middle;
  color: var(--color-text-main);
}

.claim-row {
  transition: background 0.15s ease;
}

.claim-row:hover {
  background: rgba(84, 107, 65, 0.04);
}

.claim-row:last-child td {
  border-bottom: none;
}

.code-badge {
  display: inline-block;
  padding: 3px 8px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  letter-spacing: 0.04em;
}

.item-name {
  font-weight: var(--font-weight-bold);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.claimer-name {
  font-weight: var(--font-weight-medium);
}

.nim-code {
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background: rgba(220, 204, 172, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--color-text-main);
}

.date-cell {
  white-space: nowrap;
  font-size: 12px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .claims-table {
    font-size: 12px;
  }
  .claims-table th,
  .claims-table td {
    padding: 10px 8px;
  }
}
</style>