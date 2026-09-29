<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <div class="bg-white safe-top border-b border-gray-100">
      <div class="flex items-center px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1 text-center mr-8">Checkout</h1>
      </div>
    </div>

    <div class="px-4 py-4 space-y-4 pb-24">
      <!-- Shipping Address -->
      <div class="bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold text-gray-900 mb-2">Shipping Address</h3>
        <div v-if="address" class="text-sm text-gray-600">
          <p>{{ address.name }}</p>
          <p>{{ address.street }}</p>
          <p>{{ address.city }}, {{ address.postal_code }}</p>
          <p>{{ address.country }}</p>
        </div>
        <p v-else class="text-sm text-primary tap-active" @click="showAddressForm = !showAddressForm">+ Add shipping address</p>
      </div>

      <!-- Order Summary -->
      <div class="bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold text-gray-900 mb-2">Order Summary</h3>
        <div v-for="item in selectedItems" :key="item.id" class="flex justify-between text-sm py-1">
          <span class="text-gray-600">{{ item.product?.title_en }} × {{ item.quantity }}</span>
          <span>€{{ (item.product?.sale_price * item.quantity).toFixed(2) }}</span>
        </div>
        <div class="border-t border-gray-100 mt-2 pt-2 flex justify-between font-bold">
          <span>Subtotal</span>
          <span class="text-primary">€{{ selectedTotal.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Payment Method -->
      <div class="bg-white rounded-xl p-4">
        <h3 class="text-sm font-bold text-gray-900 mb-2">Payment Method</h3>
        <div class="flex gap-2">
          <button
            v-for="method in paymentMethods"
            :key="method.code"
            @click="selectedPayment = method.code"
            class="flex-1 py-2 rounded-lg text-xs font-medium border-2 tap-active"
            :class="selectedPayment === method.code ? 'border-primary bg-orange-bg' : 'border-gray-200'"
          >
            {{ method.name_en }}
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Checkout Bar -->
    <div class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 px-4 py-3 safe-bottom">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-500">Total</span>
        <span class="text-xl font-extrabold text-primary">€{{ selectedTotal.toFixed(2) }}</span>
      </div>
      <button @click="placeOrder" class="w-full bg-primary text-white font-bold py-3 rounded-full tap-active">
        Place Order
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../composables/useCart'
import { getPaymentMethods, createOrder } from '../api'

const router = useRouter()
const { items, selectedIds, selectedItems, selectedTotal, clearCart } = useCart()
const paymentMethods = ref([])
const selectedPayment = ref('paypal')
const address = ref(null)
const showAddressForm = ref(false)

const placeOrder = async () => {
  try {
    await createOrder({
      items: selectedItems.value.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      payment_method: selectedPayment.value,
    })
    clearCart()
    router.push('/order-success')
  } catch (e) {
    alert('Order failed: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  try {
    const { data } = await getPaymentMethods()
    paymentMethods.value = data || []
  } catch {}
})
</script>
