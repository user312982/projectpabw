<template>
  <div class="app">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="mobile-brand">
        <span class="brand-itk">ITK</span>
        <span class="brand-lf">LostFound</span>
      </div>
      <button class="hamburger" @click="mobileOpen = !mobileOpen" :class="{ open: mobileOpen }">
        <span></span><span></span><span></span>
      </button>
    </div>

    <!-- Sidebar -->
    <aside class="sidebar-wrapper" :class="{ 'mobile-open': mobileOpen }">
      <div class="sidebar">
        <!-- Brand Card -->
        <div class="bento-card brand-card">
          <h1>ITK</h1>
          <h1 class="brand-text">Lost</h1>
          <h1 class="brand-text">Found</h1>
        </div>

        <!-- Nav Card -->
        <nav class="bento-card nav-card">
          <a
            href="#"
            v-for="nav in navItems"
            :key="nav.id"
            class="nav-item"
            :class="{ active: currentPage === nav.id }"
            @click.prevent="currentPage = nav.id; mobileOpen = false"
          >
            <span class="nav-icon" v-html="nav.icon"></span>
            {{ nav.label }}
          </a>
        </nav>

        <!-- Footer Card -->
        <div class="bento-card footer-card">
          <button class="logout-link" @click="$emit('logout')">Logout</button>
          <span class="version-badge">v1.0 — Petugas</span>
        </div>
      </div>
    </aside>

    <!-- Mobile Overlay -->
    <div class="mobile-overlay" v-if="mobileOpen" @click="mobileOpen = false"></div>

    <!-- Main Content -->
    <main class="main-wrapper">
      <div class="main-content" :class="mainBgClass">
        
        <!-- Header -->
        <header class="main-header">
          <div class="header-text">
            <h2>{{ currentNav.title }}</h2>
            <p class="header-subtitle">{{ currentNav.subtitle }}</p>
          </div>
          <div class="header-actions">
            <button class="btn-claim" @click="showClaimModal = true">Klaim By Kode</button>
            <div class="header-date">
              {{ todayDate }}
            </div>
          </div>
        </header>

        <!-- Content Area -->
        <div class="content-grid">
          <!-- Left: Page Content -->
          <div class="content-left">

            <!-- Dashboard Page -->
            <template v-if="currentPage === 'dashboard'">
              <DashboardCards :data="dashboardData" />
              <ItemList :items="allItems" />
            </template>

            <!-- Lost Page -->
            <template v-if="currentPage === 'lost'">
              <ItemList :items="lostItems" :hideTypeFilter="true" />
            </template>

            <!-- Found Page -->
            <template v-if="currentPage === 'found'">
              <ItemList :items="foundItems" :hideTypeFilter="true" />
            </template>

            <!-- Report Page -->
            <template v-if="currentPage === 'report'">
              <ReportForm @submitted="refreshAllData" />
            </template>

          </div>

          <!-- Right: AI Chat -->
          <div class="content-right">
            <AiChat @data-changed="refreshAllData" />
          </div>
        </div>

      </div>
    </main>

    <!-- Modal Klaim -->
    <div class="modal-overlay" v-if="showClaimModal" @click="showClaimModal = false">
      <div class="modal-content bento-card" @click.stop>
        <h3>Input Kode Klaim</h3>
        <form @submit.prevent="submitClaim" class="claim-form">
           <input type="text" v-model="claimForm.unique_code" placeholder="Kode Unik (e.g. LF-ABC12)" required />
           <input type="text" v-model="claimForm.nama_pengklaim" placeholder="Nama Pengambil" required />
           <input type="text" v-model="claimForm.nim_pengklaim" placeholder="NIM / NIP Pengambil" required />
           <input type="text" v-model="claimForm.kontak_pengklaim" placeholder="Kontak (No HP / Email)" required />
           <button type="submit" class="btn-primary">Proses Klaim</button>
           <p class="success" v-if="claimSuccess">{{claimSuccess}}</p>
           <p class="error" v-if="claimError">{{claimError}}</p>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api.js'
import AiChat from './AiChat.vue'
import DashboardCards from './DashboardCards.vue'
import ItemList from './ItemList.vue'
import ReportForm from './ReportForm.vue'

