<template>
  <div v-if="visible" class="cookie-layer" role="dialog" aria-modal="true" aria-labelledby="cookie-title">
    <section class="cookie-card"><div><span>YOUR PRIVACY</span><h2 id="cookie-title">Choose how BeCool uses cookies</h2><p>Essential cookies keep checkout and sign-in working. Analytics helps us understand which products and pages are useful.</p></div>
      <div v-if="custom" class="choices"><label><span><strong>Essential</strong><small>Required for security and shopping functions</small></span><input type="checkbox" checked disabled></label><label><span><strong>Analytics</strong><small>Anonymous usage and commerce events</small></span><input v-model="analytics" type="checkbox"></label></div>
      <div class="buttons"><button class="secondary" @click="custom?save():custom=true">{{ custom?'Save choices':'Customise' }}</button><button class="secondary" @click="reject">Essential only</button><button class="primary" @click="accept">Accept all</button></div>
      <router-link to="/privacy">Read our privacy policy</router-link>
    </section>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';import { recordConsent } from '../api'
const visible=ref(false),custom=ref(false),analytics=ref(false);const KEY='becool-cookie-preferences'
function session(){let id=sessionStorage.getItem('session_id');if(!id){id=crypto.randomUUID();sessionStorage.setItem('session_id',id)}return id}
async function persist(value){localStorage.setItem(KEY,JSON.stringify(value));visible.value=false;try{await recordConsent({session_id:session(),consent_type:'cookie',consent_given:Boolean(value.analytics)})}catch{}}
const accept=()=>persist({essential:true,analytics:true,updated_at:new Date().toISOString()}),reject=()=>persist({essential:true,analytics:false,updated_at:new Date().toISOString()}),save=()=>persist({essential:true,analytics:analytics.value,updated_at:new Date().toISOString()})
onMounted(()=>{visible.value=!localStorage.getItem(KEY)})
</script>
<style scoped>.cookie-layer{position:fixed;inset:0;z-index:100;display:flex;align-items:end;justify-content:center;padding:24px;background:rgba(16,45,37,.28);backdrop-filter:blur(3px)}.cookie-card{width:min(100%,760px);display:grid;gap:17px;padding:24px;border:1px solid #d9ded6;border-radius:24px;background:#fffdf8;box-shadow:0 24px 70px rgba(23,63,52,.22);color:#173f34}.cookie-card>div:first-child>span{font-size:9px;font-weight:900;letter-spacing:.18em;color:#76817c}.cookie-card h2{margin:5px 0;font:700 25px Georgia,serif}.cookie-card p{margin:0;color:#65756e;font-size:12px;line-height:1.55}.choices{display:grid;gap:8px}.choices label{display:flex;justify-content:space-between;align-items:center;padding:11px 13px;border-radius:12px;background:#f2f4ec}.choices strong,.choices small{display:block}.choices small{margin-top:2px;color:#76817c;font-size:10px}.choices input{width:19px;height:19px;accent-color:#173f34}.buttons{display:flex;justify-content:flex-end;gap:8px}.buttons button{min-height:43px;padding:0 16px;border-radius:999px;font-size:11px;font-weight:850}.secondary{border:1px solid #cad2cc;background:white;color:#173f34}.primary{border:0;background:#173f34;color:white}.cookie-card>a{color:#52685f;font-size:10px;text-decoration:underline}@media(max-width:620px){.cookie-layer{padding:12px}.buttons{display:grid;grid-template-columns:1fr 1fr}.buttons .primary{grid-column:1/-1}.buttons button{width:100%}}</style>
