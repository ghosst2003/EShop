<template>
  <div class="returns-page">
    <div class="page-heading">
      <div><h2>退货与退款</h2><p>审核退货、确认收货并原路退回 Stripe 款项。</p></div>
      <el-select v-model="status" clearable placeholder="全部状态" style="width: 160px" @change="load">
        <el-option v-for="item in statuses" :key="item" :label="statusLabel(item)" :value="item" />
      </el-select>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-table v-loading="loading" :data="rows" stripe style="width:100%">
      <el-table-column prop="order_number" label="订单" width="170" />
      <el-table-column label="买家" min-width="180">
        <template #default="{ row }"><strong>{{ row.buyer_name }}</strong><br><small>{{ row.buyer_email || '—' }}</small></template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" min-width="150" />
      <el-table-column prop="details" label="说明" min-width="220" show-overflow-tooltip />
      <el-table-column label="金额" width="110"><template #default="{ row }">€{{ Number(row.order_total).toFixed(2) }}</template></el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }"><el-tag :type="tagType(row.status)">{{ statusLabel(row.status) }}</el-tag></template>
      </el-table-column>
      <el-table-column label="申请时间" width="175"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 'requested'">
            <el-button size="small" type="success" @click="changeStatus(row, 'approved')">批准</el-button>
            <el-button size="small" type="danger" plain @click="changeStatus(row, 'rejected')">拒绝</el-button>
          </template>
          <el-button v-if="row.status === 'approved'" size="small" @click="changeStatus(row, 'received')">确认收货</el-button>
          <el-button v-if="['approved','received'].includes(row.status)" size="small" type="primary" :loading="workingId === row.id" @click="refund(row)">全额退款</el-button>
          <span v-if="['rejected','refunded'].includes(row.status)">已处理</span>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && !rows.length" description="暂无退货申请" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReturnRequests, refundReturnRequest, updateReturnRequestStatus } from '../api'

const rows = ref([])
const loading = ref(false)
const workingId = ref(null)
const status = ref('')
const error = ref('')
const statuses = ['requested', 'approved', 'received', 'rejected', 'refunded']
const labels = { requested: '待审核', approved: '已批准', received: '已收货', rejected: '已拒绝', refunded: '已退款' }
const statusLabel = value => labels[value] || value
const tagType = value => ({ requested: 'warning', approved: 'success', received: 'info', rejected: 'danger', refunded: 'success' }[value] || '')
const formatDate = value => value ? new Date(value).toLocaleString('zh-CN') : '—'

const load = async () => {
  loading.value = true
  error.value = ''
  try { rows.value = (await getReturnRequests({ status: status.value || undefined })).data || [] }
  catch (requestError) { error.value = requestError.response?.data?.detail || '无法加载退货申请' }
  finally { loading.value = false }
}

const changeStatus = async (row, nextStatus) => {
  const { value } = await ElMessageBox.prompt('可填写内部处理备注', `${statusLabel(nextStatus)}退货`, {
    confirmButtonText: '确认', cancelButtonText: '取消', inputPlaceholder: '选填',
  })
  await updateReturnRequestStatus(row.id, { status: nextStatus, note: value || undefined })
  ElMessage.success('退货状态已更新')
  await load()
}

const refund = async row => {
  await ElMessageBox.confirm(`将通过 Stripe 向订单 ${row.order_number} 全额退款 €${Number(row.order_total).toFixed(2)}，并恢复库存。`, '确认退款', {
    type: 'warning', confirmButtonText: '确认退款', cancelButtonText: '取消',
  })
  workingId.value = row.id
  try {
    await refundReturnRequest(row.id)
    ElMessage.success('退款已提交，库存已恢复')
    await load()
  } catch (requestError) {
    ElMessage.error(requestError.response?.data?.detail || '退款失败')
  } finally { workingId.value = null }
}

onMounted(load)
</script>

<style scoped>
.returns-page{display:grid;gap:18px}.page-heading{display:flex;align-items:end;justify-content:space-between;gap:20px}.page-heading h2{margin:0;color:#173f35}.page-heading p{margin:6px 0 0;color:#718078;font-size:13px}small{color:#7a8780}.el-table strong{color:#294b3f}
</style>
