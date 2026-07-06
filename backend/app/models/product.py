from sqlalchemy import (
    Column, Integer, String, Text, Enum, JSON, DateTime,
    ForeignKey, DECIMAL, func,
)
from sqlalchemy.orm import relationship

from app.models import Base


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
