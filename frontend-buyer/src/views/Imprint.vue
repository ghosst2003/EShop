<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 class="text-3xl font-extrabold text-gray-900 mb-8">Imprint (Impressum)</h1>

      <div class="bg-white rounded-xl p-8 space-y-6 text-gray-600">
        <div>
          <h2 class="font-bold text-gray-900 mb-2">Business Information</h2>
          <p>BeCool Market</p>
          <p>Online second-hand marketplace serving customers in the European Union.</p>
        </div>

        <div>
          <h2 class="font-bold text-gray-900 mb-2">Contact</h2>
          <p>Email: <a href="mailto:hello@eshshop.eu" class="text-primary">hello@eshshop.eu</a></p>
          <p>Support hours: Mon–Fri, 9:00–18:00 CET</p>
          <p class="mt-2 text-sm">The operator's registered legal name, address, registration number and VAT number must be added here before public commercial launch.</p>
        </div>

        <div>
          <h2 class="font-bold text-gray-900 mb-2">Dispute Resolution</h2>
          <p>The European Commission provides a platform for online dispute resolution (ODR): <a href="https://ec.europa.eu/consumers/odr" target="_blank" class="text-primary underline">ec.europa.eu/consumers/odr</a></p>
          <p class="mt-2">We are not willing or obliged to participate in dispute resolution proceedings before a consumer arbitration board.</p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
</script>
