"""买家订单路由 — 买家自主下单、查看自己的订单"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    User, Order, OrderItem, OrderStatusLog,
    Cart, CartItem, Product, Address,
)
from app.schemas import (
    BuyerOrderCreate, BuyerOrderOut, BuyerOrderListResponse,
    OrderOut, AddressOut,
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

    # 获取购物车
    cart = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product)
    ).filter(Cart.buyer_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 确定收货地址
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
    elif data.buyer_name and data.buyer_address:
        buyer_name = data.buyer_name
        buyer_email = data.buyer_email or user.email
        buyer_phone = data.buyer_phone
        buyer_address = data.buyer_address
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

    # 验证商品并计算总金额
    total_amount = Decimal("0")
    order_items = []

    for ci in cart.items:
        product = ci.product
        if not product or product.status != "active":
            raise HTTPException(status_code=400, detail=f"Product '{ci.product_title if ci.product_id else 'unknown'}' is not available")
        if product.auto_manage_stock and product.stock_quantity < ci.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.title}'")

        subtotal = Decimal(str(product.sale_price)) * ci.quantity
        total_amount += subtotal
        order_items.append({
            "product_id": product.id,
            "product_title": product.title,
            "product_title_en": product.title_en,
            "quantity": ci.quantity,
            "unit_price": product.sale_price,
            "subtotal": subtotal,
        })

    # 运费
    shipping_price = Decimal(str(data.shipping_price)) if data.shipping_price else Decimal("0")
    shipping_country = None
    if data.shipping_method:
        # 从地址中提取国家代码
        if data.address_id:
            addr = db.query(Address).filter(Address.id == data.address_id).first()
            if addr:
                shipping_country = addr.country[:2].upper()
        elif data.buyer_address:
            parts = data.buyer_address.split(", ")
            shipping_country = parts[-1][:2].upper() if parts else None

    # 创建订单
    order_number = generate_order_number()
    order = Order(
        order_number=order_number,
        buyer_id=user.id,
        buyer_name=buyer_name,
        buyer_email=buyer_email,
        buyer_phone=buyer_phone,
        buyer_address=buyer_address,
        total_amount=total_amount + shipping_price,
        currency="EUR",
        status="pending",
        payment_method=data.payment_method,
        shipping_method=data.shipping_method,
        shipping_price=shipping_price if shipping_price > 0 else None,
        shipping_country=shipping_country,
        notes=data.notes,
        created_by=user.id,
        payment_status="pending",
    )
    db.add(order)
    db.flush()

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
        product = db.query(Product).filter(Product.id == oi_data["product_id"]).first()
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

    # 清空购物车
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    db.commit()
    db.refresh(order)

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
