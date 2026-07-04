<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 class="text-3xl font-extrabold text-gray-900 mb-8">Privacy Policy</h1>

      <div class="prose prose-sm max-w-none text-gray-600 space-y-6">
        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">1. Who We Are</h2>
          <p>BeCool Market is a second-hand marketplace operated in the European Union. Our registered address is in Berlin, Germany. Contact us at hello@eshshop.eu.</p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">2. What Data We Collect</h2>
          <ul class="list-disc pl-6 space-y-1">
            <li>Session identifiers (anonymous)</li>
            <li>IP addresses (anonymised in logs)</li>
            <li>Cookie consent preferences</li>
            <li>User-agent strings</li>
            <li>GDPR data request submissions (email, request type, free-text details)</li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">3. Why We Process Your Data</h2>
          <p>We process data based on the following legal grounds under GDPR Article 6:</p>
          <ul class="list-disc pl-6 space-y-1">
            <li><strong>Consent (Art. 6(1)(a)):</strong> Cookie consent for analytics and marketing.</li>
            <li><strong>Legitimate interest (Art. 6(1)(f)):</strong> Operating and improving the marketplace, fraud prevention.</li>
            <li><strong>Legal obligation (Art. 6(1)(c)):</strong> Complying with data protection and commercial law.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">4. Data Retention</h2>
          <p>Cookie consent logs are retained for 24 months. GDPR data request records are retained for 36 months after resolution. No buyer accounts are created in v1, minimising personal data collection.</p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">5. Your Rights</h2>
          <p>Under the GDPR, you have the right to:</p>
          <ul class="list-disc pl-6 space-y-1">
            <li>Access your personal data</li>
            <li>Rectify inaccurate data</li>
            <li>Request erasure (Right to be Forgotten, Article 17)</li>
            <li>Restrict processing</li>
            <li>Data portability</li>
            <li>Withdraw consent at any time</li>
          </ul>
          <p class="mt-2">To exercise any of these rights, please use our <router-link to="/data-request" class="text-primary font-semibold hover:underline">Data Request Form</router-link> or email hello@eshshop.eu. We respond within 30 days.</p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">6. Cookies</h2>
          <p>We use essential cookies (required for site functionality) and optional cookies (analytics, marketing). You can manage your preferences via the cookie banner or <a href="#" class="text-primary">Cookie Settings</a>.</p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-gray-900 mb-3">7. Contact</h2>
          <p>For privacy-related inquiries: <a href="mailto:hello@eshshop.eu" class="text-primary">hello@eshshop.eu</a></p>
          <p>BeCool Market, Berlin, Germany.</p>
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
