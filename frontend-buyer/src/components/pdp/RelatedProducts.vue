<template>
  <div v-if="products.length" class="mt-8">
    <h2 class="text-lg font-bold text-gray-900 mb-4">You might also like</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      <ProductCard
        v-for="p in products"
        :key="p.id"
        :product="p"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProducts } from '@/api'
import ProductCard from '@/components/ProductCard.vue'

const props = defineProps({
  currentSlug: { type: String, required: true },
  categoryId: { type: [Number, String], default: null },
})

const products = ref([])

onMounted(async () => {
  try {
    const params = { limit: 5 }
    if (props.categoryId) params.category_id = props.categoryId

    const { data } = await getProducts(params)
    products.value = (data || []).filter(p => p.slug !== props.currentSlug)
  } catch (e) {
    console.error('Failed to load related products:', e)
  }
})
</script>
