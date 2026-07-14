<template>
  <div>
    <!-- Main Header -->
    <nav class="bg-primary sticky top-0 z-40">
      <div class="max-w-[1440px] mx-auto px-10">
        <div class="grid grid-cols-[auto_1fr_auto] items-center h-[72px] gap-6">
          <!-- Logo + Nav (left) -->
          <div class="flex items-center gap-6">
            <router-link to="/" class="flex items-center gap-2.5 shrink-0">
              <span class="w-[40px] h-[40px] bg-white rounded-lg flex items-center justify-center text-primary font-black text-[22px]">C</span>
              <div class="hidden sm:block leading-tight">
                <span class="text-white font-extrabold text-[22px] block">BeCool Market</span>
                <span class="text-orange-200 text-[11px]">Buy · Sell · Save</span>
              </div>
            </router-link>
            <div class="hidden md:flex items-center gap-6">
              <router-link to="/" class="text-white font-semibold text-[14px]">Home</router-link>
              <router-link to="/browse" class="text-orange-200 hover:text-white text-[14px] transition">Browse</router-link>
            </div>
          </div>

          <!-- Search Bar (center) -->
          <div class="hidden md:flex justify-center">
            <div class="relative w-full max-w-[520px]">
              <div class="bg-white rounded-full h-10 flex items-center pr-1">
                <span class="pl-4 text-gray-400 mr-1.5"></span>
                <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  type="text"
                  placeholder="Search for anything..."
                  class="bg-transparent outline-none text-[14px] text-gray-600 flex-1"
                />
                <button @click="handleSearch"
                  class="bg-primary-light text-white rounded-full w-10 h-[38px] flex items-center justify-center text-base hover:bg-primary transition">
                  🔍
                </button>
              </div>
            </div>
          </div>

          <!-- Cart, Sign In, Sign Up (right) -->
          <div class="flex items-center gap-3">
            <!-- Delivery Address Pill -->
            <div class="relative" data-delivery-pill>
              <button
                @click="showDeliveryDropdown = !showDeliveryDropdown"
                class="flex items-center gap-1.5 bg-primary-light rounded-full h-10 px-5 hover:bg-primary transition cursor-pointer"
              >
                <svg class="w-4 h-4 text-white shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                <div class="leading-tight text-left">
                  <div class="text-orange-200 text-[10px] leading-none mb-0.5">Deliver to</div>
                  <div class="text-white font-semibold text-[14px] leading-none">{{ deliveryCountryName }}</div>
                </div>
                <svg
                  class="w-3 h-3 text-orange-200 shrink-0 transition-transform duration-200"
                  :class="{ 'rotate-180': showDeliveryDropdown }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>

              <!-- Dropdown -->
              <div
                v-if="showDeliveryDropdown"
                class="absolute right-0 top-full mt-2 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50 w-60 max-h-72 overflow-y-auto"
              >
                <div
                  v-for="country in deliveryCountries"
                  :key="country.code"
                  @click="selectDeliveryCountry(country)"
                  class="flex items-center gap-2.5 px-4 py-2.5 hover:bg-orange-bg cursor-pointer transition text-[13px] text-gray-700"
                  :class="{ 'bg-orange-bg font-semibold': selectedDeliveryCountry?.code === country.code }"
                >
                  <span class="text-[18px]">{{ country.flag_emoji || '' }}</span>
                  <span>{{ country.name_en }}</span>
                </div>
                <div v-if="deliveryCountries.length === 0" class="px-4 py-3 text-gray-400 text-sm">
                  Loading countries...
                </div>
              </div>
            </div>

            <router-link to="/cart" class="flex items-center gap-1.5 bg-primary-light rounded-full h-10 px-5">
              <span class="text-white text-base">🛒</span>
              <span class="text-white text-[14px] font-semibold">Cart</span>
              <span v-if="cartCount > 0" class="bg-red-500 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center -ml-1">{{ cartCount }}</span>
            </router-link>

            <template v-if="isAuthenticated">
              <router-link to="/my-orders" class="text-white text-[14px] hover:text-orange-200 transition">
                Orders
              </router-link>
              <div class="relative">
                <button @click="showUserMenu = !showUserMenu" class="flex items-center gap-2">
                  <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center text-primary text-[14px] font-bold">
                    {{ user?.display_name?.[0]?.toUpperCase() || '?' }}
                  </div>
                  <span class="text-orange-200 text-[12px]">{{ user?.display_name || 'User' }}</span>
                </button>
                <div v-if="showUserMenu" class="absolute right-0 top-12 bg-white rounded-xl shadow-lg py-2 w-48 z-50">
                  <router-link to="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" @click="showUserMenu = false">
                    👤 My Profile
                  </router-link>
                  <router-link to="/my-orders" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" @click="showUserMenu = false">
                    📦 My Orders
                  </router-link>
                  <div class="border-t my-1"></div>
                  <button @click="handleLogout" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                    Sign Out
                  </button>
                </div>
              </div>
            </template>
            <template v-else>
              <router-link to="/login" class="text-white text-[14px] font-semibold h-10 flex items-center px-4 hover:text-orange-200 transition">
                Sign In
              </router-link>
              <router-link to="/register" class="bg-primary-light text-white text-[14px] font-semibold px-5 h-10 flex items-center rounded-full hover:bg-primary transition">
                Sign Up
              </router-link>
            </template>
          </div>

          <!-- Mobile search & avatar -->
          <div class="flex items-center gap-3 md:hidden col-span-3 justify-end">
            <button class="text-white text-lg" @click="showMobileSearch = !showMobileSearch"></button>
            <router-link to="/cart" class="relative text-white text-lg">

              <span v-if="cartCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center">{{ cartCount }}</span>
            </router-link>
            <router-link v-if="!isAuthenticated" to="/login" class="w-8 h-8 bg-white rounded-full flex items-center justify-center text-primary text-sm font-bold">G</router-link>
            <div v-else class="w-8 h-8 bg-white rounded-full flex items-center justify-center text-primary text-sm font-bold">
              {{ user?.display_name?.[0]?.toUpperCase() || '?' }}
            </div>
          </div>
        </div>

        <!-- Mobile Search -->
        <div v-if="showMobileSearch" class="md:hidden pb-3">
          <div class="bg-white rounded-full h-9 flex items-center pr-1">
            <span class="pl-4 text-gray-400 mr-2"></span>
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="Search products..."
              class="bg-transparent outline-none text-sm text-gray-600 flex-1"
            />
          </div>
        </div>
      </div>
    </nav>

    <!-- Mobile Bottom Tab Bar -->
    <div class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 flex justify-around py-2 safe-bottom">
      <router-link to="/" class="flex flex-col items-center text-[10px] font-semibold text-primary">
        <span class="text-[20px]">🏠</span>
        Home
      </router-link>
      <router-link to="/browse" class="flex flex-col items-center text-[10px] text-gray-400">
        <span class="text-[20px]">🔍</span>
        Browse
      </router-link>
      <router-link to="/cart" class="flex flex-col items-center text-[10px] text-gray-400">
        <span class="text-[20px]">🛒</span>
        Cart
      </router-link>
      <router-link v-if="isAuthenticated" to="/my-orders" class="flex flex-col items-center text-[10px] text-gray-400">
        <span class="text-[20px]">📦</span>
        Orders
      </router-link>
      <router-link v-if="isAuthenticated" to="/profile" class="flex flex-col items-center text-[10px] text-gray-400">
        <span class="text-[20px]"></span>
        Profile
      </router-link>
      <router-link v-else to="/login" class="flex flex-col items-center text-[10px] text-gray-400">
        <span class="text-[20px]">🔑</span>
        Sign In
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useCart } from '../composables/useCart'
import { useCountries } from '../composables/useCountries'
import { useLocation } from '../composables/useLocation'

