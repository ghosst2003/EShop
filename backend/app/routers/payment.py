"""支付路由 — Stripe Checkout 集成"""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlparse

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.config import settings
from app.dependencies import get_current_user
from app.models import User, Order, OrderStatusLog, OrderReservation, PaymentWebhookEvent
from app.schemas import CheckoutSessionCreate, CheckoutSessionResponse
from app.services.email import send_order_notification
from app.services.orders import capture_reservation, release_reservation

stripe.api_key = settings.stripe_secret_key

router = APIRouter()


def _money_to_cents(value) -> int:
    return int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _checkout_frontend_base(request: Request) -> str:
    """Return only an allow-listed frontend origin, preserving the mobile base path."""
    configured = settings.frontend_url.rstrip("/")
    allowed_origins = {
        origin.strip().rstrip("/")
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    }
    request_origin = (request.headers.get("origin") or "").rstrip("/")
    origin = request_origin if request_origin in allowed_origins else configured
    referer_path = urlparse(request.headers.get("referer") or "").path
    return f"{origin}/mobile" if referer_path.startswith("/mobile/") else origin


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    data: CheckoutSessionCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建 Stripe Checkout Session"""
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    order = db.query(Order).options(
        joinedload(Order.items), joinedload(Order.financials), joinedload(Order.reservation)
    ).filter(Order.id == data.order_id, Order.buyer_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.transaction_mode != "online" or order.payment_method != "stripe":
        raise HTTPException(status_code=400, detail="Face-to-face orders do not use Stripe checkout")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order cannot be paid")
    if not order.reservation or order.reservation.status != "reserved":
        raise HTTPException(status_code=409, detail="Inventory reservation is no longer active")
    if order.reservation.expires_at <= datetime.utcnow():
        release_reservation(db, order, "Inventory reservation expired before payment")
        db.commit()
        send_order_notification(db, order, "payment_failed")
        raise HTTPException(status_code=409, detail="Payment window expired. Please add the items to your cart again.")

    # Charge the authoritative order total. This includes promotion, delivery and tax
    # calculations already locked into the order and avoids float rounding drift.
    total_cents = _money_to_cents(order.total_amount)
    if total_cents <= 0:
        raise HTTPException(status_code=400, detail="This order does not require a Stripe payment")
    item_units = sum(item.quantity for item in order.items)
    line_items = [{
        "price_data": {
            "currency": order.currency.lower(),
            "product_data": {
                "name": f"BeCool order {order.order_number}",
                "description": f"{item_units} item{'s' if item_units != 1 else ''}, including delivery and tax where applicable",
            },
            "unit_amount": total_cents,
        },
        "quantity": 1,
    }]

    frontend_base = _checkout_frontend_base(request)

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        line_items=line_items,
        mode="payment",
        payment_method_types=["card"],
        success_url=f"{frontend_base}/order-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
        cancel_url=f"{frontend_base}/my-orders/{order.id}",
        metadata={"order_id": str(order.id)},
        payment_intent_data={"metadata": {"order_id": str(order.id)}},
        idempotency_key=f"becool-order-{order.id}-checkout-v1",
    )

    order.payment_intent_id = session.payment_intent or session.id
    db.commit()

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """处理 Stripe Webhook 事件"""
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = settings.stripe_webhook_secret
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

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
            expected_cents = _money_to_cents(order.total_amount) if order else None
            paid = session.get("payment_status") == "paid"
            amount_matches = session.get("amount_total") == expected_cents
            currency_matches = session.get("currency") == order.currency.lower() if order else False
            if order and order.status == "pending" and paid and amount_matches and currency_matches:
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
