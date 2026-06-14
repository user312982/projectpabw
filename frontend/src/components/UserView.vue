<template>
  <div class="user-view" :class="{ 'has-searched': hasSearched }">
    <!-- Logo -->
    <div class="logo-container">
      <img class="logo-icon" src="../assets/itk/logo-itk-white-notext.webp" alt="Logo Institut Teknologi Kalimantan" />
      <div class="logo-text">
        <span class="logo-title">ITK</span>
        <span class="logo-subtitle">Lost & Found</span>
      </div>
    </div>

    <!-- Top Right Guide Button -->
    <button class="guide-btn" @click="showGuide = true">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      <span>Panduan</span>
    </button>
    <button class="logout-btn" @click="$emit('logout')">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      <span>Logout</span>
    </button>

    <!-- Initial Search Engine View -->
    <div class="search-engine-view" v-if="!hasSearched">
      <div class="brand">
        <img class="hero-itk-logo" src="../assets/itk/logo-itk-with-gear.webp" alt="Logo Institut Teknologi Kalimantan" />
        <div class="campus-pill">Institut Teknologi Kalimantan</div>
        <h1>ITK <span class="brand-text">Lost & Found</span></h1>
        <p>Asisten AI Pencarian Barang Hilang & Ditemukan di lingkungan kampus ITK</p>
      </div>
      
      <form @submit.prevent="handleInitialSearch" class="search-form">
        <div class="search-input-wrapper">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input 
            type="text" 
            v-model="initialQuery" 
            placeholder="Tanya saya, misalnya: 'Cari dompet hitam di lobi' atau 'Lapor barang hilang'"
            class="search-input"
            autofocus
          />
        </div>
        <div class="search-actions">
          <button type="submit" class="btn btn-primary" :disabled="!initialQuery.trim()">Mulai Chat AI</button>
          <button type="button" class="btn btn-outline" @click="showGuide = true">Apa yang bisa saya lakukan?</button>
        </div>
      </form>
    </div>

    <!-- Active Chat View (After Search) -->
    <div class="active-chat-view" v-else>
      <div class="content-left">
        <div class="content-header">
           <h2>Hasil Pencarian & Laporan Terkini</h2>
           <p>Berikut adalah data yang ada di sistem, AI akan memandu Anda di sebelah kanan.</p>
        </div>
        <ItemList :items="allItems" :user="user" :enable-detail-drawer="true" @code-copied="handleCodeCopied" @updated="fetchItems" />
      </div>
      <div class="content-right">
        <!-- AiChat Component -->
        <AiChat ref="chatComponent" @data-changed="handleDataChanged" />
      </div>
    </div>

    <!-- Guide Modal -->
    <div class="modal-overlay" v-if="showGuide" @click="showGuide = false">
      <div class="modal-content bento-card" @click.stop>
        <h2>Panduan Penggunaan</h2>
        <p>Anda dapat berinteraksi dengan AI untuk mengurus barang hilang/ditemukan tanpa perlu melihat banyak menu complex.</p>
        <ul class="guide-list">
          <li><strong>Mencari Barang:</strong> "Cari dompet warna hitam" atau "Apakah ada kunci motor scoopy?"</li>
          <li><strong>Lapor Hilang:</strong> "Saya mau lapor dompet saya hilang di gedung A, nama saya Budi"</li>
          <li><strong>Lapor Ditemukan:</strong> "Saya menemukan jam tangan di parkiran depan, saya Andi"</li>
          <li><strong>Melihat Data:</strong> "Tampilkan laporan terbaru"</li>
          <li><strong>Mengubah Data:</strong> Klik tombol kode di card barang, lalu tekan enter untuk ubah</li>
          <li><strong>Klaim Barang:</strong> Klik tombol kode di card barang, lalu tekan enter untuk klaim</li>
        </ul>
        <p class="guide-hint">Tip: Klik tombol kode di samping card barang untuk mengubah atau klaim!</p>
        <button class="btn btn-black" @click="showGuide = false">Mengerti</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api.js'
import AiChat from './AiChat.vue'
import ItemList from './ItemList.vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['logout'])

const showGuide = ref(false)
const hasSearched = ref(false)
const initialQuery = ref('')
const allItems = ref([])
const chatComponent = ref(null)
const activeQueryParams = ref({})

async function fetchItems(params = activeQueryParams.value) {
  try {
    const normalizedParams = params || {}
    const res = await api.get('/api/items', { params: normalizedParams })
    activeQueryParams.value = { ...normalizedParams }
    allItems.value = res.data
  } catch (e) {
    console.error('Failed to fetch items', e)
  }
}

