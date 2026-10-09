import { createApp, nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import Home from './views/Home.vue'
import Browse from './views/Browse.vue'
import ProductDetail from './views/ProductDetail.vue'
import Cart from './views/Cart.vue'
import Checkout from './views/Checkout.vue'
import Profile from './views/Profile.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import MyOrders from './views/MyOrders.vue'
import OrderDetail from './views/OrderDetail.vue'
import OrderSuccess from './views/OrderSuccess.vue'
import SavedProducts from './views/SavedProducts.vue'
import Legal from './views/Legal.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import VerifyEmail from './views/VerifyEmail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/browse', component: Browse },
    { path: '/products/:slug', component: ProductDetail },
    { path: '/p/:token', component: ProductDetail, name: 'shared-product' },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout, meta: { requiresAuth: true } },
    { path: '/profile', component: Profile, meta: { requiresAuth: true } },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/my-orders', component: MyOrders, meta: { requiresAuth: true } },
    { path: '/my-orders/:id', component: OrderDetail, meta: { requiresAuth: true } },
    { path: '/order-success', component: OrderSuccess, meta: { requiresAuth: true } },
    { path: '/saved', component: SavedProducts, meta: { requiresAuth: true } },
    { path: '/legal/:section?', component: Legal },
    { path: '/forgot-password', component: ForgotPassword },
    { path: '/verify-email', component: VerifyEmail },
  ],
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

router.afterEach((to) => {
  const section = ({ '/': 'Home', '/browse': 'Browse', '/cart': 'Cart', '/checkout': 'Checkout', '/profile': 'Account', '/login': 'Sign in', '/register': 'Create account', '/my-orders': 'Orders', '/saved': 'Saved products' })[to.path]
    || (to.path.startsWith('/products/') ? 'Product details' : to.path.startsWith('/my-orders/') ? 'Order details' : 'BeCool Market')
  document.title = `${section} · BeCool Market`
  nextTick(() => {
    const heading = document.querySelector('h1')
    if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true }) }
  })
})

// Page transition direction tracking
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if ((to.path === '/login' || to.path === '/register') && token) {
    return '/profile'
  }

  const backRoutes = ['/', '/browse', '/cart', '/profile']
  if (backRoutes.includes(to.path) && from && !backRoutes.includes(from.path)) {
    to.meta.transition = 'slide-right'
  } else {
    to.meta.transition = 'slide-left'
  }
})

createApp(App).use(router).mount('#app')
