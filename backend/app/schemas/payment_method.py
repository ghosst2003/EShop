from typing import Optional
from datetime import datetime

from pydantic import BaseModel


# ============================================================
# 支付方式
# ============================================================

class PaymentMethodCreate(BaseModel):
    code: str
    name: str
    name_en: str
    logo_url: Optional[str] = None
    color: Optional[str] = None
    text_color: Optional[str] = None
    sort_order: int = 0


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    logo_url: Optional[str] = None
    color: Optional[str] = None
    text_color: Optional[str] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None


class PaymentMethodOut(BaseModel):
    id: int
    code: str
    name: str
    name_en: str
    logo_url: Optional[str] = None
    color: Optional[str] = None
    text_color: Optional[str] = None
    is_active: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
