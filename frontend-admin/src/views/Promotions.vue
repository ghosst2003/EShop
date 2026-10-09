<template>
  <el-card>
    <template #header><div class="head"><div><h2>优惠码</h2><p>统一配置折扣、门槛、次数和有效期，结算价格由服务器计算。</p></div><el-button type="primary" @click="openCreate">新建优惠码</el-button></div></template>
    <el-table :data="rows" v-loading="loading" stripe>
      <el-table-column prop="code" label="优惠码" width="140"><template #default="{row}"><strong>{{ row.code }}</strong></template></el-table-column>
      <el-table-column prop="label" label="名称" min-width="150" />
      <el-table-column label="优惠" width="120"><template #default="{row}">{{ row.discount_type==='percent' ? `${row.discount_value}%` : `€${row.discount_value}` }}</template></el-table-column>
      <el-table-column label="最低消费" width="110"><template #default="{row}">€{{ row.minimum_subtotal }}</template></el-table-column>
      <el-table-column label="使用次数" width="110"><template #default="{row}">{{ row.uses }} / {{ row.usage_limit || '不限' }}</template></el-table-column>
      <el-table-column label="状态" width="100"><template #default="{row}"><el-switch :model-value="row.is_active" @change="value=>toggle(row,value)" /></template></el-table-column>
      <el-table-column label="操作" width="90"><template #default="{row}"><el-button link type="primary" @click="openEdit(row)">编辑</el-button></template></el-table-column>
    </el-table>
  </el-card>
  <el-dialog v-model="visible" :title="editingId ? '编辑优惠码' : '新建优惠码'" width="560px">
    <el-form :model="form" label-width="110px">
      <el-form-item label="优惠码" required><el-input v-model="form.code" placeholder="WELCOME10" /></el-form-item>
      <el-form-item label="显示名称" required><el-input v-model="form.label" placeholder="Welcome offer" /></el-form-item>
      <el-form-item label="优惠类型"><el-radio-group v-model="form.discount_type"><el-radio value="percent">百分比</el-radio><el-radio value="fixed">固定金额</el-radio></el-radio-group></el-form-item>
      <el-form-item label="优惠值" required><el-input-number v-model="form.discount_value" :min="0.01" :max="form.discount_type==='percent'?100:99999" :precision="2" /></el-form-item>
      <el-form-item label="最低消费"><el-input-number v-model="form.minimum_subtotal" :min="0" :precision="2" /></el-form-item>
      <el-form-item label="最高优惠"><el-input-number v-model="form.maximum_discount" :min="0.01" :precision="2" placeholder="不限" /></el-form-item>
      <el-form-item label="总使用上限"><el-input-number v-model="form.usage_limit" :min="1" placeholder="不限" /></el-form-item>
      <el-form-item label="每人上限"><el-input-number v-model="form.per_customer_limit" :min="1" /></el-form-item>
      <el-form-item label="有效期"><el-date-picker v-model="dateRange" type="datetimerange" start-placeholder="开始" end-placeholder="结束" /></el-form-item>
      <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
  </el-dialog>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue'; import { ElMessage } from 'element-plus'; import { createPromotion, getPromotions, setPromotionActive, updatePromotion } from '../api'
const rows=ref([]),loading=ref(false),visible=ref(false),saving=ref(false),editingId=ref(null),dateRange=ref([])
const defaults=()=>({code:'',label:'',discount_type:'percent',discount_value:10,minimum_subtotal:0,maximum_discount:null,usage_limit:null,per_customer_limit:1,is_active:true});const form=reactive(defaults())
async function load(){loading.value=true;try{rows.value=(await getPromotions()).data.items||[]}catch{ElMessage.error('加载优惠码失败')}finally{loading.value=false}}
function openCreate(){editingId.value=null;Object.assign(form,defaults());dateRange.value=[];visible.value=true}
function openEdit(row){editingId.value=row.id;Object.assign(form,{...defaults(),...row});dateRange.value=row.starts_at&&row.ends_at?[new Date(row.starts_at),new Date(row.ends_at)]:[];visible.value=true}
async function save(){if(!form.code.trim()||!form.label.trim())return ElMessage.warning('请填写优惠码和名称');saving.value=true;try{const payload={...form,starts_at:dateRange.value?.[0]?.toISOString?.()||null,ends_at:dateRange.value?.[1]?.toISOString?.()||null};editingId.value?await updatePromotion(editingId.value,payload):await createPromotion(payload);visible.value=false;ElMessage.success('优惠码已保存');await load()}catch(e){ElMessage.error(e.response?.data?.detail||'保存失败')}finally{saving.value=false}}
async function toggle(row,value){try{await setPromotionActive(row.id,value);row.is_active=value}catch{ElMessage.error('更新失败')}}
onMounted(load)
</script>
<style scoped>.head{display:flex;align-items:center;justify-content:space-between;gap:20px}.head h2{margin:0}.head p{margin:6px 0 0;color:#6b7280;font-size:13px}</style>
