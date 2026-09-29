<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <!-- Header -->
    <div class="sticky top-0 z-40 bg-white safe-top border-b border-gray-100">
      <div class="flex items-center px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1 text-center mr-8">Shopping Cart ({{ items.length }})</h1>
      </div>
    </div>

    <div v-if="items.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
      <span class="text-5xl mb-4"></span>
      <p class="text-base">Your cart is empty</p>
      <router-link to="/browse" class="mt-4 text-primary font-semibold tap-active">Start Shopping →</router-link>
    </div>

    <div v-else>
      <!-- Cart Items -->
      <div class="px-4 py-4 space-y-3">
        <div
          v-for="item in items"
          :key="item.id"
          class="bg-white rounded-xl p-4 flex gap-3"
        >
          <!-- Checkbox -->
          <div class="flex flex-col items-center justify-between">
            <input
              type="checkbox"
              :checked="selectedIds.includes(item.id)"
              @change="toggleSelect(item.id)"
              class="w-5 h-5 accent-primary"
            />
            <button @click="removeItem(item.id)" class="text-gray-300 text-lg tap-active mt-2">✕</button>
          </div>

          <!-- Image -->
          <div class="w-20 h-20 bg-[#EBEBF0] rounded-xl overflow-hidden shrink-0">
            <img
              v-if="item.product?.images?.length"
              :src="item.product.images[0].thumbnail_url || item.product.images[0].image_url"
              class="w-full h-full object-cover"
            />
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-semibold text-gray-900 truncate">{{ item.product?.title_en || 'Product' }}</h3>
            <p class="text-primary font-bold mt-1">€{{ item.product?.sale_price }}</p>
            <div class="flex items-center justify-between mt-2">
              <div class="flex items-center gap-2 bg-[#F5F5F5] rounded-full">
                <button @click="updateQuantity(item.id, -1)" class="w-7 h-7 flex items-center justify-center text-gray-500 tap-active">−</button>
                <span class="text-sm font-medium w-6 text-center">{{ item.quantity }}</span>
                <button @click="updateQuantity(item.id, 1)" class="w-7 h-7 flex items-center justify-center text-gray-500 tap-active">+</button>
              </div>
              <span class="text-sm font-bold">€{{ (item.product?.sale_price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Shipping Estimate -->
      <div class="mx-4 mb-4 bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold text-gray-900 mb-2">Shipping Estimate</h3>
        <p class="text-xs text-gray-500">Calculated at checkout</p>
      </div>

      <!-- Bottom Checkout Bar -->
      <div class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 px-4 py-3 safe-bottom">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-500">Total ({{ selectedCount }} items)</span>
          <span class="text-xl font-extrabold text-primary">€{{ selectedTotal.toFixed(2) }}</span>
        </div>
        <button
          @click="checkout"
          :disabled="selectedCount === 0"
          class="w-full bg-primary text-white font-bold py-3 rounded-full tap-active disabled:opacity-50"
        >
          Checkout ({{ selectedCount }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../composables/useCart'

const router = useRouter()
const { items, removeItem, updateQuantity, selectedIds, toggleSelect, selectedCount, selectedTotal } = useCart()

const checkout = () => {
  if (selectedCount.value > 0) {
    router.push('/checkout')
  }
}

onMounted(() => {})
</script>
