import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器：附加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：401 清除 token
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.dispatchEvent(new CustomEvent('auth:expired'))
    }
    return Promise.reject(err)
  }
)

// ---- Public ----
export const getProducts = (params) => api.get('/products', { params })
export const getProduct = (slug) => api.get(`/products/${slug}`)
export const getProductById = (id) => api.get(`/products/id/${id}`)
export const createProductShareLink = (slug) => api.post(`/products/${slug}/share-link`)
export const getSharedProduct = (token) => api.get(`/products/shared/${encodeURIComponent(token)}`)
export const getCategories = () => api.get('/categories')
export const searchProducts = (params) => api.get('/products/search', { params })
export const getShippingOptions = (productSlug, country) => api.get(`/products/${productSlug}/shipping-options`, { params: { country } })
export const getShippingTable = (productSlug) => api.get(`/shipping/products/${productSlug}/shipping-table`)
export const getShippingNotes = (productSlug) => api.get(`/products/${productSlug}/shipping-notes`)
export const calculateShipping = (data) => api.post('/shipping/calculate', data)
export const getCartShippingEstimate = (country, productIds = []) => api.get('/shipping/cart/shipping-estimate', {
  params: {
    country,
    product_ids: productIds.length ? productIds.join(',') : undefined,
  },
})
export const getCountries = () => api.get('/shipping/countries')
export const recordConsent = (data) => api.post('/gdpr/consent', data)
export const submitDataRequest = (data) => api.post('/gdpr/data-request', data)

// ---- Auth ----
export const loginApi = (username, password) => api.post('/auth/login', { username, password })
export const registerApi = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')
export const updateProfileApi = (data) => api.put('/auth/profile', data)
export const requestPasswordReset = (account) => api.post('/auth/password-reset/request', { account })
export const confirmPasswordReset = (token, newPassword) => api.post('/auth/password-reset/confirm', { token, new_password: newPassword })
export const confirmEmailVerification = (token) => api.post('/auth/email-verification/confirm', { token })

// ---- Cart ----
export const getCart = () => api.get('/cart')
export const addToCart = (productId, quantity = 1) => api.post('/cart/items', { product_id: productId, quantity })
export const updateCartItem = (itemId, quantity) => api.put(`/cart/items/${itemId}`, { quantity })
export const removeCartItem = (itemId) => api.delete(`/cart/items/${itemId}`)
export const clearCart = () => api.delete('/cart/clear')

// ---- Addresses ----
export const getAddresses = () => api.get('/addresses')
export const createAddress = (data) => api.post('/addresses', data)
export const updateAddress = (id, data) => api.put(`/addresses/${id}`, data)
export const deleteAddress = (id) => api.delete(`/addresses/${id}`)

// ---- Orders (Buyer) ----
export const createOrder = (data) => api.post('/orders', data)
export const getMyOrders = (params) => api.get('/orders', { params })
export const getMyOrder = (id) => api.get(`/orders/${id}`)

// ---- Payment ----
export const createCheckoutSession = (orderId) => api.post('/payments/create-checkout-session', { order_id: orderId })
export const cancelOrder = (orderId) => api.post(`/orders/${orderId}/cancel`)
export const reorderOrder = (orderId) => api.post(`/orders/${orderId}/reorder`)
export const createReturnRequest = (orderId, data) => api.post(`/orders/${orderId}/return-requests`, data)
export const getReturnRequest = (orderId) => api.get(`/orders/${orderId}/return-request`)

// ---- Saved products & reviews ----
export const getSavedProducts = () => api.get('/saved-products')
export const saveProduct = (productId) => api.post(`/saved-products/${productId}`)
export const unsaveProduct = (productId) => api.delete(`/saved-products/${productId}`)
export const getProductReviews = (productId) => api.get(`/products/${productId}/reviews`)
export const submitProductReview = (productId, data) => api.post(`/products/${productId}/reviews`, data)
export const validatePromotion = (code) => api.get(`/promotions/${encodeURIComponent(code)}`)

// ---- Flash Deals ----
export const getActiveFlashDeals = () => api.get('/flash-deals/active')

// ---- Banners ----
export const getActiveBanners = () => api.get('/banners/active')

// ---- Promo Items (Mobile Home Grid) ----
export const getPromoItems = () => api.get('/promo-items')

// ---- Shipping Info (PDP section) ----
export const getReturnPolicy = (productId) => api.get(`/shipping-info/return-policy/${productId}`)
export const getPaymentMethods = () => api.get('/shipping-info/payment-methods')
export const getShippingSettings = () => api.get('/shipping-info/shipping-settings')

export default api
