<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <!-- Top Nav Tabs -->
    <div class="sticky top-0 z-40 bg-[#FFF6F0] safe-top">
      <div class="flex items-center gap-1 px-3 py-2 overflow-x-auto hide-scrollbar">
        <span
          v-for="tab in navTabs"
          :key="tab.label"
          @click="tab.action"
          class="shrink-0 text-[15px] font-medium py-1 px-1 tap-active whitespace-nowrap"
          :class="tab.label === activeTab ? 'text-orange-600 font-bold border-b-2 border-orange-600' : 'text-gray-600'"
        >
          {{ tab.label }}
          <span v-if="tab.badge" class="text-[8px] bg-red-500 text-white px-1 rounded ml-0.5 align-top">{{ tab.badge }}</span>
        </span>
      </div>

      <!-- Search Bar -->
      <div class="flex items-center gap-2 px-3 pb-3">
        <div class="flex-1 bg-white rounded-full h-9 flex items-center pr-2 border border-orange-200">
          <span class="pl-3 text-orange-400 text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </span>
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            type="text"
            :placeholder="searchPlaceholder"
            class="bg-transparent outline-none text-sm text-gray-700 flex-1 placeholder-gray-400"
          />
          <span class="text-gray-400 text-sm px-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          </span>
          <button @click="handleSearch" class="bg-gradient-to-r from-orange-500 to-red-500 text-white font-bold text-sm px-5 py-1.5 rounded-full">Search</button>
        </div>
      </div>
    </div>

    <!-- Promo Grid (3 columns) -->
    <div class="grid grid-cols-3 gap-1.5 px-3 py-2">
      <div
        v-for="(promo, i) in promoGrid"
        :key="promo.title"
        @click="promo.action"
        class="bg-[#FFF8F5] rounded-xl p-3 tap-active flex flex-col items-center gap-1.5"
      >
        <div class="w-full aspect-square rounded-lg overflow-hidden bg-[#F0EDE8] flex items-center justify-center">
          <img v-if="promo.image" :src="promo.image" class="w-full h-full object-cover" />
          <span v-else class="text-3xl">{{ promo.icon }}</span>
        </div>
        <span class="text-[11px] font-bold text-gray-800">{{ promo.title }}</span>
        <span v-if="promo.price" class="text-[11px] font-bold text-red-500">{{ promo.price }}</span>
        <span v-if="promo.tag" :class="promo.tagClass" class="text-[9px] font-bold px-1.5 py-0.5 rounded-full">{{ promo.tag }}</span>
      </div>
    </div>

    <!-- Promotional Banner -->
    <div
      v-if="promoBanner"
      @click="promoBanner.action"
      class="mx-3 mt-1 rounded-xl overflow-hidden tap-active"
      :class="promoBanner.bg"
    >
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2">
          <span class="text-white text-xl">{{ promoBanner.icon }}</span>
          <span class="text-white font-bold text-base">{{ promoBanner.title }}</span>
          <span class="text-white/80 text-xs">{{ promoBanner.subtitle }}</span>
        </div>
        <div class="bg-white/20 rounded-lg px-4 py-1.5 flex items-center gap-2">
          <span class="text-yellow-300 font-bold text-lg">€{{ promoBanner.amount }}</span>
          <span class="text-white font-bold text-sm">{{ promoBanner.cta }}</span>
        </div>
      </div>
    </div>

    <!-- Recommended Products - 2 Column Waterfall -->
    <div class="px-3 py-3">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-extrabold text-gray-800">
          <span class="text-orange-500">♥</span> Recommended
        </h2>
        <router-link to="/browse" class="text-gray-400 text-xs">View All →</router-link>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div
          v-for="(p, i) in products"
          :key="p.id"
          @click="router.push(`/products/${p.slug}`)"
          class="bg-white rounded-xl overflow-hidden tap-active"
        >
          <!-- Image -->
          <div class="relative aspect-square overflow-hidden bg-[#F0EDE8]">
            <img
              v-if="p.images?.length"
              :src="p.images[0].thumbnail_url || p.images[0].image_url"
              :alt="p.title_en || p.title"
              class="w-full h-full object-cover"
              :class="i % 3 === 0 ? 'aspect-[3/4]' : 'aspect-square'"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-4xl">
              📦
            </div>
            <!-- Overlay text on image -->
            <div v-if="p.description" class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-2 pt-6">
              <p class="text-white text-[10px] line-clamp-2">{{ p.description }}</p>
            </div>
          </div>

          <!-- Info -->
          <div class="p-2.5">
            <p class="text-[13px] text-gray-800 line-clamp-2 leading-snug">
              <span v-if="p.platform" class="text-red-500 font-bold mr-1">{{ p.platform }}</span>
              {{ p.title_en || p.title }}
            </p>
            <p v-if="p.promo_text" class="text-xs text-orange-500 mt-1">{{ p.promo_text }}</p>
            <div class="flex items-baseline gap-1 mt-1.5">
              <span class="text-xs text-red-500 font-bold">€</span>
              <span class="text-xl font-extrabold text-red-500">{{ p.sale_price }}</span>
              <span v-if="p.original_price" class="text-[10px] text-gray-400 line-through">€{{ p.original_price }}</span>
            </div>
            <div class="flex items-center justify-between mt-1">
              <span class="text-[10px] text-gray-400">
                <span class="text-red-500">After discount</span>
                <span class="ml-1">Hot {{ p.sales_count || '2000' }}+ sold</span>
              </span>
              <span v-if="p.discount_pct" class="text-[9px] font-bold text-red-500 bg-red-50 px-1 rounded">-{{ p.discount_pct }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
      <div v-if="!loading && products.length === 0" class="text-center py-12 text-gray-400">No products found.</div>

      <div v-if="products.length > 0" class="text-center mt-6">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="bg-white text-orange-500 font-semibold px-8 py-3 rounded-full border border-orange-200 tap-active disabled:opacity-50 text-sm"
        >
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>

    <div class="h-4"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getActiveFlashDeals, getActiveBanners, getCategories } from '../api'

