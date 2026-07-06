from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel


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
