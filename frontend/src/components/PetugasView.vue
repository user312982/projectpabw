<template>
  <div class="app">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="mobile-brand">
        <img class="mobile-brand-logo" src="../assets/itk/logo-itk-white-notext.webp" alt="Logo Institut Teknologi Kalimantan" />
        <span class="brand-itk">ITK</span>
        <span class="brand-lf">Lost & Found</span>
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
          <img class="sidebar-itk-logo" src="../assets/itk/logo-itk-white-notext.webp" alt="Logo Institut Teknologi Kalimantan" />
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
          <span class="version-badge">v1.0 — Staff</span>
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
            <div class="header-date">
              {{ todayDate }}
            </div>
          </div>
        </header>

        <!-- Content Area -->
        <div class="content-full">
          <!-- Dashboard Page -->
          <template v-if="currentPage === 'dashboard'">
            <DashboardCards :data="dashboardData" />
            <ItemList :items="allItems" :user="user" @code-copied="code => $emit('code-copied', code)" @updated="refreshAllData" />
          </template>

          <!-- Items Page with Tabs -->
          <template v-if="currentPage === 'items'">
            <div class="items-tabs">
              <button
                v-for="tab in itemTabs"
                :key="tab.value"
                class="tab-btn"
                :class="{ active: itemTab === tab.value }"
                @click="itemTab = tab.value"
              >
                {{ tab.label }}
              </button>
            </div>
            <ItemList :items="filteredItems" :user="user" @code-copied="code => $emit('code-copied', code)" @updated="refreshAllData" />
          </template>

          <!-- Claim Item Page -->
          <template v-if="currentPage === 'claim'">
            <ClaimItemView @claimed="refreshAllData" />
          </template>

          <!-- Claim History Page -->
          <template v-if="currentPage === 'history'">
            <ClaimHistory ref="claimHistoryRef" />
          </template>

          <!-- Report Page -->
          <template v-if="currentPage === 'report'">
            <ReportForm @submitted="refreshAllData" />
          </template>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api.js'
import DashboardCards from './DashboardCards.vue'
import ItemList from './ItemList.vue'
import ReportForm from './ReportForm.vue'
import ClaimItemView from './ClaimItemView.vue'
import ClaimHistory from './ClaimHistory.vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
})

