<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <div class="bg-white safe-top border-b border-gray-100">
      <div class="flex items-center px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1 text-center mr-8">My Orders</h1>
      </div>
    </div>

    <div v-if="orders.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
      <span class="text-5xl mb-4">📦</span>
      <p>No orders yet</p>
      <router-link to="/browse" class="mt-4 text-primary font-semibold tap-active">Start Shopping →</router-link>
    </div>

    <div v-else class="px-4 py-4 space-y-3">
      <router-link
        v-for="order in orders"
        :key="order.id"
        :to="`/my-orders/${order.id}`"
        class="block bg-white rounded-xl p-4 tap-active"
      >
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-bold">Order #{{ order.id }}</span>
          <span :class="statusBadgeClass(order.status)" class="text-xs px-2 py-0.5 rounded-full">
            {{ statusLabel(order.status) }}
          </span>
        </div>
        <div class="flex gap-2 overflow-x-auto hide-scrollbar">
          <div
            v-for="item in order.items?.slice(0, 3)"
            :key="item.id"
            class="w-16 h-16 bg-[#EBEBF0] rounded-lg overflow-hidden shrink-0"
          >
            <img v-if="item.product?.images?.length" :src="item.product.images[0].thumbnail_url" class="w-full h-full object-cover" />
          </div>
        </div>
        <div class="flex justify-between mt-2 text-sm">
          <span class="text-gray-500">{{ order.items?.length || 0 }} item(s)</span>
          <span class="font-bold text-primary">€{{ order.total_amount }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyOrders } from '../api'

const orders = ref([])

const statusLabel = (s) => ({
  pending: 'Pending',
  paid: 'Paid',
  shipped: 'Shipped',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}[s] || s)

const statusBadgeClass = (s) => ({
  pending: 'bg-yellow-100 text-yellow-700',
  paid: 'bg-blue-100 text-blue-700',
  shipped: 'bg-purple-100 text-purple-700',
  delivered: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}[s] || 'bg-gray-100 text-gray-700')

onMounted(async () => {
  try {
    const { data } = await getMyOrders()
    orders.value = data.items || []
  } catch (e) {
    console.error(e)
  }
})
</script>
