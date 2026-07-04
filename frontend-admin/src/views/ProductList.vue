<template>
  <div>
    <div class="page-header">
      <h2>商品管理</h2>
      <el-button type="primary" @click="$router.push('/products/new')">新增商品</el-button>
    </div>

    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px" @change="fetchProducts">
          <el-option label="草稿" value="draft" />
          <el-option label="上架" value="active" />
          <el-option label="已售" value="sold" />
          <el-option label="归档" value="archived" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button @click="fetchProducts">搜索</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="products" stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <el-image
            v-if="row.images?.length"
            :src="row.images[0].thumbnail_url || row.images[0].image_url"
            style="width: 50px; height: 50px"
            fit="cover"
          />
          <span v-else style="color: #ccc">无图</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="商品名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="title_en" label="英文名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="sale_price" label="售价" width="100">
        <template #default="{ row }">€ {{ row.sale_price }}</template>
      </el-table-column>
      <el-table-column prop="stock_quantity" label="库存" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.auto_manage_stock" :type="row.stock_quantity > 0 ? 'success' : 'danger'" size="small">
            {{ row.stock_quantity }}
          </el-tag>
          <span v-else style="color: #909399">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="condition_grade" label="成色" width="90">
        <template #default="{ row }">
          <el-tag :type="conditionTagType(row.condition_grade)" size="small">
            {{ conditionLabel(row.condition_grade) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发货地" width="100">
        <template #default="{ row }">
          <span v-if="row.origin_country_code" class="flex items-center gap-1">
            {{ flagEmoji(row.origin_country_code) }} {{ row.origin_country_code }}
          </span>
          <span v-else style="color: #ccc">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/products/${row.id}/edit`)">编辑</el-button>
          <el-select v-model="row.status" size="small" style="width: 90px" @change="handleStatusChange(row)">
            <el-option label="上架" value="active" />
            <el-option label="已售" value="sold" />
            <el-option label="草稿" value="draft" />
            <el-option label="归档" value="archived" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="fetchProducts"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProducts, updateProductStatus } from '../api'

const products = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchForm = reactive({ status: '' })

const conditionLabel = (g) => ({
  new: '全新', like_new: '近新', good: '良好', fair: '一般', poor: '较差', for_parts: '零件'
}[g] || g)

const flagEmoji = (code) => {
  if (!code || code.length !== 2) return ''
  const codePoints = code.toUpperCase().split('').map(char => 127397 + char.charCodeAt())
  return String.fromCodePoint(...codePoints)
}

const conditionTagType = (g) => ({
  new: 'success', like_new: 'success', good: 'warning', fair: 'info', poor: 'danger', for_parts: 'danger'
}[g] || 'info')

const statusLabel = (s) => ({ draft: '草稿', active: '上架', sold: '已售', archived: '归档' }[s] || s)
const statusTagType = (s) => ({ draft: 'info', active: 'success', sold: 'warning', archived: 'danger' }[s] || 'info')

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchForm.status) params.status = searchForm.status
    const { data } = await getProducts(params)
    products.value = data.items
    total.value = data.total
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleStatusChange = async (row) => {
  try {
    await updateProductStatus(row.id, row.status)
    ElMessage.success('状态已更新')
  } catch (e) {
    ElMessage.error('更新失败')
    fetchProducts()
  }
}

onMounted(fetchProducts)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.search-form {
  margin-bottom: 16px;
}
</style>
