import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const readStoredUser = () => {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

const token = ref(localStorage.getItem('token') || null)
const user = ref(readStoredUser())

const clearSession = () => {
  token.value = null
  user.value = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

if (typeof window !== 'undefined') {
  window.addEventListener('auth:expired', clearSession)
}

export function useAuth() {
  const router = useRouter()
  const isAuthenticated = computed(() => Boolean(token.value))
  const isBuyer = computed(() => user.value?.role === 'buyer')

  const storeSession = (data) => {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  const continueAfterAuth = () => {
    const redirect = router.currentRoute.value.query.redirect
    const safeRedirect = typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
      ? redirect
      : '/'
    router.replace(safeRedirect)
  }

  const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    storeSession(response.data)
    continueAfterAuth()
    return response.data
  }

  const register = async (userData) => {
    const response = await api.post('/auth/register', userData)
    if (response.data.verification_required) {
      const redirect = router.currentRoute.value.query.redirect
      router.replace({
        path: '/verify-email',
        query: {
          token: response.data.email_verification_token || undefined,
          redirect: typeof redirect === 'string' ? redirect : undefined,
        },
      })
      return response.data
    }
    storeSession(response.data)
    continueAfterAuth()
    return response.data
  }

  const verifyEmail = async (verificationToken) => {
    const response = await api.post('/auth/email-verification/confirm', { token: verificationToken })
    storeSession(response.data)
    return response.data
  }

  const logout = () => {
    clearSession()
    router.replace('/login')
  }

  const updateProfile = async (profileData) => {
    const response = await api.put('/auth/profile', profileData)
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  const refreshUser = async () => {
    if (!token.value) return null
    const response = await api.get('/auth/me')
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  return {
    token,
    user,
    isAuthenticated,
    isBuyer,
    login,
    register,
    verifyEmail,
    logout,
    updateProfile,
    refreshUser,
    clearSession,
  }
}
