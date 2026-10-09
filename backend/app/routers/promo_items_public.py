from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PromoItem
from app.schemas.promo_item import PromoItemOut

router = APIRouter()


@router.get("", response_model=list[PromoItemOut])
def get_active_promo_items(db: Session = Depends(get_db)):
    """获取所有激活的 Promo Items（供移动端首页使用）"""
    return (
        db.query(PromoItem)
        .filter(PromoItem.is_active == 1)
        .order_by(PromoItem.sort_order, PromoItem.created_at.desc())
        .all()
    )
