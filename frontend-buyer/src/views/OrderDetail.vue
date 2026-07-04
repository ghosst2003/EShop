<template>
  <div>
    <Navbar />
    <div class="max-w-4xl mx-auto px-4 py-8" v-if="order">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Order #{{ order.order_number }}</h1>
          <p class="text-gray-500 text-sm mt-1">{{ formatDate(order.created_at) }}</p>
        </div>
        <div class="text-right">
          <span class="text-2xl font-bold text-primary">€{{ order.total_amount }}</span>
        </div>
      </div>

      <!-- Status Badges -->
      <div class="flex gap-3 mb-6">
        <span :class="statusBadge(order.status)" class="px-4 py-2 rounded-full font-semibold text-sm">
          {{ statusLabel(order.status) }}
        </span>
        <span :class="paymentBadge(order.payment_status)" class="px-4 py-2 rounded-full font-semibold text-sm">
          {{ paymentLabel(order.payment_status) }}
        </span>
      </div>

      <!-- Order Timeline -->
      <div class="bg-white rounded-2xl shadow p-6 mb-6">
        <h2 class="font-bold text-lg mb-4">Order Progress</h2>
        <div class="flex items-center gap-0">
          <div v-for="(s, i) in timeline" :key="s.status" class="flex-1 text-center">
            <div class="w-10 h-10 rounded-full mx-auto flex items-center justify-center text-sm font-bold"
              :class="s.active ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'">
              {{ s.active ? '✓' : (i + 1) }}
            </div>
            <div class="text-xs mt-2 font-semibold" :class="s.active ? 'text-primary' : 'text-gray-400'">{{ s.label }}</div>
            <div class="text-xs text-gray-400" v-if="s.date">{{ s.date }}</div>
          </div>
        </div>
      </div>

      <!-- Order Items -->
      <div class="bg-white rounded-2xl shadow p-6 mb-6">
        <h2 class="font-bold text-lg mb-4">Items</h2>
        <div class="divide-y">
          <div v-for="item in order.items" :key="item.id" class="flex justify-between py-4">
            <div>
              <p class="font-semibold">{{ item.product_title }}</p>
              <p class="text-gray-500 text-sm">Qty: {{ item.quantity }}</p>
            </div>
            <p class="font-bold">€{{ item.subtotal }}</p>
          </div>
        </div>
      </div>

      <!-- Shipping Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-bold text-lg mb-3">Shipping Address</h2>
          <p class="text-gray-600 whitespace-pre-line">{{ order.buyer_address }}</p>
          <p class="text-gray-500 text-sm mt-2">{{ order.buyer_name }} · {{ order.buyer_phone || '-' }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-bold text-lg mb-3">Payment</h2>
          <p class="text-gray-600">Method: {{ order.payment_method || 'Not set' }}</p>
          <p v-if="order.tracking_number" class="text-gray-600 mt-2">Tracking: <span class="font-mono font-bold">{{ order.tracking_number }}</span></p>
          <p v-if="order.notes" class="text-gray-600 mt-2">Notes: {{ order.notes }}</p>
        </div>
      </div>

      <!-- Status Logs -->
      <div v-if="order.status_logs?.length" class="bg-white rounded-2xl shadow p-6 mt-6">
        <h2 class="font-bold text-lg mb-4">Status History</h2>
        <div class="space-y-2">
          <div v-for="log in order.status_logs" :key="log.id" class="flex items-center gap-3 text-sm">
            <span class="text-gray-400">{{ formatDate(log.created_at) }}</span>
            <span class="text-gray-500">{{ log.from_status || 'Created' }}</span>
            <span>→</span>
            <span class="font-semibold">{{ statusLabel(log.to_status) }}</span>
            <span v-if="log.note" class="text-gray-400">({{ log.note }})</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="loading" class="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>
    <div v-else class="min-h-screen flex items-center justify-center text-gray-400">Order not found.</div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { getMyOrder } from '../api'

const route = useRoute()
const order = ref(null)
const loading = ref(true)

const statusLabel = (s) => ({
  pending: 'Pending', paid: 'Paid', shipped: 'Shipped',
  completed: 'Completed', cancelled: 'Cancelled',
}[s] || s)

const statusBadge = (s) => ({
  pending: 'bg-orange-100 text-orange-700', paid: 'bg-green-100 text-green-700',
  shipped: 'bg-blue-100 text-blue-700', completed: 'bg-gray-100 text-gray-700',
  cancelled: 'bg-red-100 text-red-700',
}[s] || 'bg-gray-100 text-gray-700')

const paymentLabel = (s) => ({
  pending: 'Payment Pending', paid: 'Paid', failed: 'Payment Failed',
  requires_action: 'Action Required', refunded: 'Refunded',
}[s] || s)

const paymentBadge = (s) => ({
  pending: 'bg-gray-100 text-gray-600', paid: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700', requires_action: 'bg-yellow-100 text-yellow-700',
  refunded: 'bg-purple-100 text-purple-700',
}[s] || 'bg-gray-100 text-gray-600')

const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const timeline = ref([])

onMounted(async () => {
  try {
    const res = await getMyOrder(route.params.id)
    order.value = res.data

    const o = order.value
    timeline.value = [
      { status: 'created', label: 'Created', active: true, date: formatDate(o.created_at) },
      { status: 'paid', label: 'Paid', active: !!o.paid_at, date: formatDate(o.paid_at) },
      { status: 'shipped', label: 'Shipped', active: !!o.shipped_at, date: formatDate(o.shipped_at) },
      { status: 'completed', label: 'Completed', active: !!o.completed_at, date: formatDate(o.completed_at) },
    ]
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
