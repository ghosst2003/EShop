from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Product, ProductShippingRule, ProductShippingNote
from app.schemas import ProductListResponse, ProductOut, ShippingOptionOut

router = APIRouter()


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

    # 排序
    if sort == "price_asc":
        q = q.order_by(Product.sale_price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.sale_price.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Product)
        .filter(
            Product.status == "active",
            Product.title_en.ilike(f"%{q}%"),
        )
        .options(joinedload(Product.images))
        .order_by(Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total = (
        db.query(func.count(Product.id))
        .filter(Product.status == "active", Product.title_en.ilike(f"%{q}%"))
        .scalar()
    )
    return ProductListResponse(items=results, total=total, page=page, page_size=page_size)


@router.get("/{slug}", response_model=ProductOut)
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
