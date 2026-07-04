<template>
  <div>
    <Navbar />
    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Checkout</h1>

      <!-- Step Indicator -->
      <div class="flex items-center gap-4 mb-8">
        <div :class="step >= 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'" class="w-10 h-10 rounded-full flex items-center justify-center font-bold">1</div>
        <div class="flex-1 h-1" :class="step > 1 ? 'bg-primary' : 'bg-gray-200'"></div>
        <div :class="step >= 2 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'" class="w-10 h-10 rounded-full flex items-center justify-center font-bold">2</div>
        <div class="flex-1 h-1" :class="step > 2 ? 'bg-primary' : 'bg-gray-200'"></div>
        <div :class="step >= 3 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'" class="w-10 h-10 rounded-full flex items-center justify-center font-bold">3</div>
      </div>

      <!-- Step 1: Shipping Address -->
      <div v-if="step === 1">
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-bold text-lg mb-4">Shipping Address</h2>

          <div v-if="addresses.length > 0" class="space-y-3 mb-4">
            <label v-for="addr in addresses" :key="addr.id"
              class="flex items-start gap-4 p-4 border rounded-xl cursor-pointer hover:border-orange-300 transition"
              :class="selectedAddress === addr.id ? 'border-orange-400 bg-orange-50' : ''">
              <input type="radio" :value="addr.id" v-model="selectedAddress" class="mt-1 accent-orange" />
              <div>
                <div class="font-semibold">{{ addr.recipient_name }}
                  <span v-if="addr.is_default" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded ml-1">Default</span>
                </div>
                <div class="text-gray-500 text-sm">{{ addr.street_address }}, {{ addr.city }}, {{ addr.postal_code }}</div>
                <div class="text-gray-400 text-sm">{{ addr.country }} · {{ addr.phone }}</div>
              </div>
            </label>
          </div>

          <p v-if="addresses.length === 0" class="text-gray-500 mb-4">No saved addresses. Fill in the form below:</p>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <input v-model="addressForm.name" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
              <input v-model="addressForm.phone" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Address *</label>
              <textarea v-model="addressForm.address" rows="3" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none"></textarea>
            </div>
          </div>

          <button @click="goToStep(2)" :disabled="!canProceedAddress"
            class="mt-6 w-full bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
            Continue to Review
          </button>
        </div>
      </div>

      <!-- Step 2: Order Review -->
      <div v-if="step === 2">
        <div class="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 class="font-bold text-lg mb-4">Order Summary</h2>

          <div class="divide-y">
            <div v-for="item in cartItems" :key="item.id" class="flex justify-between py-3">
              <span>{{ (item.product?.title_en || item.product?.title) }} × {{ item.quantity }}</span>
              <span class="font-semibold">€{{ getItemTotal(item) }}</span>
            </div>
          </div>

          <!-- Shipping Method Selection -->
          <div class="mt-6">
            <h3 class="font-semibold text-gray-700 mb-3">Shipping Method</h3>
            <div v-if="shippingLoading" class="text-gray-400 text-sm">Loading shipping options...</div>
            <div v-else-if="shippingOptions.length === 0" class="text-gray-400 text-sm">No shipping options available for your location.</div>
            <div v-else class="space-y-2">
              <label v-for="(opt, idx) in shippingOptions" :key="idx"
                class="flex items-center justify-between p-4 border rounded-xl cursor-pointer hover:border-orange-300 transition"
                :class="selectedShipping === idx ? 'border-orange-400 bg-orange-50' : ''">
                <div class="flex items-center gap-3">
                  <input type="radio" :value="idx" v-model="selectedShipping" class="accent-orange" />
                  <div>
                    <div class="font-semibold">{{ opt.shipping_method }}</div>
                    <div v-if="opt.is_default" class="text-xs text-gray-400">Default option</div>
                  </div>
                </div>
                <div class="font-bold text-primary">€{{ Number(opt.price).toFixed(2) }}</div>
              </label>
            </div>
          </div>

          <!-- Total -->
          <div class="flex justify-between mt-4 pt-4 border-t text-lg font-bold">
            <span>
              Subtotal
              <span v-if="currentShippingPrice > 0" class="text-sm font-normal text-gray-400 ml-2">+ Shipping €{{ currentShippingPrice.toFixed(2) }}</span>
            </span>
            <span class="text-primary">€{{ grandTotal.toFixed(2) }}</span>
          </div>

          <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <p class="font-semibold text-sm">Shipping to:</p>
            <p class="text-gray-600 text-sm">{{ shippingAddress }}</p>
            <p v-if="destinationCountry" class="text-gray-400 text-xs mt-1">
              Destination country: {{ destinationCountry }}
              <span v-if="detectedCountry && detectedCountry !== destinationCountry" class="ml-1">(auto-detected)</span>
            </p>
          </div>

          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
            <textarea v-model="notes" rows="2" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" placeholder="Any special instructions..."></textarea>
          </div>
        </div>

        <div class="flex gap-4">
          <button @click="step = 1" class="flex-1 border border-gray-300 text-gray-700 font-bold py-3 rounded-xl hover:bg-gray-50 transition">
            Back
          </button>
          <button @click="placeOrder" :disabled="placing || shippingOptions.length === 0 && !selectedShipping"
            class="flex-1 bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
            {{ placing ? 'Placing Order...' : 'Place Order' }}
          </button>
        </div>
      </div>

      <!-- Step 3: Order Placed -->
      <div v-if="step === 3 && createdOrder">
        <div class="bg-white rounded-2xl shadow p-12 text-center">
          <div class="text-5xl mb-4">🎉</div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Order Placed!</h2>
          <p class="text-gray-500 mb-6">Order #{{ createdOrder.order_number }}</p>

          <div class="bg-gray-50 rounded-xl p-4 mb-6 inline-block">
            <p class="text-sm text-gray-600">Total: <span class="font-bold text-primary text-lg">€{{ createdOrder.total_amount }}</span></p>
          </div>

          <div class="flex gap-4 justify-center">
            <button v-if="createdOrder.payment_method === 'stripe'"
              @click="payNow" :disabled="paying"
              class="bg-primary text-white font-bold px-8 py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
              {{ paying ? 'Redirecting...' : 'Pay Now →' }}
            </button>
            <router-link :to="`/my-orders/${createdOrder.id}`"
              class="border border-gray-300 text-gray-700 font-bold px-8 py-3 rounded-xl hover:bg-gray-50 transition">
              View Order
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useCart } from '../composables/useCart'
import { useAuth } from '../composables/useAuth'
import { useLocation } from '../composables/useLocation'
import { getAddresses, createOrder, createCheckoutSession, getShippingOptions, getCountries, calculateShipping } from '../api'

