<template>
  <div>
    <Navbar />
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 class="text-3xl font-extrabold text-gray-900 mb-2">Data Request</h1>
      <p class="text-gray-500 mb-8">Exercise your GDPR rights — request data export, deletion, or rectification.</p>

      <div class="bg-white rounded-xl p-8">
        <form @submit.prevent="handleSubmit">
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Email Address</label>
              <input
                v-model="form.email"
                type="email"
                required
                placeholder="your@email.com"
                class="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none"
              />
              <p class="text-xs text-gray-400 mt-1">We'll use this to follow up on your request.</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Request Type</label>
              <select
                v-model="form.request_type"
                required
                class="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none"
              >
                <option value="data_export">Data Export — get a copy of my data</option>
                <option value="data_deletion">Data Deletion — erase my data (Right to be Forgotten)</option>
                <option value="rectification">Rectification — correct my data</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Details</label>
              <textarea
                v-model="form.details"
                rows="4"
                placeholder="Please describe your request in detail..."
                class="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-none"
              ></textarea>
            </div>
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="mt-8 w-full bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary-light transition disabled:opacity-50"
          >
            {{ submitting ? 'Submitting...' : 'Submit Request' }}
          </button>
        </form>

        <div v-if="submitted" class="mt-6 bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <p class="text-green-700 font-semibold">✓ Request submitted successfully!</p>
          <p class="text-green-600 text-sm mt-1">We'll respond within 30 days to your email address.</p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { submitDataRequest } from '../api'

const submitting = ref(false)
const submitted = ref(false)
const form = reactive({ email: '', request_type: 'data_export', details: '' })

const handleSubmit = async () => {
  submitting.value = true
  try {
    await submitDataRequest(form)
    submitted.value = true
  } catch (e) {
    alert('Failed to submit. Please email hello@eshshop.eu directly.')
  } finally {
    submitting.value = false
  }
}
</script>
