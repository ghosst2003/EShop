from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app.dependencies import get_current_admin
from app.models import CommerceEvent, Order, Product, User

public_router = APIRouter()
admin_router = APIRouter()


class EventInput(BaseModel):
    session_id: str = Field(min_length=8, max_length=128)
    event_name: str = Field(pattern="^(page_view|view_product|add_to_cart|begin_checkout|purchase|promo_applied)$")
    path: Optional[str] = Field(default=None, max_length=500)
    product_id: Optional[int] = None
    order_id: Optional[int] = None
    properties: Optional[dict] = None


@public_router.post("/events", status_code=202)
def record_event(data: EventInput, request: Request, db: Session = Depends(get_db)):
    user_id = None
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        payload = decode_access_token(authorization.split(" ", 1)[1])
        if payload and payload.get("sub"): user_id = int(payload["sub"])
    values = data.model_dump()
    if values.get("product_id") and not db.query(Product.id).filter(Product.id == values["product_id"]).first():
        values["product_id"] = None
    if values.get("order_id") and not db.query(Order.id).filter(Order.id == values["order_id"]).first():
        values["order_id"] = None
    db.add(CommerceEvent(**values, user_id=user_id)); db.commit()
    return {"accepted": True}


@admin_router.get("/summary")
def funnel_summary(days: int = 30, db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    since = datetime.utcnow() - timedelta(days=max(1, min(days, 365)))
    counts = dict(db.query(CommerceEvent.event_name, func.count(CommerceEvent.id)).filter(CommerceEvent.created_at >= since).group_by(CommerceEvent.event_name).all())
    sessions = dict(db.query(CommerceEvent.event_name, func.count(func.distinct(CommerceEvent.session_id))).filter(CommerceEvent.created_at >= since).group_by(CommerceEvent.event_name).all())
    top_products = db.query(CommerceEvent.product_id, func.count(CommerceEvent.id).label("events")).filter(CommerceEvent.created_at >= since, CommerceEvent.product_id.isnot(None), CommerceEvent.event_name == "view_product").group_by(CommerceEvent.product_id).order_by(func.count(CommerceEvent.id).desc()).limit(10).all()
    return {"days": days, "events": counts, "sessions": sessions, "top_products": [{"product_id": pid, "views": total} for pid,total in top_products]}
