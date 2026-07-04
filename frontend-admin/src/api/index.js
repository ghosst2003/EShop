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

// 响应拦截器：401 跳转登录
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/admin/login'
    }
    return Promise.reject(err)
  }
)

// ---- Auth ----
export const login = (username, password) => api.post('/auth/login', { username, password })
export const getMe = () => api.get('/auth/me')

// ---- Products ----
export const getProducts = (params) => api.get('/admin/products', { params })
export const getProduct = (id) => api.get(`/admin/products/${id}`)
export const createProduct = (data) => api.post('/admin/products', data)
export const updateProduct = (id, data) => api.put(`/admin/products/${id}`, data)
export const deleteProduct = (id) => api.delete(`/admin/products/${id}`)
export const updateProductStatus = (id, status) => api.patch(`/admin/products/${id}/status`, { status })
export const uploadProductImage = (productId, file, altText) => {
  const form = new FormData()
  form.append('file', file)
  if (altText) form.append('alt_text', altText)
  return api.post(`/admin/products/${productId}/images`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const deleteProductImage = (productId, imageId) =>
  api.delete(`/admin/products/${productId}/images/${imageId}`)

// ---- Categories ----
export const getCategories = () => api.get('/admin/categories')
export const createCategory = (data) => api.post('/admin/categories', data)
export const updateCategory = (id, data) => api.put(`/admin/categories/${id}`, data)
export const deleteCategory = (id) => api.delete(`/admin/categories/${id}`)

// ---- Countries ----
export const getCountries = () => api.get('/admin/countries')
export const createCountry = (data) => api.post('/admin/countries', data)
export const updateCountry = (id, data) => api.put(`/admin/countries/${id}`, data)
export const deleteCountry = (id) => api.delete(`/admin/countries/${id}`)

// ---- Shipping Methods ----
export const getShippingMethods = () => api.get('/admin/shipping-methods')
export const createShippingMethod = (data) => api.post('/admin/shipping-methods', data)
export const updateShippingMethod = (id, data) => api.put(`/admin/shipping-methods/${id}`, data)
export const deleteShippingMethod = (id) => api.delete(`/admin/shipping-methods/${id}`)

// ---- Product Shipping Overrides ----
export const getProductShippingOverrides = (productId) =>
  api.get(`/admin/products/${productId}/shipping-overrides`)
export const updateProductShippingOverrides = (productId, data) =>
  api.put(`/admin/products/${productId}/shipping-overrides`, data)

// ---- Global Shipping Origin Rules ----
export const getGlobalShippingRules = () => api.get('/admin/shipping-origins')

// ---- Product Shipping Notes ----
export const getProductShippingNotes = (productId) =>
  api.get(`/admin/products/${productId}/shipping-notes`)
export const updateProductShippingNotes = (productId, data) =>
  api.put(`/admin/products/${productId}/shipping-notes`, data)

// ---- Shipping Origins ----
export const getShippingOrigins = () => api.get('/admin/shipping-origins')
export const createShippingOriginRule = (data) => api.post('/admin/shipping-origins', data)
export const updateShippingOriginRule = (id, data) => api.put(`/admin/shipping-origins/${id}`, data)
export const deleteShippingOriginRule = (id) => api.delete(`/admin/shipping-origins/${id}`)

// ---- Flash Deals ----
export const getFlashDeals = (params) => api.get('/admin/flash-deals', { params })
export const createFlashDeal = (data) => api.post('/admin/flash-deals', data)
export const getFlashDeal = (id) => api.get(`/admin/flash-deals/${id}`)
export const updateFlashDeal = (id, data) => api.put(`/admin/flash-deals/${id}`, data)
export const deleteFlashDeal = (id) => api.delete(`/admin/flash-deals/${id}`)

// ---- Banners ----
export const getBanners = () => api.get('/admin/banners')
export const createBanner = (data) => api.post('/admin/banners', data)
export const updateBanner = (id, data) => api.put(`/admin/banners/${id}`, data)
export const deleteBanner = (id) => api.delete(`/admin/banners/${id}`)

// ---- GDPR ----
export const getGdprRequests = (statusFilter) =>
  api.get('/admin/gdpr/requests', { params: { status_filter: statusFilter } })
export const updateGdprRequest = (id, data) => api.patch(`/admin/gdpr/requests/${id}`, data)

// ---- Orders ----
export const getOrders = (params) => api.get('/admin/orders', { params })
export const getOrderStats = () => api.get('/admin/orders/stats')
export const getOrder = (id) => api.get(`/admin/orders/${id}`)
export const createOrder = (data) => api.post('/admin/orders', data)
export const updateOrder = (id, data) => api.put(`/admin/orders/${id}`, data)
export const updateOrderStatus = (id, data) => api.post(`/admin/orders/${id}/status`, data)
export const deleteOrder = (id) => api.delete(`/admin/orders/${id}`)

export default api
