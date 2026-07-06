import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/products' },
      { path: 'products', name: 'Products', component: () => import('../views/ProductList.vue') },
      { path: 'products/new', name: 'ProductNew', component: () => import('../views/ProductForm.vue') },
      { path: 'products/:id/edit', name: 'ProductEdit', component: () => import('../views/ProductForm.vue') },
      { path: 'categories', name: 'Categories', component: () => import('../views/CategoryManagement.vue') },
      { path: 'countries', name: 'Countries', component: () => import('../views/CountryManagement.vue') },
      { path: 'orders', name: 'Orders', component: () => import('../views/OrderList.vue') },
      { path: 'gdpr', name: 'GdprRequests', component: () => import('../views/GdprRequests.vue') },
      { path: 'flash-deals', name: 'FlashDeals', component: () => import('../views/FlashDealsList.vue') },
      { path: 'flash-deals/new', name: 'FlashDealNew', component: () => import('../views/FlashDealForm.vue') },
      { path: 'flash-deals/:id/edit', name: 'FlashDealEdit', component: () => import('../views/FlashDealForm.vue') },
      { path: 'banners', name: 'Banners', component: () => import('../views/BannersList.vue') },
      { path: 'shipping-methods', name: 'ShippingMethods', component: () => import('../views/ShippingMethods.vue') },
      { path: 'shipping-origins', name: 'ShippingOrigins', component: () => import('../views/ShippingOrigins.vue') },
      { path: 'return-policy', name: 'ReturnPolicy', component: () => import('../views/ReturnPolicy.vue') },
      { path: 'payment-methods', name: 'PaymentMethods', component: () => import('../views/PaymentMethods.vue') },
      { path: 'shipping-settings', name: 'ShippingSettings', component: () => import('../views/ShippingSettings.vue') },
    ],
  },
]

// 检测当前部署路径：dev server 用 '/'，production 用 '/admin'
function detectBase() {
  // 检查是否有 /admin/ 路径下的资源
  const scripts = document.querySelectorAll('script[src]')
  for (const s of scripts) {
    if (s.src.includes('/admin/')) return '/admin'
  }
  return '/'
}

const router = createRouter({
  history: createWebHistory(detectBase()),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.matched.some((r) => r.meta.requiresAuth) && !token) {
    return { name: 'Login' }
  }
})

export default router
