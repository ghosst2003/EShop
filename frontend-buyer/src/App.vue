<template>
  <div class="min-h-screen bg-[#F2F3F7]">
    <router-view />
    <CookieConsent />
  </div>
</template>

<script setup>
import CookieConsent from './components/CookieConsent.vue'
</script>