const currentPage = ref('dashboard')
const mobileOpen = ref(false)

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>' },
  { id: 'lost', label: 'Hilang', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>' },
  { id: 'found', label: 'Ditemukan', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' },
  { id: 'report', label: 'Lapor', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>' },
]

const navConfig = {
  dashboard: { title: 'Dashboard', subtitle: 'Ringkasan laporan barang hilang & ditemukan', bg: 'bg-primary' },
  lost: { title: 'Barang Hilang', subtitle: 'Daftar laporan barang yang hilang', bg: 'bg-lost' },
  found: { title: 'Ditemukan', subtitle: 'Daftar laporan barang yang ditemukan', bg: 'bg-found' },
  report: { title: 'Lapor', subtitle: 'Buat laporan barang hilang atau ditemukan', bg: 'bg-accent' },
}

const currentNav = computed(() => navConfig[currentPage.value])
const mainBgClass = computed(() => currentNav.value.bg)

const dashboardData = ref({
  total_lost: 0,
  total_found: 0,
  total_open: 0,
  total_claimed: 0,
  total_closed: 0,
})

const allItems = ref([])
const lostItems = computed(() => allItems.value.filter(i => i.type === 'lost'))
const foundItems = computed(() => allItems.value.filter(i => i.type === 'found'))

const emit = defineEmits(['logout'])

const showClaimModal = ref(false)
const claimForm = ref({ unique_code: '', nama_pengklaim: '', nim_pengklaim: '', kontak_pengklaim: '' })
const claimError = ref('')
const claimSuccess = ref('')

async function submitClaim() {
  claimError.value = ''
  claimSuccess.value = ''
  try {
    await api.post('/api/items/claim-by-code', claimForm.value)
    claimSuccess.value = 'Barang berhasil diklaim!'
    setTimeout(() => { 
      showClaimModal.value = false;
      claimForm.value = { unique_code: '', nama_pengklaim: '', nim_pengklaim: '', kontak_pengklaim: '' }
    }, 2000)
    refreshAllData()
  } catch (err) {
    claimError.value = err.response?.data?.detail || 'Gagal klaim'
  }
}

const todayDate = new Date().toLocaleDateString('id-ID', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
})

async function fetchDashboard() {
  try {
    const res = await api.get('/api/dashboard/summary')
    dashboardData.value = res.data
  } catch (e) {
    console.error('Failed to fetch dashboard:', e)
  }
}

async function fetchItems() {
  try {
    const res = await api.get('/api/items')
    allItems.value = res.data
  } catch (e) {
    console.error('Failed to fetch items:', e)
  }
}

async function refreshAllData() {
  await Promise.all([fetchDashboard(), fetchItems()])
}

onMounted(() => {
  refreshAllData()
})
</script>

<style scoped>
.app {
  display: flex;
  min-height: 100vh;
  background: var(--bg-color);
  padding: 16px;
  gap: 16px;
}

/* ── Mobile Header ────────────────── */

.mobile-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 12px 20px;
  background: rgba(14,14,14,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  align-items: center;
  justify-content: space-between;
}

.mobile-brand {
  display: flex;
  gap: 6px;
  align-items: baseline;
}

.brand-itk {
  font-size: 20px;
  font-weight: 900;
  color: var(--color-white);
  letter-spacing: -0.04em;
}

.brand-lf {
  font-size: 20px;
  font-weight: 900;
  color: var(--color-primary);
  letter-spacing: -0.04em;
}

.hamburger {
  width: 36px;
  height: 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--color-white);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger.open span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}
.hamburger.open span:nth-child(2) {
  opacity: 0;
}
.hamburger.open span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* ── Sidebar ────────────────────────── */

.sidebar-wrapper {
  width: 150px;
  flex-shrink: 0;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.bento-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.brand-card {
  padding: 28px 16px;
  background: var(--gradient-dark);
  color: var(--color-white);
  position: relative;
  overflow: hidden;
}

.brand-card::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba(16,185,129,0.15) 0%, transparent 60%);
  pointer-events: none;
}

.brand-card h1 {
  font-size: 28px;
  margin: 0;
  line-height: 0.9;
  letter-spacing: -3px;
  position: relative;
  z-index: 1;
}

.brand-text {
  color: var(--color-primary);
  margin-top: -2px !important;
}

