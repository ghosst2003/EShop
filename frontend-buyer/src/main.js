import { createApp, nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import Home from './views/Home.vue'
import ProductList from './views/ProductList.vue'
import ProductDetail from './views/ProductDetail.vue'
import PrivacyPolicy from './views/PrivacyPolicy.vue'
import Imprint from './views/Imprint.vue'
import DataRequestForm from './views/DataRequestForm.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Profile from './views/Profile.vue'
import Cart from './views/Cart.vue'
import Checkout from './views/Checkout.vue'
import MyOrders from './views/MyOrders.vue'
import OrderDetail from './views/OrderDetail.vue'
import OrderSuccess from './views/OrderSuccess.vue'
import TermsOfService from './views/TermsOfService.vue'
import SavedProducts from './views/SavedProducts.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import VerifyEmail from './views/VerifyEmail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/browse', component: ProductList },
    { path: '/products/:slug', component: ProductDetail },
    { path: '/p/:token', component: ProductDetail, name: 'shared-product' },
    { path: '/privacy', component: PrivacyPolicy },
    { path: '/imprint', component: Imprint },
    { path: '/data-request', component: DataRequestForm },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/profile', component: Profile, meta: { requiresAuth: true } },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout, meta: { requiresAuth: true } },
    { path: '/my-orders', component: MyOrders, meta: { requiresAuth: true } },
    { path: '/my-orders/:id', component: OrderDetail, meta: { requiresAuth: true } },
    { path: '/order-success', component: OrderSuccess, meta: { requiresAuth: true } },
    { path: '/saved', component: SavedProducts, meta: { requiresAuth: true } },
    { path: '/forgot-password', component: ForgotPassword },
    { path: '/verify-email', component: VerifyEmail },
    { path: '/terms', component: TermsOfService },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) return { path: '/login', query: { redirect: to.fullPath } }
  if (token && ['/login', '/register'].includes(to.path)) return '/profile'
})

router.afterEach((to) => {
  const title = ({ '/': 'Home', '/browse': 'Browse', '/cart': 'Cart', '/checkout': 'Checkout', '/profile': 'Account', '/login': 'Sign in', '/register': 'Create account', '/my-orders': 'Orders', '/saved': 'Saved products' })[to.path]
    || (to.path.startsWith('/products/') || to.path.startsWith('/p/') ? 'Product details' : to.path.startsWith('/my-orders/') ? 'Order details' : 'BeCool Market')
  document.title = `${title} · BeCool Market`
  nextTick(() => document.querySelector('h1')?.focus({ preventScroll: true }))
})

createApp(App).use(router).mount('#app')
