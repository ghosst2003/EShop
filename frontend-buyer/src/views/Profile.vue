<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-12">
      <h1 class="text-2xl font-bold text-gray-900 mb-8">My Profile</h1>

      <div class="bg-white rounded-2xl shadow p-8">
        <form @submit.prevent="handleUpdate" class="space-y-5">
          <div class="flex items-center gap-6 mb-8">
            <div class="w-20 h-20 rounded-full bg-orange-light flex items-center justify-center text-3xl font-bold text-primary">
              {{ user?.display_name?.[0]?.toUpperCase() || '?' }}
            </div>
            <div>
              <h2 class="font-bold text-lg">{{ user?.display_name }}</h2>
              <p class="text-gray-500 text-sm">@{{ user?.username }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
              <input v-model="form.display_name" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input v-model="form.email" type="email" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input v-model="form.phone" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-orange-400 outline-none" />
            </div>
          </div>

          <p v-if="success" class="text-green-600 text-sm">{{ success }}</p>
          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

          <button type="submit" :disabled="loading"
            class="bg-primary text-white font-bold px-8 py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50">
            {{ loading ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- Quick Links -->
      <div class="mt-8 grid grid-cols-2 gap-4">
        <router-link to="/my-orders" class="bg-white rounded-2xl shadow p-6 text-center hover:shadow-lg transition">
          <div class="text-2xl mb-2">📦</div>
          <div class="font-semibold">My Orders</div>
        </router-link>
        <router-link to="/" class="bg-white rounded-2xl shadow p-6 text-center hover:shadow-lg transition">
          <div class="text-2xl mb-2">🛍️</div>
          <div class="font-semibold">Continue Shopping</div>
        </router-link>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuth } from '../composables/useAuth'
import { updateProfileApi } from '../api'

const { user, updateProfile } = useAuth()
const form = ref({ display_name: '', email: '', phone: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  form.value = {
    display_name: user.value?.display_name || '',
    email: user.value?.email || '',
    phone: user.value?.phone || '',
  }
})

const handleUpdate = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await updateProfile(form.value)
    success.value = 'Profile updated successfully!'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Update failed'
  } finally {
    loading.value = false
  }
}
</script>
