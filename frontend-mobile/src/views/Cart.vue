<template>
  <div class="cart-page">
    <header class="cart-header safe-top">
      <div class="header-inner">
        <button type="button" class="icon-button" aria-label="Go back" @click="router.back()">←</button>
        <div class="header-title">
          <span class="brand-mark">b.</span>
          <div>
            <span class="eyebrow">YOUR SELECTION</span>
            <h1>Shopping bag</h1>
          </div>
        </div>
        <span class="item-count">{{ count }}</span>
      </div>
    </header>

    <main class="cart-shell">
      <div v-if="error" class="error-banner" role="alert">
        <span>{{ error }}</span>
        <button type="button" aria-label="Dismiss message" @click="clearError">×</button>
      </div>

      <div v-if="loading && !items.length" class="loading-state" aria-live="polite">
        <span class="spinner" aria-hidden="true"></span>
        <p>Loading your bag…</p>
      </div>

      <section v-else-if="!items.length" class="empty-state">
        <span class="empty-mark">b.</span>
        <span class="eyebrow">YOUR BAG IS READY</span>
        <h2>Find something worth keeping.</h2>
        <p>Well-chosen pieces will wait for you here while you decide.</p>
        <router-link to="/browse" class="shop-button">Browse all products <span>→</span></router-link>
      </section>

      <template v-else>
        <div class="bag-toolbar">
          <label class="select-control">
            <input
              type="checkbox"
              :checked="allSelected"
              :indeterminate="someSelected"
              @change="selectAll($event.target.checked)"
            />
            <span>Select all</span>
          </label>
          <span>{{ selectedCount }} of {{ items.length }} selected</span>
        </div>

        <div class="cart-list">
          <article
            v-for="item in items"
            :key="item.id || item.product_id"
            class="cart-card"
            :class="{ muted: !selectedIds.includes(item.product_id) }"
          >
            <label class="item-check" :aria-label="`Select ${productTitle(item)}`">
              <input
                type="checkbox"
                :checked="selectedIds.includes(item.product_id)"
                @change="toggleSelect(item.product_id)"
              />
            </label>

            <router-link :to="`/products/${item.product?.slug}`" class="product-image">
              <img
                v-if="productImage(item)"
                :src="productImage(item)"
                :alt="productTitle(item)"
              />
              <span v-else aria-hidden="true">b.</span>
            </router-link>

            <div class="product-info">
              <div class="item-heading">
                <div>
                  <span class="item-brand">{{ item.product?.brand || 'BECOOL EDIT' }}</span>
                  <router-link :to="`/products/${item.product?.slug}`" class="product-title">
                    {{ productTitle(item) }}
                  </router-link>
                </div>
                <button
                  type="button"
                  class="remove-button"
                  :disabled="isPending(item.product_id)"
                  :aria-label="`Remove ${productTitle(item)}`"
                  @click="removeItem(item)"
                >
                  Remove
                </button>
              </div>

              <div class="item-meta">
                <span v-if="item.product?.condition_grade">{{ formatCondition(item.product.condition_grade) }}</span>
                <span v-if="Number(item.product?.stock_quantity) <= 3" class="low-stock">
                  Only {{ item.product?.stock_quantity }} left
                </span>
              </div>
              <button type="button" class="save-button" :disabled="isPending(item.product_id)" @click="moveToSaved(item)">Save for later</button>

              <div class="item-bottom">
                <div class="quantity-control" :aria-label="`Quantity for ${productTitle(item)}`">
                  <button
                    type="button"
                    :disabled="isPending(item.product_id)"
                    :aria-label="`Decrease ${productTitle(item)} quantity`"
                    @click="setQuantity(item, item.quantity - 1)"
                  >−</button>
                  <span aria-live="polite">{{ item.quantity }}</span>
                  <button
                    type="button"
                    :disabled="isPending(item.product_id) || atStockLimit(item)"
                    :aria-label="`Increase ${productTitle(item)} quantity`"
                    @click="setQuantity(item, item.quantity + 1)"
                  >+</button>
                </div>
                <div class="price-block">
                  <span v-if="Number(item.product?.original_price) > Number(item.product?.sale_price)" class="original-price">
                    €{{ money(Number(item.product?.original_price) * item.quantity) }}
                  </span>
                  <strong>€{{ money(Number(item.product?.sale_price) * item.quantity) }}</strong>
                </div>
              </div>
            </div>
          </article>
        </div>

        <section class="delivery-note">
          <span class="note-icon" aria-hidden="true">↗</span>
          <div>
            <strong v-if="shippingLoading">Checking delivery to {{ countryCode }}…</strong>
            <strong v-else-if="estimatedShipping !== null">Estimated delivery · €{{ money(estimatedShipping) }}</strong>
            <strong v-else>Shipping calculated at checkout</strong>
            <p>{{ shippingError || `Based on ${countryCode || 'your delivery country'} and the items selected.` }}</p>
          </div>
        </section>
        <form class="promo-card" @submit.prevent="applyPromo"><label for="promo-code">Promotion code</label><div><input id="promo-code" v-model.trim="promoInput" autocomplete="off" placeholder="Enter code" /><button :disabled="promoLoading">{{ promoLoading?'Checking…':'Apply' }}</button></div><p v-if="promoMessage" :class="{error:promoError}" role="status">{{ promoMessage }}</p></form>
        <div v-if="removedItem" class="undo-card" role="status"><span>{{ productTitle(removedItem) }} removed.</span><button type="button" @click="undoRemove">Undo</button></div>
      </template>
    </main>

    <aside v-if="items.length" class="checkout-bar safe-bottom">
      <div class="checkout-inner">
        <div class="total-copy">
          <span>Estimated total · {{ selectedUnits }} {{ selectedUnits === 1 ? 'item' : 'items' }}</span>
          <span v-if="promoDiscount">Promotion −€{{ money(promoDiscount) }}</span>
          <strong>€{{ money(estimatedGrandTotal) }}</strong>
          <small>{{ estimatedShipping===null?'Shipping confirmed at checkout':'Includes estimated delivery' }}</small>
        </div>
        <button
          type="button"
          class="checkout-button"
          :disabled="selectedCount === 0 || loading"
          @click="checkout"
        >
          {{ selectedCount ? 'Continue to checkout' : 'Select an item' }}
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getShippingOptions, saveProduct, validatePromotion } from '../api'
import { useAuth } from '../composables/useAuth'
import { useCart } from '../composables/useCart'
import { useLocation } from '../composables/useLocation'

