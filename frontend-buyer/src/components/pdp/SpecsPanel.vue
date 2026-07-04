<template>
  <div class="py-4">
    <table class="w-full text-sm">
      <tbody>
        <tr v-for="(row, idx) in rows" :key="idx" class="border-b border-gray-100">
          <td class="py-3 pr-4 text-gray-400 w-1/3 whitespace-nowrap">{{ row.key }}</td>
          <td class="py-3 text-gray-700">{{ row.value }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, default: () => ({}) },
})

const conditionLabels = {
  new: 'New', like_new: 'Like New', good: 'Good',
  fair: 'Fair', poor: 'Poor', for_parts: 'For Parts / Repair',
}

const codeToFlagEmoji = (code) => {
  if (!code || code.length !== 2) return ''
  const codePoints = code.toUpperCase().split('').map(char => 127397 + char.charCodeAt())
  return String.fromCodePoint(...codePoints)
}

const rows = computed(() => {
  const p = props.product
  const rows = []
  if (p.brand) rows.push({ key: 'Brand', value: p.brand })
  if (p.condition_grade) rows.push({ key: 'Condition', value: conditionLabels[p.condition_grade] || p.condition_grade })
  if (p.condition_note) rows.push({ key: 'Condition Note', value: p.condition_note })
  if (p.stock_quantity !== undefined) rows.push({ key: 'Stock', value: p.stock_quantity > 0 ? `${p.stock_quantity} available` : 'Out of stock' })
  if (p.origin_country_code) rows.push({ key: 'Shipping Origin', value: `${codeToFlagEmoji(p.origin_country_code)} ${p.origin_country_code}` })
  return rows
})
</script>
