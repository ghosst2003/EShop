<template>
  <header class="site-header">
    <div class="utility"><div class="shell">Thoughtful second-hand finds across Europe <span>Secure payment · Buyer protection</span></div></div>
    <nav class="nav shell" aria-label="Main navigation">
      <router-link to="/" class="brand" aria-label="BeCool Market home"><span>b.</span><strong>BeCool</strong><small>PRE-LOVED MARKET</small></router-link>
      <div class="links"><router-link to="/">Home</router-link><router-link to="/browse">Browse</router-link><router-link v-if="isAuthenticated" to="/saved">Saved</router-link></div>
      <form class="search" role="search" @submit.prevent="submitSearch">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>
        <input v-model.trim="query" aria-label="Search products" placeholder="Search products, brands and categories" @input="suggest" @focus="openSuggestions=true" />
        <button type="submit">Search</button>
        <div v-if="openSuggestions && suggestions.length" class="suggestions"><button v-for="item in suggestions" :key="item" type="button" @mousedown.prevent="choose(item)">{{ item }}</button></div>
      </form>
      <div class="actions">
        <button class="country" type="button" @click="showCountries=!showCountries" :aria-expanded="showCountries">
          <svg viewBox="0 0 24 24"><path d="M12 22s7-5.1 7-12A7 7 0 1 0 5 10c0 6.9 7 12 7 12Z"/><circle cx="12" cy="10" r="2"/></svg><span>{{ countryName }}</span>
        </button>
        <div v-if="showCountries" class="country-menu"><button v-for="c in countries" :key="c.code" @click="pickCountry(c)">{{ c.flag_emoji }} {{ c.name_en }}</button></div>
        <router-link to="/cart" class="cart-link" aria-label="Shopping cart">
          <svg viewBox="0 0 24 24"><path d="M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 2-1.6L20.5 8H6.1"/><circle cx="10" cy="20" r="1"/><circle cx="18" cy="20" r="1"/></svg><span>Cart</span><b v-if="cartCount">{{ cartCount > 99 ? '99+' : cartCount }}</b>
        </router-link>
        <div v-if="isAuthenticated" class="account-wrap">
          <button type="button" class="account" @click="showUser=!showUser"><span>{{ initial }}</span><em>{{ user?.display_name || 'Account' }}</em></button>
          <div v-if="showUser" class="account-menu"><router-link to="/profile" @click="showUser=false">Account</router-link><router-link to="/my-orders" @click="showUser=false">Orders</router-link><router-link to="/saved" @click="showUser=false">Saved products</router-link><button @click="signOut">Sign out</button></div>
        </div>
        <router-link v-else to="/login" class="signin">Sign in</router-link>
      </div>
    </nav>
    <div class="mobile-search shell"><form @submit.prevent="submitSearch"><input v-model.trim="query" placeholder="Search products" aria-label="Search products"/><button>Search</button></form></div>
  </header>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getCountries, getSearchSuggestions } from '../api'
import { useAuth } from '../composables/useAuth'
import { useCart } from '../composables/useCart'
import { useLocation } from '../composables/useLocation'
const router=useRouter(),query=ref(''),suggestions=ref([]),openSuggestions=ref(false),showCountries=ref(false),showUser=ref(false),countries=ref([])
const {user,isAuthenticated,logout}=useAuth(),{count:cartCount}=useCart(),{countryCode,setLocation,initLocation}=useLocation()
const countryName=computed(()=>countries.value.find(c=>c.code===countryCode.value)?.name_en||countryCode.value||'Location')
const initial=computed(()=>(user.value?.display_name||user.value?.username||'A')[0].toUpperCase())
let suggestionTimer
function submitSearch(){if(!query.value)return;openSuggestions.value=false;router.push({path:'/browse',query:{q:query.value}})}
function choose(value){query.value=value;submitSearch()}
function suggest(){clearTimeout(suggestionTimer);if(query.value.length<2){suggestions.value=[];return}suggestionTimer=setTimeout(async()=>{try{const {data}=await getSearchSuggestions(query.value);suggestions.value=(data||[]).map(x=>typeof x==='string'?x:(x.title_en||x.title)).filter(Boolean).slice(0,6)}catch{}},180)}
function pickCountry(c){setLocation(c.code);showCountries.value=false}
function signOut(){showUser.value=false;logout()}
onMounted(async()=>{try{countries.value=(await getCountries()).data||[]}catch{}await initLocation()})
</script>

