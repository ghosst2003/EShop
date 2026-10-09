<template>
  <div>
    <div v-if="product" class="detail-page">
    <!-- Branded Header -->
    <div class="detail-header safe-top">
      <button @click="$router.back()" class="header-control tap-active" aria-label="Go back">
        ←
      </button>
      <span class="detail-brand-mark">b.</span>
      <div class="header-actions">
        <button class="header-control tap-active" aria-label="Share product" :disabled="sharePending" @click="prepareShare">{{ sharePending ? '…' : '↗' }}</button>
        <button class="header-control header-save tap-active" :class="{ saved: isSaved }" :aria-label="isSaved ? 'Remove from saved products' : 'Save product'" :aria-pressed="isSaved" @click="toggleSaved">{{ isSaved ? '♥' : '♡' }}</button>
      </div>
      <span class="sr-only" aria-live="polite">{{ saveAnnouncement }}</span>
    </div>

    <div v-if="sharePanel" class="share-panel" role="dialog" aria-modal="true" aria-labelledby="share-title">
      <button type="button" class="share-close" aria-label="Close share options" @click="sharePanel=false">×</button>
      <span class="card-kicker">SAFE SHARE LINK</span><h2 id="share-title">Share this find</h2>
      <p>The link uses a random public token and contains no product ID or internal slug.</p>
      <div class="share-actions"><a :href="whatsappUrl" target="_blank" rel="noopener noreferrer">WhatsApp</a><button type="button" @click="shareViaDevice">More apps</button><button type="button" @click="copyShareLink">Copy link</button></div>
      <p v-if="shareAnnouncement" class="share-feedback" role="status">{{ shareAnnouncement }}</p>
    </div>

    <!-- Image Gallery -->
    <div class="relative">
      <div
        class="gallery-stage"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      >
        <Transition v-if="product.images?.length" name="gallery-fade" mode="out-in">
          <img
            :key="currentImage"
            :src="product.images[currentImage].image_url"
            :alt="`${product.title_en || product.title} · image ${currentImage + 1}`"
            class="gallery-image"
          />
        </Transition>
        <span v-else class="gallery-empty"></span>

        <template v-if="product.images?.length > 1">
          <button
            type="button"
            class="gallery-arrow gallery-arrow-left"
            aria-label="Previous image"
            @click.stop="previousImage"
          >
            ‹
          </button>
          <button
            type="button"
            class="gallery-arrow gallery-arrow-right"
            aria-label="Next image"
            @click.stop="nextImage"
          >
            ›
          </button>
          <span class="gallery-counter" aria-live="polite">{{ currentImage + 1 }} / {{ product.images.length }}</span>
        </template>
      </div>
      <!-- Image dots -->
      <div v-if="product.images?.length > 1" class="gallery-dots">
        <button
          v-for="(_, i) in product.images"
          :key="i"
          type="button"
          :aria-label="`Show image ${i + 1}`"
          class="gallery-dot"
          :class="{ active: i === currentImage }"
          @click="currentImage = i"
        ></button>
      </div>
    </div>

    <!-- Content -->
    <div class="detail-content">
      <div class="product-summary">
      <span class="detail-eyebrow">PRE-LOVED · WELL-CHOSEN</span>
      <!-- Price -->
      <div class="price-row">
        <span class="sale-price">€{{ product.sale_price }}</span>
        <span v-if="product.original_price" class="original-price">€{{ product.original_price }}</span>
        <span v-if="discountPercent" class="discount-pill">{{ discountPercent }}</span>
      </div>

      <!-- Title -->
      <h1 class="product-title">{{ product.title_en || product.title }}</h1>
      <p v-if="product.brand" class="product-brand">{{ product.brand }}</p>

      <!-- Condition -->
      <div class="product-chips">
        <span :class="badgeClasses" class="condition-chip">
          {{ conditionLabel }}
        </span>
        <span v-if="product.auto_manage_stock && product.stock_quantity > 0" class="stock-chip">{{ product.stock_quantity }} available</span>
        <span v-else-if="product.auto_manage_stock" class="stock-chip out-of-stock">Out of stock</span>
      </div>

      <!-- Origin -->
      <div v-if="product.origin_country_code" class="origin-line">
        <span>{{ originFlag }}</span>
        <span>Ships from {{ originName }}</span>
      </div>
      <p v-if="product.condition_note" class="condition-note">{{ product.condition_note }}</p>
      </div>
    </div>

    <!-- Shipping Info -->
    <div class="info-card">
      <span class="card-kicker">DELIVERY</span>
      <h3>Shipping</h3>
      <div class="card-copy">
        <p v-if="detailsLoading" class="info-lead">Checking delivery to {{ deliveryCountry }}…</p>
        <p v-else-if="shippingOptions.length" class="info-lead">From €{{ lowestShipping }} to {{ deliveryCountry }}</p>
        <p v-else class="info-lead">Calculated for your address at checkout.</p>
        <p v-if="product.origin_country_code">Ships from {{ originName }} {{ originFlag }}</p>
        <p v-if="shippingSettings?.show_combined_shipping">{{ shippingSettings.combined_shipping_text }}</p>
        <p v-if="shippingSettings?.show_import_fees">{{ shippingSettings.import_fees_text }}</p>
        <ul v-if="shippingNotes.length" class="info-list">
          <li v-for="note in shippingNotes" :key="note.id">
            <strong>{{ note.title_en || note.title }}</strong>
            <span>{{ note.content_en || note.content }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Returns and payments -->
    <div class="info-card confidence-card">
      <span class="card-kicker">BUY WITH CONFIDENCE</span>
      <h3>Returns & payment</h3>
      <p v-if="detailsLoading" class="policy-note">Loading return and payment details…</p>
      <div v-else-if="returnPolicy" class="confidence-grid">
        <div>
          <strong>{{ returnPolicy.return_days }} days</strong>
          <span>Return window</span>
        </div>
        <div>
          <strong>{{ returnShippingLabel }}</strong>
          <span>Return shipping</span>
        </div>
      </div>
      <p v-else class="policy-note">Return policy details are unavailable right now.</p>
      <p v-if="returnPolicy?.restocking_fee_percent" class="policy-note">
        {{ returnPolicy.restocking_fee_percent }}% restocking fee may apply.
      </p>
      <p v-if="returnPolicy?.description_en || returnPolicy?.description" class="policy-note">
        {{ returnPolicy.description_en || returnPolicy.description }}
      </p>
      <div v-if="paymentMethods.length" class="payment-methods" aria-label="Accepted payment methods">
        <span v-for="method in paymentMethods" :key="method.id">{{ method.name_en || method.name }}</span>
      </div>
    </div>

    <!-- Product facts -->
    <div class="info-card">
      <span class="card-kicker">PRODUCT FACTS</span>
      <h3>At a glance</h3>
      <dl class="facts-list">
        <div v-for="fact in productFacts" :key="fact.label">
          <dt>{{ fact.label }}</dt>
          <dd>{{ fact.value }}</dd>
        </div>
      </dl>
    </div>

    <!-- Description -->
    <div class="info-card">
      <span class="card-kicker">THE DETAILS</span>
      <h3>Description</h3>
      <div
        class="product-description card-copy"
        :class="{ collapsed: hasLongDescription && !descriptionExpanded }"
        v-html="product.description_en || product.description"
      ></div>
      <button
        v-if="hasLongDescription"
        type="button"
        class="read-more"
        :aria-expanded="descriptionExpanded"
        @click="descriptionExpanded = !descriptionExpanded"
      >
        {{ descriptionExpanded ? 'Show less' : 'Read more' }}
      </button>
    </div>

    <div class="info-card review-card">
      <span class="card-kicker">COMMUNITY NOTES</span>
      <div class="review-heading">
        <h3>Reviews</h3>
        <strong v-if="reviews.review_count">★ {{ reviews.average_rating }} · {{ reviews.review_count }}</strong>
      </div>
      <p v-if="!reviews.review_count" class="policy-note">No reviews yet. Be the first to share a useful note.</p>
      <article v-for="review in reviews.reviews" :key="review.id" class="review-item">
        <div><strong>{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5-review.rating) }}</strong><span>{{ review.reviewer_name }}<em v-if="review.verified_purchase">Verified purchase</em></span></div>
        <h4 v-if="review.title">{{ review.title }}</h4><p v-if="review.comment">{{ review.comment }}</p>
      </article>
      <button v-if="isAuthenticated && !showReviewForm" type="button" class="read-more" @click="showReviewForm=true">Write a review</button>
      <router-link v-else-if="!isAuthenticated" class="review-signin" :to="{path:'/login',query:{redirect:route.fullPath}}">Sign in to write a review</router-link>
      <form v-if="showReviewForm" class="review-form" @submit.prevent="sendReview">
        <label>Rating<select v-model.number="reviewForm.rating" required><option v-for="rating in 5" :key="rating" :value="rating">{{ rating }} {{ rating===1?'star':'stars' }}</option></select></label>
        <label>Title<input v-model.trim="reviewForm.title" maxlength="120" placeholder="Sum it up" /></label>
        <label>Your review<textarea v-model.trim="reviewForm.comment" maxlength="2000" placeholder="What should another shopper know?"></textarea></label>
        <p v-if="reviewMessage" :class="{error:reviewError}" role="status">{{ reviewMessage }}</p>
        <button type="submit" class="review-submit" :disabled="reviewPending">{{ reviewPending?'Publishing…':'Publish review' }}</button>
      </form>
    </div>

    <section v-if="relatedProducts.length" class="recommendation-section">
      <span class="card-kicker">KEEP EXPLORING</span><h3>Related finds</h3>
      <div class="recommendation-grid"><MobileProductCard v-for="item in relatedProducts" :key="item.id" :product="item" /></div>
    </section>
    <section v-if="recentProducts.length" class="recommendation-section">
      <span class="card-kicker">RECENTLY VIEWED</span><h3>Pick up where you left off</h3>
      <div class="recommendation-grid"><MobileProductCard v-for="item in recentProducts" :key="item.id" :product="item" /></div>
    </section>

    <!-- Spacer for bottom bar -->
    <div class="h-4"></div>
  </div>

  <!-- Fixed Bottom Action Bar -->
  <div v-if="product" class="detail-action-bar safe-bottom">
    <p
      v-if="cartMessage"
      class="cart-feedback"
      :class="{ error: cartMessageType === 'error' }"
      :role="cartMessageType === 'error' ? 'alert' : 'status'"
    >
      {{ cartMessage }}
    </p>
    <div class="action-buttons">
      <button
        @click="handleAddToCart"
        class="secondary-action tap-active"
        :disabled="product.stock_quantity === 0 || actionPending !== ''"
      >
        {{ actionPending === 'cart' ? 'Adding…' : 'Add to Cart' }}
      </button>
      <button
        @click="buyNow"
        class="primary-action tap-active"
        :disabled="product.stock_quantity === 0 || actionPending !== ''"
      >
        {{ actionPending === 'buy' ? 'Preparing…' : 'Buy Now' }}
      </button>
    </div>
  </div>

  <!-- Loading / Not Found -->
  <div v-else-if="loading" class="detail-loading">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      <span>Loading...</span>
    </div>
  </div>
  <div v-else class="detail-loading">
    Product not found.
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  createProductShareLink,
  getSavedProducts,
  getPaymentMethods,
  getProduct,
  getSharedProduct,
  getProducts,
  getProductReviews,
  getReturnPolicy,
  getShippingNotes,
  getShippingOptions,
  getShippingSettings,
  saveProduct,
  submitProductReview,
  unsaveProduct,
} from '../api'
import MobileProductCard from '../components/MobileProductCard.vue'
import { useCart } from '../composables/useCart'
import { useAuth } from '../composables/useAuth'
import { useLocation } from '../composables/useLocation'

