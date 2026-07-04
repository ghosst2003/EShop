<template>
  <div>
    <div class="page-header">
      <h2>{{ isEdit ? '编辑商品' : '新增商品' }}</h2>
      <el-button @click="$router.push('/products')">返回</el-button>
    </div>

    <el-form :model="form" label-width="120px" v-loading="loading">
      <!-- 基本信息 -->
      <el-card class="form-card">
        <template #header>基本信息</template>
        <el-form-item label="中文标题" required>
          <el-input v-model="form.title" placeholder="商品中文标题" />
        </el-form-item>
        <el-form-item label="英文标题" required>
          <el-input v-model="form.title_en" placeholder="商品英文标题（买家端展示）" />
        </el-form-item>
        <el-form-item label="URL 短码">
          <el-input v-model="form.slug" placeholder="留空则从英文标题自动生成">
            <template #prepend>/products/</template>
          </el-input>
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="form.category_id" placeholder="选择分类" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="`${c.name} / ${c.name_en}`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="form.brand" placeholder="品牌（可选）" />
        </el-form-item>
      </el-card>

      <!-- 描述（富文本） -->
      <el-card class="form-card">
        <template #header>描述</template>
        <el-form-item label="中文描述">
          <QuillEditor
            v-model="form.description"
            :product-id="currentProductId"
            placeholder="中文描述（管理端参考）"
            height="200px"
          />
        </el-form-item>
        <el-form-item label="英文描述">
          <QuillEditor
            v-model="form.description_en"
            :product-id="currentProductId"
            placeholder="英文描述（买家端展示）"
            height="300px"
          />
        </el-form-item>
        <el-form-item label="成色备注">
          <el-input v-model="form.condition_note" type="textarea" :rows="2" placeholder="成色详细描述" />
        </el-form-item>
      </el-card>

      <!-- 价格与成色 -->
      <el-card class="form-card">
        <template #header>价格与成色</template>
        <div class="fixed-width-row">
          <el-form-item label="原价 (EUR)" :label-width="100">
            <el-input-number v-model="form.original_price" :precision="2" :min="0" style="width: 100px" />
          </el-form-item>
          <el-form-item label="售价 (EUR)" :label-width="100">
            <el-input-number v-model="form.sale_price" :precision="2" :min="0.01" style="width: 100px" />
          </el-form-item>
          <el-form-item label="成色" :label-width="60">
            <el-select v-model="form.condition_grade" style="width: 100px">
              <el-option label="全新 (New)" value="new" />
              <el-option label="近新 (Like New)" value="like_new" />
              <el-option label="良好 (Good)" value="good" />
              <el-option label="一般 (Fair)" value="fair" />
              <el-option label="较差 (Poor)" value="poor" />
              <el-option label="零件 (For Parts)" value="for_parts" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" :label-width="60">
            <el-select v-model="form.status" style="width: 100px">
              <el-option label="草稿" value="draft" />
              <el-option label="上架" value="active" />
              <el-option label="已售" value="sold" />
            </el-select>
          </el-form-item>
        </div>
      </el-card>

      <!-- 库存管理 -->
      <el-card class="form-card">
        <template #header>库存管理</template>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="库存数量">
              <el-input-number v-model="form.stock_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="自动管理库存">
              <el-switch v-model="form.auto_manage_stock" active-text="开启" inactive-text="关闭" />
              <p style="color: #909399; font-size: 12px; margin-top: 4px">开启后，下单自动扣减库存</p>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 重量与尺寸 -->
      <el-card class="form-card">
        <template #header>
          <span>重量与尺寸</span>
          <el-tooltip content="用于计算运费，按实际重量或体积重量（长×宽×高÷5000）取较大值" placement="top">
            <el-icon style="margin-left: 6px; cursor: help"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="重量 (kg)">
              <el-input-number v-model="form.weight_kg" :min="0.1" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="长 (cm)">
              <el-input-number v-model="form.length_cm" :min="0" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="宽 (cm)">
              <el-input-number v-model="form.width_cm" :min="0" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="高 (cm)">
              <el-input-number v-model="form.height_cm" :min="0" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="运输类别">
              <el-select v-model="form.shipping_category" style="width: 100%">
                <el-option label="标准 (Standard)" value="standard" />
                <el-option label="超大件 (Oversized)" value="oversized" />
                <el-option label="易碎品 (Fragile)" value="fragile" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 图片 -->
      <el-card class="form-card">
        <template #header>图片</template>
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
          list-type="picture-card"
          multiple
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
        <div v-if="isEdit && existingImages.length" class="existing-images">
          <p>已有图片：</p>
          <el-image
            v-for="img in existingImages"
            :key="img.id"
            :src="img.thumbnail_url || img.image_url"
            style="width: 80px; height: 80px; margin-right: 8px"
            fit="cover"
          />
        </div>
      </el-card>

      <!-- 配送设置（发货地 + 目的地 + 运费） -->
      <el-card class="form-card">
        <template #header>
          <span>配送设置</span>
          <el-tooltip content="配置从此商品发货地到各个目的地的运费" placement="top">
            <el-icon style="margin-left: 6px; cursor: help"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>

        <!-- 发货地选择 -->
        <el-form-item label="发货地" label-width="80px">
          <el-select v-model="form.origin_country_code" placeholder="选择发货国家" filterable clearable style="width: 300px" @change="onOriginChange">
            <el-option
              v-for="c in countries"
              :key="c.code"
              :label="`${c.flag_emoji || ''} ${c.name_en || c.name} (${c.code})`"
              :value="c.code"
            />
          </el-select>
          <span class="ml-2 text-gray-400 text-sm">此商品从哪个国家发货</span>
        </el-form-item>

        <el-divider />

        <!-- 运费模式切换 -->
        <el-radio-group v-model="shippingMode" style="margin-bottom: 16px">
          <el-radio-button value="global">使用全局规则</el-radio-button>
          <el-radio-button value="custom">自定义运费</el-radio-button>
        </el-radio-group>

        <!-- 全局规则展示（只读） -->
        <div v-if="shippingMode === 'global'">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-700">全局运费规则（当前发货地）</span>
          </div>

          <el-table :data="filteredGlobalRules" size="small" border style="width: 100%" stripe>
            <el-table-column label="发货地" width="150">
              <template #default="{ row }">
                <span class="text-lg mr-1">{{ row.origin_flag_emoji || '🏳️' }}</span>
                <span>{{ row.origin_country_name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="目的地" width="150">
              <template #default="{ row }">
                <span class="text-lg mr-1">{{ row.destination_flag_emoji || '🏳️' }}</span>
                <span>{{ row.destination_country_name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="派送方式" width="150">
              <template #default="{ row }">{{ row.shipping_method_name || '—' }}</template>
            </el-table-column>
            <el-table-column label="运费 (€)" width="120" align="right">
              <template #default="{ row }">
                <span class="font-bold">€{{ Number(row.fee).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column>
              <template #default="{ row }">
                <span v-if="!row.is_active" class="text-gray-400 text-xs">已停用</span>
                <span v-else class="text-green-500 text-xs">启用</span>
              </template>
            </el-table-column>
          </el-table>

          <el-alert
            v-if="filteredGlobalRules.length === 0 && form.origin_country_code"
            :title="`尚未配置从 ${originCountryName} 发货的全局规则，请前往「发货地管理」页面配置`"
            type="warning"
            :closable="false"
            style="margin-top: 12px"
          />
          <el-alert
            v-else-if="!form.origin_country_code"
            title="请先选择发货地"
            type="info"
            :closable="false"
            style="margin-top: 12px"
          />
        </div>

        <!-- 自定义规则表格 -->
        <div v-else>
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-700">自定义运费规则</span>
            <el-button size="small" type="primary" @click="shippingRules.push({ origin_country_code: form.origin_country_code || '', destination_country_code: '', shipping_method_id: null, fee: null, is_disabled: false, defaultFee: null })">
              + 添加规则
            </el-button>
          </div>

          <el-table :data="shippingRules" size="small" border style="width: 100%">
            <!-- 发货地 -->
            <el-table-column label="发货地" width="180">
              <template #default="{ row }">
                <el-select v-model="row.origin_country_code" placeholder="发货地" size="small" filterable style="width: 100%">
                  <el-option
                    v-for="c in countries"
                    :key="c.code"
                    :label="`${c.flag_emoji || ''} ${c.name_en || c.name}`"
                    :value="c.code"
                  />
                </el-select>
              </template>
            </el-table-column>
            <!-- 目的地 -->
            <el-table-column label="目的地" width="180">
              <template #default="{ row }">
                <el-select v-model="row.destination_country_code" placeholder="目的地" size="small" filterable style="width: 100%">
                  <el-option
                    v-for="c in countries"
                    :key="c.code"
                    :label="`${c.flag_emoji || ''} ${c.name_en || c.name}`"
                    :value="c.code"
                  />
                </el-select>
              </template>
            </el-table-column>
            <!-- 派送方式 -->
            <el-table-column label="派送方式" width="160">
              <template #default="{ row }">
                <el-select v-model="row.shipping_method_id" placeholder="选择方式" size="small" style="width: 100%">
                  <el-option v-for="m in shippingMethods" :key="m.id" :label="m.name" :value="m.id" />
                </el-select>
              </template>
            </el-table-column>
            <!-- 运费 -->
            <el-table-column label="运费 (€)" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.fee" :min="0" :precision="2" placeholder="运费" size="small" style="width: 100%" />
              </template>
            </el-table-column>
            <!-- 全局参考价格 -->
            <el-table-column label="参考价格" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.defaultFee" class="text-gray-400 text-xs">€{{ Number(row.defaultFee).toFixed(2) }}</span>
                <span v-else class="text-gray-300 text-xs">—</span>
              </template>
            </el-table-column>
            <!-- 禁用 -->
            <el-table-column label="禁用" width="60" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.is_disabled" size="small" />
              </template>
            </el-table-column>
            <!-- 操作 -->
            <el-table-column label="操作" width="70" fixed="right">
              <template #default="{ $index }">
                <el-button size="small" type="danger" @click="shippingRules.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <p v-if="shippingRules.length === 0" class="text-gray-400 text-sm mt-3 text-center">
            点击上方「+ 添加规则」配置发货地到目的地的运费
          </p>
        </div>
      </el-card>

      <!-- 配送说明 -->
      <el-card class="form-card">
        <template #header>
          <span>配送说明</span>
          <el-tooltip content="为买家展示关于此商品配送的说明条目（如包装方式、预计发货时间等）" placement="top">
            <el-icon style="margin-left: 6px; cursor: help"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>

        <!-- 配送说明模式切换 -->
        <el-radio-group v-model="shippingNotesMode" style="margin-bottom: 16px">
          <el-radio-button value="default">使用通用配送说明</el-radio-button>
          <el-radio-button value="custom">自定义配送说明</el-radio-button>
        </el-radio-group>

        <template v-if="shippingNotesMode === 'custom'">
          <el-table :data="shippingNotes" size="small" border style="width: 100%">
            <el-table-column label="排序" width="80">
              <template #default="{ row }">
                <el-input-number v-model="row.sort_order" :min="0" :max="999" size="small" style="width: 100%" />
              </template>
            </el-table-column>
            <el-table-column label="标题（中文）" width="180">
              <template #default="{ row }">
                <el-input v-model="row.title" placeholder="如：发货时间" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="标题（英文）" width="180">
              <template #default="{ row }">
                <el-input v-model="row.title_en" placeholder="Shipping Time" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="说明（中文）">
              <template #default="{ row }">
                <el-input v-model="row.content" type="textarea" :rows="2" placeholder="详细说明" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="说明（英文）">
              <template #default="{ row }">
                <el-input v-model="row.content_en" type="textarea" :rows="2" placeholder="Details in English" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ $index }">
                <el-button size="small" type="danger" @click="shippingNotes.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button size="small" style="margin-top: 12px" @click="shippingNotes.push({ title: '', title_en: '', content: '', content_en: '', sort_order: shippingNotes.length * 10, is_active: 1 })">
            + 添加配送说明
          </el-button>
        </template>
        <el-alert v-else title="将展示系统通用配送说明" type="success" :closable="false" />
      </el-card>

      <!-- 标签 -->
      <el-card class="form-card">
        <template #header>标签</template>
        <el-input v-model="tagsInput" placeholder="用逗号分隔，如：vintage, handmade, limited" />
      </el-card>

      <!-- 保存按钮 -->
      <div style="margin-top: 24px; text-align: center">
        <el-button type="primary" size="large" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建商品' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, QuestionFilled } from '@element-plus/icons-vue'
import QuillEditor from '../components/QuillEditor.vue'
import { getProduct, createProduct, updateProduct, getCategories, uploadProductImage, getCountries, createCountry, getShippingMethods, getProductShippingOverrides, updateProductShippingOverrides, getProductShippingNotes, updateProductShippingNotes, getGlobalShippingRules } from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const currentProductId = computed(() => isEdit.value ? route.params.id : null)

const form = reactive({
  title: '',
  title_en: '',
  slug: '',
  description: '',
  description_en: '',
  category_id: null,
  brand: '',
  original_price: null,
  sale_price: 0,
  condition_grade: 'like_new',
  condition_note: '',
  status: 'draft',
  tags: [],
  stock_quantity: 0,
  auto_manage_stock: true,
  weight_kg: 0.5,
  length_cm: null,
  width_cm: null,
  height_cm: null,
  shipping_category: 'standard',
  origin_country_code: null,
})

const categories = ref([])
const countries = ref([])
const shippingMethods = ref([])
const loading = ref(false)
const saving = ref(false)
const fileList = ref([])
const existingImages = ref([])
const tagsInput = ref('')
const shippingMode = ref('global')             // 'global' = 引用全局规则, 'custom' = 自定义覆盖
const shippingRules = ref([])           // { origin, destination, method_id, fee, is_disabled }
const globalRules = ref([])             // 全局发货地→目的地→运费规则
const shippingNotesMode = ref('default')
const shippingNotes = ref([])

// 发货地信息
const originFlag = computed(() => {
  if (!form.origin_country_code) return ''
  const c = countries.value.find(c => c.code === form.origin_country_code)
  return c?.flag_emoji || ''
})
const originCountryName = computed(() => {
  if (!form.origin_country_code) return ''
  const c = countries.value.find(c => c.code === form.origin_country_code)
  return c?.name_en || c?.name || form.origin_country_code
})

/** 查找某个目的地+派送方式的全局默认价格 */
function getDefaultFee(destCode, methodId) {
  const method = shippingMethods.value.find(m => m.id === methodId)
  if (!method) return null
  const rule = (method.countries || []).find(c => c.country_code === destCode)
  return rule ? rule.base_fee : null
}

/** 根据当前发货地筛选全局规则 */
const filteredGlobalRules = computed(() => {
  if (!form.origin_country_code) return []
  const originUpper = form.origin_country_code.toUpperCase()
  return globalRules.value.filter(r => r.origin_country_code.toUpperCase() === originUpper)
})

/** 查找全局规则中某目的地+派送方式的价格 */
function getGlobalFee(destCode, methodId) {
  const originUpper = form.origin_country_code?.toUpperCase() || ''
  const destUpper = destCode?.toUpperCase() || ''
  const rule = globalRules.value.find(r =>
    r.origin_country_code.toUpperCase() === originUpper &&
    r.destination_country_code.toUpperCase() === destUpper &&
    r.shipping_method_id === methodId
  )
  return rule ? Number(rule.fee) : null
}

/** 根据全局规则更新 shippingRules 的参考价格 */

/** 根据全局规则更新 shippingRules 的参考价格 */
function refreshDefaultFees() {
  for (const rule of shippingRules.value) {
    if (rule.destination_country_code && rule.shipping_method_id) {
      rule.defaultFee = getGlobalFee(rule.destination_country_code, rule.shipping_method_id)
    }
  }
}

/** 发货地变更时，刷新参考价格 */
function onOriginChange() {
  refreshDefaultFees()
}

onMounted(async () => {
  try {
    const { data: cats } = await getCategories()
    categories.value = cats
    const { data: ctrys } = await getCountries()
    countries.value = ctrys
    const { data: methods } = await getShippingMethods()
    shippingMethods.value = methods.filter(m => m.is_active)
    // 加载全局发货地→目的地→运费规则
    try {
      const { data: global } = await getGlobalShippingRules()
      globalRules.value = global
    } catch {}
  } catch {}

  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await getProduct(route.params.id)
      Object.assign(form, {
        title: data.title || '',
        title_en: data.title_en || '',
        slug: data.slug || '',
        description: data.description || '',
        description_en: data.description_en || '',
        category_id: data.category_id,
        brand: data.brand || '',
        original_price: data.original_price,
        sale_price: data.sale_price,
        condition_grade: data.condition_grade,
        condition_note: data.condition_note || '',
        status: data.status,
        stock_quantity: data.stock_quantity ?? 0,
        auto_manage_stock: data.auto_manage_stock ?? true,
        weight_kg: Number(data.weight_kg) || 0.5,
        length_cm: data.length_cm ? Number(data.length_cm) : null,
        width_cm: data.width_cm ? Number(data.width_cm) : null,
        height_cm: data.height_cm ? Number(data.height_cm) : null,
        shipping_category: data.shipping_category || 'standard',
        origin_country_code: data.origin_country_code || null,
      })
      existingImages.value = data.images || []
      if (data.tags?.length) tagsInput.value = data.tags.join(', ')

      // Load shipping overrides → 转换为 shippingRules 格式
      try {
        const { data: overrides } = await getProductShippingOverrides(route.params.id)
        if (overrides.length > 0) {
          // 有自定义覆盖 → 使用自定义模式
          shippingMode.value = 'custom'
          shippingRules.value = overrides.map(o => ({
            origin_country_code: form.origin_country_code || '',
            destination_country_code: o.country_code,
            shipping_method_id: o.shipping_method_id,
            fee: o.override_base_fee ? Number(o.override_base_fee) : null,
            is_disabled: Boolean(o.is_disabled),
            defaultFee: getGlobalFee(o.country_code, o.shipping_method_id),
          }))
        }
      } catch {}

      // Load shipping notes
      try {
        const { data: notes } = await getProductShippingNotes(route.params.id)
        shippingNotes.value = notes.map(n => ({
          id: n.id,
          title: n.title || '',
          title_en: n.title_en || '',
          content: n.content || '',
          content_en: n.content_en || '',
          sort_order: n.sort_order || 0,
          is_active: n.is_active ?? 1,
        }))
        if (shippingNotes.value.length > 0) {
          shippingNotesMode.value = 'custom'
        }
      } catch {}
    } catch {
      ElMessage.error('加载商品失败')
    } finally {
      loading.value = false
    }
  }
})

const handleFileChange = (file) => {
  fileList.value.push(file)
}

// 处理新增国家：当用户输入的国家代码不在现有列表中时，调用 API 创建
async function ensureCountryExists(code) {
  if (!code || code === '*') return
  const existing = countries.value.find(c => c.code === code)
  if (existing) return

  try {
    const { data } = await createCountry({
      code,
      name: code,
      name_en: code,
      flag_emoji: '',
      sort_order: countries.value.length + 1,
    })
    countries.value.push(data)
    ElMessage.success(`国家 ${code} 已添加到系统`)
  } catch (e) {
    // 可能已存在或其他错误，静默处理
  }
}

const handleSave = async () => {
  if (!form.title || !form.title_en || !form.category_id || !form.sale_price) {
    ElMessage.warning('请填写必填字段')
    return
  }

  form.tags = tagsInput.value.split(',').map((t) => t.trim()).filter(Boolean)

  // 处理运费覆盖配置
  let overrides = []
  if (shippingMode.value === 'custom') {
    overrides = shippingRules.value
      .filter(r => r.destination_country_code && r.shipping_method_id)
      .map(r => ({
        country_code: r.destination_country_code,
        shipping_method_id: r.shipping_method_id,
        override_base_fee: r.fee,
        override_per_kg_fee: null,
        surcharge: 0,
        is_disabled: r.is_disabled || false,
      }))
  }
  // shippingMode === 'global' → overrides 为空数组 → 清空自定义配置，使用全局规则

  // 构建 shipping notes
  const notes = shippingNotesMode.value === 'custom'
    ? shippingNotes.value
        .filter(n => n.title || n.title_en)
        .map((n, i) => ({
          title: n.title || n.title_en || 'Note',
          title_en: n.title_en || n.title || 'Note',
          content: n.content || '',
          content_en: n.content_en || '',
          sort_order: n.sort_order ?? i * 10,
          is_active: n.is_active ?? 1,
        }))
    : []

  // 确保所有使用的国家代码都存在于数据库中
  const countryCodes = [...new Set(overrides.map(r => r.country_code))]
  for (const code of countryCodes) {
    await ensureCountryExists(code)
  }

  saving.value = true
  try {
    // 构建产品数据（不包含 shipping_overrides，单独保存）
    const productData = {
      title: form.title,
      title_en: form.title_en,
      slug: form.slug,
      description: form.description,
      description_en: form.description_en,
      category_id: form.category_id,
      brand: form.brand,
      original_price: form.original_price,
      sale_price: form.sale_price,
      condition_grade: form.condition_grade,
      condition_note: form.condition_note,
      status: form.status,
      stock_quantity: form.stock_quantity,
      auto_manage_stock: form.auto_manage_stock,
      weight_kg: form.weight_kg,
      length_cm: form.length_cm,
      width_cm: form.width_cm,
      height_cm: form.height_cm,
      shipping_category: form.shipping_category,
      origin_country_code: form.origin_country_code,
      tags: form.tags,
    }

    let productId
    if (isEdit.value) {
      await updateProduct(route.params.id, productData)
      // 单独保存运费覆盖和配送说明
      await updateProductShippingOverrides(route.params.id, overrides)
      await updateProductShippingNotes(route.params.id, notes)
      productId = route.params.id
    } else {
      const { data } = await createProduct(productData)
      productId = data.id
      // 创建后保存运费覆盖和配送说明
      if (overrides.length) {
        await updateProductShippingOverrides(productId, overrides)
      }
      if (notes.length) {
        await updateProductShippingNotes(productId, notes)
      }
    }

    // 上传图片
    for (const file of fileList.value) {
      if (file.raw) {
        await uploadProductImage(productId, file.raw, file.name)
      }
    }

    ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
    router.push('/products')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}
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
.existing-images {
  margin-top: 12px;
}
.existing-images p {
  margin-bottom: 8px;
  color: #999;
  font-size: 14px;
}
.fixed-width-row {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  min-width: 800px;
  gap: 24px;
}
.fixed-width-row :deep(.el-form-item) {
  margin-bottom: 0;
  flex-shrink: 0;
}
.fixed-width-row :deep(.el-form-item__label) {
  white-space: nowrap;
}
</style>
