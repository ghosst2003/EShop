<template>
  <div class="checkout-page">
    <header class="checkout-header safe-top">
      <div class="header-inner">
        <button type="button" class="back-button" aria-label="Go back" @click="router.back()">←</button>
        <div>
          <span class="eyebrow">SECURE CHECKOUT</span>
          <h1>Finish your order</h1>
        </div>
        <span class="step-pill">1 / 1</span>
      </div>
    </header>

    <main class="checkout-shell">
      <div v-if="error" class="message error" role="alert">{{ error }}</div>
      <div v-if="loading" class="loading-card" aria-live="polite">Preparing checkout…</div>

      <template v-else>
        <section class="checkout-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">DELIVERY</span>
              <h2>Shipping address</h2>
            </div>
            <button v-if="addresses.length" type="button" class="text-button" @click="showAddressForm = !showAddressForm">
              {{ showAddressForm ? 'Close' : 'Add new' }}
            </button>
          </div>

          <div v-if="addresses.length" class="address-list">
            <label v-for="address in addresses" :key="address.id" class="address-option" :class="{ selected: selectedAddressId === address.id }">
              <input v-model="selectedAddressId" type="radio" name="shipping-address" :value="address.id" />
              <span>
                <strong>{{ address.recipient_name }}</strong>
                <small>{{ address.street_address }}, {{ address.city }}, {{ address.postal_code }}</small>
                <small>{{ countryName(address.country) }} · {{ address.phone }}</small>
              </span>
              <em v-if="address.is_default">Default</em>
            </label>
          </div>

          <form v-if="showAddressForm || !addresses.length" class="address-form" @submit.prevent="saveAddress">
            <label>
              <span>Full name</span>
              <input v-model.trim="addressForm.recipient_name" autocomplete="name" required />
            </label>
            <label>
              <span>Phone</span>
              <input v-model.trim="addressForm.phone" type="tel" autocomplete="tel" required />
            </label>
            <label class="wide">
              <span>Street address</span>
              <input v-model.trim="addressForm.street_address" autocomplete="street-address" required />
            </label>
            <label>
              <span>City</span>
              <input v-model.trim="addressForm.city" autocomplete="address-level2" required />
            </label>
            <label>
              <span>Postal code</span>
              <input v-model.trim="addressForm.postal_code" autocomplete="postal-code" required />
            </label>
            <label class="wide">
              <span>Country</span>
              <select v-model="addressForm.country" autocomplete="country" required>
                <option value="" disabled>Select country</option>
                <option v-for="country in countries" :key="country.code" :value="country.code">
                  {{ country.flag_emoji }} {{ country.name_en || country.name }}
                </option>
              </select>
            </label>
            <label class="default-check wide">
              <input v-model="addressForm.is_default" type="checkbox" />
              <span>Use as my default address</span>
            </label>
            <button type="submit" class="save-address" :disabled="savingAddress">
              {{ savingAddress ? 'Saving…' : 'Save and use this address' }}
            </button>
          </form>
        </section>

        <section class="checkout-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">YOUR ORDER</span>
              <h2>{{ selectedUnits }} {{ selectedUnits === 1 ? 'item' : 'items' }}</h2>
            </div>
            <router-link to="/cart" class="text-button">Edit bag</router-link>
          </div>
          <div class="order-lines">
            <div v-for="item in selectedItems" :key="item.id || item.product_id" class="order-line">
              <img v-if="item.product?.images?.[0]" :src="item.product.images[0].thumbnail_url || item.product.images[0].image_url" :alt="item.product.title_en || item.product.title" />
              <span>
                <strong>{{ item.product?.title_en || item.product?.title }}</strong>
                <small>Qty {{ item.quantity }}</small>
              </span>
              <b>€{{ money(Number(item.product?.sale_price) * item.quantity) }}</b>
            </div>
          </div>
          <div class="totals">
            <div><span>Subtotal</span><strong>€{{ money(selectedTotal) }}</strong></div>
            <div v-if="promoDiscount" class="promo-total"><span>WELCOME10 promotion</span><strong>−€{{ money(promoDiscount) }}</strong></div>
            <div>
              <span>Standard delivery</span>
              <strong v-if="shippingLoading">Calculating…</strong>
              <strong v-else>€{{ money(shippingTotal) }}</strong>
            </div>
            <div><span>Tax</span><strong>Included where applicable</strong></div>
            <div class="grand-total"><span>Total</span><strong>€{{ money(grandTotal) }}</strong></div>
          </div>
          <p v-if="shippingError" class="inline-note">{{ shippingError }}</p>
        </section>

        <section class="checkout-card payment-card">
          <span class="eyebrow">PAYMENT</span>
          <h2>Secure card checkout</h2>
          <p>You’ll continue to Stripe to pay by card. Your order is confirmed only after payment succeeds.</p>
          <div class="secure-row"><span aria-hidden="true">✓</span> Encrypted payment · No card details stored here</div>
        </section>

        <label class="terms-row">
          <input v-model="termsAccepted" type="checkbox" />
          <span>I agree to the <router-link to="/legal/terms">terms</router-link> and <router-link to="/legal/returns">return policy</router-link>.</span>
        </label>
      </template>
    </main>

    <footer v-if="!loading && selectedItems.length" class="checkout-footer safe-bottom">
      <div class="footer-inner">
        <div><span>Total</span><strong>€{{ money(grandTotal) }}</strong></div>
        <button type="button" :disabled="!canPay || placing" @click="placeOrder">
          {{ placing ? 'Opening secure payment…' : 'Continue to payment' }} <span aria-hidden="true">→</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  createAddress,
  createCheckoutSession,
  createOrder,
  getAddresses,
  getCartShippingEstimate,
  getCountries,
} from '../api'
import { useCart } from '../composables/useCart'
import { useLocation } from '../composables/useLocation'

