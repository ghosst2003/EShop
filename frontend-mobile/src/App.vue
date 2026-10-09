<template>
  <div class="min-h-screen bg-[#F7F7F7] pb-16">
    <router-view v-slot="{ Component }">
      <transition :name="transitionName" mode="out-in">
        <component :is="Component" :key="$route.fullPath" />
      </transition>
    </router-view>
  </div>

  <!-- Bottom Tab Bar -->
  <div v-if="showBottomTabBar" class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 z-50 flex safe-bottom">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="flex-1 flex flex-col items-center justify-center py-2"
      :class="isActive(tab.path) ? 'text-primary' : 'text-gray-400'"
    >
      <span class="relative inline-flex items-center justify-center text-[22px] leading-none">
        {{ tab.icon }}
        <span
          v-if="tab.badge"
          class="absolute -top-2 -right-3 min-w-[17px] h-[17px] px-1 rounded-full flex items-center justify-center bg-[#17483b] text-[#d9f06a] text-[9px] leading-none font-extrabold ring-2 ring-white"
          aria-label="Cart item count"
        >
          {{ tab.badge > 99 ? '99+' : tab.badge }}
        </span>
      </span>
      <span class="mt-0.5 text-[10px] font-medium truncate w-full text-center">{{ tab.label }}</span>
    </router-link>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth.js'
import { useCart } from './composables/useCart.js'

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()
const { count: cartCount } = useCart()

const transitionName = ref('page')

watch(() => route.path, (newPath, oldPath) => {
  const backRoutes = ['/', '/browse', '/cart', '/profile']
  if (backRoutes.includes(newPath) && oldPath && !backRoutes.includes(oldPath)) {
    transitionName.value = 'page-leave-right'
  } else {
    transitionName.value = 'page'
  }
})

const tabs = computed(() => [
  { path: '/', icon: '🏠', label: 'Home' },
  { path: '/browse', icon: '🔍', label: 'Browse' },
  { path: '/cart', icon: '🛒', label: 'Cart', badge: cartCount.value },
  { path: isAuthenticated.value ? '/profile' : '/login', icon: '👤', label: isAuthenticated.value ? 'Profile' : 'Login' },
])

const showBottomTabBar = computed(() => !['/products/', '/p/', '/cart', '/checkout', '/my-orders', '/order-success', '/register', '/login', '/forgot-password', '/verify-email', '/saved', '/legal'].some(prefix => route.path.startsWith(prefix)))

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  if (path === '/browse') return route.path === '/browse' || route.path.startsWith('/browse')
  if (path === '/cart') return route.path === '/cart'
  if (path === '/profile' || path === '/login') return route.path === '/profile' || route.path === '/login' || route.path === '/register' || route.path.startsWith('/my-orders')
  return false
}
</script>

<style>
.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom, 8px);
  background-color: white;
}
</style>
