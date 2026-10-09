<template>
  <aside v-if="visible" class="consent" role="dialog" aria-modal="true" aria-labelledby="cookie-title">
    <div class="consent-inner">
      <span class="eyebrow">YOUR PRIVACY</span><h2 id="cookie-title">Choose your cookie settings</h2>
      <p>Essential cookies keep your cart and sign-in working. Optional analytics help us improve the shop and stay off until you choose them.</p>
      <div v-if="customizing" class="choices">
        <label><span><strong>Essential</strong><small>Cart, security and checkout</small></span><input type="checkbox" checked disabled /></label>
        <label><span><strong>Analytics</strong><small>Anonymous shopping journey insights</small></span><input v-model="analytics" type="checkbox" /></label>
      </div>
      <div class="actions"><button type="button" class="secondary" @click="customizing=!customizing">{{ customizing?'Back':'Customize' }}</button><button type="button" @click="save(false)">Essential only</button><button type="button" class="primary" @click="save(customizing?analytics:true)">{{ customizing?'Save choices':'Accept all' }}</button></div>
      <router-link to="/legal/privacy">Read our privacy notice</router-link>
    </div>
  </aside>
</template>
<script setup>
import { ref } from 'vue'; import { recordConsent } from '../api'; import { trackCommerceEvent } from '../composables/useAnalytics'
const stored=localStorage.getItem('becool-cookie-preferences');let storedChoice={},hasStoredChoice=false;try{if(stored){storedChoice=JSON.parse(stored);hasStoredChoice=true}}catch{localStorage.removeItem('becool-cookie-preferences')}const visible=ref(!hasStoredChoice),customizing=ref(false),analytics=ref(Boolean(storedChoice.analytics))
const sessionId=localStorage.getItem('becool-consent-session')||crypto.randomUUID();localStorage.setItem('becool-consent-session',sessionId)
async function save(allowed){analytics.value=allowed;const choice={essential:true,analytics:allowed,updated_at:new Date().toISOString()};localStorage.setItem('becool-cookie-preferences',JSON.stringify(choice));visible.value=false;if(allowed)trackCommerceEvent('page_view',{path:location.pathname});try{await recordConsent({session_id:sessionId,consent_type:'cookie',consent_given:allowed})}catch{}}
</script>
<style scoped>
.consent{position:fixed;inset:0;z-index:100;display:flex;align-items:flex-end;justify-content:center;background:rgba(16,38,31,.32);padding:14px}.consent-inner{width:min(100%,600px);padding:22px;border-radius:24px;background:#fffdf8;color:#17483b;box-shadow:0 24px 70px rgba(16,38,31,.28)}.eyebrow{font-size:9px;font-weight:900;letter-spacing:.18em;color:#718079}.consent h2{margin:5px 0 8px;font:700 26px/1.05 Georgia,serif}.consent p{margin:0;color:#66766d;font-size:12px;line-height:1.55}.choices{display:grid;gap:8px;margin-top:14px}.choices label{display:flex;align-items:center;justify-content:space-between;padding:11px;border:1px solid #dfe3db;border-radius:13px}.choices span{display:grid;gap:2px}.choices small{color:#718079}.choices input{width:20px;height:20px;accent-color:#17483b}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}.actions button{min-height:44px;border:1px solid #17483b;border-radius:999px;color:#17483b;font-weight:850}.actions .primary{grid-column:1/-1;background:#17483b;color:#d9f06a}.actions .secondary{border-color:#d5dbd3}.consent a{display:block;margin-top:12px;color:#17483b;font-size:11px;text-align:center;text-decoration:underline;text-underline-offset:3px}@media(min-width:620px){.actions{grid-template-columns:1fr 1fr 1.25fr}.actions .primary{grid-column:auto}}
</style>
