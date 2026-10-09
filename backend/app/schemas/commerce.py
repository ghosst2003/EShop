from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.product import PublicProductOut


class SavedProductOut(BaseModel):
    id: int
    product: PublicProductOut
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = Field(None, max_length=120)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewOut(BaseModel):
    id: int
    rating: int
    title: Optional[str]
    comment: Optional[str]
    reviewer_name: str
    verified_purchase: bool
    created_at: datetime


class ReviewsSummary(BaseModel):
    average_rating: float
    review_count: int
    rating_distribution: dict[int, int]
    reviews: list[ReviewOut]


class ReturnRequestCreate(BaseModel):
    reason: str = Field(min_length=2, max_length=80)
    details: Optional[str] = Field(None, max_length=2000)


class ReturnRequestOut(BaseModel):
    id: int
    order_id: int
    reason: str
    details: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminReturnStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = Field(None, max_length=1000)


class AdminReturnOut(ReturnRequestOut):
    buyer_id: int
    updated_at: datetime
    order_number: str
    buyer_name: str
    buyer_email: Optional[str] = None
    order_total: float
    payment_status: str
