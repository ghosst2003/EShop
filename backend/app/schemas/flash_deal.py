from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel


# ============================================================
# 闪购 / Flash Deals
# ============================================================

class FlashDealCreate(BaseModel):
    product_id: int
    original_price: float
    deal_price: float
    start_time: datetime
    end_time: datetime
    is_active: bool = True
    sort_order: int = 0


class FlashDealUpdate(BaseModel):
    product_id: Optional[int] = None
    original_price: Optional[float] = None
    deal_price: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class FlashDealProductBrief(BaseModel):
    """嵌套在 FlashDealOut 中的商品简要信息"""
    id: int
    title: str
    title_en: Optional[str] = None
    slug: str
    image_url: Optional[str] = None
    sale_price: float
    status: str

    model_config = {"from_attributes": True}


class FlashDealOut(BaseModel):
    id: int
    product_id: int
    original_price: Decimal
    deal_price: Decimal
    start_time: datetime
    end_time: datetime
    is_active: int
    sort_order: int
    created_at: datetime
    updated_at: datetime
    product: Optional[FlashDealProductBrief] = None

    model_config = {"from_attributes": True}