const route = useRoute()
const router = useRouter()
const { addToCart } = useCart()
const { isAuthenticated } = useAuth()
const { countryCode, initLocation } = useLocation()

const product = ref(null)
const publicReference = ref('')
const loading = ref(true)
const detailsLoading = ref(true)
const relatedProducts = ref([])
const recentProducts = ref([])
const currentImage = ref(0)
const returnPolicy = ref(null)
const paymentMethods = ref([])
const shippingSettings = ref(null)
const shippingNotes = ref([])
const descriptionExpanded = ref(false)
const saveAnnouncement = ref('')
const shareAnnouncement = ref('')
const shareLink = ref('')
const sharePanel = ref(false)
const sharePending = ref(false)
const cartMessage = ref('')
const cartMessageType = ref('success')
const actionPending = ref('')
const savedProductIds = ref(new Set())
let cartMessageTimer

const isSaved = computed(() => Boolean(product.value && savedProductIds.value.has(product.value.id)))

const toggleSaved = async () => {
  if (!product.value) return
  if (!isAuthenticated.value) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  const next = new Set(savedProductIds.value)
  try {
    if (next.has(product.value.id)) {
      await unsaveProduct(product.value.id)
      next.delete(product.value.id)
      saveAnnouncement.value = 'Removed from saved products.'
    } else {
      await saveProduct(product.value.id)
      next.add(product.value.id)
      saveAnnouncement.value = 'Saved for later.'
    }
    savedProductIds.value = next
  } catch (error) {
    saveAnnouncement.value = error.response?.data?.detail || 'Could not update saved products.'
  }
}

