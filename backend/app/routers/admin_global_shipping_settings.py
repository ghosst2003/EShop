"""Admin: 全局配送信息设置"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, GlobalShippingSettings
from app.schemas import GlobalShippingSettingsCreate, GlobalShippingSettingsUpdate, GlobalShippingSettingsOut

router = APIRouter()


@router.get("", response_model=GlobalShippingSettingsOut)
def get_global_shipping_settings(
    db: Session = Depends(get_db),
):
    """获取全局配送信息设置"""
    settings = db.query(GlobalShippingSettings).first()
    if not settings:
        settings = GlobalShippingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("", response_model=GlobalShippingSettingsOut)
def update_global_shipping_settings(
    data: GlobalShippingSettingsUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """更新全局配送信息设置"""
    settings = db.query(GlobalShippingSettings).first()
    if not settings:
        settings = GlobalShippingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings
