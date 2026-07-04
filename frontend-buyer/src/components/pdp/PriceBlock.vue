<template>
  <div class="bg-gradient-to-r from-primary/5 to-transparent rounded-xl p-4 mb-4">
    <div class="flex items-baseline gap-3">
      <span class="text-sm text-primary font-medium">€</span>
      <span class="text-4xl font-black text-primary leading-none">{{ price }}</span>
    </div>
    <div v-if="originalPrice" class="flex items-center gap-3 mt-2">
      <span class="text-gray-400 line-through text-sm">€{{ originalPrice }}</span>
      <span class="bg-primary text-white text-xs font-bold px-2 py-0.5 rounded">
        -{{ discountPercent }}%
      </span>
    </div>
    <div v-if="soldCount !== null" class="text-xs text-gray-400 mt-1.5">
      {{ soldCount }} sold
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  salePrice: { type: [Number, String], required: true },
  originalPrice: { type: [Number, String], default: null },
  soldCount: { type: Number, default: null },
})

const price = computed(() => {
  const num = parseFloat(props.salePrice)
  return isNaN(num) ? '0.00' : num.toFixed(2)
})

const discountPercent = computed(() => {
  const sale = parseFloat(props.salePrice)
  const orig = parseFloat(props.originalPrice)
  if (!orig || !sale || orig <= sale) return 0
  return Math.round((1 - sale / orig) * 100)
})
</script>
