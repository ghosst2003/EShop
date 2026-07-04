<template>
  <div>
    <Navbar />
    <div class="max-w-2xl mx-auto px-4 py-16 text-center">
      <div class="bg-white rounded-2xl shadow p-12">
        <div class="text-6xl mb-4">🎉</div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
        <p class="text-gray-500 mb-8">Thank you for your purchase</p>

        <div v-if="orderId" class="bg-gray-50 rounded-xl p-6 mb-8 inline-block">
          <p class="text-sm text-gray-500">Order ID</p>
          <p class="text-xl font-bold">#{{ orderId }}</p>
        </div>

        <div class="flex gap-4 justify-center">
          <router-link to="/my-orders"
            class="bg-primary text-white font-bold px-8 py-3 rounded-xl hover:bg-primary-light transition">
            View My Orders
          </router-link>
          <router-link to="/"
            class="border border-gray-300 text-gray-700 font-bold px-8 py-3 rounded-xl hover:bg-gray-50 transition">
            Continue Shopping
          </router-link>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const orderId = ref(route.query.order_id || null)
</script>
