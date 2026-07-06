<template>
  <div v-if="product">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 pb-24">
      <!-- Breadcrumb -->
      <nav class="text-sm text-gray-400 mb-6">
        <router-link to="/" class="hover:text-primary transition">Home</router-link>
        <span class="mx-2">/</span>
        <router-link to="/browse" class="hover:text-primary transition">Browse</router-link>
        <span class="mx-2">/</span>
        <span class="text-gray-600 truncate">{{ product.title_en }}</span>
      </nav>

      <!-- Main Content: 5:7 split on desktop, stacked on mobile -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
        <!-- Left: Image Gallery (5 cols) -->
        <div class="lg:col-span-5">
          <ImageGallery :images="product.images" :product-name="product.title_en" />
        </div>

        <!-- Right: Product Info (7 cols) - sticky on desktop -->
        <div class="lg:col-span-7 lg:sticky lg:top-6 lg:h-fit lg:-mr-4">
          <!-- Price -->
          <PriceBlock
            :sale-price="product.sale_price"
            :original-price="product.original_price"
          />

          <!-- Title & Condition -->
          <ProductTitle
            :title="product.title_en"
            :brand="product.brand"
            :condition-grade="product.condition_grade"
          />

          <!-- Condition Note -->
          <div v-if="product.condition_note" class="mb-4 bg-orange-bg rounded-xl p-4">
            <div class="text-sm font-medium text-gray-900 mb-1">Condition Details</div>
            <p class="text-gray-600 text-sm leading-relaxed">{{ product.condition_note }}</p>
          </div>

          <!-- SKU Selector -->
          <SkuSelector :option-groups="skuOptionGroups" />

          <!-- Quantity -->
          <QuantitySelector
            :max-stock="product.stock_quantity > 0 ? product.stock_quantity : 99"
            @change="quantity = $event"
          />

          <!-- Stock Status -->
          <div v-if="product.auto_manage_stock" class="mb-4 text-sm">
            <span v-if="product.stock_quantity > 0" class="text-green-600">
              ✅ {{ product.stock_quantity }} in stock
            </span>
            <span v-else class="text-red-600 font-medium">❌ Out of stock</span>
          </div>

          <!-- Shipping Info (eBay style) -->
          <ShippingInfo
            :product-id="product.id"
            :product-slug="product.slug"
            :country-code="countryCode || 'DE'"
            :origin-country-name="originCountryName"
          />

          <!-- Shipping Table (full options with country selector) -->
          <ShippingTable
            :product-slug="product.slug"
            :origin-country-code="product.origin_country_code"
            :origin-flag="originFlag"
            :origin-country-name="originCountryName"
          />

          <!-- CTA Buttons (moved to fixed bottom bar) -->
          <div class="h-14"></div>

        </div>
      </div>

      <!-- Detail Tabs -->
      <div class="mt-12 lg:mt-16">
        <DetailTabs>
          <template #description>
            <DescriptionPanel :html="product.description_en || product.description" />
          </template>
          <template #reviews>
            <ReviewsPanel />
          </template>
          <template #specs>
            <SpecsPanel :product="product" />
          </template>
        </DetailTabs>
      </div>

      <!-- Related Products -->
      <RelatedProducts
        :current-slug="product.slug"
        :category-id="product.category_id"
      />
    </div>

    <!-- Fixed Bottom Action Bar -->
    <div class="fixed bottom-0 left-0 right-0 z-50 px-4 sm:px-6 lg:px-8 pb-2 safe-bottom">
      <div class="max-w-7xl mx-auto">
        <div class="hidden lg:grid lg:grid-cols-12">
          <div class="lg:col-start-6 lg:col-span-7">
            <CtaButtons
              :disabled="product.stock_quantity === 0"
              @add-to-cart="handleAddToCart"
              @buy-now="handleBuyNow"
            />
          </div>
        </div>
        <div class="lg:hidden">
          <CtaButtons
            :disabled="product.stock_quantity === 0"
            @add-to-cart="handleAddToCart"
            @buy-now="handleBuyNow"
          />
        </div>
      </div>
    </div>

    <Footer />
  </div>
  <div v-else-if="loading" class="min-h-screen flex items-center justify-center text-gray-400">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      <span>Loading...</span>
    </div>
  </div>
  <div v-else class="min-h-screen flex items-center justify-center text-gray-400">
    Product not found.
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { getProduct } from '../api'
import { useCart } from '../composables/useCart'
import { useCountries } from '../composables/useCountries'
import { useLocation } from '@/composables/useLocation'

// PDP Components
import ImageGallery from '../components/pdp/ImageGallery.vue'
import PriceBlock from '../components/pdp/PriceBlock.vue'
import ProductTitle from '../components/pdp/ProductTitle.vue'
import SkuSelector from '../components/pdp/SkuSelector.vue'
import QuantitySelector from '../components/pdp/QuantitySelector.vue'
import ShippingTable from '../components/pdp/ShippingTable.vue'
import ShippingInfo from '../components/pdp/ShippingInfo.vue'
import CtaButtons from '../components/pdp/CtaButtons.vue'
import DetailTabs from '../components/pdp/DetailTabs.vue'
import DescriptionPanel from '../components/pdp/DescriptionPanel.vue'
import ReviewsPanel from '../components/pdp/ReviewsPanel.vue'
import SpecsPanel from '../components/pdp/SpecsPanel.vue'
import RelatedProducts from '../components/pdp/RelatedProducts.vue'

const route = useRoute()
const router = useRouter()
const { addToCart } = useCart()
const { loadCountries, getFlagEmoji, getCountryName } = useCountries()
const { countryCode } = useLocation()

const product = ref(null)
const loading = ref(true)
const quantity = ref(1)

const originFlag = computed(() => product.value?.origin_country_code ? getFlagEmoji(product.value.origin_country_code) : '')
const originCountryName = computed(() => product.value?.origin_country_code ? getCountryName(product.value.origin_country_code) : '')

// SKU option groups — future-proof structure, currently defaults to single option
const skuOptionGroups = ref([
  {
    label: 'Specification',
    options: [{ label: 'Standard', disabled: false }],
    selected: 0,
  },
])

function handleAddToCart() {
  addToCart(product.value, quantity.value)
}

function handleBuyNow() {
  addToCart(product.value, quantity.value)
  router.push('/cart')
}

onMounted(async () => {
  loadCountries()
  // Start location detection in background
  const { initLocation } = useLocation()
  initLocation()
  try {
    const { data } = await getProduct(route.params.slug)
    product.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Hide scrollbar for thumbnail strip */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
