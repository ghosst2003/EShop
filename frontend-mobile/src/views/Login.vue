<template>
  <div class="min-h-screen bg-[#F7F7F7] flex flex-col justify-center px-6">
    <div class="text-center mb-8">
      <div class="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center text-white text-3xl font-black mx-auto mb-4">C</div>
      <h1 class="text-2xl font-extrabold text-gray-900">Sign In</h1>
      <p class="text-sm text-gray-500 mt-1">Welcome back to BeCool Market</p>
    </div>

    <div class="bg-white rounded-2xl p-6 space-y-4">
      <div>
        <label class="text-sm font-medium text-gray-700">Email or Username</label>
        <input v-model="form.username" type="text" class="w-full mt-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary" placeholder="Enter your email" />
      </div>
      <div>
        <label class="text-sm font-medium text-gray-700">Password</label>
        <input v-model="form.password" type="password" class="w-full mt-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary" placeholder="Enter password" @keyup.enter="handleLogin" />
      </div>
      <button @click="handleLogin" :disabled="loading" class="w-full bg-primary text-white font-bold py-3 rounded-full tap-active disabled:opacity-50">
        {{ loading ? 'Signing in...' : 'Sign In' }}
      </button>
    </div>

    <p class="text-center mt-6 text-sm text-gray-500">
      Don't have an account?
      <router-link to="/register" class="text-primary font-semibold tap-active">Sign Up</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) return
  loading.value = true
  try {
    await login(form.value.username, form.value.password)
    router.push('/')
  } catch (e) {
    alert('Login failed: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>