const router = useRouter()
const products = ref([])
const flashDeals = ref([])
const banners = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const currentPage = ref(1)
const searchQuery = ref('')
const activeTab = ref('Recommended')

const searchPlaceholder = ref('Search products...')

// Nav tabs: first is always "Recommended", rest from categories API
const navTabs = ref([
  { label: 'Recommended', active: true, action: () => selectTab('Recommended') },
])

// Promo grid data (3 columns)
const promoGrid = ref([
  {
    title: 'Live',
    icon: '📺',
    image: null,
    action: () => router.push('/browse?live=1'),
  },
  {
    title: 'Subsidy',
    icon: '🎁',
    tag: 'Gov Grant',
    tagClass: 'bg-green-100 text-green-600',
    price: null,
    action: () => router.push('/browse?subsidy=1'),
  },
  {
    title: 'Flash Sale',
    icon: '⚡',
    tag: 'Limited',
    tagClass: 'bg-orange-100 text-orange-600',
    price: null,
    action: () => router.push('/browse?flash=1'),
  },
])

// Update promo grid with flash deal data
const updatePromoGrid = () => {
  if (flashDeals.value.length > 0) {
    const deal = flashDeals.value[0]
    promoGrid.value[0] = {
      title: deal.title_en || deal.title || 'Hot Deal',
      icon: '🔥',
      image: deal.image_url || null,
      price: `€${deal.deal_price || deal.sale_price}`,
      tag: 'Top Seller',
      tagClass: 'bg-red-500 text-white',
      action: () => router.push(`/products/${deal.slug}`),
    }
  }
  if (flashDeals.value.length > 1) {
    const deal = flashDeals.value[1]
    promoGrid.value[1] = {
      title: deal.title_en || deal.title || 'Best Value',
      icon: '💰',
      image: deal.image_url || null,
      price: `€${deal.deal_price || deal.sale_price}`,
      tag: 'Subsidy',
      tagClass: 'bg-yellow-400 text-yellow-800',
      action: () => router.push(`/products/${deal.slug}`),
    }
  }
  if (flashDeals.value.length > 2) {
    const deal = flashDeals.value[2]
    promoGrid.value[2] = {
      title: deal.title_en || deal.title || 'Flash Deal',
      icon: '⏰',
      image: deal.image_url || null,
      price: `€${deal.deal_price || deal.sale_price}`,
      tag: 'Flash',
      tagClass: 'bg-orange-500 text-white',
      action: () => router.push(`/products/${deal.slug}`),
    }
  }
}

// Promotional banner
const promoBanner = ref({
  icon: '📢',
  title: 'Special Offer',
  subtitle: 'Limited time deals',
  amount: '5',
  cta: 'Claim Now',
  bg: 'bg-gradient-to-r from-red-500 to-red-600',
  action: () => router.push('/browse?sale=1'),
})

// Update banner from banners API
const updateBanner = () => {
  if (banners.value.length > 0) {
    const b = banners.value[0]
    promoBanner.value = {
      icon: '',
      title: b.title || 'Special Offer',
      subtitle: b.subtitle || '',
      amount: '5',
      cta: 'Claim Now',
      bg: 'bg-gradient-to-r from-red-500 to-red-600',
      action: () => router.push(b.button_link || '/browse'),
    }
  }
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/browse', query: { q: searchQuery.value } })
  }
}

const selectTab = (label) => {
  activeTab.value = label
  navTabs.value.forEach(t => t.active = (t.label === label))
  if (label === 'Recommended') {
    router.push('/')
  } else {
    router.push({ path: '/browse', query: { category: label } })
  }
}

const loadMore = async () => {
  loadingMore.value = true
  try {
    const res = await getProducts({ page: currentPage.value + 1, page_size: 10 })
    products.value = [...products.value, ...res.data.items]
    currentPage.value++
  } catch (e) {
    console.error('Failed to load more:', e)
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  try {
    const [productsRes, dealsRes, bannersRes, categoriesRes] = await Promise.all([
      getProducts({ page: 1, page_size: 20 }),
      getActiveFlashDeals(),
      getActiveBanners(),
      getCategories(),
    ])
    products.value = productsRes.data.items || []
    flashDeals.value = dealsRes.data || []
    banners.value = bannersRes.data || []

    // Build nav tabs from categories (show English name only)
    const cats = categoriesRes.data || []
    cats.forEach(cat => {
      const label = cat.name_en || cat.name || cat.title
      navTabs.value.push({
        label,
        active: false,
        action: () => selectTab(label),
      })
    })

    updatePromoGrid()
    updateBanner()
  } catch (e) {
    console.error('Failed to load:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@supports (padding-top: env(safe-area-inset-top)) {
  .safe-top {
    padding-top: env(safe-area-inset-top);
  }
}
</style>
