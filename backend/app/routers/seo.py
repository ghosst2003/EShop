"""Crawler-friendly product pages, share previews, sitemap, and robots."""
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Product, ProductShareLink


router = APIRouter()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _description(product: Product) -> str:
    source = product.description_en or product.description or "Pre-loved, well-chosen from BeCool Market."
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source)).strip()[:180]


def _absolute_url(value: str | None) -> str:
    if not value:
        return ""
    return urljoin(f"{settings.frontend_url.rstrip('/')}/", value.lstrip("/"))


def _mobile_index() -> str | None:
    backend_root = Path(__file__).resolve().parents[2]
    candidates = [
        backend_root / "static" / "mobile" / "index.html",
        backend_root.parent / "frontend-mobile" / "dist" / "index.html",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return None


def _product_html(product: Product, canonical_url: str) -> HTMLResponse:
    title = product.title_en or product.title
    description = _description(product)
    image = _absolute_url(product.images[0].image_url if product.images else None)
    availability = "https://schema.org/InStock" if product.status == "active" and (not product.auto_manage_stock or product.stock_quantity > 0) else "https://schema.org/OutOfStock"
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "description": description,
        "image": [image] if image else [],
        "brand": {"@type": "Brand", "name": product.brand} if product.brand else None,
        "itemCondition": "https://schema.org/UsedCondition",
        "offers": {
            "@type": "Offer",
            "url": canonical_url,
            "priceCurrency": product.currency,
            "price": str(product.sale_price),
            "availability": availability,
        },
    }
    schema = {key: value for key, value in schema.items() if value is not None}
    escaped_title = html.escape(f"{title} · BeCool Market", quote=True)
    escaped_description = html.escape(description, quote=True)
    escaped_url = html.escape(canonical_url, quote=True)
    escaped_image = html.escape(image, quote=True)
    json_ld = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    metadata = f"""
    <title>{escaped_title}</title>
    <meta name="description" content="{escaped_description}">
    <link rel="canonical" href="{escaped_url}">
    <meta property="og:type" content="product">
    <meta property="og:site_name" content="BeCool Market">
    <meta property="og:title" content="{escaped_title}">
    <meta property="og:description" content="{escaped_description}">
    <meta property="og:url" content="{escaped_url}">
    {f'<meta property="og:image" content="{escaped_image}">' if image else ''}
    <meta property="product:price:amount" content="{html.escape(str(product.sale_price))}">
    <meta property="product:price:currency" content="{html.escape(product.currency)}">
    <meta name="twitter:card" content="{'summary_large_image' if image else 'summary'}">
    <meta name="twitter:title" content="{escaped_title}">
    <meta name="twitter:description" content="{escaped_description}">
    {f'<meta name="twitter:image" content="{escaped_image}">' if image else ''}
    <script type="application/ld+json">{json_ld}</script>
    """
    index = _mobile_index()
    if index:
        # The mobile build is served by FastAPI under /mobile/assets even though
        # Vite emits root-relative asset URLs for its standalone dev server.
        index = index.replace('src="/assets/', 'src="/mobile/assets/').replace('href="/assets/', 'href="/mobile/assets/')
        return HTMLResponse(index.replace("<head>", f"<head>{metadata}", 1))
    return HTMLResponse(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">{metadata}</head>
    <body><main><h1>{html.escape(title)}</h1><p>{escaped_description}</p>
    <p>{html.escape(product.currency)} {html.escape(str(product.sale_price))}</p></main></body></html>""")


@router.get("/products/{slug}", response_class=HTMLResponse, include_in_schema=False)
def product_page(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).options(joinedload(Product.images)).filter(
        Product.slug == slug, Product.status.in_(["active", "sold"]),
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    canonical = f"{settings.frontend_url.rstrip('/')}/products/{product.slug}"
    return _product_html(product, canonical)


@router.get("/p/{token}", response_class=HTMLResponse, include_in_schema=False)
def shared_product_page(token: str, db: Session = Depends(get_db)):
    link = db.query(ProductShareLink).options(
        joinedload(ProductShareLink.product).joinedload(Product.images)
    ).filter(
        ProductShareLink.token_hash == _token_hash(token),
        ProductShareLink.expires_at > datetime.utcnow(),
    ).first()
    if not link or not link.product or link.product.status not in ("active", "sold"):
        raise HTTPException(status_code=404, detail="This shared product link is invalid or expired")
    canonical = f"{settings.frontend_url.rstrip('/')}/p/{token}"
    return _product_html(link.product, canonical)


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap(db: Session = Depends(get_db)):
    products = db.query(Product.slug, Product.updated_at).filter(Product.status == "active").order_by(Product.id).all()
    base = settings.frontend_url.rstrip("/")
    urls = [f"<url><loc>{html.escape(base + '/')}</loc></url>"]
    for product in products:
        lastmod = f"<lastmod>{product.updated_at.date().isoformat()}</lastmod>" if product.updated_at else ""
        urls.append(f"<url><loc>{html.escape(base + '/products/' + product.slug)}</loc>{lastmod}</url>")
    body = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(urls) + "</urlset>"
    return Response(content=body, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots():
    base = settings.frontend_url.rstrip("/")
    return f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin/\nSitemap: {base}/sitemap.xml\n"
