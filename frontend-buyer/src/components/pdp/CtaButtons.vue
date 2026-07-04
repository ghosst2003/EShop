<template>
  <div class="flex rounded-full overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed" :class="{ 'pointer-events-none': disabled }">
    <button
      @click="$emit('addToCart')"
      class="flex-1 py-3.5 text-white font-bold text-sm text-center transition-colors"
      style="background: linear-gradient(135deg, #FFD000, #FF8800);"
    >
      🛒 Add to Cart
    </button>
    <button
      @click="$emit('buyNow')"
      class="flex-1 py-3.5 text-white font-bold text-sm text-center transition-colors"
      style="background: linear-gradient(135deg, #FF6600, #FF2200);"
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
