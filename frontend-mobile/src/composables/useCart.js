import { ref, computed, watch } from 'vue'
import api from '../api'
import { useAuth } from './useAuth'

const LOCAL_KEY = 'guest-cart'

const readGuestCart = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]')
    return Array.isArray(stored) ? stored : []
  } catch {
    localStorage.removeItem(LOCAL_KEY)
    return []
  }
}

const guestCart = ref(readGuestCart())
const serverCart = ref(null)
const loading = ref(false)
const error = ref('')
const pendingProductIds = ref(new Set())
const selectedIds = ref([])
let authWatcherStarted = false
let selectionInitialized = false

const getErrorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  return err?.message || fallback
}

const saveGuest = () => {
  localStorage.setItem(LOCAL_KEY, JSON.stringify(guestCart.value))
}

const setPending = (productId, value) => {
  const next = new Set(pendingProductIds.value)
  if (value) next.add(productId)
  else next.delete(productId)
  pendingProductIds.value = next
}

export function useCart() {
  const { isAuthenticated } = useAuth()

  const items = computed(() => (
    isAuthenticated.value ? (serverCart.value?.items || []) : guestCart.value
  ))

  const count = computed(() => (
    items.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
  ))

  const total = computed(() => (
    items.value.reduce((sum, item) => {
      const price = Number(item.product?.sale_price || 0)
      return sum + price * Number(item.quantity || 0)
    }, 0)
  ))

  const selectedItems = computed(() => (
    items.value.filter(item => selectedIds.value.includes(item.product_id))
  ))

  const selectedCount = computed(() => selectedItems.value.length)
  const selectedUnits = computed(() => (
    selectedItems.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
  ))
  const selectedTotal = computed(() => (
    selectedItems.value.reduce((sum, item) => {
      const price = Number(item.product?.sale_price || 0)
      return sum + price * Number(item.quantity || 0)
    }, 0)
  ))

  const fetchServer = async ({ silent = false } = {}) => {
    if (!isAuthenticated.value) {
      serverCart.value = null
      return
    }
    if (!silent) loading.value = true
    try {
      const response = await api.get('/cart')
      serverCart.value = response.data
      error.value = ''
    } catch (err) {
      error.value = getErrorMessage(err, 'Could not load your cart.')
      throw err
    } finally {
      if (!silent) loading.value = false
    }
  }

  const syncGuest = async () => {
    if (!guestCart.value.length) {
      await fetchServer()
      return
    }

    loading.value = true
    const failed = []
    for (const item of guestCart.value) {
      try {
        await api.post('/cart/items', {
          product_id: item.product_id,
          quantity: item.quantity,
        })
      } catch {
        failed.push(item)
      }
    }

    guestCart.value = failed
    const syncError = failed.length
      ? `${failed.length} item${failed.length > 1 ? 's' : ''} could not be synced.`
      : ''
    if (failed.length) {
      saveGuest()
    } else {
      localStorage.removeItem(LOCAL_KEY)
    }

    try {
      await fetchServer({ silent: true })
      error.value = syncError
    } finally {
      loading.value = false
    }
  }

  const addToCart = async (product, quantity = 1) => {
    const productId = product?.id
    const qty = Math.max(1, Number(quantity) || 1)
    if (!productId) throw new Error('This product is unavailable.')

    const existing = items.value.find(item => item.product_id === productId)
    const nextQuantity = Number(existing?.quantity || 0) + qty
    const stock = Number(product.stock_quantity)
    if (Number.isFinite(stock) && nextQuantity > stock) {
      const message = stock > 0
        ? `Only ${stock} available. You already have ${existing?.quantity || 0} in your cart.`
        : 'This product is out of stock.'
      error.value = message
      throw new Error(message)
    }

    setPending(productId, true)
    error.value = ''
    try {
      if (isAuthenticated.value) {
        await api.post('/cart/items', { product_id: productId, quantity: qty })
        await fetchServer({ silent: true })
      } else if (existing) {
        existing.quantity = nextQuantity
        guestCart.value = [...guestCart.value]
        saveGuest()
      } else {
        guestCart.value = [...guestCart.value, { product_id: productId, product, quantity: qty }]
        saveGuest()
      }
      return true
    } catch (err) {
      const message = getErrorMessage(err, 'Could not add this item to your cart.')
      error.value = message
      throw new Error(message)
    } finally {
      setPending(productId, false)
    }
  }

  const updateQty = async (itemId, quantity) => {
    const item = isAuthenticated.value
      ? serverCart.value?.items?.find(entry => entry.id === itemId)
      : guestCart.value.find(entry => entry.product_id === itemId)
    if (!item) return false

    const qty = Number(quantity)
    const productId = item.product_id
    const stock = Number(item.product?.stock_quantity)
    if (qty > 0 && Number.isFinite(stock) && qty > stock) {
      const message = `Only ${stock} available.`
      error.value = message
      throw new Error(message)
    }

    setPending(productId, true)
    error.value = ''
    try {
      if (isAuthenticated.value) {
        if (qty <= 0) await api.delete(`/cart/items/${itemId}`)
        else await api.put(`/cart/items/${itemId}`, { quantity: qty })
        await fetchServer({ silent: true })
      } else {
        if (qty <= 0) {
          guestCart.value = guestCart.value.filter(entry => entry.product_id !== itemId)
        } else {
          item.quantity = qty
          guestCart.value = [...guestCart.value]
        }
        saveGuest()
      }
      return true
    } catch (err) {
      const message = getErrorMessage(err, 'Could not update this item.')
      error.value = message
      throw new Error(message)
    } finally {
      setPending(productId, false)
    }
  }

  const removeFromCart = async (itemId) => updateQty(itemId, 0)

  const clearCart = async () => {
    loading.value = true
    error.value = ''
    try {
      if (isAuthenticated.value) {
        await api.delete('/cart/clear')
        serverCart.value = { items: [], total_items: 0, subtotal: 0 }
      } else {
        guestCart.value = []
        localStorage.removeItem(LOCAL_KEY)
      }
      selectedIds.value = []
      selectionInitialized = false
    } catch (err) {
      const message = getErrorMessage(err, 'Could not clear your cart.')
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  const removeSelected = async () => {
    const selected = [...selectedItems.value]
    for (const item of selected) {
      await removeFromCart(isAuthenticated.value ? item.id : item.product_id)
    }
  }

  const toggleSelect = (productId) => {
    selectedIds.value = selectedIds.value.includes(productId)
      ? selectedIds.value.filter(id => id !== productId)
      : [...selectedIds.value, productId]
  }

  const selectAll = (value = true) => {
    selectedIds.value = value ? items.value.map(item => item.product_id) : []
  }

  const clearError = () => { error.value = '' }
  const isPending = productId => pendingProductIds.value.has(productId)

  if (!authWatcherStarted) {
    authWatcherStarted = true
    watch(isAuthenticated, (authenticated) => {
      if (authenticated) syncGuest().catch(() => {})
      else {
        serverCart.value = null
        loading.value = false
      }
    }, { immediate: true })
  }

  watch(items, (currentItems, previousItems = []) => {
    const available = currentItems.map(item => item.product_id)
    if (!available.length) {
      selectedIds.value = []
      selectionInitialized = false
      return
    }

    if (!selectionInitialized) {
      selectedIds.value = available
      selectionInitialized = true
      return
    }

    const previous = new Set(previousItems.map(item => item.product_id))
    const kept = selectedIds.value.filter(id => available.includes(id))
    const added = available.filter(id => !previous.has(id))
    selectedIds.value = [...new Set([...kept, ...added])]
  }, { immediate: true })

  return {
    items,
    count,
    total,
    loading,
    error,
    selectedIds,
    selectedItems,
    selectedCount,
    selectedUnits,
    selectedTotal,
    addToCart,
    updateQty,
    removeFromCart,
    clearCart,
    removeSelected,
    toggleSelect,
    selectAll,
    clearError,
    isPending,
    fetchServer,
  }
}