const router = useRouter()
const { isAuthenticated } = useAuth()
const { countryCode, initLocation } = useLocation()
const {
  items,
  count,
  loading,
  error,
  selectedIds,
  selectedCount,
  selectedUnits,
  selectedTotal,
  selectedItems,
  addToCart,
  updateQty,
  removeFromCart,
  toggleSelect,
  selectAll,
  clearError,
  isPending,
} = useCart()
const estimatedShipping = ref(null), shippingLoading = ref(false), shippingError = ref('')
const promoInput = ref(sessionStorage.getItem('esh_promo_code') || ''), promo = ref(null), promoLoading = ref(false), promoMessage = ref(''), promoError = ref(false)
const removedItem = ref(null)
let removedTimer
const promoDiscount = computed(() => promo.value ? selectedItems.value.reduce((sum,item)=>sum + (Number(item.product?.sale_price||0)-Math.round(Number(item.product?.sale_price||0)*.9*100)/100)*item.quantity,0) : 0)
const discountedSubtotal = computed(() => selectedTotal.value - promoDiscount.value)
const estimatedGrandTotal = computed(() => discountedSubtotal.value + Number(estimatedShipping.value || 0))

const allSelected = computed(() => (
  items.value.length > 0 && selectedCount.value === items.value.length
))
const someSelected = computed(() => (
  selectedCount.value > 0 && selectedCount.value < items.value.length
))

const productTitle = item => item.product?.title_en || item.product?.title || 'Product'
const productImage = item => {
  const image = item.product?.images?.[0]
  return image?.thumbnail_url || image?.image_url || ''
}
const formatCondition = value => String(value).replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase())
const money = value => Number(value || 0).toFixed(2)
const itemKey = item => item.id ?? item.product_id
const atStockLimit = item => (
  Number.isFinite(Number(item.product?.stock_quantity))
  && Number(item.quantity) >= Number(item.product.stock_quantity)
)

