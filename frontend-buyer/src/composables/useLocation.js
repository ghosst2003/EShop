import { ref } from 'vue'

const STORAGE_KEY = 'esh_location'
const CACHE_TTL = 24 * 60 * 60 * 1000 // 24 小时

const countryCode = ref(null)
const loading = ref(false)
const error = ref(null)

/**
 * 尝试从缓存读取
 */
function getCachedLocation() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const { code, ts } = JSON.parse(raw)
    if (Date.now() - ts < CACHE_TTL) {
      return code
    }
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
  return null
}

/**
 * 缓存国家代码
 */
function cacheLocation(code) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ code, ts: Date.now() }))
  } catch {
    // ignore
  }
}

/**
 * 通过免费 GeoIP API 获取国家代码
 */
async function detectViaGeoIP() {
  const apis = [
    {
      url: 'https://ipapi.co/json/',
      parse: (data) => data.country_code,
    },
    {
      url: 'https://ip-api.com/json/?fields=countryCode',
      parse: (data) => data.countryCode,
    },
  ]

  for (const api of apis) {
    try {
      const res = await fetch(api.url, { signal: AbortSignal.timeout(5000) })
      if (!res.ok) continue
      const data = await res.json()
      const code = api.parse(data)
      if (code && typeof code === 'string' && code.length === 2) {
        return code.toUpperCase()
      }
    } catch {
      // try next API
    }
  }
  return null
}

/**
 * 初始化位置检测
 * 优先级：缓存 > 浏览器 Geolocation > GeoIP API
 */
export async function initLocation() {
  // 1. 优先从缓存读取
  const cached = getCachedLocation()
  if (cached) {
    countryCode.value = cached
    return cached
  }

  loading.value = true
  error.value = null

  try {
    // 2. 尝试浏览器 Geolocation（需要反向地理编码，这里跳过，因为需要额外 API）
    // 浏览器 Geolocation 只返回经纬度，需要反向地理编码服务（如 Google Maps API）
    // 为了保持简单和免费，直接使用 GeoIP

    // 3. GeoIP API 检测
    const detected = await detectViaGeoIP()
    if (detected) {
      countryCode.value = detected
      cacheLocation(detected)
      return detected
    }

    error.value = 'Unable to detect location'
    return null
  } catch (e) {
    error.value = e.message
    return null
  } finally {
    loading.value = false
  }
}

/**
 * 手动设置国家代码（用户手动选择时调用）
 */
export function setLocation(code) {
  if (!code) return
  const upper = code.toUpperCase()
  countryCode.value = upper
  cacheLocation(upper)
}

/**
 * 组合式函数
 */
export function useLocation() {
  return {
    countryCode,
    loading,
    error,
    initLocation,
    setLocation,
  }
}
