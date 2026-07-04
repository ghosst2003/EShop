<template>
  <div class="mb-4 p-4 bg-gray-50 rounded-xl space-y-2" v-if="shippingOptions.length || shippingNotes.length">
    <!-- Dynamic cheapest shipping option -->
    <div v-if="cheapestOption" class="flex items-center gap-2 text-sm">
      <span class="text-gray-400">🚚</span>
      <span class="text-gray-600">
        From <strong class="text-gray-900">€{{ Number(cheapestOption.total_fee).toFixed(2) }}</strong>
        via {{ cheapestOption.shipping_method }}
        <span v-if="cheapestOption.estimated_days_min" class="text-gray-400 ml-1">
          ({{ cheapestOption.estimated_days_min }}-{{ cheapestOption.estimated_days_max }} days)
        </span>
      </span>
    </div>

    <!-- Shipping notes -->
    <div v-for="note in shippingNotes" :key="note.id" class="flex items-start gap-2 text-sm">
      <span class="text-gray-400 mt-0.5">📋</span>
      <div>
        <span class="text-gray-600 font-medium">{{ note.title_en || note.title }}</span>
        <div v-if="note.content_en || note.content" class="text-xs text-gray-400 mt-0.5">
          {{ note.content_en || note.content }}
        </div>
      </div>
    </div>

    <!-- Always show buyer protection -->
    <div class="flex items-center gap-2 text-sm">
      <span class="text-gray-400">🔒</span>
      <span class="text-gray-600">Buyer protection guarantee</span>
    </div>
  </div>

  <!-- Fallback: static info when no data -->
  <div v-else class="mb-4 p-4 bg-gray-50 rounded-xl space-y-2">
    <div class="flex items-center gap-2 text-sm">
      <span class="text-gray-400">🚚</span>
      <span class="text-gray-600">Shipping calculated at checkout</span>
    </div>
    <div class="flex items-center gap-2 text-sm">
      <span class="text-gray-400">🔒</span>
      <span class="text-gray-600">Buyer protection guarantee</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getShippingOptions, getShippingNotes } from '@/api'

const props = defineProps({
  productSlug: String,
  countryCode: String,
})

const shippingOptions = ref([])
const shippingNotes = ref([])
const loading = ref(false)

const cheapestOption = computed(() => {
  if (!shippingOptions.value.length) return null
  return shippingOptions.value[0] // Already sorted by default-first, then price
})

async function loadData() {
  if (!props.productSlug || !props.countryCode) return

  loading.value = true
  try {
    const { data } = await getShippingOptions(props.productSlug, props.countryCode)
    shippingOptions.value = data || []
  } catch {
    shippingOptions.value = []
  }

  try {
    const { data } = await getShippingNotes(props.productSlug)
    shippingNotes.value = data || []
  } catch {
    shippingNotes.value = []
  }
  loading.value = false
}

onMounted(loadData)
watch(() => [props.productSlug, props.countryCode], loadData)
</script>
