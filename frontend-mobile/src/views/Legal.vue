<template>
  <main class="legal-page safe-top">
    <header><button type="button" aria-label="Go back" @click="$router.back()">←</button><div><span>HELP & POLICIES</span><h1>{{ content.title }}</h1></div></header>
    <nav aria-label="Policy sections">
      <router-link v-for="item in sections" :key="item.key" :to="`/legal/${item.key}`">{{ item.label }}</router-link>
    </nav>
    <article>
      <p class="lead">{{ content.lead }}</p>
      <section v-for="block in content.blocks" :key="block.heading"><h2>{{ block.heading }}</h2><p>{{ block.copy }}</p></section>
      <a v-if="section === 'support'" class="contact" href="mailto:support@becool.shop">Email support</a>
    </article>
  </main>
</template>
<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route=useRoute(); const section=computed(()=>route.params.section || 'returns')
const sections=[{key:'returns',label:'Returns'},{key:'privacy',label:'Privacy'},{key:'terms',label:'Terms'},{key:'support',label:'Support'}]
const pages={
 returns:{title:'Returns',lead:'A clear route when a piece is not right for you.',blocks:[{heading:'Return window',copy:'Eligible orders can be requested for return within the return window shown on the product page and order details.'},{heading:'Condition',copy:'Return the item in the same condition received, with all included parts and packaging.'},{heading:'Start a return',copy:'Open My Orders, choose the delivered order, and select Request a return.'}]},
 privacy:{title:'Privacy',lead:'We use only the information needed to run your account, fulfil orders and improve the shop.',blocks:[{heading:'What we store',copy:'Account details, delivery addresses, order records and the preferences you choose to save.'},{heading:'Payments',copy:'Card details are handled by our payment provider and are not stored by BeCool.'},{heading:'Your choices',copy:'You may ask support to export or delete your account data, subject to legal record-keeping duties.'}]},
 terms:{title:'Terms',lead:'These terms explain how purchases, listings and account use work on BeCool.',blocks:[{heading:'Purchases',copy:'An order is accepted after payment confirmation. Availability and delivery estimates are shown before payment.'},{heading:'Product condition',copy:'Pre-loved items may show wear. Read the condition grade, notes and photographs before buying.'},{heading:'Account use',copy:'Keep your sign-in details secure and provide accurate delivery information.'}]},
 support:{title:'Support',lead:'Need help with an order, payment or return? We are here.',blocks:[{heading:'Before you write',copy:'Include your order number and the email on your account so we can help faster.'},{heading:'Response time',copy:'We normally respond within two business days.'}]},
}
const content=computed(()=>pages[section.value] || pages.returns)
</script>
<style scoped>
.legal-page{min-height:100vh;background:#f4f1e8;color:#173f34;padding:1.25rem 1.25rem 7rem}.legal-page>header{display:flex;align-items:center;gap:1rem}.legal-page header button{width:2.75rem;height:2.75rem;border:1px solid #d8d4c8;border-radius:50%;background:#fffdf7;font-size:1.25rem;color:#173f34}.legal-page header span{font-size:.68rem;font-weight:900;letter-spacing:.17em;color:#6c7974}.legal-page h1{margin:.1rem 0;font:700 2.15rem Georgia,serif}.legal-page nav{display:flex;gap:.55rem;overflow:auto;margin:1.3rem 0;padding-bottom:.25rem}.legal-page nav a{white-space:nowrap;border:1px solid #d8d4c8;border-radius:999px;padding:.65rem .95rem;color:#173f34;font-size:.78rem;font-weight:800}.legal-page nav a.router-link-active{background:#173f34;color:#e1f56c;border-color:#173f34}.legal-page article{background:#fffdf7;border-radius:1.65rem;padding:1.5rem;box-shadow:0 12px 34px rgba(23,63,52,.07)}.lead{font:1.25rem/1.45 Georgia,serif}.legal-page section{padding-top:1rem;border-top:1px solid #e4e0d6;margin-top:1rem}.legal-page h2{font-size:1rem}.legal-page section p{color:#5e6b66;line-height:1.65}.contact{display:inline-block;margin-top:1rem;border-radius:999px;padding:.85rem 1.1rem;background:#173f34;color:#e1f56c;font-weight:900}@media(min-width:720px){.legal-page{max-width:760px;margin:auto}}
</style>
