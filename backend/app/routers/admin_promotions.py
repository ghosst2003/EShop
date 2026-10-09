from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Promotion, PromotionRedemption, User


router = APIRouter()


class PromotionInput(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    label: str = Field(min_length=2, max_length=120)
    discount_type: str = "percent"
    discount_value: Decimal = Field(gt=0)
    minimum_subtotal: Decimal = Field(default=0, ge=0)
    maximum_discount: Optional[Decimal] = Field(default=None, gt=0)
    usage_limit: Optional[int] = Field(default=None, gt=0)
    per_customer_limit: int = Field(default=1, gt=0)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: bool = True


def serialize(row: Promotion, uses: int = 0):
    return {
        "id": row.id, "code": row.code, "label": row.label,
        "discount_type": row.discount_type, "discount_value": row.discount_value,
        "minimum_subtotal": row.minimum_subtotal, "maximum_discount": row.maximum_discount,
        "usage_limit": row.usage_limit, "per_customer_limit": row.per_customer_limit,
        "starts_at": row.starts_at, "ends_at": row.ends_at,
        "is_active": bool(row.is_active), "uses": uses,
        "created_at": row.created_at,
    }


@router.get("")
def list_promotions(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), _admin: User = Depends(get_current_admin),
):
    total = db.query(func.count(Promotion.id)).scalar() or 0
    rows = db.query(Promotion).order_by(Promotion.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    counts = dict(db.query(PromotionRedemption.promotion_id, func.count(PromotionRedemption.id)).group_by(PromotionRedemption.promotion_id).all())
    return {"items": [serialize(row, counts.get(row.id, 0)) for row in rows], "total": total}


@router.post("", status_code=201)
def create_promotion(data: PromotionInput, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    code = data.code.strip().upper()
    if data.discount_type not in ("percent", "fixed"):
        raise HTTPException(status_code=400, detail="discount_type must be percent or fixed")
    if data.discount_type == "percent" and data.discount_value > 100:
        raise HTTPException(status_code=400, detail="Percentage cannot exceed 100")
    if db.query(Promotion).filter(Promotion.code == code).first():
        raise HTTPException(status_code=400, detail="Promotion code already exists")
    row = Promotion(**data.model_dump(exclude={"is_active"}), code=code, is_active=1 if data.is_active else 0, created_by=admin.id)
    db.add(row); db.commit(); db.refresh(row)
    return serialize(row)


@router.put("/{promotion_id}")
def update_promotion(promotion_id: int, data: PromotionInput, db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    row = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not row: raise HTTPException(status_code=404, detail="Promotion not found")
    code = data.code.strip().upper()
    duplicate = db.query(Promotion).filter(Promotion.code == code, Promotion.id != promotion_id).first()
    if duplicate: raise HTTPException(status_code=400, detail="Promotion code already exists")
    for key, value in data.model_dump(exclude={"is_active"}).items(): setattr(row, key, value)
    row.code = code; row.is_active = 1 if data.is_active else 0
    db.commit(); db.refresh(row)
    uses = db.query(func.count(PromotionRedemption.id)).filter(PromotionRedemption.promotion_id == row.id).scalar() or 0
    return serialize(row, uses)


@router.patch("/{promotion_id}/active")
def set_active(promotion_id: int, active: bool, db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    row = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not row: raise HTTPException(status_code=404, detail="Promotion not found")
    row.is_active = 1 if active else 0; db.commit()
    return {"id": row.id, "is_active": bool(row.is_active)}

