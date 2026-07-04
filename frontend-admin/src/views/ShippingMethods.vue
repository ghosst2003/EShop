<template>
  <div>
    <div class="page-header">
      <h2>派送方式管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        新增派送方式
      </el-button>
    </div>

    <el-table :data="methods" border v-loading="loading">
      <el-table-column prop="code" label="代码" width="180" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="国家" width="200">
        <template #default="{ row }">
          {{ row.countries?.length || 0 }} 个国家
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editMethod(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteMethod(row)">
            {{ row.is_active ? '停用' : '删除' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="isEdit ? '编辑派送方式' : '新增派送方式'"
      width="80%"
      @close="resetForm"
    >
      <el-form :model="currentMethod" label-width="100px">
        <div class="fixed-width-row">
          <el-form-item label="代码" v-if="!isEdit">
            <el-input v-model="currentMethod.code" placeholder="如: DHL_STANDARD" />
          </el-form-item>
          <el-form-item label="中文名">
            <el-input v-model="currentMethod.name" placeholder="如: DHL 标准" />
          </el-form-item>
          <el-form-item label="英文名">
            <el-input v-model="currentMethod.name_en" placeholder="如: DHL Standard" />
          </el-form-item>
        </div>
        <el-form-item label="描述">
          <el-input v-model="currentMethod.description" type="textarea" :rows="2" />
        </el-form-item>

        <h3 class="mt-6 mb-3 font-semibold">国家定价</h3>
        <el-table :data="currentMethod.countries" border size="small" style="width: 100%">
          <el-table-column label="国家" width="220">
            <template #default="{ row }">
              <el-select v-model="row.country_code" filterable placeholder="选择国家" style="width: 100%">
                <el-option
                  v-for="c in allCountries"
                  :key="c.code"
                  :label="`${c.flag_emoji || ''} ${c.name_en || c.name} (${c.code})`"
                  :value="c.code"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="基础运费 (€)" width="140">
            <template #default="{ row }">
              <el-input-number v-model="row.base_fee" :min="0" :precision="2" :step="0.5" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="每kg附加费 (€)" width="160">
            <template #default="{ row }">
              <el-input-number v-model="row.per_kg_fee" :min="0" :precision="2" :step="0.5" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="最小重量 (kg)" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.min_weight_kg" :min="0" :precision="1" :step="0.5" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="预计天数" width="150">
            <template #default="{ row }">
              <div class="flex items-center gap-1">
                <el-input-number v-model="row.estimated_days_min" :min="1" :max="99" size="small" style="width: 60px" />
                <span>-</span>
                <el-input-number v-model="row.estimated_days_max" :min="1" :max="99" size="small" style="width: 60px" />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="默认" width="60">
            <template #default="{ row }">
              <el-switch v-model="row.is_default" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ $index }">
              <el-button size="small" type="danger" @click="currentMethod.countries.splice($index, 1)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button size="small" class="mt-3" @click="addCountry">+ 添加国家</el-button>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveMethod">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getShippingMethods,
  createShippingMethod,
  updateShippingMethod,
  deleteShippingMethod,
  getCountries,
} from '../api'

const methods = ref([])
const allCountries = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const currentMethod = reactive({
  code: '',
  name: '',
  name_en: '',
  description: '',
  countries: [],
})
const editingId = ref(null)

const isEdit = computed(() => editingId.value !== null)

onMounted(async () => {
  await loadData()
  try {
    const { data } = await getCountries()
    allCountries.value = data
  } catch {}
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getShippingMethods()
    methods.value = data
  } catch (e) {
    console.error('Failed to load shipping methods:', e)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(currentMethod, {
    code: '',
    name: '',
    name_en: '',
    description: '',
    countries: [],
  })
}

function editMethod(row) {
  editingId.value = row.id
  Object.assign(currentMethod, {
    code: row.code,
    name: row.name,
    name_en: row.name_en,
    description: row.description || '',
    countries: (row.countries || []).map(c => ({
      country_code: c.country_code,
      base_fee: Number(c.base_fee),
      per_kg_fee: Number(c.per_kg_fee || 0),
      min_weight_kg: Number(c.min_weight_kg || 0.5),
      estimated_days_min: c.estimated_days_min,
      estimated_days_max: c.estimated_days_max,
      is_default: Boolean(c.is_default),
    })),
  })
  showEditDialog.value = true
}

function addCountry() {
  currentMethod.countries.push({
    country_code: '',
    base_fee: 0,
    per_kg_fee: 0,
    min_weight_kg: 0.5,
    estimated_days_min: 3,
    estimated_days_max: 7,
    is_default: false,
  })
}

async function saveMethod() {
  if (!currentMethod.name || !currentMethod.name_en) {
    ElMessage.warning('请填写名称')
    return
  }
  if (!isEdit.value && !currentMethod.code) {
    ElMessage.warning('请填写代码')
    return
  }

  saving.value = true
  try {
    const payload = {
      name: currentMethod.name,
      name_en: currentMethod.name_en,
      description: currentMethod.description,
      countries: currentMethod.countries.filter(c => c.country_code).map(c => ({
        country_code: c.country_code,
        base_fee: c.base_fee,
        per_kg_fee: c.per_kg_fee || 0,
        min_weight_kg: c.min_weight_kg || 0.5,
        estimated_days_min: c.estimated_days_min,
        estimated_days_max: c.estimated_days_max,
        is_default: c.is_default,
      })),
    }

    if (isEdit.value) {
      payload.code = currentMethod.code
      await updateShippingMethod(editingId.value, payload)
    } else {
      payload.code = currentMethod.code
      await createShippingMethod(payload)
    }

    ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
    showEditDialog.value = false
    showCreateDialog.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

async function deleteMethod(row) {
  try {
    await ElMessageBox.confirm(
      row.is_active ? `确定停用派送方式 "${row.name}" 吗？` : `确定删除派送方式 "${row.name}" 吗？`,
      '确认',
      { type: 'warning' }
    )
    await deleteShippingMethod(row.id)
    ElMessage.success('操作成功')
    await loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.fixed-width-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 20px;
}
.fixed-width-row :deep(.el-form-item) {
  margin-bottom: 0;
}
</style>
