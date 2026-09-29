<template>
  <div v-if="product" class="min-h-screen bg-[#F7F7F7] pb-24">
    <!-- Minimal Header -->
    <div class="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-4 py-3 safe-top">
      <button @click="$router.back()" class="w-9 h-9 bg-white/90 backdrop-blur rounded-full flex items-center justify-center text-lg shadow-sm tap-active">
        ←
      </button>
      <div class="flex gap-2">
        <button class="w-9 h-9 bg-white/90 backdrop-blur rounded-full flex items-center justify-center text-base shadow-sm tap-active">♡</button>
        <button class="w-9 h-9 bg-white/90 backdrop-blur rounded-full flex items-center justify-center text-base shadow-sm tap-active"></button>
      </div>
    </div>

    <!-- Image Gallery -->
    <div class="relative">
      <div
        class="aspect-square bg-[#EEEEEE] flex items-center justify-center overflow-hidden"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      >
        <img
          v-if="product.images?.length"
          :src="product.images[currentImage].image_url"
          :alt="product.title_en"
          class="w-full h-full object-cover"
        />
        <span v-else class="text-6xl text-gray-300"></span>
      </div>
      <!-- Image dots -->
      <div v-if="product.images?.length > 1" class="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5">
        <span
          v-for="(_, i) in product.images"
          :key="i"
          class="w-1.5 h-1.5 rounded-full transition-all"
          :class="i === currentImage ? 'bg-white w-4' : 'bg-white/50'"
        ></span>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-4">
      <!-- Price -->
      <div class="flex items-baseline gap-2 mb-2">
        <span class="text-2xl font-extrabold text-primary">€{{ product.sale_price }}</span>
        <span v-if="product.original_price" class="text-sm text-gray-400 line-through">€{{ product.original_price }}</span>
        <span v-if="discountPercent" class="text-xs font-bold text-white bg-primary px-2 py-0.5 rounded-full">{{ discountPercent }}</span>
      </div>

      <!-- Title -->
      <h1 class="text-lg font-bold text-gray-900 mb-1">{{ product.title_en || product.title }}</h1>
      <p v-if="product.brand" class="text-sm text-gray-500">{{ product.brand }}</p>

      <!-- Condition -->
      <div class="flex items-center gap-2 mt-2">
        <span :class="badgeClasses" class="px-2 py-0.5 rounded-full text-xs font-medium">
          {{ conditionLabel }}
        </span>
        <span v-if="product.condition_note" class="text-xs text-gray-500 line-clamp-1">{{ product.condition_note }}</span>
      </div>

      <!-- Origin -->
      <div v-if="product.origin_country_code" class="flex items-center gap-1 mt-2 text-sm text-gray-500">
        <span>{{ originFlag }}</span>
        <span>Ships from {{ originName }}</span>
      </div>

      <!-- Stock -->
      <div v-if="product.auto_manage_stock" class="mt-2 text-sm">
        <span v-if="product.stock_quantity > 0" class="text-green-600">✅ {{ product.stock_quantity }} in stock</span>
        <span v-else class="text-red-600 font-medium">❌ Out of stock</span>
      </div>
    </div>

    <!-- Shipping Info -->
    <div class="mx-4 mb-4 bg-white rounded-xl p-4">
      <h3 class="text-sm font-bold text-gray-900 mb-2">Shipping</h3>
      <div class="text-sm text-gray-600">
        <p v-if="shippingOptions.length">From €{{ lowestShipping }}</p>
        <p v-else class="text-gray-400">Calculate shipping at checkout</p>
      </div>
    </div>

    <!-- Description -->
    <div class="mx-4 mb-4 bg-white rounded-xl p-4">
      <h3 class="text-sm font-bold text-gray-900 mb-2">Description</h3>
      <div
        class="product-description text-sm text-gray-600"
        v-html="product.description_en || product.description"
      ></div>
    </div>

    <!-- Spacer for bottom bar -->
    <div class="h-4"></div>
  </div>

  <!-- Fixed Bottom Action Bar -->
  <div v-if="product" class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 px-4 py-3 safe-bottom">
    <div class="flex gap-3">
      <button
        @click="addToCart(product, 1)"
        class="flex-1 bg-orange-bg text-primary font-bold py-3 rounded-full tap-active"
        :disabled="product.stock_quantity === 0"
      >
        Add to Cart
      </button>
      <button
        @click="buyNow"
        class="flex-1 bg-primary text-white font-bold py-3 rounded-full tap-active"
        :disabled="product.stock_quantity === 0"
      >
        Buy Now
      </button>
    </div>
  </div>

  <!-- Loading / Not Found -->
  <div v-else-if="loading" class="min-h-screen flex items-center justify-center text-gray-400">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      <span>Loading...</span>
    </div>
  </div>
  <div v-else class="min-h-screen flex items-center justify-center text-gray-400">
    Product not found.
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct } from '../api'
import { useCart } from '../composables/useCart'

const route = useRoute()
const router = useRouter()
const { addToCart } = useCart()

const product = ref(null)
const loading = ref(true)
const currentImage = ref(0)

// Swipe handling
let touchStartX = 0
const onTouchStart = (e) => { touchStartX = e.touches[0].clientX }
const onTouchMove = () => {}
const onTouchEnd = (e) => {
  const diffX = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(diffX) > 50 && product.value?.images?.length > 1) {
    if (diffX > 0) {
      currentImage.value = (currentImage.value - 1 + product.value.images.length) % product.value.images.length
    } else {
      currentImage.value = (currentImage.value + 1) % product.value.images.length
    }
  }
}

const codeToFlagEmoji = (code) => {
  if (!code || code.length !== 2) return ''
  const codePoints = code.toUpperCase().split('').map(char => 127397 + char.charCodeAt())
  return String.fromCodePoint(...codePoints)
}

const originFlag = computed(() => codeToFlagEmoji(product.value?.origin_country_code))
const originName = computed(() => product.value?.origin_country_code || '')

const conditionLabel = computed(() => ({
  new: 'New', like_new: 'Like New', good: 'Good', fair: 'Fair', poor: 'Poor', for_parts: 'Parts'
}[product.value?.condition_grade] || ''))

const badgeClasses = computed(() => ({
  new: 'bg-green-100 text-green-600', like_new: 'bg-green-100 text-green-600',
  good: 'bg-amber-100 text-amber-600', fair: 'bg-purple-100 text-purple-600',
  poor: 'bg-red-100 text-red-600', for_parts: 'bg-red-100 text-red-600'
}[product.value?.condition_grade] || ''))

const discountPercent = computed(() => {
  if (!product.value?.original_price || !product.value?.sale_price) return ''
  const pct = Math.round((1 - product.value.sale_price / product.value.original_price) * 100)
  return `-${pct}%`
})

const shippingOptions = ref([])
const lowestShipping = computed(() => {
  if (!shippingOptions.value.length) return null
  return Math.min(...shippingOptions.value.map(o => parseFloat(o.total_fee))).toFixed(2)
})

const buyNow = () => {
  addToCart(product.value, 1)
  router.push('/checkout')
}

onMounted(async () => {
  try {
    const { data } = await getProduct(route.params.slug)
    product.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@supports (padding-top: env(safe-area-inset-top)) {
  .safe-top { padding-top: env(safe-area-inset-top); }
}
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .safe-bottom { padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
}
</style>
