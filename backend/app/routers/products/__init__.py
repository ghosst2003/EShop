import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Product, ProductImage, ProductShippingRule, ProductShippingOverride, ProductShippingNote, ShippingMethod, Country, OperationLog
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductListResponse,
    ProductStatusUpdate,
    ProductImageOut,
    ShippingRuleCreate,
    ShippingRuleOut,
    ProductShippingOverrideCreate,
    ProductShippingOverrideOut,
    ProductShippingNoteCreate,
    ProductShippingNoteOut,
)
from app.utils import generate_slug, ensure_unique_slug

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _log_action(db: Session, user: User, action: str, entity_type: str, entity_id: int | None, details: dict | None):
    log = OperationLog(
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    db.commit()


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    q = db.query(Product).options(joinedload(Product.images))
    if status:
        q = q.filter(Product.status == status)
    total = q.count()
    items = q.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        # 生成唯一 slug
        if data.slug:
            base = data.slug
        else:
            base = generate_slug(data.title_en or data.title)
        existing = {s[0] for s in db.query(Product.slug).all()}
        slug = ensure_unique_slug(base, existing)

        # 验证发货地国家是否存在
        if data.origin_country_code:
            country = db.query(Country).filter(Country.code == data.origin_country_code.upper()).first()
            if not country:
                raise HTTPException(status_code=400, detail=f"Country '{data.origin_country_code}' not found")

        product = Product(
            category_id=data.category_id,
            title=data.title,
            title_en=data.title_en,
            slug=slug,
            description=data.description,
            description_en=data.description_en,
            original_price=data.original_price,
            sale_price=data.sale_price,
            currency=data.currency,
            condition_grade=data.condition_grade,
            condition_note=data.condition_note,
            brand=data.brand,
            tags=data.tags,
            status=data.status,
            stock_quantity=data.stock_quantity,
            auto_manage_stock=1 if data.auto_manage_stock else 0,
            origin_country_code=data.origin_country_code.upper() if data.origin_country_code else None,
            created_by=user.id,
        )
        if data.status == "active":
            from datetime import datetime
            product.published_at = datetime.utcnow()
        db.add(product)
        db.commit()

        # 处理运费规则
        if data.shipping_rules:
            for rule in data.shipping_rules:
                shipping_rule = ProductShippingRule(
                    product_id=product.id,
                    country=rule.country,
                    shipping_method=rule.shipping_method,
                    price=rule.price,
                )
                db.add(shipping_rule)
            db.commit()

        db.refresh(product)

        # 重新查询以加载关联数据（images, shipping_rules）
        product = db.query(Product).options(
            joinedload(Product.images),
            joinedload(Product.shipping_rules)
        ).filter(Product.id == product.id).first()

        _log_action(db, user, "create", "product", product.id, {"title": data.title})
        return product
    except Exception as e:
        logger.error("create_product error: %s", e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    product = db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.shipping_rules)
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True, exclude={"shipping_rules"}).items():
        setattr(product, field, value)

    # 验证发货地国家是否存在
    if data.origin_country_code is not None:
        country = db.query(Country).filter(Country.code == data.origin_country_code.upper()).first()
        if not country:
            raise HTTPException(status_code=400, detail=f"Country '{data.origin_country_code}' not found")

    # 处理运费规则：全量替换
    if data.shipping_rules is not None:
        db.query(ProductShippingRule).filter(ProductShippingRule.product_id == product_id).delete()
        for rule in data.shipping_rules:
            shipping_rule = ProductShippingRule(
                product_id=product_id,
                country=rule.country,
                shipping_method=rule.shipping_method,
                price=rule.price,
            )
            db.add(shipping_rule)
        db.commit()

    if data.status == "active" and product.published_at is None:
        from datetime import datetime
        product.published_at = datetime.utcnow()

    db.commit()
    db.refresh(product)

    # 重新查询以加载关联数据
    product = db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.shipping_rules)
    ).filter(Product.id == product_id).first()

    _log_action(db, user, "update", "product", product_id, data.model_dump(exclude_unset=True))
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = "archived"
    db.commit()
    _log_action(db, user, "delete", "product", product_id, None)
    return {"message": "Product archived"}


