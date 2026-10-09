<template>
  <div class="flex rounded-full overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed" :class="{ 'pointer-events-none': disabled }">
    <button
      @click="$emit('addToCart')"
      class="flex-1 py-3.5 font-bold text-base md:text-sm text-center transition-colors bg-[#DFF263] text-[#173F34]"
    >
      Add to Cart
    </button>
    <button
      @click="$emit('buyNow')"
      class="flex-1 py-3.5 text-white font-bold text-base md:text-sm text-center transition-colors bg-[#173F34]"
    >
      Buy Now
    </button>
  </div>
</template>

<script setup>
defineProps({
  disabled: { type: Boolean, default: false },
})

defineEmits(['addToCart', 'buyNow'])
</script>
