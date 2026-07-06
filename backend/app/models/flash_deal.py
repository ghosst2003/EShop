from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship

from app.models import Base


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
