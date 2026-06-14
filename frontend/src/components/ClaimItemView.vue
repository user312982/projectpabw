<template>
  <div class="claim-view">
    <div class="claim-steps" v-if="!claimedItem">
      <div class="step" :class="{ active: step >= 1, done: step > 1 }">
        <div class="step-num">1</div>
        <span>Search Item</span>
      </div>
      <div class="step-line" :class="{ active: step > 1 }"></div>
      <div class="step" :class="{ active: step >= 2, done: step > 2 }">
        <div class="step-num">2</div>
        <span>Confirm Pickup</span>
      </div>
    </div>

    <div v-if="!searchResult && !claimedItem" class="search-section">
      <div class="search-card bento-card">
        <div class="search-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </div>
        <h3>Search by Unique Code</h3>
        <p class="search-hint">Enter the item's unique code (e.g. LF-ABC12X) to find and process a claim</p>
        <form @submit.prevent="searchItem" class="search-form">
          <input
            v-model="uniqueCode"
            type="text"
            placeholder="Enter unique code (e.g. LF-ABC12X)"
            class="search-input"
            :disabled="searching"
          />
          <button type="submit" class="btn-primary search-btn" :disabled="searching || !uniqueCode.trim()">
            <span v-if="searching">Searching...</span>
            <span v-else>Search Item</span>
          </button>
        </form>
        <p v-if="searchError" class="error">{{ searchError }}</p>
      </div>
    </div>

    <div v-if="searchResult && !claimedItem" class="result-section">
      <div class="result-card bento-card">
        <div class="result-header">
          <span class="type-badge" :class="searchResult.type === 'lost' ? 'type-lost' : 'type-found'">
            <span class="type-dot"></span>
            {{ searchResult.type === 'lost' ? 'Lost' : 'Found' }}
          </span>
          <span class="status-badge" :class="'status-' + searchResult.status">
            {{ statusLabel(searchResult.status) }}
          </span>
        </div>
        <h3 class="result-title">{{ searchResult.title }}</h3>
        <p v-if="searchResult.description" class="result-desc">{{ searchResult.description }}</p>
        <div class="result-meta">
          <div class="meta-item" v-if="searchResult.category">
            <span class="meta-label">Category</span>
            <span class="meta-value">{{ capitalize(searchResult.category) }}</span>
          </div>
          <div class="meta-item" v-if="searchResult.location">
            <span class="meta-label">Location</span>
            <span class="meta-value">{{ searchResult.location }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Code</span>
            <span class="meta-value code">{{ searchResult.unique_code }}</span>
          </div>
        </div>

        <div v-if="searchResult.status === 'claimed' || searchResult.status === 'returned'" class="already-claimed">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>This item has already been processed</span>
        </div>

        <form v-if="searchResult.status !== 'claimed' && searchResult.status !== 'returned'" @submit.prevent="submitClaim" class="claim-form">
          <div class="form-divider">
            <span>Pickup Confirmation</span>
          </div>
          <div class="form-group">
            <label for="claimer-name">Claimer Name <span class="required">*</span></label>
            <input
              id="claimer-name"
              v-model="claimForm.nama_pengklaim"
              type="text"
              placeholder="Full name of person picking up"
              required
            />
          </div>
          <div class="form-group">
            <label for="claimer-nim">NIM / NIP <span class="required">*</span></label>
            <input
              id="claimer-nim"
              v-model="claimForm.nim_pengklaim"
              type="text"
              placeholder="Student/Staff ID number"
              required
            />
          </div>
          <div class="form-group">
            <label for="claimer-contact">Contact <span class="optional">(optional)</span></label>
            <input
              id="claimer-contact"
              v-model="claimForm.kontak_pengklaim"
              type="text"
              placeholder="Phone number or email"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-outline" @click="resetSearch">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              <span v-if="submitting">Processing...</span>
              <span v-else>Confirm Pickup</span>
            </button>
          </div>
          <p v-if="claimError" class="error">{{ claimError }}</p>
        </form>

        <div v-if="searchResult.status === 'claimed' || searchResult.status === 'returned'" class="form-actions">
          <button type="button" class="btn-outline" @click="resetSearch">Search Again</button>
        </div>
      </div>
    </div>

    <div v-if="claimedItem" class="success-section">
      <div class="success-card bento-card">
        <div class="success-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3>Claim Processed Successfully</h3>
        <div class="success-details">
          <div class="success-row">
            <span class="success-label">Item</span>
            <span class="success-value">{{ claimedItem.item_title || searchResult?.title }}</span>
          </div>
          <div class="success-row">
            <span class="success-label">Claimer</span>
            <span class="success-value">{{ claimedItem.nama_pengklaim }}</span>
          </div>
          <div class="success-row">
            <span class="success-label">NIM / NIP</span>
            <span class="success-value">{{ claimedItem.nim_pengklaim }}</span>
          </div>
          <div class="success-row" v-if="claimedItem.kontak_pengklaim">
            <span class="success-label">Contact</span>
            <span class="success-value">{{ claimedItem.kontak_pengklaim }}</span>
          </div>
          <div class="success-row">
            <span class="success-label">Date</span>
            <span class="success-value">{{ formatDate(claimedItem.tanggal_klaim) }}</span>
          </div>
        </div>
        <button class="btn-primary" @click="resetAll">Process Another Claim</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api.js'

const emit = defineEmits(['claimed'])

const step = ref(1)
const uniqueCode = ref('')
const searching = ref(false)
const searchError = ref('')
const searchResult = ref(null)
const submitting = ref(false)
const claimError = ref('')
const claimedItem = ref(null)

const claimForm = ref({
  unique_code: '',
  nama_pengklaim: '',
  nim_pengklaim: '',
  kontak_pengklaim: '',
})

async function searchItem() {
  if (!uniqueCode.value.trim()) return
  searching.value = true
  searchError.value = ''
  try {
    const code = uniqueCode.value.trim().toUpperCase()
    const res = await api.get(`/api/items/by-code/${code}`)
    searchResult.value = res.data
    claimForm.value.unique_code = res.data.unique_code
    step.value = 2
  } catch (err) {
    if (err.response?.status === 404) {
      searchError.value = 'Item not found. Please check the code and try again.'
    } else {
      searchError.value = 'Error searching for item. Please try again.'
    }
  } finally {
    searching.value = false
  }
}

async function submitClaim() {
  claimError.value = ''
  submitting.value = true
  try {
    const res = await api.post('/api/items/claim-by-code', {
      unique_code: claimForm.value.unique_code,
      nama_pengklaim: claimForm.value.nama_pengklaim,
      nim_pengklaim: claimForm.value.nim_pengklaim,
      kontak_pengklaim: claimForm.value.kontak_pengklaim || undefined,
    })
    claimedItem.value = res.data
    emit('claimed')
  } catch (err) {
    claimError.value = err.response?.data?.detail || 'Failed to process claim'
  } finally {
    submitting.value = false
  }
}

function resetSearch() {
  searchResult.value = null
  searchError.value = ''
  claimError.value = ''
  step.value = 1
}

function resetAll() {
  uniqueCode.value = ''
  searchResult.value = null
  searchError.value = ''
  claimError.value = ''
  claimedItem.value = null
  claimForm.value = { unique_code: '', nama_pengklaim: '', nim_pengklaim: '', kontak_pengklaim: '' }
  step.value = 1
}

function statusLabel(status) {
  switch (status) {
    case 'open': return 'Open'
    case 'claimed': return 'Claimed'
    case 'returned': return 'Returned'
    case 'closed': return 'Closed'
    default: return status
  }
}

function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.claim-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.claim-steps {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-muted);
  transition: all 0.3s ease;
}

