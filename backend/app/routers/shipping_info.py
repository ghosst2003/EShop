"""Public: 配送信息展示接口（退货政策、支付方式、全局设置）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GlobalReturnPolicy, ProductReturnPolicy, PaymentMethod, GlobalShippingSettings
from app.schemas import ReturnPolicyResolved, PaymentMethodOut, GlobalShippingSettingsOut

router = APIRouter()


@router.get("/return-policy/global", response_model=ReturnPolicyResolved)
def get_global_return_policy(db: Session = Depends(get_db)):
    """获取全局退货政策（买家端）"""
    policy = db.query(GlobalReturnPolicy).filter(GlobalReturnPolicy.is_active == 1).first()
    if not policy:
        policy = GlobalReturnPolicy()
    return ReturnPolicyResolved(
        return_days=policy.return_days,
        buyer_pays_return_shipping=bool(policy.buyer_pays_return_shipping),
        restocking_fee_percent=float(policy.restocking_fee_percent),
        description=policy.description,
        description_en=policy.description_en,
    )


@router.get("/return-policy/{product_id}", response_model=ReturnPolicyResolved)
def get_product_return_policy(product_id: int, db: Session = Depends(get_db)):
    """获取商品退货政策（合并全局默认 + 商品覆盖）"""
    global_policy = db.query(GlobalReturnPolicy).filter(
        GlobalReturnPolicy.is_active == 1
    ).first()
    if not global_policy:
        global_policy = GlobalReturnPolicy()

    product_policy = db.query(ProductReturnPolicy).filter(
        ProductReturnPolicy.product_id == product_id
    ).first()

    def get_val(field: str, fallback):
        if product_policy is None:
            return getattr(global_policy, field, fallback)
        val = getattr(product_policy, field, None)
        if val is None:
            return getattr(global_policy, field, fallback)
        return val

    return ReturnPolicyResolved(
        return_days=get_val("return_days", 30),
        buyer_pays_return_shipping=bool(get_val("buyer_pays_return_shipping", 1)),
        restocking_fee_percent=float(get_val("restocking_fee_percent", 0)),
        description=get_val("description", ""),
        description_en=get_val("description_en", ""),
    )


@router.get("/payment-methods", response_model=list[PaymentMethodOut])
def list_payment_methods(db: Session = Depends(get_db)):
    """获取所有启用的支付方式（买家端）"""
    return (
        db.query(PaymentMethod)
        .filter(PaymentMethod.is_active == 1)
        .order_by(PaymentMethod.sort_order)
        .all()
    )


@router.get("/shipping-settings", response_model=GlobalShippingSettingsOut)
def get_shipping_settings(db: Session = Depends(get_db)):
    """获取全局配送信息设置（买家端）"""
    settings = db.query(GlobalShippingSettings).first()
    if not settings:
        settings = GlobalShippingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings
