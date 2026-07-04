<template>
  <div>
    <Navbar />
    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Shopping Cart ({{ count }})</h1>

      <div v-if="items.length === 0" class="bg-white rounded-2xl shadow p-12 text-center">
        <div class="text-5xl mb-4">🛒</div>
        <p class="text-gray-500 mb-6">Your cart is empty</p>
        <router-link to="/browse" class="bg-primary text-white font-bold px-8 py-3 rounded-xl hover:bg-primary-light transition">
          Start Shopping
        </router-link>
      </div>

      <div v-else>
        <!-- Cart Items -->
        <div class="bg-white rounded-2xl shadow divide-y">
          <div v-for="item in items" :key="item.id" class="flex items-center gap-6 p-6">
            <div class="w-24 h-24 bg-[#EBEBF0] rounded-xl overflow-hidden shrink-0">
              <img v-if="item.product?.images?.[0]" :src="item.product.images[0].thumbnail_url || item.product.images[0].image_url" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">📷</div>
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 truncate">{{ item.product?.title_en || item.product?.title || 'Product' }}</h3>
              <p class="text-gray-500 text-sm">{{ item.product?.brand || '' }}</p>
              <p class="text-primary font-bold mt-1">€{{ item.product?.sale_price }}</p>
            </div>

            <div class="flex items-center gap-2">
              <button @click="updateQty(getItemId(item), (item.quantity || 1) - 1)"
                class="w-8 h-8 rounded-lg border flex items-center justify-center hover:bg-gray-100">−</button>
              <span class="w-10 text-center font-semibold">{{ item.quantity || 1 }}</span>
              <button @click="updateQty(getItemId(item), (item.quantity || 1) + 1)"
                class="w-8 h-8 rounded-lg border flex items-center justify-center hover:bg-gray-100">+</button>
            </div>

            <div class="text-right shrink-0 w-24">
              <p class="font-bold">€{{ getItemTotal(item) }}</p>
            </div>

            <button @click="removeCartItem(getItemId(item))" class="text-gray-400 hover:text-red-500 transition">✕</button>
          </div>
        </div>

        <!-- Shipping Estimate -->
        <div class="mt-4 bg-white rounded-2xl shadow p-6">
          <h3 class="font-semibold text-gray-900 mb-3">Shipping Estimate</h3>

          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-400">
              📍 Shipping to <strong>{{ selectedCountryName }}</strong>
            </span>
            <button @click="showCountrySelector = true" class="text-primary text-xs hover:underline">Change</button>
          </div>
          <select
            v-if="showCountrySelector"
            v-model="shippingCountry"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-orange-400 outline-none mb-3"
          >
            <option value="" disabled>Select destination country</option>
            <option v-for="c in countries" :key="c.code" :value="c.code">
              {{ c.flag_emoji }} {{ c.name_en || c.name }}
            </option>
          </select>

          <div v-if="shippingCountry && shippingEstimate.length" class="space-y-2 text-sm">
            <div v-for="(est, idx) in shippingEstimate" :key="idx"
                 class="flex justify-between text-gray-600">
              <span>{{ est.product_title }} × {{ est.quantity }}</span>
              <span>€{{ Number(est.shipping_cost).toFixed(2) }}</span>
            </div>
            <div class="border-t pt-2 flex justify-between font-bold text-base">
              <span>Total Shipping</span>
              <span class="text-primary">€{{ shippingTotal.toFixed(2) }}</span>
            </div>
          </div>

          <p v-else-if="shippingCountry && !shippingLoading" class="text-gray-400 text-sm">
            No shipping options for this country.
          </p>
          <p v-else-if="shippingLoading" class="text-gray-400 text-sm">Calculating...</p>
        </div>

        <!-- Cart Summary -->
        <div class="mt-6 bg-white rounded-2xl shadow p-6">
          <div class="flex justify-between items-center mb-2">
            <span class="text-lg font-bold">Subtotal</span>
            <span class="text-2xl font-black text-primary">€{{ total.toFixed(2) }}</span>
          </div>
          <div v-if="shippingTotal > 0" class="flex justify-between items-center mb-4 text-sm text-gray-500">
            <span>+ Shipping</span>
            <span>€{{ shippingTotal.toFixed(2) }}</span>
          </div>
          <router-link to="/checkout"
            class="block w-full bg-primary text-white text-center font-bold py-4 rounded-xl hover:bg-primary-light transition text-lg">
            Proceed to Checkout
          </router-link>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useCart } from '../composables/useCart'
import { useLocation } from '../composables/useLocation'
import { getShippingOptions, getCountries } from '../api'

const { items, count, total, updateQty, removeFromCart } = useCart()
const { countryCode: detectedCountry, initLocation } = useLocation()

const getItemId = (item) => item.id || item.product_id
const getItemTotal = (item) => {
  const price = item.product?.sale_price || 0
  return (price * (item.quantity || 1)).toFixed(2)
}

const countries = ref([])
const shippingCountry = ref('')
const shippingEstimate = ref([])
const shippingLoading = ref(false)
const showCountrySelector = ref(false)

const selectedCountryName = computed(() => {
  if (!shippingCountry.value) return 'Unknown'
  const c = countries.value.find(c => c.code === shippingCountry.value)
  return c?.name_en || c?.name || shippingCountry.value
})

const shippingTotal = computed(() => {
  return shippingEstimate.value.reduce((sum, e) => sum + Number(e.shipping_cost || 0), 0)
})

async function loadShippingEstimate() {
  if (!shippingCountry.value || !items.value.length) {
    shippingEstimate.value = []
    return
  }

  shippingLoading.value = true
  try {
    const results = []
    for (const item of items.value) {
      const product = item.product
      if (!product || !product.slug) continue

      try {
        const res = await getShippingOptions(product.slug, shippingCountry.value)
        const options = res.data
        if (options.length > 0) {
          // 取最便宜的选项
          const cheapest = options.reduce((min, opt) =>
            Number(opt.price) < Number(min.price) ? opt : min
          )
          results.push({
            product_title: product.title_en || product.title,
            quantity: item.quantity || 1,
            shipping_cost: (Number(cheapest.price) * (item.quantity || 1)).toFixed(2),
          })
        }
      } catch (e) {
        console.error(`Failed to get shipping for ${product.slug}:`, e)
      }
    }
    shippingEstimate.value = results
  } catch (e) {
    console.error('Failed to load shipping estimate:', e)
  } finally {
    shippingLoading.value = false
  }
}

watch(shippingCountry, loadShippingEstimate)

onMounted(async () => {
  try {
    const { data } = await getCountries()
    countries.value = data
  } catch {}

  // Auto-detect location for shipping country
  const detected = await initLocation()
  if (detected && countries.value.find(c => c.code === detected)) {
    shippingCountry.value = detected
  } else if (countries.value.length > 0) {
    shippingCountry.value = countries.value[0].code
  }
})
</script>
