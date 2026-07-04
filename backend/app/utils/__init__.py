"""
工具函数：slug 生成等
"""
import re

from unidecode import unidecode


def generate_slug(title: str, max_length: int = 80) -> str:
    """
    将商品标题转为 URL 友好的短码。
    """
    if not title or not title.strip():
        return "product"

    slug = unidecode(title).strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        return "product"

    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    return slug


def ensure_unique_slug(base_slug: str, existing_slugs: set) -> str:
    """
    保证 slug 唯一性。如果已存在，追加 -2, -3, ...
    """
    slug = base_slug
    counter = 2
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
