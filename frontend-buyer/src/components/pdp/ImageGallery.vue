<template>
  <div>
    <ImageViewer
      :src="currentImage"
      :alt="productName"
      :current="currentIndex"
      :total="imageList.length"
      :has-prev="hasPrev"
      :has-next="hasNext"
      @prev="prev"
      @next="next"
    />

    <ThumbnailStrip
      v-if="imageList.length > 1"
      :images="imageList"
      :active-index="currentIndex"
      @select="goTo"
    />
  </div>
</template>

<script setup>
import ImageViewer from './ImageViewer.vue'
import ThumbnailStrip from './ThumbnailStrip.vue'
import { useImageGallery } from '@/composables/useImageGallery'

const props = defineProps({
  images: { type: Array, default: () => [] },
  productName: { type: String, default: '' },
})

const {
  currentIndex,
  currentImage,
  imageList,
  hasNext,
  hasPrev,
  next,
  prev,
  goTo,
} = useImageGallery(props.images)
</script>
