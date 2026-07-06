from typing import Optional
from decimal import Decimal

from pydantic import BaseModel


# ============================================================
# 支付
# ============================================================

class CheckoutSessionCreate(BaseModel):
    order_id: int


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class ShippingOptionOut(BaseModel):
    """买家端查询商品发往某国的可用派送方式"""
    shipping_method: str
    price: Decimal
    is_default: bool = False