const router = useRouter()
const searchQuery = ref('')
const showMobileSearch = ref(false)
const showUserMenu = ref(false)

// Delivery address — shared state via useLocation
const { loadCountries, getCountryByCode } = useCountries()
const { countryCode, setLocation, initLocation } = useLocation()
const deliveryCountries = ref([])
const showDeliveryDropdown = ref(false)

const selectedDeliveryCountry = computed(() => {
  return countryCode.value ? getCountryByCode(countryCode.value) : null
})

const deliveryCountryName = computed(() => {
  return selectedDeliveryCountry.value?.name_en || 'Country'
})

const selectDeliveryCountry = (country) => {
  setLocation(country.code)
  showDeliveryDropdown.value = false
}

const handleDeliveryClickOutside = (e) => {
  if (!e.target.closest('[data-delivery-pill]')) {
    showDeliveryDropdown.value = false
  }
}

onMounted(async () => {
  const loaded = await loadCountries()
  deliveryCountries.value = loaded || []

  // Initialize location (uses cached value or detects via GeoIP)
  await initLocation()

  document.addEventListener('click', handleDeliveryClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDeliveryClickOutside)
})

const { user, isAuthenticated, logout } = useAuth()
const { count: cartCount } = useCart()

const hotTags = ['iPhone 15', 'Nike Air', 'IKEA', 'PS5', 'MacBook']

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/browse', query: { q: searchQuery.value } })
  }
}

const searchTag = (tag) => {
  router.push({ path: '/browse', query: { q: tag } })
}

const handleLogout = () => {
  showUserMenu.value = false
  logout()
}
</script>

<style scoped>
.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom, 8px);
}
</style>
