from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.order import OrderOut


# ============================================================
# 买家下单
# ============================================================

class BuyerOrderItemSelection(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class BuyerOrderCreate(BaseModel):
    """买家自主下单请求体"""
    items: Optional[List[BuyerOrderItemSelection]] = None
    address_id: Optional[int] = None  # 使用已保存的地址
    buyer_name: Optional[str] = None  # 如果不使用地址，直接提供
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    payment_method: str = "stripe"
    shipping_method: Optional[str] = None
    coupon_code: Optional[str] = None
    notes: Optional[str] = None
    idempotency_key: str = Field(min_length=16, max_length=80)


class BuyerOrderOut(BaseModel):
    """买家下单响应"""
    id: int
    order_number: str
    total_amount: Decimal
    currency: str
    status: str
    payment_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BuyerOrderListResponse(BaseModel):
    items: List[OrderOut]
    total: int
    page: int
    page_size: int
