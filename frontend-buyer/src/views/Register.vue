<template>
  <main class="register-page">
    <header class="register-header safe-top">
      <button type="button" aria-label="Go back" @click="$router.back()">←</button>
      <div><span class="eyebrow">JOIN BECOOL</span><h1>Create account</h1></div>
      <span class="brand-mark">b.</span>
    </header>
    <section class="register-card">
      <form @submit.prevent="handleRegister">
        <label for="register-name">Name</label>
        <input id="register-name" v-model.trim="form.display_name" autocomplete="name" maxlength="100" required placeholder="How should we address you?" />
        <label for="register-email">Email</label>
        <input id="register-email" v-model.trim="form.email" type="email" autocomplete="email" required placeholder="you@example.com" />
        <label for="register-phone">Phone <small>optional</small></label>
        <input id="register-phone" v-model.trim="form.phone" type="tel" autocomplete="tel" placeholder="+357…" />
        <label for="register-password">Password</label>
        <div class="password-field">
          <input id="register-password" v-model="form.password" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="8–72 characters" />
          <button type="button" :aria-label="showPassword ? 'Hide passwords' : 'Show passwords'" @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button>
        </div>
        <p class="password-hint" :class="{ ready: passwordReady }">{{ passwordHint }}</p>
        <label for="register-confirm">Confirm password</label>
        <input id="register-confirm" v-model="form.confirm" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="Repeat your password" />
        <label class="terms-check">
          <input v-model="accepted" type="checkbox" required />
          <span>I agree to the <router-link to="/terms">terms</router-link> and <router-link to="/privacy">privacy policy</router-link>.</span>
        </label>
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <button type="submit" class="submit-button" :disabled="loading || !accepted">{{ loading ? 'Creating account…' : 'Create account' }} <span>→</span></button>
      </form>
      <p class="switch-copy">Already registered? <router-link :to="{ path: '/login', query: $route.query }">Sign in</router-link></p>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useAuth } from '../composables/useAuth'
const { register } = useAuth()
const form = reactive({ display_name:'', email:'', phone:'', password:'', confirm:'' })
const accepted = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const passwordBytes = computed(() => new TextEncoder().encode(form.password).length)
const passwordReady = computed(() => form.password.length >= 8 && passwordBytes.value <= 72 && /[A-Za-z]/.test(form.password) && /\d/.test(form.password))
const passwordHint = computed(() => passwordBytes.value > 72 ? 'Password is too long. Use no more than 72 UTF-8 bytes.' : passwordReady.value ? 'Password looks ready.' : 'Use at least 8 characters with one letter and one number.')
const handleRegister = async () => {
  error.value = ''
  if (passwordBytes.value > 72) { error.value = 'Password is too long. Use no more than 72 UTF-8 bytes.'; return }
  if (!passwordReady.value) { error.value = 'Choose a stronger password using a letter and a number.'; return }
  if (form.password !== form.confirm) { error.value = 'Passwords do not match.'; return }
  loading.value = true
  try {
    await register({
      display_name: form.display_name,
      email: form.email,
      phone: form.phone || undefined,
      password: form.password,
    })
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'We could not create your account.'
  } finally { loading.value = false }
}
</script>

<style scoped>
.register-page{min-height:100vh;padding-bottom:35px;background:#f5f2e9;color:#183f35}.register-header{display:grid;grid-template-columns:48px 1fr 48px;align-items:center;max-width:560px;min-height:76px;margin:auto;padding:8px 15px}.register-header>button{width:44px;height:44px;border:1px solid #d7ddd4;border-radius:50%;background:#fffdf8;font-size:20px}.eyebrow{color:#758177;font-size:9px;font-weight:850;letter-spacing:.18em}.register-header h1{margin:3px 0 0;font-family:Georgia,serif;font-size:22px}.brand-mark{display:grid;width:37px;height:37px;place-items:center;justify-self:end;border-radius:13px;background:#d9f06a;font-family:Georgia,serif;font-size:23px;font-weight:800}.register-card{width:calc(100% - 28px);max-width:530px;margin:auto;padding:22px;border:1px solid rgba(23,72,59,.09);border-radius:24px;background:#fffdf8;box-shadow:0 12px 36px rgba(31,59,48,.07)}.register-card form{display:grid;grid-template-columns:124px minmax(0,1fr);column-gap:10px;row-gap:9px;align-items:center}.register-card label{margin:0;font-size:11px;font-weight:800;line-height:1.25}.register-card label small{color:#8a958e;font-weight:500}.register-card input:not([type=checkbox]){width:100%;min-height:46px;padding:0 13px;border:1px solid #d7ddd4;border-radius:13px;background:#fff;font-size:13px}.password-field{position:relative}.password-field input{padding-right:55px!important}.password-field button{position:absolute;top:3px;right:4px;width:49px;height:40px;color:#17483b;font-size:10px;font-weight:800}.terms-check,.form-error,.submit-button{grid-column:1/-1}.terms-check{display:flex;align-items:start;gap:9px;margin-top:10px!important;color:#64736a;line-height:1.45}.terms-check input{width:19px;height:19px;flex:none;accent-color:#17483b}.terms-check a,.switch-copy a{color:#17483b;font-weight:800;text-decoration:underline}.form-error{margin:3px 0 0;padding:10px 12px;border-radius:11px;background:#fff0e8;color:#7d4228;font-size:12px}.submit-button{min-height:52px;margin-top:5px;border-radius:999px;background:#17483b;color:#fffdf8;font-size:13px;font-weight:850}.submit-button:disabled{opacity:.5}.switch-copy{margin:18px 0 0;color:#6b7971;font-size:12px;text-align:center}.password-hint{grid-column:2;margin:-2px 0 2px;color:#8a4a20;font-size:10px;line-height:1.35}.password-hint.ready{color:#47704d}@media(max-width:480px){.register-card{padding:20px}.register-card form{grid-template-columns:1fr;row-gap:6px}.register-card label{margin-top:7px}.password-hint,.terms-check,.form-error,.submit-button{grid-column:auto}.password-hint{margin:0 0 2px}}.register-page a:focus-visible,.register-page button:focus-visible,.register-page input:focus-visible{outline:3px solid #d9f06a;outline-offset:2px}
</style>