const setQuantity = async (item, quantity) => {
  try {
    await updateQty(itemKey(item), quantity)
  } catch {
    // The shared error banner provides the actionable message.
  }
}

const removeItem = async (item) => {
  try {
    removedItem.value = { ...item, product: item.product }
    await removeFromCart(itemKey(item))
    window.clearTimeout(removedTimer)
    removedTimer = window.setTimeout(() => { removedItem.value = null }, 6000)
  } catch {
    removedItem.value = null
    // The shared error banner provides the actionable message.
  }
}

const undoRemove = async () => { if(!removedItem.value)return;try{await addToCart(removedItem.value.product,removedItem.value.quantity);removedItem.value=null}catch{} }
const moveToSaved = async item => { if(!isAuthenticated.value){router.push({path:'/login',query:{redirect:'/cart'}});return}try{await saveProduct(item.product_id);await removeFromCart(itemKey(item))}catch{} }
const loadShipping = async () => { if(!countryCode.value||!selectedItems.value.length){estimatedShipping.value=null;return}shippingLoading.value=true;shippingError.value='';try{const results=await Promise.all(selectedItems.value.map(async item=>{const {data}=await getShippingOptions(item.product.slug,countryCode.value);const prices=(data||[]).map(option=>Number(option.price ?? option.total_fee)).filter(Number.isFinite);return (prices.length?Math.min(...prices):0)*item.quantity}));estimatedShipping.value=results.reduce((sum,v)=>sum+v,0)}catch(e){estimatedShipping.value=null;shippingError.value='Delivery will be confirmed at checkout.'}finally{shippingLoading.value=false} }
const applyPromo = async () => {promoLoading.value=true;promoMessage.value='';promoError.value=false;try{promo.value=(await validatePromotion(promoInput.value)).data;promoInput.value=promo.value.code;sessionStorage.setItem('esh_promo_code',promo.value.code);promoMessage.value=`${promo.value.label}: ${promo.value.discount_value}% off applied.`}catch(e){promo.value=null;sessionStorage.removeItem('esh_promo_code');promoMessage.value=e.response?.data?.detail||'This promotion code is not valid.';promoError.value=true}finally{promoLoading.value=false}}

const checkout = () => {
  if (selectedCount.value) router.push('/checkout')
}
watch([selectedIds,countryCode],loadShipping,{deep:true})
onMounted(async()=>{await initLocation();if(promoInput.value)await applyPromo();await loadShipping()})
</script>

