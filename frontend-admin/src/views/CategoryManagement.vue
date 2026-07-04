<template>
  <div>
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showDialog(null)">新增分类</el-button>
    </div>

    <el-table :data="categories" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="中文名称" width="150" />
      <el-table-column prop="name_en" label="英文名称" width="150" />
      <el-table-column prop="slug" label="Slug" width="150" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑分类' : '新增分类'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="中文名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="英文名称" required>
          <el-input v-model="form.name_en" />
        </el-form-item>
        <el-form-item label="Slug" required>
          <el-input v-model="form.slug" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="form.parent_id" placeholder="无" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api'

const categories = ref([])
const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ name: '', name_en: '', slug: '', parent_id: null, sort_order: 0 })

const fetchCategories = async () => {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch {
    ElMessage.error('加载分类失败')
  }
}

const showDialog = (row) => {
  editId.value = row?.id || null
  if (row) {
    Object.assign(form, {
      name: row.name,
      name_en: row.name_en,
      slug: row.slug,
      parent_id: row.parent_id,
      sort_order: row.sort_order,
    })
  } else {
    form.name = ''
    form.name_en = ''
    form.slug = ''
    form.parent_id = null
    form.sort_order = 0
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.name || !form.name_en || !form.slug) {
    ElMessage.warning('请填写必填字段')
    return
  }
  try {
    if (editId.value) {
      await updateCategory(editId.value, form)
    } else {
      await createCategory(form)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchCategories()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = async (id) => {
  try {
    await deleteCategory(id)
    ElMessage.success('已删除')
    fetchCategories()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchCategories)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