const currentPage = ref('dashboard')
const mobileOpen = ref(false)
const claimHistoryRef = ref(null)

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>' },
  { id: 'items', label: 'Items', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/></svg>' },
  { id: 'claim', label: 'Claim Item', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
  { id: 'history', label: 'History', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
  { id: 'report', label: 'Report', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>' },
]

const navConfig = {
  dashboard: { title: 'Dashboard', subtitle: 'Overview of lost & found reports', bg: 'bg-primary' },
  items: { title: 'All Items', subtitle: 'Lost & Found items by category', bg: 'bg-primary' },
  claim: { title: 'Claim Item', subtitle: 'Process item pickup confirmation', bg: 'bg-accent' },
  history: { title: 'Claim History', subtitle: 'Record of all processed claims', bg: 'bg-primary' },
  report: { title: 'Report', subtitle: 'Create a lost or found item report', bg: 'bg-accent' },
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
const claimedItems = computed(() => allItems.value.filter(i => i.status === 'claimed' || i.status === 'closed' || i.status === 'returned'))

const itemTab = ref('all')
const itemTabs = [
  { value: 'all', label: 'All' },
  { value: 'lost', label: 'Lost' },
  { value: 'found', label: 'Found' },
  { value: 'claimed', label: 'Claimed' },
]
const filteredItems = computed(() => {
  if (itemTab.value === 'all') return allItems.value
  if (itemTab.value === 'lost') return lostItems.value
  if (itemTab.value === 'found') return foundItems.value
  if (itemTab.value === 'claimed') return claimedItems.value
  return allItems.value
})

const emit = defineEmits(['logout'])

const todayDate = new Date().toLocaleDateString('en-US', {
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
  if (claimHistoryRef.value) {
    claimHistoryRef.value.refresh()
  }
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
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  align-items: center;
  justify-content: space-between;
}

.mobile-brand {
  display: flex;
  gap: 6px;
  align-items: center;
}

.mobile-brand-logo {
  width: 24px;
  height: 28px;
  object-fit: contain;
  padding: 3px;
  border-radius: 8px;
  background: var(--color-primary);
}

.brand-itk {
  font-size: 20px;
  font-weight: 900;
  color: var(--color-primary);
  letter-spacing: 0;
}

.brand-lf {
  font-size: 20px;
  font-weight: 900;
  color: var(--color-text-muted);
  letter-spacing: 0;
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
  background: var(--color-primary);
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
  width: 160px;
  flex-shrink: 0;
  height: calc(100vh - 32px);
  position: sticky;
  top: 16px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.bento-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 20px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 2px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.brand-card {
  padding: 22px 16px 24px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  position: relative;
  overflow: hidden;
  border-color: var(--color-primary);
  border-bottom: 4px solid var(--color-accent);
}

.brand-card::after {
  display: none;
}

.brand-card h1 {
  font-size: 24px;
  margin: 0;
  line-height: 0.9;
  letter-spacing: 0;
  position: relative;
  z-index: 1;
}

.sidebar-itk-logo {
  width: 58px;
  height: 68px;
  object-fit: contain;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.brand-text {
  color: var(--color-accent);
  margin-top: -2px !important;
}

.nav-card {
  flex: 1;
  justify-content: flex-start;
  padding: 12px;
  gap: 2px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 8px;
  border-radius: var(--radius-md);
  color: var(--color-text-main);
  text-decoration: none;
  font-size: 10px;
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
  background: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 4px 16px rgba(11, 97, 170, 0.22);
}

.nav-item.active .nav-icon {
  opacity: 1;
}

.footer-card {
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.version-badge {
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-muted);
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
  box-shadow: var(--shadow-md);
}

.bg-primary { 
  background: var(--bg-color); 
  color: var(--color-text-main); 
}
.bg-lost { 
  background: var(--color-primary-subtle); 
  color: var(--color-text-main);
  border: 1px solid rgba(11, 97, 170, 0.14);
}
.bg-found { 
  background: #D1E7DD; 
  color: var(--color-text-main);
  border: 1px solid rgba(22, 163, 74, 0.16);
}
.bg-claimed { 
  background: var(--color-accent-subtle); 
  color: var(--color-text-main);
  border: 1px solid rgba(245, 183, 90, 0.24);
}
.bg-accent { 
  background: var(--color-surface); 
  color: var(--color-primary); 
}

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
  letter-spacing: 0;
  text-transform: uppercase;
  color: var(--color-primary);
  width: fit-content;
  padding-bottom: 14px;
  position: relative;
}

.header-text h2::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 5px;
  background: var(--color-accent);
  border-radius: var(--radius-pill);
}

.header-subtitle {
  font-size: 16px;
  font-weight: var(--font-weight-medium);
  margin-top: 16px;
  opacity: 0.95;
  color: var(--color-text-muted);
}

.header-date {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  padding: 8px 16px;
  border: 1px solid rgba(11, 97, 170, 0.18);
  border-radius: var(--radius-pill);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  background: rgba(11, 97, 170, 0.06);
  color: var(--color-primary);
}

.content-full {
  flex: 1;
  padding: 24px 64px 64px;
  display: flex;
  flex-direction: column;
  gap: 40px;
  overflow-y: auto;
  animation: fadeIn 0.4s ease;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  border-top-left-radius: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.8);
  border-left: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: -8px -8px 24px rgba(0,0,0,0.02);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-link {
  background: none;
  border: none;
  color: var(--color-danger);
  font-weight: bold;
  cursor: pointer;
  padding: 8px;
  margin-bottom: 8px;
  text-decoration: underline;
}

/* ── Items Tabs ─────────────────────── */

.items-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  width: fit-content;
  border: 2px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-btn:hover {
  color: var(--color-text-main);
  background: var(--color-surface-soft);
}

.tab-btn.active {
  background: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 4px 12px rgba(11, 97, 170, 0.25);
}

/* ── Mobile Overlay ────────────────── */

.mobile-overlay {
  display: none;
}

/* ── Responsive ─────────────────────── */

@media (max-width: 1200px) {
  .main-header, .content-full {
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

  .main-header {
    padding: 32px 20px 20px;
  }

  .content-full {
    padding: 20px;
  }
}
</style>