const router = useRouter()
const { user } = useAuth()
const { items: cartItems, total: cartTotal, clearCart } = useCart()
const { initLocation, countryCode: detectedCountry } = useLocation()

const step = ref(1)
const addresses = ref([])
const selectedAddress = ref(null)
const addressForm = ref({ name: '', phone: '', address: '' })
const notes = ref('')
const placing = ref(false)
const paying = ref(false)
const createdOrder = ref(null)

// Shipping
const shippingOptions = ref([])
const selectedShipping = ref(null)
const shippingLoading = ref(false)
const destinationCountry = ref('')

const canProceedAddress = computed(() => {
  return selectedAddress.value || (addressForm.value.name && addressForm.value.phone && addressForm.value.address)
})

const shippingAddress = computed(() => {
  if (selectedAddress.value) {
    const addr = addresses.value.find(a => a.id === selectedAddress.value)
    return addr ? `${addr.recipient_name}, ${addr.street_address}, ${addr.city}, ${addr.postal_code}, ${addr.country}` : ''
  }
  return `${addressForm.value.name}, ${addressForm.value.address}, ${addressForm.value.phone}`
})

const currentShippingPrice = computed(() => {
  if (selectedShipping.value !== null && shippingOptions.value[selectedShipping.value]) {
    return Number(shippingOptions.value[selectedShipping.value].price)
  }
  return 0
})

