from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Order, Promotion, PromotionRedemption


MONEY = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


def get_valid_promotion(db: Session, code: str, subtotal=0, buyer_id: int | None = None) -> Promotion | None:
    normalized = (code or "").strip().upper()
    now = datetime.utcnow()
    promotion = db.query(Promotion).filter(
        Promotion.code == normalized,
        Promotion.is_active == 1,
    ).first()
    if not promotion:
        return None
    if promotion.starts_at and promotion.starts_at > now:
        return None
    if promotion.ends_at and promotion.ends_at <= now:
        return None
    if _money(subtotal) < _money(promotion.minimum_subtotal):
        raise HTTPException(status_code=400, detail=f"Spend €{_money(promotion.minimum_subtotal)} to use this promotion")
    if promotion.usage_limit is not None:
        used = db.query(func.count(PromotionRedemption.id)).join(Order).filter(PromotionRedemption.promotion_id == promotion.id, Order.status != "cancelled").scalar() or 0
        if used >= promotion.usage_limit:
            return None
    if buyer_id and promotion.per_customer_limit:
        used = db.query(func.count(PromotionRedemption.id)).join(Order).filter(
            PromotionRedemption.promotion_id == promotion.id,
            PromotionRedemption.buyer_id == buyer_id,
            Order.status != "cancelled",
        ).scalar() or 0
        if used >= promotion.per_customer_limit:
            raise HTTPException(status_code=400, detail="You have already used this promotion")
    return promotion


def promotion_discount(promotion: Promotion, subtotal) -> Decimal:
    subtotal = _money(subtotal)
    if promotion.discount_type == "fixed":
        discount = min(subtotal, _money(promotion.discount_value))
    else:
        discount = _money(subtotal * Decimal(str(promotion.discount_value)) / Decimal("100"))
    if promotion.maximum_discount is not None:
        discount = min(discount, _money(promotion.maximum_discount))
    return _money(discount)