const router = useRouter()
const { selectedItems, selectedTotal, selectedUnits, fetchServer } = useCart()
const { countryCode, initLocation } = useLocation()

const loading = ref(true)
const error = ref('')
const addresses = ref([])
const countries = ref([])
const selectedAddressId = ref(null)
const showAddressForm = ref(false)
const savingAddress = ref(false)
const shippingLoading = ref(false)
const shippingTotal = ref(0)
const shippingError = ref('')
const termsAccepted = ref(false)
const placing = ref(false)
const createdOrderId = ref(null)
const couponCode = ref(sessionStorage.getItem('esh_promo_code') || '')
const addressForm = reactive({
  recipient_name: '',
  phone: '',
  street_address: '',
  city: '',
  postal_code: '',
  country: '',
  is_default: false,
})

const selectedAddress = computed(() => addresses.value.find(address => address.id === selectedAddressId.value))
const destinationCountry = computed(() => selectedAddress.value?.country || addressForm.country || countryCode.value || '')
const promoDiscount = computed(() => couponCode.value === 'WELCOME10' ? selectedItems.value.reduce((sum,item)=>sum + (Number(item.product?.sale_price||0)-Math.round(Number(item.product?.sale_price||0)*.9*100)/100)*item.quantity,0) : 0)
const discountedSubtotal = computed(() => Number(selectedTotal.value) - promoDiscount.value)
const grandTotal = computed(() => discountedSubtotal.value + Number(shippingTotal.value))
const canPay = computed(() => Boolean(
  selectedAddressId.value
  && selectedItems.value.length
  && termsAccepted.value
  && !shippingLoading.value
))

const money = value => Number(value || 0).toFixed(2)
const countryName = code => countries.value.find(country => country.code === code)?.name_en || code

const loadShipping = async () => {
  if (!destinationCountry.value || !selectedItems.value.length) return
  shippingLoading.value = true
  shippingError.value = ''
  try {
    const response = await getCartShippingEstimate(
      destinationCountry.value,
      selectedItems.value.map(item => item.product_id),
    )
    shippingTotal.value = Number(response.data.shipping_total || 0)
  } catch (requestError) {
    shippingTotal.value = 0
    shippingError.value = requestError.response?.data?.detail || 'Delivery could not be calculated for this address.'
  } finally {
    shippingLoading.value = false
  }
}

