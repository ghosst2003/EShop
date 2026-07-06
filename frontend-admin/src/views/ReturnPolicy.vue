<template>
  <div class="return-policy-page">
    <h2 class="page-title">退货政策管理</h2>

    <!-- 全局默认政策 -->
    <el-card class="mb-6">
      <template #header>
        <div class="card-header">
          <span>全局默认退货政策</span>
          <el-button type="primary" size="small" @click="saveGlobal" :loading="saving">保存</el-button>
        </div>
      </template>

      <el-form :model="globalPolicy" label-width="200px" class="policy-form">
        <el-form-item label="退货天数">
          <el-input-number v-model="globalPolicy.return_days" :min="0" :max="365" />
          <span class="help-text">天（0 表示不支持退货）</span>
        </el-form-item>

        <el-form-item label="买家承担退货运费">
          <el-switch v-model="globalPolicy.buyer_pays_return_shipping" />
        </el-form-item>

        <el-form-item label="重新入库费">
          <el-input-number v-model="globalPolicy.restocking_fee_percent" :min="0" :max="100" :precision="2" :step="5" />
          <span class="help-text">%</span>
        </el-form-item>

        <el-form-item label="退货说明（中文）">
          <el-input v-model="globalPolicy.description" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>

        <el-form-item label="Return Policy Description (English)">
          <el-input v-model="globalPolicy.description_en" type="textarea" :rows="3" placeholder="Optional" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 商品级别覆盖 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品级别退货政策覆盖</span>
          <div class="header-actions">
            <el-input
              v-model="searchProductId"
              placeholder="输入商品 ID 查询"
              style="width: 200px; margin-right: 8px"
              size="small"
              @keyup.enter="loadProductPolicy"
            />
            <el-button size="small" @click="loadProductPolicy">查询</el-button>
          </div>
        </div>
      </template>

      <div v-if="currentProductPolicy" class="product-policy-section">
        <el-alert
          :title="`商品 ID: ${searchProductId}`"
          type="info"
          :closable="false"
          class="mb-4"
        />

        <el-form :model="currentProductPolicy" label-width="200px" class="policy-form">
          <el-form-item label="退货天数">
            <el-input-number v-model="currentProductPolicy.return_days" :min="0" :max="365" placeholder="使用全局默认" />
            <span class="help-text">留空使用全局默认</span>
          </el-form-item>

          <el-form-item label="买家承担退货运费">
            <el-switch
              :model-value="currentProductPolicy.buyer_pays_return_shipping"
              @change="val => currentProductPolicy.buyer_pays_return_shipping = val"
            />
            <span class="help-text">留空使用全局默认</span>
          </el-form-item>

          <el-form-item label="重新入库费">
            <el-input-number v-model="currentProductPolicy.restocking_fee_percent" :min="0" :max="100" :precision="2" :step="5" placeholder="使用全局默认" />
            <span class="help-text">%</span>
          </el-form-item>

          <el-form-item label="退货说明（中文）">
            <el-input v-model="currentProductPolicy.description" type="textarea" :rows="3" placeholder="使用全局默认" />
          </el-form-item>

          <el-form-item label="Return Policy Description (English)">
            <el-input v-model="currentProductPolicy.description_en" type="textarea" :rows="3" placeholder="Use global default" />
          </el-form-item>

          <el-form-item>
            <div class="form-actions">
              <el-button type="primary" size="small" @click="saveProductPolicy" :loading="saving">保存覆盖</el-button>
              <el-button type="danger" size="small" @click="removeProductPolicy" :loading="deleting">删除覆盖（回退全局）</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <el-empty v-else description="请输入商品 ID 查询" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getGlobalReturnPolicy,
  updateGlobalReturnPolicy,
  getProductReturnPolicy,
  setProductReturnPolicy,
  deleteProductReturnPolicy,
} from '../api'

const globalPolicy = ref({
  return_days: 30,
  buyer_pays_return_shipping: true,
  restocking_fee_percent: 0,
  description: '',
  description_en: '',
})

const searchProductId = ref('')
const currentProductPolicy = ref(null)
const saving = ref(false)
const deleting = ref(false)

async function loadGlobalPolicy() {
  try {
    const { data } = await getGlobalReturnPolicy()
    globalPolicy.value = {
      return_days: data.return_days,
      buyer_pays_return_shipping: !!data.buyer_pays_return_shipping,
      restocking_fee_percent: Number(data.restocking_fee_percent),
      description: data.description || '',
      description_en: data.description_en || '',
    }
  } catch {
    ElMessage.error('加载全局退货政策失败')
  }
}

async function saveGlobal() {
  saving.value = true
  try {
    await updateGlobalReturnPolicy({
      return_days: globalPolicy.value.return_days,
      buyer_pays_return_shipping: globalPolicy.value.buyer_pays_return_shipping,
      restocking_fee_percent: globalPolicy.value.restocking_fee_percent,
      description: globalPolicy.value.description,
      description_en: globalPolicy.value.description_en,
    })
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function loadProductPolicy() {
  if (!searchProductId.value) return
  try {
    const { data } = await getProductReturnPolicy(searchProductId.value)
    if (data) {
      currentProductPolicy.value = {
        return_days: data.return_days ?? undefined,
        buyer_pays_return_shipping: data.buyer_pays_return_shipping != null ? !!data.buyer_pays_return_shipping : undefined,
        restocking_fee_percent: data.restocking_fee_percent != null ? Number(data.restocking_fee_percent) : undefined,
        description: data.description || '',
        description_en: data.description_en || '',
      }
    } else {
      currentProductPolicy.value = {
        return_days: undefined,
        buyer_pays_return_shipping: undefined,
        restocking_fee_percent: undefined,
        description: '',
        description_en: '',
      }
    }
  } catch {
    currentProductPolicy.value = null
    ElMessage.error('查询失败')
  }
}

async function saveProductPolicy() {
  saving.value = true
  try {
    await setProductReturnPolicy(searchProductId.value, {
      product_id: parseInt(searchProductId.value),
      return_days: currentProductPolicy.value.return_days,
      buyer_pays_return_shipping: currentProductPolicy.value.buyer_pays_return_shipping,
      restocking_fee_percent: currentProductPolicy.value.restocking_fee_percent,
      description: currentProductPolicy.value.description || null,
      description_en: currentProductPolicy.value.description_en || null,
    })
    ElMessage.success('已保存商品级别覆盖')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function removeProductPolicy() {
  deleting.value = true
  try {
    await deleteProductReturnPolicy(searchProductId.value)
    currentProductPolicy.value = null
    ElMessage.success('已删除覆盖，将使用全局默认')
  } catch {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
  }
}

onMounted(loadGlobalPolicy)
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
.header-actions {
  display: flex;
  align-items: center;
}
.policy-form .el-form-item {
  margin-bottom: 20px;
}
.help-text {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}
.form-actions {
  display: flex;
  gap: 8px;
}
.mb-4 {
  margin-bottom: 16px;
}
.mb-6 {
  margin-bottom: 24px;
}
</style>
