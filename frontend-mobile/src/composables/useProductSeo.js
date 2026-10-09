const upsertMeta = (selector, attributes) => {
  let element = document.head.querySelector(selector)
  if (!element) {
    element = document.createElement('meta')
    document.head.appendChild(element)
  }
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value))
}

export const applyProductSeo = (product, canonicalUrl) => {
  const title = `${product.title_en || product.title} · BeCool Market`
  const description = String(product.description_en || product.description || 'Pre-loved, well-chosen from BeCool Market.')
    .replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 180)
  const image = product.images?.[0]?.image_url ? new URL(product.images[0].image_url, window.location.origin).href : ''
  document.title = title
  upsertMeta('meta[name="description"]', { name: 'description', content: description })
  upsertMeta('meta[property="og:title"]', { property: 'og:title', content: title })
  upsertMeta('meta[property="og:description"]', { property: 'og:description', content: description })
  upsertMeta('meta[property="og:type"]', { property: 'og:type', content: 'product' })
  upsertMeta('meta[property="og:url"]', { property: 'og:url', content: canonicalUrl })
  upsertMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: image ? 'summary_large_image' : 'summary' })
  if (image) {
    upsertMeta('meta[property="og:image"]', { property: 'og:image', content: image })
    upsertMeta('meta[name="twitter:image"]', { name: 'twitter:image', content: image })
  }
  let canonical = document.head.querySelector('link[rel="canonical"]')
  if (!canonical) { canonical = document.createElement('link'); canonical.rel = 'canonical'; document.head.appendChild(canonical) }
  canonical.href = canonicalUrl
  let jsonLd = document.head.querySelector('#product-json-ld')
  if (!jsonLd) { jsonLd = document.createElement('script'); jsonLd.id = 'product-json-ld'; jsonLd.type = 'application/ld+json'; document.head.appendChild(jsonLd) }
  jsonLd.textContent = JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product', name: product.title_en || product.title,
    description, image: image ? [image] : [], brand: product.brand ? { '@type': 'Brand', name: product.brand } : undefined,
    itemCondition: 'https://schema.org/UsedCondition', offers: { '@type': 'Offer', url: canonicalUrl,
      priceCurrency: product.currency, price: String(product.sale_price),
      availability: product.status === 'active' && (!product.auto_manage_stock || product.stock_quantity > 0) ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock' },
  })
}

export const resetProductSeo = () => {
  document.title = 'BeCool Market'
  document.head.querySelector('link[rel="canonical"]')?.remove()
  document.head.querySelector('#product-json-ld')?.remove()
  upsertMeta('meta[name="description"]', { name: 'description', content: 'Pre-loved, well-chosen pieces from BeCool Market.' })
  upsertMeta('meta[property="og:title"]', { property: 'og:title', content: 'A BeCool find' })
  upsertMeta('meta[property="og:description"]', { property: 'og:description', content: 'Pre-loved, well-chosen pieces from BeCool Market.' })
  upsertMeta('meta[property="og:type"]', { property: 'og:type', content: 'website' })
  document.head.querySelector('meta[property="og:url"]')?.remove()
  document.head.querySelector('meta[property="og:image"]')?.remove()
  document.head.querySelector('meta[name="twitter:image"]')?.remove()
  upsertMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: 'summary' })
}
