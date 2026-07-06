from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ============================================================
# 收货地址
# ============================================================

class AddressCreate(BaseModel):
    label: Optional[str] = None
    recipient_name: str
    phone: str
    country: str
    city: str
    postal_code: str
    street_address: str
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street_address: Optional[str] = None
    is_default: Optional[bool] = None


class AddressOut(BaseModel):
    id: int
    label: Optional[str] = None
    recipient_name: str
    phone: str
    country: str
    city: str
    postal_code: str
    street_address: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
