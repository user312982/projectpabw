<template>
  <div class="item-card" :class="item.type === 'lost' ? 'item-lost' : 'item-found'" @click="$emit('click', item)">
    <div class="card-media">
      <img
        v-if="item.image_url && !imageLoadFailed"
        :src="item.image_url"
        alt="Foto barang"
        class="item-photo"
        @error="onImageError"
      />
      <div v-else class="photo-placeholder">
        <svg width="30" height="30" viewBox="0 0 24 24" aria-hidden="true">
          <path class="icon-fill-soft" d="M5.75 5h12.5A2.75 2.75 0 0 1 21 7.75v8.5A2.75 2.75 0 0 1 18.25 19H5.75A2.75 2.75 0 0 1 3 16.25v-8.5A2.75 2.75 0 0 1 5.75 5Z"/>
          <path class="icon-fill-strong" d="M8.75 10.5a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5Zm-2.4 6h11.3c.6 0 .93-.7.55-1.16l-3.08-3.76a1.1 1.1 0 0 0-1.67-.03l-2.07 2.35-.83-.85a1.1 1.1 0 0 0-1.57 0L5.85 15.3c-.42.45-.1 1.2.5 1.2Z"/>
        </svg>
        <span>Belum ada foto</span>
      </div>
      <div class="media-overlay"></div>
      <div class="card-header">
        <div class="header-left">
          <span class="type-badge" :class="item.type === 'lost' ? 'type-lost' : 'type-found'">
            <span class="type-dot"></span>
            {{ item.type === 'lost' ? 'Hilang' : 'Ditemukan' }}
          </span>
        </div>
        <span class="time-badge">{{ relativeTime }}</span>
      </div>
      <span class="status-badge" :class="'status-' + item.status">
        {{ statusLabel }}
      </span>
    </div>

    <div class="card-inner">
      <div class="title-row">
        <h3 class="card-title">{{ item.title }}</h3>
        <span class="category-pill">{{ capitalize(item.category) }}</span>
      </div>

      <p class="card-desc" v-if="item.description">{{ item.description }}</p>

      <!-- Meta Info Grid -->
      <div class="meta-grid">
        <div class="meta-item full-width" v-if="item.location">
          <div class="meta-icon-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
              <path class="icon-fill-soft" d="M12 2.75A7.25 7.25 0 0 0 4.75 10c0 5.28 5.82 10.34 6.55 10.95a1.1 1.1 0 0 0 1.4 0c.73-.61 6.55-5.67 6.55-10.95A7.25 7.25 0 0 0 12 2.75Z"/>
              <path class="icon-fill-strong" d="M12 12.75A2.75 2.75 0 1 0 12 7.25a2.75 2.75 0 0 0 0 5.5Z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Location</span>
            <span class="meta-value">{{ item.location }}</span>
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-icon-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
              <path class="icon-fill-soft" d="M4.75 6.25A2.25 2.25 0 0 1 7 4h10a2.25 2.25 0 0 1 2.25 2.25v11.5A2.25 2.25 0 0 1 17 20H7a2.25 2.25 0 0 1-2.25-2.25V6.25Z"/>
              <path class="icon-fill-strong" d="M8.25 8.25A1.25 1.25 0 0 1 9.5 7h5A1.25 1.25 0 0 1 15.75 8.25v.5A1.25 1.25 0 0 1 14.5 10h-5a1.25 1.25 0 0 1-1.25-1.25v-.5Zm0 5A1.25 1.25 0 0 1 9.5 12h1A1.25 1.25 0 0 1 11.75 13.25v1.5A1.25 1.25 0 0 1 10.5 16h-1a1.25 1.25 0 0 1-1.25-1.25v-1.5Zm4 0A1.25 1.25 0 0 1 13.5 12h1a1.25 1.25 0 0 1 1.25 1.25v1.5A1.25 1.25 0 0 1 14.5 16h-1a1.25 1.25 0 0 1-1.25-1.25v-1.5Z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Category</span>
            <span class="meta-value">{{ capitalize(item.category) }}</span>
          </div>
        </div>

        <div class="meta-item" v-if="item.reporter_name || editingReporter">
          <div class="meta-icon-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
              <path class="icon-fill-soft" d="M12 12.25a4.25 4.25 0 1 0 0-8.5 4.25 4.25 0 0 0 0 8.5Z"/>
              <path class="icon-fill-strong" d="M5.25 19.15c0-3.05 2.72-5.4 6.75-5.4s6.75 2.35 6.75 5.4c0 .61-.5 1.1-1.1 1.1H6.35c-.6 0-1.1-.49-1.1-1.1Z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Reporter</span>
            <span v-if="!editingReporter" class="meta-value">{{ item.reporter_name || 'Anonymous' }}</span>
            <div v-else class="inline-edit">
              <input
                v-model="editReporterName"
                type="text"
                class="inline-edit-input"
                placeholder="Reporter name"
                @keyup.enter="saveReporterName"
                @keyup.escape="cancelEditReporter"
                ref="reporterInput"
              />
              <button class="inline-edit-btn save-btn" @click="saveReporterName" title="Save">
                <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.35 16.9 4.9 12.45l1.55-1.55 2.9 2.9 8.2-8.2 1.55 1.55-9.75 9.75Z"/></svg>
              </button>
              <button class="inline-edit-btn cancel-btn" @click="cancelEditReporter" title="Cancel">
                <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m12 10.45 4.65-4.65 1.55 1.55L13.55 12l4.65 4.65-1.55 1.55L12 13.55 7.35 18.2 5.8 16.65 10.45 12 5.8 7.35 7.35 5.8 12 10.45Z"/></svg>
              </button>
            </div>
          </div>
          <button v-if="canEdit && !editingReporter" class="edit-icon-btn" @click.stop="startEditReporter" title="Edit reporter name">
            <svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m5 16.6-.55 3.35 3.35-.55L18.45 8.75 15.65 5.95 5 16.6Zm14.5-8.9.65-.65a1.98 1.98 0 0 0 0-2.8l-.4-.4a1.98 1.98 0 0 0-2.8 0l-.65.65 3.2 3.2Z"/></svg>
          </button>
        </div>

        <div class="meta-item" v-if="!item.reporter_name && !editingReporter">
          <div class="meta-icon-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
              <path class="icon-fill-soft" d="M12 12.25a4.25 4.25 0 1 0 0-8.5 4.25 4.25 0 0 0 0 8.5Z"/>
              <path class="icon-fill-strong" d="M5.25 19.15c0-3.05 2.72-5.4 6.75-5.4s6.75 2.35 6.75 5.4c0 .61-.5 1.1-1.1 1.1H6.35c-.6 0-1.1-.49-1.1-1.1Z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Reporter</span>
            <span class="meta-value muted">Anonymous</span>
          </div>
          <button v-if="canEdit" class="edit-icon-btn" @click.stop="startEditReporter" title="Add reporter name">
            <svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M10.9 20v-6.9H4v-2.2h6.9V4h2.2v6.9H20v2.2h-6.9V20h-2.2Z"/></svg>
          </button>
        </div>

        <!-- <div class="meta-item" v-if="item.reporter_contact">
          <div class="meta-icon-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </div>
          <div class="meta-info">
            <span class="meta-label">Contact</span>
            <span class="meta-value">{{ item.reporter_contact }}</span>
          </div>
        </div> -->
      </div>

      <div class="card-footer">
        <div class="code-block" :class="{ 'copied': copied }" @click.stop="copyCode">
          <svg v-if="!copied" class="code-icon" width="15" height="15" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M7.75 4A2.75 2.75 0 0 0 5 6.75v8.5A2.75 2.75 0 0 0 7.75 18h8.5A2.75 2.75 0 0 0 19 15.25v-8.5A2.75 2.75 0 0 0 16.25 4h-8.5Zm2 5h4.5v1.75h-4.5V9Zm0 3.25h4.5V14h-4.5v-1.75Z"/>
            <path fill="currentColor" opacity=".55" d="M3 9.75A2.75 2.75 0 0 1 5.75 7H6v8.25A1.75 1.75 0 0 0 7.75 17H16v.25A2.75 2.75 0 0 1 13.25 20h-7.5A2.75 2.75 0 0 1 3 17.25v-7.5Z"/>
          </svg>
          <svg v-else class="code-icon check-icon" width="15" height="15" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M9.35 16.9 4.9 12.45l1.55-1.55 2.9 2.9 8.2-8.2 1.55 1.55-9.75 9.75Z"/>
          </svg>
          <span class="code-text">{{ item.unique_code || 'LF-' + item.id }}</span>
          <span class="code-hint">{{ copied ? 'Tersalin' : 'salin' }}</span>
        </div>
        <span class="detail-hint">Lihat detail</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick, watch } from 'vue'
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
const imageLoadFailed = ref(false)