const whatsappUrl = computed(() => shareLink.value ? `https://wa.me/?text=${encodeURIComponent(`${product.value?.title_en || product.value?.title}\n${shareLink.value}`)}` : '#')
const prepareShare = async () => {
  if (!product.value || sharePending.value) return
  sharePending.value = true; shareAnnouncement.value = ''
  try {
    if (route.params.token) {
      shareLink.value = `${window.location.origin}${route.path}`
    } else {
      const { data } = await createProductShareLink(product.value.slug)
      shareLink.value = data.share_url
      publicReference.value = data.public_reference
    }
    sharePanel.value = true
  } catch (error) {
    showCartMessage(error.response?.data?.detail || 'Could not create a safe share link.', 'error')
  } finally { sharePending.value = false }
}
const shareViaDevice = async () => {
  if (!shareLink.value) return
  if (navigator.share) {
    try { await navigator.share({ title: product.value.title_en || product.value.title, text: 'A BeCool find', url: shareLink.value }) }
    catch (error) { if (error.name !== 'AbortError') shareAnnouncement.value = 'Sharing was not available. You can copy the link instead.' }
  } else { await copyShareLink() }
}
const copyShareLink = async () => {
  try { await navigator.clipboard.writeText(shareLink.value); shareAnnouncement.value = 'Safe link copied.' }
  catch { shareAnnouncement.value = 'Copy is unavailable. Select the link from your browser address bar.' }
}

