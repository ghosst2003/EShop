from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PromoItemCreate(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    icon: Optional[str] = ""
    image_url: Optional[str] = ""
    tag: Optional[str] = ""
    tag_class: Optional[str] = ""
    link_url: Optional[str] = ""
    product_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0


class PromoItemUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    tag: Optional[str] = None
    tag_class: Optional[str] = None
    link_url: Optional[str] = None
    product_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class PromoItemOut(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = ""
    icon: Optional[str] = ""
    image_url: Optional[str] = ""
    tag: Optional[str] = ""
    tag_class: Optional[str] = ""
    link_url: Optional[str] = ""
    product_id: Optional[int] = None
    is_active: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
