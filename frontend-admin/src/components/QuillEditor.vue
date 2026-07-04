<template>
  <div class="quill-editor-wrapper">
    <div :id="editorId" ref="editorContainer"></div>
    <input type="file" ref="fileInput" accept="image/png,image/jpeg,image/gif,image/webp" style="display:none" @change="handleImageUpload" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadProductImage } from '../api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  productId: { type: [Number, String], default: null },
  placeholder: { type: String, default: '在此输入内容...' },
  height: { type: String, default: '250px' },
})

const emit = defineEmits(['update:modelValue'])

const editorContainer = ref(null)
const fileInput = ref(null)
const editorId = `quill-${Math.random().toString(36).slice(2, 9)}`
let quill = null

const toolbarOptions = [
  [{ 'header': [1, 2, 3, false] }],
  ['bold', 'italic', 'underline', 'strike'],
  [{ 'color': [] }, { 'background': [] }],
  [{ 'list': 'ordered' }, { 'list': 'bullet' }],
  ['blockquote', 'link', 'image'],
  ['clean'],
]

onMounted(() => {
  if (typeof window.Quill === 'undefined') {
    ElMessage.error('Quill 编辑器加载失败，请检查网络')
    return
  }

  quill = new window.Quill(`#${editorId}`, {
    theme: 'snow',
    placeholder: props.placeholder,
    modules: {
      toolbar: {
        container: toolbarOptions,
        handlers: {
          image: imageHandler,
        }
      }
    }
  })

  // 设置编辑器高度
  const qlEditor = document.querySelector(`#${editorId} .ql-editor`)
  if (qlEditor) {
    qlEditor.style.minHeight = props.height
  }

  // 初始值
  if (props.modelValue) {
    quill.root.innerHTML = props.modelValue
  }

  // 监听内容变化
  quill.on('text-change', () => {
    emit('update:modelValue', quill.root.innerHTML)
  })
})

onBeforeUnmount(() => {
  if (quill) {
    quill = null
  }
})

// 外部更新内容
watch(() => props.modelValue, (newVal) => {
  if (quill && newVal !== quill.root.innerHTML) {
    quill.root.innerHTML = newVal || ''
  }
})

// 自定义图片上传
function imageHandler() {
  fileInput.value.click()
}

async function handleImageUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件格式
  const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的图片格式，仅支持 PNG、JPG、GIF、WebP')
    event.target.value = ''
    return
  }

  try {
    if (props.productId) {
      // 已有商品：上传到服务器
      const res = await uploadProductImage(props.productId, file)
      const imageUrl = res.data.image_url
      const range = quill.getSelection(true)
      quill.insertEmbed(range.index, 'image', imageUrl)
      quill.setSelection(range.index + 1)
      ElMessage.success('图片已上传')
    } else {
      // 新建商品：转为 base64 直接插入
      const reader = new FileReader()
      reader.onload = (e) => {
        const dataUrl = e.target.result
        const range = quill.getSelection(true)
        quill.insertEmbed(range.index, 'image', dataUrl)
        quill.setSelection(range.index + 1)
      }
      reader.readAsDataURL(file)
      ElMessage.success('图片已插入（保存商品后会自动上传到服务器）')
    }
  } catch (e) {
    ElMessage.error('图片处理失败')
  }

  event.target.value = ''
}
</script>

<style scoped>
.quill-editor-wrapper {
  width: 100%;
}
:deep(.ql-container) {
  font-size: 14px;
}
:deep(.ql-editor) {
  min-height: 200px;
}
:deep(.ql-editor img) {
  max-width: 100%;
  height: auto;
}
</style>
