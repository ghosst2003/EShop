from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, DateTime, Enum,
    ForeignKey, DECIMAL, func,
)
from sqlalchemy.orm import relationship

from app.models import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # 订单号
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # 买家ID（买家自主下单时设置）
    buyer_name = Column(String(100), nullable=False)  # 买家姓名
    buyer_email = Column(String(255))  # 买家邮箱
    buyer_phone = Column(String(50))  # 买家电话
    buyer_address = Column(Text, nullable=False)  # 收货地址
    total_amount = Column(DECIMAL(10, 2), nullable=False)  # 订单总金额
    currency = Column(String(3), default="EUR", nullable=False)
    status = Column(
        Enum("pending", "paid", "shipped", "completed", "cancelled"),
        default="pending",
        nullable=False,
        index=True,
    )
    payment_method = Column(String(50))  # 支付方式
    payment_reference = Column(String(255))  # 支付参考号
    payment_intent_id = Column(String(255))  # Stripe PaymentIntent ID
    payment_status = Column(
        Enum("pending", "requires_action", "paid", "failed", "refunded"),
        default="pending",
        nullable=False,
    )
    shipping_method = Column(String(100))  # 物流方式
    shipping_price = Column(DECIMAL(10, 2))  # 运费价格
    shipping_country = Column(String(10))  # 派送国家
    tracking_number = Column(String(100))  # 物流单号
    notes = Column(Text)  # 备注
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 创建人（管理员代下单/买家自己）
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    paid_at = Column(DateTime)  # 付款时间
    shipped_at = Column(DateTime)  # 发货时间
    completed_at = Column(DateTime)  # 完成时间

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_logs = relationship("OrderStatusLog", back_populates="order", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    buyer = relationship("User", foreign_keys=[buyer_id])


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))  # 关联商品（可为空，如果商品已删除）
    product_title = Column(String(255), nullable=False)  # 商品标题快照
    product_title_en = Column(String(255))  # 英文标题快照
    quantity = Column(Integer, default=1, nullable=False)  # 数量
    unit_price = Column(DECIMAL(10, 2), nullable=False)  # 单价
    subtotal = Column(DECIMAL(10, 2), nullable=False)  # 小计
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="items")


class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(String(50))  # 原状态
    to_status = Column(String(50), nullable=False)  # 新状态
    note = Column(Text)  # 变更说明
    operator_id = Column(Integer, ForeignKey("users.id"))  # 操作人
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="status_logs")
    operator = relationship("User")
