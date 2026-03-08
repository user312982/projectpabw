<template>
  <div class="app">
    <!-- Bento Sidebar -->
    <aside class="sidebar-wrapper">
      <div class="sidebar">
        <!-- Brand Card -->
        <div class="bento-card brand-card">
          <h1>Biz</h1>
          <h1 class="brand-text">Ledger</h1>
          <p class="brand-subtitle">System</p>
        </div>

        <!-- Nav Card -->
        <nav class="bento-card nav-card">
          <a href="#" class="nav-item active">
            Dashboard
          </a>
        </nav>

        <!-- Footer Card -->
        <div class="bento-card footer-card">
          <span class="version-badge">MVP v1.0</span>
        </div>
      </div>
    </aside>

    <!-- Main Content Container (Rounded & Colored) -->
    <main class="main-wrapper">
      <div class="main-content bg-orange">
        
        <!-- Header -->
        <header class="main-header">
          <div class="header-text">
            <h2>Dashboard</h2>
            <p class="header-subtitle">Ringkasan keuangan bisnis Anda</p>
          </div>
          <div class="header-date">
            {{ todayDate }}
          </div>
        </header>

        <!-- Main Grid -->
        <div class="content-grid">
          <!-- Left: Dashboard Data -->
          <div class="content-left">
            <DashboardCards :data="dashboardData" />
            
            <div class="tables-section">
              <ProductList :products="products" />
              <InvoiceList :invoices="invoices" />
            </div>
          </div>

          <!-- Right: AI Chat -->
          <div class="content-right">
            <AiChat @data-changed="refreshAllData" />
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from './services/api.js'
import AiChat from './components/AiChat.vue'
import DashboardCards from './components/DashboardCards.vue'
import ProductList from './components/ProductList.vue'
import InvoiceList from './components/InvoiceList.vue'

const dashboardData = ref({
  total_products: 0,
  low_stock_count: 0,
  invoices_today: 0,
  total_sales_today: 0,
})
const products = ref([])
const invoices = ref([])

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

async function fetchProducts() {
  try {
    const res = await api.get('/api/products')
    products.value = res.data
  } catch (e) {
    console.error('Failed to fetch products:', e)
  }
}

async function fetchInvoices() {
  try {
    const res = await api.get('/api/invoices')
    invoices.value = res.data
  } catch (e) {
    console.error('Failed to fetch invoices:', e)
  }
}

async function refreshAllData() {
  await Promise.all([fetchDashboard(), fetchProducts(), fetchInvoices()])
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

/* ── Bento Sidebar ────────────────────────── */

.sidebar-wrapper {
  width: 140px;
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
  padding: 32px 16px;
  background: var(--color-black);
  color: var(--color-white);
}

.brand-card h1 {
  font-size: 32px;
  margin: 0;
  line-height: 0.9;
  letter-spacing: -3px;
}

.brand-text {
  color: var(--color-orange);
  margin-top: -4px !important;
}

.brand-subtitle {
  font-size: 10px;
  font-weight: var(--font-weight-medium);
  letter-spacing: 0em;
  text-transform: uppercase;
  margin-top: 16px;
  opacity: 0.8;
}

.nav-card {
  flex: 1;
  justify-content: flex-start;
  padding: 16px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-md);
  color: var(--color-black);
  text-decoration: none;
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  width: 100%;
  transition: background 0.2s, color 0.2s;
}

.nav-item:hover {
  background: var(--bg-color);
}

.nav-item.active {
  background: var(--color-purple);
  color: var(--color-white);
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

/* ── Main Content Container ───────────────────── */

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
  overflow: hidden; /* Prevent inner children from breaking the border rounding */
  /* Thermaterials vibrant background approach */
}

/* Dynamic background classes */
.bg-orange { background: var(--color-orange); color: var(--color-white); }
.bg-purple { background: var(--color-purple); color: var(--color-white); }
.bg-light  { background: var(--color-white); color: var(--color-black); }

.main-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 48px 64px 24px;
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
}

.tables-section {
  display: flex;
  flex-direction: column;
  gap: 40px;
  flex: 1; /* allow it to grow */
}

.content-right {
  width: 400px;
  padding: 0 40px 40px 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-orange); /* Match main background if it shrinks */
}

/* ── Responsive ─────────────────────── */

@media (max-width: 1200px) {
  .main-header, .content-left {
    padding-left: 40px;
    padding-right: 40px;
  }
}

@media (max-width: 1024px) {
  .sidebar-wrapper {
    display: none;
  }

  .content-grid {
    flex-direction: column;
  }

  .content-right {
    width: 100%;
    padding: 0 40px 40px;
    height: auto;
  }
}
</style>
