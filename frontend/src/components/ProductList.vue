<template>
  <div class="data-table-wrapper">
    <div class="table-header">
      <h3>Daftar Produk</h3>
      <span class="table-count">{{ products.length }} items</span>
    </div>

    <div class="table-container">
      <table v-if="products.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Min</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td class="td-name">{{ p.name }}</td>
            <td class="td-price">{{ formatCurrency(p.sell_price) }}</td>
            <td class="td-center">{{ p.stock_qty }}</td>
            <td class="td-center">{{ p.min_stock }}</td>
            <td class="td-center">
              <span class="status-indicator" :class="p.stock_qty <= p.min_stock ? 'bg-orange' : 'bg-black'"></span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="table-empty">
        <h2 class="empty-title">NO<br>DATA</h2>
        <p>Gunakan AI Chat untuk menambahkan produk baru.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  products: {
    type: Array,
    default: () => [],
  },
})

function formatCurrency(value) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value || 0)
}
</script>

<style scoped>
.data-table-wrapper {
  background: transparent;
}

.table-header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 24px;
}

.table-header h3 {
  margin: 0;
  font-size: 32px;
  font-weight: var(--font-weight-heavy);
  text-transform: uppercase;
  letter-spacing: -0.02em;
  line-height: 1;
}

.table-count {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  padding: 16px 8px 8px 0;
  text-align: left;
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: inherit;
  opacity: 0.7;
  border-bottom: 2px solid currentColor;
}

td {
  padding: 24px 8px 24px 0;
  font-size: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  color: inherit;
}

.bg-light td {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

tr:hover td {
  opacity: 0.8;
}

.td-center {
  text-align: left; /* Changed from center for a cleaner typographical line */
}

.td-name {
  font-weight: var(--font-weight-heavy);
  font-size: 20px;
  letter-spacing: -0.01em;
}

.td-price {
  font-family: inherit;
  font-weight: var(--font-weight-bold);
}

.status-indicator {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--color-white);
}

.bg-orange { background: var(--color-orange); }
.bg-black { background: var(--color-black); }

.table-empty {
  padding: 64px 0;
  text-align: left;
}

.empty-title {
  font-size: 80px;
  line-height: 0.85;
  letter-spacing: -0.05em;
  margin: 0 0 16px 0;
  opacity: 0.3;
}

.table-empty p {
  font-size: 16px;
  font-weight: var(--font-weight-medium);
  opacity: 0.8;
}
</style>
