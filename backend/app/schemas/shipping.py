from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel


# ---- Global Shipping Methods ----
class ShippingMethodCountryCreate(BaseModel):
    country_code: str
    base_fee: float
    per_kg_fee: float = 0
    min_weight_kg: float = 0.5
    max_weight_kg: Optional[float] = None
    estimated_days_min: Optional[int] = None
    estimated_days_max: Optional[int] = None
    is_default: bool = False


class ShippingMethodCountryOut(BaseModel):
    id: int
    shipping_method_id: int
    country_code: str
    base_fee: Decimal
    per_kg_fee: Decimal
    min_weight_kg: Optional[Decimal] = None
    max_weight_kg: Optional[Decimal] = None
    estimated_days_min: Optional[int] = None
    estimated_days_max: Optional[int] = None
    is_default: int

    model_config = {"from_attributes": True}


class ShippingMethodCreate(BaseModel):
    code: str
    name: str
    name_en: str
    description: Optional[str] = None
    sort_order: int = 0
    countries: List[ShippingMethodCountryCreate] = []


class ShippingMethodUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None
    countries: Optional[List[ShippingMethodCountryCreate]] = None


class ShippingMethodOut(BaseModel):
    id: int
    code: str
    name: str
    name_en: str
    description: Optional[str] = None
    is_active: int
    sort_order: int
    countries: List[ShippingMethodCountryOut] = []

    model_config = {"from_attributes": True}


class ProductShippingOverrideCreate(BaseModel):
    country_code: str
    shipping_method_id: int
    override_base_fee: Optional[float] = None
    override_per_kg_fee: Optional[float] = None
    surcharge: float = 0
    is_disabled: bool = False


class ProductShippingOverrideOut(BaseModel):
    id: int
    product_id: int
    country_code: str
    shipping_method_id: int
    override_base_fee: Optional[Decimal] = None
    override_per_kg_fee: Optional[Decimal] = None
    surcharge: Decimal
    is_disabled: int
    method_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ============================================================
# 全局发货地→目的地→运费规则 (Shipping Origin Rules)
# ============================================================

class ShippingOriginRuleCreate(BaseModel):
    origin_country_code: str
    destination_country_code: str
    shipping_method_id: int
    fee: float
    is_active: bool = True


class ShippingOriginRuleUpdate(BaseModel):
    fee: Optional[float] = None
    is_active: Optional[bool] = None


class ShippingOriginRuleOut(BaseModel):
    id: int
    origin_country_code: str
    origin_country_name: Optional[str] = None
    origin_flag_emoji: Optional[str] = None
    destination_country_code: str
    destination_country_name: Optional[str] = None
    destination_flag_emoji: Optional[str] = None
    shipping_method_id: int
    shipping_method_name: Optional[str] = None
    fee: Decimal
    is_active: int

    model_config = {"from_attributes": True}


# ============================================================
# 商品配送说明
# ============================================================

class ProductShippingNoteCreate(BaseModel):
    title: str
    title_en: Optional[str] = None
    content: Optional[str] = None
    content_en: Optional[str] = None
    sort_order: int = 0
    is_active: int = 1


class ProductShippingNoteOut(BaseModel):
    id: int
    product_id: int
    title: str
    title_en: Optional[str] = None
    content: Optional[str] = None
    content_en: Optional[str] = None
    sort_order: int
    is_active: int

    model_config = {"from_attributes": True}


class ShippingCalculationRequest(BaseModel):
    product_id: int
    quantity: int = 1
    destination_country: str


class ShippingOptionResult(BaseModel):
    shipping_method_id: int
    shipping_method: str
    base_fee: Decimal
    per_kg_fee: Decimal
    weight_fee: Decimal
    surcharge: Decimal
    total_fee: Decimal
    estimated_days_min: Optional[int] = None
    estimated_days_max: Optional[int] = None
    is_default: bool = False
    is_override: bool = False


class CartShippingEstimate(BaseModel):
    country_code: str
    items: List[dict]  # [{product_title, quantity, shipping_cost}]
    shipping_total: Decimal
    grand_total: Decimal
