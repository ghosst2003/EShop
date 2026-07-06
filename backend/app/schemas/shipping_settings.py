from typing import Optional
from datetime import datetime

from pydantic import BaseModel


# ============================================================
# 全局配送信息设置
# ============================================================

class GlobalShippingSettingsCreate(BaseModel):
    show_combined_shipping: bool = True
    combined_shipping_text: str = "Save on combined shipping"
    show_import_fees: bool = True
    import_fees_text: str = "Import fees may apply on delivery"
    section_title: str = "Shipping, returns, and payments"


class GlobalShippingSettingsUpdate(BaseModel):
    show_combined_shipping: Optional[bool] = None
    combined_shipping_text: Optional[str] = None
    show_import_fees: Optional[bool] = None
    import_fees_text: Optional[str] = None
    section_title: Optional[str] = None


class GlobalShippingSettingsOut(BaseModel):
    id: int
    show_combined_shipping: int
    combined_shipping_text: str
    show_import_fees: int
    import_fees_text: str
    section_title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