const reviews = ref({ average_rating: 0, review_count: 0, reviews: [] })
const showReviewForm = ref(false)
const reviewPending = ref(false)
const reviewMessage = ref('')
const reviewError = ref(false)
const reviewForm = ref({ rating: 5, title: '', comment: '' })
const sendReview = async () => {
  reviewPending.value = true; reviewMessage.value = ''; reviewError.value = false
  try {
    await submitProductReview(product.value.id, reviewForm.value)
    reviews.value = (await getProductReviews(product.value.id)).data
    reviewMessage.value = 'Your review is published.'; showReviewForm.value = false
  } catch (error) {
    reviewMessage.value = error.response?.data?.detail || 'Could not publish your review.'; reviewError.value = true
  } finally { reviewPending.value = false }
}

const previousImage = () => {
  const count = product.value?.images?.length || 0
  if (count > 1) currentImage.value = (currentImage.value - 1 + count) % count
}

const nextImage = () => {
  const count = product.value?.images?.length || 0
  if (count > 1) currentImage.value = (currentImage.value + 1) % count
}

// Swipe handling
let touchStartX = 0
const onTouchStart = (e) => { touchStartX = e.touches[0].clientX }
const onTouchMove = () => {}
const onTouchEnd = (e) => {
  const diffX = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(diffX) > 50 && product.value?.images?.length > 1) {
    if (diffX > 0) previousImage()
    else nextImage()
  }
}

const codeToFlagEmoji = (code) => {
  if (!code || code.length !== 2) return ''
  const codePoints = code.toUpperCase().split('').map(char => 127397 + char.charCodeAt())
  return String.fromCodePoint(...codePoints)
}

const originFlag = computed(() => codeToFlagEmoji(product.value?.origin_country_code))
const originName = computed(() => product.value?.origin_country_code || '')
const deliveryCountry = computed(() => countryCode.value || 'your country')

const conditionLabel = computed(() => ({
  new: 'New', like_new: 'Like New', good: 'Good', fair: 'Fair', poor: 'Poor', for_parts: 'Parts'
}[product.value?.condition_grade] || ''))

