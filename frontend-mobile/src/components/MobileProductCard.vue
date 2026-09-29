<template>
  <router-link :to="`/products/${product.slug}`" class="block bg-white rounded-xl overflow-hidden tap-active">
    <!-- Image -->
    <div class="relative aspect-square overflow-hidden bg-[#EEEEEE]">
      <img
        v-if="product.images?.length"
        :src="product.images[0].thumbnail_url || product.images[0].image_url"
        :alt="product.title_en || product.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-4xl"></div>

      <!-- Condition Badge -->
      <span
        :class="badgeClasses"
        class="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[9px] font-semibold"
      >
        {{ conditionLabel }}
      </span>
    </div>

    <!-- Info -->
    <div class="p-2.5">
      <h3 class="text-[13px] font-medium text-gray-800 line-clamp-2 leading-snug">
        {{ product.title_en || product.title }}
      </h3>

      <div class="flex items-baseline gap-1.5 mt-1.5">
        <span class="text-lg font-extrabold text-primary">€{{ product.sale_price }}</span>
        <span v-if="product.original_price" class="text-[10px] text-gray-400 line-through">€{{ product.original_price }}</span>
      </div>

      <div class="flex items-center justify-between mt-1">
        <span v-if="product.original_price" class="text-[9px] font-bold text-primary bg-orange-bg px-1.5 py-0.5 rounded">
          {{ discountPercent }}
        </span>
        <span class="text-[10px] text-gray-400">{{ timeAgo(product.created_at) }}</span>
      </div>

      <div v-if="product.origin_country_code" class="flex items-center gap-1 mt-1 text-xs text-gray-500">
        <span>{{ originFlag }}</span>
        <span>{{ originName }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, required: true },
})

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
  for_parts: 'Parts',
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
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return `${Math.floor(diff / 86400)}d`
}
</script>