watch(
  () => props.item.image_url,
  () => {
    imageLoadFailed.value = false
  },
  { immediate: true }
)

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
    case 'open': return 'Open'
    case 'claimed': return 'Claimed'
    case 'returned': return 'Returned'
    case 'closed': return 'Closed'
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
  const dateStr = props.item.created_at
  const then = new Date(dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z')
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
  return then.toLocaleDateString('en-US', { day: '2-digit', month: 'short' })
})

function onImageError() {
  imageLoadFailed.value = true
}
</script>

<style scoped>
.item-card {
  background: var(--color-surface);
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  cursor: pointer;
  min-height: 100%;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  position: relative;
  overflow: hidden;
  isolation: isolate;
  transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
  animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.item-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7);
  z-index: 3;
}

.item-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  z-index: 4;
}

.item-card.item-lost::after {
  background: var(--color-primary);
}

.item-card.item-found::after {
  background: var(--color-success);
}

.item-card:hover {
  border-color: rgba(11, 97, 170, 0.24);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.13);
  transform: translateY(-5px);
}

.item-card:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(11, 97, 170, 0.14), 0 18px 42px rgba(15, 23, 42, 0.13);
}

.card-media {
  width: 100%;
  aspect-ratio: 16 / 10;
  min-height: 168px;
  overflow: hidden;
  position: relative;
  background: var(--color-primary-subtle);
}