const badgeClasses = computed(() => ({
  new: 'bg-green-100 text-green-600', like_new: 'bg-green-100 text-green-600',
  good: 'bg-amber-100 text-amber-600', fair: 'bg-purple-100 text-purple-600',
  poor: 'bg-red-100 text-red-600', for_parts: 'bg-red-100 text-red-600'
}[product.value?.condition_grade] || ''))

const discountPercent = computed(() => {
  if (!product.value?.original_price || !product.value?.sale_price) return ''
  const pct = Math.round((1 - product.value.sale_price / product.value.original_price) * 100)
  return `-${pct}%`
})

const shippingOptions = ref([])
const lowestShipping = computed(() => {
  if (!shippingOptions.value.length) return null
  return Math.min(...shippingOptions.value.map(o => parseFloat(o.price))).toFixed(2)
})

const returnShippingLabel = computed(() => (
  returnPolicy.value?.buyer_pays_return_shipping ? 'Buyer paid' : 'Free returns'
))

const productFacts = computed(() => {
  if (!product.value) return []
  const facts = [
    { label: 'Condition', value: conditionLabel.value },
    { label: 'Brand', value: product.value.brand || 'Unbranded' },
  ]
  if (publicReference.value) facts.push({ label: 'Public reference', value: publicReference.value })
  if (product.value.weight_kg) facts.push({ label: 'Weight', value: `${product.value.weight_kg} kg` })
  if (product.value.shipping_category) facts.push({ label: 'Shipping class', value: product.value.shipping_category })
  return facts
})

const descriptionText = computed(() => String(
  product.value?.description_en || product.value?.description || ''
).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim())
const hasLongDescription = computed(() => descriptionText.value.length > 220)

const showCartMessage = (message, type = 'success') => {
  window.clearTimeout(cartMessageTimer)
  cartMessage.value = message
  cartMessageType.value = type
  cartMessageTimer = window.setTimeout(() => {
    cartMessage.value = ''
  }, type === 'error' ? 4200 : 2400)
}

const handleAddToCart = async () => {
  if (!product.value || actionPending.value) return
  actionPending.value = 'cart'
  try {
    await addToCart(product.value, 1)
    showCartMessage('Added to your bag.')
  } catch (error) {
    showCartMessage(error.message || 'Could not add this item.', 'error')
  } finally {
    actionPending.value = ''
  }
}

const buyNow = async () => {
  if (!product.value || actionPending.value) return
  actionPending.value = 'buy'
  try {
    await addToCart(product.value, 1)
    router.push('/checkout')
  } catch (error) {
    showCartMessage(error.message || 'Could not prepare checkout.', 'error')
  } finally {
    actionPending.value = ''
  }
}

onBeforeUnmount(() => window.clearTimeout(cartMessageTimer))

const settleInBatches = async (tasks, batchSize = 2) => {
  const results = []
  for (let index = 0; index < tasks.length; index += batchSize) {
    results.push(...await Promise.allSettled(
      tasks.slice(index, index + batchSize).map(task => task()),
    ))
  }
  return results
}

