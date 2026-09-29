import { ref } from 'vue'

/**
 * useTabs — manages tab state for PDP detail sections
 * @param {Array} tabKeys - Array of tab key strings (e.g. ['description', 'reviews', 'specs'])
 * @param {string} defaultTab - Key of the initially active tab
 * @returns {Object} tab state and controls
 */
export function useTabs(tabKeys = [], defaultTab = '') {
  const activeTab = ref(defaultTab || tabKeys[0] || '')

  function switchTab(key) {
    if (tabKeys.includes(key)) {
      activeTab.value = key
    }
  }

  function next() {
    const idx = tabKeys.indexOf(activeTab.value)
    if (idx < tabKeys.length - 1) {
      activeTab.value = tabKeys[idx + 1]
    }
  }

  function prev() {
    const idx = tabKeys.indexOf(activeTab.value)
    if (idx > 0) {
      activeTab.value = tabKeys[idx - 1]
    }
  }

  return { activeTab, switchTab, next, prev, tabs: tabKeys }
}
