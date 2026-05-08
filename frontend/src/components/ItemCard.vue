<template>
  <div class="item-card" @click="$emit('click', item)">
    <!-- Left Color Accent -->
    <div class="card-accent" :class="item.type === 'lost' ? 'accent-lost' : 'accent-found'"></div>

    <div class="card-inner">
      <!-- Top Row: Type Badge + Status + Date -->
      <div class="card-header">
        <div class="header-left">
          <span class="type-badge" :class="item.type === 'lost' ? 'type-lost' : 'type-found'">
            <span class="type-dot"></span>
            {{ item.type === 'lost' ? 'Hilang' : 'Ditemukan' }}
          </span>
          <span class="status-badge" :class="'status-' + item.status">
            {{ statusLabel }}
          </span>
        </div>
        <span class="time-badge">{{ relativeTime }}</span>
      </div>

      <!-- Title -->
      <h3 class="card-title">{{ item.title }}</h3>

      <!-- Description -->
      <p class="card-desc" v-if="item.description">{{ item.description }}</p>

      <!-- Code Block -->
      <div class="code-block" :class="{ 'copied': copied }" @click.stop="copyCode">
        <svg v-if="!copied" class="code-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2"/>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
        </svg>
        <svg v-else class="code-icon check-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span class="code-text">{{ item.unique_code || 'LF-' + item.id }}</span>
        <span class="code-hint">{{ copied ? 'tersalin!' : 'salin' }}</span>
      </div>

      <!-- Meta Info Grid -->
      <div class="meta-grid">
        <div class="meta-item">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 7V4a2 2 0 0 1 2-2h8.5L20 7.5V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-3"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Kategori</span>
            <span class="meta-value">{{ capitalize(item.category) }}</span>
          </div>
        </div>

        <div class="meta-item" v-if="item.location">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Lokasi</span>
            <span class="meta-value">{{ item.location }}</span>
          </div>
        </div>

        <div class="meta-item" v-if="item.reporter_name || editingReporter">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Pelapor</span>
            <span v-if="!editingReporter" class="meta-value">{{ item.reporter_name || 'Anonim' }}</span>
            <div v-else class="inline-edit">
              <input
                v-model="editReporterName"
                type="text"
                class="inline-edit-input"
                placeholder="Nama pelapor"
                @keyup.enter="saveReporterName"
                @keyup.escape="cancelEditReporter"
                ref="reporterInput"
              />
              <button class="inline-edit-btn save-btn" @click="saveReporterName" title="Simpan">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </button>
              <button class="inline-edit-btn cancel-btn" @click="cancelEditReporter" title="Batal">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
          </div>
          <button v-if="canEdit && !editingReporter" class="edit-icon-btn" @click.stop="startEditReporter" title="Edit nama pelapor">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          </button>
        </div>

        <div class="meta-item" v-if="!item.reporter_name && !editingReporter">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Pelapor</span>
            <span class="meta-value muted">Anonim</span>
          </div>
          <button v-if="canEdit" class="edit-icon-btn" @click.stop="startEditReporter" title="Tambah nama pelapor">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
        </div>

        <div class="meta-item" v-if="item.reporter_contact">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Kontak</span>
            <span class="meta-value">{{ item.reporter_contact }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue'
import api from '../services/api.js'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['click', 'code-copied', 'updated'])

const copied = ref(false)
const editingReporter = ref(false)
const editReporterName = ref('')
const reporterInput = ref(null)
const savingReporter = ref(false)

const canEdit = computed(() => props.user && props.user.id === props.item.uploader_id)

function startEditReporter() {
  editReporterName.value = props.item.reporter_name || ''
  editingReporter.value = true
  nextTick(() => {
    if (reporterInput.value) reporterInput.value.focus()
  })
}

function cancelEditReporter() {
  editingReporter.value = false
  editReporterName.value = ''
}

async function saveReporterName() {
  if (savingReporter.value) return
  savingReporter.value = true
  try {
    await api.put(`/api/items/${props.item.id}`, {
      reporter_name: editReporterName.value || null,
    })
    editingReporter.value = false
    editReporterName.value = ''
    emit('updated', props.item.id)
  } catch (err) {
    console.error('Failed to update reporter name:', err)
  } finally {
    savingReporter.value = false
  }
}

