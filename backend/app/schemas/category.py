from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---- Category ----
class CategoryCreate(BaseModel):
    name: str
    name_en: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    name_en: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryTree(CategoryOut):
    children: list["CategoryTree"] = []
