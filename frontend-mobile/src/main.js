import { createApp } from 'vue'
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

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/browse', component: Browse },
    { path: '/products/:slug', component: ProductDetail },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout },
    { path: '/profile', component: Profile },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/my-orders', component: MyOrders },
    { path: '/my-orders/:id', component: OrderDetail },
    { path: '/order-success', component: OrderSuccess },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// Page transition direction tracking
router.beforeEach((to, from) => {
  const backRoutes = ['/', '/browse', '/cart', '/profile']
  if (backRoutes.includes(to.path) && from && !backRoutes.includes(from.path)) {
    to.meta.transition = 'slide-right'
  } else {
    to.meta.transition = 'slide-left'
  }
})

createApp(App).use(router).mount('#app')
