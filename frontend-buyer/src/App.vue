<template>
  <div class="min-h-screen bg-[#F2F3F7] md:pb-0 pb-16">
    <router-view />
    <CookieConsent />
  </div>

  <!-- Mobile Bottom Tab Bar — at root level for guaranteed fixed positioning -->
  <div v-if="showBottomTabBar" class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 flex safe-bottom">
    <router-link to="/" class="flex-1 flex flex-col items-center justify-center py-3 text-[11px] text-primary">
      <span class="text-[22px] leading-none">🏠</span>
      <span class="mt-1 truncate w-full text-center">Home</span>
    </router-link>
    <router-link to="/browse" class="flex-1 flex flex-col items-center justify-center py-3 text-[11px] text-gray-400">
      <span class="text-[22px] leading-none">🔍</span>
      <span class="mt-1 truncate w-full text-center">Browse</span>
    </router-link>
    <router-link to="/cart" class="flex-1 flex flex-col items-center justify-center py-3 text-[11px] text-gray-400">
      <span class="text-[22px] leading-none">🛒</span>
      <span class="mt-1 truncate w-full text-center">Cart</span>
    </router-link>
    <router-link v-if="isAuthenticated" to="/profile" class="flex-1 flex flex-col items-center justify-center py-3 text-[11px] text-gray-400">
      <span class="text-[22px] leading-none">👤</span>
      <span class="mt-1 truncate w-full text-center">Profile</span>
    </router-link>
    <router-link v-else to="/login" class="flex-1 flex flex-col items-center justify-center py-3 text-[11px] text-gray-400">
      <span class="text-[22px] leading-none">🔑</span>
      <span class="mt-1 truncate w-full text-center">Sign In</span>
    </router-link>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from './composables/useAuth'
import CookieConsent from './components/CookieConsent.vue'

const route = useRoute()
const { isAuthenticated } = useAuth()

const showBottomTabBar = computed(() => !route.path.startsWith('/products/'))
</script>

<style>
.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom, 8px);
  background-color: white;
}
</style>
