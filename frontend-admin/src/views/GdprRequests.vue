<template>
  <div>
    <div class="page-header">
      <h2>GDPR 数据请求</h2>
      <el-select v-model="statusFilter" placeholder="全部状态" style="width: 140px" @change="fetchRequests" clearable>
        <el-option label="待处理" value="pending" />
        <el-option label="处理中" value="in_progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
    </div>

    <el-table :data="requests" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="request_type" label="请求类型" width="140">
        <template #default="{ row }">
          {{ typeLabel(row.request_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="details" label="详情" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="170" />
      <el-table-column prop="processed_at" label="处理时间" width="170" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)" :disabled="row.status === 'completed'">处理</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="处理 GDPR 请求" width="500px">
      <el-form :model="processForm" label-width="100px">
        <el-form-item label="请求类型">
          <el-input :value="typeLabel(currentRequest?.request_type)" disabled />
        </el-form-item>
        <el-form-item label="详情">
          <el-input :value="currentRequest?.details" type="textarea" :rows="2" disabled />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="processForm.status" style="width: 100%">
            <el-option label="处理中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="processForm.admin_notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleProcess">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGdprRequests, updateGdprRequest } from '../api'

const requests = ref([])
const loading = ref(false)
const statusFilter = ref('')
const dialogVisible = ref(false)
const currentRequest = ref(null)
const processForm = reactive({ status: 'in_progress', admin_notes: '' })

const typeLabel = (t) => ({ data_export: '数据导出', data_deletion: '数据删除', rectification: '数据更正' }[t] || t)
const statusLabel = (s) => ({ pending: '待处理', in_progress: '处理中', completed: '已完成', rejected: '已拒绝' }[s] || s)
const statusTag = (s) => ({ pending: 'info', in_progress: 'warning', completed: 'success', rejected: 'danger' }[s] || 'info')

const fetchRequests = async () => {
  loading.value = true
  try {
    const { data } = await getGdprRequests(statusFilter.value || undefined)
    requests.value = data
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showDialog = (row) => {
  currentRequest.value = row
  processForm.status = row.status
  processForm.admin_notes = row.admin_notes || ''
  dialogVisible.value = true
}

const handleProcess = async () => {
  try {
    await updateGdprRequest(currentRequest.value.id, processForm)
    ElMessage.success('处理成功')
    dialogVisible.value = false
    fetchRequests()
  } catch {
    ElMessage.error('处理失败')
  }
}

onMounted(fetchRequests)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
