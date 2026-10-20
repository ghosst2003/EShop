<template>
  <div><Navbar /><div class="checkout-page">
    <header class="checkout-header safe-top">
      <div class="header-inner">
        <button type="button" class="back-button" aria-label="Go back" @click="router.back()">←</button>
        <div>
          <span class="eyebrow">{{ checkoutMode === 'mixed' ? 'CHECKOUT OPTIONS' : checkoutMode === 'in_person' ? 'MEETUP RESERVATION' : 'SECURE CHECKOUT' }}</span>
          <h1>{{ checkoutMode === 'mixed' ? 'Choose how to checkout' : checkoutMode === 'in_person' ? 'Reserve your meetup' : 'Finish your order' }}</h1>
        </div>
        <span class="step-pill">1 / 1</span>
      </div>
    </header>

    <main class="checkout-shell">
      <div v-if="error" class="message error" role="alert">{{ error }}</div>
      <div v-if="loading" class="loading-card" aria-live="polite">Preparing checkout…</div>

      <template v-else>
        <section v-if="availableModes.length > 1" class="checkout-card mode-picker" aria-labelledby="checkout-mode-title">
          <span class="eyebrow">CHECKOUT TYPE</span>
          <h2 id="checkout-mode-title">Choose one group</h2>
          <p>Delivery and meetup items use different payment flows. Choose a group now; the other items stay in your bag.</p>
          <div class="mode-options">
            <button type="button" :class="{ selected: checkoutMode === 'online' }" @click="selectCheckoutMode('online')">
              <span aria-hidden="true">↗</span>
              <strong>Delivery & online payment</strong>
              <small>{{ modeSummary('online') }}</small>
            </button>
            <button type="button" :class="{ selected: checkoutMode === 'in_person' }" @click="selectCheckoutMode('in_person')">
              <span aria-hidden="true">◎</span>
              <strong>Face-to-face meetup</strong>
              <small>{{ modeSummary('in_person') }}</small>
            </button>
          </div>
        </section>

        <template v-if="checkoutMode !== 'mixed'">
        <section v-if="checkoutMode === 'online'" class="checkout-card details-card">
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

        <section v-else class="checkout-card meetup-card details-card">
          <div class="section-heading"><div><span class="eyebrow">MEETUP</span><h2>Face-to-face details</h2></div><em>48-hour hold</em></div>
          <dl>
            <div><dt>Location</dt><dd>{{ meetupDetails.location }}</dd></div>
            <div v-if="meetupDetails.schedule"><dt>Available times</dt><dd>{{ meetupDetails.schedule }}</dd></div>
            <div><dt>Payment</dt><dd>{{ meetupDetails.payment }}</dd></div>
          </dl>
          <p v-if="meetupDetails.instructions" class="meetup-note">{{ meetupDetails.instructions }}</p>
          <div class="contact-form">
            <label><span>Your name</span><input v-model.trim="meetupBuyer.name" autocomplete="name" required /></label>
            <label><span>Phone or WhatsApp</span><input v-model.trim="meetupBuyer.phone" type="tel" autocomplete="tel" required /></label>
            <label class="wide"><span>Message for the meetup <small>optional</small></span><textarea v-model.trim="meetupBuyer.note" placeholder="Preferred day or anything the seller should know"></textarea></label>
          </div>
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
            <div v-if="promoDiscount" class="promo-total"><span>{{ promotion?.label || couponCode }} promotion</span><strong>−€{{ money(promoDiscount) }}</strong></div>
            <div>
              <span>{{ checkoutMode === 'in_person' ? 'Collection' : 'Standard delivery' }}</span>
              <strong v-if="checkoutMode === 'in_person'">At meetup</strong>
              <strong v-else-if="shippingLoading">Calculating…</strong>
              <strong v-else>€{{ money(shippingTotal) }}</strong>
            </div>
            <div><span>Tax</span><strong>Included where applicable</strong></div>
            <div class="grand-total"><span>Total</span><strong>€{{ money(grandTotal) }}</strong></div>
          </div>
          <p v-if="shippingError" class="inline-note">{{ shippingError }}</p>
        </section>

        <section class="checkout-card payment-card">
          <span class="eyebrow">{{ checkoutMode === 'in_person' ? 'PAY AT MEETUP' : 'PAYMENT' }}</span>
          <h2>{{ checkoutMode === 'in_person' ? 'Inspect first, then pay' : 'Secure card checkout' }}</h2>
          <p>{{ checkoutMode === 'in_person' ? 'No online payment is taken. The private contact details appear in your order after reservation.' : 'You’ll continue to Stripe to pay by card. Your order is confirmed only after payment succeeds.' }}</p>
          <div class="secure-row"><span aria-hidden="true">✓</span> {{ checkoutMode === 'in_person' ? 'No card required · cancel before meeting if plans change' : 'Encrypted payment · No card details stored here' }}</div>
        </section>

        <label class="terms-row">
          <input v-model="termsAccepted" type="checkbox" />
          <span>I agree to the <router-link to="/terms">terms</router-link> and <router-link to="/terms">return policy</router-link>{{ checkoutMode === 'in_person' ? ', and understand that payment happens at the meetup.' : '.' }}</span>
        </label>
        </template>
      </template>
    </main>

    <footer v-if="!loading && selectedItems.length && checkoutMode !== 'mixed'" class="checkout-footer safe-bottom">
      <div class="footer-inner">
        <div><span>Total</span><strong>€{{ money(grandTotal) }}</strong></div>
        <button type="button" :disabled="!canPay || placing" @click="placeOrder">
          {{ placing ? (checkoutMode === 'in_person' ? 'Reserving…' : 'Opening secure payment…') : (checkoutMode === 'in_person' ? 'Reserve meetup' : 'Continue to payment') }} <span aria-hidden="true">→</span>
        </button>
      </div>
    </footer>
  </div></div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  createAddress,
  createCheckoutSession,
  createOrder,
  getAddresses,
  getCartShippingEstimate,
  getCountries,
  validatePromotion,
} from '../api'
import { useCart } from '../composables/useCart'
import { useAuth } from '../composables/useAuth'
import { useLocation } from '../composables/useLocation'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const { items, selectedIds, selectedItems, selectedTotal, selectedUnits, fetchServer } = useCart()
const { user } = useAuth()
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
const authoritativeTotal = ref(null)
const termsAccepted = ref(false)
const placing = ref(false)
const createdOrderId = ref(null)
const checkoutAttemptKey = ref(sessionStorage.getItem('esh_checkout_idempotency_key') || crypto.randomUUID())
sessionStorage.setItem('esh_checkout_idempotency_key', checkoutAttemptKey.value)
const couponCode = ref(sessionStorage.getItem('esh_promo_code') || '')
const promotion = ref(null)
const addressForm = reactive({
  recipient_name: '',
  phone: '',
  street_address: '',
  city: '',
  postal_code: '',
  country: '',
  is_default: false,
})
const meetupBuyer = reactive({ name: user.value?.display_name || user.value?.username || '', phone: user.value?.phone || '', note: '' })

