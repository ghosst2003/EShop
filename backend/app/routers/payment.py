"""支付路由 — Stripe Checkout 集成"""
import os
from decimal import Decimal

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Order, OrderStatusLog
from app.schemas import CheckoutSessionCreate, CheckoutSessionResponse

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter()


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    data: CheckoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建 Stripe Checkout Session"""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == data.order_id, Order.buyer_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order cannot be paid")

    # 创建 Stripe Checkout Session
    line_items = []
    for item in order.items:
        line_items.append({
            "price_data": {
                "currency": order.currency.lower(),
                "product_data": {
                    "name": item.product_title,
                    "description": f"Qty: {item.quantity}",
                },
                "unit_amount": int(float(item.unit_price) * 100),  # cents
            },
            "quantity": item.quantity,
        })

    if not line_items:
        line_items.append({
            "price_data": {
                "currency": order.currency.lower(),
                "product_data": {"name": f"Order {order.order_number}"},
                "unit_amount": int(float(order.total_amount) * 100),
            },
            "quantity": 1,
        })

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        line_items=line_items,
        mode="payment",
        success_url=f"{FRONTEND_URL}/order-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
        cancel_url=f"{FRONTEND_URL}/my-orders/{order.id}",
        metadata={"order_id": order.id},
    )

    order.payment_intent_id = session.payment_intent or session.id
    db.commit()

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """处理 Stripe Webhook 事件"""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 处理支付成功事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")

        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order and order.status == "pending":
                from datetime import datetime
                old_status = order.status
                order.status = "paid"
                order.payment_status = "paid"
                order.paid_at = datetime.now()
                order.payment_reference = session.get("payment_intent")

                log = OrderStatusLog(
                    order_id=order.id,
                    from_status=old_status,
                    to_status="paid",
                    note="Stripe 支付成功",
                )
                db.add(log)
                db.commit()

    return {"received": True}
