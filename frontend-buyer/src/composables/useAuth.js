import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const token = ref(localStorage.getItem('token') || null)
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

export function useAuth() {
  const router = useRouter()
  const isAuthenticated = computed(() => !!token.value)
  const isBuyer = computed(() => user.value?.role === 'buyer')

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  }

  const register = async (userData) => {
    const res = await api.post('/auth/register', userData)
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  const updateProfile = async (profileData) => {
    const res = await api.put('/auth/profile', profileData)
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
  }

  return { token, user, isAuthenticated, isBuyer, login, register, logout, updateProfile }
}
