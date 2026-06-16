<template>
  <div v-if="open" class="drawer-overlay" @click="$emit('close')">
    <aside class="drawer-panel" @click.stop>
      <header class="drawer-header">
        <div>
          <h3>Item Detail</h3>
          <p>{{ item?.unique_code || `LF-${item?.id}` }}</p>
        </div>
        <button class="close-btn" @click="$emit('close')" aria-label="Close detail">
          ✕
        </button>
      </header>

      <div v-if="item" class="drawer-body">
        <div class="photo-wrap">
          <img v-if="item.image_url" :src="item.image_url" alt="Item photo" class="photo" />
          <div v-else class="photo-empty">
            <div class="photo-empty-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="currentColor" d="M5.75 5h12.5A2.75 2.75 0 0 1 21 7.75v8.5A2.75 2.75 0 0 1 18.25 19H5.75A2.75 2.75 0 0 1 3 16.25v-8.5A2.75 2.75 0 0 1 5.75 5Zm0 1.5c-.69 0-1.25.56-1.25 1.25v8.5c0 .69.56 1.25 1.25 1.25h12.5c.69 0 1.25-.56 1.25-1.25v-8.5c0-.69-.56-1.25-1.25-1.25H5.75Z"/>
                <circle cx="8.75" cy="9" r="1.25" fill="currentColor"/>
                <path fill="currentColor" d="m7.3 15.7 2.6-2.9c.33-.37.91-.38 1.26-.03l1.3 1.3 1.75-1.95c.33-.36.9-.38 1.25-.03l2.24 2.17v1.73H7.3v-.3Z"/>
              </svg>
            </div>
            <strong>Foto belum tersedia</strong>
            <span>Unggah foto untuk membantu pencocokan klaim lebih cepat.</span>
          </div>
        </div>

        <section class="meta-grid">
          <div class="meta-item"><span class="meta-label">Title</span><span class="meta-value">{{ item.title }}</span></div>
          <div class="meta-item"><span class="meta-label">Type</span><span class="meta-value">{{ item.type }}</span></div>
          <div class="meta-item"><span class="meta-label">Category</span><span class="meta-value">{{ item.category }}</span></div>
          <div class="meta-item"><span class="meta-label">Status</span><span class="meta-value">{{ item.status }}</span></div>
          <div class="meta-item"><span class="meta-label">Location</span><span class="meta-value">{{ item.location || "-" }}</span></div>
          <div class="meta-item"><span class="meta-label">Reporter</span><span class="meta-value">{{ item.reporter_name || "Anonymous" }}</span></div>
          <div class="meta-item"><span class="meta-label">Reported At</span><span class="meta-value">{{ formatDate(item.created_at) }}</span></div>
        </section>

        <section v-if="canVerify" class="actions">
          <button class="btn-primary" :disabled="verifying" @click="verifyReturned">
            <span v-if="verifying">Processing...</span>
            <span v-else>Verify & Mark Returned</span>
          </button>
          <p v-if="actionError" class="error">{{ actionError }}</p>
        </section>

        <section class="timeline-wrap">
          <div class="timeline-head">
            <h4>Timeline</h4>
            <button class="btn-ghost" :disabled="loadingTimeline" @click="loadTimeline">Refresh</button>
          </div>

          <p v-if="loadingTimeline" class="muted">Loading timeline...</p>
          <p v-else-if="timelineError" class="error">{{ timelineError }}</p>
          <p v-else-if="timeline.length === 0" class="muted">Belum ada riwayat.</p>

          <ul v-else class="timeline-list">
            <li v-for="event in timeline" :key="`${event.id}-${event.created_at}`" class="timeline-item">
              <div class="dot"></div>
              <div class="event-content">
                <div class="event-top">
                  <strong>{{ event.event_label }}</strong>
                  <span class="event-time">{{ formatDate(event.created_at) }}</span>
                </div>
                <div class="event-sub">
                  <span>{{ event.actor_name_snapshot || "System" }}</span>
                  <span v-if="event.event_note">• {{ event.event_note }}</span>
                </div>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import api from '../services/api.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  item: { type: Object, default: null },
  user: { type: Object, default: null },
})

const emit = defineEmits(['close', 'updated'])

const loadingTimeline = ref(false)
const timelineError = ref('')
const timeline = ref([])
const actionError = ref('')
const verifying = ref(false)

const canVerify = computed(() => props.user?.role === 'petugas' && props.item?.status === 'claimed')