<style scoped>
.cart-page { min-height:100vh; padding-bottom:178px; background:#f5f2e9; color:#183f35; }
.cart-header { position:sticky; top:0; z-index:40; border-bottom:1px solid rgba(23,72,59,.12); background:rgba(245,242,233,.94); backdrop-filter:blur(14px); }
.header-inner { display:grid; grid-template-columns:48px 1fr 48px; align-items:center; max-width:760px; min-height:72px; margin:0 auto; padding:8px 14px; }
.icon-button { width:44px; height:44px; border:1px solid #d8ded5; border-radius:50%; background:#fffdf8; color:#17483b; font-size:20px; }
.header-title { display:flex; align-items:center; justify-content:center; gap:10px; min-width:0; }
.brand-mark,.empty-mark { display:grid; place-items:center; flex:0 0 auto; width:35px; height:35px; border-radius:50%; background:#17483b; color:#d9f06a; font-family:Georgia,serif; font-size:19px; font-weight:700; }
.eyebrow { display:block; color:#66776d; font-size:9px; font-weight:850; letter-spacing:.2em; }
.header-title h1 { margin:2px 0 0; font-family:Georgia,serif; font-size:20px; line-height:1; }
.item-count { display:grid; place-items:center; justify-self:end; min-width:32px; height:32px; padding:0 8px; border-radius:999px; background:#e3ef86; color:#17483b; font-size:12px; font-weight:850; }
.cart-shell { max-width:760px; margin:0 auto; padding:18px 14px 28px; }
.error-banner { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:14px; padding:12px 14px; border:1px solid #e4c2ac; border-radius:14px; background:#fff4eb; color:#74422b; font-size:13px; font-weight:650; }
.error-banner button { width:36px; height:36px; flex:0 0 auto; font-size:20px; }
.loading-state,.empty-state { min-height:58vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
.loading-state { gap:12px; color:#66776d; font-size:13px; }
.spinner { width:32px; height:32px; border:3px solid #d8ded5; border-top-color:#17483b; border-radius:50%; animation:spin .8s linear infinite; }
.empty-state { padding:44px 22px; }
.empty-mark { width:54px; height:54px; margin-bottom:22px; font-size:27px; }
.empty-state h2 { max-width:430px; margin:10px 0 0; font-family:Georgia,serif; font-size:34px; line-height:1.06; }
.empty-state p { max-width:370px; margin:14px 0 0; color:#66776d; font-size:14px; line-height:1.6; }
.shop-button { display:flex; align-items:center; justify-content:center; gap:16px; min-height:50px; margin-top:24px; padding:0 22px; border-radius:999px; background:#17483b; color:#fffdf8; font-size:12px; font-weight:850; }
.bag-toolbar { display:flex; align-items:center; justify-content:space-between; gap:16px; margin:2px 2px 12px; color:#6a786f; font-size:12px; }
.select-control { display:flex; min-height:44px; align-items:center; gap:10px; color:#294b3f; font-weight:800; cursor:pointer; }
input[type='checkbox'] { width:20px; height:20px; border-radius:6px; accent-color:#17483b; cursor:pointer; }
.cart-list { display:grid; gap:12px; }
.cart-card { display:grid; grid-template-columns:24px 108px minmax(0,1fr); gap:12px; padding:14px; border:1px solid rgba(23,72,59,.1); border-radius:22px; background:#fffdf8; box-shadow:0 8px 24px rgba(31,59,48,.055); transition:opacity .2s ease; }
.cart-card.muted { opacity:.58; }
.item-check { display:flex; align-items:flex-start; padding-top:42px; cursor:pointer; }
.product-image { position:relative; display:block; width:108px; aspect-ratio:4/5; overflow:hidden; border-radius:16px; background:#e8e8df; }
.product-image img { width:100%; height:100%; object-fit:cover; }
.product-image > span { display:grid; place-items:center; width:100%; height:100%; color:#17483b; font-family:Georgia,serif; font-size:28px; }
.product-info { display:flex; min-width:0; flex-direction:column; }
.item-heading { display:flex; align-items:flex-start; justify-content:space-between; gap:8px; }
.item-brand { display:block; margin-bottom:5px; color:#748278; font-size:9px; font-weight:850; letter-spacing:.13em; text-transform:uppercase; }
.product-title { display:-webkit-box; overflow:hidden; color:#183f35; font-family:Georgia,serif; font-size:17px; font-weight:700; line-height:1.2; -webkit-box-orient:vertical; -webkit-line-clamp:2; }
.remove-button { min-height:38px; flex:0 0 auto; padding:0 4px; color:#77837b; font-size:11px; font-weight:750; text-decoration:underline; text-underline-offset:3px; }
.remove-button:disabled { opacity:.4; }
.item-meta { display:flex; flex-wrap:wrap; gap:7px; margin-top:8px; color:#68776e; font-size:11px; }
.item-meta span { padding:4px 7px; border-radius:999px; background:#f0f2e9; }
.item-meta .low-stock { background:#fff0df; color:#8a4a20; }
.save-button { align-self:flex-start; min-height:34px; margin-top:5px; color:#17483b; font-size:10px; font-weight:800; text-decoration:underline; text-underline-offset:3px; }
.item-bottom { display:flex; align-items:end; justify-content:space-between; gap:10px; margin-top:auto; padding-top:12px; }
.quantity-control { display:grid; grid-template-columns:38px 32px 38px; align-items:center; min-height:40px; overflow:hidden; border:1px solid #d7ddd4; border-radius:999px; background:#f7f6ef; text-align:center; }
.quantity-control button { min-height:40px; color:#17483b; font-size:18px; font-weight:600; }
.quantity-control button:disabled { color:#adb5af; }
.quantity-control span { font-size:12px; font-weight:850; }
.price-block { display:flex; flex-direction:column; align-items:flex-end; }
.price-block strong { color:#17483b; font-family:Georgia,serif; font-size:18px; white-space:nowrap; }
.original-price { color:#9aa29c; font-size:10px; text-decoration:line-through; }
.delivery-note { display:flex; gap:12px; margin-top:14px; padding:16px; border:1px solid rgba(23,72,59,.1); border-radius:18px; background:#edf1e8; }
.note-icon { display:grid; place-items:center; width:36px; height:36px; flex:0 0 auto; border-radius:50%; background:#d9f06a; color:#17483b; font-size:18px; }
.delivery-note strong { display:block; font-size:13px; }
.delivery-note p { margin:4px 0 0; color:#66776d; font-size:11px; line-height:1.5; }
.promo-card { margin-top:12px; padding:16px; border:1px solid rgba(23,72,59,.1); border-radius:18px; background:#fffdf8; }
.promo-card>label { display:block; margin-bottom:7px; color:#294b3f; font-size:11px; font-weight:850; }
.promo-card>div { display:flex; gap:8px; }.promo-card input { min-width:0; flex:1; border:1px solid #d7ddd4; border-radius:12px; padding:11px; color:#17483b; text-transform:uppercase; }
.promo-card button { border-radius:999px; background:#17483b; padding:0 16px; color:#fffdf8; font-size:11px; font-weight:850; }
.promo-card p { margin:8px 0 0; color:#47704d; font-size:11px; }.promo-card p.error { color:#9d3434; }
.undo-card { position:fixed; right:14px; bottom:114px; left:14px; z-index:55; display:flex; align-items:center; justify-content:space-between; max-width:732px; margin:auto; border-radius:14px; background:#173f34; padding:12px 14px; color:#fffdf8; font-size:12px; box-shadow:0 10px 30px rgba(23,63,52,.24) }.undo-card button { color:#d9f06a; font-weight:900; }
.checkout-bar { position:fixed; right:0; bottom:0; left:0; z-index:50; border-top:1px solid rgba(23,72,59,.1); background:rgba(255,253,248,.96); box-shadow:0 -12px 34px rgba(31,59,48,.09); backdrop-filter:blur(14px); }
.checkout-inner { display:flex; max-width:760px; min-height:94px; margin:0 auto; padding:12px 14px; align-items:center; justify-content:space-between; gap:18px; }
.total-copy { display:flex; min-width:0; flex-direction:column; }
.total-copy > span { color:#66776d; font-size:10px; font-weight:750; }
.total-copy strong { margin-top:2px; color:#17483b; font-family:Georgia,serif; font-size:25px; line-height:1; }
.total-copy small { margin-top:4px; color:#89938d; font-size:9px; }
.checkout-button { display:flex; min-height:52px; flex:0 0 auto; align-items:center; justify-content:center; gap:18px; padding:0 21px; border-radius:999px; background:#17483b; color:#fffdf8; font-size:12px; font-weight:850; box-shadow:0 8px 20px rgba(23,72,59,.2); }
.checkout-button:disabled { background:#9da8a2; box-shadow:none; }
button:focus-visible,a:focus-visible,input:focus-visible { outline:3px solid #d9f06a; outline-offset:3px; }
@keyframes spin { to { transform:rotate(360deg); } }
@media (max-width:520px) {
  .cart-card { grid-template-columns:22px 84px minmax(0,1fr); gap:10px; padding:12px; border-radius:18px; }
  .product-image { width:84px; }
  .product-title { font-size:15px; }
  .remove-button { font-size:10px; }
  .item-bottom { align-items:center; }
  .quantity-control { grid-template-columns:34px 26px 34px; }
  .price-block strong { font-size:16px; }
  .checkout-inner { gap:10px; }
  .checkout-button { min-height:50px; gap:10px; padding:0 17px; }
  .total-copy small { display:none; }
}
@media (max-width:380px) {
  .cart-card { grid-template-columns:20px 72px minmax(0,1fr); }
  .product-image { width:72px; }
  .item-meta { display:none; }
  .quantity-control { grid-template-columns:32px 24px 32px; }
  .checkout-button { padding:0 14px; font-size:11px; }
}
@media (prefers-reduced-motion:reduce) {
  .spinner { animation:none; }
  .cart-card { transition:none; }
}
</style>
