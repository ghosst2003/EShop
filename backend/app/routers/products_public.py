import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.config import settings
from app.models import Product, ProductShippingRule, ProductShippingNote, ShippingMethod, ShippingMethodCountry, ShippingOriginRule, Country, ProductShareLink
from app.schemas import ProductListResponse, PublicProductOut, SharedProductOut, ShippingOptionOut

router = APIRouter()


def _share_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _public_reference(product_id: int) -> str:
    digest = hmac.new(
        settings.secret_key.encode("utf-8"),
        f"product:{product_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:10].upper()
    return f"BC-{digest}"


def _encode_cursor(created_at: datetime, product_id: int) -> str:
    payload = json.dumps(
        {"created_at": created_at.isoformat(), "id": product_id},
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
        return datetime.fromisoformat(payload["created_at"]), int(payload["id"])
    except (binascii.Error, UnicodeDecodeError, ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=400, detail="Invalid product cursor") from exc


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    condition_grade: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: Optional[str] = None,
    brand: Optional[str] = None,
    tag: Optional[str] = None,
    in_stock: bool = False,
    ships_to: Optional[str] = None,
    limit: Optional[int] = Query(None, ge=1, le=100),
    cursor: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # 只展示 active 状态的商品
    q = db.query(Product).filter(Product.status == "active").options(joinedload(Product.images))

    if category_id:
        q = q.filter(Product.category_id == category_id)
    if condition_grade:
        q = q.filter(Product.condition_grade == condition_grade)
    if price_min is not None:
        q = q.filter(Product.sale_price >= price_min)
    if price_max is not None:
        q = q.filter(Product.sale_price <= price_max)
    if brand:
        q = q.filter(Product.brand.ilike(f"%{brand}%"))
    if tag:
        q = q.filter(Product.tags.contains([tag]))
    if in_stock:
        q = q.filter((Product.auto_manage_stock == 0) | (Product.stock_quantity > 0))
    if ships_to:
        destination = ships_to.upper()
        country_exists = db.query(Country.code).filter(Country.code == destination, Country.is_active == 1).first()
        if not country_exists:
            q = q.filter(Product.id == -1)
        else:
            has_global_delivery = (
                db.query(ShippingMethodCountry.id)
                .join(ShippingMethod)
                .filter(ShippingMethodCountry.country_code == destination, ShippingMethod.is_active == 1)
                .first()
            )
            if not has_global_delivery:
                supported_origins = db.query(ShippingOriginRule.origin_country_code).join(ShippingMethod).filter(
                    ShippingOriginRule.destination_country_code == destination,
                    ShippingOriginRule.is_active == 1,
                    ShippingMethod.is_active == 1,
                )
                q = q.filter(Product.origin_country_code.in_(supported_origins))

    total = q.count()

    # 首页无限滚动使用稳定的 (created_at, id) 游标。保留 page/page_size 兼容其他页面。
    if limit is not None or cursor is not None:
        batch_size = limit or page_size
        if cursor:
            cursor_created_at, cursor_id = _decode_cursor(cursor)
            q = q.filter(
                or_(
                    Product.created_at < cursor_created_at,
                    (Product.created_at == cursor_created_at) & (Product.id < cursor_id),
                )
            )

        rows = (
            q.order_by(Product.created_at.desc(), Product.id.desc())
            .limit(batch_size + 1)
            .all()
        )
        has_more = len(rows) > batch_size
        items = rows[:batch_size]
        next_cursor = (
            _encode_cursor(items[-1].created_at, items[-1].id)
            if has_more and items
            else None
        )
        return ProductListResponse(
            items=items,
            total=total,
            page=1,
            page_size=batch_size,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    # 传统页码分页
    if sort == "price_asc":
        q = q.order_by(Product.sale_price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.sale_price.desc())
    else:
        q = q.order_by(Product.created_at.desc(), Product.id.desc())

    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    condition_grade: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: bool = False,
    ships_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(
        Product.status == "active",
        or_(Product.title_en.ilike(f"%{q}%"), Product.title.ilike(f"%{q}%"), Product.brand.ilike(f"%{q}%")),
    )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if condition_grade:
        query = query.filter(Product.condition_grade == condition_grade)
    if price_min is not None:
        query = query.filter(Product.sale_price >= price_min)
    if price_max is not None:
        query = query.filter(Product.sale_price <= price_max)
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if in_stock:
        query = query.filter((Product.auto_manage_stock == 0) | (Product.stock_quantity > 0))
    if ships_to:
        destination = ships_to.upper()
        has_global_delivery = db.query(ShippingMethodCountry.id).join(ShippingMethod).filter(
            ShippingMethodCountry.country_code == destination,
            ShippingMethod.is_active == 1,
        ).first()
        if not has_global_delivery:
            supported_origins = db.query(ShippingOriginRule.origin_country_code).join(ShippingMethod).filter(
                ShippingOriginRule.destination_country_code == destination,
                ShippingOriginRule.is_active == 1,
                ShippingMethod.is_active == 1,
            )
            query = query.filter(Product.origin_country_code.in_(supported_origins))
    total = query.count()
    if sort == "price_asc":
        query = query.order_by(Product.sale_price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.sale_price.desc())
    else:
        query = query.order_by(Product.created_at.desc(), Product.id.desc())
    results = query.options(joinedload(Product.images)).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(items=results, total=total, page=page, page_size=page_size)


@router.get("/id/{product_id}", response_model=PublicProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.id == product_id, Product.status == "active")
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/shared/{token}", response_model=SharedProductOut)
def get_shared_product(token: str, db: Session = Depends(get_db)):
    link = db.query(ProductShareLink).options(
        joinedload(ProductShareLink.product).joinedload(Product.images)
    ).filter(
        ProductShareLink.token_hash == _share_token_hash(token),
        ProductShareLink.expires_at > datetime.utcnow(),
    ).first()
    if not link or not link.product or link.product.status not in ("active", "sold"):
        raise HTTPException(status_code=404, detail="This shared product link is invalid or expired")
    link.product.views_count += 1
    db.commit()
    return {
        "product": PublicProductOut.model_validate(link.product),
        "public_reference": _public_reference(link.product.id),
    }


@router.post("/{slug}/share-link")
def create_share_link(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.query(ProductShareLink).filter(ProductShareLink.expires_at <= datetime.utcnow()).delete()
    raw_token = secrets.token_urlsafe(24)
    expires_at = datetime.utcnow() + timedelta(days=180)
    db.add(ProductShareLink(
        product_id=product.id,
        token_hash=_share_token_hash(raw_token),
        expires_at=expires_at,
    ))
    db.commit()
    return {
        "share_url": f"{settings.frontend_url.rstrip('/')}/p/{raw_token}",
        "expires_at": expires_at,
        "public_reference": _public_reference(product.id),
    }


@router.get("/{slug}", response_model=PublicProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.slug == slug, Product.status == "active")
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # 增加浏览次数
    product.views_count += 1
    db.commit()
    return product


@router.get("/{slug}/shipping-options", response_model=list[ShippingOptionOut])
def get_shipping_options(
    slug: str,
    country: str = Query(..., description="Destination country code (e.g. DE, FR)"),
    db: Session = Depends(get_db),
):
    """获取商品发往指定国家的可用派送方式和价格"""
    product = db.query(Product).filter(Product.slug == slug, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rules = (
        db.query(ProductShippingRule)
        .filter(ProductShippingRule.product_id == product.id)
        .all()
    )

    # 精确匹配优先，默认规则(*) 作为兜底
    exact = [r for r in rules if r.country == country.upper()]
    default = [r for r in rules if r.country == "*"]
    matched = exact if exact else default

    return [
        ShippingOptionOut(
            shipping_method=r.shipping_method,
            price=r.price,
            is_default=(r.country == "*"),
        )
        for r in matched
    ]


@router.get("/{slug}/shipping-notes")
def get_product_shipping_notes(
    slug: str,
    db: Session = Depends(get_db),
):
    """获取商品的配送说明条目（公开接口）"""
    product = db.query(Product).filter(Product.slug == slug, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    notes = (
        db.query(ProductShippingNote)
        .filter(
            ProductShippingNote.product_id == product.id,
            ProductShippingNote.is_active == 1,
        )
        .order_by(ProductShippingNote.sort_order, ProductShippingNote.id)
        .all()
    )
    return [
        {
            "id": n.id,
            "title": n.title,
            "title_en": n.title_en,
            "content": n.content,
            "content_en": n.content_en,
        }
        for n in notes
    ]
