"""Admin return review and Stripe refund workflow."""
import os
from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Order, OrderReservation, OrderStatusLog, ReturnRequest, User
from app.schemas import AdminReturnOut, AdminReturnStatusUpdate
from app.services.email import send_order_notification
from app.services.orders import restore_order_stock


router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def serialize_return(request: ReturnRequest, order: Order) -> dict:
    return {
        "id": request.id,
        "order_id": request.order_id,
        "buyer_id": request.buyer_id,
        "reason": request.reason,
        "details": request.details,
        "status": request.status,
        "created_at": request.created_at,
        "updated_at": request.updated_at,
        "order_number": order.order_number,
        "buyer_name": order.buyer_name,
        "buyer_email": order.buyer_email,
        "order_total": float(order.total_amount),
        "payment_status": order.payment_status,
    }


@router.get("", response_model=list[AdminReturnOut])
def list_returns(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(ReturnRequest, Order).join(Order, ReturnRequest.order_id == Order.id)
    if status:
        query = query.filter(ReturnRequest.status == status)
    rows = query.order_by(desc(ReturnRequest.created_at)).all()
    return [serialize_return(request, order) for request, order in rows]


@router.post("/{return_id}/status", response_model=AdminReturnOut)
def update_return_status(
    return_id: int,
    data: AdminReturnStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    request = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).with_for_update().first()
    if not request:
        raise HTTPException(status_code=404, detail="Return request not found")
    transitions = {"requested": {"approved", "rejected"}, "approved": {"received"}}
    if data.status not in transitions.get(request.status, set()):
        raise HTTPException(status_code=400, detail=f"Cannot change return from {request.status} to {data.status}")
    request.status = data.status
    order = db.query(Order).filter(Order.id == request.order_id).first()
    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=order.status,
        to_status=order.status,
        note=f"Return {data.status}. {data.note or ''}".strip(),
        operator_id=admin.id,
    ))
    db.commit()
    db.refresh(request)
    if data.status in ("approved", "rejected"):
        send_order_notification(db, order, f"return_{data.status}")
    return serialize_return(request, order)


@router.post("/{return_id}/refund", response_model=AdminReturnOut)
def refund_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    request = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).with_for_update().first()
    if not request:
        raise HTTPException(status_code=404, detail="Return request not found")
    if request.status == "refunded":
        order = db.query(Order).filter(Order.id == request.order_id).first()
        return serialize_return(request, order)
    if request.status not in ("approved", "received"):
        raise HTTPException(status_code=400, detail="Approve the return before issuing a refund")

    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == request.order_id).with_for_update().first()
    if order.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Only a paid order can be refunded")
    payment_intent = order.payment_reference
    if not payment_intent or not payment_intent.startswith("pi_"):
        raise HTTPException(status_code=409, detail="The Stripe payment reference is missing")

    refund = stripe.Refund.create(
        payment_intent=payment_intent,
        metadata={"order_id": order.id, "return_request_id": request.id},
        idempotency_key=f"becool-return-{request.id}-full-refund-v1",
    )
    if refund.status not in ("succeeded", "pending"):
        raise HTTPException(status_code=502, detail="Stripe did not accept the refund")

    restore_order_stock(db, order)
    reservation = db.query(OrderReservation).filter(OrderReservation.order_id == order.id).first()
    if reservation:
        reservation.status = "returned"
        reservation.released_at = datetime.utcnow()
    request.status = "refunded"
    order.payment_status = "refunded"
    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=order.status,
        to_status=order.status,
        note=f"Full Stripe refund issued ({refund.id}); returned stock restored",
        operator_id=admin.id,
    ))
    db.commit()
    db.refresh(request)
    send_order_notification(db, order, "refund_completed")
    return serialize_return(request, order)
