"""支付路由 — Stripe Checkout 集成"""
import os
from datetime import datetime
from decimal import Decimal

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Order, OrderStatusLog, OrderReservation, PaymentWebhookEvent
from app.schemas import CheckoutSessionCreate, CheckoutSessionResponse
from app.services.email import send_order_notification
from app.services.orders import capture_reservation, release_reservation

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
        joinedload(Order.items), joinedload(Order.financials), joinedload(Order.reservation)
    ).filter(Order.id == data.order_id, Order.buyer_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order cannot be paid")
    if not order.reservation or order.reservation.status != "reserved":
        raise HTTPException(status_code=409, detail="Inventory reservation is no longer active")
    if order.reservation.expires_at <= datetime.utcnow():
        release_reservation(db, order, "Inventory reservation expired before payment")
        db.commit()
        send_order_notification(db, order, "payment_failed")
        raise HTTPException(status_code=409, detail="Payment window expired. Please add the items to your cart again.")

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

    if order.shipping_price and Decimal(str(order.shipping_price)) > 0:
        line_items.append({
            "price_data": {
                "currency": order.currency.lower(),
                "product_data": {"name": "Standard delivery"},
                "unit_amount": int(Decimal(str(order.shipping_price)) * 100),
            },
            "quantity": 1,
        })

    if order.financials and not order.financials.prices_include_tax and Decimal(str(order.financials.tax_amount)) > 0:
        line_items.append({
            "price_data": {
                "currency": order.currency.lower(),
                "product_data": {"name": "VAT"},
                "unit_amount": int(Decimal(str(order.financials.tax_amount)) * 100),
            },
            "quantity": 1,
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
        payment_intent_data={"metadata": {"order_id": order.id}},
        idempotency_key=f"becool-order-{order.id}-checkout-v1",
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

    event_id = event.get("id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Stripe event has no id")
    if db.query(PaymentWebhookEvent).filter(PaymentWebhookEvent.event_id == event_id).first():
        return {"received": True, "duplicate": True}
    db.add(PaymentWebhookEvent(event_id=event_id, event_type=event["type"]))
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return {"received": True, "duplicate": True}

    notification = None

    # 处理支付成功事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")

        if order_id:
            order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == int(order_id)).first()
            if order and order.status == "pending":
                old_status = order.status
                order.status = "paid"
                order.payment_status = "paid"
                order.paid_at = datetime.utcnow()
                order.payment_reference = session.get("payment_intent")
                capture_reservation(db, order)

                log = OrderStatusLog(
                    order_id=order.id,
                    from_status=old_status,
                    to_status="paid",
                    note="Stripe 支付成功",
                )
                db.add(log)
                notification = (order, "payment_received")

    elif event["type"] in ("checkout.session.expired", "checkout.session.async_payment_failed", "payment_intent.payment_failed"):
        payment_object = event["data"]["object"]
        order_id = payment_object.get("metadata", {}).get("order_id")
        if order_id:
            order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == int(order_id)).first()
            if order and order.status == "pending":
                release_reservation(db, order, "Payment was not completed; reserved inventory was released")
                notification = (order, "payment_failed")

    db.commit()
    if notification:
        send_order_notification(db, notification[0], notification[1])

    return {"received": True}