function extractIntentFilterFromText(text) {
  const normalized = (text || '').toLowerCase()
  const wantsLost = /\bhilang\b|\blost\b/.test(normalized)
  const wantsFound = /\bditemukan\b|\bfound\b/.test(normalized)
  const wantsRecent = /\bterbaru\b|\brecent\b/.test(normalized)
  const params = {}
  if (wantsLost && !wantsFound) params.type = 'lost'
  if (wantsFound && !wantsLost) params.type = 'found'
  return { params, wantsRecent }
}

async function handleDataChanged(payload) {
  const toolsUsed = Array.isArray(payload) ? payload : (payload?.toolsUsed || [])
  const userText = Array.isArray(payload) ? '' : (payload?.userText || '')

  const searchTool = toolsUsed.find(t => t.name === 'search_items')
  if (searchTool) {
    const args = searchTool.args || {}
    const params = {}
    if (args.keyword) params.search = args.keyword
    if (args.category) params.category = args.category
    if (args.type) params.type = args.type
    try {
      await fetchItems(params)
    } catch (e) {
      console.error(e)
    }
    return
  }

  const matchTool = toolsUsed.find(t => t.name === 'match_items')
  if (matchTool) {
    const args = matchTool.args || {}
    const params = {}
    if (args.keyword) params.search = args.keyword
    try {
      await fetchItems(params)
    } catch (e) {
      console.error(e)
    }
    return
  }

  const listTool = toolsUsed.find(t => t.name === 'list_recent_items')
  if (listTool) {
    const { params } = extractIntentFilterFromText(userText)
    try {
      await fetchItems(params)
    } catch (e) {
      console.error(e)
    }
    return
  }

  if (toolsUsed && toolsUsed.length > 0) {
    try {
      const { params } = extractIntentFilterFromText(userText)
      await fetchItems(params)
    } catch (e) {
      console.error(e)
    }
    return
  }

  const { params, wantsRecent } = extractIntentFilterFromText(userText)
  if (Object.keys(params).length > 0 || wantsRecent) {
    try {
      await fetchItems(params)
    } catch (e) {
      console.error(e)
    }
    return
  }

  fetchItems();
}

function handleCodeCopied(code) {
  hasSearched.value = true
  fetchItems()
}

function handleInitialSearch() {
  if (!initialQuery.value.trim()) return
  hasSearched.value = true
  activeQueryParams.value = {}
  fetchItems()
  // Wait for AiChat to mount and send the initial query
  setTimeout(() => {
    if (chatComponent.value && chatComponent.value.sendMessageExt) {
       chatComponent.value.sendMessageExt(initialQuery.value)
    }
  }, 100)
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.user-view {
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--bg-color);
  color: var(--color-text-main);
  display: flex;
  flex-direction: column;
}

.user-view::before {
  content: '';
  position: absolute;
  right: -180px;
  bottom: -120px;
  width: min(720px, 70vw);
  aspect-ratio: 1148 / 584;
  background-image: url('../assets/itk/gear-blue-half.webp');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.08;
  pointer-events: none;
}

.user-view.has-searched {
  padding: 24px 32px 32px;
}

/* Logo Styles */
.logo-container {
  position: absolute;
  top: 24px;
  left: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10;
  background: var(--color-surface);
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-accent);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.logo-container:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.logo-icon {
  flex-shrink: 0;
  width: 34px;
  height: 40px;
  object-fit: contain;
  padding: 4px;
  border-radius: 10px;
  background: var(--color-primary);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0;
}

.logo-subtitle {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-accent);
  letter-spacing: 0.02em;
}

.guide-btn {
  position: absolute;
  top: 28px;
  right: 162px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-main);
  cursor: pointer;
  transition: 0.3s;
  z-index: 10;
  backdrop-filter: blur(5px);
}
.guide-btn:hover { background: var(--color-light-gray); border-color: var(--color-text-muted); }

.logout-btn {
  position: absolute;
  top: 28px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-main);
  cursor: pointer;
  transition: 0.3s;
  z-index: 10;
  backdrop-filter: blur(5px);
}
.logout-btn:hover { background: var(--color-light-gray); border-color: var(--color-text-muted); }