const saveAddress = async () => {
  savingAddress.value = true
  error.value = ''
  try {
    const response = await createAddress({ ...addressForm, label: 'Home' })
    addresses.value = [...addresses.value, response.data]
    selectedAddressId.value = response.data.id
    showAddressForm.value = false
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not save this address.'
  } finally {
    savingAddress.value = false
  }
}

const placeOrder = async () => {
  if (!canPay.value) return
  placing.value = true
  error.value = ''
  try {
    if (!createdOrderId.value) {
      const orderResponse = await createOrder({
        items: selectedItems.value.map(item => ({ product_id: item.product_id, quantity: item.quantity })),
        address_id: selectedAddressId.value,
        payment_method: 'stripe',
        shipping_method: 'Standard delivery',
        shipping_price: shippingTotal.value,
        coupon_code: couponCode.value || undefined,
      })
      createdOrderId.value = orderResponse.data.id
      sessionStorage.setItem('pending_order_id', String(orderResponse.data.id))
      await fetchServer({ silent: true })
    }
    const paymentResponse = await createCheckoutSession(createdOrderId.value)
    window.location.assign(paymentResponse.data.checkout_url)
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not start secure payment. Your pending order is saved in My Orders.'
  } finally {
    placing.value = false
  }
}

watch(selectedAddressId, loadShipping)

