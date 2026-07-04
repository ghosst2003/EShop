from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional["UserOut"] = None


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}


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


# ---- Product ----
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
    shipping_rules: Optional[list["ShippingRuleCreate"]] = None


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
    shipping_rules: Optional[list["ShippingRuleCreate"]] = None


class ProductImageOut(BaseModel):
    id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: int
    is_primary: int

    model_config = {"from_attributes": True}


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
    created_by: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageOut] = []
    shipping_rules: list[ShippingRuleOut] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int


class ProductStatusUpdate(BaseModel):
    status: str  # draft / active / sold / archived


# ---- GDPR ----
class GdprConsentRequest(BaseModel):
    session_id: str
    consent_type: str  # cookie / newsletter / data_processing
    consent_given: bool


class GdprDataRequest(BaseModel):
    email: str
    request_type: str  # data_export / data_deletion / rectification
    details: Optional[str] = None


class GdprRequestOut(BaseModel):
    id: int
    email: str
    request_type: str
    details: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GdprRequestStatusUpdate(BaseModel):
    status: str  # pending / in_progress / completed / rejected
    admin_notes: Optional[str] = None


# ---- Operation Log ----
class OperationLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- 订单系统 ----

class OrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_title: str
    product_title_en: Optional[str] = None
    quantity: int = 1
    unit_price: Decimal


class OrderCreate(BaseModel):
    buyer_name: str
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: str
    payment_method: Optional[str] = None
    shipping_method: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    buyer_name: Optional[str] = None
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    payment_method: Optional[str] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: Optional[int]
    product_title: str
    product_title_en: Optional[str]
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderStatusLogOut(BaseModel):
    id: int
    from_status: Optional[str]
    to_status: str
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    order_number: str
    buyer_id: Optional[int] = None
    buyer_name: str
    buyer_email: Optional[str]
    buyer_phone: Optional[str]
    buyer_address: str
    total_amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str]
    payment_reference: Optional[str]
    payment_intent_id: Optional[str] = None
    payment_status: str = "pending"
    shipping_method: Optional[str]
    shipping_price: Optional[Decimal] = None
    shipping_country: Optional[str] = None
    tracking_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]
    shipped_at: Optional[datetime]
    completed_at: Optional[datetime]
    items: List[OrderItemOut] = []
    status_logs: List[OrderStatusLogOut] = []

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: List[OrderOut]
    total: int
    page: int
    page_size: int


class OrderStats(BaseModel):
    total_orders: int
    pending_count: int
    paid_count: int
    shipped_count: int
    completed_count: int
    cancelled_count: int
    total_revenue: Decimal


# ============================================================
# 购物车
# ============================================================

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductOut] = None

    model_config = {"from_attributes": True}


class CartOut(BaseModel):
    id: int
    buyer_id: int
    items: List[CartItemOut] = []
    total_items: int = 0
    subtotal: Decimal = Decimal("0")

    model_config = {"from_attributes": True}


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


# ============================================================
# 买家下单
# ============================================================

class BuyerOrderCreate(BaseModel):
    """买家自主下单请求体"""
    address_id: Optional[int] = None  # 使用已保存的地址
    buyer_name: Optional[str] = None  # 如果不使用地址，直接提供
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    payment_method: str = "stripe"
    shipping_method: Optional[str] = None
    shipping_price: Optional[float] = None
    notes: Optional[str] = None


class BuyerOrderOut(BaseModel):
    """买家下单响应"""
    id: int
    order_number: str
    total_amount: Decimal
    currency: str
    status: str
    payment_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BuyerOrderListResponse(BaseModel):
    items: List[OrderOut]
    total: int
    page: int
    page_size: int


# ============================================================
# 支付
# ============================================================

class CheckoutSessionCreate(BaseModel):
    order_id: int


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class ShippingOptionOut(BaseModel):
    """买家端查询商品发往某国的可用派送方式"""
    shipping_method: str
    price: Decimal
    is_default: bool = False


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
