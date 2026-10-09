<template>
  <router-link :to="`/products/${product.slug}`" class="product-card">
    <div class="product-image"><img v-if="product.images?.length" :src="product.images[0].thumbnail_url || product.images[0].image_url" :alt="product.title_en || product.title" loading="lazy" /><span v-else aria-hidden="true">b.</span><em>{{ conditionLabel }}</em></div>
    <div class="product-info"><p>{{ product.brand || 'PRE-LOVED' }}</p><h3>{{ product.title_en || product.title }}</h3><div><strong>€{{ product.sale_price }}</strong><s v-if="product.original_price">€{{ product.original_price }}</s><span v-if="discountPercent">{{ discountPercent }}</span></div><small v-if="product.origin_country_code">{{ originFlag }} Ships from {{ product.origin_country_code }}</small></div>
  </router-link>
</template>
<script setup>
import { computed } from 'vue'
const props=defineProps({product:{type:Object,required:true}})
const originFlag=computed(()=>{const c=props.product.origin_country_code;if(!c||c.length!==2)return'';return String.fromCodePoint(...c.toUpperCase().split('').map(x=>127397+x.charCodeAt()))})
const conditionLabel=computed(()=>({new:'New',like_new:'Like new',good:'Good',fair:'Fair',poor:'Worn',for_parts:'Parts'}[props.product.condition_grade]||'Pre-loved'))
const discountPercent=computed(()=>props.product.original_price&&props.product.sale_price?`-${Math.round((1-props.product.sale_price/props.product.original_price)*100)}%`:'')
</script>
<style scoped>
.product-card{display:block;overflow:hidden;border-radius:1.15rem;background:#fffdf7;color:#173f34;box-shadow:0 8px 24px rgba(23,63,52,.06);transition:transform .18s ease,box-shadow .18s ease}.product-card:active{transform:scale(.985)}.product-card:focus-visible{outline:3px solid #173f34;outline-offset:3px}.product-image{position:relative;aspect-ratio:1/1;overflow:hidden;display:grid;place-items:center;background:#e7e3d8}.product-image img{width:100%;height:100%;object-fit:cover}.product-image>span{font:700 2.6rem Georgia,serif;color:#aeb9b3}.product-image em{position:absolute;left:.65rem;top:.65rem;border-radius:999px;padding:.28rem .5rem;background:rgba(255,253,247,.92);color:#173f34;font-size:.56rem;font-style:normal;font-weight:900;text-transform:uppercase;letter-spacing:.05em}.product-info{padding:.8rem}.product-info>p{margin:0 0 .25rem;color:#77827e;font-size:.58rem;font-weight:900;letter-spacing:.14em}.product-info h3{display:-webkit-box;min-height:2.25rem;margin:0;overflow:hidden;-webkit-line-clamp:2;-webkit-box-orient:vertical;font-size:.84rem;line-height:1.3}.product-info>div{display:flex;align-items:baseline;gap:.4rem;margin-top:.5rem}.product-info strong{font:700 1.08rem Georgia,serif}.product-info s{color:#8c9591;font-size:.64rem}.product-info>div span{margin-left:auto;border-radius:999px;padding:.2rem .35rem;background:#dff263;font-size:.56rem;font-weight:900}.product-info small{display:block;margin-top:.45rem;color:#6e7a75;font-size:.62rem}
</style>
