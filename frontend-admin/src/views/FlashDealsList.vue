<template>
  <div>
    <div class="page-header">
      <h2>闪购管理</h2>
      <el-button type="primary" @click="$router.push('/flash-deals/new')">新增闪购</el-button>
    </div>

    <el-table :data="deals" v-loading="loading" style="width: 100%">
      <el-table-column label="商品" width="280">
        <template #default="{ row }">
          <div class="deal-product">
            <el-image
              v-if="row.product?.image_url"
              :src="row.product.image_url"
              style="width: 40px; height: 40px; border-radius: 4px; margin-right: 8px"
              fit="cover"
            />
            <span>{{ row.product?.title_en || row.product?.title || `商品 #${row.product_id}` }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="原价" width="100">
        <template #default="{ row }">€{{ row.original_price }}</template>
      </el-table-column>
      <el-table-column label="闪购价" width="100">
        <template #default="{ row }">
          <span class="deal-price">€{{ row.deal_price }}</span>
        </template>
      </el-table-column>
      <el-table-column label="折扣" width="80">
        <template #default="{ row }">
          <span class="discount-badge">
            -{{ calcDiscount(row.original_price, row.deal_price) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column label="活动时间" width="320">
        <template #default="{ row }">
          <span class="time-range">{{ formatTime(row.start_time) }} ~ {{ formatTime(row.end_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_active_display"
            @change="toggleActive(row)"
            :loading="row._toggling"
            size="small"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/flash-deals/${row.id}/edit`)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && deals.length === 0" description="暂无闪购活动" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFlashDeals, deleteFlashDeal, updateFlashDeal } from '../api'

const deals = ref([])
const loading = ref(false)

function calcDiscount(original, deal) {
  if (!original || original <= 0) return 0
  return Math.round((1 - deal / original) * 100)
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadDeals() {
  loading.value = true
  try {
    const { data } = await getFlashDeals()
    deals.value = data.map(d => ({
      ...d,
      is_active_display: d.is_active === 1,
      _toggling: false,
    }))
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function toggleActive(row) {
  row._toggling = true
  try {
    await updateFlashDeal(row.id, { is_active: row.is_active_display })
    row.is_active = row.is_active_display ? 1 : 0
    ElMessage.success(row.is_active_display ? '已启用' : '已禁用')
  } catch {
    row.is_active_display = !row.is_active_display
    ElMessage.error('操作失败')
  } finally {
    row._toggling = false
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除该闪购活动？', '确认', { type: 'warning' })
    await deleteFlashDeal(id)
    ElMessage.success('已删除')
    loadDeals()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(loadDeals)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.deal-product {
  display: flex;
  align-items: center;
}
.deal-price {
  color: #ff4400;
  font-weight: bold;
}
.discount-badge {
  color: #fff;
  background: #ff4400;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}
.time-range {
  font-size: 12px;
  color: #666;
}
</style>
