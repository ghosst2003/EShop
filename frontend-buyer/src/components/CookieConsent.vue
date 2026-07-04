<template>
  <div v-if="!consented" class="fixed bottom-4 left-4 right-4 z-50 md:left-8 md:right-8 lg:left-16 lg:right-16">
    <div class="bg-white rounded-xl shadow-lg p-4 md:p-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="flex-1">
          <p class="text-sm md:text-base text-gray-700">
            We use cookies to enhance your experience, analyse site traffic, and serve personalised content.
            By clicking "Accept All", you consent to all cookies.
          </p>
        </div>
        <div class="flex gap-2 shrink-0">
          <button
            @click="handleAccept"
            class="px-6 py-2 bg-footer-dark text-white text-sm font-semibold rounded-lg hover:bg-gray-800 transition"
          >
            Accept All
          </button>
          <button
            @click="handleCustomize"
            class="px-6 py-2 bg-orange-light text-gray-800 text-sm font-semibold rounded-lg hover:bg-orange-bg transition"
          >
            Customise
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { recordConsent } from '../api'

const consented = ref(true)

onMounted(() => {
  consented.value = localStorage.getItem('cookie_consent') === 'true'
})

const handleAccept = async () => {
  try {
    await recordConsent({ session_id: getSessionId(), consent_type: 'cookie', consent_given: true })
  } catch {}
  localStorage.setItem('cookie_consent', 'true')
  consented.value = true
}

const handleCustomize = () => {
  localStorage.setItem('cookie_consent', 'true')
  consented.value = true
}

const getSessionId = () => {
  let sid = sessionStorage.getItem('session_id')
  if (!sid) {
    sid = crypto.randomUUID?.() || Math.random().toString(36).slice(2)
    sessionStorage.setItem('session_id', sid)
  }
  return sid
}
</script>
