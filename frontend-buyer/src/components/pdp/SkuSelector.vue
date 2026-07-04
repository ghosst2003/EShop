<template>
  <div class="mb-4">
    <div
      v-for="(group, gIdx) in optionGroups"
      :key="gIdx"
      class="mb-3"
    >
      <div class="text-sm font-medium text-gray-900 mb-2">{{ group.label }}</div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(option, oIdx) in group.options"
          :key="oIdx"
          @click="selectOption(gIdx, oIdx)"
          :disabled="option.disabled"
          class="px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-150"
          :class="group.selected === oIdx
            ? 'border-primary bg-primary/5 text-primary'
            : option.disabled
              ? 'border-gray-200 text-gray-300 cursor-not-allowed line-through'
              : 'border-gray-200 text-gray-600 hover:border-gray-300'"
        >
          {{ option.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  // Future: full variant data. For now defaults to a single "One Size" option.
  optionGroups: {
    type: Array,
    default: () => [
      {
        label: 'Specification',
        options: [{ label: 'One Size', disabled: false }],
        selected: 0,
      },
    ],
  },
})

const emit = defineEmits(['change'])

// Local selection state
const selections = ref(props.optionGroups.map(g => g.selected || 0))

function selectOption(groupIdx, optionIdx) {
  if (props.optionGroups[groupIdx]?.options[optionIdx]?.disabled) return
  selections.value[groupIdx] = optionIdx
  emit('change', { groupIdx, optionIdx, selections: [...selections.value] })
}
</script>
