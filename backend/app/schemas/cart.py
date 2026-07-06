from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.product import ProductOut


# ============================================================
# 购物车
# ============================================================

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductOut] = None

    model_config = {"from_attributes": True}


class CartOut(BaseModel):
    id: int
    buyer_id: int
    items: List[CartItemOut] = []
    total_items: int = 0
    subtotal: Decimal = Decimal("0")

    model_config = {"from_attributes": True}
