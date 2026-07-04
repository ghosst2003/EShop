<template>
  <div>
    <Navbar />

    <!-- ===== MAIN CONTENT AREA ===== -->
    <div class="max-w-[1440px] mx-auto px-10 pt-4">
      <div class="flex gap-4">

        <!-- LEFT: Category Sidebar -->
        <aside class="hidden lg:block w-[240px] shrink-0 bg-white rounded-xl overflow-hidden">
          <div class="p-4 pb-2">
            <h3 class="text-[14px] font-bold text-gray-800">📂 All Categories</h3>
          </div>
          <nav class="px-2">
            <a
              v-for="(cat, i) in categories"
              :key="cat.id"
              href="#"
              @click.prevent="filterByCategory(cat.id)"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-[12px] transition group"
              :class="activeCategory === cat.id ? 'bg-orange-bg text-primary font-bold' : 'text-gray-700 hover:bg-gray-50'"
            >
              <span class="text-base">{{ catIcons[i] || '' }}</span>
              <span>{{ cat.name_en }}</span>
              <span v-if="i === 0" class="ml-auto text-[8px] font-bold text-white bg-primary px-2 py-0.5 rounded-full">HOT</span>
            </a>
          </nav>
        </aside>

        <!-- CENTER: Banner -->
        <div class="flex-1 min-w-0">
          <div
            v-for="(banner, idx) in banners"
            :key="banner.id"
            v-show="currentBanner === idx"
            class="relative rounded-xl overflow-hidden"
            :style="banner.image_url
              ? { backgroundImage: `url(${banner.image_url})`, backgroundSize: 'cover', backgroundPosition: 'center', height: '440px' }
              : { background: `linear-gradient(135deg, ${banner.bg_color_from}, ${banner.bg_color_to})`, height: '440px' }"
          >
            <!-- 渐变色光晕效果（仅无图片时显示） -->
            <template v-if="!banner.image_url">
              <div class="absolute top-10 right-20 w-[400px] h-[350px] rounded-full opacity-40" :style="{ backgroundColor: banner.bg_color_to }"></div>
              <div class="absolute bottom-10 right-40 w-[250px] h-[200px] rounded-full opacity-30" :style="{ backgroundColor: banner.bg_color_from }"></div>
            </template>

            <div class="relative z-10 p-10 h-full flex flex-col justify-between">
              <div>
                <span v-if="banner.tag" class="text-white/80 text-[13px] font-bold tracking-wide">{{ banner.tag }}</span>
                <h1 class="text-white text-[48px] font-black leading-tight mt-4">{{ banner.title }}</h1>
                <p v-if="banner.subtitle" class="text-white/70 text-base mt-4">{{ banner.subtitle }}</p>
                <router-link :to="banner.button_link" class="inline-block bg-white font-bold px-8 py-3 rounded-full mt-6 transition text-base"
                  :style="{ color: banner.bg_color_from }">
                  {{ banner.button_text }} →
                </router-link>
              </div>

              <!-- Carousel dots -->
              <div v-if="banners.length > 1" class="flex gap-3 mt-4">
                <span
                  v-for="(b, i) in banners" :key="b.id"
                  class="w-2 h-2 rounded-full cursor-pointer transition"
                  :class="i === currentBanner ? 'bg-white' : 'bg-white/40'"
                  @click="currentBanner = i"
                ></span>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Promo Cards -->
        <div class="hidden xl:flex flex-col gap-3 w-[280px] shrink-0">
          <!-- Flash Deals Card -->
          <div class="bg-white rounded-xl p-5 flex-1">
            <h3 class="text-[14px] font-extrabold text-primary"> Flash Deals</h3>
            <div class="flex items-center gap-2 mt-2">
              <span class="text-xs text-gray-400">Ends in</span>
              <div class="flex gap-1">
                <span class="bg-gray-800 text-white text-xs font-bold w-6 h-6 rounded flex items-center justify-center">{{ hours }}</span>
                <span class="text-primary font-bold">:</span>
                <span class="bg-gray-800 text-white text-xs font-bold w-6 h-6 rounded flex items-center justify-center">{{ minutes }}</span>
                <span class="text-primary font-bold">:</span>
                <span class="bg-gray-800 text-white text-xs font-bold w-6 h-6 rounded flex items-center justify-center">{{ seconds }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-3 text-2xl">👜 🎧 ⌚</div>
            <router-link to="/browse" class="block bg-primary text-white text-sm font-semibold text-center py-2 rounded-full mt-3 hover:bg-primary-light transition">
              Grab Deals
            </router-link>
          </div>

          <!-- New User Card -->
          <div class="bg-white rounded-xl p-5 flex-1">
            <div class="text-3xl text-center mb-2"></div>
            <h3 class="text-[15px] font-bold text-gray-800 text-center">New User Bonus</h3>
            <p class="text-xs text-gray-500 text-center mt-1">Get €5 off your first order!</p>
            <button class="block w-full bg-orange-bg text-primary text-sm font-semibold text-center py-2 rounded-full mt-3 hover:bg-orange-light transition">
              Claim Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== CATEGORY SHORTCUTS ===== -->
    <section class="bg-white mt-3">
      <div class="max-w-[1440px] mx-auto px-10 py-5">
        <div class="grid grid-cols-6 md:grid-cols-12 gap-3">
          <a
            v-for="(sc, i) in shortcuts"
            :key="sc.name"
            href="#"
            class="flex flex-col items-center gap-1.5 py-3 rounded-xl transition group"
            :class="i === 0 ? 'bg-[#FFF0E8]' : 'bg-gray-50 hover:bg-gray-100'"
          >
            <span class="text-[28px]">{{ sc.icon }}</span>
            <span class="text-[11px] font-semibold text-gray-700">{{ sc.name }}</span>
          </a>
        </div>
      </div>
    </section>

    <!-- ===== FLASH DEALS ===== -->
    <section id="flash-deals-section" class="bg-white mt-3">
      <div class="max-w-[1440px] mx-auto px-10 py-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-extrabold text-primary"> Flash Deals</h2>
            <div class="flex items-center gap-1">
              <span class="bg-gray-800 text-white text-sm font-bold w-7 h-7 rounded flex items-center justify-center">{{ hours }}</span>
              <span class="text-primary font-bold mx-0.5">:</span>
              <span class="bg-gray-800 text-white text-sm font-bold w-7 h-7 rounded flex items-center justify-center">{{ minutes }}</span>
              <span class="text-primary font-bold mx-0.5">:</span>
              <span class="bg-gray-800 text-white text-sm font-bold w-7 h-7 rounded flex items-center justify-center">{{ seconds }}</span>
            </div>
          </div>
          <router-link to="/browse" class="text-primary text-sm font-semibold hover:underline">View All Deals →</router-link>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <router-link
            v-for="item in flashDeals"
            :key="item.id"
            :to="`/products/${item.slug}`"
            class="bg-[#F8F8F8] rounded-xl overflow-hidden group cursor-pointer block"
          >
            <div class="aspect-square bg-[#EEEEEE] flex items-center justify-center group-hover:scale-105 transition-transform overflow-hidden">
              <img
                v-if="item.image_url"
                :src="item.image_url"
                :alt="item.title_en"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-5xl text-gray-300">📦</span>
            </div>
            <div class="p-3">
              <p class="text-[13px] font-semibold text-gray-800 truncate">{{ item.title_en || item.title }}</p>
              <div class="flex items-baseline gap-2 mt-1">
                <span class="text-lg font-extrabold text-primary">€{{ item.deal_price }}</span>
                <span class="text-xs text-gray-400 line-through">€{{ item.original_price }}</span>
              </div>
              <div class="flex items-center justify-between mt-1.5">
                <span class="text-[11px] font-bold text-white bg-primary px-2 py-0.5 rounded">-{{ item.discount_pct }}%</span>
                <span class="text-[11px] text-gray-400">Deal</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== RECOMMENDED PRODUCTS ===== -->
    <section class="mt-3">
      <div class="max-w-[1440px] mx-auto px-10 py-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-extrabold text-gray-800">✨ Recommended For You</h2>
            <div class="w-[100px] h-[3px] bg-primary rounded-full mt-2"></div>
          </div>
        </div>

        <!-- Product Grid - 5 columns on desktop, 2 on mobile -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <ProductCard v-for="p in products" :key="p.id" :product="p" />
        </div>

        <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
        <div v-if="!loading && products.length === 0" class="text-center py-12 text-gray-400">No products found.</div>

        <!-- Load More -->
        <div v-if="products.length > 0" class="text-center mt-8">
          <button
            @click="loadMore"
            :disabled="loadingMore"
            class="bg-white text-primary font-semibold px-12 py-3 rounded-full border border-orange-light hover:bg-orange-bg transition disabled:opacity-50"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Products' }}
          </button>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import ProductCard from '../components/ProductCard.vue'
import { getProducts, getCategories, getActiveFlashDeals, getActiveBanners } from '../api'

const router = useRouter()
const products = ref([])
const categories = ref([])
const flashDeals = ref([])
const banners = ref([])
const currentBanner = ref(0)
const loading = ref(true)
const loadingMore = ref(false)
const activeCategory = ref(null)
const currentPage = ref(1)

// Category icons
const catIcons = ['', '', '', '', '', '', '', '', '', '', '', '']

// Category shortcuts
const shortcuts = [
  { name: 'Deals', icon: '️' },
  { name: 'Hot Sales', icon: '' },
  { name: 'Fashion', icon: '' },
  { name: 'Phones', icon: '' },
  { name: 'Computers', icon: '' },
  { name: 'Home', icon: '' },
  { name: 'Beauty', icon: '' },
  { name: 'Shoes', icon: '' },
  { name: 'Gaming', icon: '' },
  { name: 'Cameras', icon: '' },
  { name: 'Watches', icon: '' },
  { name: 'Toys', icon: '' },
]

// Flash deals - loaded from API
// flashDeals ref is initialized above, fetched in onMounted

// Countdown timer
const hours = ref('02')
const minutes = ref('45')
const seconds = ref('18')
let timer = null
let bannerTimer = null
let totalSeconds = 2 * 3600 + 45 * 60 + 18  // default fallback

const filterByCategory = (catId) => {
  activeCategory.value = activeCategory.value === catId ? null : catId
  router.push({ path: '/browse', query: { category: activeCategory.value || undefined } })
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
    const [productsRes, categoriesRes, dealsRes, bannersRes] = await Promise.all([
      getProducts({ page: 1, page_size: 10 }),
      getCategories(),
      getActiveFlashDeals(),
      getActiveBanners(),
    ])
    products.value = productsRes.data.items
    categories.value = categoriesRes.data
    flashDeals.value = dealsRes.data || []
    banners.value = bannersRes.data || []

    // 如果有闪购活动，使用最早结束的时间作为倒计时基准
    if (flashDeals.value.length > 0) {
      const earliestEnd = new Date(
        Math.min(...flashDeals.value.map(d => new Date(d.end_time).getTime()))
      )
      const now = new Date()
      totalSeconds = Math.max(0, Math.floor((earliestEnd - now) / 1000))
    }
  } catch (e) {
    console.error('Failed to load:', e)
  } finally {
    loading.value = false
  }

  // Start countdown timer
  timer = setInterval(() => {
    if (totalSeconds <= 0) {
      totalSeconds = 24 * 3600
    }
    totalSeconds--
    const h = Math.floor(totalSeconds / 3600)
    const m = Math.floor((totalSeconds % 3600) / 60)
    const s = totalSeconds % 60
    hours.value = String(h).padStart(2, '0')
    minutes.value = String(m).padStart(2, '0')
    seconds.value = String(s).padStart(2, '0')
  }, 1000)

  // Banner auto-rotation
  if (banners.value.length > 1) {
    bannerTimer = setInterval(() => {
      currentBanner.value = (currentBanner.value + 1) % banners.value.length
    }, 5000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (bannerTimer) clearInterval(bannerTimer)
})
</script>
