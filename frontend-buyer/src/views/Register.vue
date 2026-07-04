<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Create Account</h1>
        <p class="text-gray-500 mt-2">Join BeCool Market today</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username *</label>
          <input v-model="form.username" type="text" required
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
          <input v-model="form.display_name" type="text"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="form.email" type="email"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <input v-model="form.phone" type="tel"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password *</label>
          <input v-model="form.password" type="password" required minlength="6"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password *</label>
          <input v-model="form.confirm" type="password" required minlength="6"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none transition" />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </form>

      <p class="text-center text-gray-500 mt-6">
        Already have an account?
        <router-link to="/login" class="text-primary font-semibold hover:underline">Sign In</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const { register } = useAuth()
const form = ref({ username: '', display_name: '', email: '', phone: '', password: '', confirm: '' })
const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  if (form.value.password !== form.value.confirm) {
    error.value = 'Passwords do not match'
    return
  }
  loading.value = true
  try {
    await register({
      username: form.value.username,
      password: form.value.password,
      display_name: form.value.display_name,
      email: form.value.email || undefined,
      phone: form.value.phone || undefined,
    })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
