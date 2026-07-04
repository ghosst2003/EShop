"""订单管理 - 后台 API"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem, OrderStatusLog, User, Product
from app.schemas import (
    OrderCreate, OrderUpdate, OrderStatusUpdate,
    OrderOut, OrderListResponse, OrderStats,
)
from app.dependencies import get_current_admin

router = APIRouter()


def generate_order_number() -> str:
    """生成订单号：BC-年月日-6位随机数"""
    today = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4().hex[:6]).upper()
    return f"BC-{today}-{random_suffix}"


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """获取订单列表"""
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    if keyword:
        query = query.filter(
            (Order.order_number.ilike(f"%{keyword}%")) |
            (Order.buyer_name.ilike(f"%{keyword}%")) |
            (Order.buyer_email.ilike(f"%{keyword}%"))
        )

    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    # 加载关联数据
    for order in orders:
        db.refresh(order)

    return OrderListResponse(
        items=[OrderOut.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=OrderStats)
def get_order_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """获取订单统计"""
    total = db.query(func.count(Order.id)).scalar() or 0
    pending = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
    paid = db.query(func.count(Order.id)).filter(Order.status == "paid").scalar() or 0
    shipped = db.query(func.count(Order.id)).filter(Order.status == "shipped").scalar() or 0
    completed = db.query(func.count(Order.id)).filter(Order.status == "completed").scalar() or 0
    cancelled = db.query(func.count(Order.id)).filter(Order.status == "cancelled").scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.status.in_(["paid", "shipped", "completed"])
    ).scalar() or 0

    return OrderStats(
        total_orders=total,
        pending_count=pending,
        paid_count=paid,
        shipped_count=shipped,
        completed_count=completed,
        cancelled_count=cancelled,
        total_revenue=Decimal(str(revenue)),
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return OrderOut.model_validate(order)


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """创建订单（管理员代下单）"""
    order_number = generate_order_number()

    # 计算总金额
    total_amount = Decimal("0")
    for item in data.items:
        subtotal = Decimal(str(item.unit_price)) * item.quantity
        total_amount += subtotal

    # 创建订单
    order = Order(
        order_number=order_number,
        buyer_name=data.buyer_name,
        buyer_email=data.buyer_email,
        buyer_phone=data.buyer_phone,
        buyer_address=data.buyer_address,
        total_amount=total_amount,
        payment_method=data.payment_method,
        shipping_method=data.shipping_method,
        notes=data.notes,
        status="pending",
        created_by=admin.id,
    )
    db.add(order)
    db.flush()

    # 创建订单明细
    for item_data in data.items:
        subtotal = Decimal(str(item_data.unit_price)) * item_data.quantity
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            product_title=item_data.product_title,
            product_title_en=item_data.product_title_en,
            quantity=item_data.quantity,
            unit_price=Decimal(str(item_data.unit_price)),
            subtotal=subtotal,
        )
        db.add(item)

        # 如果关联了商品，减少库存
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product:
                if product.auto_manage_stock:
                    if product.stock_quantity < item_data.quantity:
                        raise HTTPException(status_code=400, detail=f"库存不足: {product.title}")
                    product.stock_quantity -= item_data.quantity
                    if product.stock_quantity <= 0:
                        product.status = "sold"
                else:
                    product.status = "sold"

    # 记录状态变更日志
    log = OrderStatusLog(
        order_id=order.id,
        from_status=None,
        to_status="pending",
        note="订单创建",
        operator_id=admin.id,
    )
    db.add(log)

    db.commit()
    db.refresh(order)

    return OrderOut.model_validate(order)


@router.put("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """更新订单信息"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return OrderOut.model_validate(order)


@router.post("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    valid_transitions = {
        "pending": ["paid", "cancelled"],
        "paid": ["shipped", "cancelled"],
        "shipped": ["completed"],
    }

    if order.status not in valid_transitions:
        raise HTTPException(status_code=400, detail=f"订单状态 '{order.status}' 不可变更")

    if data.status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"不能从 '{order.status}' 变更为 '{data.status}'"
        )

    old_status = order.status
    order.status = data.status

    # 更新时间戳
    now = datetime.now()
    if data.status == "paid":
        order.paid_at = now
    elif data.status == "shipped":
        order.shipped_at = now
    elif data.status == "completed":
        order.completed_at = now

    # 记录日志
    log = OrderStatusLog(
        order_id=order.id,
        from_status=old_status,
        to_status=data.status,
        note=data.note,
        operator_id=admin.id,
    )
    db.add(log)

    db.commit()
    db.refresh(order)
    return OrderOut.model_validate(order)


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status not in ["pending", "cancelled"]:
        raise HTTPException(status_code=400, detail="只能删除待处理或已取消的订单")

    db.delete(order)
    db.commit()
