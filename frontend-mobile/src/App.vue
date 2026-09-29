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
      <span class="text-[22px] leading-none">{{ tab.icon }}</span>
      <span class="mt-0.5 text-[10px] font-medium truncate w-full text-center">{{ tab.label }}</span>
      <span v-if="tab.badge" class="absolute top-1 right-1/4 bg-red-500 text-white text-[8px] font-bold w-4 h-4 rounded-full flex items-center justify-center -mt-1">
        {{ tab.badge > 9 ? '9+' : tab.badge }}
      </span>
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

const showBottomTabBar = computed(() => !route.path.startsWith('/products/') && !route.path.startsWith('/checkout') && !route.path.startsWith('/my-orders') && !route.path.startsWith('/order-success') && !route.path.startsWith('/register'))

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
