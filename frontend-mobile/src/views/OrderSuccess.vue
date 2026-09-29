<template>
  <div class="min-h-screen bg-[#F7F7F7] flex flex-col items-center justify-center px-6">
    <div class="text-center">
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span class="text-4xl">✓</span>
      </div>
      <h1 class="text-2xl font-extrabold text-gray-900 mb-2">Order Placed!</h1>
      <p class="text-gray-500 mb-8">Your order has been confirmed and will be shipped soon.</p>

      <div class="space-y-3">
        <router-link to="/my-orders" class="block w-full bg-primary text-white font-bold py-3 rounded-full tap-active">
          View My Orders
        </router-link>
        <router-link to="/" class="block w-full bg-white text-primary font-bold py-3 rounded-full border border-orange-light tap-active">
          Continue Shopping
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Simple success page
</script>
