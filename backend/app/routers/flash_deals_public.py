from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import FlashDeal, Product

router = APIRouter()


@router.get("/active")
def get_active_flash_deals(db: Session = Depends(get_db)):
    """获取当前有效的闪购列表（公开接口，无需认证）"""
    now = datetime.utcnow()
    deals = (
        db.query(FlashDeal)
        .options(joinedload(FlashDeal.product).joinedload(Product.images))
        .filter(
            FlashDeal.is_active == 1,
            FlashDeal.start_time <= now,
            FlashDeal.end_time >= now,
        )
        .order_by(FlashDeal.sort_order, FlashDeal.end_time.asc())
        .all()
    )

    result = []
    for deal in deals:
        product = deal.product
        if not product or product.status != "active":
            continue
        image_url = None
        if product.images:
            first_img = product.images[0]
            image_url = first_img.thumbnail_url or first_img.image_url
        result.append({
            "id": deal.id,
            "product_id": product.id,
            "slug": product.slug,
            "title": product.title,
            "title_en": product.title_en or product.title,
            "image_url": image_url,
            "original_price": float(deal.original_price),
            "deal_price": float(deal.deal_price),
            "discount_pct": round((1 - float(deal.deal_price) / float(deal.original_price)) * 100) if deal.original_price and float(deal.original_price) > 0 else 0,
            "end_time": deal.end_time.isoformat(),
        })

    return result
