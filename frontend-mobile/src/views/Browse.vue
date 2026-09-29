<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <!-- Header -->
    <div class="sticky top-0 z-40 bg-white safe-top border-b border-gray-100">
      <div class="flex items-center gap-3 px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1">Browse</h1>
        <button @click="showFilter = !showFilter" class="text-lg tap-active">
          {{ showFilter ? '✕' : '' }}
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div v-if="showFilter" class="bg-white px-4 py-3 border-b border-gray-100">
      <div class="flex gap-2 overflow-x-auto hide-scrollbar">
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="filters.category_id = filters.category_id === cat.id ? null : cat.id; fetchProducts()"
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium tap-active"
          :class="filters.category_id === cat.id ? 'bg-primary text-white' : 'bg-[#F5F5F5] text-gray-600'"
        >
          {{ cat.name_en }}
        </button>
      </div>
      <div class="flex gap-2 mt-2">
        <select v-model="filters.sort" @change="fetchProducts" class="flex-1 bg-[#F5F5F5] rounded-lg px-3 py-2 text-xs">
          <option value="">Newest</option>
          <option value="price_asc">Price ↑</option>
          <option value="price_desc">Price ↓</option>
        </select>
        <select v-model="filters.condition" @change="fetchProducts" class="flex-1 bg-[#F5F5F5] rounded-lg px-3 py-2 text-xs">
          <option value="">All Conditions</option>
          <option value="new">New</option>
          <option value="like_new">Like New</option>
          <option value="good">Good</option>
        </select>
      </div>
    </div>

    <!-- Product Grid -->
    <div class="px-4 py-4">
      <p class="text-xs text-gray-500 mb-3">{{ total }} products</p>

      <div class="grid grid-cols-2 gap-3">
        <MobileProductCard v-for="p in products" :key="p.id" :product="p" />
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
      <div v-if="!loading && products.length === 0" class="text-center py-12 text-gray-400">No products found.</div>

      <!-- Load More -->
      <div v-if="products.length > 0" class="text-center mt-4">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="bg-white text-primary font-semibold px-8 py-3 rounded-full border border-orange-light tap-active disabled:opacity-50"
        >
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import MobileProductCard from '../components/MobileProductCard.vue'
import { getProducts, getCategories, searchProducts } from '../api'

const route = useRoute()
const products = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const showFilter = ref(false)
const loading = ref(true)
const loadingMore = ref(false)

const filters = reactive({
  category_id: null,
  condition: '',
  sort: '',
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (route.query.q) {
      const { data } = await searchProducts({ q: route.query.q, ...params })
      products.value = data.items
      total.value = data.total
      return
    }
    if (filters.category_id) params.category_id = filters.category_id
    if (route.query.category) params.category_id = route.query.category
    if (filters.condition) params.condition_grade = filters.condition
    if (filters.sort) params.sort = filters.sort

    const { data } = await getProducts(params)
    products.value = data.items
    total.value = data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  loadingMore.value = true
  try {
    const params = { page: page.value + 1, page_size: pageSize }
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.condition) params.condition_grade = filters.condition
    if (filters.sort) params.sort = filters.sort
    if (route.query.q) {
      const { data } = await searchProducts({ q: route.query.q, ...params })
      products.value = [...products.value, ...data.items]
    } else {
      const { data } = await getProducts(params)
      products.value = [...products.value, ...data.items]
    }
    page.value++
  } catch (e) {
    console.error(e)
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch {}
  fetchProducts()
})

watch(() => route.query.q, () => { page.value = 1; fetchProducts() })
</script>
