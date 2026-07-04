<template>
  <div>
    <div class="page-header">
      <h2>国家管理</h2>
      <el-button type="primary" @click="showAddDialog">+ 添加国家</el-button>
    </div>

    <el-table :data="countries" border v-loading="loading">
      <el-table-column prop="code" label="代码" width="100" />
      <el-table-column label="国旗" width="80">
        <template #default="{ row }">
          <span class="text-lg">{{ row.flag_emoji || '️' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="中文名" />
      <el-table-column prop="name_en" label="英文名" />
      <el-table-column label="排序" width="80" align="center">
        <template #default="{ row }">
          {{ row.sort_order }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定停用此国家？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">停用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="代码" required>
          <el-input v-model="dialogForm.code" placeholder="如: CN" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="中文名" required>
          <el-input v-model="dialogForm.name" placeholder="如: 中国" />
        </el-form-item>
        <el-form-item label="英文名" required>
          <el-input v-model="dialogForm.name_en" placeholder="如: China" />
        </el-form-item>
        <el-form-item label="国旗 Emoji">
          <el-input v-model="dialogForm.flag_emoji" placeholder="如: 🇳" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dialogForm.sort_order" :min="0" :max="999" />
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
import { getCountries, createCountry, updateCountry, deleteCountry } from '../api'

const countries = ref([])
const loading = ref(false)
const saving = ref(false)

const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogForm = ref({
  code: '',
  name: '',
  name_en: '',
  flag_emoji: '',
  sort_order: 0,
})
const editingId = ref(null)
const dialogTitle = computed(() => isEdit.value ? '编辑国家' : '添加国家')

const fetchCountries = async () => {
  loading.value = true
  try {
    const { data } = await getCountries()
    countries.value = data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  dialogForm.value = { code: '', name: '', name_en: '', flag_emoji: '', sort_order: 0 }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogForm.value = {
    code: row.code,
    name: row.name,
    name_en: row.name_en,
    flag_emoji: row.flag_emoji || '',
    sort_order: row.sort_order || 0,
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!dialogForm.value.code || !dialogForm.value.name || !dialogForm.value.name_en) {
    ElMessage.warning('请填写必填字段')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateCountry(editingId.value, dialogForm.value)
      ElMessage.success('更新成功')
    } else {
      await createCountry(dialogForm.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchCountries()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteCountry(id)
    ElMessage.success('已停用')
    await fetchCountries()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(fetchCountries)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