watch(
  () => [props.open, props.item?.id],
  ([isOpen, itemId]) => {
    if (isOpen && itemId) loadTimeline()
  },
  { immediate: true }
)

async function loadTimeline() {
  if (!props.item?.id) return
  loadingTimeline.value = true
  timelineError.value = ''
  try {
    const res = await api.get(`/api/items/${props.item.id}/timeline`)
    timeline.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    timelineError.value = err.response?.data?.detail || 'Gagal memuat timeline'
  } finally {
    loadingTimeline.value = false
  }
}

async function verifyReturned() {
  if (!props.item?.id || verifying.value) return
  verifying.value = true
  actionError.value = ''
  try {
    await api.post(`/api/items/${props.item.id}/verify-return`, {})
    emit('updated', props.item.id)
    await loadTimeline()
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Gagal verifikasi pengembalian'
  } finally {
    verifying.value = false
  }
}

function formatDate(value) {
  if (!value) return '-'
  const d = new Date(value)
  return d.toLocaleString('id-ID', { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.drawer-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.35); z-index: 150; display: flex; justify-content: flex-end; }
.drawer-panel { width: min(560px, 100vw); height: 100vh; background: var(--color-surface); border-left: 1px solid var(--color-border); display: flex; flex-direction: column; overflow: hidden; }
.drawer-header { padding: 18px 20px; border-bottom: 1px solid var(--color-border); display: flex; align-items: flex-start; justify-content: space-between; flex-shrink: 0; }
.drawer-header h3 { margin: 0; font-size: 20px; }
.drawer-header p { margin: 6px 0 0; color: var(--color-text-muted); font-size: 12px; }
.close-btn { border: 1px solid var(--color-border); background: var(--color-surface); border-radius: 8px; width: 32px; height: 32px; cursor: pointer; }
.drawer-body { padding: 16px 20px 24px; overflow-y: auto; min-height: 0; display: flex; flex-direction: column; gap: 16px; -webkit-overflow-scrolling: touch; }
.photo-wrap { width: 100%; border: 1px solid var(--color-border); border-radius: 12px; overflow: hidden; background: var(--bg-color); min-height: 210px; display: flex; align-items: center; justify-content: center; }
.photo { width: 100%; max-height: 340px; object-fit: cover; display: block; }
.photo-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 18px; text-align: center; color: var(--color-text-muted); }
.photo-empty strong { color: var(--color-text-main); font-size: 14px; }
.photo-empty span { font-size: 12px; max-width: 260px; line-height: 1.4; }
.photo-empty-icon { width: 54px; height: 54px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; background: rgba(10, 97, 170, 0.12); color: var(--color-primary); }
.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.meta-item { border: 1px solid var(--color-border); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 4px; }
.meta-label { font-size: 10px; text-transform: uppercase; color: var(--color-text-muted); }
.meta-value { font-size: 13px; font-weight: 600; color: var(--color-text-main); word-break: break-word; }
.actions { display: flex; flex-direction: column; gap: 8px; }
.timeline-wrap { border-top: 1px solid var(--color-border); padding-top: 10px; min-height: 0; display: flex; flex-direction: column; gap: 8px; }
.timeline-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.timeline-head h4 { margin: 0; font-size: 16px; }
.timeline-list { list-style: none; margin: 0; padding: 0 2px 2px 0; display: flex; flex-direction: column; gap: 10px; }
.timeline-item { display: flex; gap: 10px; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: var(--color-primary); margin-top: 8px; flex-shrink: 0; }
.event-content { flex: 1; border: 1px solid var(--color-border); border-radius: 10px; padding: 10px; }
.event-top { display: flex; justify-content: space-between; gap: 10px; font-size: 13px; }
.event-time { color: var(--color-text-muted); font-size: 11px; white-space: nowrap; }
.event-sub { margin-top: 6px; color: var(--color-text-muted); font-size: 12px; }
.muted { color: var(--color-text-muted); font-size: 13px; margin: 0; }
.error { color: var(--color-danger); font-size: 13px; margin: 0; }
.btn-primary { background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: 10px; padding: 10px 12px; cursor: pointer; font-weight: 600; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { border: 1px solid var(--color-border); background: transparent; border-radius: 8px; padding: 6px 10px; cursor: pointer; font-size: 12px; }
@media (max-width: 768px) {
  .drawer-panel { width: 100vw; }
  .drawer-header { padding: 14px 14px 12px; }
  .drawer-body { padding: 12px 14px 18px; gap: 12px; }
  .meta-grid { grid-template-columns: 1fr; }
  .photo-wrap { min-height: 170px; }
}
</style>
