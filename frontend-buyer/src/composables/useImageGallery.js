import { ref, computed } from 'vue'

/**
 * useImageGallery — manages product image gallery state
 * @param {Array} images - Array of image objects with thumbnail_url/image_url
 * @returns {Object} gallery state and controls
 */
export function useImageGallery(images = []) {
  const currentIndex = ref(0)

  const imageList = computed(() => {
    if (!images?.length) return []
    return images.map(img => img.thumbnail_url || img.image_url)
  })

  const currentImage = computed(() => imageList.value[currentIndex.value] || '')

  const hasNext = computed(() => currentIndex.value < imageList.value.length - 1)
  const hasPrev = computed(() => currentIndex.value > 0)

  function next() {
    if (hasNext.value) {
      currentIndex.value++
    } else {
      currentIndex.value = 0 // loop
    }
  }

  function prev() {
    if (hasPrev.value) {
      currentIndex.value--
    } else {
      currentIndex.value = imageList.value.length - 1 // loop
    }
  }

  function goTo(index) {
    if (index >= 0 && index < imageList.value.length) {
      currentIndex.value = index
    }
  }

  function reset() {
    currentIndex.value = 0
  }

  return {
    currentIndex,
    currentImage,
    imageList,
    hasNext,
    hasPrev,
    next,
    prev,
    goTo,
    reset,
  }
}
