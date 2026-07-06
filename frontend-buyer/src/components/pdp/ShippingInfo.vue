<template>
  <div class="mb-6 bg-white rounded-xl border border-gray-200 overflow-hidden">
    <!-- Title -->
    <div class="px-4 pt-4 pb-3">
      <h3 class="text-base font-semibold text-gray-900">{{ settings.section_title || 'Shipping, returns, and payments' }}</h3>
    </div>

    <div class="divide-y divide-gray-200">
      <!-- Shipping -->
      <div class="px-4 py-3">
        <div class="flex gap-3">
          <span class="w-[110px] flex-shrink-0 text-sm font-medium text-gray-500 text-right">Shipping:</span>
          <div class="flex-1 min-w-0">
            <!-- Shipping cost - dynamic from backend -->
            <div v-if="cheapestOption" class="text-sm font-semibold text-gray-900">
              €{{ Number(cheapestOption.total_fee).toFixed(2) }}
              <span class="font-normal text-gray-600 ml-1">{{ cheapestOption.shipping_method }}</span>
              <button class="text-gray-400 hover:text-blue-600 ml-1 inline-flex items-center" title="More info">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </button>
            </div>
            <div v-else class="text-sm text-gray-600">
              Shipping calculated at checkout
            </div>

            <!-- Shipping origin -->
            <div v-if="originCountryName" class="text-xs text-gray-400 mt-1">
              Located in: {{ originCountryName }}
            </div>

            <!-- Combined shipping note -->
            <div v-if="settings.show_combined_shipping" class="text-xs text-gray-400 mt-1 flex items-center gap-1">
              {{ settings.combined_shipping_text }}
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Import fees -->
      <div v-if="settings.show_import_fees" class="px-4 py-3">
        <div class="flex gap-3">
          <span class="w-[110px] flex-shrink-0 text-sm font-medium text-gray-500 text-right">Import fees:</span>
          <div class="flex-1 min-w-0">
            <span class="text-sm text-gray-600">{{ settings.import_fees_text }}</span>
            <button class="text-gray-400 hover:text-blue-600 ml-1 inline-flex items-center" title="More info">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Delivery -->
      <div class="px-4 py-3">
        <div class="flex gap-3">
          <span class="w-[110px] flex-shrink-0 text-sm font-medium text-gray-500 text-right">Delivery:</span>
          <div class="flex-1 min-w-0">
            <span v-if="deliveryText" class="text-sm text-gray-600">{{ deliveryText }}</span>
            <span v-else class="text-sm text-gray-400">Estimated delivery will be shown at checkout</span>
            <button v-if="deliveryText" class="text-gray-400 hover:text-blue-600 ml-1 inline-flex items-center" title="More info">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Returns -->
      <div class="px-4 py-3">
        <div class="flex gap-3">
          <span class="w-[110px] flex-shrink-0 text-sm font-medium text-gray-500 text-right">Returns:</span>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-600 leading-relaxed">
              {{ returnsText }}
              <button class="text-blue-600 hover:underline ml-1">See details</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payments -->
      <div class="px-4 py-3">
        <div class="flex gap-3">
          <span class="w-[110px] flex-shrink-0 text-sm font-medium text-gray-500 text-right">Payments:</span>
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
              <!-- Payment icons from backend -->
              <span v-for="pay in paymentMethods" :key="pay.code"
                    class="inline-flex items-center justify-center h-7 px-2 border border-gray-200 rounded text-[11px] font-semibold"
                    :style="pay.color ? { color: pay.text_color || '#374151', backgroundColor: pay.color } : {}">
                {{ pay.name_en || pay.name }}
              </span>
              <!-- Fallback if no payment methods configured -->
              <span v-if="!paymentMethods.length" class="text-sm text-gray-400">Payment methods will be shown at checkout</span>
            </div>
            <button class="text-blue-600 hover:underline text-sm">See details</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getShippingOptions, getShippingNotes, getReturnPolicy, getPaymentMethods, getShippingSettings } from '@/api'

const props = defineProps({
  productSlug: String,
  productId: Number,
  countryCode: String,
  originCountryName: String,
})

const shippingOptions = ref([])
const shippingNotes = ref([])
const returnPolicy = ref(null)
const paymentMethods = ref([])
const settings = ref({
  section_title: 'Shipping, returns, and payments',
  show_combined_shipping: true,
  combined_shipping_text: 'Save on combined shipping',
  show_import_fees: true,
  import_fees_text: 'Import fees may apply on delivery',
})
const loading = ref(false)

// ========================================
// 动态数据（从后端加载）
// ========================================

const cheapestOption = computed(() => {
  if (!shippingOptions.value.length) return null
  return shippingOptions.value[0] // 已按 default-first, price 排序
})

const deliveryText = computed(() => {
  if (!cheapestOption.value) return ''
  const min = cheapestOption.value.estimated_days_min
  const max = cheapestOption.value.estimated_days_max
  if (min && max) {
    return `Estimated between ${min}-${max} business days`
  }
  return ''
})

const returnsText = computed(() => {
  if (!returnPolicy.value) {
    return '30 days returns. Buyer pays for return shipping.'
  }
  const policy = returnPolicy.value
  let text = ''
  if (policy.return_days > 0) {
    text += `${policy.return_days} days returns. `
  } else {
    return 'No returns accepted.'
  }
  if (policy.buyer_pays_return_shipping) {
    text += 'Buyer pays for return shipping. '
  } else {
    text += 'Free returns. '
  }
  if (policy.restocking_fee_percent > 0) {
    text += `${policy.restocking_fee_percent}% restocking fee applies.`
  } else {
    text += 'No restocking fee.'
  }
  return text
})

async function loadShippingData() {
  if (!props.productSlug || !props.countryCode) return

  loading.value = true
  try {
    const { data } = await getShippingOptions(props.productSlug, props.countryCode)
    shippingOptions.value = data || []
  } catch {
    shippingOptions.value = []
  }

  try {
    const { data } = await getShippingNotes(props.productSlug)
    shippingNotes.value = data || []
  } catch {
    shippingNotes.value = []
  }
  loading.value = false
}

async function loadReturnPolicy() {
  if (!props.productId) return
  try {
    const { data } = await getReturnPolicy(props.productId)
    returnPolicy.value = data
  } catch {
    returnPolicy.value = null
  }
}

async function loadPaymentMethods() {
  try {
    const { data } = await getPaymentMethods()
    paymentMethods.value = data || []
  } catch {
    paymentMethods.value = []
  }
}

async function loadShippingSettings() {
  try {
    const { data } = await getShippingSettings()
    settings.value = {
      section_title: data.section_title,
      show_combined_shipping: !!data.show_combined_shipping,
      combined_shipping_text: data.combined_shipping_text,
      show_import_fees: !!data.show_import_fees,
      import_fees_text: data.import_fees_text,
    }
  } catch {
    // Use defaults on error
  }
}

onMounted(() => {
  loadShippingData()
  loadReturnPolicy()
  loadPaymentMethods()
  loadShippingSettings()
})
watch(() => [props.productSlug, props.countryCode], loadShippingData)
watch(() => props.productId, loadReturnPolicy, { immediate: true })
</script>
