from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ============================================================
# Banner
# ============================================================

class BannerCreate(BaseModel):
    tag: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    button_text: str = "Shop Now"
    button_link: str = "/browse"
    bg_color_from: str = "#FF5000"
    bg_color_to: str = "#FF6B35"
    is_active: bool = True
    sort_order: int = 0


class BannerUpdate(BaseModel):
    tag: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    bg_color_from: Optional[str] = None
    bg_color_to: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class BannerOut(BaseModel):
    id: int
    tag: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    button_text: str
    button_link: str
    bg_color_from: str
    bg_color_to: str
    is_active: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