function copyCode() {
  const code = props.item.unique_code || 'LF-' + props.item.id
  navigator.clipboard.writeText(code)
  emit('code-copied', code)
  
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

const statusLabel = computed(() => {
  switch (props.item.status) {
    case 'open': return 'Aktif'
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
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60) return 'Baru saja'
  if (diff < 3600) return `${Math.floor(diff / 60)} menit`
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam`
  if (diff < 604800) return `${Math.floor(diff / 86400)} hari`
  return then.toLocaleDateString('id-ID', { day: '2-digit', month: 'short' })
})
</script>

<style scoped>
.item-card {
  background: #FFF8EC;
  border-radius: 14px;
  display: flex;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(84, 107, 65, 0.08);
  position: relative;
  overflow: hidden;
  animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(84, 107, 65, 0.15);
}

.card-accent {
  width: 4px;
  flex-shrink: 0;
  transition: width 0.25s ease;
}

.item-card:hover .card-accent {
  width: 6px;
}

.accent-lost {
  background: #99AD7A;
}

.accent-found {
  background: #546B41;
}

.card-inner {
  flex: 1;
  padding: 14px 16px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
}

.header-left {
  display: flex;
  gap: 6px;
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
  letter-spacing: 0.01em;
}

.type-lost {
  background: rgba(153, 173, 122, 0.2);
  color: #546B41;
}

.type-found {
  background: rgba(84, 107, 65, 0.12);
  color: #546B41;
}

.type-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

.type-lost .type-dot {
  background: #99AD7A;
  animation: pulse 2s infinite;
}

.type-found .type-dot {
  background: #546B41;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-open {
  background: rgba(153, 173, 122, 0.2);
  color: #546B41;
}

.status-claimed {
  background: rgba(220, 204, 172, 0.4);
  color: #546B41;
}

.status-closed {
  background: rgba(84, 107, 65, 0.08);
  color: #99AD7A;
}

.time-badge {
  font-size: 10px;
  font-weight: 500;
  color: #99AD7A;
  white-space: nowrap;
}

/* Title */
.card-title {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.3;
  color: #546B41;
  margin: 0;
  letter-spacing: -0.01em;
}

/* Description */
.card-desc {
  font-size: 12px;
  color: #99AD7A;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Code Block */
.code-block {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
  padding: 6px 12px;
  background: #546B41;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.code-block:hover {
  background: #3d4f2f;
  transform: translateY(-1px);
}

.code-icon {
  color: #DCCCAC;
  flex-shrink: 0;
}

.code-text {
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  font-weight: 700;
  color: #FFF8EC;
  letter-spacing: 0.04em;
}

.code-hint {
  font-size: 9px;
  font-weight: 500;
  color: #DCCCAC;
  text-transform: lowercase;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.code-block:hover .code-hint {
  opacity: 1;
}

/* Copied State */
.code-block.copied {
  background: #99AD7A;
  animation: copySuccess 0.4s ease;
}

.code-block.copied .code-icon,
.code-block.copied .code-text,
.code-block.copied .code-hint {
  color: #546B41;
}

.code-block.copied .code-hint {
  opacity: 1;
  font-weight: 600;
}

.check-icon {
  animation: checkPop 0.3s ease;
}

@keyframes copySuccess {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes checkPop {
  0% { transform: scale(0) rotate(-45deg); }
  50% { transform: scale(1.2) rotate(0deg); }
  100% { transform: scale(1) rotate(0deg); }
}

/* Meta Grid */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(220, 204, 172, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(220, 204, 172, 0.5);
}

.meta-icon-wrap {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(84, 107, 65, 0.1);
  color: #546B41;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 0px;
  min-width: 0;
}

.meta-label {
  font-size: 9px;
  font-weight: 500;
  color: #99AD7A;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-value {
  font-size: 11px;
  font-weight: 600;
  color: #546B41;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-value.muted {
  color: #99AD7A;
  font-style: italic;
}

.edit-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: none;
  background: rgba(84, 107, 65, 0.08);
  color: #99AD7A;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
  padding: 0;
}

.edit-icon-btn:hover {
  background: rgba(84, 107, 65, 0.2);
  color: #546B41;
}

.inline-edit {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.inline-edit-input {
  flex: 1;
  min-width: 0;
  padding: 2px 6px;
  border: 1px solid #99AD7A;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #546B41;
  background: #FFF8EC;
  outline: none;
  font-family: inherit;
}

.inline-edit-input:focus {
  border-color: #546B41;
  box-shadow: 0 0 0 2px rgba(84, 107, 65, 0.15);
}

.inline-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
  transition: all 0.2s ease;
}

.inline-edit-btn.save-btn {
  background: #546B41;
  color: #FFF8EC;
}

.inline-edit-btn.save-btn:hover {
  background: #3d4f2f;
}

.inline-edit-btn.cancel-btn {
  background: rgba(220, 204, 172, 0.5);
  color: #546B41;
}

.inline-edit-btn.cancel-btn:hover {
  background: rgba(220, 204, 172, 0.8);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.97) translateY(6px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
