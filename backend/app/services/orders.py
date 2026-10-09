from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import Order, OrderReservation, OrderStatusLog, Product


MONEY = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


def tax_rate_for(country_code: str | None) -> Decimal:
    rates = {}
    for entry in settings.tax_rates.split(","):
        if ":" not in entry:
            continue
        country, value = entry.split(":", 1)
        try:
            rates[country.strip().upper()] = Decimal(value.strip())
        except Exception:
            continue
    return rates.get((country_code or "").upper(), Decimal(str(settings.default_tax_rate)))


def calculate_tax(taxable: Decimal, rate: Decimal) -> tuple[Decimal, Decimal]:
    taxable = money(taxable)
    if rate <= 0:
        return Decimal("0.00"), taxable
    if settings.prices_include_tax:
        tax = money(taxable - (taxable / (Decimal("1") + rate)))
        return tax, taxable
    tax = money(taxable * rate)
    return tax, money(taxable + tax)


def restore_order_stock(db: Session, order: Order) -> None:
    for item in order.items:
        if not item.product_id:
            continue
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if product and product.auto_manage_stock:
            product.stock_quantity += item.quantity
            if product.status == "sold" and product.stock_quantity > 0:
                product.status = "active"


def release_reservation(db: Session, order: Order, note: str, operator_id: int | None = None) -> bool:
    reservation = db.query(OrderReservation).filter(OrderReservation.order_id == order.id).with_for_update().first()
    if not reservation or reservation.status != "reserved":
        return False
    restore_order_stock(db, order)
    reservation.status = "released"
    reservation.released_at = datetime.utcnow()
    old_status = order.status
    if order.status == "pending":
        order.status = "cancelled"
    if order.payment_status != "paid":
        order.payment_status = "failed"
    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=old_status,
        to_status=order.status,
        note=note,
        operator_id=operator_id,
    ))
    return True


def capture_reservation(db: Session, order: Order) -> bool:
    reservation = db.query(OrderReservation).filter(OrderReservation.order_id == order.id).with_for_update().first()
    if not reservation or reservation.status != "reserved":
        return False
    reservation.status = "captured"
    return True


def release_expired_reservations(db: Session) -> int:
    reservations = (
        db.query(OrderReservation)
        .filter(OrderReservation.status == "reserved", OrderReservation.expires_at <= datetime.utcnow())
        .with_for_update(skip_locked=True)
        .all()
    )
    released = 0
    released_orders = []
    for reservation in reservations:
        order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == reservation.order_id).first()
        if order and release_reservation(db, order, "Inventory reservation expired before payment"):
            released += 1
            released_orders.append(order)
    if released:
        db.commit()
        from app.services.email import send_order_notification
        for order in released_orders:
            send_order_notification(db, order, "payment_failed")
    return released
