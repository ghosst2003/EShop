from typing import Optional

from pydantic import BaseModel


# ---- Country ----
class CountryCreate(BaseModel):
    code: str
    name: str
    name_en: str
    flag_emoji: Optional[str] = None
    sort_order: int = 0


class CountryUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    flag_emoji: Optional[str] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None


class CountryOut(BaseModel):
    id: int
    code: str
    name: str
    name_en: str
    flag_emoji: Optional[str] = None
    is_active: int
    sort_order: int

    model_config = {"from_attributes": True}
