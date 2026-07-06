<template>
  <div class="payment-methods-page">
    <h2 class="page-title">支付方式管理</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>已配置的支付方式</span>
          <el-button type="primary" size="small" @click="showAddDialog">添加支付方式</el-button>
        </div>
      </template>

      <el-table :data="methods" stripe v-loading="loading">
        <el-table-column prop="code" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="name_en" label="英文名称" width="150" />
        <el-table-column label="预览" width="120">
          <template #default="{ row }">
            <span
              class="payment-preview"
              :style="{ color: row.text_color, backgroundColor: row.color }"
            >
              {{ row.name_en }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editRow(row)">编辑</el-button>
            <el-button
              v-if="row.is_active"
              link
              type="danger"
              size="small"
              @click="deactivateRow(row)"
            >停用</el-button>
            <el-button
              v-else
              link
              type="success"
              size="small"
              @click="reactivateRow(row)"
            >启用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="代码">
          <el-input v-model="form.code" :disabled="!!form.id" placeholder="如: paypal, gpay" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="英文名称">
          <el-input v-model="form.name_en" placeholder="英文显示名称" />
        </el-form-item>
        <el-form-item label="Logo URL">
          <el-input v-model="form.logo_url" placeholder="可选" />
        </el-form-item>
        <el-form-item label="背景色">
          <el-color-picker v-model="form.color" />
          <span class="help-text">{{ form.color }}</span>
        </el-form-item>
        <el-form-item label="文字颜色">
          <el-color-picker v-model="form.text_color" />
          <span class="help-text">{{ form.text_color }}</span>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :step="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMethod" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPaymentMethods,
  createPaymentMethod,
  updatePaymentMethod,
  deletePaymentMethod,
  reactivatePaymentMethod,
} from '../api'

const methods = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')

const form = ref({
  id: null,
  code: '',
  name: '',
  name_en: '',
  logo_url: '',
  color: '',
  text_color: '',
  sort_order: 0,
})

async function loadMethods() {
  loading.value = true
  try {
    const { data } = await getPaymentMethods()
    methods.value = data || []
  } catch {
    ElMessage.error('加载支付方式失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  dialogTitle.value = '添加支付方式'
  form.value = { id: null, code: '', name: '', name_en: '', logo_url: '', color: '', text_color: '', sort_order: 0 }
  dialogVisible.value = true
}

function editRow(row) {
  dialogTitle.value = '编辑支付方式'
  form.value = {
    id: row.id,
    code: row.code,
    name: row.name,
    name_en: row.name_en,
    logo_url: row.logo_url || '',
    color: row.color || '',
    text_color: row.text_color || '',
    sort_order: row.sort_order,
  }
  dialogVisible.value = true
}

async function saveMethod() {
  saving.value = true
  try {
    if (form.value.id) {
      await updatePaymentMethod(form.value.id, {
        name: form.value.name,
        name_en: form.value.name_en,
        logo_url: form.value.logo_url || null,
        color: form.value.color || null,
        text_color: form.value.text_color || null,
        sort_order: form.value.sort_order,
      })
    } else {
      await createPaymentMethod({
        code: form.value.code,
        name: form.value.name,
        name_en: form.value.name_en,
        logo_url: form.value.logo_url || null,
        color: form.value.color || null,
        text_color: form.value.text_color || null,
        sort_order: form.value.sort_order,
      })
    }
    dialogVisible.value = false
    ElMessage.success('已保存')
    loadMethods()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function deactivateRow(row) {
  await ElMessageBox.confirm(`确定停用 "${row.name}"？`, '确认')
  try {
    await deletePaymentMethod(row.id)
    ElMessage.success('已停用')
    loadMethods()
  } catch {
    ElMessage.error('操作失败')
  }
}

async function reactivateRow(row) {
  try {
    await reactivatePaymentMethod(row.id)
    ElMessage.success('已启用')
    loadMethods()
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(loadMethods)
</script>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.payment-preview {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid #eee;
}
.help-text {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}
</style>