@router.patch("/{product_id}/status", response_model=ProductOut)
def update_status(
    product_id: int,
    data: ProductStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = data.status
    if data.status == "active" and product.published_at is None:
        from datetime import datetime
        product.published_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    _log_action(db, user, "status_change", "product", product_id, {"status": data.status})
    return product


@router.post("/{product_id}/images", response_model=ProductImageOut)
def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    alt_text: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 保存文件
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    content = file.file.read()
    filepath.write_bytes(content)

    image = ProductImage(
        product_id=product_id,
        image_url=f"/uploads/products/{filename}",
        alt_text=alt_text,
        sort_order=product.images[-1].sort_order + 1 if product.images else 0,
        is_primary=0 if product.images else 1,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    _log_action(db, user, "upload_image", "product_image", product_id, {"filename": filename})
    return image


@router.delete("/{product_id}/images/{image_id}")
def delete_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image = (
        db.query(ProductImage)
        .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
        .first()
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(image)
    db.commit()
    _log_action(db, user, "delete_image", "product_image", image_id, None)
    return {"message": "Image deleted"}


@router.get("/{product_id}/shipping-rules", response_model=list[ShippingRuleOut])
def get_shipping_rules(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取商品的运费规则"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.shipping_rules


@router.put("/{product_id}/shipping-rules", response_model=list[ShippingRuleOut])
def update_shipping_rules(
    product_id: int,
    rules: list[ShippingRuleCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """批量更新商品的运费规则（全量替换）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.query(ProductShippingRule).filter(ProductShippingRule.product_id == product_id).delete()
    for rule in rules:
        shipping_rule = ProductShippingRule(
            product_id=product_id,
            country=rule.country,
            shipping_method=rule.shipping_method,
            price=rule.price,
        )
        db.add(shipping_rule)
    db.commit()
    _log_action(db, user, "update_shipping", "product", product_id, {"rules_count": len(rules)})
    return product.shipping_rules


# ---- Product Shipping Overrides (New System) ----

@router.get("/{product_id}/shipping-overrides", response_model=list[ProductShippingOverrideOut])
def get_shipping_overrides(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取商品的运费覆盖配置"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    overrides = (
        db.query(ProductShippingOverride)
        .join(ShippingMethod)
        .filter(ProductShippingOverride.product_id == product_id)
        .all()
    )
    result = []
    for o in overrides:
        result.append(ProductShippingOverrideOut(
            id=o.id,
            product_id=o.product_id,
            country_code=o.country_code,
            shipping_method_id=o.shipping_method_id,
            override_base_fee=o.override_base_fee,
            override_per_kg_fee=o.override_per_kg_fee,
            surcharge=o.surcharge,
            is_disabled=o.is_disabled,
            method_name=o.method.name,
        ))
    return result


@router.put("/{product_id}/shipping-overrides", response_model=list[ProductShippingOverrideOut])
def update_shipping_overrides(
    product_id: int,
    overrides: list[ProductShippingOverrideCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """批量更新商品的运费覆盖配置（全量替换）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.query(ProductShippingOverride).filter(
        ProductShippingOverride.product_id == product_id
    ).delete()

    for o_data in overrides:
        override = ProductShippingOverride(
            product_id=product_id,
            country_code=o_data.country_code,
            shipping_method_id=o_data.shipping_method_id,
            override_base_fee=o_data.override_base_fee,
            override_per_kg_fee=o_data.override_per_kg_fee,
            surcharge=o_data.surcharge,
            is_disabled=1 if o_data.is_disabled else 0,
        )
        db.add(override)

    db.commit()
    _log_action(db, user, "update_shipping_overrides", "product", product_id, {"rules_count": len(overrides)})
    return get_shipping_overrides(product_id, db, user)


# ============================================================
# 商品配送说明
# ============================================================

@router.get("/{product_id}/shipping-notes", response_model=list[ProductShippingNoteOut])
def get_shipping_notes(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    notes = (
        db.query(ProductShippingNote)
        .filter(ProductShippingNote.product_id == product_id)
        .order_by(ProductShippingNote.sort_order, ProductShippingNote.id)
        .all()
    )
    return notes


@router.put("/{product_id}/shipping-notes", response_model=list[ProductShippingNoteOut])
def update_shipping_notes(
    product_id: int,
    notes: list[ProductShippingNoteCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 全量替换：先删除旧的，再插入新的
    db.query(ProductShippingNote).filter(
        ProductShippingNote.product_id == product_id
    ).delete()

    for n_data in notes:
        note = ProductShippingNote(
            product_id=product_id,
            title=n_data.title,
            title_en=n_data.title_en,
            content=n_data.content,
            content_en=n_data.content_en,
            sort_order=n_data.sort_order,
            is_active=n_data.is_active,
        )
        db.add(note)

    db.commit()
    _log_action(db, user, "update_shipping_notes", "product", product_id, {"notes_count": len(notes)})
    return get_shipping_notes(product_id, db, user)
