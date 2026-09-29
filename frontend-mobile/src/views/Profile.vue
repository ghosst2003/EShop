<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <!-- Header -->
    <div class="bg-primary safe-top">
      <div class="flex items-center px-4 py-6">
        <div class="w-16 h-16 bg-white rounded-full flex items-center justify-center text-primary text-2xl font-bold">
          {{ user?.display_name?.[0]?.toUpperCase() || '?' }}
        </div>
        <div class="ml-4">
          <h2 class="text-white text-lg font-bold">{{ user?.display_name || 'User' }}</h2>
          <p class="text-orange-200 text-sm">{{ user?.email || '' }}</p>
        </div>
      </div>
    </div>

    <!-- Menu -->
    <div class="px-4 py-4 space-y-3">
      <router-link to="/my-orders" class="flex items-center gap-3 bg-white rounded-xl px-4 py-4 tap-active">
        <span class="text-xl">📦</span>
        <span class="flex-1 text-sm font-medium">My Orders</span>
        <span class="text-gray-400">→</span>
      </router-link>

      <div class="flex items-center gap-3 bg-white rounded-xl px-4 py-4 tap-active" @click="showSettings = !showSettings">
        <span class="text-xl">⚙️</span>
        <span class="flex-1 text-sm font-medium">Settings</span>
        <span class="text-gray-400">{{ showSettings ? '↑' : '→' }}</span>
      </div>

      <div v-if="showSettings" class="bg-white rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <span class="text-sm">Delivery Country</span>
          <span class="text-sm text-gray-500">{{ deliveryCountryName }}</span>
        </div>
      </div>

      <div class="flex items-center gap-3 bg-white rounded-xl px-4 py-4 tap-active" @click="handleLogout">
        <span class="text-xl"></span>
        <span class="flex-1 text-sm font-medium text-red-500">Sign Out</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useLocation } from '../composables/useLocation'
import { useCountries } from '../composables/useCountries'

const { user, logout } = useAuth()
const { countryCode } = useLocation()
const { getCountryByCode } = useCountries()

const showSettings = ref(false)
const deliveryCountryName = computed(() => {
  const country = countryCode.value ? getCountryByCode(countryCode.value) : null
  return country?.name_en || 'Not set'
})

const handleLogout = () => {
  logout()
}
</script>
