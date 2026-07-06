from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship

from app.models import Base


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
