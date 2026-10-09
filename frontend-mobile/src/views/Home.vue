<template>
  <main class="home-shell min-h-screen pb-5">
    <header class="home-header safe-top">
      <div class="brand-row">
        <div class="brand-lockup"><span class="brand-mark">b.</span><div><strong>becool</strong><small>MARKET · EUROPE</small></div></div>
        <p class="brand-tagline">Good finds.<br /><span>Better prices.</span></p>
      </div>
      <form class="search-field" @submit.prevent="handleSearch">
        <label class="sr-only" for="home-search">Search the product catalogue</label>
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/></svg>
        <input id="home-search" v-model="searchQuery" type="search" list="home-search-suggestions" :placeholder="searchPlaceholder" />
        <datalist id="home-search-suggestions"><option v-for="suggestion in searchSuggestions" :key="suggestion" :value="suggestion" /></datalist>
        <button type="submit">Search</button>
      </form>
    </header>

    <section v-if="promoBanner" class="hero-offer" :style="promoBanner.style">
      <div class="hero-copy">
        <span v-if="promoBanner.tag" class="eyebrow">{{ promoBanner.tag }}</span>
        <h1>{{ promoBanner.title }}</h1>
        <p v-if="promoBanner.subtitle">{{ promoBanner.subtitle }}</p>
        <button class="hero-cta" :disabled="promoPending==='banner'" @click="activatePromo(promoBanner,'banner')">{{ promoPending==='banner'?'Opening…':promoBanner.cta }} <span aria-hidden="true">↗</span></button>
      </div>
      <span class="hero-orbit orbit-one"></span><span class="hero-orbit orbit-two"></span>
    </section>

    <section class="promo-section" v-if="promoGrid.length">
      <div class="section-heading compact-heading"><div><span class="eyebrow dark-eyebrow">CURRENT PROMOTIONS</span><h2>More ways to save</h2></div></div>
      <div class="promo-grid">
        <button v-for="(promo, index) in promoGrid" :key="promo.id" :disabled="promoPending===promo.id" @click="activatePromo(promo,promo.id)" class="promo-tile" :class="`promo-tone-${index % 3}`">
          <img v-if="promo.image && !failedPromoImages.has(promo.id)" :src="promo.image" :alt="promo.title" @error="failedPromoImages.add(promo.id)" />
          <span class="promo-label">{{ promo.title }}</span>
          <span v-if="promo.tag" class="promo-tag">{{ promo.tag }}</span>
          <span class="promo-action">{{ promoPending===promo.id?'Opening…':'Explore' }} <span aria-hidden="true">→</span></span>
        </button>
      </div>
    </section>

    <section class="products-section">
      <div class="section-heading">
        <div><span class="eyebrow dark-eyebrow">PRE-LOVED, WELL-CHOSEN</span><h2>Fresh finds</h2></div>
        <button class="see-all" @click="router.push('/browse')">Shop all <span>→</span></button>
      </div>
      <div class="product-grid">
        <router-link v-for="p in products" :key="p.id" class="product-card" :to="`/products/${p.slug}`">
          <div class="product-art" :class="{ 'has-photo': hasProductImage(p) }">
            <img v-if="hasProductImage(p)" :src="p.images[0].thumbnail_url || p.images[0].image_url" :alt="productTitle(p)" @error="failedProductImages.add(p.id)" />
            <template v-else><span class="art-overline">A GOOD FIND</span><span class="art-word">{{ productCategory(p) }}</span><span class="art-dot">b.</span></template>
            <span v-if="p.discount_pct" class="discount-stamp">−{{ p.discount_pct }}%</span>
          </div>
          <div class="product-copy">
            <span class="product-kicker">{{ englishText(p.platform, 'CURATED PICK') }}</span>
            <h3>{{ productTitle(p) }}</h3>
            <div class="product-price"><strong>€{{ p.sale_price }}</strong><del v-if="p.original_price">€{{ p.original_price }}</del></div>
            <div class="product-foot"><span>Quality finds, fair prices</span><span>↗</span></div>
          </div>
        </router-link>
      </div>
      <div v-if="loading" class="empty-state">Finding good things…</div>
      <div v-if="!loading && products.length === 0" class="empty-state">No products found.</div>
      <div v-if="loadingMore" class="product-grid loading-grid" aria-label="Loading more products">
        <div v-for="index in 4" :key="`skeleton-${index}`" class="product-skeleton" aria-hidden="true">
          <span></span><i></i><i></i>
        </div>
      </div>
      <div v-if="products.length > 0" ref="loadSentinel" class="feed-status" aria-live="polite">
        <button v-if="loadError" class="load-retry" @click="loadMore">Couldn’t load more · Tap to retry</button>
        <span v-else-if="!hasMore">You’ve seen every find.</span>
      </div>
    </section>
  </main>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getActiveFlashDeals, getActiveBanners, getCategories, getPromoItems, getProductById } from '../api'

