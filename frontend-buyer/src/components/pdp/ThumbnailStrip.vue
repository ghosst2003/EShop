<template>
  <div class="flex gap-2 mt-3 overflow-x-auto hide-scrollbar">
    <button
      v-for="(img, idx) in images"
      :key="idx"
      @click="$emit('select', idx)"
      class="w-16 h-16 sm:w-20 sm:h-20 rounded-lg overflow-hidden shrink-0 border-2 transition-all duration-200"
      :class="idx === activeIndex
        ? 'border-primary ring-1 ring-primary/30'
        : 'border-transparent hover:border-gray-300'"
    >
      <img :src="img" class="w-full h-full object-cover" loading="lazy" />
    </button>
  </div>
</template>

<script setup>
defineProps({
  images: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: 0 },
})

defineEmits(['select'])
</script>
