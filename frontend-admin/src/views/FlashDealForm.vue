<template>
  <div>
    <div class="page-header">
      <h2>{{ isEdit ? '编辑闪购' : '新增闪购' }}</h2>
      <el-button @click="$router.push('/flash-deals')">返回</el-button>
    </div>

    <el-form :model="form" label-width="120px" v-loading="loading" style="max-width: 600px">
      <el-card class="form-card">
        <template #header>基本信息</template>

        <el-form-item label="商品" required>
          <el-select
            v-model="form.product_id"
            placeholder="搜索并选择商品"
            filterable
            remote
            :remote-method="searchProducts"
            :loading="searchLoading"
            style="width: 100%"
          >
            <el-option
              v-for="p in productOptions"
              :key="p.id"
              :label="`${p.title_en || p.title} (€${p.sale_price})`"
              :value="p.id"
            >
              <div style="display: flex; align-items: center; gap: 8px">
                <el-image
                  v-if="p.thumbnail_url"
                  :src="p.thumbnail_url"
                  style="width: 30px; height: 30px; border-radius: 4px"
                  fit="cover"
                />
                <span>{{ p.title_en || p.title }}</span>
                <span style="color: #999; font-size: 12px; margin-left: auto">€{{ p.sale_price }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="原价 (EUR)" required>
          <el-input-number v-model="form.original_price" :min="0.01" :precision="2" style="width: 200px" />
        </el-form-item>

        <el-form-item label="闪购价 (EUR)" required>
          <el-input-number v-model="form.deal_price" :min="0.01" :precision="2" style="width: 200px" />
        </el-form-item>

        <el-form-item label="活动时间" required>
          <el-date-picker
            v-model="dateTimeRange"
            type="datetimerange"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="是否启用">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" style="width: 120px" />
        </el-form-item>
      </el-card>

      <div style="margin-top: 24px; text-align: center">
        <el-button type="primary" size="large" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建闪购' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFlashDeal, createFlashDeal, updateFlashDeal, getProducts } from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const form = reactive({
  product_id: null,
  original_price: null,
  deal_price: null,
  is_active: true,
  sort_order: 0,
})

const dateTimeRange = ref([])
const loading = ref(false)
const saving = ref(false)
const productOptions = ref([])
const searchLoading = ref(false)

async function searchProducts(query) {
  if (!query) return
  searchLoading.value = true
  try {
    const { data } = await getProducts({ page: 1, page_size: 50, keyword: query })
    productOptions.value = (data.items || []).map(p => ({
      id: p.id,
      title: p.title,
      title_en: p.title_en,
      sale_price: p.sale_price,
      thumbnail_url: p.images?.[0]?.thumbnail_url || p.images?.[0]?.image_url || null,
    }))
  } catch {
    // fallback: search by title manually
    const { data } = await getProducts({ page: 1, page_size: 50 })
    const filtered = (data.items || []).filter(p =>
      (p.title_en || p.title).toLowerCase().includes(query.toLowerCase())
    )
    productOptions.value = filtered.map(p => ({
      id: p.id,
      title: p.title,
      title_en: p.title_en,
      sale_price: p.sale_price,
      thumbnail_url: p.images?.[0]?.thumbnail_url || p.images?.[0]?.image_url || null,
    }))
  } finally {
    searchLoading.value = false
  }
}

async function loadDeal() {
  loading.value = true
  try {
    const { data } = await getFlashDeal(route.params.id)
    form.product_id = data.product_id
    form.original_price = data.original_price
    form.deal_price = data.deal_price
    form.is_active = data.is_active === 1
    form.sort_order = data.sort_order
    dateTimeRange.value = [data.start_time, data.end_time]
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!form.product_id || !form.original_price || !form.deal_price || !dateTimeRange.value?.length) {
    ElMessage.warning('请填写必填字段')
    return
  }
  if (form.deal_price >= form.original_price) {
    ElMessage.warning('闪购价应低于原价')
    return
  }

  saving.value = true
  try {
    const payload = {
      product_id: form.product_id,
      original_price: form.original_price,
      deal_price: form.deal_price,
      start_time: dateTimeRange.value[0],
      end_time: dateTimeRange.value[1],
      is_active: form.is_active,
      sort_order: form.sort_order,
    }

    if (isEdit.value) {
      await updateFlashDeal(route.params.id, payload)
      ElMessage.success('保存成功')
    } else {
      await createFlashDeal(payload)
      ElMessage.success('创建成功')
    }
    router.push('/flash-deals')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  // 加载一些初始商品选项供选择
  try {
    const { data } = await getProducts({ page: 1, page_size: 20 })
    productOptions.value = (data.items || []).map(p => ({
      id: p.id,
      title: p.title,
      title_en: p.title_en,
      sale_price: p.sale_price,
      thumbnail_url: p.images?.[0]?.thumbnail_url || p.images?.[0]?.image_url || null,
    }))
  } catch {}

  if (isEdit.value) {
    await loadDeal()
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.form-card {
  margin-bottom: 16px;
}
</style>
