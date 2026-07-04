<template>
  <div class="mb-6 rounded-xl py-4 pl-4 pr-4 overflow-visible border-t border-b border-gray-200">
    <!-- Shipping Origin -->
    <div v-if="originCountryCode" class="mb-4">
      <div class="text-sm font-medium text-gray-900 mb-1 -ml-4">Shipping Origin</div>
      <div class="flex items-center gap-2">
        <span class="text-xl">{{ originFlag }}</span>
        <span class="text-gray-700">{{ originCountryName }}</span>
      </div>
    </div>

    <h3 class="text-sm font-medium text-gray-900 mb-3 -ml-4">Shipping Options</h3>

      <!-- Country selector -->
      <div class="mb-4 px-4">
        <!-- Auto-detected indicator -->
        <div v-if="detectedLocation" class="flex items-center justify-between mb-2">
          <span class="text-xs text-gray-400">
            📍 Shipping to <strong>{{ destinationCountryName }}</strong>
            <button @click="showSelector = true" class="text-primary ml-1 hover:underline text-xs">Change</button>
          </span>
        </div>
        <select
          v-if="showSelector"
          v-model="selectedCountry"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-orange-400 outline-none"
        >
          <option value="" disabled>Select destination</option>
          <option v-for="c in countries" :key="c.code" :value="c.code">
            {{ c.flag_emoji }} {{ c.name_en || c.name }}
          </option>
        </select>
      </div>

      <!-- Shipping options table -->
      <div v-if="selectedCountry && filteredOptions.length" class="mx-4 bg-white rounded-lg overflow-hidden border border-gray-200">
        <table class="w-full text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="text-left py-2 px-3 font-medium text-gray-600">Method</th>
              <th class="text-right py-2 px-3 font-medium text-gray-600">Price</th>
              <th class="text-right py-2 px-3 font-medium text-gray-600">Est. Delivery</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="opt in filteredOptions" :key="opt.shipping_method"
                class="border-t border-gray-100 hover:bg-gray-50"
                :class="{ 'bg-orange-50 border-orange-200': opt.is_default }">
              <td class="py-2 px-3">
                {{ opt.shipping_method }}
                <span v-if="opt.is_default" class="text-xs bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded ml-1">Default</span>
              </td>
              <td class="text-right font-semibold text-primary px-3">€{{ Number(opt.total_fee).toFixed(2) }}</td>
              <td class="text-right text-gray-500 text-xs px-3">
                {{ opt.estimated_days_min }}-{{ opt.estimated_days_max }} days
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-else-if="selectedCountry" class="text-gray-400 text-sm text-center py-4 px-4">
        No shipping options available for this country.
      </p>

      <p v-else class="text-gray-400 text-sm text-center py-2 px-4">
        Select a country to see shipping costs.
      </p>

    <!-- Shipping Notes -->
    <div v-if="shippingNotes.length" class="mt-5 mx-4">
      <h4 class="text-sm font-medium text-gray-900 mb-3 -ml-4">Shipping Information</h4>
      <div class="space-y-3">
        <div v-for="note in shippingNotes" :key="note.id" class="flex gap-3 items-start">
          <span class="text-primary mt-0.5 flex-shrink-0">📋</span>
          <div>
            <div class="text-sm font-medium text-gray-900">{{ note.title_en || note.title }}</div>
            <div v-if="note.content_en || note.content" class="text-xs text-gray-500 mt-0.5 leading-relaxed">
              {{ note.content_en || note.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getShippingTable, getShippingNotes, getCountries } from '@/api'
import { useLocation } from '@/composables/useLocation'
import { useCountries } from '@/composables/useCountries'

const props = defineProps({
  productSlug: String,
  originCountryCode: String,
  originFlag: String,
  originCountryName: String,
})

const { countryCode: detectedCountry, initLocation } = useLocation()
const { getCountryName } = useCountries()

const countries = ref([])
const selectedCountry = ref('')
const allOptions = ref([])
const shippingNotes = ref([])
const showSelector = ref(false)
const detectedLocation = ref(false)

const filteredOptions = computed(() => {
  if (!selectedCountry.value) return []
  const country = allOptions.value.find(c => c.country_code === selectedCountry.value)
  return country?.options || []
})

const destinationCountryName = computed(() => {
  if (!selectedCountry.value) return ''
  return getCountryName(selectedCountry.value) || selectedCountry.value
})

watch(selectedCountry, () => {
  // Options are pre-loaded for all countries
})

onMounted(async () => {
  try {
    const { data } = await getCountries()
    countries.value = data
  } catch {}

  // Try to detect user location
  const detected = await initLocation()
  if (detected && countries.value.find(c => c.code === detected)) {
    selectedCountry.value = detected
    detectedLocation.value = true
    showSelector.value = false
  } else {
    // Fallback: pre-select DE or first country
    const common = countries.value.find(c => c.code === 'DE')
    if (common) selectedCountry.value = common.code
    else if (countries.value.length > 0) selectedCountry.value = countries.value[0].code
    showSelector.value = true
  }

  if (props.productSlug && props.productSlug.trim()) {
    try {
      const { data } = await getShippingTable(props.productSlug)
      allOptions.value = data
    } catch (e) {
      console.error('Failed to load shipping table:', e)
    }

    // Load shipping notes
    try {
      const { data } = await getShippingNotes(props.productSlug)
      shippingNotes.value = data || []
    } catch (e) {
      console.error('Failed to load shipping notes:', e)
    }
  }
})

// 监听 productSlug 变化，重新加载运费表和配送说明
watch(() => props.productSlug, async (newSlug) => {
  if (newSlug && newSlug.trim()) {
    try {
      const { data } = await getShippingTable(newSlug)
      allOptions.value = data
    } catch (e) {
      console.error('Failed to load shipping table:', e)
    }
    try {
      const { data } = await getShippingNotes(newSlug)
      shippingNotes.value = data || []
    } catch (e) {
      console.error('Failed to load shipping notes:', e)
    }
  }
})
</script>
