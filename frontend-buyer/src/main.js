import { createApp } from 'vue'
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

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/browse', component: ProductList },
    { path: '/products/:slug', component: ProductDetail },
    { path: '/privacy', component: PrivacyPolicy },
    { path: '/imprint', component: Imprint },
    { path: '/data-request', component: DataRequestForm },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/profile', component: Profile },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout },
    { path: '/my-orders', component: MyOrders },
    { path: '/my-orders/:id', component: OrderDetail },
    { path: '/order-success', component: OrderSuccess },
    { path: '/terms', component: TermsOfService },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

createApp(App).use(router).mount('#app')
