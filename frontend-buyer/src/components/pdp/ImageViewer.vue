<template>
  <div
    class="relative w-full aspect-square overflow-hidden bg-[#F5F5F5] cursor-crosshair group"
    @mouseenter="isZooming = true"
    @mousemove="handleMouseMove"
    @mouseleave="isZooming = false"
  >
    <Transition name="fade" mode="out-in">
      <img
        :key="src"
        :src="src"
        :alt="alt"
        class="w-full h-full object-cover transition-transform duration-300 ease-out"
        :style="zoomStyle"
        @load="onLoad"
        @error="onError"
      />
    </Transition>

    <!-- Loading placeholder -->
    <div v-if="!loaded && !errored" class="absolute inset-0 flex items-center justify-center">
      <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error fallback -->
    <div v-if="errored" class="absolute inset-0 flex items-center justify-center text-gray-300 text-6xl">
      🖼️
    </div>

    <!-- Prev/Next arrows (hover) -->
    <button
      v-if="showArrows && hasPrev"
      @click="$emit('prev')"
      class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 bg-white/90 rounded-full flex items-center justify-center text-gray-600 shadow
             opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-white"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
    </button>
    <button
      v-if="showArrows && hasNext"
      @click="$emit('next')"
      class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 bg-white/90 rounded-full flex items-center justify-center text-gray-600 shadow
             opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-white"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
    </button>

    <!-- Image counter -->
    <div
      v-if="total > 1"
      class="absolute bottom-3 right-3 bg-black/60 text-white text-xs px-2.5 py-1 rounded-full backdrop-blur-sm"
    >
      {{ current + 1 }} / {{ total }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  alt: { type: String, default: '' },
  current: { type: Number, default: 0 },
  total: { type: Number, default: 1 },
  hasPrev: { type: Boolean, default: false },
  hasNext: { type: Boolean, default: false },
  showArrows: { type: Boolean, default: true },
  zoomScale: { type: Number, default: 1.8 },
})

defineEmits(['prev', 'next'])

const isZooming = ref(false)
const mouseX = ref(50)
const mouseY = ref(50)
const loaded = ref(false)
const errored = ref(false)

const zoomStyle = computed(() => {
  if (!isZooming.value) return { transform: 'scale(1)', transformOrigin: 'center center' }
  return {
    transform: `scale(${props.zoomScale})`,
    transformOrigin: `${mouseX.value}% ${mouseY.value}%`,
  }
})

function handleMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  mouseX.value = ((e.clientX - rect.left) / rect.width) * 100
  mouseY.value = ((e.clientY - rect.top) / rect.height) * 100
}

function onLoad() {
  loaded.value = true
  errored.value = false
}

function onError() {
  errored.value = true
  loaded.value = true
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