const selectedModes = computed(() => [...new Set(selectedItems.value.map(item => item.product?.transaction_mode || 'online'))])
const checkoutMode = computed(() => selectedModes.value.length === 1 ? selectedModes.value[0] : 'mixed')
const availableModes = computed(() => [...new Set(items.value.map(item => item.product?.transaction_mode || 'online'))])
const meetupDetails = computed(() => {
  const product = selectedItems.value[0]?.product || {}
  return {
    location: product.pickup_location || 'Location confirmed after reservation',
    schedule: product.pickup_schedule || '',
    payment: product.pickup_payment || 'Pay at the meetup',
    instructions: product.pickup_instructions || '',
  }
})
const selectedAddress = computed(() => addresses.value.find(address => address.id === selectedAddressId.value))
const destinationCountry = computed(() => selectedAddress.value?.country || addressForm.country || countryCode.value || '')
const promoDiscount = computed(() => Number(promotion.value?.discount_amount || 0))
const discountedSubtotal = computed(() => Number(selectedTotal.value) - promoDiscount.value)
const grandTotal = computed(() => authoritativeTotal.value ?? (discountedSubtotal.value + Number(shippingTotal.value)))
const canPay = computed(() => Boolean(
  selectedItems.value.length
  && termsAccepted.value
  && checkoutMode.value !== 'mixed'
  && (checkoutMode.value === 'in_person'
    ? meetupBuyer.name && meetupBuyer.phone
    : selectedAddressId.value && !shippingLoading.value && !shippingError.value)
))

