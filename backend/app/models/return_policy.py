from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship

from app.models import Base


class GlobalReturnPolicy(Base):
    """全局默认退货政策"""
    __tablename__ = "global_return_policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    return_days = Column(Integer, default=30, nullable=False)  # 退货天数
    buyer_pays_return_shipping = Column(Integer, default=1, nullable=False)  # 买家付退货运费
    restocking_fee_percent = Column(DECIMAL(5, 2), default=0)  # 重新入库费百分比
    description = Column(Text)  # 详细描述（中英混合或纯英）
    description_en = Column(Text)  # 英文描述
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class ProductReturnPolicy(Base):
    """商品级别退货政策覆盖"""
    __tablename__ = "product_return_policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    return_days = Column(Integer)  # NULL = 使用全局
    buyer_pays_return_shipping = Column(Integer)  # NULL = 使用全局
    restocking_fee_percent = Column(DECIMAL(5, 2))  # NULL = 使用全局
    description = Column(Text)  # NULL = 使用全局
    description_en = Column(Text)  # NULL = 使用全局

    product = relationship("Product")
