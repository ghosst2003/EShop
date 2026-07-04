<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">订单管理</span>
          <el-button type="primary" @click="showCreateDialog = true">+ 新建订单</el-button>
        </div>
      </template>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-blue">{{ stats.total_orders }}</div>
          <div class="stat-label">总订单</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-orange">{{ stats.pending_count }}</div>
          <div class="stat-label">待处理</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-green">{{ stats.paid_count }}</div>
          <div class="stat-label">已付款</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-cyan">{{ stats.shipped_count }}</div>
          <div class="stat-label">已发货</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-purple">{{ stats.completed_count }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value stat-gray">€{{ stats.total_revenue }}</div>
          <div class="stat-label">总收入</div>
        </el-card>
      </div>

      <!-- 筛选 -->
      <div class="filter-row">
        <el-input v-model="searchKeyword" placeholder="搜索订单号/买家..." clearable @clear="loadOrders" style="width: 250px" />
        <el-select v-model="statusFilter" placeholder="订单状态" clearable @change="loadOrders" style="width: 150px">
          <el-option label="待处理" value="pending" />
          <el-option label="已付款" value="paid" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button type="primary" @click="loadOrders">搜索</el-button>
      </div>

      <!-- 订单表格 -->
      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column label="来源" width="70">
          <template #default="{ row }">
            <el-tag v-if="row.buyer_id" type="success" size="small">买家</el-tag>
            <el-tag v-else type="info" size="small">后台</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buyer_name" label="买家" width="120" />
        <el-table-column prop="buyer_email" label="邮箱" width="180" />
        <el-table-column label="金额" width="120">
          <template #default="{ row }">€{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="支付" width="90">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 'paid' ? 'success' : 'info'" size="small">{{ paymentLabel(row.payment_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrder(row)">详情</el-button>
            <el-dropdown @command="(cmd) => handleStatusChange(row, cmd)">
              <el-button size="small">变更状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="row.status === 'pending'" command="paid">标记已付款</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'pending'" command="cancelled">取消订单</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'paid'" command="shipped">标记已发货</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'paid'" command="cancelled">取消订单</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'shipped'" command="completed">标记已完成</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadOrders"
        />
      </div>
    </el-card>

    <!-- 新建订单对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建订单" width="700px">
      <el-form :model="newOrder" label-width="100px">
        <el-form-item label="买家姓名" required>
          <el-input v-model="newOrder.buyer_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newOrder.buyer_email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="newOrder.buyer_phone" />
        </el-form-item>
        <el-form-item label="收货地址" required>
          <el-input v-model="newOrder.buyer_address" type="textarea" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="newOrder.payment_method">
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="PayPal" value="paypal" />
            <el-option label="现金" value="cash" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流方式">
          <el-select v-model="newOrder.shipping_method">
            <el-option label="DHL" value="dhl" />
            <el-option label="DPD" value="dpd" />
            <el-option label="自取" value="pickup" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="newOrder.notes" type="textarea" />
        </el-form-item>

        <el-divider>订单商品</el-divider>
        <div v-for="(item, i) in newOrder.items" :key="i" class="order-item-row">
          <el-form-item label="商品名称" required>
            <el-input v-model="item.product_title" />
          </el-form-item>
          <div class="inline-fields">
            <el-form-item label="数量">
              <el-input-number v-model="item.quantity" :min="1" />
            </el-form-item>
            <el-form-item label="单价">
              <el-input-number v-model="item.unit_price" :min="0" :precision="2" />
            </el-form-item>
          </div>
          <el-button size="small" type="danger" @click="newOrder.items.splice(i, 1)">删除</el-button>
        </div>
        <el-button size="small" @click="newOrder.items.push({ product_title: '', quantity: 1, unit_price: 0 })">+ 添加商品</el-button>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createOrder" :loading="creating">创建订单</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情抽屉 -->
    <el-drawer v-model="showDetail" title="订单详情" size="500px">
      <div v-if="currentOrder" class="detail-content">
        <div class="detail-header">
          <h3 class="detail-title">{{ currentOrder.order_number }}</h3>
          <el-tag :type="statusType(currentOrder.status)">{{ statusLabel(currentOrder.status) }}</el-tag>
        </div>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="买家">{{ currentOrder.buyer_name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentOrder.buyer_email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentOrder.buyer_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ currentOrder.buyer_address }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ currentOrder.payment_method || '-' }}</el-descriptions-item>
          <el-descriptions-item label="物流方式">{{ currentOrder.shipping_method || '-' }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ currentOrder.tracking_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="总金额">€{{ currentOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="section-title">商品明细</h4>
        <el-table :data="currentOrder.items" size="small">
          <el-table-column prop="product_title" label="商品" />
          <el-table-column prop="quantity" label="数量" width="60" />
          <el-table-column label="单价" width="100">
            <template #default="{ row }">€{{ row.unit_price }}</template>
          </el-table-column>
          <el-table-column label="小计" width="100">
            <template #default="{ row }">€{{ row.subtotal }}</template>
          </el-table-column>
        </el-table>

        <h4 class="section-title">状态日志</h4>
        <el-timeline>
          <el-timeline-item
            v-for="log in currentOrder.status_logs"
            :key="log.id"
            :timestamp="formatDate(log.created_at)"
          >
            {{ log.from_status || '创建' }} → {{ statusLabel(log.to_status) }}
            <span v-if="log.note" class="log-note">({{ log.note }})</span>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const orders = ref([])
const stats = ref({})
const loading = ref(false)
const creating = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref('')
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showDetail = ref(false)
const currentOrder = ref(null)

const newOrder = ref({
  buyer_name: '',
  buyer_email: '',
  buyer_phone: '',
  buyer_address: '',
  payment_method: '',
  shipping_method: '',
  notes: '',
  items: [{ product_title: '', quantity: 1, unit_price: 0 }],
})

const statusLabel = (s) => ({
  pending: '待处理', paid: '已付款', shipped: '已发货',
  completed: '已完成', cancelled: '已取消',
}[s] || s)

const statusType = (s) => ({
  pending: 'warning', paid: 'success', shipped: 'info',
  completed: '', cancelled: 'danger',
}[s] || '')

const paymentLabel = (s) => ({
  pending: '待付', paid: '已付', failed: '失败',
  requires_action: '需操作', refunded: '已退款',
}[s] || '待付')

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (statusFilter.value) params.status = statusFilter.value
    if (searchKeyword.value) params.keyword = searchKeyword.value

    const res = await api.get('/admin/orders', { params })
    orders.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await api.get('/admin/orders/stats')
    stats.value = res.data
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const createOrder = async () => {
  if (!newOrder.value.buyer_name || !newOrder.value.buyer_address) {
    ElMessage.warning('请填写买家姓名和地址')
    return
  }
  creating.value = true
  try {
    await api.post('/admin/orders', newOrder.value)
    ElMessage.success('订单创建成功')
    showCreateDialog.value = false
    newOrder.value = { buyer_name: '', buyer_email: '', buyer_phone: '', buyer_address: '', payment_method: '', shipping_method: '', notes: '', items: [{ product_title: '', quantity: 1, unit_price: 0 }] }
    loadOrders()
    loadStats()
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    creating.value = false
  }
}

const viewOrder = async (order) => {
  try {
    const res = await api.get(`/admin/orders/${order.id}`)
    currentOrder.value = res.data
    showDetail.value = true
  } catch (e) {
    ElMessage.error('加载订单详情失败')
  }
}

const handleStatusChange = async (order, newStatus) => {
  try {
    await api.post(`/admin/orders/${order.id}/status`, { status: newStatus })
    ElMessage.success('状态更新成功')
    loadOrders()
    loadStats()
  } catch (e) {
    ElMessage.error('更新失败: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(() => {
  loadOrders()
  loadStats()
})
</script>

<style scoped>
/* 统计卡片 — 横向排列 */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  flex: 1;
  text-align: center;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
}
.stat-label {
  font-size: 14px;
  color: #909399;
}
.stat-blue  { color: #409eff; }
.stat-orange { color: #e6a23c; }
.stat-green  { color: #67c23a; }
.stat-cyan   { color: #00bcd4; }
.stat-purple { color: #9c27b0; }
.stat-gray   { color: #606266; }

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  font-size: 18px;
  font-weight: bold;
}

/* 筛选行 */
.filter-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

/* 分页 */
.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 订单商品行 */
.order-item-row {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}
.inline-fields {
  display: flex;
  gap: 16px;
}

/* 订单详情 */
.detail-content > * + * {
  margin-top: 16px;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.detail-title {
  font-size: 18px;
  font-weight: bold;
}
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-top: 16px;
}
.log-note {
  color: #909399;
}
</style>
