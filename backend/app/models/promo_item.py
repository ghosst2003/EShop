from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.models import Base


class PromoItem(Base):
    __tablename__ = "promo_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    subtitle = Column(String(200), default="")
    icon = Column(String(10), default="")
    image_url = Column(String(500), default="")
    tag = Column(String(50), default="")
    tag_class = Column(String(100), default="")
    link_url = Column(String(500), default="")
    product_id = Column(Integer, default=None)
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
