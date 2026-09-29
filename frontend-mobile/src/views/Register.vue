<template>
  <div class="min-h-screen bg-[#F7F7F7]">
    <div class="bg-white safe-top border-b border-gray-100">
      <div class="flex items-center px-4 py-3">
        <button @click="$router.back()" class="text-xl tap-active">←</button>
        <h1 class="text-base font-bold flex-1 text-center mr-8">Sign Up</h1>
      </div>
    </div>

    <div class="px-6 py-8">
      <div class="bg-white rounded-2xl p-6 space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700">Display Name</label>
          <input v-model="form.display_name" type="text" class="w-full mt-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary" placeholder="Your name" />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700">Email</label>
          <input v-model="form.email" type="email" class="w-full mt-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary" placeholder="your@email.com" />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700">Password</label>
          <input v-model="form.password" type="password" class="w-full mt-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary" placeholder="Min 8 characters" />
        </div>
        <button @click="handleRegister" :disabled="loading" class="w-full bg-primary text-white font-bold py-3 rounded-full tap-active disabled:opacity-50">
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </div>

      <p class="text-center mt-6 text-sm text-gray-500">
        Already have an account?
        <router-link to="/login" class="text-primary font-semibold tap-active">Sign In</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register } = useAuth()
const form = ref({ display_name: '', email: '', password: '' })
const loading = ref(false)

const handleRegister = async () => {
  loading.value = true
  try {
    await register(form.value.display_name, form.value.email, form.value.password)
    router.push('/')
  } catch (e) {
    alert('Registration failed: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>
