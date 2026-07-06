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
    }
    return Promise.reject(err)
  }
)

// ---- Public ----
export const getProducts = (params) => api.get('/products', { params })
export const getProduct = (slug) => api.get(`/products/${slug}`)
export const getCategories = () => api.get('/categories')
export const searchProducts = (params) => api.get('/products/search', { params })
export const getShippingOptions = (productSlug, country) => api.get(`/products/${productSlug}/shipping-options`, { params: { country } })
export const getShippingTable = (productSlug) => api.get(`/shipping/products/${productSlug}/shipping-table`)
export const getShippingNotes = (productSlug) => api.get(`/products/${productSlug}/shipping-notes`)
export const calculateShipping = (data) => api.post('/shipping/calculate', data)
export const getCountries = () => api.get('/shipping/countries')
export const recordConsent = (data) => api.post('/gdpr/consent', data)
export const submitDataRequest = (data) => api.post('/gdpr/data-request', data)

// ---- Auth ----
export const loginApi = (username, password) => api.post('/auth/login', { username, password })
export const registerApi = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')
export const updateProfileApi = (data) => api.put('/auth/profile', data)

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

// ---- Flash Deals ----
export const getActiveFlashDeals = () => api.get('/flash-deals/active')

// ---- Banners ----
export const getActiveBanners = () => api.get('/banners/active')

// ---- Shipping Info (PDP section) ----
export const getReturnPolicy = (productId) => api.get(`/shipping-info/return-policy/${productId}`)
export const getPaymentMethods = () => api.get('/shipping-info/payment-methods')
export const getShippingSettings = () => api.get('/shipping-info/shipping-settings')

export default api