.step.active {
  color: var(--color-text-main);
}

.step.done .step-num {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  background: var(--color-border);
  color: var(--color-text-muted);
  transition: all 0.3s ease;
}

.step.active .step-num {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.step-line {
  flex: 1;
  height: 2px;
  background: var(--color-border);
  border-radius: 2px;
  max-width: 60px;
  transition: background 0.3s ease;
}

.step-line.active {
  background: var(--color-primary);
}

.search-section,
.result-section,
.success-section {
  animation: fadeIn 0.4s ease;
}

.bento-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  padding: 32px;
}

.search-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.search-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(11, 97, 170, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.search-card h3 {
  font-size: 24px;
  letter-spacing: 0;
  margin: 0;
}

.search-hint {
  color: var(--color-text-muted);
  font-size: 14px;
  max-width: 400px;
  margin: 0;
}

.search-form {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 500px;
  margin-top: 8px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  background: var(--color-surface);
  color: var(--color-text-main);
  outline: none;
  transition: all 0.25s ease;
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
}

.search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(11, 97, 170, 0.14);
}

.search-input::placeholder {
  color: var(--color-text-muted);
  font-family: var(--font-main);
}

.search-btn {
  white-space: nowrap;
}

.result-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  gap: 8px;
  align-items: center;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(11, 97, 170, 0.1);
  color: var(--color-lost);
}

.type-found {
  background: rgba(22, 163, 74, 0.12);
  color: var(--color-found);
}

.type-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-lost);
}

.type-found .type-dot {
  background: var(--color-found);
}

.status-badge {
  padding: 3px 8px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-open { background: rgba(11, 97, 170, 0.1); color: var(--color-lost); }
.status-claimed { background: rgba(245, 158, 11, 0.14); color: #92400E; }
.status-closed { background: rgba(55, 65, 81, 0.1); color: var(--color-closed); }
.status-returned { background: rgba(22, 163, 74, 0.12); color: #166534; }

.result-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-main);
}

.result-desc {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 12px;
  background: var(--color-surface-soft);
  border-radius: 8px;
  border: 1px solid var(--color-bot-border);
}

.meta-label {
  font-size: 9px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-main);
}

.meta-value.code {
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  letter-spacing: 0.04em;
}

.already-claimed {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-warm-surface);
  border-radius: var(--radius-md);
  color: var(--color-text-main);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
}

.form-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.form-divider::before,
.form-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.form-divider span {
  font-size: 13px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.claim-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 13px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-main);
}

.required {
  color: var(--color-danger);
}

.optional {
  font-size: 11px;
  font-weight: var(--font-weight-normal);
  color: var(--color-text-muted);
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: var(--font-main);
  color: var(--color-text-main);
  background: var(--color-surface);
  outline: none;
  transition: all 0.25s ease;
}

.form-group input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(11, 97, 170, 0.14);
}

.form-group input::placeholder {
  color: var(--color-text-muted);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.error {
  color: var(--color-danger);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  text-align: center;
  margin: 0;
}

.success-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(22, 163, 74, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  animation: scaleIn 0.5s ease;
}

.success-card h3 {
  font-size: 24px;
  margin: 0;
  letter-spacing: 0;
}

.success-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--color-surface-soft);
  border-radius: var(--radius-md);
  padding: 16px;
}

.success-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.success-row + .success-row {
  border-top: 1px solid var(--color-border);
}

.success-label {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-muted);
}

.success-value {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-main);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@media (max-width: 768px) {
  .search-form {
    flex-direction: column;
  }
  .bento-card {
    padding: 20px;
  }
  .form-actions {
    flex-direction: column;
  }
  .form-actions .btn-outline,
  .form-actions .btn-primary {
    width: 100%;
    text-align: center;
  }
}
</style>
