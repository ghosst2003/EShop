import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, PromoItem
from app.schemas.promo_item import PromoItemCreate, PromoItemUpdate, PromoItemOut

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[PromoItemOut])
def list_promo_items(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取 Promo Items 列表"""
    return db.query(PromoItem).order_by(PromoItem.sort_order, PromoItem.created_at.desc()).all()


@router.post("", response_model=PromoItemOut)
def create_promo_item(
    data: PromoItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建 Promo Item"""
    item = PromoItem(
        title=data.title,
        subtitle=data.subtitle or "",
        icon=data.icon or "",
        image_url=data.image_url or "",
        tag=data.tag or "",
        tag_class=data.tag_class or "",
        link_url=data.link_url or "",
        product_id=data.product_id,
        is_active=1 if data.is_active else 0,
        sort_order=data.sort_order,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=PromoItemOut)
def update_promo_item(
    item_id: int,
    data: PromoItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新 Promo Item"""
    item = db.query(PromoItem).filter(PromoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Promo item not found")

    update_data = data.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = 1 if update_data["is_active"] else 0

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_promo_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除 Promo Item"""
    item = db.query(PromoItem).filter(PromoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Promo item not found")

    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
