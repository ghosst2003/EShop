from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel


class ShippingRuleCreate(BaseModel):
    country: str
    shipping_method: str
    price: float


class ShippingRuleOut(BaseModel):
    id: int
    product_id: int
    country: str
    shipping_method: str
    price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductImageOut(BaseModel):
    id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: int
    is_primary: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    category_id: int
    title: str
    title_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: float
    currency: str = "EUR"
    condition_grade: str
    condition_note: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[list[str]] = None
    status: str = "draft"
    stock_quantity: int = 0
    auto_manage_stock: bool = True
    weight_kg: float = 0.5
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    shipping_category: str = "standard"
    origin_country_code: Optional[str] = None
    pickup_enabled: bool = False
    pickup_contact: Optional[str] = None
    pickup_payment: Optional[str] = None
    shipping_rules: Optional[list["ShippingRuleCreate"]] = None


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    title_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    condition_grade: Optional[str] = None
    condition_note: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None
    stock_quantity: Optional[int] = None
    auto_manage_stock: Optional[bool] = None
    weight_kg: Optional[float] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    shipping_category: Optional[str] = None
    origin_country_code: Optional[str] = None
    pickup_enabled: Optional[bool] = None
    pickup_contact: Optional[str] = None
    pickup_payment: Optional[str] = None
    shipping_rules: Optional[list["ShippingRuleCreate"]] = None


class ProductOut(BaseModel):
    id: int
    category_id: int
    title: str
    title_en: Optional[str] = None
    slug: str
    description: Optional[str] = None
    description_en: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: float
    currency: str
    condition_grade: str
    condition_note: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[list] = None
    status: str
    stock_quantity: int = 0
    auto_manage_stock: bool = True
    views_count: int
    weight_kg: Optional[Decimal] = None
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    shipping_category: Optional[str] = None
    origin_country_code: Optional[str] = None
    pickup_enabled: bool = False
    pickup_contact: Optional[str] = None
    pickup_payment: Optional[str] = None
    created_by: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    images: list["ProductImageOut"] = []
    shipping_rules: list["ShippingRuleOut"] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int


class ProductStatusUpdate(BaseModel):
    status: str  # draft / active / sold / archived
