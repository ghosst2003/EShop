"""买家订单路由 — 买家自主下单、查看自己的订单"""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.config import settings
from app.dependencies import get_current_user
from app.models import (
    User, Order, OrderItem, OrderStatusLog,
    Cart, CartItem, Product, Address, ReturnRequest, OrderRequestKey,
    OrderReservation, OrderFinancialSnapshot,
)
from app.services.email import send_order_notification
from app.services.orders import calculate_tax, money, release_reservation, tax_rate_for
from app.services.shipping import quote_cart_shipping
from app.schemas import (
    BuyerOrderCreate, BuyerOrderOut, BuyerOrderListResponse,
    OrderOut, AddressOut, ReturnRequestCreate, ReturnRequestOut,
)

router = APIRouter()


def generate_order_number() -> str:
    today = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4().hex[:6]).upper()
    return f"BC-{today}-{random_suffix}"


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    data: BuyerOrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """买家自主下单 — 从购物车创建订单"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can create orders")

    existing_key = db.query(OrderRequestKey).filter(
        OrderRequestKey.buyer_id == user.id,
        OrderRequestKey.idempotency_key == data.idempotency_key,
    ).first()
    if existing_key:
        existing_order = db.query(Order).filter(Order.id == existing_key.order_id).first()
        if existing_order:
            return OrderOut.model_validate(existing_order)

    # 获取购物车
    cart = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product)
    ).filter(Cart.buyer_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Older clients omit items and check out the whole cart. Newer clients can
    # send a product selection so unchecked items stay in the cart.
    order_cart_items = list(cart.items)
    selected_product_ids = None
    if data.items is not None:
        if not data.items:
            raise HTTPException(status_code=400, detail="Select at least one cart item")
        selected_product_ids = {item.product_id for item in data.items}
        submitted_quantities = {item.product_id: item.quantity for item in data.items}
        cart_product_ids = {item.product_id for item in cart.items}
        missing_product_ids = selected_product_ids - cart_product_ids
        if missing_product_ids:
            raise HTTPException(status_code=400, detail="One or more selected items are no longer in the cart")
        order_cart_items = [
            item for item in cart.items
            if item.product_id in selected_product_ids
        ]
        for cart_item in order_cart_items:
            if submitted_quantities[cart_item.product_id] != cart_item.quantity:
                raise HTTPException(status_code=409, detail="Cart changed. Review quantities before paying.")

    # 确定收货地址
    shipping_country = None
    if data.address_id:
        address = db.query(Address).filter(
            Address.id == data.address_id, Address.buyer_id == user.id
        ).first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        buyer_name = address.recipient_name
        buyer_email = user.email
        buyer_phone = address.phone
        buyer_address = f"{address.street_address}, {address.city}, {address.postal_code}, {address.country}"
        shipping_country = address.country.strip().upper()
    elif data.buyer_name and data.buyer_address:
        buyer_name = data.buyer_name
        buyer_email = data.buyer_email or user.email
        buyer_phone = data.buyer_phone
        buyer_address = data.buyer_address
        shipping_country = data.buyer_address.split(",")[-1].strip().upper()[:2]
    else:
        # 使用默认地址
        address = db.query(Address).filter(
            Address.buyer_id == user.id, Address.is_default == 1
        ).first()
        if not address:
            raise HTTPException(status_code=400, detail="No address provided. Please add a shipping address first.")
        buyer_name = address.recipient_name
        buyer_email = user.email
        buyer_phone = address.phone
        buyer_address = f"{address.street_address}, {address.city}, {address.postal_code}, {address.country}"
        shipping_country = address.country.strip().upper()

    # 验证商品并计算总金额
    subtotal_amount = Decimal("0")
    discounted_subtotal = Decimal("0")
    order_items = []
    coupon_code = (data.coupon_code or "").strip().upper()
    if coupon_code and coupon_code != "WELCOME10":
        raise HTTPException(status_code=400, detail="This promotion code is not valid")
    discount_rate = Decimal("0.10") if coupon_code == "WELCOME10" else Decimal("0")

    product_ids = [ci.product_id for ci in order_cart_items]
    locked_products = db.query(Product).filter(Product.id.in_(product_ids)).with_for_update().all()
    products_by_id = {product.id: product for product in locked_products}

    for ci in order_cart_items:
        product = products_by_id.get(ci.product_id)
        if not product or product.status != "active":
            raise HTTPException(status_code=400, detail=f"Product '{ci.product_title if ci.product_id else 'unknown'}' is not available")
        if product.auto_manage_stock and product.stock_quantity < ci.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.title}'")

        original_unit_price = money(product.sale_price)
        subtotal_amount += original_unit_price * ci.quantity
        unit_price = original_unit_price
        if discount_rate:
            unit_price = (unit_price * (Decimal("1") - discount_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal = unit_price * ci.quantity
        discounted_subtotal += subtotal
        order_items.append({
            "product_id": product.id,
            "product_title": product.title,
            "product_title_en": product.title_en,
            "quantity": ci.quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    # Price, shipping, promotions, and tax are all authoritative on the server.
    shipping_quote = quote_cart_shipping(db, order_cart_items, shipping_country)
    if not shipping_quote.configured:
        raise HTTPException(status_code=400, detail="Delivery is not configured for one or more items at this address")
    shipping_price = shipping_quote.total
    tax_rate = tax_rate_for(shipping_country)
    tax_amount, total_amount = calculate_tax(discounted_subtotal + shipping_price, tax_rate)
    discount_amount = money(subtotal_amount - discounted_subtotal)

    # 创建订单
    order_number = generate_order_number()
    order = Order(
        order_number=order_number,
        buyer_id=user.id,
        buyer_name=buyer_name,
        buyer_email=buyer_email,
        buyer_phone=buyer_phone,
        buyer_address=buyer_address,
        total_amount=total_amount,
        currency="EUR",
        status="pending",
        payment_method=data.payment_method,
        shipping_method=shipping_quote.method,
        shipping_price=shipping_price,
        shipping_country=shipping_country,
        notes=(f"Promotion {coupon_code} applied. " if coupon_code else "") + (data.notes or ""),
        created_by=user.id,
        payment_status="pending",
    )
    db.add(order)
    db.flush()
    db.add(OrderRequestKey(
        buyer_id=user.id,
        idempotency_key=data.idempotency_key,
        order_id=order.id,
    ))
    db.add(OrderReservation(
        order_id=order.id,
        status="reserved",
        expires_at=datetime.utcnow() + timedelta(minutes=settings.stock_reservation_minutes),
    ))
    db.add(OrderFinancialSnapshot(
        order_id=order.id,
        subtotal=money(subtotal_amount),
        discount_amount=discount_amount,
        shipping_amount=shipping_price,
        tax_amount=tax_amount,
        total_amount=total_amount,
        tax_rate=tax_rate,
        prices_include_tax=1 if settings.prices_include_tax else 0,
        coupon_code=coupon_code or None,
    ))

    # 创建订单明细 & 扣减库存
    for oi_data in order_items:
        item = OrderItem(
            order_id=order.id,
            product_id=oi_data["product_id"],
            product_title=oi_data["product_title"],
            product_title_en=oi_data["product_title_en"],
            quantity=oi_data["quantity"],
            unit_price=Decimal(str(oi_data["unit_price"])),
            subtotal=Decimal(str(oi_data["subtotal"])),
        )
        db.add(item)

        # 扣减库存
        product = products_by_id.get(oi_data["product_id"])
        if product and product.auto_manage_stock:
            product.stock_quantity -= oi_data["quantity"]
            if product.stock_quantity <= 0:
                product.status = "sold"

    # 状态日志
    log = OrderStatusLog(
        order_id=order.id,
        from_status=None,
        to_status="pending",
        note="买家下单",
        operator_id=user.id,
    )
    db.add(log)

    # Only remove the items included in this order.
    cart_items_to_delete = db.query(CartItem).filter(CartItem.cart_id == cart.id)
    if selected_product_ids is not None:
        cart_items_to_delete = cart_items_to_delete.filter(
            CartItem.product_id.in_(selected_product_ids)
        )
    cart_items_to_delete.delete(synchronize_session=False)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_key = db.query(OrderRequestKey).filter(
            OrderRequestKey.buyer_id == user.id,
            OrderRequestKey.idempotency_key == data.idempotency_key,
        ).first()
        if existing_key:
            return OrderOut.model_validate(db.query(Order).filter(Order.id == existing_key.order_id).first())
        raise
    db.refresh(order)
    send_order_notification(db, order, "order_created")

    return OrderOut.model_validate(order)


@router.get("", response_model=BuyerOrderListResponse)
def list_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看自己的订单列表"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can view orders")

    query = db.query(Order).filter(Order.buyer_id == user.id)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 加载 items
    for order in orders:
        db.refresh(order)

    return BuyerOrderListResponse(
        items=[OrderOut.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看订单详情 — 只能看自己的订单"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can view orders")

    order = db.query(Order).filter(
        Order.id == order_id, Order.buyer_id == user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderOut.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can cancel orders")
    order = db.query(Order).options(joinedload(Order.items)).filter(
        Order.id == order_id,
        Order.buyer_id == user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending" or order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="This order can no longer be cancelled online")

    if not release_reservation(db, order, "Cancelled by buyer", user.id):
        for item in order.items:
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
                if product and product.auto_manage_stock:
                    product.stock_quantity += item.quantity
                    if product.status == "sold":
                        product.status = "active"
        order.status = "cancelled"
        order.payment_status = "failed"
        db.add(OrderStatusLog(order_id=order.id, from_status="pending", to_status="cancelled", note="Cancelled by buyer", operator_id=user.id))
    db.commit()
    db.refresh(order)
    send_order_notification(db, order, "order_cancelled")
    return OrderOut.model_validate(order)


@router.post("/{order_id}/reorder")
def reorder_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can reorder")
    order = db.query(Order).options(joinedload(Order.items)).filter(
        Order.id == order_id,
        Order.buyer_id == user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    cart = db.query(Cart).filter(Cart.buyer_id == user.id).first()
    if not cart:
        cart = Cart(buyer_id=user.id)
        db.add(cart)
        db.flush()

    added = 0
    unavailable = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.status == "active").first()
        if not product or (product.auto_manage_stock and product.stock_quantity <= 0):
            unavailable.append(item.product_title_en or item.product_title)
            continue
        quantity = min(item.quantity, product.stock_quantity) if product.auto_manage_stock else item.quantity
        existing = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id,
        ).first()
        if existing:
            existing.quantity = min(
                existing.quantity + quantity,
                product.stock_quantity if product.auto_manage_stock else existing.quantity + quantity,
            )
        else:
            db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity))
        added += 1
    db.commit()
    return {"added_count": added, "unavailable": unavailable}


@router.post("/{order_id}/return-requests", response_model=ReturnRequestOut, status_code=201)
def request_return(
    order_id: int,
    data: ReturnRequestCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can request returns")
    order = db.query(Order).filter(Order.id == order_id, Order.buyer_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in ("shipped", "completed"):
        raise HTTPException(status_code=400, detail="Returns are available after an order has shipped")
    existing = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == order.id,
        ReturnRequest.buyer_id == user.id,
        ReturnRequest.status.in_(["requested", "approved"]),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A return request is already open for this order")
    request = ReturnRequest(
        order_id=order.id,
        buyer_id=user.id,
        reason=data.reason,
        details=data.details,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    send_order_notification(db, order, "return_requested")
    return request


@router.get("/{order_id}/return-request", response_model=ReturnRequestOut)
def get_return_request(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == order_id,
        ReturnRequest.buyer_id == user.id,
    ).order_by(ReturnRequest.created_at.desc()).first()
    if not request:
        raise HTTPException(status_code=404, detail="No return request found")
    return request
