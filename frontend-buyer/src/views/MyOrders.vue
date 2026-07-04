<template>
  <div>
    <Navbar />
    <div class="max-w-5xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">My Orders</h1>

      <!-- Status Tabs -->
      <div class="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button v-for="s in statuses" :key="s.value"
          @click="statusFilter = s.value; loadOrders()"
          :class="statusFilter === s.value ? 'bg-primary text-white' : 'bg-white text-gray-600 hover:bg-gray-50'"
          class="px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap transition">
          {{ s.label }}
        </button>
      </div>

      <!-- Orders List -->
      <div v-if="orders.length === 0 && !loading" class="bg-white rounded-2xl shadow p-12 text-center">
        <div class="text-5xl mb-4">📦</div>
        <p class="text-gray-500">No orders yet</p>
        <router-link to="/browse" class="text-primary font-semibold hover:underline mt-2 inline-block">Start Shopping →</router-link>
      </div>

      <div v-else class="space-y-4">
        <div v-for="order in orders" :key="order.id"
          class="bg-white rounded-2xl shadow p-6 hover:shadow-lg transition">
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center gap-3">
                <span class="font-bold text-lg">#{{ order.order_number }}</span>
                <el-tag :type="statusType(order.status)" size="small">{{ statusLabel(order.status) }}</el-tag>
                <el-tag v-if="order.payment_status !== 'pending'" :type="order.payment_status === 'paid' ? 'success' : 'info'" size="small">
                  {{ paymentLabel(order.payment_status) }}
                </el-tag>
              </div>
              <p class="text-gray-500 text-sm mt-1">{{ formatDate(order.created_at) }} · {{ order.items?.length || 0 }} item(s)</p>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-primary">€{{ order.total_amount }}</p>
              <router-link :to="`/my-orders/${order.id}`" class="text-primary text-sm font-semibold hover:underline">
                View Details →
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="flex justify-center mt-6 gap-2">
        <button v-if="page > 1" @click="page--; loadOrders()" class="px-4 py-2 bg-white rounded-lg hover:bg-gray-50">← Prev</button>
        <span class="px-4 py-2 text-gray-500">Page {{ page }}</span>
        <button v-if="orders.length === pageSize" @click="page++; loadOrders()" class="px-4 py-2 bg-white rounded-lg hover:bg-gray-50">Next →</button>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { getMyOrders } from '../api'

const orders = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const statusFilter = ref('')

const statuses = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'paid', label: 'Paid' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const statusLabel = (s) => ({
  pending: 'Pending', paid: 'Paid', shipped: 'Shipped',
  completed: 'Completed', cancelled: 'Cancelled',
}[s] || s)

const statusType = (s) => ({
  pending: 'warning', paid: 'success', shipped: 'info',
  completed: '', cancelled: 'danger',
}[s] || '')

const paymentLabel = (s) => ({
  pending: 'Payment Pending', paid: 'Paid', failed: 'Payment Failed',
  requires_action: 'Action Required', refunded: 'Refunded',
}[s] || s)

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (statusFilter.value) params.status = statusFilter.value
    const res = await getMyOrders(params)
    orders.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error('Failed to load orders:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadOrders())
</script>
