<template>
  <div class="mb-4">
    <h1 class="text-lg sm:text-xl font-bold text-gray-900 leading-snug">{{ title }}</h1>
    <div v-if="brand" class="text-sm text-gray-400 mt-1">Brand: {{ brand }}</div>
    <div class="flex flex-wrap gap-2 mt-3">
      <span :class="badgeClasses" class="inline-flex px-3 py-1 rounded-full text-xs font-semibold">
        {{ conditionLabel }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  brand: { type: String, default: '' },
  conditionGrade: { type: String, default: '' },
})

const conditionLabel = computed(() => ({
  new: 'New',
  like_new: 'Like New',
  good: 'Good',
  fair: 'Fair',
  poor: 'Poor',
  for_parts: 'For Parts / Repair',
}[props.conditionGrade] || props.conditionGrade))

const badgeClasses = computed(() => ({
  new: 'bg-green-100 text-green-700',
  like_new: 'bg-green-100 text-green-700',
  good: 'bg-amber-100 text-amber-700',
  fair: 'bg-purple-100 text-purple-700',
  poor: 'bg-red-100 text-red-700',
  for_parts: 'bg-red-100 text-red-700',
}[props.conditionGrade] || 'bg-gray-100 text-gray-600'))
</script>
