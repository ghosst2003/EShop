<template>
  <div class="flex items-center gap-4 mb-4">
    <span class="text-sm text-gray-500">Quantity</span>
    <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden">
      <button
        @click="decrement"
        :disabled="quantity <= 1"
        class="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-50 transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M20 12H4"/></svg>
      </button>
      <input
        type="number"
        v-model.number="quantity"
        min="1"
        :max="maxStock"
        class="w-12 h-9 text-center text-sm border-x border-gray-200 focus:outline-none focus:ring-1 focus:ring-primary/30"
      />
      <button
        @click="increment"
        :disabled="quantity >= maxStock"
        class="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-50 transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
      </button>
    </div>
    <span v-if="maxStock > 0" class="text-xs text-gray-400">{{ maxStock }} available</span>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  maxStock: { type: Number, default: 99 },
  initialValue: { type: Number, default: 1 },
})

const emit = defineEmits(['change'])

const quantity = ref(props.initialValue)

watch(quantity, (val) => {
  const clamped = Math.max(1, Math.min(val, props.maxStock))
  if (val !== clamped) quantity.value = clamped
  emit('change', quantity.value)
})

function increment() {
  if (quantity.value < props.maxStock) {
    quantity.value++
  }
}

function decrement() {
  if (quantity.value > 1) {
    quantity.value--
  }
}
</script>
