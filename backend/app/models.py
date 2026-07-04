from sqlalchemy import (
    Column, Integer, String, Text, Enum, JSON, DateTime,
    ForeignKey, BigInteger, DECIMAL,
    Index, func,
)
from sqlalchemy.orm import relationship

from app.database import engine

# Must be imported before Base.metadata.create_all()
from sqlalchemy.orm import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "buyer", name="user_role"), default="admin", nullable=False)
    display_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    avatar = Column(String(500))
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    products = relationship("Product", back_populates="creator")
    created_orders = relationship("Order", foreign_keys="Order.created_by", back_populates="creator")
    buyer_orders = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    cart = relationship("Cart", back_populates="buyer", uselist=False)
    addresses = relationship("Address", back_populates="buyer", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    products = relationship("Product", back_populates="category")
    children = relationship("Category", back_populates="parent", remote_side=[id])
    parent = relationship("Category", back_populates="children", remote_side=[parent_id])


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    description_en = Column(Text)
    original_price = Column(DECIMAL(10, 2))
    sale_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    condition_grade = Column(
        Enum("new", "like_new", "good", "fair", "poor", "for_parts"),
        nullable=False,
    )
    condition_note = Column(Text)
    brand = Column(String(100))
    tags = Column(JSON)
    status = Column(
        Enum("draft", "active", "sold", "archived"),
        default="draft",
        nullable=False,
    )
    stock_quantity = Column(Integer, default=0, nullable=False)
    auto_manage_stock = Column(Integer, default=1, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    # Shipping / weight fields
    weight_kg = Column(DECIMAL(10, 2), default=0.5)
    length_cm = Column(DECIMAL(10, 2))
    width_cm = Column(DECIMAL(10, 2))
    height_cm = Column(DECIMAL(10, 2))
    shipping_category = Column(String(50), default="standard")
    origin_country_code = Column(String(10), ForeignKey("countries.code"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    category = relationship("Category", back_populates="products")
    creator = relationship("User", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    shipping_rules = relationship("ProductShippingRule", back_populates="product", cascade="all, delete-orphan")
    flash_deals = relationship("FlashDeal", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    alt_text = Column(String(255))
    sort_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="images")


class ProductShippingRule(Base):
    """商品按国家的派送方式和价格配置"""
    __tablename__ = "product_shipping_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    country = Column(String(10), nullable=False)  # ISO 3166-1 alpha-2, 或 "*" 表示默认
    shipping_method = Column(String(100), nullable=False)  # 如 "DHL Standard"
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="shipping_rules")


class Country(Base):
    """国家/地区配置表"""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)  # ISO 3166-1 alpha-2
    name = Column(String(100), nullable=False)  # 中文名
    name_en = Column(String(100), nullable=False)  # 英文名
    flag_emoji = Column(String(10))  # 国旗 emoji
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class GdprConsentLog(Base):
    __tablename__ = "gdpr_consent_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(128), nullable=False)
    consent_type = Column(Enum("cookie", "newsletter", "data_processing"), nullable=False)
    consent_given = Column(Integer, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class DataDeletionRequest(Base):
    __tablename__ = "data_deletion_requests"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    request_type = Column(Enum("data_export", "data_deletion", "rectification"), nullable=False)
    details = Column(Text)
    status = Column(
        Enum("pending", "in_progress", "completed", "rejected"),
        default="pending",
        nullable=False,
    )
    admin_notes = Column(Text)
    processed_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


# ============================================================
# 订单系统
# ============================================================

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


# ============================================================
# 购物车
# ============================================================

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


# ============================================================
# 收货地址
# ============================================================

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(100))  # 如"Home", "Office"
    recipient_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    street_address = Column(Text, nullable=False)
    is_default = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="addresses")


# ============================================================
# 闪购 / Flash Deals
# ============================================================

class FlashDeal(Base):
    """限时闪购活动"""
    __tablename__ = "flash_deals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    original_price = Column(DECIMAL(10, 2), nullable=False)
    deal_price = Column(DECIMAL(10, 2), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="flash_deals")


# ============================================================
# 首页 Banner
# ============================================================

class Banner(Base):
    """首页轮播横幅"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag = Column(String(50))  # 如 "MEGA SALE"
    title = Column(String(255), nullable=False)  # 主标题
    subtitle = Column(String(255))  # 副标题/描述
    image_url = Column(String(500))  # 背景图片 URL
    button_text = Column(String(50), default="Shop Now")  # 按钮文字
    button_link = Column(String(255), default="/browse")  # 按钮链接
    bg_color_from = Column(String(20), default="#FF5000")  # 渐变起始色
    bg_color_to = Column(String(20), default="#FF6B35")  # 渐变结束色
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


# ============================================================
# 全局派送方式配置
# ============================================================

class ShippingMethod(Base):
    """全局派送方式定义（如 DHL Standard, Express）"""
    __tablename__ = "shipping_methods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    country_rules = relationship("ShippingMethodCountry", back_populates="method", cascade="all, delete-orphan")

    @property
    def countries(self):
        """别名供 Pydantic schema使用"""
        return self.country_rules


class ShippingMethodCountry(Base):
    """派送方式在各国家的定价规则"""
    __tablename__ = "shipping_method_countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id", ondelete="CASCADE"), nullable=False)
    country_code = Column(String(10), nullable=False)
    base_fee = Column(DECIMAL(10, 2), nullable=False)  # 基础运费
    per_kg_fee = Column(DECIMAL(10, 2), default=0)  # 每kg附加费
    min_weight_kg = Column(DECIMAL(10, 2), default=0.5)  # 最小计费重量
    max_weight_kg = Column(DECIMAL(10, 2))
    estimated_days_min = Column(Integer)
    estimated_days_max = Column(Integer)
    is_default = Column(Integer, default=0)

    method = relationship("ShippingMethod", back_populates="country_rules")


class ProductShippingNote(Base):
    """商品配送说明条目（按商品、按条目、中英双语）"""
    __tablename__ = "product_shipping_notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    title_en = Column(String(200))
    content = Column(Text)
    content_en = Column(Text)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)

    product = relationship("Product")


class ShippingOriginRule(Base):
    """全局发货地→目的地→运费规则（后台统一管理）"""
    __tablename__ = "shipping_origin_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin_country_code = Column(String(10), nullable=False, index=True)  # 发货国家
    destination_country_code = Column(String(10), nullable=False, index=True)  # 目的地国家
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id", ondelete="CASCADE"), nullable=False)
    fee = Column(DECIMAL(10, 2), nullable=False)  # 固定运费
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    method = relationship("ShippingMethod")
    origin_country = relationship("Country", foreign_keys=[origin_country_code], primaryjoin="ShippingOriginRule.origin_country_code == Country.code")
    destination_country = relationship("Country", foreign_keys=[destination_country_code], primaryjoin="ShippingOriginRule.destination_country_code == Country.code")


class ProductShippingOverride(Base):
    """商品级别的派送价格覆盖配置"""
    __tablename__ = "product_shipping_overrides"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    country_code = Column(String(10), nullable=False)
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id"), nullable=False)
    override_base_fee = Column(DECIMAL(10, 2))  # NULL = 使用全局价格
    override_per_kg_fee = Column(DECIMAL(10, 2))  # NULL = 使用全局价格
    surcharge = Column(DECIMAL(10, 2), default=0)  # 附加费
    is_disabled = Column(Integer, default=0)  # 禁用该方式

    product = relationship("Product")
    method = relationship("ShippingMethod")
