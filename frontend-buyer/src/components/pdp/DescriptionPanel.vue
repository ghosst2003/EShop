<template>
  <div class="py-4">
    <div class="prose prose-sm max-w-none product-description" v-html="html"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  html: { type: String, default: '<p>No description available.</p>' },
})

const safeHtml = computed(() => props.html || '<p>No description available.</p>')
</script>

<style scoped>
.product-description :deep(h1),
.product-description :deep(h2),
.product-description :deep(h3) {
  font-weight: bold;
  margin: 16px 0 8px;
}
.product-description :deep(p) {
  margin-bottom: 10px;
  line-height: 1.7;
}
.product-description :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 12px 0;
}
.product-description :deep(ul),
.product-description :deep(ol) {
  padding-left: 24px;
  margin-bottom: 12px;
}
.product-description :deep(a) {
  color: #FF4400;
  text-decoration: underline;
}
.product-description :deep(blockquote) {
  border-left: 3px solid #FF4400;
  padding-left: 16px;
  color: #666;
  margin: 12px 0;
}
</style>
