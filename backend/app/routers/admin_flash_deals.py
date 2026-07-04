import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, FlashDeal, Product
from app.schemas import FlashDealCreate, FlashDealUpdate, FlashDealOut

router = APIRouter()
logger = logging.getLogger(__name__)


def _serialize_deal(deal: FlashDeal) -> dict:
    """序列化闪购对象，包含商品简要信息"""
    result = {
        "id": deal.id,
        "product_id": deal.product_id,
        "original_price": float(deal.original_price),
        "deal_price": float(deal.deal_price),
        "start_time": deal.start_time,
        "end_time": deal.end_time,
        "is_active": deal.is_active,
        "sort_order": deal.sort_order,
        "created_at": deal.created_at,
        "updated_at": deal.updated_at,
        "product": None,
    }
    if deal.product:
        image_url = None
        if deal.product.images:
            first_img = deal.product.images[0]
            image_url = first_img.thumbnail_url or first_img.image_url
        result["product"] = {
            "id": deal.product.id,
            "title": deal.product.title,
            "title_en": deal.product.title_en,
            "image_url": image_url,
            "sale_price": float(deal.product.sale_price) if deal.product.sale_price else 0,
            "status": deal.product.status,
        }
    return result


@router.get("")
def list_flash_deals(
    is_active: int | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取闪购列表"""
    q = db.query(FlashDeal).options(joinedload(FlashDeal.product).joinedload(Product.images))
    if is_active is not None:
        q = q.filter(FlashDeal.is_active == is_active)
    deals = q.order_by(FlashDeal.sort_order, FlashDeal.created_at.desc()).all()
    return [_serialize_deal(d) for d in deals]


@router.post("", response_model=FlashDealOut)
def create_flash_deal(
    data: FlashDealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建闪购"""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    deal = FlashDeal(
        product_id=data.product_id,
        original_price=data.original_price,
        deal_price=data.deal_price,
        start_time=data.start_time,
        end_time=data.end_time,
        is_active=1 if data.is_active else 0,
        sort_order=data.sort_order,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    deal = db.query(FlashDeal).options(joinedload(FlashDeal.product)).filter(FlashDeal.id == deal.id).first()
    return deal


@router.get("/{deal_id}")
def get_flash_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取闪购详情"""
    deal = db.query(FlashDeal).options(joinedload(FlashDeal.product).joinedload(Product.images)).filter(FlashDeal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Flash deal not found")
    return _serialize_deal(deal)


@router.put("/{deal_id}")
def update_flash_deal(
    deal_id: int,
    data: FlashDealUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新闪购"""
    deal = db.query(FlashDeal).filter(FlashDeal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Flash deal not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "is_active":
            setattr(deal, field, 1 if value else 0)
        else:
            setattr(deal, field, value)

    db.commit()
    db.refresh(deal)

    deal = db.query(FlashDeal).options(joinedload(FlashDeal.product).joinedload(Product.images)).filter(FlashDeal.id == deal_id).first()
    return _serialize_deal(deal)


@router.delete("/{deal_id}")
def delete_flash_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除闪购"""
    deal = db.query(FlashDeal).filter(FlashDeal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Flash deal not found")
    db.delete(deal)
    db.commit()
    return {"message": "Flash deal deleted"}