.nav-card {
  flex: 1;
  justify-content: flex-start;
  padding: 16px;
  gap: 4px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 12px;
  border-radius: var(--radius-md);
  color: var(--color-black);
  text-decoration: none;
  font-size: 11px;
  font-weight: var(--font-weight-bold);
  width: 100%;
  transition: all 0.25s ease;
  text-align: center;
  position: relative;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.25s, transform 0.25s;
}

.nav-item:hover {
  background: var(--bg-color);
}

.nav-item:hover .nav-icon {
  opacity: 1;
  transform: scale(1.1);
}

.nav-item.active {
  background: var(--gradient-dark);
  color: var(--color-white);
  box-shadow: 0 4px 16px rgba(14,14,14,0.2);
}

.nav-item.active .nav-icon {
  opacity: 1;
}

.footer-card {
  padding: 16px;
  background: transparent;
  border: 1px solid var(--color-gray);
}

.version-badge {
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  color: var(--color-dark-gray);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Main Content ───────────────────── */

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 32px);
  border-radius: var(--radius-xl);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: background 0.5s ease;
}

.bg-primary { background: var(--gradient-primary); color: var(--color-white); }
.bg-lost { background: var(--gradient-lost); color: var(--color-white); }
.bg-found { background: var(--gradient-found); color: var(--color-white); }
.bg-accent { background: var(--gradient-accent); color: var(--color-white); }

.main-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 48px 64px 24px;
  animation: slideUp 0.5s ease;
}

.header-text h2 {
  font-size: clamp(3rem, 6vw, 5rem);
  margin: 0;
  line-height: 0.9;
  letter-spacing: -0.04em;
  text-transform: uppercase;
}

.header-subtitle {
  font-size: 16px;
  font-weight: var(--font-weight-medium);
  margin-top: 16px;
  opacity: 0.9;
}

.header-date {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  padding: 8px 16px;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-pill);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  background: rgba(255,255,255,0.1);
}

.content-grid {
  display: flex;
  flex: 1;
  min-height: 500px;
}

.content-left {
  flex: 1;
  padding: 24px 64px 64px;
  display: flex;
  flex-direction: column;
  gap: 40px;
  overflow-y: auto;
  animation: fadeIn 0.4s ease;
}

.content-right {
  width: 400px;
  padding: 0 40px 40px 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* ── Mobile Overlay ────────────────── */

.mobile-overlay {
  display: none;
}

/* ── Responsive ─────────────────────── */

@media (max-width: 1200px) {
  .main-header, .content-left {
    padding-left: 40px;
    padding-right: 40px;
  }
}

@media (max-width: 1024px) {
  .mobile-header {
    display: flex;
  }

  .app {
    flex-direction: column;
    padding: 0;
    padding-top: 60px;
  }

  .sidebar-wrapper {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    width: 180px;
    z-index: 99;
    background: var(--bg-color);
    padding: 16px;
    transform: translateX(-100%);
    transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  }

  .sidebar-wrapper.mobile-open {
    transform: translateX(0);
  }

  .mobile-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 98;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
  }

  .main-wrapper {
    min-height: auto;
    border-radius: 0;
  }

  .main-content {
    border-radius: 0;
  }

  .content-grid {
    flex-direction: column;
  }

  .content-right {
    width: 100%;
    padding: 0 20px 40px;
    height: auto;
  }

  .main-header {
    padding: 32px 20px 20px;
  }

  .content-left {
    padding: 20px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-claim {
  padding: 10px 16px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255,255,255,0.4);
  background: var(--color-primary);
  color: white;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(16,185,129,0.3);
  transition: transform 0.2s;
}

.btn-claim:hover {
  transform: scale(1.05);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--color-white);
  padding: 32px;
  border-radius: 20px;
  max-width: 400px;
  width: 100%;
}
.modal-content h3 { margin-top: 0; }

.claim-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.claim-form input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--color-gray);
}

.claim-form .btn-primary {
  padding: 12px;
  border-radius: 8px;
  border: none;
  background: var(--color-primary);
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.logout-link {
  background: none;
  border: none;
  color: #ef4444;
  font-weight: bold;
  cursor: pointer;
  padding: 8px;
  margin-bottom: 8px;
  text-decoration: underline;
}

.error { color: red; text-align: center; }
.success { color: green; text-align: center; }
</style>
