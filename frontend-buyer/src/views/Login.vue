<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Welcome Back</h1>
        <p class="text-gray-500 mt-2">Sign in to your BeCool Market account</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input v-model="form.username" type="text" required
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition"
            placeholder="Enter your username" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input v-model="form.password" type="password" required
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition"
            placeholder="Enter your password" />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <p class="text-center text-gray-500 mt-6">
        Don't have an account?
        <router-link to="/register" class="text-primary font-semibold hover:underline">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const { login } = useAuth()
const router = useRouter()
const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await login(form.value.username, form.value.password)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
