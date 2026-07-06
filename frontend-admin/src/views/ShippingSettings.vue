<template>
  <div class="shipping-settings-page">
    <h2 class="page-title">配送信息区域设置</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>Shipping Info 区域配置</span>
          <el-button type="primary" size="small" @click="save" :loading="saving">保存</el-button>
        </div>
      </template>

      <el-alert type="info" :closable="false" class="mb-4">
        此处设置商品详情页 &quot;Shipping, returns, and payments&quot; 区域的显示行为。
      </el-alert>

      <el-form :model="settings" label-width="240px">
        <el-divider content-position="left">区域标题</el-divider>

        <el-form-item label="Section Title">
          <el-input v-model="settings.section_title" />
        </el-form-item>

        <el-divider content-position="left">合并运费提示</el-divider>

        <el-form-item label='显示 "Save on combined shipping"'>
          <el-switch v-model="settings.show_combined_shipping" />
        </el-form-item>

        <el-form-item v-if="settings.show_combined_shipping" label="提示文字">
          <el-input v-model="settings.combined_shipping_text" />
        </el-form-item>

        <el-divider content-position="left">进口费用提示</el-divider>

        <el-form-item label='显示 "Import fees" 行'>
          <el-switch v-model="settings.show_import_fees" />
        </el-form-item>

        <el-form-item v-if="settings.show_import_fees" label="提示文字">
          <el-input v-model="settings.import_fees_text" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预览 -->
    <el-card class="mt-6">
      <template #header>
        <span>前端预览</span>
      </template>

      <div class="preview-container">
        <div class="preview-panel">
          <div class="preview-title">{{ settings.section_title || 'Shipping, returns, and payments' }}</div>
          <div class="preview-row">
            <span class="preview-label">Shipping:</span>
            <span class="preview-value">€5.99 Standard</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">Import fees:</span>
            <span class="preview-value">{{ settings.import_fees_text }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">Delivery:</span>
            <span class="preview-value">Estimated between 5-10 business days</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">Returns:</span>
            <span class="preview-value">30 days returns...</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">Payments:</span>
            <span class="preview-value">PayPal · G Pay · VISA · MC</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGlobalShippingSettings, updateGlobalShippingSettings } from '../api'

const settings = ref({
  section_title: 'Shipping, returns, and payments',
  show_combined_shipping: true,
  combined_shipping_text: 'Save on combined shipping',
  show_import_fees: true,
  import_fees_text: 'Import fees may apply on delivery',
})

const saving = ref(false)

async function loadSettings() {
  try {
    const { data } = await getGlobalShippingSettings()
    settings.value = {
      section_title: data.section_title,
      show_combined_shipping: !!data.show_combined_shipping,
      combined_shipping_text: data.combined_shipping_text,
      show_import_fees: !!data.show_import_fees,
      import_fees_text: data.import_fees_text,
    }
  } catch {
    ElMessage.error('加载设置失败')
  }
}

async function save() {
  saving.value = true
  try {
    await updateGlobalShippingSettings({
      section_title: settings.value.section_title,
      show_combined_shipping: settings.value.show_combined_shipping,
      combined_shipping_text: settings.value.combined_shipping_text,
      show_import_fees: settings.value.show_import_fees,
      import_fees_text: settings.value.import_fees_text,
    })
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
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
.mb-4 {
  margin-bottom: 16px;
}
.mt-6 {
  margin-top: 24px;
}
.preview-container {
  display: flex;
  justify-content: center;
}
.preview-panel {
  width: 100%;
  max-width: 500px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.preview-title {
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  border-bottom: 1px solid #e5e7eb;
}
.preview-row {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  gap: 12px;
}
.preview-row:last-child {
  border-bottom: none;
}
.preview-label {
  width: 110px;
  text-align: right;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  flex-shrink: 0;
}
.preview-value {
  font-size: 14px;
  color: #4b5563;
}
</style>
