<template>
  <div>
    <!-- Tab Navigation -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="flex gap-0 -mb-px">
        <button
          v-for="tab in tabDefs"
          :key="tab.key"
          @click="switchTab(tab.key)"
          class="px-6 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap"
          :class="activeTab === tab.key
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab Content with transition -->
    <Transition name="tab-fade" mode="out-in">
      <slot :name="activeTab" />
    </Transition>
  </div>
</template>

<script setup>
import { useTabs } from '@/composables/useTabs'

const props = defineProps({
  tabs: {
    type: Array,
    default: () => [
      { key: 'description', label: 'Description' },
      { key: 'reviews', label: 'Reviews' },
      { key: 'specs', label: 'Specifications' },
    ],
  },
})

const tabDefs = props.tabs
const keys = props.tabs.map(t => t.key)
const { activeTab, switchTab } = useTabs(keys, keys[0])
</script>

<style scoped>
.tab-fade-enter-active,
.tab-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.tab-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.tab-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