const money = value => Number(value || 0).toFixed(2)
const countryName = code => countries.value.find(country => country.code === code)?.name_en || code
const modeItems = mode => items.value.filter(item => (item.product?.transaction_mode || 'online') === mode)
const modeSummary = mode => {
  const group = modeItems(mode)
  const units = group.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
  const total = group.reduce((sum, item) => sum + Number(item.product?.sale_price || 0) * Number(item.quantity || 0), 0)
  return `${units} ${units === 1 ? 'item' : 'items'} · €${money(total)}`
}

const selectCheckoutMode = async mode => {
  selectedIds.value = modeItems(mode).map(item => item.product_id)
  error.value = ''
  authoritativeTotal.value = null
  createdOrderId.value = null
  checkoutAttemptKey.value = crypto.randomUUID()
  sessionStorage.setItem('esh_checkout_idempotency_key', checkoutAttemptKey.value)
  await nextTick()
  if (couponCode.value) {
    try {
      promotion.value = (await validatePromotion(couponCode.value, selectedTotal.value)).data
    } catch {
      promotion.value = null
      couponCode.value = ''
      sessionStorage.removeItem('esh_promo_code')
    }
  }
  await loadShipping()
}

const loadShipping = async () => {
  if (checkoutMode.value !== 'online') {
    shippingTotal.value = 0
    shippingError.value = ''
    return
  }
  if (!destinationCountry.value || !selectedItems.value.length) return
  shippingLoading.value = true
  shippingError.value = ''
  authoritativeTotal.value = null
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
        address_id: checkoutMode.value === 'online' ? selectedAddressId.value : undefined,
        buyer_name: checkoutMode.value === 'in_person' ? meetupBuyer.name : undefined,
        buyer_phone: checkoutMode.value === 'in_person' ? meetupBuyer.phone : undefined,
        payment_method: checkoutMode.value === 'in_person' ? 'in_person' : 'stripe',
        coupon_code: couponCode.value || undefined,
        notes: checkoutMode.value === 'in_person' ? meetupBuyer.note || undefined : undefined,
        idempotency_key: checkoutAttemptKey.value,
      })
      createdOrderId.value = orderResponse.data.id
      shippingTotal.value = Number(orderResponse.data.financials?.shipping_amount ?? orderResponse.data.shipping_price ?? 0)
      authoritativeTotal.value = Number(orderResponse.data.total_amount)
      sessionStorage.setItem('pending_order_id', String(orderResponse.data.id))
      await fetchServer({ silent: true })
    }
    sessionStorage.removeItem('esh_checkout_idempotency_key')
    if (checkoutMode.value === 'in_person') {
      sessionStorage.removeItem('esh_promo_code')
      router.replace({ path: `/my-orders/${createdOrderId.value}`, query: { meetup: 'reserved' } })
    } else {
      const paymentResponse = await createCheckoutSession(createdOrderId.value)
      window.location.assign(paymentResponse.data.checkout_url)
    }
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not start secure payment. Your pending order is saved in My Orders.'
  } finally {
    placing.value = false
  }
}

watch([selectedAddressId, checkoutMode], loadShipping)

