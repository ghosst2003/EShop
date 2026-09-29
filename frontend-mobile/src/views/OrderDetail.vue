<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <div class="bg-white safe-top border-b border-gray-100">
      <div class="flex items-center px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1 text-center mr-8">Order Details</h1>
      </div>
    </div>

    <div v-if="order" class="px-4 py-4 space-y-4">
      <!-- Status -->
      <div class="bg-white rounded-xl p-4 text-center">
        <span :class="statusBadgeClass(order.status)" class="text-sm px-3 py-1 rounded-full font-medium">
          {{ statusLabel(order.status) }}
        </span>
        <p class="text-xs text-gray-500 mt-2">Order #{{ order.id }} · {{ order.created_at }}</p>
      </div>

      <!-- Items -->
      <div class="bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold mb-3">Items</h3>
        <div v-for="item in order.items" :key="item.id" class="flex gap-3 py-2 border-b border-gray-100 last:border-0">
          <div class="w-16 h-16 bg-[#EBEBF0] rounded-lg overflow-hidden shrink-0">
            <img v-if="item.product?.images?.length" :src="item.product.images[0].thumbnail_url" class="w-full h-full object-cover" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ item.product?.title_en }}</p>
            <p class="text-xs text-gray-500">Qty: {{ item.quantity }}</p>
          </div>
          <span class="text-sm font-bold">€{{ (item.product?.sale_price * item.quantity).toFixed(2) }}</span>
        </div>
      </div>

      <!-- Shipping -->
      <div class="bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold mb-2">Shipping</h3>
        <p class="text-sm text-gray-600">{{ order.shipping_address?.street }}</p>
        <p class="text-sm text-gray-600">{{ order.shipping_address?.city }}, {{ order.shipping_address?.postal_code }}</p>
      </div>

      <!-- Total -->
      <div class="bg-white rounded-xl p-4">
        <div class="flex justify-between text-sm">
          <span>Subtotal</span>
          <span>€{{ order.subtotal }}</span>
        </div>
        <div class="flex justify-between text-sm mt-1">
          <span>Shipping</span>
          <span>€{{ order.shipping_cost || '0.00' }}</span>
        </div>
        <div class="flex justify-between font-bold mt-2 pt-2 border-t border-gray-100">
          <span>Total</span>
          <span class="text-primary">€{{ order.total_amount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getMyOrder } from '../api'

const route = useRoute()
const order = ref(null)

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
    const { data } = await getMyOrder(route.params.id)
    order.value = data
  } catch (e) {
    console.error(e)
  }
})
</script>
