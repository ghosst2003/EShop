import { ref } from 'vue'
import { getCountries } from '../api'

const countriesCache = ref([])
let loaded = false

export function useCountries() {
  const loadCountries = async () => {
    if (loaded && countriesCache.value.length > 0) {
      return countriesCache.value
    }
    try {
      const { data } = await getCountries()
      countriesCache.value = data
      loaded = true
    } catch (e) {
      console.error('Failed to load countries:', e)
    }
    return countriesCache.value
  }

  const getCountryByCode = (code) => {
    return countriesCache.value.find(c => c.code === code)
  }

  const getCountryName = (code) => {
    const country = getCountryByCode(code)
    return country?.name_en || code
  }

  const codeToFlagEmoji = (code) => {
    if (!code || code.length !== 2) return ''
    const codePoints = code
      .toUpperCase()
      .split('')
      .map(char => 127397 + char.charCodeAt())
    return String.fromCodePoint(...codePoints)
  }

  const getFlagEmoji = (code) => {
    const country = getCountryByCode(code)
    if (country?.flag_emoji) return country.flag_emoji
    return codeToFlagEmoji(code)
  }

  return {
    countriesCache,
    loadCountries,
    getCountryByCode,
    getCountryName,
    getFlagEmoji,
  }
}
