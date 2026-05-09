<template>
  <div class="report-form-wrapper">
    <div class="form-header">
      <div class="form-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
      </div>
      <h3>Report Item</h3>
      <p>Fill out the form below to report a lost or found item</p>
    </div>

    <form @submit.prevent="submitForm" class="report-form">
      <!-- Type Selection -->
      <div class="form-group">
        <label class="form-label">Report Type</label>
        <div class="type-selector">
          <button
            type="button"
            class="type-btn"
            :class="{ active: form.type === 'lost', lost: form.type === 'lost' }"
            @click="form.type = 'lost'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
            Lost Item
          </button>
          <button
            type="button"
            class="type-btn"
            :class="{ active: form.type === 'found', found: form.type === 'found' }"
            @click="form.type = 'found'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            Found Item
          </button>
        </div>
      </div>

      <!-- Title -->
      <div class="form-group">
        <label class="form-label">Item Name *</label>
        <input
          v-model="form.title"
          type="text"
          placeholder="e.g. Black Leather Wallet"
          class="form-input"
          required
        />
      </div>

      <!-- Category -->
      <div class="form-group">
        <label class="form-label">Category</label>
        <select v-model="form.category" class="form-input">
          <option v-for="c in categories" :key="c.value" :value="c.value">
            {{ c.label }}
          </option>
        </select>
      </div>

      <!-- Two Column Row -->
      <div class="form-row">
        <!-- Description -->
        <div class="form-group form-group-full">
          <label class="form-label">Description</label>
          <textarea
            v-model="form.description"
            placeholder="Item description, color, brand, etc..."
            class="form-input form-textarea"
            rows="3"
          ></textarea>
        </div>
      </div>

      <!-- Location & Date -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Location</label>
          <input
            v-model="form.location"
            type="text"
            placeholder="e.g. Building A, 2nd Floor"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Date of Incident</label>
          <input
            v-model="form.date_event"
            type="date"
            class="form-input"
          />
        </div>
      </div>

      <!-- Reporter Info -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Reporter Name</label>
          <input
            v-model="form.reporter_name"
            type="text"
            placeholder="Full name (optional)"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Reporter Contact</label>
          <input
            v-model="form.reporter_contact"
            type="text"
            placeholder="Phone / Email / LINE ID"
            class="form-input"
          />
        </div>
      </div>

      <!-- Submit -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="submitting || !form.title"
      >
        <span v-if="!submitting">Submit Report</span>
        <span v-else class="btn-loading">
          <span class="spinner"></span>
          Submitting...
        </span>
      </button>

      <!-- Status Message -->
      <div v-if="statusMessage" :class="['status-msg', statusType]">
        <svg v-if="statusType === 'success'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        {{ statusMessage }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../services/api.js'

const emit = defineEmits(['submitted'])

const categories = [
  { label: 'Electronics', value: 'elektronik' },
  { label: 'Clothing', value: 'pakaian' },
  { label: 'Documents', value: 'dokumen' },
  { label: 'Accessories', value: 'aksesoris' },
  { label: 'Bags', value: 'tas' },
  { label: 'Keys', value: 'kunci' },
  { label: 'Others', value: 'lainnya' },
]

const form = reactive({
  type: 'lost',
  title: '',
  description: '',
  category: 'lainnya',
  location: '',
  date_event: '',
  reporter_name: '',
  reporter_contact: '',
})

const submitting = ref(false)
const statusMessage = ref('')
const statusType = ref('')

async function submitForm() {
  if (!form.title) return

  submitting.value = true
  statusMessage.value = ''

  try {
    await api.post('/api/items', {
      ...form,
      date_event: form.date_event || null,
      reporter_name: form.reporter_name || null,
    })

    statusMessage.value = 'Report submitted successfully!'
    statusType.value = 'success'

    // Reset form
    form.title = ''
    form.description = ''
    form.category = 'lainnya'
    form.location = ''
    form.date_event = ''
    form.reporter_name = ''
    form.reporter_contact = ''

    emit('submitted')
  } catch (err) {
    statusMessage.value = 'Failed to submit report. Please try again.'
    statusType.value = 'error'
    console.error(err)
  } finally {
    submitting.value = false
    setTimeout(() => {
      statusMessage.value = ''
    }, 4000)
  }
}
</script>

<style scoped>
.report-form-wrapper {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 36px;
  animation: scaleIn 0.4s ease;
  position: relative;
  overflow: hidden;
}

.report-form-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-accent);
}

.form-header {
  margin-bottom: 32px;
}

.form-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--gradient-accent);
  color: var(--color-on-primary);
  margin-bottom: 16px;
}

.form-header h3 {
  font-size: 28px;
  font-weight: var(--font-weight-heavy);
  text-transform: uppercase;
  letter-spacing: -0.02em;
  margin: 0;
  color: var(--color-text-main);
}

.form-header p {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-top: 8px;
  font-weight: var(--font-weight-medium);
}

.report-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.form-input {
  padding: 14px 18px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-main);
  background: var(--color-light-gray);
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s, background 0.25s;
  font-family: inherit;
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(84, 107, 65, 0.1);
  background: var(--color-surface);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.type-selector {
  display: flex;
  gap: 8px;
}

.type-btn {
  flex: 1;
  padding: 14px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-light-gray);
  font-weight: var(--font-weight-bold);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.25s;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.type-btn:hover {
  border-color: var(--color-text-main);
  color: var(--color-text-main);
}

.type-btn.active.lost {
  background: var(--gradient-lost);
  color: var(--color-text-main);
  border-color: rgba(84, 107, 65, 0.3);
  box-shadow: 0 4px 16px rgba(84, 107, 65, 0.15);
}

.type-btn.active.found {
  background: var(--gradient-found);
  color: var(--color-text-main);
  border-color: rgba(153, 173, 122, 0.4);
  box-shadow: 0 4px 16px rgba(153, 173, 122, 0.2);
}

.submit-btn {
  padding: 16px;
  border: none;
  border-radius: var(--radius-pill);
  background: var(--gradient-dark);
  color: var(--color-on-primary);
  font-weight: var(--font-weight-bold);
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 0.25s;
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 8px 24px rgba(14,14,14,0.25);
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: var(--color-on-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-msg {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  animation: slideIn 0.3s ease;
}

.status-msg.success {
  background: #D1FAE5;
  color: #065F46;
}

.status-msg.error {
  background: #FEE2E2;
  color: #991B1B;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .report-form-wrapper {
    padding: 24px;
  }
}
</style>
