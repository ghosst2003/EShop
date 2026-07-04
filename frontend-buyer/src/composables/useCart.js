import { ref, computed, watch } from 'vue'
import api from '../api'
import { useAuth } from './useAuth'

const LOCAL_KEY = 'guest-cart'
const guestCart = ref(JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]'))
const serverCart = ref(null)

export function useCart() {
  const { isAuthenticated } = useAuth()

  const items = computed(() =>
    isAuthenticated.value && serverCart.value ? serverCart.value.items : guestCart.value
  )

  const count = computed(() =>
    items.value.reduce((sum, i) => sum + (i.quantity || 0), 0)
  )

  const total = computed(() =>
    items.value.reduce((sum, i) => {
      const p = i.product?.sale_price || 0
      return sum + (p * i.quantity)
    }, 0)
  )

  const addToGuest = (product, qty = 1) => {
    const ex = guestCart.value.find(i => i.product_id === product.id)
    if (ex) {
      ex.quantity += qty
    } else {
      guestCart.value.push({ product_id: product.id, product, quantity: qty })
    }
    saveGuest()
  }

  const saveGuest = () => localStorage.setItem(LOCAL_KEY, JSON.stringify(guestCart.value))

  const syncGuest = async () => {
    for (const item of guestCart.value) {
      try {
        await api.post('/cart/items', { product_id: item.product_id, quantity: item.quantity })
      } catch (e) {
        console.error('Sync cart item failed:', e)
      }
    }
    guestCart.value = []
    localStorage.removeItem(LOCAL_KEY)
    await fetchServer()
  }

  const fetchServer = async () => {
    if (!isAuthenticated.value) { serverCart.value = null; return }
    try {
      const res = await api.get('/cart')
      serverCart.value = res.data
    } catch (e) {
      console.error('Fetch cart failed:', e)
    }
  }

  const addToCart = async (product, qty = 1) => {
    if (isAuthenticated.value) {
      try {
        await api.post('/cart/items', { product_id: product.id, quantity: qty })
        await fetchServer()
      } catch (e) {
        alert(e.response?.data?.detail || 'Failed to add to cart')
      }
    } else {
      addToGuest(product, qty)
    }
  }

  const updateQty = async (itemId, qty) => {
    if (isAuthenticated.value) {
      const item = serverCart.value?.items.find(i => i.id === itemId)
      if (!item) return
      if (qty <= 0) {
        await api.delete(`/cart/items/${itemId}`)
      } else {
        await api.put(`/cart/items/${itemId}`, { quantity: qty })
      }
      await fetchServer()
    } else {
      const idx = guestCart.value.findIndex(i => i.product_id === itemId)
      if (idx === -1) return
      if (qty <= 0) {
        guestCart.value.splice(idx, 1)
      } else {
        guestCart.value[idx].quantity = qty
      }
      saveGuest()
    }
  }

  const removeFromCart = async (itemId) => {
    if (isAuthenticated.value) {
      await api.delete(`/cart/items/${itemId}`)
      await fetchServer()
    } else {
      guestCart.value = guestCart.value.filter(i => i.product_id !== itemId)
      saveGuest()
    }
  }

  const clearCart = async () => {
    if (isAuthenticated.value) {
      await api.delete('/cart/clear')
      serverCart.value = null
    } else {
      guestCart.value = []
      localStorage.removeItem(LOCAL_KEY)
    }
  }

  watch(isAuthenticated, (v) => {
    if (v) syncGuest()
    fetchServer()
  }, { immediate: true })

  return { items, count, total, addToCart, updateQty, removeFromCart, clearCart }
}