.item-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.45s ease;
}

.item-card:hover .item-photo {
  transform: scale(1.045);
}

.media-overlay {
  position: absolute;
  inset: 0;
  background: rgba(33, 37, 41, 0.14);
  pointer-events: none;
}

.photo-placeholder {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.icon-fill-soft {
  fill: rgba(11, 97, 170, 0.18);
}

.icon-fill-strong {
  fill: currentColor;
}

.card-header {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  z-index: 2;
}

.header-left {
  display: flex;
  gap: 6px;
  align-items: center;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 11px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.16);
}

.type-lost {
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-lost);
}

.type-found {
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-found);
}

.type-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.type-lost .type-dot {
  background: var(--color-lost);
  animation: pulse 2s infinite;
}

.type-found .type-dot {
  background: var(--color-found);
}

.status-badge {
  position: absolute;
  left: 16px;
  bottom: 16px;
  z-index: 2;
  padding: 7px 11px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid rgba(255, 255, 255, 0.56);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(10px);
}

.status-open {
  background: rgba(11, 97, 170, 0.9);
  color: #FFFFFF;
}

.status-claimed {
  background: rgba(245, 183, 90, 0.95);
  color: var(--color-on-accent);
}

.status-closed {
  background: rgba(55, 65, 81, 0.9);
  color: #FFFFFF;
}

.status-returned {
  background: rgba(22, 163, 74, 0.92);
  color: #FFFFFF;
}

.time-badge {
  padding: 7px 10px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(10px);
}

.card-inner {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.card-title {
  flex: 1;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.22;
  color: var(--color-text-main);
  margin: 0;
  letter-spacing: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.category-pill {
  flex-shrink: 0;
  max-width: 112px;
  padding: 5px 9px;
  border-radius: var(--radius-pill);
  background: var(--color-warm-surface);
  color: #92400E;
  border: 1px solid rgba(245, 183, 90, 0.24);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.035em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-desc {
  min-height: 38px;
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.48;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding: 9px 10px;
  background: var(--bg-color);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.meta-item.full-width {
  grid-column: 1 / -1;
}

.meta-item.full-width .meta-value {
  white-space: normal;
  word-break: break-word;
}

.meta-icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 0px;
  min-width: 0;
}

.meta-label {
  font-size: 9px;
  font-weight: 800;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-value.muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding-top: 2px;
}

.code-block {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  max-width: 100%;
  padding: 9px 12px;
  background: var(--color-primary);
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  box-shadow: 0 8px 18px rgba(11, 97, 170, 0.2);
}

.code-block:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(11, 97, 170, 0.28);
}

.code-icon {
  color: rgba(255, 255, 255, 0.82);
  flex-shrink: 0;
}

.code-text {
  min-width: 0;
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  font-weight: 800;
  color: var(--color-on-primary);
  letter-spacing: 0.03em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.code-hint {
  font-size: 10px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.72);
  text-transform: lowercase;
  white-space: nowrap;
}

.code-block.copied {
  background: var(--color-success);
  animation: copySuccess 0.4s ease;
}

.code-block.copied .code-icon,
.code-block.copied .code-text,
.code-block.copied .code-hint {
  color: #FFFFFF;
}

.detail-hint {
  flex-shrink: 0;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
}

.check-icon {
  animation: checkPop 0.3s ease;
}

.edit-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: none;
  background: rgba(11, 97, 170, 0.08);
  color: var(--color-text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
  padding: 0;
}

.edit-icon-btn:hover {
  background: rgba(11, 97, 170, 0.14);
  color: var(--color-primary);
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
  border: 1px solid var(--color-text-muted);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-main);
  background: var(--color-surface);
  outline: none;
  font-family: inherit;
}

.inline-edit-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(11, 97, 170, 0.14);
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
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.inline-edit-btn.save-btn:hover {
  background: var(--color-primary-dark);
}

.inline-edit-btn.cancel-btn {
  background: var(--color-surface-soft);
  color: var(--color-text-main);
}

.inline-edit-btn.cancel-btn:hover {
  background: var(--color-bot-border);
}

@media (max-width: 420px) {
  .card-header {
    left: 12px;
    right: 12px;
  }

  .status-badge {
    left: 12px;
    bottom: 12px;
  }

  .card-inner {
    padding: 14px;
  }

  .title-row,
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .category-pill,
  .code-block {
    max-width: 100%;
  }

  .detail-hint {
    display: none;
  }
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
