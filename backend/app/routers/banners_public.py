from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Banner

router = APIRouter()


@router.get("/active")
def get_active_banners(db: Session = Depends(get_db)):
    """获取当前有效的 Banner 列表（公开接口）"""
    banners = (
        db.query(Banner)
        .filter(Banner.is_active == 1)
        .order_by(Banner.sort_order, Banner.created_at.desc())
        .all()
    )
    return banners
