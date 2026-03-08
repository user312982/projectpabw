<template>
  <div class="dashboard-cards">
    <div class="card bg-purple">
      <div class="card-title">
        Total Produk
      </div>
      <div class="card-value">{{ data.total_products }}</div>
    </div>

    <div class="card bg-black">
      <div class="card-title">
        Stok Menipis
      </div>
      <div class="card-value" :class="{ 'text-orange': data.low_stock_count > 0 }">
        {{ data.low_stock_count }}
      </div>
    </div>

    <div class="card bg-gray">
      <div class="card-title text-black">
        Faktur Hari Ini
      </div>
      <div class="card-value text-black">{{ data.invoices_today }}</div>
    </div>

    <div class="card bg-orange">
      <div class="card-title">
        Penjualan Hari Ini
      </div>
      <div class="card-value currency">{{ formatCurrency(data.total_sales_today) }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      total_products: 0,
      low_stock_count: 0,
      invoices_today: 0,
      total_sales_today: 0,
    }),
  },
})

function formatCurrency(value) {
  if (!value) return '0'
  
  // Custom format for large display: "Rp 5.000K" or similar if needed, 
  // but let's stick to standard tight format for now.
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value).replace(/\s/g, '')
}
</script>

<style scoped>
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 32px 32px 24px;
  border-radius: var(--radius-lg);
  min-height: 180px;
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
}

.bg-purple { background: var(--color-purple); color: var(--color-white); }
.bg-black { background: var(--color-black); color: var(--color-white); }
.bg-gray { background: var(--color-gray); color: var(--color-black); }
.bg-orange { background: var(--color-orange); color: var(--color-white); }

.text-black { color: var(--color-black) !important; }
.text-orange { color: var(--color-orange) !important; }

.card-title {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.9;
}

.card-value {
  font-size: clamp(4rem, 6vw, 6rem);
  font-weight: var(--font-weight-heavy);
  line-height: 0.85;
  letter-spacing: -0.05em;
  margin-top: 24px;
}

.card-value.currency {
  font-size: clamp(2.5rem, 4vw, 4rem);
  letter-spacing: -0.03em;
}

@media (max-width: 1400px) {
  .card-value {
    font-size: 4rem;
  }
  .card-value.currency {
    font-size: 3rem;
  }
}

@media (max-width: 600px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
}
</style>