onMounted(async () => {
  initLocation()
  try {
    const response = route.params.token ? await getSharedProduct(route.params.token) : await getProduct(route.params.slug)
    const data = route.params.token ? response.data.product : response.data
    product.value = data
    if (route.params.token) {
      publicReference.value = response.data.public_reference
      shareLink.value = `${window.location.origin}${route.path}`
    }

    const destination = countryCode.value || 'DE'
    try {
      recentProducts.value = (JSON.parse(localStorage.getItem('esh_recent_products') || '[]') || []).filter(item => item.id !== data.id).slice(0, 4)
    } catch { recentProducts.value = [] }
    localStorage.setItem('esh_recent_products', JSON.stringify([data, ...recentProducts.value].slice(0, 6)))

    const [shippingResult, returnResult, paymentResult, settingsResult, notesResult, reviewsResult, savedResult, relatedResult] = await settleInBatches([
      () => getShippingOptions(data.slug, destination),
      () => getReturnPolicy(data.id),
      () => getPaymentMethods(),
      () => getShippingSettings(),
      () => getShippingNotes(data.slug),
      () => getProductReviews(data.id),
      () => isAuthenticated.value ? getSavedProducts() : Promise.resolve({ data: [] }),
      () => getProducts({ category_id: data.category_id, page_size: 5 }),
    ])
    if (shippingResult.status === 'fulfilled') shippingOptions.value = shippingResult.value.data || []
    if (returnResult.status === 'fulfilled') returnPolicy.value = returnResult.value.data
    if (paymentResult.status === 'fulfilled') paymentMethods.value = paymentResult.value.data || []
    if (settingsResult.status === 'fulfilled') shippingSettings.value = settingsResult.value.data
    if (notesResult.status === 'fulfilled') shippingNotes.value = notesResult.value.data || []
    if (reviewsResult.status === 'fulfilled') reviews.value = reviewsResult.value.data
    if (savedResult.status === 'fulfilled') savedProductIds.value = new Set((savedResult.value.data || []).map(item => item.product.id))
    if (relatedResult.status === 'fulfilled') relatedProducts.value = (relatedResult.value.data.items || []).filter(item => item.id !== data.id).slice(0, 4)
  } catch (e) {
    console.error(e)
  } finally {
    detailsLoading.value = false
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { min-height:100vh; padding-bottom:108px; background:#f5f2e9; color:#183c32; font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.detail-header { position:absolute; inset:0 0 auto; z-index:30; display:grid; grid-template-columns:1fr auto 1fr; align-items:center; padding:12px 16px; }
.header-control { display:grid; width:44px; height:44px; place-items:center; border:1px solid rgba(23,72,59,.1); border-radius:15px; background:rgba(255,253,246,.92); color:#17483b; box-shadow:0 6px 20px rgba(23,72,59,.1); font-size:20px; backdrop-filter:blur(10px); }
.header-save { justify-self:end; }
.header-actions { display:flex; justify-self:end; gap:7px; }
.header-actions .header-control { width:40px; height:40px; }
.header-control.saved { background:#d9f06a; }
.share-panel { position:fixed; z-index:60; top:max(72px,calc(env(safe-area-inset-top) + 64px)); right:12px; left:12px; max-width:520px; margin:auto; padding:20px; border:1px solid rgba(23,72,59,.12); border-radius:22px; background:#fffdf8; color:#183c32; box-shadow:0 22px 60px rgba(23,63,52,.24); }
.share-panel h2 { margin:5px 0 7px; font:700 23px Georgia,serif; }.share-panel>p { margin:0; color:#5f6f64; font-size:12px; line-height:1.5; }
.share-close { position:absolute; top:8px; right:9px; display:grid; width:38px; height:38px; place-items:center; color:#17483b; font-size:22px; }
.share-actions { display:grid; grid-template-columns:1fr 1fr 1fr; gap:7px; margin-top:15px; }.share-actions a,.share-actions button { display:grid; min-height:44px; place-items:center; border:1px solid #c7d2c7; border-radius:999px; color:#17483b; font-size:11px; font-weight:800; }.share-actions a:first-child { border-color:#17483b; background:#17483b; color:#fffdf8; }.share-feedback { margin-top:10px!important; color:#345144!important; font-weight:750; text-align:center; }
.detail-brand-mark { display:grid; width:38px; height:38px; place-items:center; border-radius:13px; background:#d9f06a; color:#17483b; font-family:Georgia,serif; font-size:25px; font-weight:800; line-height:1; box-shadow:0 6px 20px rgba(23,72,59,.14); }
.gallery-stage { position:relative; display:flex; height:clamp(410px,64vh,570px); align-items:center; justify-content:center; overflow:hidden; background:#e7e3d8; touch-action:pan-y; }
.gallery-image { width:100%; height:100%; object-fit:contain; }
.gallery-empty { width:72px; height:72px; border:2px dashed #9aaa9f; border-radius:22px; }
.gallery-arrow { position:absolute; top:50%; z-index:10; display:grid; width:44px; height:44px; place-items:center; transform:translateY(-50%); border-radius:999px; background:rgba(255,255,255,.92); color:#17483b; box-shadow:0 4px 18px rgba(23,72,59,.14); font-family:Georgia,serif; font-size:31px; line-height:1; }
.gallery-arrow-left { left:12px; }
.gallery-arrow-right { right:12px; }
.gallery-counter { position:absolute; right:12px; bottom:16px; padding:6px 10px; border-radius:999px; background:rgba(23,72,59,.82); color:#fffdf6; font-size:10px; font-weight:750; letter-spacing:.4px; }
.gallery-dots { position:absolute; bottom:0; left:50%; display:flex; transform:translateX(-50%); }
.gallery-dot { position:relative; width:44px; height:44px; }
.gallery-dot::after { position:absolute; top:50%; left:50%; width:7px; height:7px; border-radius:999px; background:rgba(255,253,246,.7); box-shadow:0 1px 4px rgba(23,72,59,.16); content:""; transform:translate(-50%,-50%); transition:width .2s,background .2s; }
.gallery-dot.active::after { width:22px; background:#d9f06a; }
.gallery-fade-enter-active, .gallery-fade-leave-active { transition:opacity .18s ease, transform .18s ease; }
.gallery-fade-enter-from { opacity:0; transform:scale(.985); }
.gallery-fade-leave-to { opacity:0; transform:scale(1.015); }
.detail-content { position:relative; z-index:20; margin:-6px 12px 14px; }
.product-summary { padding:23px 19px 20px; border:1px solid rgba(23,72,59,.05); border-radius:23px; background:#fffdf8; box-shadow:0 10px 30px rgba(37,55,43,.07); }
.detail-eyebrow,.card-kicker { display:block; color:#66736a; font-size:10px; font-weight:800; letter-spacing:1.45px; }
.price-row { display:flex; align-items:baseline; gap:9px; margin-top:11px; }
.sale-price { color:#17483b; font-family:Georgia,serif; font-size:30px; font-weight:700; line-height:1; letter-spacing:-.7px; }
.original-price { color:#68756b; font-size:13px; text-decoration:line-through; }
.discount-pill { margin-left:auto; padding:5px 8px; border-radius:999px; background:#d9f06a; color:#17483b; font-size:10px; font-weight:800; }
.product-title { margin:15px 0 0; color:#183c32; font-family:Georgia,serif; font-size:25px; font-weight:700; line-height:1.08; letter-spacing:-.6px; }
.product-brand { margin:7px 0 0; color:#66756b; font-size:13px; font-weight:650; }
.product-chips { display:flex; flex-wrap:wrap; gap:7px; margin-top:16px; }
.condition-chip,.stock-chip { display:inline-flex; min-height:32px; align-items:center; padding:6px 11px; border-radius:999px; background:#edf0e9!important; color:#456052!important; font-size:12px; font-weight:750; }
.stock-chip { background:#e9f2c8!important; color:#345144!important; }
.stock-chip.out-of-stock { background:#f3ddd5!important; color:#874f3f!important; }
.origin-line { display:flex; align-items:center; gap:6px; margin-top:13px; color:#5f6f64; font-size:13px; }
.condition-note { margin:12px 0 0; color:#5f6f64; font-size:13px; line-height:1.55; }
.info-card { margin:0 12px 12px; padding:18px 19px; border:1px solid rgba(23,72,59,.05); border-radius:19px; background:#fffdf8; box-shadow:0 6px 22px rgba(37,55,43,.045); }
.info-card h3 { margin:5px 0 8px; color:#183c32; font-family:Georgia,serif; font-size:19px; line-height:1.1; }
.card-copy { margin:0; color:#5f6f64; font-size:14px; line-height:1.65; }
.card-copy p { margin:4px 0 0; }
.info-lead { color:#294b3f; font-weight:750; }
.info-list { display:grid; gap:10px; margin:14px 0 0; padding:14px 0 0; border-top:1px solid #e7e9e2; list-style:none; }
.info-list li { display:grid; gap:2px; }
.info-list strong { color:#294b3f; font-size:13px; }
.confidence-grid { display:grid; grid-template-columns:1fr 1fr; gap:9px; margin-top:13px; }
.confidence-grid div { padding:12px; border-radius:14px; background:#f0f2e9; }
.confidence-grid strong,.confidence-grid span { display:block; }
.confidence-grid strong { color:#294b3f; font-family:Georgia,serif; font-size:16px; }
.confidence-grid span { margin-top:4px; color:#65746a; font-size:12px; }
.policy-note { margin:12px 0 0; color:#5f6f64; font-size:13px; line-height:1.55; }
.payment-methods { display:flex; flex-wrap:wrap; gap:7px; margin-top:14px; }
.payment-methods span { padding:6px 9px; border:1px solid #d5ddd2; border-radius:999px; color:#3f5d50; font-size:12px; font-weight:700; }
.facts-list { margin:8px 0 0; }
.facts-list div { display:grid; grid-template-columns:minmax(100px,.8fr) 1.2fr; gap:14px; padding:11px 0; border-bottom:1px solid #e9ebe5; }
.facts-list div:last-child { border-bottom:0; }
.facts-list dt { color:#6a786f; font-size:13px; }
.facts-list dd { margin:0; color:#294b3f; font-size:13px; font-weight:700; text-align:right; text-transform:capitalize; overflow-wrap:anywhere; }
.product-description.collapsed { display:-webkit-box; overflow:hidden; -webkit-box-orient:vertical; -webkit-line-clamp:5; }
.read-more { min-height:44px; margin-top:8px; color:#17483b; font-size:13px; font-weight:800; }
.review-heading { display:flex; align-items:baseline; justify-content:space-between; gap:12px; }
.review-heading strong { color:#17483b; font-size:13px; }
.review-item { padding:14px 0; border-top:1px solid #e7e9e2; }
.review-item>div { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.review-item>div>strong { color:#577133; letter-spacing:1px; }
.review-item span { color:#68756b; font-size:11px; }
.review-item em { margin-left:7px; padding:3px 6px; border-radius:999px; background:#e9f2c8; color:#345144; font-size:9px; font-style:normal; font-weight:800; }
.review-item h4 { margin:9px 0 3px; font-size:13px; }
.review-item p { margin:0; color:#5f6f64; font-size:13px; line-height:1.55; }
.review-signin { display:inline-block; min-height:44px; padding-top:13px; color:#17483b; font-size:13px; font-weight:800; }
.review-form { display:grid; gap:10px; padding-top:14px; border-top:1px solid #e7e9e2; }
.review-form label { display:grid; gap:5px; color:#5f6f64; font-size:11px; font-weight:800; }
.review-form input,.review-form select,.review-form textarea { width:100%; border:1px solid #d5ddd2; border-radius:11px; background:white; padding:10px; color:#17483b; }
.review-form textarea { min-height:80px; resize:vertical; }
.review-form p { margin:0; color:#345144; font-size:12px; }.review-form p.error { color:#9d3434; }
.review-submit { min-height:44px; border-radius:999px; background:#17483b; color:#fffdf6; font-size:12px; font-weight:800; }
.recommendation-section { margin:20px 0 6px; padding:0 12px; }
.recommendation-section>h3 { margin:5px 0 12px; font:700 21px Georgia,serif; }
.recommendation-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
.detail-action-bar { position:fixed; right:0; bottom:0; left:0; z-index:50; padding:12px 16px; border-top:1px solid rgba(23,72,59,.08); background:rgba(255,253,248,.94); box-shadow:0 -10px 30px rgba(37,55,43,.07); backdrop-filter:blur(14px); }
.cart-feedback { max-width:560px; margin:0 auto 9px; padding:8px 12px; border:1px solid #cbd9bd; border-radius:11px; background:#eef3cb; color:#17483b; font-size:12px; font-weight:750; text-align:center; }
.cart-feedback.error { border-color:#e4c2ac; background:#fff4eb; color:#74422b; }
.action-buttons { display:flex; gap:10px; max-width:560px; margin:0 auto; }
.secondary-action,.primary-action { min-height:48px; flex:1; border-radius:999px; font-size:12px; font-weight:800; }
.secondary-action { border:1px solid #c7d2c7; background:#eef3cb; color:#17483b; }
.primary-action { background:#17483b; color:#fffdf6; box-shadow:0 7px 18px rgba(23,72,59,.2); }
.secondary-action:disabled,.primary-action:disabled { opacity:.45; }
.detail-loading { display:flex; min-height:100vh; align-items:center; justify-content:center; background:#f5f2e9; color:#748278; }
.header-control:focus-visible,.gallery-arrow:focus-visible,.gallery-dot:focus-visible,.read-more:focus-visible,.secondary-action:focus-visible,.primary-action:focus-visible { outline:3px solid #d9f06a; outline-offset:3px; }
@media (prefers-reduced-motion:reduce) {
  .gallery-fade-enter-active,.gallery-fade-leave-active,.gallery-dot::after { transition:none; }
}
@supports (padding-top: env(safe-area-inset-top)) {
  .safe-top { padding-top: env(safe-area-inset-top); }
}
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .safe-bottom { padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
}
</style>
