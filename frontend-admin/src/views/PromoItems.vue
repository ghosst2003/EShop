<template>
  <div>
    <div class="page-header">
      <h2>Promo Items</h2>
      <el-button type="primary" @click="showAddDialog">Add Promo Item</el-button>
    </div>

    <el-table :data="promoItems" v-loading="loading" style="width: 100%">
      <el-table-column label="Preview" width="120">
        <template #default="{ row }">
          <div class="promo-preview">
            <span v-if="row.icon" class="promo-icon">{{ row.icon }}</span>
            <img v-else-if="row.image_url" :src="row.image_url" class="promo-img" />
            <span v-else class="promo-icon"></span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Title" prop="title" width="120" />
      <el-table-column label="Tag" width="100">
        <template #default="{ row }">
          <span v-if="row.tag" :class="row.tag_class" class="text-xs px-2 py-0.5 rounded-full">{{ row.tag }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Link" prop="link_url" show-overflow-tooltip />
      <el-table-column label="Sort" prop="sort_order" width="60" />
      <el-table-column label="Active" width="80">
        <template #default="{ row }">
          <el-switch
            v-model="row._active"
            @change="toggleActive(row)"
            :loading="row._toggling"
            size="small"
          />
        </template>
      </el-table-column>
      <el-table-column label="Actions" fixed="right" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="editItem(row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Promo Item' : 'Add Promo Item'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="Icon">
          <el-input v-model="form.icon" placeholder="Emoji icon, e.g. 🔥" maxlength="10" />
        </el-form-item>
        <el-form-item label="Image">
          <div class="flex items-center gap-3">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleImageChange"
              :file-list="imageFileList"
              accept="image/*"
              :limit="1"
            >
              <el-button size="small">Upload Image</el-button>
            </el-upload>
            <span v-if="form.image_url" class="text-xs text-green-600">Uploaded</span>
          </div>
          <div v-if="form.image_url" class="mt-2">
            <el-image :src="form.image_url" style="width: 80px; height: 80px; border-radius: 8px" fit="cover" />
          </div>
        </el-form-item>
        <el-form-item label="Title" required>
          <el-input v-model="form.title" placeholder="e.g. Flash Sale" />
        </el-form-item>
        <el-form-item label="Tag">
          <el-input v-model="form.tag" placeholder="e.g. Limited" />
        </el-form-item>
        <el-form-item label="Tag Style">
          <el-select v-model="form.tag_class" placeholder="Select style">
            <el-option label="Blue" value="bg-blue-100 text-blue-600" />
            <el-option label="Green" value="bg-green-100 text-green-600" />
            <el-option label="Orange" value="bg-orange-100 text-orange-600" />
            <el-option label="Red" value="bg-red-500 text-white" />
            <el-option label="Yellow" value="bg-yellow-400 text-yellow-800" />
            <el-option label="Purple" value="bg-purple-100 text-purple-600" />
          </el-select>
        </el-form-item>
        <el-form-item label="Link Type">
          <el-radio-group v-model="linkType">
            <el-radio-button value="url">Custom URL</el-radio-button>
            <el-radio-button value="product">Product</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="linkType === 'url'" label="URL">
          <el-input v-model="form.link_url" placeholder="/browse?flash=1" />
        </el-form-item>
        <el-form-item v-if="linkType === 'product'" label="Product">
          <el-select v-model="form.product_id" placeholder="Select a product" filterable remote
            :remote-method="searchProducts" :loading="searching" style="width: 100%">
            <el-option
              v-for="p in productOptions"
              :key="p.id"
              :label="p.title_en || p.title"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Sort">
          <el-input-number v-model="form.sort_order" :min="0" :max="99" />
        </el-form-item>
        <el-form-item label="Active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveItem" :loading="saving">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const promoItems = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const imageFileList = ref([])

const form = ref({
  id: null,
  title: '',
  icon: '',
  image_url: '',
  tag: '',
  tag_class: 'bg-blue-100 text-blue-600',
  link_url: '',
  product_id: null,
  sort_order: 0,
  is_active: true,
})

const linkType = ref('url')
const productOptions = ref([])
const searching = ref(false)

const fetchItems = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/promo-items')
    promoItems.value = res.data.map(item => ({
      ...item,
      _active: item.is_active === 1,
      _toggling: false,
    }))
  } catch (e) {
    ElMessage.error('Failed to load promo items')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  linkType.value = 'url'
  form.value = { id: null, title: '', icon: '', image_url: '', tag: '', tag_class: 'bg-blue-100 text-blue-600', link_url: '', product_id: null, sort_order: 0, is_active: true }
  imageFileList.value = []
  productOptions.value = []
  dialogVisible.value = true
}

const editItem = (row) => {
  isEdit.value = true
  linkType.value = row.product_id ? 'product' : 'url'
  form.value = {
    id: row.id,
    title: row.title,
    icon: row.icon || '',
    image_url: row.image_url || '',
    tag: row.tag || '',
    tag_class: row.tag_class || 'bg-blue-100 text-blue-600',
    link_url: row.link_url || '',
    product_id: row.product_id || null,
    sort_order: row.sort_order,
    is_active: row.is_active === 1,
  }
  imageFileList.value = []
  // Load product options if editing a product link
  if (row.product_id) {
    searchProducts('')
  }
  dialogVisible.value = true
}

const handleImageChange = async (file) => {
  const formData = new FormData()
  formData.append('file', file.raw)
  try {
    const res = await api.post('/admin/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.value.image_url = res.data.url
    ElMessage.success('Image uploaded')
  } catch (e) {
    ElMessage.error('Upload failed')
  }
}

const searchProducts = async (query) => {
  searching.value = true
  try {
    const res = await api.get('/products', { params: { q: query, page: 1, page_size: 20 } })
    productOptions.value = res.data.items || []
  } catch (e) {
    productOptions.value = []
  } finally {
    searching.value = false
  }
}

const saveItem = async () => {
  if (!form.value.title) {
    ElMessage.warning('Title is required')
    return
  }
  // Clear link_url if product is selected, clear product_id if URL is set
  if (linkType.value === 'product') {
    form.value.link_url = ''
  } else {
    form.value.product_id = null
  }
  saving.value = true
  try {
    const payload = { ...form.value }
    delete payload.id
    if (isEdit.value) {
      await api.put(`/admin/promo-items/${form.value.id}`, payload)
      ElMessage.success('Updated')
    } else {
      await api.post('/admin/promo-items', payload)
      ElMessage.success('Created')
    }
    dialogVisible.value = false
    fetchItems()
  } catch (e) {
    ElMessage.error('Save failed')
  } finally {
    saving.value = false
  }
}

const toggleActive = async (row) => {
  row._toggling = true
  try {
    await api.put(`/admin/promo-items/${row.id}`, { is_active: row._active })
    ElMessage.success('Updated')
  } catch (e) {
    row._active = !row._active
    ElMessage.error('Failed')
  } finally {
    row._toggling = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('Delete this promo item?', 'Confirm', { type: 'warning' })
    await api.delete(`/admin/promo-items/${id}`)
    ElMessage.success('Deleted')
    fetchItems()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('Delete failed')
  }
}

onMounted(fetchItems)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.promo-preview {
  width: 60px;
  height: 60px;
  background: #f0ede8;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.promo-icon {
  font-size: 28px;
}
.promo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
</style>