onMounted(async () => {
  await initLocation()
  await fetchServer({ silent: true }).catch(() => {})
  if (!selectedItems.value.length) {
    router.replace('/cart')
    return
  }
  try {
    const [addressResult, countryResult, promotionResult] = await Promise.all([
      getAddresses(), getCountries(),
      couponCode.value ? validatePromotion(couponCode.value, selectedTotal.value).catch(() => null) : Promise.resolve(null),
    ])
    addresses.value = addressResult.data || []
    countries.value = countryResult.data || []
    promotion.value = promotionResult?.data || null
    if (couponCode.value && !promotion.value) {
      couponCode.value = ''
      sessionStorage.removeItem('esh_promo_code')
    }
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
.mode-picker>p{margin:8px 0 14px;color:#66766c;font-size:12px;line-height:1.55}.mode-options{display:grid;grid-template-columns:1fr 1fr;gap:10px}.mode-options button{display:grid;grid-template-columns:36px 1fr;gap:2px 10px;min-height:78px;padding:12px;border:1px solid #d7ddd4;border-radius:15px;background:#f8f7f0;color:#183f35;text-align:left}.mode-options button>span{display:grid;grid-row:1/3;width:34px;height:34px;place-items:center;border-radius:50%;background:#e8ece4;font-size:18px}.mode-options button strong{align-self:end;font-size:12px}.mode-options button small{color:#748178;font-size:10px}.mode-options button.selected{border-color:#17483b;background:#eef3cb;box-shadow:inset 0 0 0 1px #17483b}.mode-options button.selected>span{background:#d9f06a}@media(max-width:520px){.mode-options{grid-template-columns:1fr}}
.meetup-card .section-heading em{padding:6px 9px;border-radius:999px;background:#dff263;color:#173f34;font-size:9px;font-style:normal;font-weight:900}.meetup-card dl{margin:0}.meetup-card dl div{display:grid;grid-template-columns:95px 1fr;gap:12px;padding:9px 0;border-top:1px solid #e7eae3}.meetup-card dt{color:#718078;font-size:11px}.meetup-card dd{margin:0;color:#173f34;font-size:12px;font-weight:750;line-height:1.45}.meetup-note{padding:11px;border-radius:13px;background:#f2f0e7;color:#65736c;font-size:11px;line-height:1.5}.contact-form{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:15px;padding-top:15px;border-top:1px solid #e7eae3}.contact-form label{display:grid;gap:6px}.contact-form label>span{font-size:11px;font-weight:800}.contact-form small{color:#849088}.contact-form input,.contact-form textarea{width:100%;border:1px solid #d6ddd3;border-radius:12px;background:#fff;padding:12px;color:#183f35;font-size:13px}.contact-form textarea{min-height:78px;resize:vertical}.contact-form .wide{grid-column:1/-1}@media(max-width:480px){.contact-form{grid-template-columns:1fr}.contact-form .wide{grid-column:auto}}
</style>

<style scoped>
.checkout-page{min-height:100vh;padding-bottom:126px;background:#f5f2e9;color:#183f35}.checkout-header{position:sticky;top:0;z-index:40;border-bottom:1px solid rgba(23,72,59,.1);background:rgba(245,242,233,.95);backdrop-filter:blur(14px)}.header-inner{display:grid;grid-template-columns:48px 1fr 48px;align-items:center;max-width:760px;min-height:72px;margin:auto;padding:8px 14px}.back-button{width:44px;height:44px;border:1px solid #d8ded5;border-radius:50%;background:#fffdf8;font-size:20px}.eyebrow{display:block;color:#758177;font-size:9px;font-weight:850;letter-spacing:.18em}.header-inner h1,.checkout-card h2{margin:3px 0 0;font-family:Georgia,serif}.header-inner h1{font-size:21px}.step-pill{justify-self:end;color:#64756b;font-size:11px;font-weight:800}.checkout-shell{display:grid;gap:14px;max-width:760px;margin:auto;padding:16px 14px}.checkout-card{padding:18px;border:1px solid rgba(23,72,59,.09);border-radius:22px;background:#fffdf8;box-shadow:0 7px 24px rgba(31,59,48,.05)}.section-heading{display:flex;align-items:start;justify-content:space-between;gap:12px;margin-bottom:14px}.checkout-card h2{font-size:21px}.text-button{min-height:40px;display:inline-flex;align-items:center;color:#17483b;font-size:12px;font-weight:800;text-decoration:underline;text-underline-offset:3px}.address-list{display:grid;gap:9px}.address-option{display:grid;grid-template-columns:22px 1fr auto;gap:10px;align-items:start;padding:13px;border:1px solid #d9dfd6;border-radius:15px;cursor:pointer}.address-option.selected{border-color:#17483b;background:#f0f3e8}.address-option input{margin-top:3px;accent-color:#17483b}.address-option strong,.address-option small{display:block}.address-option strong{font-size:13px}.address-option small{margin-top:3px;color:#68776e;font-size:11px;line-height:1.4}.address-option em{padding:4px 7px;border-radius:999px;background:#d9f06a;font-size:9px;font-style:normal;font-weight:800}.address-form{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:14px;padding-top:14px;border-top:1px solid #e8ebe4}.address-form label{display:grid;gap:6px}.address-form label>span{font-size:11px;font-weight:750}.address-form .wide,.save-address{grid-column:1/-1}.address-form input:not([type=checkbox]),.address-form select{width:100%;min-height:46px;padding:0 12px;border:1px solid #d6ddd3;border-radius:12px;background:#fff;color:#183f35;font-size:13px}.default-check{grid-template-columns:20px 1fr!important;align-items:center}.default-check input{width:18px;height:18px;accent-color:#17483b}.save-address{min-height:48px;border-radius:999px;background:#e3ef86;color:#17483b;font-size:12px;font-weight:850}.order-lines{display:grid;gap:11px}.order-line{display:grid;grid-template-columns:54px 1fr auto;gap:11px;align-items:center}.order-line img{width:54px;height:64px;border-radius:10px;object-fit:cover}.order-line span strong,.order-line span small{display:block}.order-line span strong{font-family:Georgia,serif;font-size:14px}.order-line span small{margin-top:3px;color:#78857d;font-size:10px}.order-line b{font-family:Georgia,serif;font-size:15px}.totals{display:grid;gap:9px;margin-top:16px;padding-top:14px;border-top:1px solid #e7eae3}.totals div{display:flex;justify-content:space-between;color:#65756b;font-size:12px}.totals strong{color:#294b3f}.totals .promo-total,.totals .promo-total strong{color:#47704d}.totals .grand-total{padding-top:10px;border-top:1px solid #e7eae3;color:#183f35;font-size:16px;font-weight:800}.grand-total strong{font-family:Georgia,serif;font-size:23px}.inline-note,.payment-card p{color:#66766c;font-size:12px;line-height:1.55}.inline-note{margin:10px 0 0;color:#8a4a20}.secure-row{margin-top:13px;padding:11px;border-radius:13px;background:#eef3cb;font-size:11px;font-weight:750}.secure-row span{margin-right:7px}.terms-row{display:flex;align-items:start;gap:10px;padding:2px 5px;color:#607168;font-size:11px;line-height:1.45}.terms-row input{width:19px;height:19px;flex:none;accent-color:#17483b}.terms-row a{color:#17483b;font-weight:800;text-decoration:underline}.message,.loading-card{padding:14px;border-radius:14px;background:#fffdf8;font-size:13px}.message.error{border:1px solid #e4c2ac;background:#fff4eb;color:#74422b}.checkout-footer{position:fixed;right:0;bottom:0;left:0;z-index:50;border-top:1px solid rgba(23,72,59,.1);background:rgba(255,253,248,.96);box-shadow:0 -12px 34px rgba(31,59,48,.09);backdrop-filter:blur(14px)}.footer-inner{display:flex;max-width:760px;min-height:88px;margin:auto;padding:12px 14px;align-items:center;justify-content:space-between;gap:15px}.footer-inner>div span,.footer-inner>div strong{display:block}.footer-inner>div span{color:#718078;font-size:10px}.footer-inner>div strong{font-family:Georgia,serif;font-size:25px}.footer-inner button{min-height:52px;padding:0 20px;border-radius:999px;background:#17483b;color:#fffdf8;font-size:12px;font-weight:850}.footer-inner button:disabled{background:#9da8a2}.checkout-page button:focus-visible,.checkout-page a:focus-visible,.checkout-page input:focus-visible,.checkout-page select:focus-visible{outline:3px solid #d9f06a;outline-offset:2px}@media(max-width:480px){.address-form{grid-template-columns:1fr}.address-form .wide,.save-address{grid-column:auto}.footer-inner button{padding:0 16px}}
@media(min-width:900px){.header-inner,.checkout-shell,.footer-inner{max-width:980px}.header-inner{min-height:92px;padding-inline:20px}.header-inner h1{font-size:28px}.checkout-shell{grid-template-columns:1.15fr .85fr;align-items:start;padding:28px 20px}.checkout-shell>.message,.checkout-shell>.loading-card,.checkout-shell>.terms-row,.checkout-shell>.mode-picker{grid-column:1/-1}.details-card{grid-row:span 3}.checkout-card{padding:25px}.payment-card{grid-column:2}.checkout-footer{position:static}.footer-inner{justify-content:flex-end;padding:20px}.footer-inner>div{margin-right:auto}}
</style>