/* Search Engine View */
.search-engine-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  animation: fadeIn 0.8s ease;
  position: relative;
  z-index: 1;
}
.brand {
  text-align: center;
  margin-bottom: 36px;
}
.hero-itk-logo {
  display: block;
  width: min(260px, 72vw);
  height: 112px;
  object-fit: contain;
  margin: 0 auto 8px;
}
.campus-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  margin-bottom: 14px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(11, 97, 170, 0.16);
  background: var(--color-accent-subtle);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.02em;
}
.brand h1 {
  font-size: 72px;
  margin: 0;
  letter-spacing: 0;
}
.brand-text { color: var(--color-primary); }
.brand p { opacity: 0.8; font-size: 18px; margin-top: 15px; font-weight: 500;}

.search-form {
  width: 100%;
  max-width: 650px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.search-input-wrapper {
  position: relative;
  width: 100%;
  transition: transform 0.2s;
}
.search-input-wrapper:focus-within {
  transform: scale(1.02);
}
.search-icon {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
}
.search-input {
  width: 100%;
  padding: 24px 24px 24px 64px;
  font-size: 18px;
  border-radius: 40px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-main);
  outline: none;
  font-family: inherit;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s;
}
.search-input:focus {
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: 0 0 0 4px rgba(10, 97, 170, 0.14), var(--shadow-lg);
}
.search-input::placeholder { color: var(--color-text-muted); }

.search-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
.btn {
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}
.btn-primary { background: var(--color-primary); color: var(--color-on-primary); }
.btn-primary:active { transform: scale(0.95); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: transparent; border: 1px solid var(--color-border); color: var(--color-text-main); backdrop-filter: blur(5px);}
.btn-outline:hover { background: var(--color-light-gray); border-color: var(--color-text-muted);}

/* Active Chat View */
.active-chat-view {
  display: flex;
  gap: 24px;
  padding-top: 84px;
  flex: 1;
  min-height: 0;
}
.content-left {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  backdrop-filter: blur(12px);
  border-radius: 22px;
  padding: 24px 28px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-top: 4px solid var(--color-accent);
  animation: slideIn 0.5s ease;
  position: relative;
  z-index: 1;
}
.content-header {
  flex-shrink: 0;
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--color-border);
}
.content-header h2 {
  margin: 0 0 8px 0;
  font-size: 26px;
  letter-spacing: 0;
  line-height: 1.16;
  width: fit-content;
  padding-bottom: 10px;
  position: relative;
  color: var(--color-primary);
}
.content-header h2::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 4px;
  background: var(--color-accent);
  border-radius: var(--radius-pill);
}
.content-header p {
  margin: 0;
  opacity: 0.7;
  max-width: 680px;
}

.content-right {
  width: 420px;
  flex-shrink: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  animation: slideIn 0.5s ease;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  padding: 20px;
}
.modal-content {
  background: var(--color-surface);
  color: var(--color-text-main);
  padding: 40px;
  border-radius: 24px;
  max-width: 500px;
  width: 100%;
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.modal-content h2 { margin-top: 0; font-size: 24px; letter-spacing: 0; margin-bottom: 16px;}
.modal-content p { opacity: 0.8; line-height: 1.5; }
.guide-list { margin: 24px 0; padding-left: 20px; line-height: 1.8; opacity: 0.9;}
.guide-list li { margin-bottom: 8px; }
.btn-black { background: var(--color-text-main); color: var(--bg-color); width: 100%; border-radius: 12px; padding: 14px; font-weight: bold; border: none; cursor: pointer; transition: all 0.2s; }
.btn-black:hover { transform: translateY(-2px); opacity: 0.9; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

@media (max-width: 1024px) {
  .user-view.has-searched { padding: 16px; }
  .active-chat-view { flex-direction: column; gap: 18px; padding-top: 82px; }
  .content-right { width: 100%; height: 500px; }
  .logo-container { top: 14px; left: 16px; }
  .guide-btn { top: 16px; right: 116px; padding: 8px 12px;}
  .logout-btn { top: 16px; right: 16px; padding: 8px 12px;}
  .brand h1 { font-size: 48px; }
  .search-input { padding: 18px 20px 18px 50px; font-size: 16px; }
}

@media (max-width: 640px) {
  .logo-container {
    padding: 7px 10px;
    gap: 8px;
  }
  .logo-icon {
    width: 28px;
    height: 34px;
  }
  .logo-title { font-size: 14px; }
  .logo-subtitle { display: none; }
  .guide-btn span,
  .logout-btn span {
    display: none;
  }
  .guide-btn { right: 70px; }
  .active-chat-view { padding-top: 76px; }
  .content-left {
    border-radius: 18px;
    padding: 20px;
  }
  .content-header h2 {
    font-size: 22px;
  }
}
</style>
