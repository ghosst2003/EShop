from typing import Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# ============================================================
# 退货政策
# ============================================================

class GlobalReturnPolicyCreate(BaseModel):
    return_days: int = 30
    buyer_pays_return_shipping: bool = True
    restocking_fee_percent: float = 0
    description: Optional[str] = None
    description_en: Optional[str] = None


class GlobalReturnPolicyUpdate(BaseModel):
    return_days: Optional[int] = None
    buyer_pays_return_shipping: Optional[bool] = None
    restocking_fee_percent: Optional[float] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    is_active: Optional[int] = None


class GlobalReturnPolicyOut(BaseModel):
    id: int
    return_days: int
    buyer_pays_return_shipping: int
    restocking_fee_percent: Decimal
    description: Optional[str] = None
    description_en: Optional[str] = None
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductReturnPolicyCreate(BaseModel):
    product_id: int
    return_days: Optional[int] = None
    buyer_pays_return_shipping: Optional[bool] = None
    restocking_fee_percent: Optional[float] = None
    description: Optional[str] = None
    description_en: Optional[str] = None


class ProductReturnPolicyUpdate(BaseModel):
    return_days: Optional[int] = None
    buyer_pays_return_shipping: Optional[bool] = None
    restocking_fee_percent: Optional[float] = None
    description: Optional[str] = None
    description_en: Optional[str] = None


class ProductReturnPolicyOut(BaseModel):
    id: int
    product_id: int
    return_days: Optional[int] = None
    buyer_pays_return_shipping: Optional[int] = None
    restocking_fee_percent: Optional[Decimal] = None
    description: Optional[str] = None
    description_en: Optional[str] = None

    model_config = {"from_attributes": True}


class ReturnPolicyResolved(BaseModel):
    """返回解析后的退货政策（商品级覆盖 + 全局默认合并）"""
    return_days: int
    buyer_pays_return_shipping: bool
    restocking_fee_percent: float
    description: Optional[str] = None
    description_en: Optional[str] = None
