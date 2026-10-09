from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
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


class ReviewModeration(Base):
    """Moderation and merchant reply kept separate for backward-compatible installs."""
    __tablename__ = "review_moderation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("product_reviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    merchant_reply = Column(Text)
    moderated_by = Column(Integer, ForeignKey("users.id"))
    moderated_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    review = relationship("ProductReview")


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


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    label = Column(String(120), nullable=False)
    discount_type = Column(String(20), default="percent", nullable=False)
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    minimum_subtotal = Column(DECIMAL(10, 2), default=0, nullable=False)
    maximum_discount = Column(DECIMAL(10, 2))
    usage_limit = Column(Integer)
    per_customer_limit = Column(Integer, default=1, nullable=False)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Integer, default=1, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class PromotionRedemption(Base):
    __tablename__ = "promotion_redemptions"
    __table_args__ = (UniqueConstraint("promotion_id", "order_id", name="uq_promotion_order"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrderShipment(Base):
    __tablename__ = "order_shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    carrier = Column(String(80), nullable=False)
    tracking_number = Column(String(120), nullable=False)
    tracking_url = Column(String(600))
    estimated_delivery_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class CommerceEvent(Base):
    __tablename__ = "commerce_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    event_name = Column(String(50), nullable=False, index=True)
    path = Column(String(500))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), index=True)
    properties = Column(JSON)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
