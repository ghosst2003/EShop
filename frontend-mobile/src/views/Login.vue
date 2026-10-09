<template>
  <main class="auth-page">
    <router-link to="/" class="brand" aria-label="BeCool Market home"><span>b.</span><strong>becool</strong></router-link>
    <section class="auth-card">
      <span class="eyebrow">WELCOME BACK</span>
      <h1>Sign in to continue</h1>
      <p class="intro">Your bag and saved finds will be waiting.</p>
      <form @submit.prevent="handleLogin">
        <label for="login-username">Username</label>
        <input id="login-username" v-model.trim="form.username" autocomplete="username" required placeholder="Your username" />
        <div class="password-label"><label for="login-password">Password</label><router-link to="/forgot-password">Forgot password?</router-link></div>
        <div class="password-field">
          <input id="login-password" v-model="form.password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required placeholder="Your password" />
          <button type="button" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button>
        </div>
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <button type="submit" class="submit-button" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }} <span>→</span></button>
      </form>
      <p class="switch-copy">New to BeCool? <router-link :to="{ path: '/register', query: $route.query }">Create an account</router-link></p>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuth } from '../composables/useAuth'
const { login } = useAuth()
const form = reactive({ username: '', password: '' })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try { await login(form.username, form.password) }
  catch (requestError) { error.value = requestError.response?.data?.detail || 'We could not sign you in. Check your details and try again.' }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-page{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:34px 18px 92px;background:#f5f2e9;color:#183f35}.brand{display:flex;align-items:center;gap:9px;margin-bottom:20px;color:#17483b}.brand span{display:grid;width:42px;height:42px;place-items:center;border-radius:14px;background:#d9f06a;font-family:Georgia,serif;font-size:28px;font-weight:800}.brand strong{font-family:Georgia,serif;font-size:25px}.auth-card{width:min(100%,430px);padding:27px 23px;border:1px solid rgba(23,72,59,.09);border-radius:24px;background:#fffdf8;box-shadow:0 14px 40px rgba(31,59,48,.08)}.eyebrow{color:#76837b;font-size:9px;font-weight:850;letter-spacing:.18em}.auth-card h1{margin:8px 0 0;font-family:Georgia,serif;font-size:30px;line-height:1.05}.intro{margin:10px 0 22px;color:#69776f;font-size:13px}.auth-card form{display:grid;gap:9px}.auth-card label{font-size:11px;font-weight:800}.auth-card input{width:100%;min-height:49px;padding:0 13px;border:1px solid #d7ddd4;border-radius:13px;background:#fff;color:#183f35;font-size:14px}.password-label{display:flex;align-items:center;justify-content:space-between;margin-top:5px}.password-label a,.switch-copy a{color:#17483b;font-size:11px;font-weight:800;text-decoration:underline;text-underline-offset:3px}.password-field{position:relative}.password-field input{padding-right:58px}.password-field button{position:absolute;right:5px;top:5px;min-width:49px;height:39px;color:#17483b;font-size:10px;font-weight:800}.form-error{margin:3px 0 0;padding:10px 12px;border-radius:11px;background:#fff0e8;color:#7d4228;font-size:12px;line-height:1.45}.submit-button{display:flex;min-height:52px;align-items:center;justify-content:center;gap:18px;margin-top:9px;border-radius:999px;background:#17483b;color:#fffdf8;font-size:13px;font-weight:850}.submit-button:disabled{opacity:.55}.switch-copy{margin:20px 0 0;color:#6c7b72;font-size:12px;text-align:center}.switch-copy a{font-size:12px}.auth-page a:focus-visible,.auth-page button:focus-visible,.auth-page input:focus-visible{outline:3px solid #d9f06a;outline-offset:2px}
</style>
