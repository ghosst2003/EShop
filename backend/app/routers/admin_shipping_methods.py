"""Admin: 全局派送方式管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, ShippingMethod, ShippingMethodCountry
from app.schemas import ShippingMethodCreate, ShippingMethodUpdate, ShippingMethodOut

router = APIRouter()


@router.get("", response_model=list[ShippingMethodOut])
def list_shipping_methods(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取所有派送方式（含各国定价）"""
    return db.query(ShippingMethod).options(
        joinedload(ShippingMethod.country_rules)
    ).order_by(ShippingMethod.sort_order).all()


@router.post("", response_model=ShippingMethodOut)
def create_shipping_method(
    data: ShippingMethodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """新增派送方式（含各国定价）"""
    existing = db.query(ShippingMethod).filter(ShippingMethod.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"派送方式代码 {data.code} 已存在")

    method = ShippingMethod(
        code=data.code,
        name=data.name,
        name_en=data.name_en,
        description=data.description,
        sort_order=data.sort_order,
    )
    db.add(method)
    db.commit()
    db.refresh(method)

    # 创建各国定价
    for country_data in data.countries:
        rule = ShippingMethodCountry(
            shipping_method_id=method.id,
            country_code=country_data.country_code,
            base_fee=country_data.base_fee,
            per_kg_fee=country_data.per_kg_fee,
            min_weight_kg=country_data.min_weight_kg,
            max_weight_kg=country_data.max_weight_kg,
            estimated_days_min=country_data.estimated_days_min,
            estimated_days_max=country_data.estimated_days_max,
            is_default=1 if country_data.is_default else 0,
        )
        db.add(rule)
    db.commit()

    db.refresh(method)
    return method


@router.put("/{method_id}", response_model=ShippingMethodOut)
def update_shipping_method(
    method_id: int,
    data: ShippingMethodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新派送方式"""
    method = db.query(ShippingMethod).filter(ShippingMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Shipping method not found")

    for field, value in data.model_dump(exclude_unset=True, exclude={"countries"}).items():
        setattr(method, field, value)

    # 如果有新的国家定价，全量替换
    if data.countries is not None:
        db.query(ShippingMethodCountry).filter(
            ShippingMethodCountry.shipping_method_id == method_id
        ).delete()
        for country_data in data.countries:
            rule = ShippingMethodCountry(
                shipping_method_id=method_id,
                country_code=country_data.country_code,
                base_fee=country_data.base_fee,
                per_kg_fee=country_data.per_kg_fee,
                min_weight_kg=country_data.min_weight_kg,
                max_weight_kg=country_data.max_weight_kg,
                estimated_days_min=country_data.estimated_days_min,
                estimated_days_max=country_data.estimated_days_max,
                is_default=1 if country_data.is_default else 0,
            )
            db.add(rule)

    db.commit()
    db.refresh(method)
    return method


@router.delete("/{method_id}")
def delete_shipping_method(
    method_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """停用派送方式（设置 is_active = 0）"""
    method = db.query(ShippingMethod).filter(ShippingMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Shipping method not found")
    method.is_active = 0
    db.commit()
    return {"message": "Shipping method deactivated"}
