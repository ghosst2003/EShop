<template>
  <div>
    <div class="page-header">
      <h2>Banner 管理</h2>
      <el-button type="primary" @click="showAddDialog">新增 Banner</el-button>
    </div>

    <el-table :data="banners" v-loading="loading" style="width: 100%">
      <el-table-column label="预览" width="260">
        <template #default="{ row }">
          <div
            class="banner-preview"
            :style="row.image_url
              ? { backgroundImage: `url(${row.image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' }
              : { background: `linear-gradient(135deg, ${row.bg_color_from}, ${row.bg_color_to})` }"
          >
            <span v-if="row.tag" class="preview-tag">{{ row.tag }}</span>
            <span class="preview-title">{{ row.title }}</span>
            <span v-if="row.subtitle" class="preview-subtitle">{{ row.subtitle }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="按钮" width="120">
        <template #default="{ row }">
          <span class="text-sm">{{ row.button_text }}</span>
          <span class="text-xs text-gray-400 block">{{ row.button_link }}</span>
        </template>
      </el-table-column>
      <el-table-column label="背景" width="100">
        <template #default="{ row }">
          <div v-if="row.image_url" class="text-xs text-green-600">图片</div>
          <div v-else class="text-xs text-gray-400">渐变色</div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-switch
            v-model="row._active"
            @change="toggleActive(row)"
            :loading="row._toggling"
            size="small"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="editBanner(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑 Banner' : '新增 Banner'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="背景图片">
          <div class="flex items-center gap-3">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleImageChange"
              :file-list="imageFileList"
              accept="image/*"
              :limit="1"
            >
              <el-button size="small">选择图片</el-button>
            </el-upload>
            <span v-if="form.image_url" class="text-xs text-green-600">已上传图片</span>
          </div>
          <div v-if="form.image_url" class="mt-2">
            <el-image :src="form.image_url" style="width: 100%; height: 100px; border-radius: 8px" fit="cover" />
          </div>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tag" placeholder="如 MEGA SALE" />
        </el-form-item>
        <el-form-item label="主标题" required>
          <el-input v-model="form.title" placeholder="如 Summer Clearance Sale" />
        </el-form-item>
        <el-form-item label="副标题">
          <el-input v-model="form.subtitle" placeholder="描述文字" />
        </el-form-item>
        <el-form-item label="按钮文字">
          <el-input v-model="form.button_text" />
        </el-form-item>
        <el-form-item label="按钮链接">
          <el-input v-model="form.button_link" placeholder="/browse" />
        </el-form-item>
        <el-form-item label="背景色">
          <div class="flex gap-4">
            <div>
              <span class="text-xs text-gray-400">起始</span>
              <el-color-picker v-model="form.bg_color_from" />
            </div>
            <div>
              <span class="text-xs text-gray-400">结束</span>
              <el-color-picker v-model="form.bg_color_to" />
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-1">上传图片后背景色作为备用</p>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBanners, createBanner, updateBanner, deleteBanner } from '../api'
import api from '../api'

const banners = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const imageFileList = ref([])

const defaultForm = {
  tag: '',
  title: '',
  subtitle: '',
  image_url: '',
  button_text: 'Shop Now',
  button_link: '/browse',
  bg_color_from: '#FF5000',
  bg_color_to: '#FF6B35',
  sort_order: 0,
}

const form = reactive({ ...defaultForm })

async function loadBanners() {
  loading.value = true
  try {
    const { data } = await getBanners()
    banners.value = data.map(b => ({ ...b, _active: b.is_active === 1, _toggling: false }))
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleImageChange(file) {
  imageFileList.value = [file]
}

function showAddDialog() {
  isEdit.value = false
  editId.value = null
  Object.assign(form, defaultForm)
  imageFileList.value = []
  dialogVisible.value = true
}

function editBanner(row) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    tag: row.tag || '',
    title: row.title,
    subtitle: row.subtitle || '',
    image_url: row.image_url || '',
    button_text: row.button_text,
    button_link: row.button_link,
    bg_color_from: row.bg_color_from,
    bg_color_to: row.bg_color_to,
    sort_order: row.sort_order,
  })
  imageFileList.value = row.image_url ? [{ name: '当前图片', url: row.image_url }] : []
  dialogVisible.value = true
}

async function toggleActive(row) {
  row._toggling = true
  try {
    await updateBanner(row.id, { is_active: row._active })
    row.is_active = row._active ? 1 : 0
    ElMessage.success(row._active ? '已启用' : '已禁用')
  } catch {
    row._active = !row._active
    ElMessage.error('操作失败')
  } finally {
    row._toggling = false
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除该 Banner？', '确认', { type: 'warning' })
    await deleteBanner(id)
    ElMessage.success('已删除')
    loadBanners()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleSave() {
  if (!form.title) {
    ElMessage.warning('请填写主标题')
    return
  }
  saving.value = true
  try {
    let bannerId
    if (isEdit.value) {
      await updateBanner(editId.value, { ...form })
      bannerId = editId.value
      ElMessage.success('保存成功')
    } else {
      const { data } = await createBanner({ ...form })
      bannerId = data.id
      ElMessage.success('创建成功')
    }

    // 上传 Banner 图片
    if (imageFileList.value.length && imageFileList.value[0].raw) {
      const formData = new FormData()
      formData.append('file', imageFileList.value[0].raw)
      await api.post(`/admin/banners/${bannerId}/image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }

    dialogVisible.value = false
    loadBanners()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(loadBanners)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.banner-preview {
  border-radius: 8px;
  padding: 12px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 80px;
  justify-content: center;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.preview-tag {
  font-size: 11px;
  font-weight: bold;
  opacity: 0.8;
}
.preview-title {
  font-size: 16px;
  font-weight: 800;
}
.preview-subtitle {
  font-size: 11px;
  opacity: 0.7;
}
</style>
