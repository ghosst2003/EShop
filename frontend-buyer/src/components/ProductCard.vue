<template>
  <div class="group relative bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow flex flex-col">
    <router-link :to="`/products/${product.slug}`" class="block flex flex-col flex-1">
      <!-- Image -->
      <div class="relative aspect-[4/3] overflow-hidden bg-[#EEEEEE]">
        <img
          v-if="product.images?.length"
          :src="product.images[0].thumbnail_url || product.images[0].image_url"
          :alt="product.title_en || product.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-5xl"></div>

        <!-- Wishlist -->
        <button class="absolute top-2 right-2 w-6 h-6 bg-black/35 rounded-full flex items-center justify-center text-white text-sm hover:bg-primary transition">
          ♡
        </button>

        <!-- Condition Badge -->
        <span
          :class="badgeClasses"
          class="absolute bottom-2 left-2 px-3 py-0.5 rounded-full text-[10px] font-semibold"
        >
          {{ conditionLabel }}
        </span>
      </div>

      <!-- Info -->
      <div class="p-3 flex-1">
        <h3 class="text-[13px] font-semibold text-gray-800 line-clamp-2 mb-1 leading-snug">
          {{ product.title_en || product.title }}
        </h3>

        <div class="flex items-baseline gap-2 mt-2">
          <span class="text-lg font-extrabold text-primary">€{{ product.sale_price }}</span>
          <span v-if="product.original_price" class="text-xs text-gray-400 line-through">€{{ product.original_price }}</span>
        </div>

        <div class="flex items-center justify-between mt-1.5">
          <span v-if="product.original_price" class="text-[9px] font-bold text-primary bg-orange-100/80 px-1.5 py-0.5 rounded">
            {{ discountPercent }}
          </span>
          <span class="text-[11px] text-gray-400">{{ timeAgo(product.created_at) }}</span>
        </div>

        <div v-if="product.origin_country_code" class="flex items-center gap-1 mt-1 text-xs text-gray-500">
          <span class="text-[11px]">{{ originFlag }}</span>
          <span>{{ originName }}</span>
        </div>
      </div>
    </router-link>

    <!-- Add to Cart Button (appears on hover) -->
    <button
      v-if="product.status === 'active' && product.stock_quantity !== 0"
      @click.stop="addToCart(product)"
      class="w-full bg-primary text-white text-xs font-bold py-2 hover:bg-primary-light transition opacity-0 group-hover:opacity-100 shrink-0">
      🛒 Add to Cart
    </button>
    <div v-else class="w-full bg-gray-100 text-gray-400 text-xs font-bold py-2 text-center cursor-not-allowed shrink-0">
      {{ product.status === 'sold' ? 'Sold Out' : 'Unavailable' }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCart } from '../composables/useCart'

const props = defineProps({
  product: { type: Object, required: true },
})

const { addToCart } = useCart()

const codeToFlagEmoji = (code) => {
  if (!code || code.length !== 2) return ''
  const codePoints = code.toUpperCase().split('').map(char => 127397 + char.charCodeAt())
  return String.fromCodePoint(...codePoints)
}

const originFlag = computed(() => codeToFlagEmoji(props.product.origin_country_code))
const originName = computed(() => {
  const code = props.product.origin_country_code
  return code ? code.toUpperCase() : ''
})

const conditionLabel = computed(() => ({
  new: 'New',
  like_new: 'Like New',
  good: 'Good',
  fair: 'Fair',
  poor: 'Poor',
  for_parts: 'For Parts',
}[props.product.condition_grade] || props.product.condition_grade))

const badgeClasses = computed(() => ({
  new: 'bg-green-100 text-green-600',
  like_new: 'bg-green-100 text-green-600',
  good: 'bg-amber-100 text-amber-600',
  fair: 'bg-purple-100 text-purple-600',
  poor: 'bg-red-100 text-red-600',
  for_parts: 'bg-red-100 text-red-600',
}[props.product.condition_grade] || 'bg-gray-100 text-gray-600'))

const discountPercent = computed(() => {
  if (!props.product.original_price || !props.product.sale_price) return ''
  const pct = Math.round((1 - props.product.sale_price / props.product.original_price) * 100)
  return `-${pct}%`
})

const timeAgo = (dateStr) => {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}
</script>
