import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage
from html import escape

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Order, OrderNotification


logger = logging.getLogger(__name__)

EVENT_COPY = {
    "order_created": ("We received your order", "Your items are reserved while you complete payment."),
    "payment_received": ("Payment received", "Your payment is confirmed and we are preparing your order."),
    "payment_failed": ("Payment window ended", "Payment was not completed and the reserved stock has been released."),
    "order_shipped": ("Your order is on its way", "Your order has shipped."),
    "order_completed": ("Order delivered", "Your order is complete. Thank you for shopping with BeCool."),
    "order_cancelled": ("Order cancelled", "Your order has been cancelled."),
    "return_requested": ("Return request received", "We received your return request and will review it shortly."),
    "return_approved": ("Return approved", "Your return has been approved. Follow the return instructions provided by support."),
    "return_rejected": ("Return request update", "Your return request could not be approved. Contact support if you need help."),
    "refund_completed": ("Refund issued", "Your refund has been sent to the original payment method."),
}


def send_order_notification(db: Session, order: Order, event: str) -> bool:
    """Send once per lifecycle event. SMTP failures are recorded and never break commerce flows."""
    recipient = (order.buyer_email or "").strip()
    if not recipient or event not in EVENT_COPY:
        return False

    notification = db.query(OrderNotification).filter(
        OrderNotification.order_id == order.id,
        OrderNotification.event == event,
    ).first()
    if notification and notification.status == "sent":
        return True
    if not notification:
        notification = OrderNotification(
            order_id=order.id,
            event=event,
            recipient=recipient,
        )
        db.add(notification)
        db.flush()

    notification.attempts += 1
    if not settings.smtp_host or not settings.smtp_from_email:
        notification.status = "skipped"
        notification.last_error = "SMTP is not configured"
        db.commit()
        return False

    subject, message = EVENT_COPY[event]
    order_url = f"{settings.frontend_url.rstrip('/')}/my-orders/{order.id}"
    email = EmailMessage()
    email["From"] = settings.smtp_from_email
    email["To"] = recipient
    email["Subject"] = f"{subject} · {order.order_number}"
    email.set_content(
        f"{subject}\n\n{message}\n\nOrder: {order.order_number}\n"
        f"Total: {order.currency} {order.total_amount}\nView order: {order_url}"
    )
    email.add_alternative(
        "<div style='font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#183f35'>"
        "<div style='font:700 28px Georgia,serif;margin-bottom:20px'>BeCool Market</div>"
        f"<h1 style='font:700 24px Georgia,serif'>{escape(subject)}</h1>"
        f"<p style='line-height:1.6'>{escape(message)}</p>"
        f"<p><strong>Order</strong> {escape(order.order_number)}<br>"
        f"<strong>Total</strong> {escape(order.currency)} {escape(str(order.total_amount))}</p>"
        f"<p><a href='{escape(order_url)}' style='display:inline-block;padding:12px 18px;border-radius:999px;background:#17483b;color:#fff;text-decoration:none'>View order</a></p>"
        "</div>",
        subtype="html",
    )
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as client:
            if settings.smtp_use_tls:
                client.starttls()
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(email)
        notification.status = "sent"
        notification.last_error = None
        notification.sent_at = datetime.utcnow()
        db.commit()
        return True
    except Exception as exc:
        logger.exception("Could not send %s notification for order %s", event, order.id)
        notification.status = "failed"
        notification.last_error = str(exc)[:1000]
        db.commit()
        return False