<style scoped>
.site-header{position:sticky;top:0;z-index:60;border-bottom:1px solid rgba(23,63,52,.12);background:rgba(248,246,239,.96);backdrop-filter:blur(16px)}.shell{width:min(100% - 40px,1360px);margin:auto}.utility{background:#173f34;color:#f8f5ec;font-size:11px}.utility .shell{display:flex;justify-content:space-between;padding:7px 0}.utility span{color:#cdd9d4}.nav{height:76px;display:grid;grid-template-columns:auto auto minmax(260px,1fr) auto;align-items:center;gap:28px}.brand{display:grid;grid-template-columns:42px auto;grid-template-rows:24px 14px;column-gap:10px;color:#173f34}.brand>span{grid-row:1/3;display:grid;width:42px;height:42px;place-items:center;border-radius:13px;background:#dff263;font:800 28px Georgia,serif}.brand strong{font:700 22px Georgia,serif}.brand small{font-size:8px;font-weight:900;letter-spacing:.15em;color:#7b8781}.links{display:flex;gap:20px}.links a{color:#52685f;font-size:13px;font-weight:800}.links a.router-link-active{color:#173f34;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:6px}.search{position:relative;height:45px;display:flex;align-items:center;border:1px solid #d8ddd5;border-radius:999px;background:white;overflow:visible}.search>svg{width:18px;margin-left:16px;fill:none;stroke:#6c7b74;stroke-width:2}.search input{min-width:0;flex:1;border:0;background:transparent;padding:0 10px;color:#173f34;outline:0}.search>button,.mobile-search button{height:37px;margin-right:4px;padding:0 17px;border:0;border-radius:999px;background:#173f34;color:white;font-size:11px;font-weight:850}.suggestions{position:absolute;top:51px;right:0;left:0;padding:8px;border:1px solid #d8ddd5;border-radius:16px;background:white;box-shadow:0 16px 35px rgba(23,63,52,.12)}.suggestions button{display:block;width:100%;border:0;border-radius:9px;background:transparent;padding:9px;text-align:left;color:#173f34}.suggestions button:hover{background:#f0f3e8}.actions{position:relative;display:flex;align-items:center;gap:12px}.country,.cart-link,.account,.signin{min-height:42px;display:flex;align-items:center;gap:7px;border:0;background:transparent;color:#173f34;font-size:12px;font-weight:800}.country svg,.cart-link svg{width:20px;fill:none;stroke:currentColor;stroke-width:1.8}.cart-link{position:relative}.cart-link b{display:grid;min-width:19px;height:19px;place-items:center;border-radius:999px;background:#dff263;font-size:9px}.signin{padding:0 17px;border:1px solid #173f34;border-radius:999px}.account>span{display:grid;width:36px;height:36px;place-items:center;border-radius:50%;background:#173f34;color:#dff263}.account em{max-width:85px;overflow:hidden;text-overflow:ellipsis;font-style:normal}.country-menu,.account-menu{position:absolute;right:0;top:50px;width:220px;max-height:320px;overflow:auto;padding:8px;border:1px solid #d8ddd5;border-radius:15px;background:white;box-shadow:0 16px 35px rgba(23,63,52,.14)}.country-menu button,.account-menu button,.account-menu a{display:block;width:100%;border:0;border-radius:9px;background:transparent;padding:10px;text-align:left;color:#173f34;font-size:12px}.country-menu button:hover,.account-menu button:hover,.account-menu a:hover{background:#f0f3e8}.account-menu{width:170px}.mobile-search{display:none;padding-bottom:10px}.mobile-search form{display:flex;border:1px solid #d8ddd5;border-radius:999px;background:white}.mobile-search input{min-width:0;flex:1;border:0;background:transparent;padding:0 16px;outline:0}@media(max-width:1050px){.nav{grid-template-columns:auto 1fr auto}.links{display:none}.search{grid-column:2}.country span,.account em{display:none}}@media(max-width:720px){.utility{display:none}.shell{width:min(100% - 24px,1360px)}.nav{height:62px;grid-template-columns:auto 1fr auto;gap:10px}.brand{grid-template-columns:36px auto;grid-template-rows:20px 10px}.brand>span{width:36px;height:36px;font-size:24px}.brand strong{font-size:18px}.search,.country{display:none}.actions{justify-self:end}.cart-link>span{display:none}.signin{padding:0 12px}.mobile-search{display:block}.mobile-search form{height:42px}.account-wrap{position:relative}}
</style>
