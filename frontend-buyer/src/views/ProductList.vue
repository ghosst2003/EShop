<template>
  <div>
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-2xl font-extrabold text-gray-900 mb-6">Browse Products</h1>

      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Filters Sidebar (Desktop) -->
        <aside class="hidden lg:block w-64 shrink-0">
          <div class="bg-white rounded-xl p-6 sticky top-24 space-y-6">
            <!-- Category -->
            <div>
              <h3 class="font-bold text-gray-900 mb-3">Category</h3>
              <div class="space-y-2">
                <label v-for="cat in categories" :key="cat.id" class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" :value="cat.id" v-model="filters.category_id" @change="fetchProducts" class="accent-primary" />
                  <span class="text-sm text-gray-600">{{ cat.name_en }}</span>
                </label>
              </div>
            </div>

            <!-- Condition -->
            <div>
              <h3 class="font-bold text-gray-900 mb-3">Condition</h3>
              <div class="space-y-2">
                <label v-for="g in grades" :key="g.value" class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" :value="g.value" v-model="filters.conditions" @change="fetchProducts" class="accent-primary rounded" />
                  <span class="text-sm text-gray-600">{{ g.label }}</span>
                </label>
              </div>
            </div>

            <!-- Price Range -->
            <div>
              <h3 class="font-bold text-gray-900 mb-3">Price Range</h3>
              <div class="flex gap-2">
                <input
                  v-model.number="filters.price_min"
                  type="number"
                  placeholder="Min"
                  class="w-full border rounded-lg px-3 py-2 text-sm"
                  @change="fetchProducts"
                />
                <input
                  v-model.number="filters.price_max"
                  type="number"
                  placeholder="Max"
                  class="w-full border rounded-lg px-3 py-2 text-sm"
                  @change="fetchProducts"
                />
              </div>
            </div>

            <!-- Sort -->
            <div>
              <h3 class="font-bold text-gray-900 mb-3">Sort By</h3>
              <select v-model="filters.sort" @change="fetchProducts" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Newest First</option>
                <option value="price_asc">Price: Low → High</option>
                <option value="price_desc">Price: High → Low</option>
              </select>
            </div>
          </div>
        </aside>

        <!-- Mobile Filter Button -->
        <div class="lg:hidden">
          <button
            @click="showMobileFilter = !showMobileFilter"
            class="w-full bg-white rounded-xl px-4 py-3 text-sm font-semibold text-gray-700 flex items-center justify-between"
          >
            <span>Filters & Sort</span>
            <span>▼</span>
          </button>
          <div v-if="showMobileFilter" class="bg-white rounded-xl p-4 mt-2 space-y-4">
            <!-- Mobile filters same as desktop -->
            <div>
              <h3 class="font-bold text-sm mb-2">Category</h3>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  @click="filters.category_id = cat.id; fetchProducts()"
                  class="px-3 py-1 rounded-full text-xs"
                  :class="filters.category_id === cat.id ? 'bg-primary text-white' : 'bg-orange-light text-gray-600'"
                >
                  {{ cat.name_en }}
                </button>
              </div>
            </div>
            <div>
              <h3 class="font-bold text-sm mb-2">Sort</h3>
              <select v-model="filters.sort" @change="fetchProducts" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Newest</option>
                <option value="price_asc">Price ↑</option>
                <option value="price_desc">Price ↓</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Product Grid -->
        <div class="flex-1">
          <p class="text-sm text-gray-500 mb-4">{{ total }} products found</p>

          <!-- Desktop Grid -->
          <div class="hidden sm:grid sm:grid-cols-2 xl:grid-cols-3 gap-6">
            <ProductCard v-for="p in products" :key="p.id" :product="p" />
          </div>

          <!-- Mobile Single Column -->
          <div class="sm:hidden grid grid-cols-2 gap-3">
            <ProductCard v-for="p in products" :key="p.id" :product="p" />
          </div>

          <!-- Pagination -->
          <div class="flex justify-center mt-8">
            <button
              v-if="page > 1"
              @click="page--; fetchProducts()"
              class="px-4 py-2 bg-white rounded-lg text-sm font-semibold mr-2 hover:bg-orange-bg"
            >
              ← Prev
            </button>
            <button
              v-if="products.length === pageSize"
              @click="page++; fetchProducts()"
              class="px-4 py-2 bg-white rounded-lg text-sm font-semibold hover:bg-orange-bg"
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import ProductCard from '../components/ProductCard.vue'
import { getProducts, getCategories, searchProducts } from '../api'

const route = useRoute()
const products = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const showMobileFilter = ref(false)

const filters = reactive({
  category_id: null,
  conditions: [],
  price_min: null,
  price_max: null,
  sort: '',
})

const grades = [
  { value: 'new', label: 'New' },
  { value: 'like_new', label: 'Like New' },
  { value: 'good', label: 'Good' },
  { value: 'fair', label: 'Fair' },
  { value: 'poor', label: 'Poor' },
  { value: 'for_parts', label: 'For Parts' },
]

const fetchProducts = async () => {
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
    if (filters.conditions.length === 1) params.condition_grade = filters.conditions[0]
    if (filters.price_min) params.price_min = filters.price_min
    if (filters.price_max) params.price_max = filters.price_max
    if (filters.sort) params.sort = filters.sort

    const { data } = await getProducts(params)
    products.value = data.items
    total.value = data.total
  } catch (e) {
    console.error(e)
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
