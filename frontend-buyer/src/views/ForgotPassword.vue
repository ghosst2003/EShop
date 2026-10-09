<template>
  <main class="reset-page">
    <router-link to="/login" class="back-link">← Back to sign in</router-link>
    <section class="reset-card">
      <span class="brand-mark">b.</span>
      <span class="eyebrow">ACCOUNT RECOVERY</span>
      <h1>{{ resetToken ? 'Choose a new password' : 'Reset your password' }}</h1>
      <p>{{ resetToken ? 'Use 8+ characters with at least one letter and one number.' : 'Enter your username or email to create a secure reset link.' }}</p>
      <form v-if="!resetToken" @submit.prevent="requestReset">
        <label for="reset-account">Username or email</label>
        <input id="reset-account" v-model.trim="account" autocomplete="username" required />
        <button :disabled="loading">{{ loading ? 'Preparing…' : 'Continue' }}</button>
      </form>
      <form v-else @submit.prevent="confirmReset">
        <label for="new-password">New password</label>
        <input id="new-password" v-model="newPassword" type="password" autocomplete="new-password" minlength="8" required />
        <label for="confirm-new-password">Confirm password</label>
        <input id="confirm-new-password" v-model="confirmPassword" type="password" autocomplete="new-password" minlength="8" required />
        <button :disabled="loading">{{ loading ? 'Updating…' : 'Update password' }}</button>
      </form>
      <p v-if="message" class="message" :class="{ error }" role="status">{{ message }}</p>
    </section>
  </main>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import { confirmPasswordReset, requestPasswordReset } from '../api'
const router = useRouter()
const route = useRoute()
const account = ref('')
const resetToken = ref(typeof route.query.token === 'string' ? route.query.token : '')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const message = ref('')
const error = ref(false)
const requestReset = async () => {
  loading.value = true; error.value = false; message.value = ''
  try {
    const { data } = await requestPasswordReset(account.value)
    message.value = data.message
    if (data.reset_token) resetToken.value = data.reset_token
  } catch (requestError) { error.value = true; message.value = requestError.response?.data?.detail || 'Could not start password reset.' }
  finally { loading.value = false }
}
const confirmReset = async () => {
  if (newPassword.value !== confirmPassword.value) { error.value = true; message.value = 'Passwords do not match.'; return }
  loading.value = true; error.value = false
  try {
    const { data } = await confirmPasswordReset(resetToken.value, newPassword.value)
    message.value = data.message
    setTimeout(() => router.replace('/login'), 900)
  } catch (requestError) { error.value = true; message.value = requestError.response?.data?.detail || 'Could not update password.' }
  finally { loading.value = false }
}
</script>
<style scoped>
.reset-page{min-height:100vh;padding:28px 18px;background:#f5f2e9;color:#183f35}.back-link{display:inline-flex;min-height:44px;align-items:center;color:#17483b;font-size:12px;font-weight:800}.reset-card{max-width:430px;margin:45px auto 0;padding:27px 23px;border-radius:24px;background:#fffdf8;box-shadow:0 14px 40px rgba(31,59,48,.08)}.brand-mark{display:grid;width:45px;height:45px;place-items:center;margin-bottom:18px;border-radius:14px;background:#d9f06a;font-family:Georgia,serif;font-size:28px;font-weight:800}.eyebrow{color:#758177;font-size:9px;font-weight:850;letter-spacing:.18em}.reset-card h1{margin:8px 0 0;font-family:Georgia,serif;font-size:29px}.reset-card>p{color:#68776f;font-size:13px;line-height:1.5}.reset-card form{display:grid;gap:8px;margin-top:20px}.reset-card label{font-size:11px;font-weight:800}.reset-card input{min-height:49px;padding:0 13px;border:1px solid #d7ddd4;border-radius:13px}.reset-card form button{min-height:50px;margin-top:8px;border-radius:999px;background:#17483b;color:white;font-weight:850}.message{margin:14px 0 0;padding:10px;border-radius:11px;background:#eef3cb;color:#17483b;font-size:12px}.message.error{background:#fff0e8;color:#7d4228}
</style>