const router = useRouter()
const products = ref([])
const flashDeals = ref([])
const banners = ref([])
const promoGrid = ref([])
const failedPromoImages = ref(new Set())
const failedProductImages = ref(new Set())
const loading = ref(true)
const loadingMore = ref(false)
const nextCursor = ref(null)
const hasMore = ref(true)
const loadError = ref(false)
const loadSentinel = ref(null)
const searchQuery = ref('')
const searchSuggestions = ref([])
const activeTab = ref('Recommended')
const promoPending = ref(null)
const feedBatchSize = 12
let feedObserver = null

const searchPlaceholder = ref('Search products...')

const hasProductImage = (product) => Boolean(
  product.images?.length && !failedProductImages.value.has(product.id)
)

const productDescription = (product) => {
  const description = product.description_en
  if (!description) return ''
  return description
    .replace(/<\/?(?:script|style)[^>]*>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim()
}

const englishText = (value, fallback = '') => {
  const text = String(value || '').trim()
  return text && !/[\u3400-\u9fff]/.test(text) ? text : fallback
}

const productCategory = (product) => {
  const name = englishText(product.category_name_en || product.category_name || product.category?.name_en || product.category?.name)
  if (name) return name.toUpperCase()
  const title = String(product.title_en || product.title || '').toLowerCase()
  if (/book|novel|science|algorithm|network|python|design pattern|jvm|sapiens|to live|hundred years/.test(title)) return 'BOOKS'
  if (/thermos|tumbler|glass|home|kitchen/.test(title)) return 'HOME'
  return 'PRE-LOVED'
}

const productTitle = (product) => englishText(product.title_en || product.title, 'Selected item')

// Nav tabs: first is always "Recommended", rest from categories API
const navTabs = ref([
  { label: 'Recommended', active: true, action: () => selectTab('Recommended') },
])

// Promotional banner
const promoBanner = ref(null)

// Update banner from banners API
const updateBanner = () => {
  const b = banners.value[0]
  const title = englishText(b?.title)
  if (!b || title.length < 3) return

  const from = b.bg_color_from || '#17483b'
  const to = b.bg_color_to || '#315044'
  const background = b.image_url
    ? `linear-gradient(90deg, ${from}dd, ${to}99), url(${b.image_url}) center / cover`
    : `linear-gradient(125deg, ${from}, ${to})`

  promoBanner.value = {
    tag: englishText(b.tag),
    title,
    subtitle: englishText(b.subtitle),
    cta: englishText(b.button_text, 'Shop Now'),
    style: { background },
    action: () => {
      if (/^https?:\/\//.test(b.button_link || '')) window.location.href = b.button_link
      else router.push(b.button_link || '/browse')
    },
  }
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.trim()
    const history = [query, ...searchSuggestions.value].filter((item, index, all) => item && all.indexOf(item) === index).slice(0, 8)
    searchSuggestions.value = history
    localStorage.setItem('esh_search_history', JSON.stringify(history))
    router.push({ path: '/browse', query: { q: query } })
  }
}
const activatePromo = async (promo, key) => {
  if (promoPending.value !== null) return
  promoPending.value = key
  try { await promo.action() } finally { promoPending.value = null }
}

const selectTab = (label, categoryId = null) => {
  activeTab.value = label
  navTabs.value.forEach(t => t.active = (t.label === label))
  if (label === 'Recommended') {
    router.push('/')
  } else {
    router.push({ path: '/browse', query: { category: categoryId } })
  }
}

const loadMore = async () => {
  if (loading.value || loadingMore.value || !hasMore.value || !nextCursor.value) return

  loadingMore.value = true
  loadError.value = false
  try {
    const res = await getProducts({ limit: feedBatchSize, cursor: nextCursor.value })
    const knownIds = new Set(products.value.map(product => product.id))
    const newProducts = (res.data.items || []).filter(product => !knownIds.has(product.id))
    products.value = [...products.value, ...newProducts]
    nextCursor.value = res.data.next_cursor || null
    hasMore.value = Boolean(res.data.has_more && nextCursor.value)
  } catch (e) {
    console.error('Failed to load more:', e)
    loadError.value = true
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  try {
    const [productsRes, dealsRes, bannersRes, categoriesRes, promoRes] = await Promise.all([
      getProducts({ limit: feedBatchSize }),
      getActiveFlashDeals(),
      getActiveBanners(),
      getCategories(),
      getPromoItems(),
    ])
    products.value = Array.from(
      new Map((productsRes.data.items || []).map(product => [product.id, product])).values()
    )
    let history = []
    try { history = JSON.parse(localStorage.getItem('esh_search_history') || '[]') } catch { history = [] }
    searchSuggestions.value = [...history, ...products.value.map(productTitle)].filter((item,index,all)=>item&&all.indexOf(item)===index).slice(0,12)
    nextCursor.value = productsRes.data.next_cursor || null
    hasMore.value = Boolean(productsRes.data.has_more && nextCursor.value)
    flashDeals.value = dealsRes.data || []
    banners.value = bannersRes.data || []

    // Build promo grid from API
    const promos = promoRes.data || []
    promoGrid.value = promos.map(p => {
      const promoId = p.id
      const item = {
        id: p.id,
      title: englishText(p.title, 'Featured'),
        icon: p.icon || '',
        image: p.image_url || null,
        tag: p.tag || '',
        tagClass: p.tag_class || '',
        productId: p.product_id || null,
        linkUrl: p.link_url || '',
      }
      item.action = async () => {
        if (item.productId) {
          // Fetch product to get slug, then navigate
          try {
            const res = await getProductById(item.productId)
            const slug = res.data.slug
            router.push(`/products/${slug}`)
          } catch (e) {
            console.error('Failed to load product:', e)
          }
        } else if (item.linkUrl) {
          if (item.linkUrl.startsWith('http')) {
            window.location.href = item.linkUrl
          } else {
            router.push(item.linkUrl)
          }
        }
      }
      return item
    })

    // Build nav tabs from categories (show English name only)
    const cats = categoriesRes.data || []
    cats.forEach(cat => {
      const label = englishText(cat.name_en || cat.name || cat.title)
      if (!label) return
      navTabs.value.push({
        label,
        active: false,
        action: () => selectTab(label, cat.id),
      })
    })

    updateBanner()
  } catch (e) {
    console.error('Failed to load:', e)
  } finally {
    loading.value = false
  }

  await nextTick()
  if (loadSentinel.value) {
    feedObserver = new IntersectionObserver(
      entries => {
        if (entries.some(entry => entry.isIntersecting)) loadMore()
      },
      { rootMargin: '320px 0px', threshold: 0.01 },
    )
    feedObserver.observe(loadSentinel.value)
  }
})

onUnmounted(() => {
  feedObserver?.disconnect()
})
</script>

<style scoped>
.home-shell { background: #f5f2e9; color: #183c32; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.home-header { padding: max(16px, env(safe-area-inset-top)) 20px 12px; background: #17483b; color: #fffdf6; border-radius: 0 0 25px 25px; }
.brand-row { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:16px; }
.brand-lockup { display:flex; align-items:center; gap:11px; flex-shrink:0; }
.brand-mark { width:42px; height:42px; display:grid; place-items:center; background:#d9f06a; border-radius:14px; color:#17483b; font-family:Georgia,serif; font-size:30px; font-weight:800; line-height:1; }
.brand-lockup strong { display:block; font-family:Georgia,serif; font-size:26px; letter-spacing:-.8px; line-height:1; }
.brand-lockup small { display:block; margin-top:4px; color:#b7c9bf; font-size:8px; font-weight:700; letter-spacing:1.7px; }
.brand-tagline { margin:0; color:#fffdf6; font-family:Georgia,serif; font-size:clamp(12px, 3.5vw, 15px); line-height:1.35; text-align:right; }
.brand-tagline span { color:#d9f06a; }
.search-field { height:46px; display:flex; align-items:center; gap:10px; padding:4px 5px 4px 14px; background:#fffdf6; border-radius:14px; color:#17483b; }
.search-field svg { width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:1.8; flex:none; }
.search-field input { width:100%; min-width:0; border:0; outline:0; background:transparent; color:#183c32; font-size:13px; }
.search-field input::placeholder { color:#89958e; }
.search-field input::-webkit-search-cancel-button { display:none; }
.search-field button { align-self:stretch; border-radius:11px; padding:0 15px; background:#d9f06a; color:#173f34; font-size:12px; font-weight:750; }
.hero-offer { position:relative; display:flex; min-height:180px; overflow:hidden; align-items:center; justify-content:space-between; margin:18px 16px 0; padding:23px 20px; border-radius:23px; color:#fffdf6; cursor:pointer; }
.hero-copy { position:relative; z-index:1; max-width:63%; }
.eyebrow { display:block; font-size:8px; line-height:1.2; font-weight:800; letter-spacing:1.8px; color:currentColor; opacity:.72; }
.hero-copy h1 { margin:10px 0 4px; font-family:Georgia,serif; font-size:27px; line-height:1.05; letter-spacing:-.8px; }
.hero-copy p { margin:0; color:currentColor; opacity:.85; font-size:11px; }
.hero-cta { display:flex; align-items:center; gap:12px; margin-top:15px; padding:9px 13px; border-radius:99px; background:#fffdf6; color:#17483b; font-size:10px; font-weight:700; }
.hero-cta span { font-size:14px; }
.hero-orbit { position:absolute; border:1px solid currentColor; border-radius:50%; pointer-events:none; opacity:.22; }
.orbit-one { width:218px; height:218px; right:-75px; top:-45px; }
.orbit-two { width:155px; height:155px; right:-45px; top:-15px; }
.promo-section, .products-section { margin-top:27px; }
.promo-section { padding:0 20px; }
.section-heading { display:flex; align-items:flex-end; justify-content:space-between; padding:0 20px; margin-bottom:13px; }
.compact-heading { padding:0; }
.dark-eyebrow { color:#758177; }
.section-heading h2 { margin:5px 0 0; color:#183c32; font-family:Georgia,serif; font-size:23px; font-weight:700; letter-spacing:-.5px; }
.heading-arrow { color:#738676; font-size:22px; }
.promo-grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:9px; }
.promo-tile { position:relative; display:flex; min-width:0; height:119px; flex-direction:column; align-items:flex-start; overflow:hidden; padding:12px 10px; border-radius:16px; text-align:left; }
.promo-tone-0 { background:#e7e4d8; color:#26473b; }
.promo-tone-1 { background:#f1d8c8; color:#7b442b; }
.promo-tone-2 { background:#d9e1d6; color:#315044; }
.promo-tile img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.3; }
.promo-label { position:relative; overflow:hidden; max-width:100%; font-family:Georgia,serif; font-size:clamp(14px, 4.2vw, 18px); font-weight:700; line-height:1.05; text-overflow:ellipsis; white-space:nowrap; }
.promo-tag { position:relative; max-width:100%; margin-top:8px; overflow:hidden; padding:4px 6px; border:1px solid currentColor; border-radius:99px; font-size:8px; font-weight:700; line-height:1; text-overflow:ellipsis; white-space:nowrap; }
.promo-action { position:absolute; bottom:12px; left:10px; color:currentColor; font-size:8px; font-weight:800; letter-spacing:.35px; }
.promo-action span { margin-left:3px; font-size:11px; }
.product-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; padding:0 16px; }
.product-card { overflow:hidden; border-radius:17px; background:#fffdf8; box-shadow:0 4px 18px rgba(37,55,43,.045); cursor:pointer; }
.product-art { position:relative; display:flex; aspect-ratio:1/1.03; overflow:hidden; flex-direction:column; justify-content:center; padding:14px; background:#e7e3d8; color:#42584a; }
.product-card:nth-child(4n+2) .product-art { background:#e7ded0; color:#705a46; }
.product-card:nth-child(4n+3) .product-art { background:#dce5dd; color:#405a4d; }
.product-card:nth-child(4n+4) .product-art { background:#eee3d7; color:#795842; }
.product-art.has-photo { padding:0; background:#e9e7df; }
.product-art img { width:100%; height:100%; object-fit:cover; }
.art-overline { font-size:7px; font-weight:800; letter-spacing:1.5px; opacity:.62; }
.art-word { max-width:100%; margin-top:6px; font-family:Georgia,serif; font-size:clamp(18px,6vw,27px); font-weight:700; line-height:.95; letter-spacing:-.8px; overflow-wrap:anywhere; }
.art-dot { position:absolute; right:12px; bottom:4px; font-family:Georgia,serif; font-size:73px; line-height:1; opacity:.08; }
.discount-stamp { position:absolute; left:9px; top:9px; padding:5px 7px; border-radius:99px; background:#d9f06a; color:#17483b; font-size:9px; font-weight:800; }
.product-copy { padding:11px 11px 10px; }
.product-kicker { display:block; margin-bottom:6px; color:#8a958b; font-size:7px; font-weight:800; letter-spacing:1.15px; }
.product-copy h3 { display:-webkit-box; min-height:34px; margin:0; overflow:hidden; color:#253a31; font-size:12px; font-weight:650; line-height:1.4; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
.product-price { display:flex; align-items:baseline; gap:7px; margin-top:9px; }
.product-price strong { color:#17483b; font-family:Georgia,serif; font-size:20px; line-height:1; }
.product-price del { color:#a7aaa2; font-size:10px; }
.product-foot { display:flex; align-items:center; justify-content:space-between; margin-top:10px; padding-top:8px; border-top:1px solid #efeee8; color:#8a958b; font-size:8px; }
.save-mark { color:#597164; font-size:16px; line-height:1; }
.see-all { display:flex; align-items:center; gap:5px; padding-bottom:3px; color:#597164; font-size:11px; font-weight:650; }
.see-all span { font-size:16px; }
.loading-grid { margin-top:12px; }
.product-skeleton { overflow:hidden; border-radius:17px; background:#fffdf8; }
.product-skeleton span, .product-skeleton i { display:block; background:linear-gradient(90deg,#e7e3d8 25%,#f3f0e8 50%,#e7e3d8 75%); background-size:200% 100%; animation:skeleton-shimmer 1.25s infinite linear; }
.product-skeleton span { aspect-ratio:1/1.03; }
.product-skeleton i { height:10px; margin:12px 11px 0; border-radius:99px; }
.product-skeleton i:last-child { width:55%; margin-bottom:14px; }
.feed-status { min-height:54px; display:flex; align-items:center; justify-content:center; padding:14px 20px 4px; color:#89958c; font-size:11px; }
.load-retry { padding:10px 15px; border:1px solid #cdd5c8; border-radius:99px; color:#315044; font-size:11px; font-weight:700; }
@keyframes skeleton-shimmer { to { background-position:-200% 0; } }
.empty-state { padding:40px 20px; text-align:center; color:#89958c; font-size:13px; }
@media (max-width:360px) { .hero-offer { padding:19px 15px; } .hero-copy h1 { font-size:23px; } .hero-price { width:82px; height:82px; } .product-grid { gap:9px; padding-inline:12px; } }
</style>