const grandTotal = computed(() => {
  return cartTotal.value + currentShippingPrice.value
})

const getItemTotal = (item) => {
  const price = item.product?.sale_price || 0
  return (price * (item.quantity || 1)).toFixed(2)
}

const goToStep = async (s) => {
  step.value = s
  // 进入第2步时加载运费选项
  if (s === 2) {
    await loadShippingOptions()
  }
}

const loadShippingOptions = async () => {
  if (!cartItems.value.length) return

  // 确定目的地国家
  let country = ''
  if (selectedAddress.value) {
    const addr = addresses.value.find(a => a.id === selectedAddress.value)
    if (addr) country = addr.country.substring(0, 2).toUpperCase()
  }
  if (!country && addressForm.value.address) {
    const parts = addressForm.value.address.split(',')
    country = parts[parts.length - 1].trim().substring(0, 2).toUpperCase()
  }
  // 使用检测到的国家作为兜底
  if (!country && detectedCountry.value) {
    country = detectedCountry.value
  }

  destinationCountry.value = country
  if (!country) {
    shippingOptions.value = []
    return
  }

  shippingLoading.value = true
  try {
    // 为每个商品获取运费选项，合并取最便宜的
    const allOptions = {}
    for (const ci of cartItems.value) {
      if (!ci.product) continue
      try {
        const productSlug = ci.product.slug
        if (!productSlug) continue
        const res = await getShippingOptions(productSlug, country)
        const options = res.data
        if (options.length > 0) {
          for (const opt of options) {
            if (!allOptions[opt.shipping_method]) {
              allOptions[opt.shipping_method] = {
                shipping_method: opt.shipping_method,
                total_price: 0,
                is_default: opt.is_default,
              }
            }
            allOptions[opt.shipping_method].total_price += Number(opt.price) * (ci.quantity || 1)
          }
        }
      } catch (e) {
        console.error(`Failed to get shipping for product ${ci.product_id}:`, e)
      }
    }

    shippingOptions.value = Object.values(allOptions).sort((a, b) => a.total_price - b.total_price)

    // 默认选择第一个选项
    if (shippingOptions.value.length > 0) {
      selectedShipping.value = 0
    }
  } catch (e) {
    console.error('Failed to load shipping options', e)
  } finally {
    shippingLoading.value = false
  }
}

const placeOrder = async () => {
  if (selectedShipping.value === null || !shippingOptions.value.length) {
    alert('Please select a shipping method')
    return
  }

  placing.value = true
  try {
    const opt = shippingOptions.value[selectedShipping.value]
    const data = {}
    if (selectedAddress.value) {
      data.address_id = selectedAddress.value
    } else {
      data.buyer_name = addressForm.value.name
      data.buyer_phone = addressForm.value.phone
      data.buyer_address = addressForm.value.address
    }
    data.shipping_method = opt.shipping_method
    data.shipping_price = Number(opt.price)
    if (notes.value) data.notes = notes.value

    const res = await createOrder(data)
    createdOrder.value = res.data
    step.value = 3
    clearCart()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to create order')
  } finally {
    placing.value = false
  }
}

const payNow = async () => {
  paying.value = true
  try {
    const res = await createCheckoutSession(createdOrder.value.id)
    window.location.href = res.data.checkout_url
  } catch (e) {
    alert(e.response?.data?.detail || 'Payment failed to initialize')
  } finally {
    paying.value = false
  }
}

onMounted(async () => {
  // Start location detection in background
  initLocation()
  if (cartItems.value.length === 0) {
    router.push('/cart')
    return
  }
  try {
    const res = await getAddresses()
    addresses.value = res.data
    const def = addresses.value.find(a => a.is_default)
    if (def) selectedAddress.value = def.id
  } catch (e) {
    // not logged in or no addresses
  }
})
</script>