onMounted(async () => {
  await initLocation()
  if (!selectedItems.value.length) {
    router.replace('/cart')
    return
  }
  try {
    const [addressResult, countryResult] = await Promise.all([getAddresses(), getCountries()])
    addresses.value = addressResult.data || []
    countries.value = countryResult.data || []
    const defaultAddress = addresses.value.find(address => address.is_default) || addresses.value[0]
    if (defaultAddress) selectedAddressId.value = defaultAddress.id
    else {
      showAddressForm.value = true
      addressForm.country = countryCode.value || ''
    }
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not prepare checkout.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.checkout-page{min-height:100vh;padding-bottom:126px;background:#f5f2e9;color:#183f35}.checkout-header{position:sticky;top:0;z-index:40;border-bottom:1px solid rgba(23,72,59,.1);background:rgba(245,242,233,.95);backdrop-filter:blur(14px)}.header-inner{display:grid;grid-template-columns:48px 1fr 48px;align-items:center;max-width:760px;min-height:72px;margin:auto;padding:8px 14px}.back-button{width:44px;height:44px;border:1px solid #d8ded5;border-radius:50%;background:#fffdf8;font-size:20px}.eyebrow{display:block;color:#758177;font-size:9px;font-weight:850;letter-spacing:.18em}.header-inner h1,.checkout-card h2{margin:3px 0 0;font-family:Georgia,serif}.header-inner h1{font-size:21px}.step-pill{justify-self:end;color:#64756b;font-size:11px;font-weight:800}.checkout-shell{display:grid;gap:14px;max-width:760px;margin:auto;padding:16px 14px}.checkout-card{padding:18px;border:1px solid rgba(23,72,59,.09);border-radius:22px;background:#fffdf8;box-shadow:0 7px 24px rgba(31,59,48,.05)}.section-heading{display:flex;align-items:start;justify-content:space-between;gap:12px;margin-bottom:14px}.checkout-card h2{font-size:21px}.text-button{min-height:40px;display:inline-flex;align-items:center;color:#17483b;font-size:12px;font-weight:800;text-decoration:underline;text-underline-offset:3px}.address-list{display:grid;gap:9px}.address-option{display:grid;grid-template-columns:22px 1fr auto;gap:10px;align-items:start;padding:13px;border:1px solid #d9dfd6;border-radius:15px;cursor:pointer}.address-option.selected{border-color:#17483b;background:#f0f3e8}.address-option input{margin-top:3px;accent-color:#17483b}.address-option strong,.address-option small{display:block}.address-option strong{font-size:13px}.address-option small{margin-top:3px;color:#68776e;font-size:11px;line-height:1.4}.address-option em{padding:4px 7px;border-radius:999px;background:#d9f06a;font-size:9px;font-style:normal;font-weight:800}.address-form{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:14px;padding-top:14px;border-top:1px solid #e8ebe4}.address-form label{display:grid;gap:6px}.address-form label>span{font-size:11px;font-weight:750}.address-form .wide,.save-address{grid-column:1/-1}.address-form input:not([type=checkbox]),.address-form select{width:100%;min-height:46px;padding:0 12px;border:1px solid #d6ddd3;border-radius:12px;background:#fff;color:#183f35;font-size:13px}.default-check{grid-template-columns:20px 1fr!important;align-items:center}.default-check input{width:18px;height:18px;accent-color:#17483b}.save-address{min-height:48px;border-radius:999px;background:#e3ef86;color:#17483b;font-size:12px;font-weight:850}.order-lines{display:grid;gap:11px}.order-line{display:grid;grid-template-columns:54px 1fr auto;gap:11px;align-items:center}.order-line img{width:54px;height:64px;border-radius:10px;object-fit:cover}.order-line span strong,.order-line span small{display:block}.order-line span strong{font-family:Georgia,serif;font-size:14px}.order-line span small{margin-top:3px;color:#78857d;font-size:10px}.order-line b{font-family:Georgia,serif;font-size:15px}.totals{display:grid;gap:9px;margin-top:16px;padding-top:14px;border-top:1px solid #e7eae3}.totals div{display:flex;justify-content:space-between;color:#65756b;font-size:12px}.totals strong{color:#294b3f}.totals .promo-total,.totals .promo-total strong{color:#47704d}.totals .grand-total{padding-top:10px;border-top:1px solid #e7eae3;color:#183f35;font-size:16px;font-weight:800}.grand-total strong{font-family:Georgia,serif;font-size:23px}.inline-note,.payment-card p{color:#66766c;font-size:12px;line-height:1.55}.inline-note{margin:10px 0 0;color:#8a4a20}.secure-row{margin-top:13px;padding:11px;border-radius:13px;background:#eef3cb;font-size:11px;font-weight:750}.secure-row span{margin-right:7px}.terms-row{display:flex;align-items:start;gap:10px;padding:2px 5px;color:#607168;font-size:11px;line-height:1.45}.terms-row input{width:19px;height:19px;flex:none;accent-color:#17483b}.terms-row a{color:#17483b;font-weight:800;text-decoration:underline}.message,.loading-card{padding:14px;border-radius:14px;background:#fffdf8;font-size:13px}.message.error{border:1px solid #e4c2ac;background:#fff4eb;color:#74422b}.checkout-footer{position:fixed;right:0;bottom:0;left:0;z-index:50;border-top:1px solid rgba(23,72,59,.1);background:rgba(255,253,248,.96);box-shadow:0 -12px 34px rgba(31,59,48,.09);backdrop-filter:blur(14px)}.footer-inner{display:flex;max-width:760px;min-height:88px;margin:auto;padding:12px 14px;align-items:center;justify-content:space-between;gap:15px}.footer-inner>div span,.footer-inner>div strong{display:block}.footer-inner>div span{color:#718078;font-size:10px}.footer-inner>div strong{font-family:Georgia,serif;font-size:25px}.footer-inner button{min-height:52px;padding:0 20px;border-radius:999px;background:#17483b;color:#fffdf8;font-size:12px;font-weight:850}.footer-inner button:disabled{background:#9da8a2}.checkout-page button:focus-visible,.checkout-page a:focus-visible,.checkout-page input:focus-visible,.checkout-page select:focus-visible{outline:3px solid #d9f06a;outline-offset:2px}@media(max-width:480px){.address-form{grid-template-columns:1fr}.address-form .wide,.save-address{grid-column:auto}.footer-inner button{padding:0 16px}}
</style>
