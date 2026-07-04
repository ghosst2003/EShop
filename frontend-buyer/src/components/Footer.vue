<template>
  <footer class="bg-[#1B1B1B] text-white">
    <div class="max-w-[1440px] mx-auto px-10 py-12">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-8">
        <!-- Shopping -->
        <div>
          <h4 class="text-sm font-bold mb-4">Shopping</h4>
          <ul class="space-y-3 text-[13px] text-gray-400">
            <li><router-link to="/browse" class="hover:text-white transition">All Products</router-link></li>
            <li><a href="/browse?sort=new" class="hover:text-white transition">New Arrivals</a></li>
            <li><a href="/browse?sort=popular" class="hover:text-white transition">Best Sellers</a></li>
          </ul>
        </div>
        <!-- Support -->
        <div>
          <h4 class="text-sm font-bold mb-4">Support</h4>
          <ul class="space-y-3 text-[13px] text-gray-400">
            <li><router-link to="/data-request" class="hover:text-white transition">Help Center</router-link></li>
            <li><a href="mailto:support@becool.market" class="hover:text-white transition">Contact Us</a></li>
            <li><router-link to="/privacy" class="hover:text-white transition">Returns & Refunds</router-link></li>
          </ul>
        </div>
        <!-- Company -->
        <div>
          <h4 class="text-sm font-bold mb-4">Company</h4>
          <ul class="space-y-3 text-[13px] text-gray-400">
            <li><router-link to="/imprint" class="hover:text-white transition">About Us</router-link></li>
            <li><router-link to="/privacy" class="hover:text-white transition">Privacy Policy</router-link></li>
            <li><router-link to="/terms" class="hover:text-white transition">Terms of Service</router-link></li>
          </ul>
        </div>
      </div>

      <div class="border-t border-[#333] mt-10 pt-6 flex flex-col md:flex-row justify-between items-center text-xs text-gray-500">
        <span>© 2026 BeCool Market. All rights reserved.</span>
        <span class="mt-2 md:mt-0">Secure Payments  ·  EU Shipping  ·  Buyer Guarantee  ·  Eco-Friendly</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>
