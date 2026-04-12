<template>
  <div class="user-view" :class="{ 'has-searched': hasSearched }">
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
        <h1>ITK <span class="brand-text">LostFound</span></h1>
        <p>Asisten AI Pencarian Barang Hilang & Ditemukan</p>
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
        <ItemList :items="allItems" />
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
        </ul>
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

const emit = defineEmits(['logout'])

const showGuide = ref(false)
const hasSearched = ref(false)
const initialQuery = ref('')
const allItems = ref([])
const chatComponent = ref(null)

async function fetchItems() {
  try {
    const res = await api.get('/api/items')
    allItems.value = res.data
  } catch (e) {
    console.error('Failed to fetch items', e)
  }
}

async function handleDataChanged(toolsUsed) {
  if (toolsUsed && toolsUsed.length > 0) {
    const searchTool = toolsUsed.find(t => t.name === 'search_items' || t.name === 'match_items');
    if (searchTool) {
      const args = searchTool.args || {};
      const params = {};
      if (args.keyword) params.search = args.keyword;
      if (args.category) params.category = args.category;
      if (args.type) params.type = args.type;
      
      try {
        const res = await api.get('/api/items', { params })
        allItems.value = res.data
      } catch (e) {
        console.error(e)
      }
      return;
    }
  }
  
  // Default: fetch all
  fetchItems();
}

function handleInitialSearch() {
  if (!initialQuery.value.trim()) return
  hasSearched.value = true
  fetchItems() // Fetch all default
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
  background: var(--bg-color); /* inherits gradient or dark bg */
  color: var(--color-white);
  display: flex;
  flex-direction: column;
}

.user-view.has-searched {
  padding: 20px;
}

.guide-btn {
  position: absolute;
  top: 20px;
  right: 140px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  color: white;
  cursor: pointer;
  transition: 0.3s;
  z-index: 10;
  backdrop-filter: blur(5px);
}
.guide-btn:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.4); }

.logout-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.2);
  background: transparent;
  color: white;
  cursor: pointer;
  transition: 0.3s;
  z-index: 10;
  backdrop-filter: blur(5px);
}
.logout-btn:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.4); }

/* Search Engine View */
.search-engine-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  animation: fadeIn 0.8s ease;
}
.brand {
  text-align: center;
  margin-bottom: 40px;
}
.brand h1 {
  font-size: 72px;
  margin: 0;
  letter-spacing: -3px;
  text-shadow: 0 4px 20px rgba(16,185,129,0.3);
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
  color: rgba(255,255,255,0.6);
}
.search-input {
  width: 100%;
  padding: 24px 24px 24px 64px;
  font-size: 18px;
  border-radius: 40px;
  border: 1.5px solid rgba(255,255,255,0.2);
  background: rgba(14,14,14,0.6);
  color: white;
  outline: none;
  font-family: inherit;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.search-input:focus { border-color: var(--color-primary); background: rgba(14,14,14,0.8); box-shadow: 0 10px 40px rgba(16,185,129,0.15);}
.search-input::placeholder { color: rgba(255,255,255,0.4); }

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
.btn-primary { background: var(--gradient-primary); color: white; box-shadow: 0 4px 15px rgba(16,185,129,0.4);}
.btn-primary:active { transform: scale(0.95); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none;}
.btn-outline { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); color: white; backdrop-filter: blur(5px);}
.btn-outline:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.5);}

/* Active Chat View */
.active-chat-view {
  display: flex;
  gap: 20px;
  padding-top: 60px; /* Space for buttons */
  flex: 1;
  min-height: 0;
}
.content-left {
  flex: 1;
  background: rgba(14,14,14,0.5);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  padding: 24px 32px;
  overflow-y: auto;
  border: 1px solid rgba(255,255,255,0.08);
  animation: slideIn 0.5s ease;
}
.content-header {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.content-header h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  letter-spacing: -1px;
}
.content-header p {
  margin: 0;
  opacity: 0.7;
}

.content-right {
  width: 420px;
  flex-shrink: 0;
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
  background: var(--color-white);
  color: var(--color-black);
  padding: 40px;
  border-radius: 24px;
  max-width: 500px;
  width: 100%;
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.modal-content h2 { margin-top: 0; font-size: 24px; letter-spacing: -0.5px; margin-bottom: 16px;}
.modal-content p { opacity: 0.8; line-height: 1.5; }
.guide-list { margin: 24px 0; padding-left: 20px; line-height: 1.8; opacity: 0.9;}
.guide-list li { margin-bottom: 8px; }
.btn-black { background: var(--color-black); color: white; width: 100%; border-radius: 12px; padding: 14px;}
.btn-black:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.15);}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

@media (max-width: 1024px) {
  .active-chat-view { flex-direction: column; }
  .content-right { width: 100%; height: 500px; }
  .guide-btn { top: 10px; right: 100px; padding: 8px 12px;}
  .logout-btn { top: 10px; right: 10px; padding: 8px 12px;}
  .brand h1 { font-size: 48px; }
  .search-input { padding: 18px 20px 18px 50px; font-size: 16px; }
}
</style>
