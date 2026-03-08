<template>
  <div class="data-table-wrapper">
    <div class="table-header">
      <h3>Daftar Faktur</h3>
      <span class="table-count">{{ invoices.length }} items</span>
    </div>

    <div class="table-container">
      <table v-if="invoices.length > 0">
        <thead>
          <tr>
            <th>Invoice No</th>
            <th>Customer</th>
            <th>Items</th>
            <th>Total</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.id">
            <td class="td-invoice-no">{{ inv.invoice_no }}</td>
            <td class="td-name">{{ inv.customer_name }}</td>
            <td class="td-center">{{ inv.items?.length || 0 }}</td>
            <td class="td-price">{{ formatCurrency(inv.total) }}</td>
            <td class="td-date">{{ formatDate(inv.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="table-empty">
        <h2 class="empty-title">NO<br>INVOICES</h2>
        <p>Gunakan AI Chat untuk membuat faktur baru.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  invoices: {
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

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).toUpperCase()
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
  text-align: left;
}

.td-name {
  font-weight: var(--font-weight-heavy);
  font-size: 20px;
  letter-spacing: -0.01em;
}

.td-invoice-no {
  font-weight: var(--font-weight-bold);
  font-size: 14px;
  letter-spacing: 0.02em;
}

.td-price {
  font-weight: var(--font-weight-bold);
}

.td-date {
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  opacity: 0.8;
}

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
