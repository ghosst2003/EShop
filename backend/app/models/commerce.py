from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.models import Base


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("buyer_id", "product_id", name="uq_wishlist_buyer_product"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product")


class ProductReview(Base):
    __tablename__ = "product_reviews"
    __table_args__ = (UniqueConstraint("buyer_id", "product_id", name="uq_review_buyer_product"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(120))
    comment = Column(Text)
    verified_purchase = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    buyer = relationship("User")


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(String(80), nullable=False)
    details = Column(Text)
    status = Column(String(30), default="requested", nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class ProductShareLink(Base):
    __tablename__ = "product_share_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product")


class OrderRequestKey(Base):
    """Maps one buyer checkout attempt to exactly one order."""
    __tablename__ = "order_request_keys"
    __table_args__ = (UniqueConstraint("buyer_id", "idempotency_key", name="uq_order_request_buyer_key"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    idempotency_key = Column(String(80), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrderReservation(Base):
    """Tracks inventory reserved while a buyer completes payment."""
    __tablename__ = "order_reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    status = Column(String(20), default="reserved", nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    released_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrderFinancialSnapshot(Base):
    """Immutable server-side calculation used to charge and audit an order."""
    __tablename__ = "order_financial_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    shipping_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    tax_rate = Column(DECIMAL(6, 4), default=0, nullable=False)
    prices_include_tax = Column(Integer, default=1, nullable=False)
    coupon_code = Column(String(50))
    pricing_version = Column(String(30), default="server-v1", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class PaymentWebhookEvent(Base):
    """Stripe event ledger. A unique event id makes webhook retries harmless."""
    __tablename__ = "payment_webhook_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(120), nullable=False)
    processed_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrderNotification(Base):
    """Delivery ledger for transactional email, unique per order lifecycle event."""
    __tablename__ = "order_notifications"
    __table_args__ = (UniqueConstraint("order_id", "event", name="uq_order_notification_event"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    event = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
