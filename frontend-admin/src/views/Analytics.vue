<template>
  <el-card><template #header><div class="head"><div><h2>转化分析</h2><p>仅统计同意 Analytics Cookie 的匿名访问，默认查看最近 30 天。</p></div><el-select v-model="days" @change="load"><el-option label="最近 7 天" :value="7"/><el-option label="最近 30 天" :value="30"/><el-option label="最近 90 天" :value="90"/></el-select></div></template>
    <div class="funnel" v-loading="loading"><article v-for="step in funnel" :key="step.key"><span>{{ step.label }}</span><strong>{{ step.value }}</strong><small>{{ step.rate }}</small></article></div>
    <el-alert title="口径说明" type="info" :closable="false" description="访问和商品浏览按匿名会话去重；加购、开始结账和购买为事件数。Cookie 未同意时不会发送事件。" />
    <h3>热门商品</h3><el-table :data="summary.top_products||[]" stripe><el-table-column prop="product_id" label="商品 ID"/><el-table-column prop="views" label="浏览次数"/></el-table>
  </el-card>
</template>
<script setup>
import {computed,onMounted,ref} from 'vue';import {ElMessage} from 'element-plus';import api from '../api';const days=ref(30),summary=ref({events:{},sessions:{},top_products:[]}),loading=ref(false)
const funnel=computed(()=>{const e=summary.value.events||{},s=summary.value.sessions||{},base=s.page_view||0;return[{key:'page_view',label:'访问会话',value:base,rate:'基准'},{key:'view_product',label:'商品浏览',value:s.view_product||e.view_product||0,rate:base?`${Math.round((s.view_product||0)/base*100)}%`:'—'},{key:'add_to_cart',label:'加购',value:e.add_to_cart||0,rate:base?`${Math.round((e.add_to_cart||0)/base*100)}%`:'—'},{key:'begin_checkout',label:'开始结账',value:e.begin_checkout||0,rate:base?`${Math.round((e.begin_checkout||0)/base*100)}%`:'—'},{key:'purchase',label:'购买成功',value:e.purchase||0,rate:base?`${Math.round((e.purchase||0)/base*100)}%`:'—'}]})
async function load(){loading.value=true;try{summary.value=(await api.get('/admin/analytics/summary',{params:{days:days.value}})).data}catch{ElMessage.error('加载分析数据失败')}finally{loading.value=false}}onMounted(load)
</script>
<style scoped>.head{display:flex;align-items:center;justify-content:space-between}.head h2{margin:0}.head p{margin:6px 0 0;color:#6b7280;font-size:13px}.funnel{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px}.funnel article{padding:18px;border-radius:12px;background:#f4f7f5}.funnel span,.funnel small{display:block;color:#66766d}.funnel strong{display:block;margin:7px 0;font-size:28px;color:#17483b}.funnel small{font-size:12px}h3{margin-top:24px}@media(max-width:1000px){.funnel{grid-template-columns:repeat(2,1fr)}}</style>
