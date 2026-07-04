<template>
  <div>
    <div class="page-header">
      <h2>发货地管理</h2>
      <div>
        <el-button @click="fetchRules">刷新</el-button>
        <el-button type="primary" @click="showAddDialog">+ 添加规则</el-button>
      </div>
    </div>

    <el-alert
      title="统一管理发货地→目的地→运费规则，商品编辑页可引用此配置或进行自定义覆盖"
      type="info"
      :closable="false"
      style="margin-bottom: 16px"
    />

    <!-- 筛选 -->
    <div class="filter-bar mb-3">
      <el-select v-model="filterDest" placeholder="筛选目的地" clearable filterable style="width: 200px">
        <el-option v-for="c in countries" :key="c.code" :label="`${c.flag_emoji || ''} ${c.name_en || c.name}`" :value="c.code" />
      </el-select>
    </div>

    <el-table :data="filteredRules" stripe style="width: 100%" v-loading="loading">
      <el-table-column label="发货地" width="180">
        <template #default="{ row }">
          <span class="text-lg mr-1">{{ row.origin_flag_emoji || '🏳️' }}</span>
          <span>{{ row.origin_country_name || row.origin_country_code }}</span>
        </template>
      </el-table-column>
      <el-table-column label="目的地" width="180">
        <template #default="{ row }">
          <span class="text-lg mr-1">{{ row.destination_flag_emoji || '🏳️' }}</span>
          <span>{{ row.destination_country_name || row.destination_country_code }}</span>
        </template>
      </el-table-column>
      <el-table-column label="运费 (€)" width="120" align="right">
        <template #default="{ row }">
          <span class="font-bold text-primary">€{{ Number(row.fee).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除此规则？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-alert
      v-if="rules.length === 0 && !loading"
      title="暂无发货地规则，点击「添加规则」开始配置"
      type="warning"
      :closable="false"
      style="margin-top: 16px"
    />

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="发货地" required>
          <el-select v-model="dialogForm.origin_country_code" placeholder="选择发货国家" filterable style="width: 100%" :disabled="isEdit">
            <el-option v-for="c in countries" :key="c.code" :label="`${c.flag_emoji || ''} ${c.name_en || c.name} (${c.code})`" :value="c.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="目的地" required>
          <el-select v-model="dialogForm.destination_country_code" placeholder="选择目的国家" filterable style="width: 100%" :disabled="isEdit">
            <el-option v-for="c in countries" :key="c.code" :label="`${c.flag_emoji || ''} ${c.name_en || c.name} (${c.code})`" :value="c.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="运费 (€)" required>
          <el-input-number v-model="dialogForm.fee" :min="0" :precision="2" :step="1" style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="dialogForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getShippingOrigins, createShippingOriginRule, updateShippingOriginRule, deleteShippingOriginRule, getCountries, getShippingMethods } from '../api'

const rules = ref([])
const countries = ref([])
const shippingMethods = ref([])
const loading = ref(false)
const saving = ref(false)

const filterDest = ref('')

const filteredRules = computed(() => {
  let result = rules.value
  if (filterDest.value) result = result.filter(r => r.destination_country_code === filterDest.value)
  return result
})

const fetchRules = async () => {
  loading.value = true
  try {
    const { data } = await getShippingOrigins()
    rules.value = data
  } catch (e) {
    ElMessage.error('加载规则失败')
  } finally {
    loading.value = false
  }
}

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogForm = ref({
  origin_country_code: '',
  destination_country_code: '',
  shipping_method_id: null,
  fee: 0,
  is_active: true,
})
const editingId = ref(null)
const dialogTitle = computed(() => isEdit.value ? '编辑规则' : '添加规则')

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  // 自动选择第一个派送方式
  const defaultMethod = shippingMethods.value.length > 0 ? shippingMethods.value[0].id : null
  dialogForm.value = {
    origin_country_code: '',
    destination_country_code: '',
    shipping_method_id: defaultMethod,
    fee: 0,
    is_active: true,
  }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogForm.value = {
    origin_country_code: row.origin_country_code,
    destination_country_code: row.destination_country_code,
    shipping_method_id: row.shipping_method_id,
    fee: Number(row.fee),
    is_active: !!row.is_active,
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!dialogForm.value.origin_country_code || !dialogForm.value.destination_country_code) {
    ElMessage.warning('请填写必填字段')
    return
  }
  // 如果派送方式还没选中（数据未加载完），自动取第一个
  if (!dialogForm.value.shipping_method_id && shippingMethods.value.length > 0) {
    dialogForm.value.shipping_method_id = shippingMethods.value[0].id
  }
  if (!dialogForm.value.shipping_method_id) {
    ElMessage.warning('暂无可用派送方式')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateShippingOriginRule(editingId.value, {
        fee: dialogForm.value.fee,
        is_active: dialogForm.value.is_active,
      })
      ElMessage.success('更新成功')
    } else {
      await createShippingOriginRule(dialogForm.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchRules()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteShippingOriginRule(id)
    ElMessage.success('已删除')
    await fetchRules()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  try {
    const { data: ctrys } = await getCountries()
    countries.value = ctrys
    const { data: methods } = await getShippingMethods()
    shippingMethods.value = methods.filter(m => m.is_active)
  } catch {}
  await fetchRules()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-bar {
  display: flex;
  align-items: center;
}
.text-primary {
  color: #409eff;
}
</style>
