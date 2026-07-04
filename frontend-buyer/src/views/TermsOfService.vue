<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <div class="max-w-[800px] mx-auto px-10 py-12">
      <h1 class="text-3xl font-bold text-gray-800 mb-8">Terms of Service</h1>

      <div class="prose prose-gray max-w-none">
        <p class="text-gray-600 text-sm mb-8">Last updated: June 2026</p>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">1. Acceptance of Terms</h2>
          <p class="text-gray-600 leading-relaxed">
            By accessing and using BeCool Market ("Platform"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">2. Use License</h2>
          <p class="text-gray-600 leading-relaxed">
            Permission is granted to temporarily download one copy of the materials (information or software) on BeCool Market's Platform for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:
          </p>
          <ul class="list-disc ml-6 text-gray-600 leading-relaxed mt-2">
            <li>Modify or copy the materials</li>
            <li>Use the materials for any commercial purpose</li>
            <li>Attempt to decompile or reverse engineer any software contained on the Platform</li>
            <li>Remove any copyright or other proprietary notations from the materials</li>
          </ul>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">3. Buyer & Seller Obligations</h2>
          <p class="text-gray-600 leading-relaxed">
            <strong>Buyers:</strong> Must provide accurate delivery information, pay for purchases within the specified timeframe, and inspect items upon receipt. Disputes must be reported within 14 days of delivery.
          </p>
          <p class="text-gray-600 leading-relaxed mt-3">
            <strong>Sellers:</strong> Must provide accurate item descriptions, ship within agreed timeframes, and ensure items match their listed condition. Sellers are responsible for any damage during transit unless otherwise agreed.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">4. Payment Terms</h2>
          <p class="text-gray-600 leading-relaxed">
            All prices are displayed in EUR and include applicable VAT. Payment is processed through our secure payment gateway. BeCool Market holds payment in escrow until the buyer confirms receipt of the item or the buyer protection period expires.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">5. Shipping & Delivery</h2>
          <p class="text-gray-600 leading-relaxed">
            Shipping is the responsibility of the seller. All items must be shipped within 3 business days of payment confirmation. Tracking information must be provided. Buyers should inspect items within 14 days of delivery and report any issues immediately.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">6. Returns & Refunds</h2>
          <p class="text-gray-600 leading-relaxed">
            Returns are accepted within 14 days of delivery if the item does not match the listing description. The buyer must contact the seller through the Platform's messaging system. Refunds are processed within 5 business days after the item is returned and verified.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">7. Limitation of Liability</h2>
          <p class="text-gray-600 leading-relaxed">
            BeCool Market provides the Platform as an intermediary service. We are not liable for the quality, safety, or legality of items listed, the truth or accuracy of listings, or the ability of sellers to sell items. Our total liability shall not exceed the amount paid by the buyer for the specific transaction in dispute.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">8. Governing Law</h2>
          <p class="text-gray-600 leading-relaxed">
            These terms are governed by the laws of the European Union. Any disputes arising from these terms shall be resolved through the Platform's dispute resolution process first, and if unresolved, through the appropriate EU consumer protection authority.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 mb-3">9. Contact</h2>
          <p class="text-gray-600 leading-relaxed">
            For questions about these Terms of Service, please contact us at <a href="mailto:legal@becool.market" class="text-primary hover:underline">legal@becool.market</a>.
          </p>
        </section>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
</script>
