<template>
  <main class="saved-page safe-top">
    <header class="page-header">
      <button type="button" class="back-button" aria-label="Go back" @click="$router.back()">←</button>
      <div><span class="eyebrow">YOUR EDIT</span><h1>Saved pieces</h1></div>
    </header>

    <div v-if="loading" class="state-card" role="status">Loading your saved pieces…</div>
    <div v-else-if="error" class="state-card error" role="alert">
      <p>{{ error }}</p><button type="button" @click="load">Try again</button>
    </div>
    <div v-else-if="!products.length" class="state-card empty">
      <span class="empty-mark">♡</span><h2>Your shortlist is empty</h2>
      <p>Save pieces you love and come back to them here.</p>
      <router-link to="/browse">Discover products</router-link>
    </div>
    <section v-else class="saved-grid" aria-label="Saved products">
      <article v-for="product in products" :key="product.id" class="saved-item">
        <router-link :to="`/products/${product.slug}`" class="product-link">
          <div class="image-wrap"><img v-if="product.images?.[0]" :src="product.images[0].thumbnail_url || product.images[0].image_url" :alt="product.title_en || product.title" /></div>
          <div class="product-copy"><p>{{ product.brand || 'PRE-LOVED' }}</p><h2>{{ product.title_en || product.title }}</h2><strong>€{{ product.sale_price }}</strong></div>
        </router-link>
        <button type="button" class="remove-button" :disabled="removing === product.id" @click="remove(product)">{{ removing === product.id ? 'Removing…' : 'Remove' }}</button>
      </article>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getSavedProducts, unsaveProduct } from '../api'

const products = ref([])
const loading = ref(true)
const error = ref('')
const removing = ref(null)

async function load() {
  loading.value = true; error.value = ''
  try { products.value = ((await getSavedProducts()).data || []).map(item => item.product) }
  catch (e) { error.value = e.response?.data?.detail || 'We could not load your saved pieces.' }
  finally { loading.value = false }
}
async function remove(product) {
  removing.value = product.id
  try { await unsaveProduct(product.id); products.value = products.value.filter(item => item.id !== product.id) }
  catch (e) { error.value = e.response?.data?.detail || 'Could not remove this product.' }
  finally { removing.value = null }
}
onMounted(load)
</script>

<style scoped>
.saved-page{min-height:100vh;background:#f4f1e8;color:#173f34;padding-bottom:7rem}.page-header{display:flex;align-items:center;gap:1rem;padding:1.25rem 1.25rem 1rem}.page-header h1{margin:.1rem 0 0;font-family:Georgia,serif;font-size:2rem}.eyebrow{font-size:.7rem;font-weight:900;letter-spacing:.19em;color:#66756f}.back-button{width:2.75rem;height:2.75rem;border:1px solid #d8d4c8;border-radius:50%;background:#fffdf7;color:#173f34;font-size:1.25rem}.state-card{margin:1rem 1.25rem;padding:2rem;border-radius:1.6rem;background:#fffdf7;text-align:center}.state-card.error{color:#9e2f2f}.state-card button,.state-card a{display:inline-block;margin-top:1rem;border:0;border-radius:999px;padding:.8rem 1.2rem;background:#173f34;color:#e1f56c;font-weight:800}.empty-mark{display:block;font-size:3rem}.empty h2{font-family:Georgia,serif}.empty p{color:#66756f}.saved-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem;padding:1rem 1.25rem}.saved-item{overflow:hidden;border-radius:1.35rem;background:#fffdf7;box-shadow:0 10px 28px rgba(23,63,52,.07)}.product-link{display:block;color:inherit}.image-wrap{aspect-ratio:1/1;background:#e9e6dc}.image-wrap img{width:100%;height:100%;object-fit:cover}.product-copy{padding:.85rem}.product-copy p{margin:0 0 .25rem;font-size:.62rem;font-weight:900;letter-spacing:.13em;color:#77817e}.product-copy h2{min-height:2.5rem;margin:0;font-size:.9rem;line-height:1.25}.product-copy strong{display:block;margin-top:.55rem;font-family:Georgia,serif;font-size:1.15rem}.remove-button{width:calc(100% - 1.7rem);margin:0 .85rem .85rem;border:1px solid #d9d5ca;border-radius:999px;background:transparent;padding:.55rem;color:#173f34;font-weight:800;font-size:.75rem}.remove-button:disabled{opacity:.55}@media(min-width:720px){.saved-page{max-width:900px;margin:auto}.saved-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
</style>
